"""Check the updated-data stopping policy and validation-only generation trigger."""

import copy
import json
import unittest
from pathlib import Path

from csts_pilot.proposition_evidence_run import validate_settings
from scripts.supervise_proposition_pilot import decision


class PilotTests(unittest.TestCase):
    """Keep checkpoint selection and the generation decision independent of test scores."""

    def setUp(self):
        self.summary = {
            "status": "complete",
            "source_commit": "candidate",
            "settings": {"training": {"seed": 7}, "dataset_revision": "jep-csts-v1"},
            "live_scores": {
                "ratings": {"spearman": 0.9},
                "evidence": {"spearman": 0.2},
            },
        }
        self.selection = {
            "status": "checkpoints_frozen",
            "test_scores_used_for_selection": False,
            "candidates": {
                "ratings": {"epoch": 2, "validation": {"spearman": 0.81}},
                "evidence": {"epoch": 3, "validation": {"spearman": 0.82}},
            },
        }

    def test_generation_uses_selected_validation_scores(self):
        """A positive validation result triggers generation even with lower test scores."""
        result = decision(self.summary, self.selection)
        self.assertTrue(result["positive"])
        self.assertAlmostEqual(result["validation_difference"], 0.01)
        altered = copy.deepcopy(self.summary)
        altered["live_scores"]["evidence"]["spearman"] = 0.99
        self.assertEqual(
            decision(altered, self.selection)["positive"], result["positive"]
        )

    def test_tie_or_loss_keeps_generation_unqueued(self):
        """The trigger requires the declared strict validation improvement."""
        for score in (0.8, 0.81):
            self.selection["candidates"]["evidence"]["validation"]["spearman"] = score
            self.assertFalse(decision(self.summary, self.selection)["positive"])

    def test_incomplete_or_test_selected_comparison_cannot_trigger(self):
        """Only a completed comparison with frozen validation selections qualifies."""
        self.summary["status"] = "running"
        with self.assertRaises(ValueError):
            decision(self.summary, self.selection)
        self.summary["status"] = "complete"
        self.selection["test_scores_used_for_selection"] = True
        with self.assertRaises(ValueError):
            decision(self.summary, self.selection)

    def test_updated_settings_accept_patience_two(self):
        """Validate the actual published-data settings and reject an undeclared policy."""
        path = (
            Path(__file__).resolve().parents[1]
            / "configs/csts-qwen-jep-v1-proposition-evidence.json"
        )
        settings = json.loads(path.read_text())
        self.assertEqual(settings["training"]["patience"], 2)
        self.assertEqual(settings["splits"]["training"]["rows"], 6051)
        self.assertEqual(settings["splits"]["test"]["rows"], 2430)
        validate_settings(settings)
        settings["training"]["patience"] = 3
        with self.assertRaisesRegex(ValueError, "patience"):
            validate_settings(settings)


if __name__ == "__main__":
    unittest.main()
