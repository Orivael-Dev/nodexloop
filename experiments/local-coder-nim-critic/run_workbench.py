#!/usr/bin/env python3
"""Local model writes a Python script/repair; NIM critiques it; Docker verifies."""
import argparse
import ast
import datetime as dt
import difflib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile

import yaml

HERE = Path(__file__).resolve().parent
GYM_PATH = HERE.parent / "code-gym-v0" / "run_gym.py"
spec = importlib.util.spec_from_file_location("nodexloop_code_gym", GYM_PATH)
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)

MAX_PROMPT_FILE = 30000
MAX_REVIEW_TEXT = 3500
DOCKER_IMAGE = "python:3.12-alpine"


def relative_path(value):
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts or not str(path).endswith(".py"):
        raise ValueError("Use a relative .py file path without '..'")
    if any(part.startswith(".") for part in path.parts):
        raise ValueError("Hidden paths are not permitted")
    return path


def snapshot_commit(repo, workspace):
    """Use tracked HEAD only; never modify the original checkout."""
    repo = Path(repo).expanduser().resolve()
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, check=True)
    if git("status", "--porcelain").stdout.strip():
        raise ValueError("Git checkout must be clean; commit or stash changes first")
    commit = git("rev-parse", "HEAD").stdout.decode().strip()
    archive = git("archive", "--format=tar", "HEAD").stdout
    if len(archive) > 40_000_000:
        raise ValueError("Repository archive is too large for this experimental runner")
    total = 0
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for item in tar:
            path = Path(item.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe archive member: " + item.name)
            # Avoid exposing tracked secrets; Docker still sees all archived files.
            if any(p == ".env" or p.startswith(".env.") for p in path.parts):
                raise ValueError("Tracked .env file detected, refusing to prepare sandbox")
            dest = workspace / path
            if item.isdir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            if not item.isfile() or item.size > 2_000_000:
                raise ValueError("Unsupported or oversized repository member: " + item.name)
            total += item.size
            if total > 25_000_000:
                raise ValueError("Repository snapshot exceeds 25 MB")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(item) as inp, dest.open("wb") as out:
                shutil.copyfileobj(inp, out)
    return commit


def run_tests(workspace, command, timeout=25, image=DOCKER_IMAGE):
    argv = shlex.split(command)
    # Running subprocess via shell is intentionally not supported.
    if len(argv) < 3 or argv[:3] != ["python", "-m", "unittest"]:
        raise ValueError("v0 supports only python -m unittest ... test commands")
    cmd = ["docker", "run", "--rm", "--pull=never", "--network=none",
           "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
           "--pids-limit=64", "--memory=512m", "--cpus=1",
           "--user=65534:65534", "--workdir=/workspace",
           "--tmpfs", "/tmp:rw,nosuid,nodev,size=32m",
           "-e", "PYTHONDONTWRITEBYTECODE=1",
           "--mount", f"type=bind,src={workspace},dst=/workspace,readonly",
           image, *argv]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return {"passed": r.returncode == 0, "exit_code": r.returncode,
                "output": (r.stdout + "\n" + r.stderr)[-MAX_REVIEW_TEXT:]}
    except subprocess.TimeoutExpired:
        return {"passed": False, "exit_code": None, "output": "TIMEOUT in Docker test sandbox"}


def make_patch(path, before, after, mode="debug"):
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="/dev/null" if mode == "create" else "a/" + str(path),
        tofile="b/" + str(path),
    ))


def verdict(text):
    match = re.search(r"(?im)^\s*VERDICT:\s*(APPROVE|REQUEST_CHANGES)\b", text)
    return match.group(1).upper() if match else "UNPARSEABLE"


