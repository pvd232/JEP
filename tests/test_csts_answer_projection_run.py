"""Check transformed prediction binding before restoring original passages."""

import pytest

from csts_pilot.answer_projection_run import original_predictions


def inputs():
    """Return two distinct comparisons and their condition-specific answers."""
    original = [
        {
            "row_id": "a",
            "condition": "color",
            "sentence1": "red car",
            "sentence2": "blue car",
            "target": 0.0,
        },
        {
            "row_id": "b",
            "condition": "color",
            "sentence1": "green car",
            "sentence2": "green vehicle",
            "target": 1.0,
        },
    ]
    transformed = [
        dict(original[0], sentence1="red", sentence2="blue"),
        dict(original[1], sentence1="green", sentence2="green"),
    ]
    predictions = [
        dict(transformed[1], prediction=0.9),
        dict(transformed[0], prediction=0.1),
    ]
    return original, transformed, predictions


def test_prediction_order_is_restored_by_exact_row_identity():
    original, transformed, predictions = inputs()
    assert original_predictions(original, transformed, predictions) == [
        dict(original[0], prediction=0.1),
        dict(original[1], prediction=0.9),
    ]


@pytest.mark.parametrize("change", ("duplicate", "answer", "metadata"))
def test_changed_or_duplicate_prediction_bindings_are_rejected(change):
    original, transformed, predictions = inputs()
    if change == "duplicate":
        predictions[1] = dict(predictions[0])
    elif change == "answer":
        predictions[0]["sentence2"] = "wrong answer"
    else:
        transformed[0]["condition"] = "wrong condition"
    with pytest.raises(ValueError):
        original_predictions(original, transformed, predictions)


@pytest.mark.parametrize("value", (float("nan"), float("inf")))
def test_nonfinite_projection_scores_are_rejected(value):
    original, transformed, predictions = inputs()
    predictions[0]["prediction"] = value
    with pytest.raises(ValueError, match="finite"):
        original_predictions(original, transformed, predictions)
