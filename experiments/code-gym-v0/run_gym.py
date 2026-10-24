#!/usr/bin/env python3
"""Comparative coding gym: isolated Docker grading + OpenAI-compatible endpoints."""
import argparse
import ast
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parent
RESULT_MARKER = "NODEXLOOP_GRADE:"

# This script runs inside the Docker sandbox, not in the host Python process.
SANDBOX_SCRIPT = r'''
import contextlib, io, json, resource, sys
resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
data = json.load(sys.stdin)
out = []
namespace = {"__name__": "candidate"}
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    try:
        exec(compile(data["source"], "<candidate>", "exec"), namespace)
        func = namespace[data["entrypoint"]]
        for case in data["cases"]:
            try:
                actual = func(*case.get("args", []), **case.get("kwargs", {}))
                expected = case["expected"]
                correct = type(actual) is type(expected) and actual == expected
                out.append({"ok": correct, "expected": expected, "actual": actual if isinstance(actual, (str, int, float, bool, list, dict, type(None))) else repr(actual)[:120]})
            except BaseException as exc:
                out.append({"ok": False, "error": type(exc).__name__})
    except BaseException as exc:
        out = [{"ok": False, "error": "load_" + type(exc).__name__} for _ in data["cases"]]
print("NODEXLOOP_GRADE:" + json.dumps({"results": out}, default=str))
'''

def load_input(config_path, case_path):
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config.get("kind") != "GymExperiment" or config.get("apiVersion") != "nodexloop.training/v1alpha1":
        raise ValueError("Unsupported gym manifest")
    cases = json.loads(case_path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) != 10:
        raise ValueError("Exactly ten benchmark tasks are required for v0")
    ids = [task["id"] for task in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task IDs")
    for task in cases:
        ast.parse(task["starter"])
        if not task["prompt"] or not task["entrypoint"]:
            raise ValueError("Missing prompt/entrypoint: " + task["id"])
        if not task["visible"] or not task["hidden"]:
            raise ValueError("Need independent visible and hidden tests: " + task["id"])
        for check in task["visible"] + task["hidden"]:
            if "expected" not in check:
                raise ValueError("Test missing expected value: " + task["id"])
    return config, cases

def extract_code(content):
    """Strip one fenced source block while retaining unfenced plain Python."""
    content = content.strip()
    match = re.search(r"~~~(?:python)?\s*\n(.*?)\n~~~|```(?:python)?\s*\n(.*?)\n```", content, re.S | re.I)
    if match:
        return (match.group(1) or match.group(2)).strip()
    return content

def endpoint(settings):
    base = os.getenv(settings["base_url_env"], "").strip().rstrip("/")
    model = os.getenv(settings["model_env"], "").strip()
    key = os.getenv(settings.get("api_key_env", ""), "").strip()
    if not base or not model:
        raise ValueError("Missing endpoint/model environment variables for " + settings["model_env"])
    if not base.startswith(("http://", "https://")):
        raise ValueError("Expected an HTTP(S) OpenAI-compatible endpoint")
    url = base if base.endswith("/chat/completions") else base + "/chat/completions"
    return url, model, key

def chat(settings, messages, max_tokens=900):
    url, model, key = endpoint(settings)
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    start = time.monotonic()
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, data=payload, headers=headers, method="POST"),
            timeout=120,
        ) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Model HTTP failure (status %s) for %s" % (exc.code, model)) from None
    elapsed = time.monotonic() - start
    message = data["choices"][0]["message"]["content"]
    if isinstance(message, list):
        message = "\n".join(x.get("text", "") for x in message if isinstance(x, dict))
    usage = data.get("usage") or {}
    return {"text": str(message or ""), "seconds": round(elapsed, 3),
            "total_tokens": usage.get("total_tokens"), "model": model}

