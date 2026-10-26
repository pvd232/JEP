"""Check schema boundaries and stable evidence serialization."""

import copy
import json
import unittest

from csts_pilot.structured_evidence import canonical_text, validate_record


PASSAGE = "A boy in red stands beside a girl in blue."
CONDITION = "color of clothing"


def record():
    return {
        "condition": CONDITION,
        "status": "answered",
        "reason": "",
        "entities": [
            {"id": "boy", "type": "person", "source_quote": "A boy"},
            {"id": "girl", "type": "person", "source_quote": "a girl"},
        ],
        "facts": [
            {"entity_id": "boy", "predicate": "clothing_color", "value": "red", "source_quote": "A boy in red", "support_status": "explicit", "reason": ""},
            {"entity_id": "girl", "predicate": "clothing_color", "value": "blue", "source_quote": "a girl in blue", "support_status": "explicit", "reason": ""},
        ],
    }


class StructuredEvidenceTests(unittest.TestCase):
    def test_preserves_entities_and_canonical_meaning(self):
        result = json.loads(canonical_text(record(), PASSAGE, CONDITION))
        self.assertEqual([f["value"] for f in result["facts"]], ["red", "blue"])
        self.assertEqual([e["id"] for e in result["entities"]], ["e1", "e2"])
        self.assertNotIn("source_quote", result["facts"][0])

    def test_permutation_and_local_ids_preserve_serialization(self):
        changed = record()
        changed["entities"].reverse()
        changed["facts"].reverse()
        for entity in changed["entities"]:
            entity["id"] += "_renamed"
        for fact in changed["facts"]:
            fact["entity_id"] += "_renamed"
        self.assertEqual(canonical_text(record(), PASSAGE, CONDITION), canonical_text(changed, PASSAGE, CONDITION))

    def test_unknown_is_explicit_and_empty(self):
        unknown = {"condition": CONDITION, "status": "unknown", "reason": "Clothing color unavailable.", "entities": [], "facts": []}
        self.assertEqual(validate_record(unknown, PASSAGE, CONDITION), unknown)
        unknown["facts"] = record()["facts"]
        with self.assertRaises(ValueError):
            validate_record(unknown, PASSAGE, CONDITION)

    def test_rejects_structural_and_support_failures(self):
        mutations = [
            lambda r: r.update(extra=True),
            lambda r: r.update(condition="other"),
            lambda r: r.update(status="invalid"),
            lambda r: r.update(facts=[]),
            lambda r: r["entities"].append(copy.deepcopy(r["entities"][0])),
            lambda r: r["entities"][0].update(source_quote="a man"),
            lambda r: r["facts"][0].update(entity_id="missing"),
            lambda r: r["facts"][0].update(source_quote="purple"),
            lambda r: r["facts"][0].update(value=""),
            lambda r: r["facts"][0].update(support_status="inferred", reason=""),
            lambda r: r["facts"][0].update(support_status="unknown"),
        ]
        for change in mutations:
            with self.subTest(change=change):
                changed = record()
                change(changed)
                with self.assertRaises(ValueError):
                    validate_record(changed, PASSAGE, CONDITION)

    def test_inference_and_ambiguity_require_reasons(self):
        inferred = record()
        inferred["facts"][0].update(support_status="inferred", reason="The described red item is the boy's clothing.")
        validate_record(inferred, PASSAGE, CONDITION)
        inferred.update(status="ambiguous", reason="")
        with self.assertRaises(ValueError):
            validate_record(inferred, PASSAGE, CONDITION)
        inferred["reason"] = "The question could refer to either person."
        validate_record(inferred, PASSAGE, CONDITION)

    def test_returns_an_independent_record(self):
        source = record()
        checked = validate_record(source, PASSAGE, CONDITION)
        checked["facts"][0]["value"] = "changed"
        self.assertEqual(source["facts"][0]["value"], "red")


if __name__ == "__main__":
    unittest.main()
