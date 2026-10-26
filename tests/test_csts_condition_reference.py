"""Check masking, subtraction and frozen operating-point decisions."""

import numpy as np
import pytest
import torch

from csts_pilot.baseline_models import EOD, EncoderConfig
from csts_pilot.condition_reference import (
    confusion,
    geometry,
    native_layout,
    pooled_states,
    recall_cutoff,
    representations,
    select_arm,
    sentence_tokens,
    unit,
)


def test_sentence_offset_mask_excludes_prompt_specials_and_eod():
    class Tokenizer:
        all_special_ids = (99,)

        def get_vocab(self):
            return {EOD: 99}

        def __call__(self, texts, **kwargs):
            ids, offsets = [], []
            for text in texts:
                start = text.index("Query: ") + len("Query: ")
                ids.append([1, 2, 99, 3])
                offsets.append(
                    [
                        (0, start - 1),
                        (start - 1, start + 3),
                        (start + 3, start + 4),
                        (start + 4, len(text)),
                    ]
                )
            return {"input_ids": ids, "offset_mapping": offsets}

    sequences, masks = sentence_tokens(
        Tokenizer(), [("color", "red car")], EncoderConfig(device="cpu")
    )
    assert sequences == [[1, 2, 99, 3, 99]]
    assert masks == [[False, True, False, True, False]]


@pytest.mark.parametrize(
    "attention,mask",
    [
        ([[0, 1, 1, 1]], [[0, 0, 1, 0]]),
        ([[1, 1, 1, 0]], [[0, 1, 0, 0]]),
    ],
)
def test_pooling_honors_eod_and_both_padding_sides(attention, mask):
    hidden = torch.arange(8).reshape(1, 4, 2).float()
    attention = torch.tensor(attention)
    raw, mean = pooled_states(hidden, attention, torch.tensor(mask))
    last = torch.where(attention[0].bool())[0][-1]
    torch.testing.assert_close(raw[0], hidden[0, last])
    torch.testing.assert_close(mean[0], hidden[0, torch.tensor(mask[0]).bool()][0])


def test_raw_and_unit_first_subtraction_match_the_analytic_example():
    cache = {
        "keys": [("c", "one"), ("c", "two")],
        "raw": torch.tensor([[1.0, 0.0, 2.0], [0.0, 1.0, 2.0]]),
        "means": torch.eye(3)[:2],
        "reference_keys": [("c", ""), ("", "")],
        "references": torch.tensor([[0.0, 0.0, 2.0], [0.0, 0.0, 1.0]]),
    }
    result = representations(cache)
    assert result["A"][0] @ result["A"][1] == pytest.approx(0.8)
    assert result["B_r"][0] @ result["B_r"][1] == pytest.approx(0)
    assert result["B_u"][0] @ result["B_u"][1] == pytest.approx(
        (1 - 2 / np.sqrt(5)) / 2
    )
    with pytest.raises(ValueError, match="indices"):
        unit(np.zeros((1, 3)))


def test_cutoff_is_largest_with_required_recall_and_ties_are_included():
    rows = [{"rating": 5}] * 10 + [{"rating": 1}, {"rating": 2}, {"rating": 3}]
    scores = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2, 0.1, 0.2, 0.1, 0.9])
    cutoff = recall_cutoff(rows, scores)
    assert cutoff == 0.2
    result = confusion(rows, scores, cutoff)
    assert (result["tp"], result["fn"], result["fp"], result["tn"]) == (9, 1, 1, 1)
    assert result["recall"] == 0.9
    assert result["excluded_middle_rating"] == 1


def test_selection_obeys_both_gates_and_tie_order():
    def metric(fpr, rank):
        return {
            "spearman": rank,
            "operating_point": {"false_positive_rate": fpr, "cutoff": 0.5},
        }

    metrics = {
        "A": metric(0.15, 0.8),
        "B_u": metric(0.12, 0.796),
        "B_r": metric(0.12, 0.796),
        "D": metric(0.10, 0.79),
    }
    result = select_arm(metrics)
    assert result["selected_arm"] == "B_u"
    assert not result["eligibility"]["D"]["eligible"]
    assert not result["test_scores_used_for_selection"]


def test_geometry_matches_direct_cosines_and_covariance():
    x = unit(np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]]))
    result = geometry(x)
    direct = x @ x.T
    assert result["mean_pairwise_cosine"] == pytest.approx((direct.sum() - 3) / 6)
    covariance = np.cov(x, rowvar=False, bias=True)
    assert result["covariance_trace"] == pytest.approx(np.trace(covariance))
    assert result["sample_covariance_rank_ceiling"] == 2


def test_native_evaluation_declares_its_objective():
    from viper.authoring import input, stage
    from viper.metrics import FloatComparator, MetricDependency, measure
    from viper.metrics import max as maximize
    from viper.outputs import EvalOutputs, output

    from csts_pilot.condition_reference import AnalysisConfig, analyze, native_spearman
    from jep_pilot.loaders import load_json

    measured = measure(
        native_spearman,
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
        dependencies=(
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        ),
    )
    configured = stage(
        analyze,
        stage_id="analysis",
        eval_id="condition_reference_check",
        config=AnalysisConfig(rows_sha256="0" * 64, split="validation"),
        inputs=(input("rows", path="csts_data/dev.json", data_role="eval"),),
        split_inputs=("rows",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            )
        ),
        metrics=(measured,),
        objective=maximize(measured),
        reuse="never",
    )
    assert configured.spec.kind == "eval"


def test_native_layout_retains_original_pair_batches_and_row_indices():
    rows = [
        {"condition": "c", "sentence1": f"a{i}", "sentence2": f"b{i}"} for i in range(3)
    ]
    keys, left, right = native_layout(rows)
    assert keys == [("c", p) for p in ("a0", "a1", "b0", "b1", "a2", "b2")]
    assert left == [0, 1, 4]
    assert right == [2, 3, 5]
