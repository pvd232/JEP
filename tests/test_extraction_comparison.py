"""Offline counterexamples for the extraction comparison's scientific controls."""

import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import shutil
import unittest
from unittest.mock import patch

from csts_pilot import extraction_comparison as experiment
from csts_pilot.extraction_native import NATIVE_MODELS


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = self.root / "data"
        self.data.mkdir()
        pairs = [
            ("A black dog.", "A tan dog.", "color of dogs", "g1"),
            ("A black dog.", "A white dog.", "color of dogs", "g1"),
            ("Two people run.", "A person walks.", "activity", "g2"),
        ]
        self.rows = []
        for index, (left, right, condition, group) in enumerate(pairs, 1):
            rating = float(2 * index - 1)
            self.rows.append({"row_id": f"v{index}", "sentence1": left,
                              "sentence2": right, "condition": condition,
                              "rating": rating, "target": (rating - 1) / 4,
                              "pair_id": f"pair{index}", "group_id": group})
        self.config = {"model": "gpt-6.1-sol", "reasoning_effort": "max",
                       "arms": list(experiment.ARMS), "native_models": copy.deepcopy(NATIVE_MODELS),
                       "sample_rows": 3, "max_output_tokens": 512, "max_payload_bytes": 65536,
                       "sample_seed": 42, "review_seed": 7, "timeout_seconds": 1,
                       "dataset": {"revision": "synthetic-test-fixture"}}
        for split in ("validation", "test"):
            rows = copy.deepcopy(self.rows)
            if split == "test":
                for row in rows:
                    row["row_id"] = row["row_id"].replace("v", "t")
            raw = experiment.encoded(rows)
            (self.data / (split + ".json")).write_bytes(raw)
            self.config["dataset"][split] = {"rows": len(rows),
                                             "sha256": experiment.digest(raw)}
        self.config_path = self.root / "config.json"
        self.save_config()
        self.output = self.root / "run"
        experiment.prepare(self.config_path, self.data, self.output)

    def save_config(self):
        self.config_path.write_bytes(experiment.encoded(self.config))

    def seal(self):
        path = self.root / "references.json"
        sources = experiment.read(self.output / "sources.json")
        path.write_bytes(experiment.encoded([
            {"id": row["id"], "expected_answer": "Source-supported reference."}
            for row in sources]))
        experiment.seal_references(self.output, path)
        return path

    def payload(self, folder, prompt, config, cli, closed_book):
        """Generate deterministic synthetic responses without model execution."""
        item = json.loads(prompt.split("INPUT:\n")[1])
        if "row_id" in item:
            return str({"v1": 1, "v2": 3, "v3": 5}[item["row_id"]])
        if "propositions" in prompt.split("INPUT:\n")[0]:
            return json.dumps({"status": "answered", "reason": "", "propositions": [
                {"text": item["passage"], "source_quote": item["passage"],
                 "support_status": "explicit", "reason": ""}]})
        return json.dumps({"status": "answered", "reason": "",
                           "entities": [{"id": "e1", "type": "subject",
                                         "source_quote": item["passage"], "count": 1}],
                           "facts": [{"entity_id": "e1", "predicate": "description",
                                      "value": item["passage"],
                                      "source_quote": item["passage"],
                                      "support_status": "explicit", "reason": ""}]})

    def run_gpt(self, *arms, fail=None):
        def capture(*args):
            if fail and args[0].parent.name == fail:
                raise ValueError("Synthetic failure")
            return self.write_capture(args[0], self.payload(*args))
        with patch.object(experiment, "capture_codex", side_effect=capture):
            for arm in arms:
                experiment.run_arm(self.output, arm, "unused-cli", execute=True)

    def write_capture(self, folder, payload):
        """Retain synthetic raw artifacts through the real result-validation path."""
        response = {"payload": payload}
        events = [{"type": "thread.started", "thread_id": "fixture-thread"},
                  {"type": "turn.started"},
                  {"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(response)}},
                  {"type": "turn.completed"}]
        (folder / "response.json").write_bytes(experiment.encoded(response))
        (folder / "events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events))
        return payload

    def call_cli(self, *arguments):
        """Exercise the actual argument parser and dispatch without a subprocess."""
        output = io.StringIO()
        with patch("sys.argv", ["extraction_comparison", *map(str, arguments)]):
            with contextlib.redirect_stdout(output):
                experiment.main()
        return json.loads(output.getvalue())

    def completed_reviews(self, reject_arm=None):
        links = {row["candidate_id"]: row for row in
                 experiment.read(self.output / "review-map.json")}
        rows = []
        for item in experiment.read(self.output / "review-packet.json"):
            accepted = links[item["candidate_id"]]["arm"] != reject_arm
            rows.append({"candidate_id": item["candidate_id"], "reviewer_id": "reviewer-1",
                         **{key: accepted for key in experiment.FIELDS},
                         "rationale": "Synthetic controlled judgment."})
        path = self.root / "reviews.json"
        path.write_bytes(experiment.encoded(rows))
        return path

    def test_projection_is_label_blind_and_deduplicates_sources(self):
        sources = experiment.items_for(self.output, "gpt_json")
        pairs = experiment.items_for(self.output, "gpt_direct")
        self.assertEqual(len(sources), 5)
        self.assertEqual(len(pairs), 3)
        self.assertEqual(len({item["id"] for item in sources}), 5)
        for item in sources:
            self.assertEqual(set(item), {"id", "passage", "condition"})
        for item in pairs:
            self.assertEqual(set(item), {"row_id", "sentence1", "sentence2", "condition"})
        for item in sources:
            prompt = experiment.prompt_for(item, "gpt_json")
            self.assertNotIn("group_id", prompt)
            self.assertEqual(set(json.loads(prompt.split("INPUT:\n")[1])),
                             {"passage", "condition"})

    def test_dataset_hash_and_scale_are_enforced(self):
        for bad in ("hash", "scale", "nan_target", "boolean_rating"):
            with self.subTest(bad=bad):
                rows = copy.deepcopy(self.rows)
                if bad == "scale":
                    rows[0]["target"] = 2
                elif bad == "nan_target":
                    rows[0]["target"] = float("nan")
                elif bad == "boolean_rating":
                    rows[0]["rating"], rows[0]["target"] = True, False
                raw = experiment.encoded(rows)
                (self.data / "validation.json").write_bytes(raw)
                self.config["dataset"]["validation"]["sha256"] = (
                    "0" * 64 if bad == "hash" else experiment.digest(raw))
                self.save_config()
                with self.assertRaises(ValueError):
                    experiment.prepare(self.config_path, self.data, self.root / ("bad-" + bad))

    def test_duplicate_row_ids_fail_preparation(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["row_id"] = rows[0]["row_id"]
        raw = experiment.encoded(rows)
        (self.data / "validation.json").write_bytes(raw)
        self.config["dataset"]["validation"]["sha256"] = experiment.digest(raw)
        self.save_config()
        with self.assertRaises(ValueError):
            experiment.prepare(self.config_path, self.data, self.root / "duplicate")

    def test_artifact_mutation_fails_verification(self):
        with (self.output / "sources.json").open("a") as handle:
            handle.write(" ")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            experiment.verify_run(self.output)

    def test_code_mutation_fails_verification(self):
        with patch.object(experiment, "code_identity", return_value={"changed": "code"}):
            with self.assertRaisesRegex(ValueError, "protocol changed"):
                experiment.verify_run(self.output)

    def test_test_requires_identical_validation_protocol(self):
        with self.assertRaises(ValueError):
            experiment.prepare(self.config_path, self.data, self.root / "test-no-lock", split="test")
        result = experiment.prepare(
            self.config_path, self.data, self.root / "test", split="test",
            protocol_lock=self.output / "protocol.json")
        self.assertEqual(result["rows"], 3)
        self.config["max_output_tokens"] += 1
        self.save_config()
        with self.assertRaises(ValueError):
            experiment.prepare(self.config_path, self.data, self.root / "test-changed",
                               split="test", protocol_lock=self.output / "protocol.json")

    def test_codex_tool_use_failure_and_extra_envelope_are_rejected(self):
        valid = [{"type": "thread.started", "thread_id": "fixture-thread"},
                 {"type": "turn.started"},
                 {"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps({"payload": "3"})}},
                 {"type": "turn.completed"}]
        self.assertEqual(experiment.completed_codex(valid, {"payload": "3"}), "3")
        for events, response in (
            (valid + [{"type": "item.completed", "item": {"type": "command_execution"}}],
             {"payload": "3"}),
            ([{"type": "turn.failed"}], {"payload": "3"}),
            (valid + [{"type": "turn.completed"}], {"payload": "3"}),
            (valid, {"payload": "3", "extra": "x"}),
        ):
            with self.assertRaises(ValueError):
                experiment.completed_codex(events, response)

    def test_direct_scores_require_finite_number_in_range(self):
        for payload in ("NaN", "Infinity", "true", "false", "0.9", "5.1", '"3"', "null"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                experiment.validate_payload(payload, "gpt_direct", {})
        self.assertEqual(experiment.validate_payload("3.25", "gpt_direct", {}), {"score": 3.25})

    def test_reference_coverage_and_pre_capture_seal(self):
        references = self.root / "bad-references.json"
        sources = experiment.read(self.output / "sources.json")
        values = [{"id": row["id"], "expected_answer": "reference"} for row in sources]
        values[1]["id"] = values[0]["id"]
        references.write_bytes(experiment.encoded(values))
        with self.assertRaises(ValueError):
            experiment.seal_references(self.output, references)
        with patch.object(experiment, "capture_codex") as capture:
            with self.assertRaises(ValueError):
                experiment.run_arm(self.output, "gpt_propositions", "unused", execute=True)
            capture.assert_not_called()

    def test_references_cannot_be_sealed_after_capture(self):
        self.seal()
        self.run_gpt("gpt_propositions")
        with self.assertRaises(ValueError):
            experiment.seal_references(self.output, self.root / "references.json")

    def test_failed_direct_predictions_preserve_denominator(self):
        self.seal()
        self.run_gpt("gpt_direct", fail="gpt_direct")
        result = experiment.summarize(self.output)
        self.assertEqual(result["arms"]["gpt_direct"], {"expected": 3, "valid": 0, "failed": 3})
        self.assertEqual(result["direct_similarity"]["status"], "incomplete_no_complete_case_score")

    def test_direct_metric_uses_retained_labels_and_full_coverage(self):
        self.seal()
        self.run_gpt("gpt_direct")
        result = experiment.summarize(self.output)
        self.assertEqual(result["direct_similarity"]["n"], 3)
        self.assertAlmostEqual(result["direct_similarity"]["mse_1_5"], 0.0)
        self.assertAlmostEqual(result["direct_similarity"]["spearman"], 1.0)

    def test_review_packet_hides_arm_source_ids_and_labels(self):
        self.seal()
        self.run_gpt("gpt_propositions", "gpt_json")
        experiment.review_packet(self.output, ["gpt_propositions", "gpt_json"])
        packet = experiment.read(self.output / "review-packet.json")
        self.assertEqual(len(packet), 10)
        for item in packet:
            self.assertEqual(set(item), {"candidate_id", "passage", "condition",
                                        "expected_answer", "raw_output", "structurally_valid"})
        self.assertEqual(len({item["candidate_id"] for item in packet}), 10)

    def test_component_paired_fidelity_and_duplicate_review_rejection(self):
        self.seal()
        self.run_gpt("gpt_propositions", "gpt_json")
        experiment.review_packet(self.output, ["gpt_propositions", "gpt_json"])
        path = self.completed_reviews(reject_arm="gpt_json")
        result = experiment.summarize(self.output, path)
        paired = result["paired_vs_propositions"]["gpt_json"]
        self.assertEqual(paired["mean_difference"], -1.0)
        self.assertEqual(paired["components"], 2)
        self.assertEqual(paired["paired_component_95_ci"], [-1.0, -1.0])
        rows = experiment.read(path)
        rows[1]["candidate_id"] = rows[0]["candidate_id"]
        path.write_bytes(experiment.encoded(rows))
        with self.assertRaises(ValueError):
            experiment.summarize(self.output, path)

    def test_capture_artifact_response_tamper_is_rejected(self):
        self.seal()
        self.run_gpt("gpt_direct")
        folder = self.output / "captures" / "gpt_direct" / "v1"
        response = folder / "response.json"
        response.write_bytes(experiment.encoded({"payload": "5"}))
        with self.assertRaisesRegex(ValueError, "raw capture changed"):
            experiment.load_results(self.output, ["gpt_direct"])

    def test_result_payload_and_parsed_tamper_is_rejected(self):
        self.seal()
        self.run_gpt("gpt_direct")
        path = self.output / "captures" / "gpt_direct" / "v1" / "result.json"
        result = experiment.read(path)
        result["payload"], result["parsed"] = "5", {"score": 5}
        path.write_bytes(experiment.encoded(result))
        with self.assertRaisesRegex(ValueError, "retained model response"):
            experiment.load_results(self.output, ["gpt_direct"])

    def test_failed_parse_retains_raw_payload_and_full_denominator(self):
        self.seal()
        with patch.object(experiment, "capture_codex", side_effect=
                          lambda folder, *args: self.write_capture(folder, "{malformed")):
            experiment.run_arm(self.output, "gpt_json", "unused", execute=True)
        values = experiment.load_results(self.output, ["gpt_json"])["gpt_json"]
        self.assertEqual(len(values), 5)
        self.assertTrue(all(not value["valid"] for value in values.values()))
        self.assertTrue(all(value["payload"] == "{malformed" for value in values.values()))
        self.assertTrue(all("response.json" in value["raw_artifacts"] for value in values.values()))
        summary = experiment.summarize(self.output)
        self.assertEqual(summary["arms"]["gpt_json"]["failed"], 5)
        with self.assertRaises(ValueError):
            experiment.export_arm(self.output, "gpt_json")

    def test_export_retains_status_reason_and_raw_capture_identity(self):
        self.seal()
        record = {"status": "not_specified", "reason": "No supported answer.",
                  "propositions": []}
        with patch.object(experiment, "capture_codex", side_effect=lambda folder, *args:
                          self.write_capture(folder, json.dumps(record))):
            experiment.run_arm(self.output, "gpt_propositions", "unused", execute=True)
        experiment.export_arm(self.output, "gpt_propositions")
        rows = experiment.read(self.output / "downstream-gpt_propositions.json")
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertEqual(row["status"], "not_specified")
            self.assertEqual(row["reason"], "No supported answer.")
            self.assertEqual(row["evidence"], "")
            path = self.output / row["capture_path"]
            self.assertEqual(experiment.digest(path.read_bytes()), row["capture_sha256"])

    def test_operational_then_reviewed_summary_preserves_both_snapshots(self):
        self.seal()
        self.run_gpt("gpt_propositions", "gpt_json")
        operational = experiment.summarize(self.output)
        original = Path(operational["report_path"]).read_bytes()
        experiment.review_packet(self.output, ["gpt_propositions", "gpt_json"])
        review_path = self.completed_reviews()
        reviewed = experiment.summarize(self.output, review_path)
        self.assertEqual(operational["status"], "operational_counts_only")
        self.assertEqual(reviewed["status"], "reviewed_fidelity")
        self.assertNotEqual(operational["report_path"], reviewed["report_path"])
        self.assertEqual(Path(operational["report_path"]).read_bytes(), original)
        self.assertEqual(experiment.summarize(self.output, review_path)["report_path"],
                         reviewed["report_path"])
        self.assertIn("scope_correct", experiment.FIELDS)

    def test_cli_dispatch_prepares_runs_reviews_summarizes_and_exports(self):
        self.output = self.root / "cli-run"
        prepared = self.call_cli("prepare", "--config", self.config_path,
                                 "--data-dir", self.data, "--output", self.output)
        self.assertEqual(prepared["rows"], 3)
        with patch.object(experiment, "capture_codex") as capture:
            direct = self.call_cli("run", "--output", self.output, "--arm", "gpt_direct")
            extraction = self.call_cli("run", "--output", self.output,
                                       "--arm", "gpt_propositions")
            native = self.call_cli("run", "--output", self.output, "--arm", "knowcoder")
            capture.assert_not_called()
        self.assertEqual(direct["requests"], 3)
        self.assertEqual(extraction["requests"], 5)
        self.assertFalse(native["execute"])
        references = self.root / "cli-references.json"
        sources = experiment.read(self.output / "sources.json")
        references.write_bytes(experiment.encoded([
            {"id": item["id"], "expected_answer": "Supported reference."}
            for item in sources]))
        self.call_cli("seal-references", "--output", self.output, "--references", references)

        def capture(folder, *arguments):
            return self.write_capture(folder, self.payload(folder, *arguments))

        with patch.object(experiment, "capture_codex", side_effect=capture) as captured:
            for arm in ("gpt_direct", "gpt_propositions"):
                executed = self.call_cli("run", "--output", self.output,
                                         "--arm", arm, "--cli", "unused", "--execute")
                self.assertTrue(executed["execute"])
            self.assertEqual(captured.call_count, 8)
        operational = self.call_cli("summarize", "--output", self.output)
        self.assertEqual(operational["direct_similarity"]["mse_0_1"], 0.0)
        packet = self.call_cli("review-packet", "--output", self.output,
                               "--arms", "gpt_propositions")
        self.assertEqual(packet["candidates"], 5)
        reviews = self.completed_reviews()
        reviewed = self.call_cli("summarize", "--output", self.output, "--reviews", reviews)
        self.assertEqual(reviewed["status"], "reviewed_fidelity")
        exported = self.call_cli("export", "--output", self.output,
                                 "--arm", "gpt_propositions")
        self.assertEqual(exported["rows"], 5)
        self.assertFalse(exported["similarity_evaluated"])

    def test_cli_help_has_no_inference_side_effects(self):
        output = io.StringIO()
        with patch("sys.argv", ["extraction_comparison", "--help"]):
            with patch.object(experiment, "capture_codex") as capture:
                with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit:
                    experiment.main()
                self.assertEqual(exit.exception.code, 0)
                capture.assert_not_called()
        self.assertIn("prepare", output.getvalue())
        self.assertFalse((self.output / "captures").exists())

    def test_sealed_review_map_tamper_is_rejected(self):
        self.seal()
        self.run_gpt("gpt_propositions", "gpt_json")
        experiment.review_packet(self.output, ["gpt_propositions", "gpt_json"])
        reviews = self.completed_reviews()
        path = self.output / "review-map.json"
        mapping = experiment.read(path)
        mapping[0]["group_id"] = "tampered-component"
        path.write_bytes(experiment.encoded(mapping))
        with self.assertRaisesRegex(ValueError, "review.*changed|Review.*changed"):
            experiment.summarize(self.output, reviews)

    def test_gpt_concurrency_is_bounded_and_records_operator_workers(self):
        self.seal()
        guard = threading.Lock()
        rendezvous = threading.Barrier(2)
        active, peak, calls = 0, 0, 0

        def capture(folder, *arguments):
            nonlocal active, peak, calls
            with guard:
                active += 1
                calls += 1
                peak = max(peak, active)
                synchronize = calls <= 2
            try:
                if synchronize:
                    rendezvous.wait(timeout=2)
                time.sleep(0.01)
                return self.write_capture(folder, self.payload(folder, *arguments))
            finally:
                with guard:
                    active -= 1

        with patch.object(experiment, "capture_codex", side_effect=capture):
            result = experiment.run_arm(self.output, "gpt_propositions", "unused",
                                        execute=True, workers=2)
        self.assertEqual(result["workers"], 2)
        self.assertEqual(calls, 5)
        self.assertEqual(peak, 2)
        self.assertEqual(active, 0)
        values = experiment.load_results(self.output, ["gpt_propositions"])["gpt_propositions"]
        self.assertTrue(all(item["valid"] for item in values.values()))
        attempts = list((self.output / "arm-executions" / "gpt_propositions").glob("attempt-*.json"))
        self.assertEqual(len(attempts), 1)
        receipt = experiment.read(attempts[0])
        self.assertEqual(receipt["workers"], 2)
        self.assertEqual(receipt["pending_requests"], 5)
        with patch.object(experiment, "capture_codex") as capture_again:
            experiment.run_arm(self.output, "gpt_propositions", "unused", execute=True, workers=3)
            capture_again.assert_not_called()
        self.assertEqual(experiment.verify_run(self.output), self.config)

    def test_invalid_workers_fail_before_capture(self):
        for workers in (0, -1, True, False, 1.5, "2", 17):
            with self.subTest(workers=workers), patch.object(experiment, "capture_codex") as capture:
                with self.assertRaisesRegex(ValueError, "workers"):
                    experiment.run_arm(self.output, "gpt_direct", "unused", execute=True,
                                       workers=workers)
                capture.assert_not_called()

    def test_native_parallelism_is_rejected_before_model_loading(self):
        from csts_pilot import extraction_native
        for arm in experiment.NATIVE_ARMS:
            with self.subTest(arm=arm), patch.object(extraction_native, "NativeGenerator") as model:
                with self.assertRaisesRegex(ValueError, "Native arms require workers=1"):
                    experiment.run_arm(self.output, arm, "unused", execute=True, workers=2)
                model.assert_not_called()

    def test_all_existing_requests_preflight_before_parallel_capture(self):
        self.seal()
        self.run_gpt("gpt_propositions")
        items = experiment.items_for(self.output, "gpt_propositions")
        # Leave the final item as an existing incompatible attempt, with earlier
        # items pending again: none may start until the final mismatch is found.
        for item in items[:-1]:
            shutil.rmtree(self.output / "captures" / "gpt_propositions" / item["id"])
        path = self.output / "captures" / "gpt_propositions" / items[-1]["id"] / "request.json"
        request = experiment.read(path)
        request["prompt"] = "incompatible request"
        path.write_bytes(experiment.encoded(request))
        with patch.object(experiment, "capture_codex") as capture:
            with self.assertRaisesRegex(ValueError, "request identity mismatch"):
                experiment.run_arm(self.output, "gpt_propositions", "unused", execute=True, workers=2)
            capture.assert_not_called()

    def test_cli_workers_dispatch_is_operator_control(self):
        result = self.call_cli("run", "--output", self.output, "--arm", "gpt_direct", "--workers", 4)
        self.assertEqual(result["workers"], 4)
        self.assertFalse(result["execute"])

    def test_bootstrap_keeps_source_components_together(self):
        self.assertEqual(experiment.paired_interval({"one": [1, -1]}, 3), None)
        self.assertEqual(experiment.paired_interval({"one": [1], "two": [1, 1]}, 3, 100),
                         [1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
