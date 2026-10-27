"""Observe delegated status and preserve the native acknowledgment and recorded scores."""

import json
import tempfile
import unittest
from pathlib import Path

from csts_pilot.colab_training_status import decorate, markdown


class ColabStatusTests(unittest.TestCase):
    def test_full_bank_report_uses_current_concurrent_hardware(self):
        """The full-bank experiment supersedes the older migration's hardware description."""
        report = decorate(
            {
                "training_policy": {"proposition_until_patience": True},
                "stages": {
                    "evidence_pretrain": {"status": "pending", "trace_available": True}
                },
            },
            Path("/absent/migration.json"),
        )
        self.assertEqual(report["stages"]["evidence_pretrain"]["status"], "running")
        displayed = markdown("## Writing\n", report)
        self.assertIn("80 GB A100", displayed)
        self.assertNotIn("Asian L4", displayed)

    def test_delegated_training_changes_presentation_without_mutating_native_ack(self):
        """A live A100 trace fixes pending presentation while preserving the original object."""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "migration.json"
            path.write_text(
                json.dumps(
                    {"hardware": "A100", "batch_size": 32, "microbatch_size": 32}
                )
            )
            native = {
                "stages": {
                    "evidence_ratings": {
                        "status": "pending",
                        "trace_status": "running",
                        "trace_available": True,
                        "epochs": [{"validation_spearman": 0.85}],
                    }
                }
            }
            report = decorate(native, path)
            self.assertEqual(native["stages"]["evidence_ratings"]["status"], "pending")
            self.assertEqual(report["stages"]["evidence_ratings"]["status"], "running")
            self.assertEqual(
                report["stages"]["evidence_ratings"]["epochs"],
                native["stages"]["evidence_ratings"]["epochs"],
            )
            body = "## Proposition model: ratings on the full training set\n\nStatus: **pending**.\n| 1 | 0.850000 |\n"
            displayed = markdown(body, report)
            self.assertIn("Status: **running**.", displayed)
            self.assertIn("| 1 | 0.850000 |", displayed)
            self.assertIn("microbatch: **32**", displayed)

    def test_session_receipt_alone_does_not_claim_training_progress(self):
        """An allocated session cannot turn a missing trace into a running training stage."""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "migration.json"
            path.write_text(json.dumps({"hardware": "A100"}))
            report = decorate(
                {
                    "stages": {
                        "evidence_ratings": {
                            "status": "pending",
                            "trace_available": False,
                        }
                    }
                },
                path,
            )
            self.assertEqual(report["stages"]["evidence_ratings"]["status"], "pending")
            self.assertEqual(markdown("unchanged", report), "unchanged")


if __name__ == "__main__":
    unittest.main()
