"""Check report source identity, calibration scope and paired subgroup analysis."""

import copy
import json
from pathlib import Path

import pytest

from csts_pilot.proposition_evidence_report import (
    APPEARANCE,
    aligned_predictions,
    bootstrap_differences,
    build_report,
    cohort_rows,
    file_sha256,
    fit_validation_calibration,
    score_rows,
)


def rows(split="validation", n=20):
    result = []
    for i in range(n):
        target = (i % 5) / 4
        result.append(
            {
                "row_id": f"{split}_{i}",
                "pair_id": f"{split}_pair_{i // 2}",
                "group_id": f"{split}_group_{i // 2}",
                "condition": "colors of clothes" if i % 2 else "shape of object",
                "sentence1": f"red square {i}",
                "sentence2": f"blue circle {i}",
                "rating": 1 + 4 * target,
                "target": target,
                "prediction": 0.2 + 0.5 * target,
            }
        )
    return result


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def test_calibration_uses_validation_and_preserves_raw_ties():
    validation = rows()
    fitted = fit_validation_calibration(validation)
    assert fitted["a"] == pytest.approx(2)
    assert fitted["c"] == pytest.approx(-0.4)
    assert fitted["validation_oof_mae_1_5"] < 1e-12
    test = rows("test")
    original = copy.deepcopy(test)
    score = score_rows(test, fitted)
    assert test == original
    assert score["spearman"] == pytest.approx(1)
    assert score["calibrated_mae_1_5"] < 1e-12
    assert score["mae_1_5"] > 0
    test[0]["target"] = 1
    test[0]["rating"] = 5
    assert fit_validation_calibration(validation) == fitted


def test_reordered_or_changed_source_labels_are_rejected():
    source = rows()
    candidates = {"ratings": copy.deepcopy(source), "evidence": copy.deepcopy(source)}
    aligned_predictions(candidates, source)
    candidates["evidence"] = list(reversed(source))
    with pytest.raises(ValueError, match="IDs, labels"):
        aligned_predictions(candidates, source)
    candidates["evidence"] = copy.deepcopy(source)
    candidates["evidence"][0]["sentence1"] = "another caption"
    with pytest.raises(ValueError, match="IDs, labels"):
        aligned_predictions(candidates, source)


def test_paired_bootstrap_and_exact_cohort_definitions():
    source = rows()
    candidates = {arm: copy.deepcopy(source) for arm in ("ratings", "evidence")}
    fitted = {arm: fit_validation_calibration(source) for arm in candidates}
    result = bootstrap_differences(candidates, fitted, draws=30, seed=9)
    assert result["groups"] == 10
    for item in result["contrasts"].values():
        assert item["difference"] == 0
        assert item["ci95"] == [0, 0]
    spec = {
        "colour_regex": r"\bcolou?rs?\b",
        "splits": {"validation": {"condition_families": {"shape of object": APPEARANCE}}},
    }
    cohorts = cohort_rows(candidates, spec, "validation")
    assert len(cohorts["appearance"]["ratings"]) == 10
    assert len(cohorts["colour"]["ratings"]) == 10
    candidates["ratings"][0]["condition"] = "discoloration of object"
    assert len(cohort_rows(candidates, spec, "validation")["colour"]["ratings"]) == 10


def test_small_cohort_undefined_ranks_are_explicit():
    tiny = rows(n=1)
    candidates = {arm: tiny for arm in ("ratings", "evidence")}
    fitted = {arm: {"a": 1, "c": 0} for arm in candidates}
    result = bootstrap_differences(candidates, fitted, draws=5, seed=1)
    assert result["contrasts"]["spearman"]["difference"] is None
    assert result["contrasts"]["spearman"]["ci95"] is None
    assert result["contrasts"]["spearman"]["defined_draws"] == 0


def fixture(root: Path):
    directory = root / "qwen_evidence_results/propositions_v41"
    directory.mkdir(parents=True, exist_ok=True)
    sources = {split: rows(split) for split in ("validation", "test")}
    settings = {
        "training": {"seed": 7},
        "bootstrap_draws": 10,
        "bootstrap_seed": 9,
        "splits": {},
    }
    for split, source in sources.items():
        path = root / f"{split}.json"
        dump(path, [{k: v for k, v in row.items() if k != "prediction"} for row in source])
        settings["splits"][split] = {
            "path": path.name,
            "sha256": file_sha256(path),
            "rows": len(source),
            "groups": 10,
        }
    taxonomy = {
        "colour_regex": r"\bcolou?rs?\b",
        "splits": {split: {"condition_families": {"shape of object": APPEARANCE}} for split in sources},
    }
    dump(root / "cohorts.json", taxonomy)
    settings["report_cohorts"] = {"path": "cohorts.json", "sha256": file_sha256(root / "cohorts.json")}
    candidates = {}
    for arm in ("ratings", "evidence"):
        model = directory / f"{arm}_selected_model.pt"
        model.write_bytes(f"selected_{arm}".encode())
        selected = {"sha256": file_sha256(model), "validation": {"spearman": 1.0}}
        candidates[arm] = {**selected, "run": {"path": "/unused/run.json"}}
        for phase in ("pretrain", "ratings"):
            dump(directory / f"{arm}_{phase}_trace.json", {"selected": selected})
        dump(directory / f"{arm}_validation_predictions.json", sources["validation"])
        dump(directory / f"{arm}_predictions.json", sources["test"])
    selection = {"status": "checkpoints_frozen", "test_scores_used_for_selection": False, "candidates": candidates}
    dump(directory / "selection.json", selection)
    summary = {
        "status": "complete",
        "source_commit": "a" * 40,
        "selection_sha256": file_sha256(directory / "selection.json"),
        "settings": settings,
        "preparation": {"answered_training_inputs": 2486},
        "live_scores": {arm: {"spearman": 1.0} for arm in candidates},
        "runs": [],
        "gpu_stage_seconds": 10,
    }
    dump(directory / "summary.json", summary)
    return directory


def test_complete_report_verifies_checkpoint_and_source_bytes(tmp_path):
    directory = fixture(tmp_path)
    report = build_report(tmp_path, directory)
    assert report["cohorts"]["test"]["all"]["scores"]["ratings"]["calibrated_mae_1_5"] < 1e-12
    assert (tmp_path / "training_outputs/csts_proposition_evidence_report.md").exists()
    (directory / "ratings_selected_model.pt").write_bytes(b"changed")
    with pytest.raises(ValueError, match="checkpoint bytes"):
        build_report(tmp_path, directory)


def test_report_rejects_modified_cohort_and_source_files(tmp_path):
    directory = fixture(tmp_path)
    (tmp_path / "cohorts.json").write_text("{}")
    with pytest.raises(ValueError, match="cohort definitions"):
        build_report(tmp_path, directory)
    directory = fixture(tmp_path)
    with (tmp_path / "validation.json").open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="source split bytes"):
        build_report(tmp_path, directory)
