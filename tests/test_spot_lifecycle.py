"""Observe Spot placement, explicit recovery, VIPER publication and cleanup boundaries."""
import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from csts_pilot.full_data_prompt_protocol import digest_file
from csts_pilot.full_data_prompt_uploads import publish_one
from csts_pilot.full_data_prompt_worker import rebind_resume_state, require_training_compatibility

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    """Load a project lifecycle adapter without running its cloud entrypoint."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/full_data_prompt_20261107" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResumeTests(unittest.TestCase):
    """Preserve successful epochs while requiring exact prior-state authorization."""
    def setUp(self):
        self.state = {"source_commit": "a"*40, "protocol_sha256": "b"*64, "worker": "worker1",
                      "lease": {"execution_id": "c"*32}, "trials": {"finished": {"records": [1,2,3,4,5]}},
                      "status": "failed_preserved", "failure": {"message": "serializer"}}
        self.approval = {"training_source_commit": "a"*40, "resumes": {"worker1": {
            "state_sha256": "d"*64, "previous_source_commit": "a"*40, "previous_execution_id": "c"*32}}}

    def test_hash_bound_rebind_preserves_completed_records(self):
        state = rebind_resume_state(copy.deepcopy(self.state), self.approval, "worker1",
                                    "e"*40, "b"*64, {"execution_id": "f"*32}, "d"*64)
        self.assertEqual(state["trials"], self.state["trials"])
        self.assertEqual(state["training_source_commit"], "a"*40)
        self.assertEqual(state["status"], "running")
        self.assertNotIn("failure", state)

    def test_changed_preserved_state_cannot_rebind(self):
        with self.assertRaisesRegex(ValueError, "Explicit resume"):
            rebind_resume_state(self.state, self.approval, "worker1",
                                "e"*40, "b"*64, {"execution_id": "f"*32}, "0"*64)

    def test_scientific_code_change_cannot_reuse_training_revision(self):
        with patch("subprocess.check_output", return_value="csts_pilot/baseline_stages.py\n"):
            with self.assertRaisesRegex(ValueError, "scientific"):
                require_training_compatibility(ROOT, "a"*40, "b"*40)


class PlacementTests(unittest.TestCase):
    """Use current manifest regions instead of an embedded Tokyo worker mapping."""
    def test_taiwan_capacity_can_be_selected_without_tokyo(self):
        deploy = load_script("deploy_spot")
        advice = [{"recommendations": [{"shards": [{"zone": "zones/asia-east1-b", "machineType": "g2-standard-4"}]}]}]
        result = deploy.candidates(["asia-east1"], ["asia-east1-a", "asia-east1-b", "asia-northeast1-b"], advice)
        self.assertEqual(result[0], ("asia-east1-b", "g2-standard-4"))
        self.assertTrue(all(zone.startswith("asia-east1-") for zone, _ in result))

    def test_outside_region_cannot_enter_candidate_search(self):
        with self.assertRaises(ValueError):
            load_script("deploy_spot").candidates(["us-east1"], ["us-east1-a"], [])


class PublicationTests(unittest.TestCase):
    """Require VIPER's streamed cloud verification before a durable generation ACK."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root / "transfer/epoch1"
        self.folder.mkdir(parents=True)
        self.archive = self.folder / "native.tar"
        self.archive.write_bytes(b"sealed native checkpoint")
        self.manifest = self.folder / "ready.json"
        self.manifest.write_text(json.dumps({"worker": "worker1", "generation": "epoch1",
            "source_commit": "a"*40, "execution_id": "b"*32, "instance_id": "123",
            "archive": str(self.archive), "archive_sha256": digest_file(self.archive),
            "archive_size": self.archive.stat().st_size}))

    def cloud(self):
        cloud = Mock()
        def references(destination, sources):
            result = {}
            for name, path in sources.items():
                digest = digest_file(path)
                size = path.stat().st_size
                result[name] = SimpleNamespace(sha256=digest, bytes=size,
                    model_dump=lambda mode, digest=digest, size=size: {"sha256":digest,"bytes":size,"stored_at":{"kind":"gcs"}})
            return result
        cloud.resolved_files.side_effect = references
        return cloud

    def test_verified_publication_writes_bound_viper_ack(self):
        cloud = self.cloud()
        ack = publish_one(self.root, self.manifest, cloud, "owner", "study")
        self.assertEqual(cloud.verify_file.call_count, 2)
        self.assertEqual(ack["archive_sha256"], digest_file(self.archive))
        self.assertEqual(ack["transport"], "viper_cloud")
        self.assertTrue((self.folder / "ack.json").exists())

    def test_cloud_verification_failure_preserves_local_without_ack(self):
        cloud = self.cloud()
        cloud.verify_file.side_effect = RuntimeError("remote SHA differs")
        with self.assertRaises(RuntimeError):
            publish_one(self.root, self.manifest, cloud, "owner", "study")
        self.assertTrue(self.archive.exists())
        self.assertFalse((self.folder / "ack.json").exists())


class CleanupTests(unittest.TestCase):
    """Limit deletion to exact task identities and retain unverified recovery bytes."""
    def setUp(self):
        self.collector = load_script("collect_epochs")
        self.assignment = {"instance_name": "jep-test", "instance_id": "123",
                           "project": "mantra-477901", "zone": "asia-east1-b",
                           "boot_disk": {"name": "jep-test", "id": "456"}}

    def test_replacement_instance_cannot_be_deleted(self):
        response = subprocess.CompletedProcess([], 0, json.dumps({"id":"999","labels":{"task":"jep-full-data-20261107"}}), "")
        with patch.object(self.collector, "run", return_value=response):
            with self.assertRaises(PermissionError):
                self.collector.describe(self.assignment, "admin@example.test")

    def test_unverified_failure_keeps_recovery_disk(self):
        with patch.object(self.collector, "describe", return_value={"id":"123"}), patch.object(
                self.collector, "run", return_value=subprocess.CompletedProcess([],0,"","")) as run:
            receipt = self.collector.cleanup(self.assignment, "admin@example.test", False, True)
        self.assertTrue(receipt["recovery_disk_preserved"])
        self.assertEqual(run.call_count, 1)
        self.assertIn("--keep-disks=all", run.call_args.args[0])

    def test_changed_recovery_disk_cannot_be_deleted(self):
        responses = [subprocess.CompletedProcess([],0,"",""), subprocess.CompletedProcess([],0,
            json.dumps({"id":"999","labels":{"task":"jep-full-data-20261107"}}),"")]
        with patch.object(self.collector, "describe", return_value={"id":"123"}), patch.object(
                self.collector, "run", side_effect=responses) as run:
            with self.assertRaises(PermissionError):
                self.collector.cleanup(self.assignment, "admin@example.test", True, True)
        self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
