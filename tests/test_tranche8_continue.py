"""Check the operational boundaries of a resumable, paid capture."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from csts_pilot import proposition_capture as capture

SPEC = importlib.util.spec_from_file_location(
    "tranche8_continue", Path(__file__).parents[1] / "scripts/tranche8_continue.py"
)
assert SPEC is not None and SPEC.loader is not None
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


class ContinuationTests(unittest.TestCase):
    def test_passed_gate_cannot_authorize_another_source_or_prompt(self) -> None:
        from csts_pilot import proposition_provenance as verifier

        source = Path(capture.__file__).read_bytes()
        audit = Path(__file__).parents[1] / "training_outputs/proposition_audit"
        gate_text = verifier.text(audit / "fresh_gate.json")
        gate = json.loads(gate_text)
        evidence = verifier.audit_evidence(audit)
        controller.verify_gate(gate, capture, source, evidence, gate_text)
        with self.assertRaises(controller.ContinuationFailure):
            controller.verify_gate(gate, capture, source + b"\n", evidence, gate_text)
        changed = {**gate, "generation_template_sha256": "0" * 64}
        with self.assertRaises(ValueError):
            controller.verify_gate(
                changed, capture, source, evidence, json.dumps(changed)
            )
        with self.assertRaises(controller.ContinuationFailure):
            controller.verify_gate({"passed": True}, capture, source)

    def failed_batch(self, root: Path, returncode: int = 0, tool: bool = False) -> Path:
        directory = root / "training/batch_0000"
        directory.mkdir(parents=True)
        controller.save(
            directory / "receipt.json",
            {"status": "failed", "returncode": returncode, "items": 1},
        )
        events = [
            {
                "type": "item.completed",
                "item": {"type": "command_execution" if tool else "agent_message"},
            },
            {"type": "turn.completed", "usage": {"input_tokens": 1}},
        ]
        (directory / "events.jsonl").write_text(
            "\n".join(json.dumps(event) for event in events)
        )
        controller.save(
            directory / "inputs.json",
            [{"id": "x", "passage": "A cat sleeps.", "condition": "animal"}],
        )
        controller.save(
            directory / "response.json",
            {
                "records": [
                    {
                        "id": "x",
                        "status": "answered",
                        "target": "animal",
                        "attribute": "type",
                        "answer": "cat",
                        "evidence": ["a cat"],
                    }
                ]
            },
        )
        return directory

    def test_bad_quote_can_retry_under_identical_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.failed_batch(root)
            self.assertTrue(controller.retryable_output_failures(root, capture))

    def test_cli_failure_is_not_retried(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.failed_batch(root, returncode=1)
            self.assertFalse(controller.retryable_output_failures(root, capture))

    def test_tool_event_is_not_retried(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.failed_batch(root, tool=True)
            self.assertFalse(controller.retryable_output_failures(root, capture))

    def test_failed_attempt_and_success_do_not_double_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.failed_batch(root)
            for suffix in ("-attempt_02", "-attempt_03"):
                directory = root / ("training/batch_0000" + suffix)
                directory.mkdir()
                controller.save(
                    directory / "receipt.json", {"status": "complete", "items": 1}
                )
            self.assertEqual(controller.counts(root)["completed_items"], 1)
            self.assertEqual(controller.counts(root)["failed_attempts"], 1)

    def test_checkpoint_name_binds_archive_bytes_and_does_not_mutate_batch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            root = directory / "output"
            self.failed_batch(root)
            controller.save(root / "launch.json", {"frozen": True})
            (directory / "proposition_capture.py").write_text("frozen source")
            controller.save(directory / "audit_gate.json", {"passed": True})
            original = (root / "training/batch_0000/receipt.json").read_bytes()
            with patch.object(controller, "run", return_value=b"checkpoint_verified"):
                state = controller.checkpoint(root, directory, {})
            receipt = state["checkpoints"][0]
            archive = directory / receipt["name"]
            self.assertEqual(controller.sha(archive.read_bytes()), receipt["sha256"])
            self.assertIn(receipt["sha256"][:16], archive.name)
            self.assertEqual(
                (root / "training/batch_0000/receipt.json").read_bytes(), original
            )


if __name__ == "__main__":
    unittest.main()
