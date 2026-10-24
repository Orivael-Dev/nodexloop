import importlib.util
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_gym", ROOT / "run_gym.py")
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)


@unittest.skipUnless(shutil.which("docker"), "Docker unavailable")
class DockerIntegrationTests(unittest.TestCase):
    def test_executes_candidate_only_in_isolated_container(self):
        image = "python:3.12-alpine"
        if subprocess.run(["docker", "image", "inspect", image],
                          capture_output=True).returncode:
            self.skipTest("Sandbox image not pre-pulled")
        task = {"entrypoint": "double"}
        checks = [{"args": [2], "expected": 4}, {"args": [3], "expected": 6}]
        result = gym.grade("def double(x):\n    return 2*x\n", task, checks,
                           {"image": image, "timeout_seconds": 15})
        self.assertEqual(result["passed"], 2, result)

    def test_detects_wrong_answer(self):
        image = "python:3.12-alpine"
        if subprocess.run(["docker", "image", "inspect", image],
                          capture_output=True).returncode:
            self.skipTest("Sandbox image not pre-pulled")
        task = {"entrypoint": "double"}
        checks = [{"args": [2], "expected": 4}]
        result = gym.grade("def double(x):\n    return x+1\n", task, checks,
                           {"image": image, "timeout_seconds": 15})
        self.assertEqual(result["passed"], 0, result)


if __name__ == "__main__":
    unittest.main()
