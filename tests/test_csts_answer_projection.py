"""Check full-cohort answer replacement and original-source split integrity."""

import copy

import pytest

from csts_pilot.answer_projection import transform_rows, validate_original_split
from csts_pilot.answers import answer_id


def row(index=0):
    return {
        "row_id": f"row-{index}",
        "pair_id": f"pair-{index}",
        "group_id": f"group-{index}",
        "sentence1": f"A red car {index}.",
        "sentence2": f"A blue car {index}.",
        "condition": "car color",
        "rating": 2.0,
        "target": 0.25,
    }


def test_transform_preserves_all_rows_identity_labels_fields_and_original_objects():
    rows = [row(index) for index in range(3)]
    before = copy.deepcopy(rows)
    records = {}
    for index, sides in ((0, ("sentence1", "sentence2")), (1, ("sentence1",))):
        for side in sides:
            key = answer_id(rows[index][side], rows[index]["condition"])
            records[key] = {
                "valid": True,
                "answer": "red" if side == "sentence1" else "blue",
            }
    result, audit = transform_rows(rows, records)
    assert rows == before
    assert len(result) == len(rows)
    assert audit["comparison_coverage"] == {"both": 1, "one": 1, "neither": 1}
    assert audit["accepted_side_occurrences"] == 3
    assert audit["accepted_count_per_row"] == [2, 1, 0]
    assert audit["fallback_side_occurrences"] == 3
    assert result[0]["sentence1"] == "red" and result[0]["sentence2"] == "blue"
    assert result[1]["sentence2"] == rows[1]["sentence2"]
    assert result[2] == rows[2]
    for old, changed in zip(rows, result, strict=True):
        assert changed.keys() == old.keys()
        assert {
            key: value
            for key, value in changed.items()
            if key not in {"sentence1", "sentence2"}
        } == {
            key: value
            for key, value in old.items()
            if key not in {"sentence1", "sentence2"}
        }


def test_rejected_answers_fallback_and_shared_transformed_answers_do_not_change_sources():
    training, validation = [row(0)], [row(1)]
    validate_original_split(training, validation)
    records = {
        answer_id(item["sentence1"], item["condition"]): {
            "valid": True,
            "answer": "red",
        }
        for item in training + validation
    }
    records[answer_id(training[0]["sentence2"], training[0]["condition"])] = {
        "valid": False,
        "answer": "NOT_SPECIFIED",
    }
    train_changed, _ = transform_rows(training, records)
    valid_changed, _ = transform_rows(validation, records)
    assert train_changed[0]["sentence1"] == valid_changed[0]["sentence1"] == "red"
    assert train_changed[0]["sentence2"] == training[0]["sentence2"]
    assert train_changed[0]["group_id"] != valid_changed[0]["group_id"]


@pytest.mark.parametrize("identity", ("row_id", "group_id"))
def test_original_split_rejects_shared_comparison_or_source_group(identity):
    training, validation = [row(0)], [row(1)]
    validation[0][identity] = training[0][identity]
    with pytest.raises(ValueError, match="overlap"):
        validate_original_split(training, validation)


def test_original_split_rejects_canonical_caption_overlap_even_with_different_group_ids():
    training, validation = [row(0)], [row(1)]
    validation[0]["sentence2"] = "  A  RED CAR 0. "
    with pytest.raises(ValueError, match="source captions"):
        validate_original_split(training, validation)
