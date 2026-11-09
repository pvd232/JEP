"""Counterexamples for extraction format contracts and safe Python decoding."""

import copy
import json
import unittest

from csts_pilot.extraction_formats import (
    FORMATS, POLICY, build_prompt, canonical_text, parse_payload,
)

PASSAGE = "A black and white dog is playing with a tan dog."


def evidence():
    """Return two distinct dogs, including two attributes on the first dog."""
    return {
        "status": "answered", "reason": "",
        "entities": [
            {"id": "dog1", "type": "dog", "source_quote": "A black and white dog", "count": 1},
            {"id": "dog2", "type": "dog", "source_quote": "a tan dog", "count": 1},
        ],
        "facts": [
            {"entity_id": "dog1", "predicate": "color", "value": "black",
             "source_quote": "A black and white dog", "support_status": "explicit", "reason": ""},
            {"entity_id": "dog1", "predicate": "color", "value": "white",
             "source_quote": "A black and white dog", "support_status": "explicit", "reason": ""},
            {"entity_id": "dog2", "predicate": "color", "value": "tan",
             "source_quote": "a tan dog", "support_status": "explicit", "reason": ""},
        ],
    }


def python_payload(record):
    """Serialize fixtures using the exact allowlisted constructor grammar."""
    def call(name, item):
        return name + "(" + ", ".join(f"{key}={value!r}" for key, value in item.items()) + ")"
    return (
        f"Evidence(status={record['status']!r}, reason={record['reason']!r}, "
        + "entities=[" + ", ".join(call("Entity", e) for e in record["entities"]) + "], "
        + "facts=[" + ", ".join(call("Fact", f) for f in record["facts"]) + "])"
    )


