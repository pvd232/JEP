"""Exercise partial target coverage, held-out separation and frozen-byte bindings."""

import copy
import hashlib
import json
import unittest

from csts_pilot.proposition_pretraining import (
    _answer_id,
    _inventory,
    prepare_frozen_proposition_pretraining,
    prepare_proposition_pretraining,
)


def encoded(value):
    return (
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode()


def row(index):
    return {
        "row_id": f"row-{index}",
        "pair_id": f"pair-{index}",
        "group_id": f"group-{index}",
        "sentence1": f"A red car {index}.",
        "sentence2": f"A blue car {index}.",
        "condition": "color of car",
        "rating": 1.0,
        "target": 0.0,
    }


def fixture():
    training, validation = [row(index) for index in range(3)], [row(3)]
    records = []
    statuses = ["answered", "answered", "answered", "not_specified", "ambiguous"]
    inventory, _, _, _ = _inventory(training)
    for item, status in zip(inventory.values(), statuses):
        color = "red" if "red" in item["passage"] else "blue"
        records.append(
            {
                "id": item["id"],
                "status": status,
                "target": "car",
                "attribute": "color",
                "answer": f"The object's hue is {color}."
                if status == "answered"
                else "",
                "evidence": [color] if status == "answered" else [],
            }
        )
    provenance = {
        "items": len(records),
        "source_training_sha256": hashlib.sha256(encoded(training)).hexdigest(),
        "records_sha256": hashlib.sha256(encoded(records)).hexdigest(),
        "capture_source_sha256": "a" * 64,
        "capture_source_commit": "b" * 40,
        "generation_template_sha256": "c" * 64,
        "schema_sha256": "d" * 64,
        "audit_gate_sha256": "e" * 64,
        "model_alias": "gpt-6.1-sol",
        "reasoning_effort": "high",
        "operational_subset_only": True,
        "completed_batches": [
            {
                "batch": "batch_0000",
                "receipt_sha256": "f" * 64,
                "records_sha256": "a" * 64,
            }
        ],
    }
    return {
        "training": training,
        "validation": validation,
        "records": records,
        "provenance": provenance,
    }


def freeze(values):
    values = copy.deepcopy(values)
    values["provenance"]["items"] = len(values["records"])
    values["provenance"]["records_sha256"] = hashlib.sha256(
        encoded(values["records"])
    ).hexdigest()
    values["provenance"]["source_training_sha256"] = hashlib.sha256(
        encoded(values["training"])
    ).hexdigest()
    inputs = {name: encoded(value) for name, value in values.items()}
    return inputs, {
        name: hashlib.sha256(value).hexdigest() for name, value in inputs.items()
    }


class PropositionPretrainingTests(unittest.TestCase):
    def test_partial_bank_accepts_paraphrases_and_preserves_both_arm_rows(self):
        values = fixture()
        prepared = prepare_frozen_proposition_pretraining(*freeze(values))
        self.assertEqual(prepared["training"], values["training"][:2])
        self.assertEqual(len(prepared["aligned"]), 3)
        self.assertEqual(
            prepared["audit"]["comparison_answer_coverage"],
            {"neither": 1, "one": 1, "both": 1},
        )
        self.assertEqual(prepared["audit"]["stage_b_comparisons"], 3)
        self.assertEqual(prepared["audit"]["uncaptured_training_inputs"], 1)
        self.assertTrue(prepared["audit"]["partial_capture"])
        self.assertFalse(prepared["audit"]["validation_evidence_used_for_training"])
        self.assertFalse(prepared["audit"]["raw_receipts_replayed_by_this_helper"])
        prepared["training"][0]["rating"] = 5
        self.assertEqual(values["training"][0]["rating"], 1.0)

    def test_changed_frozen_bytes_fail_before_preparation(self):
        inputs, hashes = freeze(fixture())
        inputs["records"] += b" "
        with self.assertRaisesRegex(ValueError, "Changed frozen preparation bytes"):
            prepare_frozen_proposition_pretraining(inputs, hashes)

    def test_validation_group_and_caption_leaks_are_rejected(self):
        for change in ("group", "caption", "row_id"):
            with self.subTest(change=change):
                values = fixture()
                target = values["validation"][0]
                if change == "group":
                    target["group_id"] = values["training"][0]["group_id"]
                elif change == "caption":
                    target["sentence1"] = "Ａ RED CAR 0."
                    target["condition"] = "number of cars"
                else:
                    target["row_id"] = values["training"][0]["row_id"]
                with self.assertRaisesRegex(ValueError, "must be disjoint"):
                    prepare_frozen_proposition_pretraining(*freeze(values))

    def test_foreign_duplicate_and_validation_targets_are_rejected(self):
        for change in ("foreign", "duplicate", "validation"):
            with self.subTest(change=change):
                values = fixture()
                if change == "foreign":
                    values["records"][0]["id"] = "0" * 64
                elif change == "duplicate":
                    values["records"].append(copy.deepcopy(values["records"][0]))
                else:
                    item = values["validation"][0]
                    values["records"][0]["id"] = _answer_id(
                        item["sentence1"], item["condition"]
                    )
                with self.assertRaises(ValueError):
                    prepare_frozen_proposition_pretraining(*freeze(values))

    def test_bad_quotation_and_nonempty_abstention_are_rejected(self):
        for change in ("quotation", "abstention"):
            with self.subTest(change=change):
                values = fixture()
                if change == "quotation":
                    values["records"][0]["evidence"] = ["yellow"]
                else:
                    values["records"][-1]["answer"] = "Unknown"
                with self.assertRaises(ValueError):
                    prepare_frozen_proposition_pretraining(*freeze(values))

    def test_manifest_cannot_rebind_the_frozen_training_or_records(self):
        for field in ("source_training_sha256", "records_sha256"):
            with self.subTest(field=field):
                inputs, hashes = freeze(fixture())
                manifest = json.loads(inputs["provenance"])
                manifest[field] = "0" * 64
                inputs["provenance"] = encoded(manifest)
                hashes["provenance"] = hashlib.sha256(inputs["provenance"]).hexdigest()
                with self.assertRaisesRegex(ValueError, "provenance changed"):
                    prepare_frozen_proposition_pretraining(inputs, hashes)

    def test_empty_answered_training_support_is_rejected(self):
        values = fixture()
        for record in values["records"]:
            record.update(status="not_specified", answer="", evidence=[])
        with self.assertRaisesRegex(ValueError, "No accepted generated training"):
            prepare_frozen_proposition_pretraining(*freeze(values))

    def test_literal_quotes_are_checked_against_actual_raw_source_alias(self):
        values = fixture()
        alias = dict(values["training"][0], row_id="alias-0", sentence1="A RED car 0.")
        values["training"].append(alias)
        values["records"][0]["evidence"] = ["RED"]
        inputs, hashes = freeze(values)
        values["provenance"] = json.loads(inputs["provenance"])
        sources = list(_inventory(values["training"])[0].values())
        sources[0] = {
            "id": sources[0]["id"],
            "passage": alias["sentence1"],
            "condition": alias["condition"],
        }
        prepared = prepare_proposition_pretraining(
            values["training"],
            values["validation"],
            values["records"],
            sources,
            values["provenance"],
            input_sha256=hashes,
        )
        self.assertEqual(len(prepared["aligned"]), 3)
        sources[0]["passage"] = "A rEd car 0."
        with self.assertRaisesRegex(ValueError, "differs from its original training"):
            prepare_proposition_pretraining(
                values["training"],
                values["validation"],
                values["records"],
                sources,
                values["provenance"],
                input_sha256=hashes,
            )


if __name__ == "__main__":
    unittest.main()
