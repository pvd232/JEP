"""Check held-out transport release, retry and archival boundaries offline."""

import importlib.util
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


transport = load("test_transport", "scripts/tranche8_test_capture.py")
capture = load("frozen_capture", "csts_pilot/proposition_capture.py")
OPERATOR = "a" * 40
NATIVE = "b" * 40
ITEMS = [{"id": "one", "passage": "A red car.", "condition": "car color"}]


class TestTransport(unittest.TestCase):
    def test_native_eligibility_is_first_and_uses_owner_source_pin(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            transport, "WORK_ROOT", Path(directory)
        ), patch.object(
            transport, "native_release", side_effect=transport.TestCaptureFailure("ineligible")
        ) as release, patch.object(transport, "fetch_inventory") as inventory, patch.object(
            transport, "fetch_capture"
        ) as fetch:
            with self.assertRaises(transport.TestCaptureFailure):
                transport.capture_and_evaluate(OPERATOR, 4, NATIVE)
            self.assertEqual(release.call_args.args[0], NATIVE)
            inventory.assert_not_called()
            fetch.assert_not_called()

    def failed_attempt(self, root, returncode=0, inputs=None, tool=False):
        root.mkdir(exist_ok=True)
        (root / "receipt.json").write_text(json.dumps({"status": "failed", "returncode": returncode}))
        (root / "inputs.json").write_text(json.dumps(ITEMS if inputs is None else inputs))
        events = [{"type": "turn.completed", "usage": {}}]
        if tool:
            events.insert(0, {"type": "item.completed", "item": {"type": "command_execution"}})
        (root / "events.jsonl").write_text("\n".join(json.dumps(x) for x in events) + "\n")
        (root / "response.json").write_text('{"records":[]}')

    def test_response_defect_can_retry_but_cli_tool_and_changed_inputs_cannot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, code, changed, tool, expected in (
                ("response", 0, None, False, True),
                ("cli", 1, None, False, False),
                ("tool", 0, None, True, False),
                ("input", 0, [dict(ITEMS[0], passage="A blue car.")], False, False),
            ):
                path = root / name
                self.failed_attempt(path, code, changed, tool)
                self.assertEqual(transport.response_failure_only(capture, path, ITEMS), expected)

    def test_fourth_attempt_is_refused_without_removing_prior_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "batch_0000-attempt_04"
            path.mkdir()
            with self.assertRaises(transport.TestCaptureFailure):
                transport.attempt_directories(Path(directory))
            self.assertTrue(path.is_dir())

    def test_frozen_policy_rejects_model_or_prompt_change(self):
        release = {"generation_policy": {
            "generation_template_sha256": transport.sha(capture.PROMPT.encode()),
            "schema_sha256": transport.sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode()),
            "model_alias": capture.MODEL, "reasoning_effort": capture.EFFORT,
        }}
        self.assertEqual(transport.frozen_policy(capture, release), release["generation_policy"])
        release["generation_policy"]["model_alias"] = "changed"
        with self.assertRaises(transport.TestCaptureFailure):
            transport.frozen_policy(capture, release)

    def test_final_archive_preserves_incomplete_attempt_and_queues_native_sealing(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            root = directory / "capture"
            attempt = root / "test/batch_0000"
            attempt.mkdir(parents=True)
            (attempt / "partial-response.json").write_text("preserved incomplete response")
            for name in ("launch.json", "generation_inputs.json", "group_ids.json", "pre_generation.json", "proposition_capture.py"):
                (root / name).write_text("{}\n")
            scripts = []

            def remote(script, *args):
                compile(script, "native_checkpoint", "exec")
                scripts.append(script)
                return {"native_path": "native/closed-archive", "publication_queue": "native/queue"}

            with patch.object(transport, "run", return_value=b""), patch.object(
                transport, "remote", side_effect=remote
            ):
                state = transport.checkpoint(root, directory, NATIVE, "c" * 64, final=True)
            archive = directory / state["checkpoints"][0]["name"]
            self.assertTrue(archive.exists())
            self.assertTrue((attempt / "partial-response.json").exists())
            with tarfile.open(archive) as stream:
                self.assertIn("test/batch_0000/partial-response.json", stream.getnames())
            self.assertIn("seal_one", scripts[0])
            self.assertEqual(state["checkpoints"][0]["publication_queue"], "native/queue")


if __name__ == "__main__":
    unittest.main()
