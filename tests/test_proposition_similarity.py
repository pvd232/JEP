"""Contract tests for the paired evidence similarity experiment."""

import copy
import importlib.util
import json
import math
import unittest

from csts_pilot.proposition_similarity import (
    MODEL_ID, PROMPT, REVISION, component_resamples, evaluate_predictions,
    json_bytes, last_token_pool, pair_predictions, spearman, token_sequences, validate_inputs,
)


class Tokenizer:
    def __init__(self):
        self.calls = []

    def __call__(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        return {"input_ids": [[10, 20], [30]] if len(texts) == 2 else [[10, 20]]}

    def get_vocab(self):
        return {"<|endoftext|>": 99}


def fixture():
    return {
        "protocol": {"model_id": MODEL_ID, "revision": REVISION, "prompt": PROMPT, "max_length": 512, "batch_size": 4, "seed": 42},
        "sources": [
            {"id": "a", "passage": "Two dogs.", "condition": "animal count", "status": "answered", "evidence_text": "There are two dogs."},
            {"id": "b", "passage": "Three dogs.", "condition": "animal count", "status": "answered", "evidence_text": "There are three dogs."},
            {"id": "c", "passage": "Dogs.", "condition": "animal count", "status": "ambiguous", "evidence_text": "The number of dogs is unclear."},
        ],
        "pairs": [
            {"id": "p1", "source_a": "a", "source_b": "b", "group_id": "g1"},
            {"id": "p2", "source_a": "c", "source_b": "a", "group_id": "g1"},
            {"id": "p3", "source_a": "b", "source_b": "c", "group_id": "g2"},
        ],
    }


class InputTests(unittest.TestCase):
    def test_nested_loading_info_sets_have_stable_json(self):
        first = {"model_loading": {"missing_keys": set(), "unexpected_keys": set(),
                                  "nested": [{"keys": {"z.weight", "a.weight"}}]}}
        second = {"model_loading": {"nested": [{"keys": {"a.weight", "z.weight"}}],
                                   "unexpected_keys": set(), "missing_keys": set()}}
        encoded = json_bytes(first)
        self.assertEqual(encoded, json_bytes(second))
        self.assertEqual(json.loads(encoded)["model_loading"], {
            "missing_keys": [], "unexpected_keys": [],
            "nested": [{"keys": ["a.weight", "z.weight"]}],
        })
        for _ in range(3):
            self.assertEqual(encoded, json_bytes(first))
        with self.assertRaisesRegex(TypeError, "Unsupported JSON value: object"):
            json_bytes({"model_loading": {"unsupported": object()}})

    def test_tokenization_appends_exact_eod_without_special_tokens_or_truncation(self):
        tokenizer = Tokenizer()
        result = token_sequences(tokenizer, [("color", "Brown dog."), ("color", "Black dog.")], 3)
        self.assertEqual(result, [[10, 20, 99], [30, 99]])
        self.assertEqual(tokenizer.calls[0][0][0], PROMPT.format(condition="color", passage="Brown dog."))
        self.assertEqual(tokenizer.calls[0][1], {"padding": False, "truncation": False, "add_special_tokens": False})

    def test_overlong_sequence_fails_instead_of_silent_truncation(self):
        with self.assertRaisesRegex(ValueError, "no inputs were truncated"):
            token_sequences(Tokenizer(), [("color", "dog")], 2)

    def test_mismatched_source_condition_and_duplicate_ids_rejected(self):
        value = fixture()
        value["sources"][1]["condition"] = "color"
        with self.assertRaisesRegex(ValueError, "share its condition"):
            validate_inputs(value)
        value = fixture()
        value["sources"][1]["id"] = "a"
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_inputs(value)

    def test_fallback_is_symmetric_and_ambiguous_evidence_is_not_embedded_as_answer(self):
        value = fixture()
        cosines = {("raw", "a", "b"): .2, ("evidence", "a", "b"): .3,
                   ("raw", "c", "a"): .4, ("raw", "b", "c"): .5}
        result = pair_predictions(value, cosines)
        self.assertEqual([p["fallback"] for p in result], [False, True, True])
        self.assertEqual([p["evidence_cosine"] for p in result], [.3, .4, .5])
        value["sources"][1]["evidence_text"] = "  "
        self.assertTrue(pair_predictions(value, cosines)[0]["fallback"])

    @unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch is needed for the actual pooling tensor test")
    def test_last_attended_token_pooling_handles_both_padding_sides(self):
        import torch
        hidden = torch.tensor([[[0., 5.], [3., 4.], [100., 0.]], [[100., 0.], [0., 8.], [4., 3.]]])
        masks = torch.tensor([[1, 1, 0], [0, 1, 1]])
        result = last_token_pool(hidden, masks)
        torch.testing.assert_close(result, torch.tensor([[.6, .8], [.8, .6]]))
        with self.assertRaises(ValueError):
            last_token_pool(hidden, torch.zeros_like(masks))


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.predictions = [
            {"id": "p1", "raw_cosine": -.5, "evidence_cosine": .0, "fallback": False},
            {"id": "p2", "raw_cosine": .2, "evidence_cosine": .5, "fallback": False},
            {"id": "p3", "raw_cosine": .8, "evidence_cosine": .8, "fallback": True},
        ]
        self.labels = {"p3": 5., "p1": 1., "p2": 3.}
        self.groups = {"p1": "g1", "p2": "g1", "p3": "g2"}

    def test_spearman_ties_and_constants(self):
        self.assertAlmostEqual(spearman([1, 1, 3], [1, 2, 3]), math.sqrt(3) / 2)
        self.assertIsNone(spearman([1, 1, 1], [1, 2, 3]))

    def test_component_bootstrap_never_splits_rows_within_group(self):
        draws = component_resamples(["g1", "g1", "g2"], 50, 42)
        self.assertEqual(draws, component_resamples(["g1", "g1", "g2"], 50, 42))
        self.assertTrue(any(draw.count(0) == 2 for draw in draws))
        for draw in draws:
            self.assertEqual(draw.count(0), draw.count(1))
            self.assertEqual(draw.count(0) + draw.count(2), 2)

    def test_exact_id_join_unclipped_mse_and_direct_scale(self):
        result = evaluate_predictions(self.predictions, self.labels, self.groups, draws=40, direct_by_id={"p1": 1, "p2": 3, "p3": 5})
        self.assertAlmostEqual(result["metrics"]["raw"]["mse_0_1"], (.25 + .09 + .04) / 3)
        self.assertAlmostEqual(result["metrics"]["raw"]["mse_1_5"], 16 * (.25 + .09 + .04) / 3)
        self.assertEqual(result["metrics"]["gpt_direct"]["mse_0_1"], 0)
        self.assertEqual(result["fallback_pairs"], 1)
        self.assertEqual(result["answered_pairs_only"]["n"], 2)
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["groups"], 2)
        self.assertAlmostEqual(result["metrics"]["propositions_with_fallback"]["mse_0_1"], .04 / 3)

    def test_reordering_predictions_and_maps_preserves_point_metrics(self):
        a = evaluate_predictions(self.predictions, self.labels, self.groups, draws=20)
        b = evaluate_predictions(list(reversed(self.predictions)), self.labels, self.groups, draws=20)
        self.assertEqual(a["metrics"], b["metrics"])

    def test_missing_extra_duplicate_or_nonfinite_scores_fail(self):
        for labels in ({"p1": 1., "p2": 3.}, dict(self.labels, extra=4.)):
            with self.assertRaisesRegex(ValueError, "IDs"):
                evaluate_predictions(self.predictions, labels, self.groups, draws=5)
        value = copy.deepcopy(self.predictions)
        value[1]["id"] = "p1"
        with self.assertRaises(ValueError):
            evaluate_predictions(value, self.labels, self.groups, draws=5)
        value = copy.deepcopy(self.predictions)
        value[0]["raw_cosine"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            evaluate_predictions(value, self.labels, self.groups, draws=5)

    def test_fallback_cannot_change_score(self):
        value = copy.deepcopy(self.predictions)
        value[-1]["evidence_cosine"] = .9
        with self.assertRaisesRegex(ValueError, "preserve the raw"):
            evaluate_predictions(value, self.labels, self.groups, draws=5)


if __name__ == "__main__":
    unittest.main()
