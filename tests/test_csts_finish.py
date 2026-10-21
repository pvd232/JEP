"""Require all evaluations and cloud-verified cleanup before shutdown."""

import json

import pytest
from csts_pilot.finish_study import ARMS, SEEDS, aggregate, ready


def test_completion_requires_every_arm_seed_and_verified_cleanup():
    summary = {
        "status": "complete",
        "evaluation": [
            {
                "arm": arm,
                "seed": seed,
                "diagnostics": {"n": 2620, "mse_0_1": 0.1, "spearman": 0.5},
            }
            for arm in ARMS
            for seed in SEEDS
        ],
    }
    storage = {
        "status": "complete",
        "files": 362,
        "cloud_completion": {"sha256": "verified"},
    }
    assert ready(summary, storage)
    assert not ready(summary, {})
    assert not ready(dict(summary, status="training"), storage)
    incomplete = dict(summary, evaluation=summary["evaluation"][:-1])
    with pytest.raises(ValueError, match="one evaluation"):
        ready(incomplete, storage)
    repeated = dict(
        summary, evaluation=summary["evaluation"][:-1] + summary["evaluation"][:1]
    )
    with pytest.raises(ValueError, match="one evaluation"):
        ready(repeated, storage)


def test_paired_intervals_average_losses_across_matched_seeds(tmp_path):
    summary = {
        "source_commit": "test",
        "data_manifest": {},
        "selected": {},
        "runs": [],
        "evaluation": [],
    }
    for arm in ARMS:
        for seed, offset in zip(SEEDS, (0.1, -0.1, 0.1), strict=True):
            directory = tmp_path / f"{arm}_{seed}"
            predictions = directory / "artifacts/eval/predictions/predictions.json"
            predictions.parent.mkdir(parents=True)
            error = 0.2 if arm == "joint" else offset
            comparisons = [
                {
                    "sentence1": str(i),
                    "sentence2": "caption",
                    "condition": "color",
                    "target": 0.5,
                    "prediction": 0.5 + error,
                    "group_id": str(i),
                }
                for i in range(3)
            ]
            predictions.write_text(json.dumps(comparisons))
            summary["evaluation"].append(
                {
                    "arm": arm,
                    "seed": seed,
                    "path": str(directory / "resolved.yaml"),
                    "diagnostics": {
                        "mse_0_1": error**2,
                        "spearman": 0.5,
                        "condition_changes": {"accuracy_ties_half": 0.75},
                    },
                }
            )
    result = aggregate(summary)
    interval = result["paired_mse_intervals"]["joint_minus_ratings"]
    assert interval["difference"] == pytest.approx(0.03)
    assert interval["lower_95"] == pytest.approx(0.03)
    assert interval["upper_95"] == pytest.approx(0.03)
    assert result["means"]["ratings"]["mse_0_1"] == pytest.approx(0.01)
