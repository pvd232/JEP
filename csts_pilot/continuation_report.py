"""Report the separately budgeted continuation against its frozen original winners."""

import argparse
import hashlib
import math
import shutil
from pathlib import Path
from typing import Any

from csts_pilot.convergence_analysis import metrics, paired_intervals
from csts_pilot.convergence_report import read_json, render_curves, write_json


def build_report(root: Path, results: Path, output: Path) -> dict[str, Any]:
    """Recompute paired comparisons after checking frozen selection and calibration."""
    summary = read_json(results / "summary.json")
    if summary["status"] != "complete":
        raise ValueError("The continuation is still incomplete.")
    if (
        hashlib.sha256((results / "selection.json").read_bytes()).hexdigest()
        != summary["selection_sha256"]
    ):
        raise ValueError("The continuation selection differs from its frozen identity.")
    settings = summary["settings"]
    selection = read_json(results / "selection.json")
    expected = settings["splits"]["test"]
    candidates, scores, traces = {}, {}, {}
    for arm in ("mse", "pearson"):
        traces[arm] = read_json(results / f"{arm}_trace.json")
        for phase in ("original", "continued"):
            if phase == "original":
                parent = settings["parents"][arm]
                rows = read_json(root / parent["baseline_predictions"])
                checkpoint = parent["baseline_checkpoint"]
            else:
                rows = read_json(results / f"{arm}_predictions.json")
                checkpoint = selection["candidates"][f"{arm}_full"]
            if (
                len(rows) != expected["rows"]
                or len({r["group_id"] for r in rows}) != expected["groups"]
            ):
                raise ValueError(
                    "The continuation test cohort differs from its fixed identity."
                )
            for row in rows:
                if row["target"] != (row["rating"] - 1) / 4:
                    raise ValueError(
                        "The continuation test labels differ from their human ratings."
                    )
                affine = checkpoint["calibration"]
                if not math.isclose(
                    row["calibrated_prediction"],
                    affine["a"] * row["prediction"] + affine["c"],
                    abs_tol=1e-14,
                    rel_tol=0,
                ):
                    raise ValueError(
                        "The continuation calibration differs from its validation fit."
                    )
            name = f"{arm}_{phase}"
            candidates[name] = rows
            scores[name] = {
                "epoch": checkpoint["epoch"],
                "sha256": checkpoint["sha256"],
                "raw": metrics(rows),
                "calibrated": metrics(rows, "calibrated_prediction"),
            }
    intervals = paired_intervals(
        candidates,
        settings["bootstrap_draws"],
        settings["bootstrap_seed"],
        contrasts={
            "mse_continued_minus_original": ("mse_continued", "mse_original"),
            "pearson_continued_minus_original": (
                "pearson_continued",
                "pearson_original",
            ),
            "pearson_continued_minus_mse_continued": (
                "pearson_continued",
                "mse_continued",
            ),
        },
    )
    report = {
        "source_commit": summary["source_commit"],
        "scores": scores,
        "paired_intervals": intervals,
        "selection_sha256": summary["selection_sha256"],
        "compute": {},
        "scope": "One-seed constant-rate continuation; original winners remain eligible; an already examined benchmark.",
    }
    lines = [
        "# Rating-training continuation",
        "",
        f"Source: `{summary['source_commit']}`. Resume the completed seed-7 MSE and Pearson runs after epoch 24. Encoder LR is 3e-6 and projection LR is 1e-4, held constant through this phase. Validation Spearman selects checkpoints and drives patience five, with a ceiling of 48 total epochs.",
        "",
        "| Arm and phase | Selected epoch | Test Spearman | Raw MSE | Calibrated MSE |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, score in scores.items():
        label = name.replace("mse_", "MSE, ").replace("pearson_", "Pearson, ")
        lines.append(
            f"| {label} | {score['epoch']} | {score['raw']['spearman']:.6f} | {score['raw']['mse_0_1']:.6f} | {score['calibrated']['mse_0_1']:.6f} |"
        )
    lines.extend(
        [
            "",
            "MSE uses targets rescaled through $y=(r-1)/4$ and raw cosine predictions. MSE on the original 1–5 rating scale is 16 times the reported value.",
            "",
            "This continuation asks whether the 24-epoch rating baseline still benefits from additional optimization. It introduces an explicit constant-rate restart, so its gains describe that continuation policy. Validation selects the ranking baseline; actual update counts differ between the arms under the same patience rule.",
            "",
            "The test ratings are Tu's 2024 human reannotations distributed by LivNLP; 214 invalid comparisons were excluded. Training and validation use the release's separate human/LLM aggregation. See the [label audit](csts_sol61_max_label_audit.json).",
            "",
            "The original epoch-23 MSE and epoch-22 Pearson winners remain incumbents throughout the continuation. AdamW moments, terminal weights and RNG state were restored from epoch 24. Both continued checkpoints and validation calibration were frozen before test access. Unchanged checkpoint bytes reuse their original completed evaluation.",
            "",
            "## Paired uncertainty",
            "",
        ]
    )
    for name, contrast in intervals["contrasts"].items():
        rho = contrast["spearman"]
        label = (
            name.replace(
                "mse_continued_minus_original", "MSE, continued minus original"
            )
            .replace(
                "pearson_continued_minus_original", "Pearson, continued minus original"
            )
            .replace(
                "pearson_continued_minus_mse_continued",
                "Continued Pearson minus continued MSE",
            )
        )
        lines.append(
            f"- {label}: Spearman difference {rho['difference']:+.6f}; paired 95% interval [{rho['ci95'][0]:+.6f}, {rho['ci95'][1]:+.6f}]."
        )
    lines.extend(
        [
            "",
            "The 2,000 paired bootstrap draws resample the same 1,241 source components across candidates. Intervals are conditional on this training seed. This follow-up uses an already examined benchmark; confirmation requires a prospectively chosen comparison and independently reviewed Spanish JEP data.",
            "",
            "## Training and stopping",
            "",
        ]
    )
    for arm, trace in traces.items():
        start = trace["continuation"]["start_epoch"]
        epochs = trace["epochs"][start:]
        compute = {
            "completed_epoch": len(trace["epochs"]),
            "additional_epochs": len(epochs),
            "additional_updates": trace["actual_updates"]
            - trace["continuation"]["restored_step"],
            "fit_seconds": sum(e["fit_seconds"] for e in epochs),
            "validation_seconds": sum(e["validation_seconds"] for e in epochs),
            "stop_reason": trace["stop_reason"],
            "last_training_objective": epochs[-1]["training_objective"],
            "mean_preclip_gradient_norm_last_epoch": epochs[-1].get(
                "mean_preclip_gradient_norm"
            ),
        }
        report["compute"][arm] = compute
        lines.append(
            f"- {arm.upper()}: stopped at epoch {len(trace['epochs'])} after {len(epochs)} additional epochs and {compute['additional_updates']:,} updates; reason `{trace['stop_reason']}`. Fitting took {compute['fit_seconds'] / 60:.2f} minutes and validation {compute['validation_seconds'] / 60:.2f} minutes. Final training objective: {compute['last_training_objective']:.6f}."
        )
    lines.extend(
        [
            "",
            "Patience reports a validation plateau under the declared rule. Batch gradient norms are recorded before clipping as an optimization diagnostic; they use stochastic batches and changing weights. A stationary training minimum remains unproven.",
            "",
            "![Continuation curves](csts_continuation_curves.png)",
            "",
            "Training and evaluation use native VIPER stages. Local verification precedes downstream computation; cloud promotion runs in an independent CPU worker. Native cloud publication and shutdown receipts are separate closeout artifacts. The previous studies, completed reports and original stopped VM remain preserved.",
            "",
        ]
    )
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "csts_continuation_results.json", report)
    write_json(output / "csts_continuation_intervals.json", intervals)
    (output / "csts_continuation_report.md").write_text("\n".join(lines))
    for arm in traces:
        write_json(output / f"csts_continuation_{arm}_trace.json", traces[arm])
        shutil.copyfile(
            results / f"{arm}_predictions.json",
            output / f"csts_continuation_{arm}_predictions.json",
        )
    shutil.copyfile(
        results / "selection.json", output / "csts_continuation_selection.json"
    )
    render_curves(traces, output / "csts_continuation_curves.png")
    return report


def main() -> None:
    """Render the verified small continuation artifacts with a CPU interpreter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = build_report(root, args.results, root / "training_outputs")
    print({"scores": report["scores"], "compute": report["compute"]}, flush=True)


if __name__ == "__main__":
    main()
