"""Check the independence and score-scale invariants of the natural-text run."""

import pytest

from csts_pilot.data import canonical, normalize_rating, partition


def row(a, b, condition="type of animal", label=3):
    return {"sentence1": a, "sentence2": b, "condition": condition, "label": label}


def test_connected_sources_and_conditions_stay_together():
    training = [row("A", "B"), row("B", "C"), row("A", "B", "color", 5)]
    training += [row(f"source {i}", f"other {i}", label=1 + i % 5) for i in range(100)]
    parts, _ = partition(training, [row("held out", "evidence", label=5)])
    homes = {r["sentence1"]: name for name, rows in parts.items() for r in rows}
    assert homes["A"] == homes["B"]
    assert (
        len(
            {
                name
                for name, rows in parts.items()
                if any(r["sentence1"] == "A" for r in rows)
            }
        )
        == 1
    )
    assert parts["train"] and parts["dev"]


def test_evaluation_overlap_removes_whole_training_component():
    training = [row("Shared caption", "indirect"), row("indirect", "third")]
    training += [row("independent", "caption")]
    parts, manifest = partition(training, [row(" SHARED   CAPTION ", "evaluation")])
    assert manifest["overlapping_training_rows_removed"] == 2
    assert sum(len(parts[name]) for name in ("train", "dev")) == 1
    assert canonical(" SHARED   CAPTION ") == canonical("Shared caption")


def test_invalid_rows_and_rating_scale():
    parts, manifest = partition(
        [row("a", "b"), row("c", "d", label=-1)], [row("e", "f", label=1)]
    )
    assert manifest["invalid_rows_removed"]["train"] == 1
    assert normalize_rating(1) == 0
    assert normalize_rating(3) == 0.5
    assert normalize_rating(5) == 1
    assert parts["evaluation"][0]["target"] == 0
    with pytest.raises(ValueError):
        normalize_rating(-1)
