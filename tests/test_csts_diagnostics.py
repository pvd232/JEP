"""Check metrics that distinguish conditional comparisons from score calibration."""

import pytest

from csts_pilot.diagnostics import summarize


def test_equal_scores_receive_half_credit_for_condition_ordering():
    rows = [
        {
            "target": 0.0,
            "rating": 1.0,
            "prediction": 0.5,
            "pair_id": "pair",
            "condition": "color",
        },
        {
            "target": 1.0,
            "rating": 5.0,
            "prediction": 0.5,
            "pair_id": "pair",
            "condition": "action",
        },
    ]
    metrics = summarize(rows)
    assert metrics["spearman"] is None
    assert metrics["condition_changes"]["n"] == 1
    assert metrics["condition_changes"]["ties"] == 1
    assert metrics["condition_changes"]["accuracy_ties_half"] == 0.5
    assert metrics["condition_changes"]["difference_mse"] == 1.0
    assert metrics["mse_1_5"] == 16 * metrics["mse_0_1"]


def test_condition_change_error_and_ranking_are_separate():
    rows = [
        {
            "target": 0.0,
            "rating": 1.0,
            "prediction": 0.4,
            "pair_id": "pair",
            "condition": "color",
        },
        {
            "target": 1.0,
            "rating": 5.0,
            "prediction": 0.6,
            "pair_id": "pair",
            "condition": "action",
        },
    ]
    metrics = summarize(rows)
    assert metrics["condition_changes"]["accuracy_ties_half"] == 1.0
    assert metrics["condition_changes"]["difference_mse"] == pytest.approx(0.64)
