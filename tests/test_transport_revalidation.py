"""Reject warning look-alikes and derive scores without rewriting original captures."""

import copy
import json
from pathlib import Path
import shutil
import unittest

from csts_pilot import extraction_comparison as experiment
from csts_pilot import transport_revalidation as amendment
import test_extraction_comparison as fixture_module


def events(payload="3", warning=None):
    result = [{"type": "thread.started", "thread_id": "fixture-thread"},
              {"type": "turn.started"}]
    if warning is not None:
        result.append({"type": "error", "message": warning})
    result.extend([{"type": "item.completed", "item": {"type": "agent_message",
                    "text": json.dumps({"payload": payload})}}, {"type": "turn.completed"}])
    return result


class CompletedCaptureTest(unittest.TestCase):
    def test_exact_known_warnings_with_final_answer_are_accepted(self):
        for message in (
            "Reconnecting... 2/5 (request timed out)",
            "Reconnecting... 2/5 (stream disconnected before completion: invalid peer certificate: UnknownIssuer)",
        ):
            self.assertEqual(amendment.validate_completed_capture(events(warning=message), {"payload": "3"}), "3")

    def test_warning_lookalikes_and_genuine_errors_are_rejected(self):
        for message in (
            "Reconnecting... 2/5 (request timed out) trailing error",
            "Reconnecting... 0/5 (request timed out)",
            "Reconnecting... 6/5 (request timed out)",
            "Reconnecting... 2/6 (request timed out)",
            "Reconnecting... 2/5 (permission denied)",
            "Reconnecting... 2/5 (invalid peer certificate)",
            "Model request failed", "Authentication failed", "request timed out",
        ):
            with self.subTest(message=message), self.assertRaises(ValueError):
                amendment.validate_completed_capture(events(warning=message), {"payload": "3"})

    def test_warning_never_replaces_completion_or_allows_tools(self):
        valid = events(warning="Reconnecting... 2/5 (request timed out)")
        for altered in (
            valid[:-1], valid + [{"type": "turn.failed"}],
            valid[:-1] + [{"type": "turn.failed"}, valid[-1]],
            valid[:-1] + [valid[-1], valid[-1]],
            valid[:-1] + [{"type": "item.completed", "item": {"type": "command_execution"}}, valid[-1]],
            valid[:-1] + [{"type": "tool.call"}, valid[-1]],
            valid[:-1] + [copy.deepcopy(valid[-2]), valid[-1]],
            [valid[0], *valid],
            [valid[1], *valid],
        ):
            with self.subTest(events=altered), self.assertRaises(ValueError):
                amendment.validate_completed_capture(altered, {"payload": "3"})

    def test_agent_response_must_agree_exactly_and_not_repeat_keys(self):
        for payload in ('{"payload":"4"}', '{"payload":"3","payload":"3"}',
                        '{"payload":"3","extra":false}', 'not JSON'):
            altered = events()
            altered[-2]["item"]["text"] = payload
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                amendment.validate_completed_capture(altered, {"payload": "3"})

    def test_original_numeric_constraints_remain_strict(self):
        for payload in ("NaN", "Infinity", "true", "null", '"3"', "0.9", "5.1"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                amendment._score(payload)


class DerivationTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.ComparisonTest(
            methodName="test_projection_is_label_blind_and_deduplicates_sources")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.seal()
        self.fixture.run_gpt("gpt_direct", "gpt_propositions")
        self.run = self.fixture.output
        self.frozen = self.fixture.root / "frozen-code"
        destination = self.frozen / "csts_pilot"
        destination.mkdir(parents=True)
        for name in experiment.code_identity():
            shutil.copy2(Path(experiment.__file__).with_name(name), destination / name)

    def make_original_warning_failure(self, arm):
        path = next((self.run / "captures" / arm).glob("*/result.json"))
        result = experiment.read(path)
        folder = path.parent
        raw_events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]
        raw_events.insert(2, {"type": "error", "message": "Reconnecting... 2/5 (request timed out)"})
        (folder / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in raw_events))
        result.update(valid=False, payload=None, error="Codex inference failed")
        result.pop("parsed", None)
        result["raw_artifacts"] = {p.name: experiment.digest(p.read_bytes())
                                   for p in folder.iterdir() if p.is_file() and p.name != "result.json"}
        path.write_bytes(experiment.encoded(result))

    def snapshot(self):
        return {str(p.relative_to(self.run)): p.read_bytes()
                for p in self.run.rglob("*") if p.is_file()}

    def test_parser_amendment_uses_all_original_rows_and_preserves_every_byte(self):
        self.make_original_warning_failure("gpt_direct")
        self.make_original_warning_failure("gpt_propositions")
        before = self.snapshot()
        output = self.fixture.root / "amendment"
        metrics = amendment.derive(self.run, self.frozen, output)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(metrics["new_model_calls"], 0)
        self.assertFalse(metrics["sealed_review_panel_changed"])
        self.assertEqual(metrics["original_first_pass"]["gpt_direct"],
                         {"expected": 3, "original_valid": 2, "amended_valid": 3})
        self.assertEqual(metrics["original_first_pass"]["gpt_propositions"],
                         {"expected": 5, "original_valid": 4, "amended_valid": 5})
        self.assertEqual(metrics["direct_similarity"]["n"], 3)
        self.assertEqual(metrics["direct_similarity"]["mse_1_5"], 0)
        self.assertEqual(metrics["direct_similarity"]["spearman"], 1)
        self.assertEqual(metrics["proposition_amendment_scope"], "sensitivity_only")
        with self.assertRaises(ValueError):
            amendment.derive(self.run, self.frozen, output)

    def test_changed_original_capture_rejects_derivation(self):
        path = next((self.run / "captures" / "gpt_direct").glob("*/response.json"))
        path.write_text('{"payload":"5"}')
        with self.assertRaisesRegex(ValueError, "[Rr]aw capture changed"):
            amendment.derive(self.run, self.frozen, self.fixture.root / "amendment")

    def test_frozen_owner_rejects_prompt_change_even_with_rewritten_local_hashes(self):
        path = next((self.run / "captures" / "gpt_direct").glob("*/request.json"))
        request = experiment.read(path)
        request["prompt"] = "A different scientific instruction."
        path.write_bytes(experiment.encoded(request))
        result_path = path.parent / "result.json"
        result = experiment.read(result_path)
        result["raw_artifacts"]["request.json"] = experiment.digest(path.read_bytes())
        result_path.write_bytes(experiment.encoded(result))
        with self.assertRaisesRegex(ValueError, "Frozen origin verifier rejected"):
            amendment.derive(self.run, self.frozen, self.fixture.root / "amendment")


if __name__ == "__main__":
    unittest.main()