def grade(source, task, tests, sandbox):
    """Never run candidate code in the host process."""
    cmd = [
        "docker", "run", "--rm", "-i", "--pull=never", "--network=none",
        "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--pids-limit=64", "--memory=256m", "--cpus=1", "--user=65534:65534",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=16m",
        sandbox["image"], "python", "-I", "-B", "-c", SANDBOX_SCRIPT,
    ]
    body = json.dumps({"source": source, "entrypoint": task["entrypoint"], "cases": tests})
    started = time.monotonic()
    try:
        run = subprocess.run(cmd, input=body, text=True, capture_output=True,
                             timeout=sandbox.get("timeout_seconds", 12), check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"passed": 0, "total": len(tests), "feedback": ["sandbox_" + type(exc).__name__],
                "seconds": round(time.monotonic() - started, 3)}
    duration = round(time.monotonic() - started, 3)
    marked = [line for line in run.stdout.splitlines() if line.startswith(RESULT_MARKER)]
    if run.returncode or not marked:
        return {"passed": 0, "total": len(tests), "feedback": ["sandbox_execution_failed"],
                "seconds": duration}
    try:
        results = json.loads(marked[-1][len(RESULT_MARKER):])["results"]
        if len(results) != len(tests):
            raise ValueError("Incomplete grading results")
    except (ValueError, KeyError, TypeError):
        return {"passed": 0, "total": len(tests), "feedback": ["invalid_grader_result"],
                "seconds": duration}
    feedback = []
    for i, result in enumerate(results, 1):
        if not result["ok"]:
            detail = result.get("error") or ("expected %s, got %s" % (
                repr(result.get("expected"))[:120], repr(result.get("actual"))[:120]))
            feedback.append("visible case %s: %s" % (i, detail))
    return {"passed": sum(bool(result["ok"]) for result in results), "total": len(tests),
            "feedback": feedback, "seconds": duration}

def task_messages(task):
    return [
        {"role": "system", "content": "Write a complete Python module. Return ONLY Python source code, no markdown. Do not use external packages. Follow the function name/signature."},
        {"role": "user", "content": task["prompt"] + "\n\nExisting broken implementation:\n" + task["starter"]},
    ]

def coach_messages(task, code, visible):
    return [
        {"role": "system", "content": "You are a debugging coach. Give one short actionable diagnosis, not replacement code. You receive visible feedback only; never assume hidden test results."},
        {"role": "user", "content": "Task:\n" + task["prompt"] + "\n\nAttempt:\n" + code +
         "\n\nVisible grader feedback:\n" + "\n".join(visible["feedback"])},
    ]

def run_condition(condition, task, config, initial):
    sandbox = config["sandbox"]
    small = config["models"]["small"]
    large = config["models"]["large"]
    max_repairs = config["experiment"]["max_repairs"] if condition in ("small_gym", "small_teacher") else 0
    response = initial
    attempts = []
    calls = [initial]
    for attempt_index in range(max_repairs + 1):
        code = extract_code(response["text"])
        visible = grade(code, task, task["visible"], sandbox)
        # Hidden results NEVER enter a model prompt or teacher critique.
        hidden = grade(code, task, task["hidden"], sandbox)
        attempts.append({"attempt": attempt_index + 1, "code": code,
                         "visible": visible, "hidden": hidden})
        if attempt_index == max_repairs or visible["passed"] == visible["total"]:
            break
        hint = ""
        if condition == "small_teacher":
            critique = chat(large, coach_messages(task, code, visible), max_tokens=280)
            calls.append(critique)
            hint = "\nTeacher diagnosis:\n" + critique["text"]
        retry_messages = task_messages(task) + [
            {"role": "assistant", "content": code},
            {"role": "user", "content": "Your solution failed these VISIBLE checks:\n" +
             "\n".join(visible["feedback"]) + hint +
             "\nRepair your solution. Return complete Python source only."},
        ]
        response = chat(small, retry_messages)
        calls.append(response)
    counts = [x["total_tokens"] for x in calls if isinstance(x["total_tokens"], (int, float))]
    return {
        "condition": condition,
        "model": initial["model"],
        "attempts": attempts,
        "first_hidden_passed": attempts[0]["hidden"]["passed"] == attempts[0]["hidden"]["total"],
        "final_hidden_passed": attempts[-1]["hidden"]["passed"] == attempts[-1]["hidden"]["total"],
        "hidden_fraction": attempts[-1]["hidden"]["passed"] / attempts[-1]["hidden"]["total"],
        "model_calls": len(calls),
        "model_seconds": round(sum(x["seconds"] for x in calls), 3),
        "grader_seconds": round(sum(y[z]["seconds"] for y in attempts for z in ("visible", "hidden")), 3),
        "total_tokens": sum(counts) if len(counts) == len(calls) else None,
    }

