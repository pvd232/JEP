"""Check cache safety, missing-side fallback, batching and saved comparator use."""

import copy
import json

import numpy as np
import pytest

from csts_pilot.answer_input import (
    ARMS,
    GENERIC_CONDITION,
    answer_layout,
    baseline_scores,
    decide,
    replaced_rows,
)
from csts_pilot.answers import answer_id
from csts_pilot.evidence_controls import checked_cache


def row(index=0):
    return {
        "row_id": str(index),
        "pair_id": str(index),
        "group_id": str(index),
        "sentence1": f"A red car {index}.",
        "sentence2": f"A blue car {index}.",
        "condition": "car color",
        "rating": 2.0,
        "target": 0.25,
    }


def accepted(passage, condition, answer):
    return {
        "id": answer_id(passage, condition),
        "passage": passage,
        "condition": condition,
        "answer": answer,
        "valid": True,
        "response": json.dumps(
            {"target": "car", "attribute": "color", "evidence": answer}
        ),
        "review_response": '{"accept":true}',
    }


def test_saved_comparator_reorders_without_reencoding_and_rejects_changes():
    rows = [row(0), row(1)]
    saved = [dict(rows[1], prediction=0.2), dict(rows[0], prediction=0.6)]
    np.testing.assert_array_equal(baseline_scores(rows, saved), [0.6, 0.2])
    for changed in (
        [saved[0], saved[0]],
        [dict(saved[0], sentence1="changed"), saved[1]],
        [dict(saved[0], prediction=float("nan")), saved[1]],
    ):
        with pytest.raises(ValueError):
            baseline_scores(rows, changed)


def test_cache_rejects_unsupported_or_unreviewed_accepted_answer(tmp_path):
    comparison = row()
    record = accepted(comparison["sentence1"], comparison["condition"], "red")
    path = tmp_path / "answers.jsonl"
    path.write_text(json.dumps(record) + "\n")
    assert checked_cache(path)[record["id"]]["answer"] == "red"
    for changed in (
        dict(record, answer="green"),
        dict(record, review_response='{"accept":false}'),
        dict(record, id="wrong"),
    ):
        path.write_text(json.dumps(changed) + "\n")
        with pytest.raises(ValueError):
            checked_cache(path)


@pytest.mark.parametrize("arm", ARMS)
def test_missing_side_preserves_original_passage_and_condition(arm):
    comparison = row()
    record = accepted(comparison["sentence1"], comparison["condition"], "red")
    active, indices, counts = replaced_rows([comparison], {record["id"]: record}, arm)
    assert indices == [0] and counts == [1]
    assert active[0]["sentence1"] == "red"
    assert active[0]["sentence2"] == comparison["sentence2"]
    expected = GENERIC_CONDITION if arm.endswith("generic") else comparison["condition"]
    assert active[0]["side_conditions"] == [expected, comparison["condition"]]
    assert comparison == row()


def test_no_accepted_sides_are_skipped_and_not_represented_by_common_missing_token():
    comparison = row()
    record = dict(
        accepted(comparison["sentence1"], comparison["condition"], "red"),
        valid=False,
        answer="NOT_SPECIFIED",
    )
    assert replaced_rows([comparison], {record["id"]: record}, ARMS[0]) == ([], [], [0])


def test_two_pair_batch_layout_retains_left_then_right_and_side_conditions():
    rows = [dict(row(i), side_conditions=[f"L{i}", f"R{i}"]) for i in range(3)]
    keys, left, right = answer_layout(rows)
    assert left == [0, 1, 4] and right == [2, 3, 5]
    assert [condition for condition, _ in keys] == ["L0", "L1", "R0", "R1", "L2", "R2"]
    for index, comparison in enumerate(rows):
        assert keys[left[index]][1] == comparison["sentence1"]
        assert keys[right[index]][1] == comparison["sentence2"]


def test_gate_requires_ranking_gain_and_both_guards():
    native = {
        "spearman": 0.78,
        "operating_point": {"false_positive_rate": 0.1, "cutoff": 0.5},
        "condition_changes": {"accuracy_ties_half": 0.9},
    }
    metrics = {"saved_qwen": native, **{arm: copy.deepcopy(native) for arm in ARMS}}
    metrics[ARMS[0]]["spearman"] = 0.785
    metrics[ARMS[0]]["condition_changes"]["accuracy_ties_half"] = 0.89
    metrics[ARMS[0]]["operating_point"]["false_positive_rate"] = 0.11
    assert decide(metrics)["selected_arm"] == ARMS[0]
    metrics[ARMS[0]]["operating_point"]["false_positive_rate"] = 0.11001
    assert decide(metrics)["selected_arm"] is None
    metrics[ARMS[0]]["operating_point"]["false_positive_rate"] = 0.1
    metrics[ARMS[0]]["condition_changes"]["accuracy_ties_half"] = None
    assert decide(metrics)["selected_arm"] is None
