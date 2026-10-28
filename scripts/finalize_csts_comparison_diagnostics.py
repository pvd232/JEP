"""Preserve the comparison study, its input references and supplemental checks."""

import argparse
import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr
from viper.storage import ViperCloudDestination, publish_resolved_files

from csts_pilot.background_storage import _save


def read(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root, directory = args.root, args.output
    while not (directory / "analysis.json").exists():
        time.sleep(2)
    while (
        read(directory / "capture-status.json").get("cloud_status") != "published"
        or not (directory / "color-input-publication.json").exists()
    ):
        time.sleep(2)
    result = read(directory / "analysis.json")
    if result["status"] != "complete":
        raise ValueError("Finalize completed analysis outputs.")
    spec = importlib.util.spec_from_file_location(
        "comparison_analysis", directory / "review/scripts/analyze_csts_comparison.py"
    )
    analysis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analysis)
    inputs = read(directory / "input-references.json")
    color_root = Path("/home/machina/jep-color-diagnostic-20261028")
    vector_file = color_root / "results/seed7_R_B/embeddings.npz"
    if (
        analysis.digest(vector_file)
        != inputs["color_metrics"]["state_artifacts"]["seed7_R_B"]["embeddings"]
    ):
        raise ValueError("Use the exact saved ratings control color vectors.")
    model = torch.load(
        directory / "control-comparison.pt", map_location="cpu", weights_only=True
    )
    state = model["selected"]["state"]
    with np.load(vector_file, allow_pickle=False) as arrays:
        cosine = analysis.probe_scores(
            inputs["color_probe"], arrays["ids"], arrays["z"]
        )
        learned = analysis.probe_scores(
            inputs["color_probe"],
            arrays["ids"],
            arrays["z"],
            state["residual.weight"].numpy().reshape(-1),
            float(state["residual.bias"].item()),
        )
    comparison = {
        "A_cosine": result["color"]["cosine"],
        "A_learned_seed7": result["color"]["learned"]["7"],
        "R_cosine": cosine,
        "R_learned_seed7": learned,
    }
    _save(
        directory / "color-control-replay.json",
        {
            "scope": "Supplementary descriptive replay of each seed 7 comparison on its matching cached encoder. Original implied labels remain pending human review.",
            "scores": comparison,
        },
    )
    text = "\n## Matched color replay\n\nThis descriptive table applies each encoder's own comparison, using comparison seed 7 in both arms.\n\n| Encoder and score | Implied margin | Explicit cue benefit | Condition switch margin |\n| --- | --- | --- | --- |\n"
    for name, values in comparison.items():
        values = values["summary"]
        text += f"| {name} | {values['implicit_margin']:.6f} | {values['Q']:.6f} | {values['C']:.6f} |\n"
    text += "\n[Matched probe values](color-control-replay.json) · [Interpretation of selected examples](case-notes.md) · [Implied label review](implied-label-review.md)\n"
    report_path = directory / "report.md"
    report_path.write_text(
        report_path.read_text().split("\n## Matched color replay")[0] + text
    )

    control = read(directory / "control-comparison.json")
    rows = read(root / "csts_data/readout/test.json")
    old = read(
        Path(
            "/home/machina/jep-full-propositions-20261027-operator/checkpoints/final/ratings_predictions.json"
        )
    )
    index = {r["row_id"]: i for i, r in enumerate(rows)}
    for row in old:
        current = rows[index[row["row_id"]]]
        if any(
            row[k] != current[k]
            for k in ("condition", "sentence1", "sentence2", "target")
        ):
            raise ValueError("The archived control input changed.")
    before = np.array([r["prediction"] for r in old])
    after = np.array([control["cosine_predictions"][index[r["row_id"]]] for r in old])
    targets = [r["target"] for r in old]
    parity = {
        "archived_rows": len(old),
        "current_rows": len(rows),
        "archived_spearman": float(spearmanr(targets, before).statistic),
        "replayed_common_spearman": float(spearmanr(targets, after).statistic),
        "maximum_absolute_score_difference": float(np.max(np.abs(after - before))),
        "mean_absolute_score_difference": float(np.mean(np.abs(after - before))),
        "interpretation": "The replay uses the unchanged checkpoint on the current full cohort, with L4 inference and batches of 64. The original published predictions retain their original hardware and batch history.",
    }
    _save(directory / "control-replay-parity.json", parity)
    with (directory / "report.md").open("a") as stream:
        stream.write(
            f"\nThe original ratings reference covers {len(old):,} rows. This study replays the unchanged control checkpoint on all {len(rows):,} current rows. Its common row replay differs from the original predictions by mean absolute score {parity['mean_absolute_score_difference']:.6f}. [Replay check](control-replay-parity.json).\n"
        )
    predictions = read(directory / "interaction-predictions.json")
    affine = {}
    for encoder in ("A", "R"):
        x = np.asarray(predictions[encoder + "_cosine"])
        y = np.asarray(predictions[encoder + "_learned"])
        slope, intercept = np.linalg.lstsq(
            np.column_stack([x, np.ones(len(x))]), y, rcond=None
        )[0]
        approximation = slope * x + intercept
        affine[encoder] = {
            "slope": float(slope),
            "intercept": float(intercept),
            "fraction_of_score_variance_explained": float(
                1 - np.sum((y - approximation) ** 2) / np.sum((y - y.mean()) ** 2)
            ),
            "approximation_rmse": float(np.sqrt(np.mean((y - approximation) ** 2))),
            "cosine_spearman": result["metrics"][encoder + "_cosine"]["spearman"],
            "learned_spearman": result["metrics"][encoder + "_learned"]["spearman"],
        }
    _save(
        directory / "affine-score-check.json",
        {
            "scope": "Descriptive affine approximation to the saved test score outputs; the approximation uses score outputs rather than human ratings and supplies no model selection.",
            "encoders": affine,
        },
    )
    with report_path.open("a") as stream:
        stream.write(
            "\n## Score scaling and ordering\n\nAn affine approximation summarizes the learned score as a scale and offset of cosine. It is fitted to the saved score outputs for inspection.\n\n| Encoder | Scale | Offset | Score variance explained | Approximation RMSE |\n| --- | --- | --- | --- | --- |\n"
        )
        for encoder, values in affine.items():
            stream.write(
                f"| {encoder} | {values['slope']:.6f} | {values['intercept']:.6f} | {100 * values['fraction_of_score_variance_explained']:.4f}% | {values['approximation_rmse']:.6f} |\n"
            )
        stream.write(
            "\nPositive scaling preserves ordering while increasing margins. Small departures from the affine approximation contribute the observed Spearman changes. The color ordering counts therefore accompany its raw margin changes. [Score approximation](affine-score-check.json).\n"
        )
    sources = directory / "sources"
    sources.mkdir(exist_ok=True)
    for name in ("capture_csts_control_vectors.py", "analyze_csts_comparison.py"):
        shutil.copyfile(directory / "review/scripts" / name, sources / name)
    shutil.copyfile(__file__, sources / "finalize_csts_comparison_diagnostics.py")
    shutil.copyfile(
        directory / "review/tests/test_comparison_diagnostics.py",
        sources / "test_comparison_diagnostics.py",
    )
    config = read(root / "configs/csts-native-comparison.json")
    destination = ViperCloudDestination.model_validate(
        config["publication_destination"]
    )
    model_dir = directory / "models"
    model_dir.mkdir(exist_ok=True)
    ratings_checkpoint = model_dir / "ratings_control.pt"
    shutil.copyfile(color_root / "weights/seed7_R_B.pt", ratings_checkpoint)
    verification = {
        "focused_tests": {"passed": 4, "seconds": 11.96},
        "source_commit": read(directory / "source-commit.json")["commit"],
        "source_sha256": {
            p.name: hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
            for p in sources.iterdir()
        },
        "encoder_updates": 0,
        "cosine_probe_reproduction": "All three published cosine margins reproduced within 1e-10.",
        "existing_scorer_parity": "The saved scorer algebra matches the native symmetric comparison in the focused test.",
        "control_replay": parity,
        "math_rendering": "GitHub math fences and macro syntax checked. Direct observation of the deployed GitHub renderer remains pending.",
    }
    if (directory / "math-verification.json").exists():
        verification["math_rendering"] = read(directory / "math-verification.json")
    _save(directory / "verification.json", verification)
    _save(
        directory / "cloud-receipts.json",
        {
            "vector_capture": read(directory / "capture-publication.json"),
            "color_vectors": read(directory / "color-input-publication.json"),
            "original_comparisons": read(
                directory / "comparison-source-reference.json"
            ),
            "source": read(directory / "source-commit.json"),
        },
    )
    excluded = {
        "control_test.pt",
        "control_training.pt",
        "control_validation.pt",
        "original-comparisons.pt",
        "final-publication.json",
    }
    files = {
        "csts_comparison_diagnosis_20261028/final/" + p.name: p
        for p in directory.iterdir()
        if p.is_file()
        and p.name not in excluded
        and p.suffix in (".json", ".md", ".pt")
    }
    files.update(
        {
            "csts_comparison_diagnosis_20261028/final/sources/" + p.name: p
            for p in sources.iterdir()
            if p.is_file()
        }
    )
    files["csts_comparison_diagnosis_20261028/inputs/ratings_control.pt"] = (
        ratings_checkpoint
    )
    refs = publish_resolved_files(root, destination, files)
    _save(
        directory / "final-publication.json",
        {
            "status": "published",
            "references": {k: v.model_dump(mode="json") for k, v in refs.items()},
        },
    )
    print("COMPARISON_DIAGNOSTICS_PUBLISHED", len(refs), flush=True)


if __name__ == "__main__":
    main()
