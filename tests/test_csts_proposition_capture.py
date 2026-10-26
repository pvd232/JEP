"""Check generation blinding, source-group batching and evidence validation."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from csts_pilot.proposition_capture import (
    EFFORT,
    MODEL,
    PROMPT,
    SCHEMA,
    batches,
    capture_lock,
    checked_events,
    checked_records,
    cli_command,
    completed_batch,
    request_batch,
    sha,
    validate_inputs,
)


def item(identity="one", passage="Two horses are ridden while a bull is pursued."):
    return {"id": identity, "passage": passage, "condition": "type of animal"}


def answer(identity="one"):
    return {
        "id": identity,
        "status": "answered",
        "target": "animals",
        "attribute": "type and roles",
        "answer": "Horses are ridden; a bull is pursued.",
        "evidence": ["Two horses are ridden", "a bull is pursued"],
    }


class CaptureChecks(unittest.TestCase):
    def completed_fixture(self, directory):
        directory.mkdir()
        sources = [item()]
        prompt = PROMPT + json.dumps(sources, ensure_ascii=False)
        files = {
            "prompt.txt": prompt,
            "inputs.json": json.dumps(sources),
            "schema.json": json.dumps(SCHEMA),
            "response.json": json.dumps({"records": [answer()]}),
            "records.json": json.dumps([answer()]),
            "events.jsonl": json.dumps({"type": "turn.completed", "usage": {"output_tokens": 2}}),
        }
        for filename, content in files.items():
            (directory / filename).write_text(content)
        receipt = {"status": "complete", "returncode": 0, "model_alias": MODEL,
                   "reasoning_effort": EFFORT, "command": cli_command(directory, "/test/cli"),
                   "items": 1, "labels_or_companion_fields_provided": False,
                   "tools_permitted": False, "usage": {"output_tokens": 2}}
        for filename, field in (("prompt.txt", "prompt_sha256"), ("inputs.json", "input_sha256"), ("schema.json", "schema_sha256"), ("events.jsonl", "events_sha256"), ("response.json", "response_sha256"), ("records.json", "records_sha256")):
            receipt[field] = sha((directory / filename).read_bytes())
        (directory / "receipt.json").write_text(json.dumps(receipt))
        return receipt

    def test_only_blinded_single_passage_fields_are_accepted(self):
        validate_inputs([item()])
        for field in ("rating", "sentence2", "prediction", "group_id"):
            with self.assertRaises(ValueError):
                validate_inputs([dict(item(), **{field: "leak"})])

    def test_batches_never_share_original_groups(self):
        items = [item(str(i)) for i in range(6)]
        groups = {str(i): str(i // 2) for i in range(6)}
        selected = batches(items, groups, 64)
        self.assertEqual([len(batch) for batch in selected], [3, 3])
        for batch in selected:
            self.assertEqual(len({groups[row["id"]] for row in batch}), len(batch))
        self.assertEqual({row["id"] for batch in selected for row in batch}, set(groups))

    def test_paraphrases_are_valid_with_exact_supporting_spans(self):
        self.assertNotIn(answer()["answer"], item()["passage"])
        result = checked_records([item()], {"records": [answer()]})
        self.assertEqual(result, [answer()])

    def test_wrong_source_spans_and_duplicate_or_missing_ids_fail(self):
        wrong = dict(answer(), evidence=["three horses"])
        for records in ([wrong], [], [answer(), answer()]):
            with self.assertRaises(ValueError):
                checked_records([item()], {"records": records})

    def test_unknown_answers_do_not_fabricate_evidence(self):
        missing = dict(answer(), status="not_specified", answer="", evidence=[])
        self.assertEqual(checked_records([item()], {"records": [missing]}), [missing])
        with self.assertRaises(ValueError):
            checked_records([item()], {"records": [dict(missing, answer="none")]})

    def test_word_ceiling_and_empty_answered_evidence_fail(self):
        for changed in (
            dict(answer(), answer="word " * 61),
            dict(answer(), evidence=[]),
            dict(answer(), target=""),
        ):
            with self.assertRaises(ValueError):
                checked_records([item()], {"records": [changed]})

    def test_tools_and_incomplete_turns_fail_event_check(self):
        normal = [
            {"type": "thread.started", "thread_id": "opaque"},
            {"type": "turn.started"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "{}"}},
            {"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 2}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            def save(events):
                path.write_text("\n".join(json.dumps(event) for event in events))
            save(normal)
            self.assertEqual(checked_events(path)["output_tokens"], 2)
            tool = copy.deepcopy(normal)
            tool[2]["item"]["type"] = "command_execution"
            save(tool)
            with self.assertRaises(ValueError):
                checked_events(path)
            save(normal[:-1])
            with self.assertRaises(ValueError):
                checked_events(path)

    def test_completed_request_reuses_without_new_inference(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            directory = root / "batch_0000"
            self.completed_fixture(directory)
            with mock.patch("csts_pilot.proposition_capture.capture_batch") as capture:
                receipt = request_batch([item()], root, 0, "/test/cli", 30, True)
                self.assertTrue(receipt["reused"])
                capture.assert_not_called()

    def test_completed_request_tampering_fails_instead_of_regenerating(self):
        for filename in ("inputs.json", "prompt.txt", "schema.json", "events.jsonl", "response.json", "records.json"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as parent:
                directory = Path(parent) / "batch_0000"
                self.completed_fixture(directory)
                with (directory / filename).open("a") as stream:
                    stream.write(" ")
                with self.assertRaises(ValueError):
                    completed_batch([item()], directory, "/test/cli")

    def test_failed_request_is_preserved_and_retry_uses_new_attempt_directory(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            failed = root / "batch_0000-attempt_05"
            failed.mkdir()
            (failed / "receipt.json").write_text('{"status":"failed"}')
            before = (failed / "receipt.json").read_bytes()
            with mock.patch("csts_pilot.proposition_capture.capture_batch", return_value={}) as capture:
                request_batch([item()], root, 0, "/test/cli", 30, True)
                self.assertEqual(capture.call_args.args[1], root / "batch_0000-attempt_06")
            self.assertEqual((failed / "receipt.json").read_bytes(), before)


    def test_running_attempt_requires_explicit_abandoned_recovery(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            interrupted = root / "batch_0000"
            interrupted.mkdir()
            receipt = interrupted / "receipt.json"
            receipt.write_text('{"status":"running"}')
            before = receipt.read_bytes()
            with mock.patch("csts_pilot.proposition_capture.capture_batch", return_value={}) as capture:
                with self.assertRaisesRegex(RuntimeError, "recover-abandoned"):
                    request_batch([item()], root, 0, "/test/cli", 30, True)
                capture.assert_not_called()
                request_batch([item()], root, 0, "/test/cli", 30, True, True)
                self.assertEqual(capture.call_args.args[1], root / "batch_0000-attempt_02")
            self.assertEqual(receipt.read_bytes(), before)

    def test_live_orphaned_cli_keeps_batch_locked(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            child = None
            try:
                with capture_lock(root / "batch_0000.lock") as descriptor:
                    child = subprocess.Popen(
                        [sys.executable, "-c", "import time; time.sleep(30)"],
                        pass_fds=(descriptor,),
                    )
                # Only the CLI owns the descriptor now; a parent restart must
                # still fail even with explicit abandoned-attempt recovery.
                with mock.patch("csts_pilot.proposition_capture.capture_batch") as capture:
                    with self.assertRaisesRegex(RuntimeError, "owned"):
                        request_batch([item()], root, 0, "/test/cli", 30, True, True)
                    capture.assert_not_called()
            finally:
                if child is not None:
                    child.terminate()
                    child.wait(timeout=5)
            with capture_lock(root / "batch_0000.lock"):
                pass

    def test_capture_cli_inherits_partition_and_batch_ownership(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            partition = root / "partition.capture.lock"
            children = []

            def fake_cli(_command, **kwargs):
                children.append(subprocess.Popen(
                    [sys.executable, "-c", "import time; time.sleep(30)"],
                    pass_fds=kwargs["pass_fds"],
                ))
                directory = kwargs["cwd"]
                (directory / "response.json").write_text(json.dumps({"records": [answer()]}))
                kwargs["stdout"].write(json.dumps({"type": "turn.completed", "usage": {"output_tokens": 2}}))
                return SimpleNamespace(returncode=0)

            try:
                with capture_lock(partition) as partition_fd, mock.patch(
                    "csts_pilot.proposition_capture.subprocess.check_output", return_value="fixture"
                ), mock.patch("csts_pilot.proposition_capture.subprocess.run", side_effect=fake_cli):
                    request_batch([item()], root, 0, "/test/cli", 30, False, partition_lock_fd=partition_fd)
                # The child retains both output ownership and the current batch
                # after every descriptor in the original capture parent closes.
                for path in (partition, root / "batch_0000.lock"):
                    with self.assertRaisesRegex(RuntimeError, "owned"), capture_lock(path):
                        self.fail("A live CLI lost capture ownership.")
            finally:
                for child in children:
                    child.terminate()
                    child.wait(timeout=5)

    def test_partition_lock_rejects_a_second_owner(self):
        with tempfile.TemporaryDirectory() as parent:
            path = Path(parent) / "partition.capture.lock"
            with capture_lock(path), self.assertRaisesRegex(RuntimeError, "owned"), capture_lock(path):
                self.fail("A second owner acquired the capture lock.")


if __name__ == "__main__":
    unittest.main()
