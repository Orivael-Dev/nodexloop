import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import os

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_workbench", ROOT / "run_workbench.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)

def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)

class WorkbenchUnitTests(unittest.TestCase):
    def test_file_path_restrictions(self):
        for invalid in ["/tmp/secret.py", "../secret.py", ".env/secret.py", "a.txt"]:
            with self.assertRaises(ValueError):
                wb.relative_path(invalid)
        self.assertEqual(str(wb.relative_path("src/service.py")), "src/service.py")

    def test_critic_verdict(self):
        self.assertEqual(wb.verdict("VERDICT: APPROVE\nFINDINGS: NONE"), "APPROVE")
        self.assertEqual(wb.verdict("VERDICT: REQUEST_CHANGES"), "REQUEST_CHANGES")
        self.assertEqual(wb.verdict("probably okay"), "UNPARSEABLE")

    def test_patch_for_creation(self):
        result = wb.make_patch(Path("util.py"), "", "def f():\n    return 1\n", mode="create")
        self.assertIn("--- /dev/null", result)
        self.assertIn("+++ b/util.py", result)

    def test_snapshot_clean_git_and_refuses_dirty(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            origin = root / "original"
            copy = root / "copy"
            origin.mkdir()
            (origin / "calc.py").write_text("def add(a,b): return a+b\n")
            git(origin, "init")
            git(origin, "config", "user.email", "test@example.invalid")
            git(origin, "config", "user.name", "Test")
            git(origin, "add", "calc.py")
            git(origin, "commit", "-m", "fixture")
            copy.mkdir()
            commit = wb.snapshot_commit(origin, copy)
            self.assertEqual(commit, git(origin, "rev-parse", "HEAD").stdout.strip())
            self.assertEqual((copy / "calc.py").read_text(), "def add(a,b): return a+b\n")
            (origin / "calc.py").write_text("changed")
            with self.assertRaises(ValueError):
                wb.snapshot_commit(origin, copy)

    def test_coder_only_receives_authorized_file(self):
        prompt = wb.make_coder_messages({"mode":"debug","description":"fix add"},
            "src/add.py", "def add(a,b): return a-b", "", None)
        self.assertIn("src/add.py", prompt[1]["content"])
        self.assertNotIn("hidden_tests", prompt[1]["content"])


@unittest.skipUnless(shutil.which("docker"), "Docker not available")
class WorkbenchSandboxTests(unittest.TestCase):
    def setUp(self):
        self.image = "python:3.12-alpine"
        if subprocess.run(["docker", "image", "inspect", self.image],
                          capture_output=True).returncode:
            self.skipTest("Docker test image not pulled")

    def test_real_docker_baseline_and_fix(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "logic.py").write_text("def double(x): return x+1\n")
            (root / "test_logic.py").write_text(
                "import unittest\nfrom logic import double\n"
                "class T(unittest.TestCase):\n"
                "    def test_double(self): self.assertEqual(double(3), 6)\n")
            command = "python -m unittest discover -s . -p test_*.py -v"
            baseline = wb.run_tests(root, command)
            self.assertFalse(baseline["passed"], baseline)
            (root / "logic.py").write_text("def double(x): return x*2\n")
            repaired = wb.run_tests(root, command)
            self.assertTrue(repaired["passed"], repaired)


if __name__ == "__main__":
    unittest.main()