def make_coder_messages(task, target, before, context, previous):
    system = ("You are a local coding agent. Return ONLY the COMPLETE Python source for "
              "the requested target file. No markdown, no explanations, no other files. "
              "Never edit tests, bypass assertions or pretend tests passed.")
    user = (f"MODE: {task['mode']}\nTARGET: {target}\nTASK: {task['description']}\n"
            f"CURRENT FILE:\n{before or '[file does not exist]'}\n"
            f"AUTHORIZED READ CONTEXT:\n{context or '[none]'}")
    if previous:
        user += ("\nPREVIOUS ATTEMPT CODE:\n" + previous["code"][:MAX_PROMPT_FILE] +
                 "\nACTUAL TEST OUTPUT:\n" + previous["tests"]["output"] +
                 "\nNIM REVIEW:\n" + previous["review"][:2200] +
                 "\nProvide a corrected full file. Only trust independently observed tests.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def make_critic_messages(task, target, before, proposed, patch, tests):
    system = ("You are NVIDIA NIM, an independent code critic, not a coder. "
              "Review the requirements and actual test result. Find concrete "
              "regressions, edge cases, and unsupported assumptions. "
              "Do not claim you ran tests, and never instruct editing tests. "
              "Respond exactly with VERDICT: APPROVE or VERDICT: REQUEST_CHANGES; "
              "FINDINGS: ...; NEXT_CHANGE: ...; TEST_STATUS: ... . "
              "A passing test is required, but not sufficient, for APPROVE.")
    user = (f"MODE: {task['mode']}\nTASK: {task['description']}\nFILE: {target}\n"
            f"ORIGINAL:\n{before[:MAX_PROMPT_FILE]}\nPROPOSED:\n{proposed[:MAX_PROMPT_FILE]}\n"
            f"DIFF:\n{patch[:MAX_PROMPT_FILE]}\n"
            f"OBSERVED TESTS (not model claims):\n{json.dumps(tests)}")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def episode(config, repo, file, task_description, mode, test_command, output_dir):
    target = relative_path(file)
    if mode not in {"create", "debug"}:
        raise ValueError("Mode must be 'create' or 'debug'")
    if not shutil.which("docker"):
        raise ValueError("Docker is required")
    if subprocess.run(["docker", "image", "inspect", DOCKER_IMAGE],
                      capture_output=True).returncode:
        raise ValueError("Pre-pull sandbox image with docker pull " + DOCKER_IMAGE)
    local_settings = config["models"]["local_coder"]
    critic_settings = config["models"]["nim_critic"]
    gym.endpoint(local_settings)
    gym.endpoint(critic_settings)
    transport = config.get("transport", {})
    max_rounds = int(config.get("experiment", {}).get("max_rounds", 3))
    if max_rounds < 1 or max_rounds > 5:
        raise ValueError("max_rounds must be in 1..5")
    with tempfile.TemporaryDirectory(prefix="nxl-nim-critic-") as scratch:
        workdir = Path(scratch).resolve()
        commit = snapshot_commit(repo, workdir)
        candidate_path = workdir / target
        if mode == "debug" and not candidate_path.is_file():
            raise ValueError("DEBUG target must exist at HEAD: " + str(target))
        if mode == "create" and candidate_path.exists():
            raise ValueError("CREATE target already exists at HEAD: " + str(target))
        before = candidate_path.read_text(encoding="utf-8") if candidate_path.exists() else ""
        if len(before) > MAX_PROMPT_FILE:
            raise ValueError("Target too large for coding context; use a smaller script")
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        original_tests = run_tests(workdir, test_command)
        previous = None
        history = []
        selected = None
        task = {"mode": mode, "description": task_description}
        for index in range(1, max_rounds + 1):
            candidate = gym.chat(local_settings,
                                 make_coder_messages(task, target, before, "", previous),
                                 max_tokens=2600, transport=transport)
            code = gym.extract_code(candidate["text"]).strip() + "\n"
            if len(code) > MAX_PROMPT_FILE:
                raise ValueError("Generated code exceeds max file size")
            try:
                ast.parse(code, filename=str(target))
                candidate_path.write_text(code, encoding="utf-8")
                tests = run_tests(workdir, test_command)
            except SyntaxError as exc:
                tests = {"passed": False, "exit_code": None,
                         "output": f"SYNTAX ERROR: line {exc.lineno}, {exc.msg}"}
            patch = make_patch(target, before, code, mode=mode)
            critique = gym.chat(
                critic_settings,
                make_critic_messages(task, target, before, code, patch, tests),
                max_tokens=650, transport=transport,
            )
            decision = verdict(critique["text"])
            item = {"round": index, "code": code, "diff": patch,
                    "tests": tests, "review": critique["text"],
                    "verdict": decision, "coder_model": candidate["model"],
                    "critic_model": critique["model"],
                    "coder_seconds": candidate["seconds"], "critic_seconds": critique["seconds"],
                    "coder_tokens": candidate["total_tokens"], "critic_tokens": critique["total_tokens"]}
            history.append(item)
            print(f"Round {index}: tests={'PASS' if tests['passed'] else 'FAIL'} "
                  f"nim={decision}", flush=True)
            # Do not discard a previously passing attempt because later critique is wrong.
            if selected is None or (tests["passed"] and not selected["tests"]["passed"]):
                selected = item
            if tests["passed"] and decision == "APPROVE":
                selected = item
                break
            previous = item
        # A passing candidate always beats a failing one. No automatic write to repo.
        result = {
            "schema": "nodexloop.local-coder-nim-critic/v0",
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "original_commit": commit, "task": task, "target": str(target),
            "test_command": test_command, "baseline_tests": original_tests,
            "accepted": bool(selected and selected["tests"]["passed"] and selected["verdict"] == "APPROVE"),
            "test_passed": bool(selected and selected["tests"]["passed"]),
            "selected_round": selected["round"] if selected else None,
            "iterations": history,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        results_path = output_dir / ("run-" + stamp + ".json")
        patch_path = output_dir / ("run-" + stamp + ".patch")
        results_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        patch_path.write_text(selected["diff"] if selected else "", encoding="utf-8")
        print(f"Original checkout UNCHANGED; report: {results_path}")
        print(f"Proposed patch: {patch_path}")
        print("Final status:", "VERIFIED" if result["accepted"]
              else "TESTS PASS / REVIEW REQUIRED" if result["test_passed"]
              else "NOT VERIFIED")
        return result


def main():
    parser = argparse.ArgumentParser(description="Local coder → Docker tests → NIM critic")
    parser.add_argument("--config", type=Path, default=HERE / "experiment.yaml")
    parser.add_argument("--repo", type=Path, required=True, help="Existing clean local Git checkout")
    parser.add_argument("--mode", choices=["create", "debug"], required=True)
    parser.add_argument("--file", required=True, help="Explicit relative .py file allowed to change")
    parser.add_argument("--task", required=True, help="Concrete acceptance criteria")
    parser.add_argument("--test", required=True, help="python -m unittest ... (Docker only)")
    parser.add_argument("--output-dir", type=Path, default=HERE / "results")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    episode(config, args.repo, args.file, args.task, args.mode, args.test, args.output_dir)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError,
            OSError) as exc:
        print("ERROR:", str(exc), file=sys.stderr)
        sys.exit(1)