class ExtractionFormatsTest(unittest.TestCase):
    def test_json_python_agree_on_identity_binding(self):
        record = evidence()
        for format, payload in (("json", json.dumps(record)), ("python", python_payload(record))):
            with self.subTest(format=format):
                self.assertEqual(parse_payload(payload, format, PASSAGE), record)

    def test_same_color_different_entities_survive(self):
        record = evidence()
        record["facts"][2]["value"] = "black"
        parsed = parse_payload(json.dumps(record), "json", PASSAGE)
        text = canonical_text(parsed)
        self.assertIn("Entity 1", text)
        self.assertIn("Entity 2", text)
        self.assertEqual(text.count("color is black"), 2)

    def test_count_is_preserved(self):
        record = evidence()
        record["entities"][0]["count"] = 2
        parsed = parse_payload(python_payload(record), "python", PASSAGE)
        self.assertIn("(2 dog)", canonical_text(parsed))

    def test_unspecified_plural_count_stays_unknown(self):
        record = evidence()
        record["entities"][0]["count"] = None
        for format, payload in (("json", json.dumps(record)), ("python", python_payload(record))):
            parsed = parse_payload(payload, format, PASSAGE)
            self.assertIsNone(parsed["entities"][0]["count"])
            self.assertIn("unspecified number of dog", canonical_text(parsed))
        self.assertIn("count=null/None", build_prompt(PASSAGE, "color", "json"))

    def test_counts_reject_boolean_zero_float(self):
        for count in (True, 0, -1, 1.0, "2"):
            record = evidence()
            record["entities"][0]["count"] = count
            with self.subTest(count=count), self.assertRaises(ValueError):
                parse_payload(json.dumps(record), "json", PASSAGE)

    def test_quote_must_be_exact(self):
        record = evidence()
        record["facts"][0]["source_quote"] = "a black dog"
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "json", PASSAGE)

    def test_inferred_support_requires_reason(self):
        record = evidence()
        record["facts"][0]["support_status"] = "inferred"
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "json", PASSAGE)
        record["facts"][0]["reason"] = "Unambiguous pronoun resolution."
        self.assertEqual(parse_payload(json.dumps(record), "json", PASSAGE), record)

    def test_duplicate_ids_and_missing_references_fail(self):
        for mutate in (
            lambda r: r["entities"][1].update(id="dog1"),
            lambda r: r["facts"][0].update(entity_id="missing"),
            lambda r: r["facts"].append(copy.deepcopy(r["facts"][0])),
            lambda r: r["entities"].append(
                {"id": "unused", "type": "dog", "source_quote": "dog", "count": 1}),
        ):
            record = evidence()
            mutate(record)
            with self.assertRaises(ValueError):
                parse_payload(json.dumps(record), "json", PASSAGE)

    def test_json_duplicate_keys_and_extra_fields_fail(self):
        with self.assertRaises(ValueError):
            parse_payload('{"status":"answered","status":"not_specified"}', "json", PASSAGE)
        record = evidence()
        record["rating"] = 5
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "json", PASSAGE)

    def test_python_rejects_execution_and_expansion(self):
        valid = python_payload(evidence())
        for payload in (
            "__import__('os').system('touch /tmp/never-executed')",
            valid.replace("count=1", "count=1+1", 1),
            valid.replace("count=1", "count=True", 1),
            valid.replace("entities=[", "entities=list([", 1),
            "result = " + valid,
            valid.replace("reason=''", "reason=f'{1}'", 1),
            valid.replace("reason=''", "**{'reason': ''}", 1),
            valid.replace("reason=''", "reason='', reason=''", 1),
            valid.replace("entities=[", "entities=(", 1),
        ):
            with self.subTest(payload=payload[:80]), self.assertRaises(ValueError):
                parse_payload(payload, "python", PASSAGE)

    def test_nonanswer_requires_empty_claims_and_reason(self):
        for format in FORMATS:
            record = {"status": "not_specified", "reason": "No color is stated."}
            record.update({"propositions": []} if format == "propositions" else
                          {"entities": [], "facts": []})
            payload = python_payload(record) if format == "python" else json.dumps(record)
            self.assertEqual(parse_payload(payload, format, PASSAGE), record)
            self.assertEqual(canonical_text(record), "")
        record = evidence()
        record["status"] = "not_specified"
        record["reason"] = "No information."
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "json", PASSAGE)

    def test_ambiguous_requires_reason(self):
        record = evidence()
        record["status"] = "ambiguous"
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "json", PASSAGE)

    def test_propositions_preserve_natural_claim(self):
        record = {"status": "answered", "reason": "", "propositions": [
            {"text": "One dog is black and white; the other is tan.",
             "source_quote": PASSAGE, "support_status": "explicit", "reason": ""},
        ]}
        parsed = parse_payload(json.dumps(record), "propositions", PASSAGE)
        self.assertEqual(canonical_text(parsed), record["propositions"][0]["text"])
        record["propositions"].append(copy.deepcopy(record["propositions"][0]))
        with self.assertRaises(ValueError):
            parse_payload(json.dumps(record), "propositions", PASSAGE)

    def test_canonical_ids_ignore_model_local_naming(self):
        first = evidence()
        second = copy.deepcopy(first)
        second["entities"].reverse()
        for entity in second["entities"]:
            entity["id"] = "renamed-" + entity["id"]
        for fact in second["facts"]:
            fact["entity_id"] = "renamed-" + fact["entity_id"]
        second["facts"].reverse()
        self.assertEqual(canonical_text(first), canonical_text(second))
        self.assertNotIn("source_quote", canonical_text(first))
        self.assertNotIn("renamed", canonical_text(second))

    def test_prompts_share_policy_and_only_expose_supplied_inputs(self):
        for format in FORMATS:
            prompt = build_prompt("The runner wears red.", "color of clothes", format)
            self.assertTrue(prompt.startswith(POLICY))
            inputs = json.loads(prompt.split("INPUT:\n")[1])
            self.assertEqual(set(inputs), {"passage", "condition"})
            self.assertNotIn("target", inputs)
            self.assertNotIn("rating", inputs)

    def test_malformed_and_oversized_payload_fail(self):
        for payload in ("", "[]", "{", "x" * 100_001):
            with self.subTest(payload=payload[:10]), self.assertRaises(ValueError):
                parse_payload(payload, "json", PASSAGE)


if __name__ == "__main__":
    unittest.main()
