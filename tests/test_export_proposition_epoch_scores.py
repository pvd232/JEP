"""Fixtures matching native phase-A and phase-B progress snapshots."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_proposition_epoch_scores import collect, markdown


class EpochPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.name = "propositions_v41_full_after_indicative"
        self.directory = self.root / "qwen_evidence_results" / self.name
        self.directory.mkdir(parents=True)
        self.experiment = (
            "csts_qwen_proposition_evidence_a6daf0ee_d73dcec7_ratings_pretrain"
        )
        self.trace = (
            self.root
            / "experiments"
            / self.experiment
            / "runs/ratings_pretrain/01M5XG0J4ZFFRGER9NVS4NFWZ3/artifacts/train/trace/trace.json"
        )
        self.summary = {
            "source_commit": "a6daf0eeea544716d7340f0f24de687e4ba93490",
            "attempt": "d73dcec7",
            "status": "running",
            "current_stage": "ratings_pretrain",
            "in_flight": {"name": "ratings_pretrain", "experiment_id": self.experiment},
            "runs": [],
            "settings": {
                "splits": {
                    "training": {"sha256": "train"},
                    "validation": {"sha256": "validation", "rows": 1572, "groups": 678},
                }
            },
            "live_scores": {"do_not_publish_test_scores": 0.9},
        }
        self.write(self.directory / "summary.json", self.summary)
        self.epoch = {
            "epoch": 1,
            "step": 72,
            "training_objective": 0.07945909878777564,
            "validation": {
                "spearman": 0.767296901710081,
                "mse_1_5": 1.1149826139470598,
                "n": 1572,
            },
            "elapsed_seconds": 699.2299,
        }

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def phase_a(self):
        self.write(
            self.trace,
            {
                "status": "running",
                "arm": "ratings",
                "phase": "pretrain",
                "current_epoch": 2,
                "updates": 75,
                "completed_epoch": 1,
                "epochs": [self.epoch],
            },
        )

    def test_actual_in_flight_structure_and_markdown(self):
        self.phase_a()
        report = collect(self.root, self.name)
        phase = report["stages"]["ratings_pretrain"]
        self.assertEqual(phase["optimizer_updates"], 75)
        self.assertEqual(phase["completed_epoch"], 1)
        self.assertEqual(phase["current_epoch"], 2)
        self.assertEqual(phase["epochs"][0]["optimizer_updates"], 72)
        self.assertEqual(phase["epochs"][0]["validation_spearman"], 0.767296901710081)
        self.assertIn("0.767297", markdown(report))
        self.assertNotIn("do_not_publish_test_scores", json.dumps(report))
        self.assertEqual(report["stages"]["evidence_pretrain"]["completed_epoch"], 0)

    def test_updated_stopping_policy_is_published(self):
        """Readers see the configured patience and wall budget for the current run."""
        self.summary["settings"]["training"] = {"patience": 2}
        self.summary["settings"]["phases"] = {
            "ratings": {"max_epochs": 24, "max_seconds": 8100}
        }
        self.write(self.directory / "summary.json", self.summary)
        report = collect(self.root, self.name)
        self.assertEqual(report["training_policy"]["ratings_max_seconds"], 8100)
        self.assertIn("patience 2", markdown(report))

    def test_completion_policy_reports_disabled_ceilings_and_live_trace(self):
        """A live continuation takes precedence over its copied parent trace."""
        self.phase_a()
        self.summary["settings"]["training"] = {
            "patience": 2,
            "train_until_patience": True,
        }
        self.write(self.directory / "summary.json", self.summary)
        self.write(
            self.directory / "ratings_pretrain_trace.json",
            {"status": "complete", "epochs": []},
        )
        report = collect(self.root, self.name)
        self.assertEqual(report["stages"]["ratings_pretrain"]["completed_epoch"], 1)
        self.assertIn("time and epoch limits disabled", markdown(report))

    def test_phase_b_copied_trace_structure(self):
        epoch = {
            "epoch": 1,
            "step": 219,
            "training_mse_0_1": 0.03,
            "validation": {"spearman": 0.8, "mse_1_5": 0.7, "n": 1572},
            "fit_seconds": 1800,
            "validation_seconds": 60,
            "observed_epoch_seconds": 1900,
            "epochs_without_improvement": 0,
        }
        self.write(
            self.directory / "ratings_ratings_trace.json",
            {
                "status": "complete",
                "epochs": [epoch],
                "actual_updates": 219,
                "stop_reason": "validation_patience",
            },
        )
        report = collect(self.root, self.name)
        phase = report["stages"]["ratings_ratings"]
        self.assertEqual(phase["epochs"][0]["training_loss"], 0.03)
        self.assertEqual(phase["epochs"][0]["epochs_without_improvement"], 0)
        self.assertEqual(phase["stop_reason"], "validation_patience")

    def test_completed_native_resolved_yaml_reference(self):
        self.phase_a()
        self.summary["runs"] = [
            {
                "name": "ratings_pretrain",
                "status": "succeeded",
                "path": str(self.trace.parents[3] / "resolved.yaml"),
            }
        ]
        self.summary["in_flight"] = None
        self.summary["current_stage"] = "evidence_pretrain"
        self.write(self.directory / "summary.json", self.summary)
        report = collect(self.root, self.name)
        self.assertEqual(report["stages"]["ratings_pretrain"]["completed_epoch"], 1)

    def test_missing_and_partial_trace_preserve_matched_history(self):
        self.phase_a()
        previous = collect(self.root, self.name)
        self.trace.write_text('{"epochs": [')
        partial = collect(self.root, self.name, previous)
        phase = partial["stages"]["ratings_pretrain"]
        self.assertEqual(len(phase["epochs"]), 1)
        self.assertEqual(phase["optimizer_updates"], 75)
        self.assertFalse(phase["trace_available"])
        self.assertTrue(phase["notes"])
        self.trace.unlink()
        missing = collect(self.root, self.name, partial)
        self.assertEqual(len(missing["stages"]["ratings_pretrain"]["epochs"]), 1)
        self.summary["attempt"] = "new_attempt"
        self.write(self.directory / "summary.json", self.summary)
        changed = collect(self.root, self.name, previous)
        self.assertEqual(changed["stages"]["ratings_pretrain"]["epochs"], [])

    def test_conflicting_replay_preserves_original_observation(self):
        self.phase_a()
        previous = collect(self.root, self.name)
        self.epoch["validation"]["spearman"] = 0.9
        self.phase_a()
        report = collect(self.root, self.name, previous)
        phase = report["stages"]["ratings_pretrain"]
        self.assertEqual(phase["epochs"][0]["validation_spearman"], 0.767296901710081)
        self.assertIn("Conflicting observation", phase["notes"][0])


if __name__ == "__main__":
    unittest.main()
