"""Verify subset transport without credentials, devices or model calls."""

import importlib.util
import fcntl
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("subset_operator", Path(__file__).parents[1] / "scripts/tranche8_subset_operator.py")
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)


class SubsetOperatorTests(unittest.TestCase):
    def fixture(self, temporary):
        base = Path(temporary)
        original, actual, output, inventory_root = (base / name for name in ("original", "private-bank", "output", "inventory"))
        for path in (original, actual / "training", output, inventory_root / "full_inventory"):
            path.mkdir(parents=True)
        alias = base / "bank-alias"
        alias.symlink_to(actual, target_is_directory=True)
        source = b"pinned source\n"
        for name in ("full_capture_controller.py", "proposition_capture.py", "audit_gate.json"):
            (original / name).write_bytes(b"{}" if name.endswith(".json") else source)
        items = [{"id": str(i), "passage": "passage", "condition": "condition"} for i in range(2880)]
        records = [{"id": item["id"], "status": "answered", "answer": "answer"} for item in items]
        groups = {item["id"]: item["id"] for item in items}
        (inventory_root / "full_inventory/training_groups.json").write_text(json.dumps(groups))
        selected = [items[start:start+64] for start in range(0, len(items), 64)]
        for index, batch_items in enumerate(selected):
            batch = actual / "training" / f"batch_{index:04d}"
            batch.mkdir()
            (batch / "receipt.json").write_text(json.dumps({"status": "complete"}))
            (batch / "records.json").write_text(json.dumps(records[index*64:index*64+len(batch_items)]))
        controller = SimpleNamespace(verify_gate=Mock(return_value={"generation_template_sha256": "a"*64, "schema_sha256": "b"*64, "model_alias": "fixed", "reasoning_effort": "high"}), verify_inventory=Mock(return_value={"training": items}), GENERATION_ROOT=inventory_root, EXPECTED={"training": {"source": "c"*64}})
        def completed(batch_items, directory, cli):
            self.assertEqual(directory, directory.resolve())
            self.assertTrue(str(directory).startswith(str(actual)))
            self.assertEqual(batch_items, selected[int(directory.name.split("_")[1])])
        capture = SimpleNamespace(batches=Mock(return_value=selected), completed_batch=Mock(side_effect=completed), checked_records=Mock(side_effect=lambda expected, payload: payload["records"]), CLI="fixed-cli")
        return base, original, alias, actual, output, source, controller, capture

    def test_harvest_resolves_alias_before_exact_command_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, original, alias, actual, output, source, controller, capture = self.fixture(temporary)
            failed = actual / "training/batch_0045"
            failed.mkdir()
            (failed / "receipt.json").write_text('{"status":"failed"}')
            with patch.object(operator, "ORIGINAL", original), patch.object(operator, "BANK", alias), patch.object(operator, "CONTROLLER_SHA", operator.sha(source)), patch.object(operator, "CAPTURE_SHA", operator.sha(source)), patch.object(operator, "load", side_effect=[controller, capture]):
                result = operator.harvest(output)
            self.assertEqual(result["items"], 2880)
            self.assertEqual(result["completed_batches"], 45)
            self.assertEqual(capture.completed_batch.call_count, 45)
            self.assertEqual(json.loads((output / operator.INPUTS[1]).read_text())["items"], 2880)
            self.assertTrue((failed / "receipt.json").exists())

    def test_invalid_completed_batch_is_never_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, original, alias, _, output, source, controller, capture = self.fixture(temporary)
            capture.completed_batch.side_effect = ValueError("invalid bytes")
            with patch.object(operator, "ORIGINAL", original), patch.object(operator, "BANK", alias), patch.object(operator, "CONTROLLER_SHA", operator.sha(source)), patch.object(operator, "CAPTURE_SHA", operator.sha(source)), patch.object(operator, "load", side_effect=[controller, capture]):
                with self.assertRaises(ValueError):
                    operator.harvest(output)
            self.assertFalse((output / operator.INPUTS[0]).exists())

    def test_duplicate_completed_attempt_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, original, alias, actual, output, source, controller, capture = self.fixture(temporary)
            duplicate = actual / "training/batch_0000-attempt_02"
            duplicate.mkdir()
            (duplicate / "receipt.json").write_text('{"status":"complete"}')
            with patch.object(operator, "ORIGINAL", original), patch.object(operator, "BANK", alias), patch.object(operator, "CONTROLLER_SHA", operator.sha(source)), patch.object(operator, "CAPTURE_SHA", operator.sha(source)), patch.object(operator, "load", side_effect=[controller, capture]):
                with self.assertRaises(operator.SubsetFailure):
                    operator.harvest(output)

    def test_active_batch_blocks_harvest(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, original, alias, actual, output, source, controller, capture = self.fixture(temporary)
            (actual / "training/batch_0000/receipt.json").write_text('{"status":"running"}')
            with patch.object(operator, "ORIGINAL", original), patch.object(operator, "BANK", alias), patch.object(operator, "CONTROLLER_SHA", operator.sha(source)), patch.object(operator, "CAPTURE_SHA", operator.sha(source)), patch.object(operator, "load", side_effect=[controller, capture]):
                with self.assertRaises(operator.SubsetFailure):
                    operator.harvest(output)

    def test_existing_supervisor_lock_blocks_harvest(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, _, alias, actual, output, _, _, _ = self.fixture(temporary)
            with (actual / "supervisor.lock").open("a+") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                with patch.object(operator, "BANK", alias):
                    with self.assertRaises(operator.SubsetFailure):
                        operator.harvest(output)

    def test_supervisor_changes_only_module_allowlists(self):
        source = (Path(__file__).parents[1] / "scripts/tranche8_native_supervisor.py").read_bytes()
        result = operator.subset_supervisor(source)
        self.assertEqual(result.count(b"csts_pilot.proposition_subset"), 2)
        compile(result, "subset_supervisor", "exec")
        with self.assertRaises(operator.SubsetFailure):
            operator.subset_supervisor(source + b"\n")

    def test_transport_compiles_and_only_installs_regular_declared_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            records = b"[]\n"
            (directory / operator.INPUTS[0]).write_bytes(records)
            (directory / operator.INPUTS[1]).write_text(json.dumps({"items": 2880, "records_sha256": operator.sha(records)}))
            captured = []
            def remote(script, *args):
                compile(script, "subset_import", "exec")
                captured.append(script)
                return {"status": "complete"}
            native = SimpleNamespace(copy_to_gpu=Mock(return_value=("/tmp/task-archive", "a"*64)), preamble=Mock(return_value=""), remote=remote)
            operator.transfer(native, "a"*40, directory)
            self.assertIn("member.isfile()", captured[0])
            self.assertIn("len(stream.getmembers())==len(expected)", captured[0])
            self.assertNotIn("extractall", captured[0])

    def test_status_writes_are_fixed(self):
        with self.assertRaises(operator.SubsetFailure):
            operator.publish("unrelated.txt", b"content")

    def test_subset_status_exposes_only_curated_source_free_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            captured = []
            def remote(script, *args):
                compile(script, "subset_status", "exec")
                captured.append(script)
                return {"preparation": {"training_available_records": 2880}, "result": {"promising_for_full_generation": False}, "epoch_zero_metrics": {"saved_qwen": {"n": 30}}}
            native = SimpleNamespace(native_status=Mock(return_value={"status": "running", "result": {"metrics": {}}}), preamble=Mock(return_value=""), remote=remote)
            result = operator.subset_status(native, "a"*40, Path(temporary))
            self.assertEqual(result["preparation"]["training_available_records"], 2880)
            self.assertFalse(result["result"]["promising_for_full_generation"])
            self.assertIn("epoch_zero_metrics", result)
            self.assertNotIn("training_capture", captured[0])
            self.assertNotIn("predictions", captured[0])


if __name__ == "__main__":
    unittest.main()
