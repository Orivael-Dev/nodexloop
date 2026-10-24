import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_gym", ROOT / "run_gym.py")
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)


class GymSmokeTests(unittest.TestCase):
    def test_manifest_and_tasks(self):
        manifest, cases = gym.load_input(ROOT / "experiment.gym.yaml", ROOT / "tasks.json")
        self.assertEqual(manifest["kind"], "GymExperiment")
        self.assertEqual(len(cases), 10)
        self.assertEqual(len({x["id"] for x in cases}), 10)

    def test_fenced_code(self):
        self.assertEqual(gym.extract_code("~~~python\nx = 3\n~~~"), "x = 3")
        self.assertEqual(gym.extract_code("```python\nx = 4\n```"), "x = 4")
        self.assertEqual(gym.extract_code("def f():\n    return 2"), "def f():\n    return 2")

    def test_grade_invokes_networkless_docker_not_host_exec(self):
        fixture = {"id": "simple", "entrypoint": "f"}
        checks = [{"args": [1], "expected": 2}]
        result_line = gym.RESULT_MARKER + json.dumps({"results": [{"ok": True}]}) + "\n"
        fake = SimpleNamespace(stdout=result_line, stderr="", returncode=0)
        with patch.object(gym.subprocess, "run", return_value=fake) as docker:
            scored = gym.grade("def f(x): return x+1", fixture, checks,
                               {"image": "python:3.12-alpine", "timeout_seconds": 8})
        self.assertEqual(scored["passed"], 1)
        arguments = docker.call_args.args[0]
        self.assertIn("--network=none", arguments)
        self.assertIn("--read-only", arguments)
        self.assertIn("--cap-drop=ALL", arguments)

    def test_summary_reports_no_fake_token_counts(self):
        rows = [{
            "condition": "small_direct", "first_hidden_passed": False,
            "final_hidden_passed": True, "hidden_fraction": 1.0,
            "model_seconds": 3.0, "total_tokens": None,
        }]
        summary = gym.summary(rows)["small_direct"]
        self.assertEqual(summary["final_pass_rate"], 1.0)
        self.assertIsNone(summary["mean_tokens_reported"])


if __name__ == "__main__":
    unittest.main()