def summary(rows):
    output = {}
    for condition in ("small_direct", "large_direct", "small_gym", "small_teacher"):
        subset = [r for r in rows if r["condition"] == condition]
        if not subset:
            continue
        known = [x["total_tokens"] for x in subset if x["total_tokens"] is not None]
        output[condition] = {
            "episodes": len(subset),
            "first_pass_rate": round(sum(r["first_hidden_passed"] for r in subset) / len(subset), 3),
            "final_pass_rate": round(sum(r["final_hidden_passed"] for r in subset) / len(subset), 3),
            "mean_hidden_score": round(sum(r["hidden_fraction"] for r in subset) / len(subset), 3),
            "mean_model_seconds": round(sum(r["model_seconds"] for r in subset) / len(subset), 3),
            "mean_tokens_reported": round(sum(known) / len(known), 1) if known else None,
            "token_coverage": str(len(known)) + "/" + str(len(subset)),
        }
    return output

def main():
    parser = argparse.ArgumentParser(description="NodeXLoop short-code training-gym discovery benchmark")
    parser.add_argument("--config", type=Path, default=ROOT / "experiment.gym.yaml")
    parser.add_argument("--cases", type=Path, default=ROOT / "tasks.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--check", action="store_true", help="Validate files; do not call models or run code")
    args = parser.parse_args()
    config, tasks = load_input(args.config, args.cases)
    if args.check:
        print("Valid manifest and %d synthetic tasks; no model calls made." % len(tasks))
        return
    if not shutil.which("docker"):
        raise RuntimeError("Docker is required; candidate code is never executed on the host.")
    sandbox_image = config["sandbox"]["image"]
    inspect = subprocess.run(["docker", "image", "inspect", sandbox_image], capture_output=True)
    if inspect.returncode:
        raise RuntimeError("Pre-pull sandbox image before running: docker pull " + sandbox_image)
    for spec in config["models"].values():
        endpoint(spec)
    reps = args.repeats if args.repeats is not None else config["experiment"]["repetitions"]
    if reps < 1 or args.limit < 1:
        raise ValueError("Repetitions and task limit must be positive")
    rows = []
    for task in tasks[:args.limit]:
        for repetition in range(1, reps + 1):
            # Sharing the first small-model response removes first-attempt variation
            # from comparisons between baseline, gym feedback and teacher feedback.
            initial_small = chat(config["models"]["small"], task_messages(task))
            initial_large = chat(config["models"]["large"], task_messages(task))
            for condition in ("small_direct", "large_direct", "small_gym", "small_teacher"):
                first = initial_large if condition == "large_direct" else initial_small
                result = run_condition(condition, task, config, first)
                result.update({"task": task["id"], "repetition": repetition})
                rows.append(result)
            print("Completed %s, repetition %s" % (task["id"], repetition), flush=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir / ("gym-" + timestamp + ".json")
    report = {
        "schema": "nodexloop.gym.results/v0",
        "created_utc": timestamp,
        "notes": "Synthetic tasks. Docker-isolated checks. Hidden feedback never shown to models. First small-model attempt is shared across three small-model conditions; times/token counts are per-condition estimates, not actual bill totals.",
        "configuration": {"sandbox_image": sandbox_image, "max_repairs": config["experiment"]["max_repairs"], "repetitions": reps},
        "summary": summary(rows),
        "episodes": rows,
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print("Saved " + str(output))

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError, urllib.error.URLError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
