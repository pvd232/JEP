"""Check held-out separation, source-only requests, factual joins and score-table preservation."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from csts_pilot.proposition_monitoring import (
    heldout,
    insert,
    inventory,
    read_status,
    review_metrics,
)
from scripts import capture_proposition_inputs as capture
from scripts import proposition_validation_suite as suite


class MonitoringTests(unittest.TestCase):
    """Reject label leakage and unmeasured claims in proposition monitoring."""

    def test_heldout_sample_is_group_disjoint_and_label_independent(self):
        """Changing rating labels leaves the same source-only validation sample."""
        train = [
            {
                "group_id": "train",
                "condition": "color",
                "sentence1": "Red car",
                "sentence2": "Blue car",
                "rating": 1,
            }
        ]
        valid = [
            {
                "group_id": "v" + str(i),
                "condition": "color",
                "sentence1": f"Green ball {i}",
                "sentence2": f"Orange ball {i}",
                "rating": i,
            }
            for i in range(4)
        ]
        items, groups = heldout(train, valid, 3)
        self.assertEqual(len(set(groups.values())), 3)
        capture.validate_inputs(items)
        for row in valid:
            row["rating"] = -999
        self.assertEqual(heldout(train, valid, 3), (items, groups))
        valid[0]["sentence1"] = train[0]["sentence1"]
        with self.assertRaises(ValueError):
            heldout(train, valid, 3)

    def test_source_quotes_cannot_be_fabricated(self):
        """A generated answer with a nonexistent evidence quotation fails structural validation."""
        items, _ = inventory(
            [
                {
                    "group_id": "g",
                    "condition": "color",
                    "sentence1": "Red car",
                    "sentence2": "Blue car",
                }
            ]
        )
        records = [
            {
                "id": r["id"],
                "status": "answered",
                "target": "car",
                "attribute": "color",
                "answer": "red",
                "evidence": ["Red car"],
            }
            for r in items
        ]
        with self.assertRaises(ValueError):
            capture.checked_records(items, {"records": records})

    def test_independent_reviews_keep_omissions_and_unsupported_facts_separate(self):
        """Factual support alone cannot count an incomplete answer as fully correct."""
        candidates = [{"id": "a"}, {"id": "b"}]
        first = [
            {
                "id": "a",
                "supported": True,
                "complete": True,
                "unsupported_assertion": False,
                "notes": "",
            },
            {
                "id": "b",
                "supported": True,
                "complete": False,
                "unsupported_assertion": False,
                "notes": "omits second object",
            },
        ]
        second = [dict(row) for row in first]
        second[1].update(supported=False, unsupported_assertion=True)
        result = review_metrics(candidates, [first, second])
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["unsupported_assertion_count"], 1)
        self.assertEqual(result["review_agreement"], 0.5)
        with self.assertRaises(ValueError):
            review_metrics(candidates, [first, second[:1]])

    def test_pending_metrics_and_native_scores_remain_distinct(self):
        """Repeated monitor inserts preserve native epoch rows and never invent a loss."""
        original = "# Epoch scores\n\n| 4 | 0.875915 |\n"
        body = insert(original, {"status": "running"})
        self.assertTrue(body.startswith(original))
        self.assertIn("Pending", body)
        self.assertEqual(insert(body, {"status": "running"}), body)
        measured = insert(
            body,
            {
                "evaluations": [
                    {
                        "epoch": 2,
                        "mean_answer_cross_entropy": 1.25,
                        "factual_review": {"accuracy": 0.75, "n": 64},
                    }
                ]
            },
        )
        self.assertIn("1.250000 | 75.0% | 64", measured)
        self.assertIn("| 4 | 0.875915 |", measured)

    def test_gpu_job_filters_bad_references_and_waits_on_the_training_lease(self):
        """Evaluation uploads reviewed references and queues behind training without stopping it."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            suite.save(
                root / "validation_capture/records.json",
                [
                    {"id": "a", "status": "answered", "answer": "red"},
                    {"id": "b", "status": "answered", "answer": "blue"},
                ],
            )
            suite.save(
                root / "validation_inputs.json",
                [
                    {"id": key, "passage": "Red car", "condition": "color"}
                    for key in ("a", "b")
                ],
            )
            for reviewer in (1, 2):
                directory = (
                    root
                    / "validation_reference_review"
                    / f"reviewer_{reviewer}_batch_0"
                )
                attempt = directory / "attempt_1"
                suite.save(
                    attempt / "response.json",
                    {
                        "reviews": [
                            {
                                "id": key,
                                "supported": key == "a",
                                "complete": True,
                                "unsupported_assertion": key == "b",
                            }
                            for key in ("a", "b")
                        ]
                    },
                )
                suite.save(directory / "receipt.json", {"attempt": str(attempt)})
            with (
                patch.object(suite, "review"),
                patch.object(suite, "remote", return_value=b"123\n") as remote,
            ):
                suite.gpu_job(root)
                self.assertEqual(
                    [r["id"] for r in suite.read(root / "validated_references.json")],
                    ["a"],
                )
                command = remote.call_args.args[1].decode()
                self.assertIn("flock " + suite.LOCK, command)
                self.assertNotIn("kill", command)
                count = remote.call_count
                suite.gpu_job(root)
                self.assertEqual(remote.call_count, count)

    def test_saved_losses_publish_before_review_and_survive_monitor_restart(self):
        """Retain measured loss while factual review is pending, preserving finished reviews."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            measured = {"epoch": 2, "mean_answer_cross_entropy": 0.451316}
            suite.save(root / "epoch_2_result.json", measured)
            suite.save(root / "status.json", {"status": "running", "evaluations": []})
            state = read_status(root)
            self.assertEqual(state["evaluations"], [measured])
            self.assertIn("0.451316 | Pending", insert("# Epoch scores", state))
            reviewed = {**measured, "factual_review": {"accuracy": 0.75, "n": 64}}
            suite.save(root / "status.json", {"evaluations": [reviewed]})
            self.assertEqual(read_status(root)["evaluations"], [reviewed])


if __name__ == "__main__":
    unittest.main()
