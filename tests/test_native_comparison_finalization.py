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
