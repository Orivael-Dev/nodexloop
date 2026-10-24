import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_gym", ROOT / "run_gym.py")
gym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gym)


class NetworkResilienceTests(unittest.TestCase):
    def setUp(self):
        gym._LAST_REQUEST_FINISHED = None
        self.env = patch.dict(os.environ, {
            "GYM_TEST_URL": "http://localhost:9999/v1",
            "GYM_TEST_MODEL": "test-model",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.settings = {
            "base_url_env": "GYM_TEST_URL",
            "model_env": "GYM_TEST_MODEL",
        }
        self.transport = {
            "request_timeout_seconds": 180,
            "max_retries": 2,
            "pause_between_calls_seconds": 0,
            "retry_backoff_seconds": 0,
            "max_backoff_seconds": 0,
        }
        self.messages = [{"role": "user", "content": "test"}]

    def test_timeout_then_recovery(self):
        reply = io.BytesIO(json.dumps({
            "choices": [{"message": {"content": "def f(): return 1"}}],
            "usage": {"total_tokens": 12},
        }).encode())
        with patch.object(gym.urllib.request, "urlopen",
                          side_effect=[TimeoutError("The read operation timed out"), reply]) as mocked, \
             patch.object(gym.time, "sleep"):
            result = gym.chat(self.settings, self.messages, transport=self.transport)
        self.assertEqual(result["request_attempts"], 2)
        self.assertEqual(result["total_tokens"], 12)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(mocked.call_args.kwargs["timeout"], 180)

    def test_nonretryable_authorization_failure(self):
        failure = urllib.error.HTTPError(
            "http://localhost/test", 401, "unauthorized", {}, io.BytesIO(b"")
        )
        with patch.object(gym.urllib.request, "urlopen", side_effect=failure) as mocked:
            with self.assertRaisesRegex(RuntimeError, "non-retryable"):
                gym.chat(self.settings, self.messages, transport=self.transport)
        self.assertEqual(mocked.call_count, 1)

    def test_retryable_429_retries_are_bounded(self):
        def failure():
            return urllib.error.HTTPError(
                "http://localhost/test", 429, "limited",
                {"Retry-After": "10"}, io.BytesIO(b"")
            )
        with patch.object(gym.urllib.request, "urlopen", side_effect=[
            failure(), failure(), failure(),
        ]) as mocked, patch.object(gym.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "after 3 request"):
                gym.chat(self.settings, self.messages, transport=self.transport)
        self.assertEqual(mocked.call_count, 3)


class CheckpointTests(unittest.TestCase):
    def test_save_and_resume_reject_mismatched_input(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "gym-progress.json"
            rows = [{
                "task": "appointments", "repetition": 1,
                "condition": "small_direct", "first_hidden_passed": True,
                "final_hidden_passed": True, "hidden_fraction": 1.0,
                "model_seconds": 0.3, "total_tokens": 20,
            }]
            gym.save_progress(path, "abc123", rows)
            self.assertEqual(gym.load_progress(path, "abc123"), rows)
            with self.assertRaisesRegex(ValueError, "do not match"):
                gym.load_progress(path, "different")


if __name__ == "__main__":
    unittest.main()
