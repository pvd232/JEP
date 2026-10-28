"""Check early diagnostic alignment and unchanged-baseline comparisons."""

import copy
import json

import pytest

from csts_pilot.proposition_indicative_report import build_indicative_report
from csts_pilot.proposition_evidence_report import file_sha256


def fixture(root):
    directory = root / "indicative"
    directory.mkdir()
    baseline = [
        {
            "row_id": f"r{i}",
            "pair_id": f"p{i // 2}",
            "group_id": f"g{i // 2}",
            "sentence1": f"red dog {i}",
            "sentence2": f"blue dog {i}",
            "condition": "color of dog",
            "target": (i % 5) / 4,
            "rating": 1 + i % 5,
            "prediction": 0.1 + 0.7 * (i % 5) / 4,
        }
        for i in range(20)
    ]
    source = [{k: v for k, v in row.items() if k != "prediction"} for row in baseline]
    path = root / "validation.json"
    path.write_text(json.dumps(source))
    cohorts = {
        "colour_regex": r"\bcolou?rs?\b",
        "splits": {"validation": {"condition_families": {"color of dog": "appearance-and-sensory-attributes"}}},
    }
    (root / "cohorts.json").write_text(json.dumps(cohorts))
    raw = {
        "arms": {arm: copy.deepcopy(baseline) for arm in ("ratings", "evidence")},
        "baseline": baseline,
        "protocol": {
            "validation": {"path": "validation.json", "sha256": file_sha256(path), "rows": 20, "groups": 10},
            "report_cohorts": {"path": "cohorts.json", "sha256": file_sha256(root / "cohorts.json")},
            "bootstrap_draws": 10,
            "seed": 7,
            "auxiliary_updates": 8,
            "rating_updates": 25,
        },
        "traces": {arm: {"updates": 33} for arm in ("ratings", "evidence")},
    }
    (directory / "results.json").write_text(json.dumps(raw))
    return directory, raw


def test_indicative_report_retains_protocol_and_three_paired_contrasts(tmp_path):
    directory, raw = fixture(tmp_path)
    original = copy.deepcopy(raw)
    result = build_indicative_report(tmp_path, directory)
    assert json.loads((directory / "results.json").read_text()) == original
    assert result["status"] == "early_validation_diagnostic_complete"
    assert result["protocol"]["auxiliary_updates"] == 8
    assert set(result["cohorts"]) == {"all", "appearance", "colour"}
    for cohort in result["cohorts"].values():
        assert set(cohort["paired_intervals"]) == {
            "evidence_minus_ratings", "ratings_minus_baseline", "evidence_minus_baseline"
        }
        for contrast in cohort["paired_intervals"].values():
            assert contrast["contrasts"]["spearman"]["difference"] == 0
            assert contrast["contrasts"]["spearman"]["ci95"] == [0, 0]
    assert (directory / "indicative_report.md").exists()


def test_indicative_report_rejects_baseline_order_mismatch(tmp_path):
    directory, raw = fixture(tmp_path)
    raw["baseline"].reverse()
    (directory / "results.json").write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="IDs, labels"):
        build_indicative_report(tmp_path, directory)


def test_indicative_report_requires_source_sha_and_exact_arms(tmp_path):
    directory, raw = fixture(tmp_path)
    raw["protocol"]["validation"]["sha256"] = "0" * 64
    (directory / "results.json").write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="source split bytes"):
        build_indicative_report(tmp_path, directory)
