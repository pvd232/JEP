"""Regress controller access failures without allocating or interrupting GPU work."""
import importlib.util
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    """Load a lifecycle entrypoint without executing cloud operations."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/full_data_prompt_20261107" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ControllerFailureTests(unittest.TestCase):
    """Separate inaccessible control state from actual worker and provider failures."""
    def setUp(self):
        self.collector = load("collect_epochs")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.local = Path(self.tmp.name)
        self.assignment = {"project": "mantra-477901", "zone": "asia-east1-b",
                           "instance_name": "jep-test", "instance_id": "123",
                           "execution_id": "b" * 32, "deadline_epoch": time.time() + 3600}
        self.args = SimpleNamespace(source="a" * 40, max_hours=1, local=self.local,
                                    delete_verified_disks=True,
                                    approval={"assignments": {"worker1": self.assignment},
                                              "controller_account": "controller@example.iam.gserviceaccount.com"})
        self.state = {"source_commit": "a" * 40, "worker": "worker1", "seeds": [7],
                      "status": "running", "test_opened": False, "trials": {},
                      "lease": {"execution_id": "b" * 32, "deadline_verified": True}}

    def test_expired_auth_never_deletes_or_relabels_running_work(self):
        old = self.local / "worker1-latest-state.json"
        old.write_text(json.dumps(self.state))
        preserved = old.read_bytes()
        error = self.collector.CloudCommandError("Reauthentication failed. cannot prompt")
        with patch.object(self.collector, "describe", side_effect=error), \
             patch.object(self.collector, "cleanup") as cleanup:
            with self.assertRaises(self.collector.ObservationUnavailable):
                self.collector.monitor("worker1", self.args)
        cleanup.assert_not_called()
        self.assertEqual(old.read_bytes(), preserved)
        receipt = json.loads((self.local / "worker1-cleanup.json").read_text())
        self.assertIsNone(receipt["instance_deleted"])
        self.assertEqual(receipt["cleanup_status"], "not_attempted")

    def test_transient_ssh_failure_is_retried_without_deleting_worker(self):
        failure = self.collector.CloudCommandError("IAP backend temporarily unreachable")
        auth = self.collector.CloudCommandError("Reauthentication failed")
        with patch.object(self.collector, "describe", side_effect=[{"status": "RUNNING"}, {"status": "RUNNING"}, auth]), \
             patch.object(self.collector, "read_worker", side_effect=[failure, {"state": self.state, "ready": []}]) as read, \
             patch.object(self.collector.time, "sleep"), patch.object(self.collector, "cleanup") as cleanup:
            with self.assertRaises(self.collector.ObservationUnavailable):
                self.collector.monitor("worker1", self.args)
        self.assertEqual(read.call_count, 2)
        cleanup.assert_not_called()
        self.assertEqual(json.loads((self.local / "worker1-latest-state.json").read_text()), self.state)

    def test_repeated_transport_failures_are_bounded_without_cleanup(self):
        with patch.object(self.collector, "describe", return_value={"status": "RUNNING"}), \
             patch.object(self.collector, "read_worker", side_effect=subprocess.TimeoutExpired("ssh", 90)) as read, \
             patch.object(self.collector.time, "sleep"), patch.object(self.collector, "cleanup") as cleanup:
            with self.assertRaises(self.collector.ObservationUnavailable):
                self.collector.monitor("worker1", self.args)
        self.assertEqual(read.call_count, 5)
        cleanup.assert_not_called()

    def test_worker_reported_failure_allows_owned_compute_cleanup_but_keeps_disk(self):
        self.state.update(status="failed_preserved", failure={"message": "worker stage failed"})
        with patch.object(self.collector, "describe", return_value={"status": "RUNNING"}), \
             patch.object(self.collector, "read_worker", return_value={"state": self.state, "ready": []}), \
             patch.object(self.collector, "cleanup", return_value={"instance_deleted": True, "disk_deleted": False}) as cleanup:
            with self.assertRaisesRegex(self.collector.WorkerReportedFailure, "worker stage failed"):
                self.collector.monitor("worker1", self.args)
        self.assertFalse(cleanup.call_args.args[2])
        self.assertTrue(json.loads((self.local / "worker1-cleanup.json").read_text())["instance_deleted"])

    def test_cleanup_error_does_not_replace_original_worker_failure(self):
        self.state.update(status="failed_preserved", failure={"message": "original worker error"})
        with patch.object(self.collector, "describe", return_value={"status": "RUNNING"}), \
             patch.object(self.collector, "read_worker", return_value={"state": self.state, "ready": []}), \
             patch.object(self.collector, "cleanup", side_effect=self.collector.CloudCommandError("Reauthentication failed")):
            with self.assertRaisesRegex(self.collector.WorkerReportedFailure, "original worker error"):
                self.collector.monitor("worker1", self.args)
        self.assertEqual(json.loads((self.local / "worker1-cleanup.json").read_text())["cleanup_status"], "failed")

    def test_changed_identity_cannot_trigger_cleanup(self):
        with patch.object(self.collector, "describe", side_effect=PermissionError("immutable ID changed")), \
             patch.object(self.collector, "cleanup") as cleanup:
            with self.assertRaises(PermissionError):
                self.collector.monitor("worker1", self.args)
        cleanup.assert_not_called()

    def test_personal_login_is_rejected_before_metadata_or_cloud_access(self):
        with patch.object(self.collector.urllib.request, "urlopen") as request:
            with self.assertRaisesRegex(PermissionError, "personal login"):
                self.collector.require_controller_identity("person@example.com")
        request.assert_not_called()

    def test_cli_environment_excludes_personal_credential_overrides(self):
        sentinel = self.local / "personal-adc.json"
        sentinel.write_text("unchanged")
        with patch.object(Path, "home", return_value=self.local), \
             patch.dict(self.collector.os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": str(sentinel),
                         "CLOUDSDK_AUTH_ACCESS_TOKEN": "test-value", "CLOUDSDK_CONFIG": "/personal-config"}):
            env = self.collector.controller_environment()
        self.assertNotIn("GOOGLE_APPLICATION_CREDENTIALS", env)
        self.assertNotIn("CLOUDSDK_AUTH_ACCESS_TOKEN", env)
        self.assertNotEqual(env["CLOUDSDK_CONFIG"], "/personal-config")
        self.assertEqual(sentinel.read_text(), "unchanged")


class ReporterFailureTests(unittest.TestCase):
    """Require evidence of cleanup before closing a monitor after controller errors."""
    def test_auth_failure_is_unknown_and_does_not_become_a_terminal_worker_result(self):
        reporter = load("publish_status")
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            folder = data / "collection-worker1"
            folder.mkdir()
            (data / "approval-worker1.json").write_text(json.dumps({
                "controller_account": "expired@example.com", "source_commit": "a" * 40,
                "assignments": {"worker1": {"zone": "asia-east1-b", "project": "mantra-477901",
                                          "instance_name": "jep-test", "instance_id": "123", "execution_id": "b" * 32}}}))
            state = {"worker": "worker1", "source_commit": "a" * 40, "status": "running", "trials": {},
                     "seeds": [8, 10], "lease": {"execution_id": "b" * 32}, "test_opened": False}
            (folder / "worker1-latest-state.json").write_text(json.dumps(state))
            (folder / "collection-final.json").write_text(json.dumps([{"status": "failed_preserved", "reason": "Reauthentication failed"}]))
            with patch.object(reporter, "command", side_effect=subprocess.CalledProcessError(1, ["gcloud"], stderr="Reauthentication failed")):
                result = reporter.observe("worker1", data)
            self.assertFalse(result["fresh"])
            self.assertNotIn("final", result)
            page = reporter.render({"workers": [result], "generated_epoch": time.time(),
                                    "monitor_status": "controller_unavailable", "forecast": None}, [])
            self.assertIn("Current GPU activity, training completion and cleanup are unconfirmed", page)
            self.assertNotIn("Stopped; recovery work preserved", page)
            self.assertGreater(len(page.splitlines()), 10)


if __name__ == "__main__":
    unittest.main()
