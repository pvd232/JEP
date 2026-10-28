"""Protect the common cohort comparison and source group inference."""

import copy
import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "native_finalization",
    Path(__file__).parents[1] / "scripts/finalize_csts_native_comparison.py",
)
finalization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finalization)

completed_spec = importlib.util.spec_from_file_location(
    "completed_native_scoring",
    Path(__file__).parents[1] / "scripts/score_completed_csts_native.py",
)
completed = importlib.util.module_from_spec(completed_spec)
completed_spec.loader.exec_module(completed)


def rows():
    return [
        {
            "row_id": str(i),
            "group_id": str(i // 2),
            "pair_id": str(i // 2),
            "sentence1": f"first {i}",
            "sentence2": f"second {i}",
            "condition": f"condition {i}",
            "rating": i % 5 + 1,
            "target": (i % 5) / 4,
        }
        for i in range(8)
    ]


def test_reference_subset_uses_original_order_and_exact_inputs():
    current = rows()
    archived = [dict(r, prediction=r["target"]) for r in reversed(current[:-1])]
    shared, values = finalization.align_reference(current, archived)
    assert shared == current[:-1]
    np.testing.assert_array_equal(values, [r["target"] for r in shared])
    changed = copy.deepcopy(archived)
    changed[0]["condition"] = "another condition"
    with pytest.raises(ValueError, match="text or target"):
        finalization.align_reference(current, changed)
    with pytest.raises(ValueError, match="unique"):
        finalization.align_reference(current, archived + archived[:1])


def test_source_group_bootstrap_identity_and_seed_variation():
    current = rows()
    values = np.array([r["target"] for r in current])
    result = finalization.contrast(
        current, {"7": values, "8": values, "9": values}, values, draws=40
    )
    assert result["groups"] == 4
    assert result["mean_spearman_difference"] == 0
    assert result["seed_difference_sample_std"] == 0
    assert result["group_bootstrap_95"]["low"] == 0
    assert result["group_bootstrap_95"]["high"] == 0


def test_completed_score_freezes_the_model_and_remaining_protocol():
    selected = {"sha256": "a" * 64, "epoch": 3}
    fitted = {
        "status": "succeeded",
        "cloud_status": "published",
        "selected": selected,
        "seed": 8,
        "source_commit": "b" * 40,
        "terminal": {"status": "succeeded"},
    }
    trace = {"selected": selected, "budget_censored": False}
    protocol = {"settings_sha256": "c" * 64, "executed_seeds": [7, 8, 9]}
    frozen = completed.frozen_selection(fitted, trace, "c" * 64, protocol)
    assert frozen["selected_model_sha256"] == {"8": "a" * 64}
    assert frozen["executed_seeds"] == [7, 8, 9]
    for changed in (
        {"status": "running"},
        {"terminal": {"status": "failed"}},
        {"seed": 99},
    ):
        with pytest.raises(ValueError):
            completed.frozen_selection({**fitted, **changed}, trace, "c" * 64, protocol)
    with pytest.raises(ValueError):
        completed.frozen_selection(
            fitted, {**trace, "budget_censored": True}, "c" * 64, protocol
        )
    with pytest.raises(ValueError):
        completed.frozen_selection(fitted, trace, "d" * 64, protocol)
    assert completed.frozen_selection(
        {**fitted, "cloud_status": "pending"}, trace, "c" * 64, protocol
    )["selected_model_sha256"] == {"8": "a" * 64}


def test_reusing_completed_scores_checks_selected_model_and_test():
    saved = {
        "status": "complete",
        "cloud_status": "published",
        "seed": 8,
        "selected_model_sha256": "a" * 64,
        "test_sha256": "b" * 64,
        "selection": {"selected_model_sha256": {"8": "a" * 64}},
        "runs": {"test": {"cloud_reference": {"sha256": "c" * 64}}},
    }
    ref = finalization.completed_score_source(saved, "8", "a" * 64, "b" * 64, "test")
    assert ref["reference"] == saved["runs"]["test"]["cloud_reference"]
    with pytest.raises(ValueError):
        finalization.completed_score_source(saved, "8", "d" * 64, "b" * 64, "test")
    with pytest.raises(ValueError):
        finalization.completed_score_source(saved, "8", "a" * 64, "d" * 64, "test")
