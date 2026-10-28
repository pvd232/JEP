"""Input-contract checks for inference through the trained proposition scorer."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from csts_pilot.format_similarity import (
    ARMS, CHECKPOINT_SHA256, MODEL_ID, PROMPT, REVISION,
    effective_inputs, evaluate_formats, inference_rows, validate_inputs, write_json,
)


def fixture():
    def source(identity, passage, evidence):
        return {"id": identity, "passage": passage, "condition": "number of animals",
                "arms": {arm: {"status": "answered", "text": evidence, "failure": None} for arm in ARMS[1:]}}
    return {"protocol": {"checkpoint_sha256": CHECKPOINT_SHA256, "model_id": MODEL_ID,
                          "revision": REVISION, "prompt": PROMPT, "max_length": 160},
            "sources": [source("a", "Two dogs.", "There are two dogs."), source("b", "Three dogs.", "There are three dogs.")],
            "pairs": [{"id": "p1", "source_a": "a", "source_b": "b", "group_id": "g1"}]}


class Tokenizer:
    def __init__(self):
        self.calls = []

    def get_vocab(self):
        return {"<|endoftext|>": 99}

    def __call__(self, texts, **kwargs):
        self.calls.append(kwargs)
        return {"input_ids": [[1] * (160 if "OVERFLOW" in text else 8) for text in texts]}


class FormatSimilarityTests(unittest.TestCase):
    def test_evaluation_known_correlations_scale_and_paired_group_contrasts(self):
        ratings = {"p1": 1, "p2": 2, "p3": 4, "p4": 5}
        groups = {"p1": "g1", "p2": "g1", "p3": "g2", "p4": "g2"}
        rows = [{"id": identity, "raw": 1 - (rating - 1) / 4,
                 "propositions": (rating - 1) / 4, "json": (rating - 1) / 4,
                 "python": 1 - (rating - 1) / 4,
                 "fallback_by_arm": {arm: [None, None] for arm in ARMS[1:]}}
                for identity, rating in ratings.items()]
        result = evaluate_formats(rows, ratings, groups, ratings, draws=50, seed=7)
        self.assertEqual(result["metrics"]["propositions"]["spearman"], 1)
        self.assertEqual(result["metrics"]["raw"]["spearman"], -1)
        self.assertEqual(result["metrics"]["raw"]["mse_0_1"], .625)
        self.assertEqual(result["metrics"]["raw"]["mse_1_5"], 10)
        self.assertEqual(result["metrics"]["gpt_direct"]["mse_0_1"], 0)
        comparisons = result["bootstrap"]["comparisons"]
        self.assertEqual(comparisons["json_minus_propositions"]["spearman"]["interval"], [0, 0])
        self.assertEqual(comparisons["python_minus_propositions"]["spearman"]["interval"], [-2, -2])
        self.assertEqual(comparisons["propositions_minus_raw"]["spearman"]["defined_draws"], 50)

    def test_evaluation_exact_joins_and_per_side_fallback_audit(self):
        rows = [{"id": "a", **{arm: .2 for arm in ARMS}, "fallback_by_arm": {
                    "propositions": [None, None], "json": ["not_specified", None],
                    "python": ["failure:parse_error", "ambiguous"]}},
                {"id": "b", **{arm: .8 for arm in ARMS},
                 "fallback_by_arm": {arm: [None, None] for arm in ARMS[1:]}}]
        labels, groups, direct = {"a": 2, "b": 4}, {"a": "g1", "b": "g1"}, {"a": 2, "b": 4}
        result = evaluate_formats(rows, labels, groups, direct, draws=10)
        self.assertEqual(result["fallback"]["json"]["pairs_with_one"], 1)
        self.assertEqual(result["fallback"]["python"]["pairs_with_both"], 1)
        self.assertEqual(result["fallback"]["python"]["side_occurrences"], 2)
        for changed in ([rows[0]], [*rows, rows[0]]):
            with self.assertRaisesRegex(ValueError, "identical unique IDs"):
                evaluate_formats(changed, labels, groups, direct, draws=10)
        changed = copy.deepcopy(rows); changed[0]["json"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite cosine"):
            evaluate_formats(changed, labels, groups, direct, draws=10)
        changed = copy.deepcopy(rows); changed[0]["fallback_by_arm"]["json"] = [None]
        with self.assertRaisesRegex(ValueError, "two optional per-side"):
            evaluate_formats(changed, labels, groups, direct, draws=10)

    def test_shared_contract_rejects_checkpoint_prompt_or_ceiling_changes(self):
        for key, value in (("checkpoint_sha256", "0" * 64), ("prompt", "new prompt"), ("max_length", 512)):
            inputs = fixture()
            inputs["protocol"][key] = value
            with self.assertRaisesRegex(ValueError, "contract"):
                validate_inputs(inputs)

    def test_per_side_fallback_keeps_the_other_answered_side(self):
        inputs = fixture()
        inputs["sources"][0]["arms"]["json"] = {"status": "not_specified", "text": "", "failure": None}
        texts, reasons, tokens = effective_inputs(inputs, Tokenizer())
        self.assertEqual(texts["json"]["a"], "Two dogs.")
        self.assertEqual(texts["json"]["b"], "There are three dogs.")
        self.assertEqual(reasons["json"]["a"], "not_specified")
        self.assertIsNone(reasons["json"]["b"])
        self.assertEqual(len(tokens), 8)

    def test_failed_ambiguous_empty_and_overflow_are_distinct_fallbacks(self):
        for record, reason in (
            ({"status": None, "text": "", "failure": "parse_error"}, "failure:parse_error"),
            ({"status": "ambiguous", "text": "two or three", "failure": None}, "ambiguous"),
            ({"status": "answered", "text": " ", "failure": None}, "empty_evidence"),
            ({"status": "answered", "text": "OVERFLOW", "failure": None}, "token_overflow"),
        ):
            inputs = fixture()
            inputs["sources"][0]["arms"]["python"] = record
            tokenizer = Tokenizer()
            texts, reasons, retained = effective_inputs(inputs, tokenizer)
            self.assertEqual(reasons["python"]["a"], reason)
            self.assertEqual(texts["python"]["a"], inputs["sources"][0]["passage"])
            self.assertTrue(all(row["input_ids"][-1] == 99 and len(row["input_ids"]) <= 160 for row in retained))
            self.assertEqual(tokenizer.calls[0], {"padding": False, "truncation": False, "add_special_tokens": False})

    def test_original_overflow_is_a_hard_failure(self):
        inputs = fixture()
        inputs["sources"][0]["passage"] = "OVERFLOW"
        with self.assertRaisesRegex(ValueError, "original passage"):
            effective_inputs(inputs, Tokenizer())

    def test_inference_rows_use_only_constant_validation_placeholders(self):
        inputs = fixture()
        texts, _, _ = effective_inputs(inputs, Tokenizer())
        rows = inference_rows(inputs, texts["json"])
        self.assertEqual(rows[0]["rating"], 1.0)
        self.assertEqual(rows[0]["target"], 0.0)
        self.assertEqual(rows[0]["sentence1"], "There are two dogs.")
        self.assertEqual(rows[0]["group_id"], "g1")
        self.assertNotIn("rating", inputs["pairs"][0])

    def test_missing_duplicate_mismatched_or_labeled_inputs_fail(self):
        variants = []
        inputs = fixture(); inputs["sources"][1]["condition"] = "color"; variants.append(inputs)
        inputs = fixture(); inputs["sources"].append(copy.deepcopy(inputs["sources"][0])); variants.append(inputs)
        inputs = fixture(); inputs["sources"][0]["arms"].pop("python"); variants.append(inputs)
        inputs = fixture(); inputs["pairs"][0]["rating"] = 4; variants.append(inputs)
        inputs = fixture(); inputs["labels"] = []; variants.append(inputs)
        for inputs in variants:
            with self.assertRaises(ValueError):
                validate_inputs(inputs)

    def test_set_metadata_serialization_is_deterministic_and_finite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "receipt.json"
            write_json(path, {"loading": {"missing_keys": set(), "keys": {"b", "a"}}})
            first = path.read_bytes()
            write_json(path, {"loading": {"keys": {"a", "b"}, "missing_keys": set()}})
            self.assertEqual(first, path.read_bytes())
            self.assertEqual(json.loads(first)["loading"]["keys"], ["a", "b"])
            with self.assertRaises(ValueError):
                write_json(path, {"score": float("nan")})


if __name__ == "__main__":
    unittest.main()
