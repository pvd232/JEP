"""Recovery boundaries: transient-only retries, durable caps and provenance."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("recovery", Path(__file__).parents[1] / "scripts/tranche8_capture_recovery.py")
assert SPEC is not None and SPEC.loader is not None
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


class RecoveryTests(unittest.TestCase):
    def batch(self, root, name="batch_0040", events=None, **receipt):
        directory = root / "training" / name
        directory.mkdir(parents=True)
        recovery.save(directory / "receipt.json", {"status": "failed", "items": 64, "returncode": 0, **receipt})
        (directory / "events.jsonl").write_text("\n".join(json.dumps(event) for event in (events if events is not None else [{"type": "error", "message": "Too many requests: request rate limit reached (429)"}])))
        recovery.save(directory / "inputs.json", [])
        return directory

    def capture(self):
        return SimpleNamespace(CLI="codex", completed_batch=Mock(), checked_events=Mock(), checked_records=Mock(side_effect=ValueError("invalid response")))

    def test_rate_limit_error_plus_completed_turn_remains_rejected_but_retryable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.batch(root, events=[{"type": "error", "message": "Too many requests 429"}, {"type": "item.completed", "item": {"type": "agent_message"}}, {"type": "turn.completed", "usage": {}}])
            self.assertTrue(recovery.preflight(root, self.capture()))

    def test_timeout_command_approval_policy_is_not_a_policy_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.batch(root, events=[{"type": "thread.started"}], returncode=None, error="Command ['codex', '-c', 'approval_policy=never'] timed out after 1200 seconds")
            self.assertTrue(recovery.preflight(root, self.capture()))

    def test_auth_quota_policy_and_unknown_tool_all_stop_recovery(self):
        for event in [
            {"type": "error", "message": "429 insufficient_quota"},
            {"type": "error", "message": "429 usage limit reached"},
            {"type": "error", "code": "usage_limit_reached", "message": "429"},
            {"type": "error", "message": "429 authentication required"},
            {"type": "error", "message": "429 policy violation"},
            {"type": "error", "message": "Connection failed: please sign in"},
            {"type": "item.completed", "item": {"type": "command_execution"}},
            {"type": "unexpected"},
        ]:
            with self.subTest(event=event), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.batch(root, events=[event], error="timed out after 1200 seconds")
                with self.assertRaises(recovery.RecoveryFailure):
                    recovery.preflight(root, self.capture())

    def test_total_attempt_cap_survives_another_supervisor_invocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("batch_0040", "batch_0040-attempt_02", "batch_0040-attempt_03"):
                self.batch(root, name)
            for _ in range(2):
                with self.assertRaises(recovery.RecoveryFailure):
                    recovery.preflight(root, self.capture())
            self.assertEqual(len(list((root / "training").iterdir())), 3)

    def test_completed_batch_is_validated_and_historical_failure_does_not_block(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.batch(root, events=[{"type": "error", "message": "unexpected historical failure"}])
            self.batch(root, "batch_0040-attempt_02", status="complete")
            capture = self.capture()
            self.assertFalse(recovery.preflight(root, capture))
            capture.completed_batch.assert_called_once()
            capture.completed_batch.side_effect = ValueError("corrupt completion")
            with self.assertRaises(ValueError):
                recovery.preflight(root, capture)

    def test_response_defect_may_retry_with_valid_event_log_and_zero_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = self.batch(root, events=[{"type": "turn.completed", "usage": {}}])
            recovery.save(directory / "response.json", {"records": []})
            self.assertTrue(recovery.preflight(root, self.capture()))

    def test_incomplete_event_trace_is_not_a_response_defect(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.batch(root, events=[{"type": "thread.started"}])
            capture = self.capture()
            capture.checked_events.side_effect = ValueError("incomplete turn")
            with self.assertRaises(recovery.RecoveryFailure):
                recovery.preflight(root, capture)

    def test_child_pin_failure_writes_terminal_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            recovery.save(directory / "supervisor_receipt.json", {"status": "launching", "source_commit": recovery.COMMIT})
            with patch.object(recovery, "DIRECTORY", directory), patch.object(recovery.fcntl, "flock"), patch.object(recovery, "pinned", side_effect=ValueError("bad pin")):
                result = recovery.run(12)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(json.loads((directory / "supervisor_receipt.json").read_text())["status"], "failed")
            self.assertEqual(json.loads((directory / "result.json").read_text())["status"], "failed")

    def test_history_preserves_exact_terminal_bytes_and_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            original = {"supervisor_receipt.json": b'{"status":"failed"}\n', "result.json": b'{"failure":"preserve me"}\n'}
            for name, data in original.items():
                (directory / name).write_bytes(data)
            history = Path(recovery.archive_terminal(directory))
            manifest = json.loads((history / "manifest.json").read_text())
            for name, data in original.items():
                self.assertEqual((history / name).read_bytes(), data)
                self.assertEqual(manifest["sha256"][name], recovery.digest(data))
            self.assertEqual((directory / "supervisor_receipt.json").read_bytes(), original["supervisor_receipt.json"])
            self.assertFalse((directory / "result.json").exists())

    def test_live_supervisor_is_never_replaced(self):
        with patch.object(recovery.os, "kill", return_value=None), patch.object(recovery.subprocess, "check_output") as processes:
            with self.assertRaises(recovery.RecoveryFailure):
                recovery.no_live_capture({"pid": 42})
            processes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
