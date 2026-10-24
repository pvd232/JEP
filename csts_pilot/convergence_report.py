"""Recompute Tranche 1 results and render its learning curves on the CPU."""

import argparse
import csv
import hashlib
import json
import math
import shutil
from pathlib import Path
from typing import Any

from csts_pilot.convergence_analysis import metrics, paired_intervals


def read_json(path: Path) -> Any:
    """Read the collected, checksum-verified small artifacts."""
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    """Keep machine-readable report artifacts free of NaN and infinity."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def render_curves(traces: dict[str, Any], destination: Path) -> None:
    """Plot common metrics against epochs, optimizer updates and measured time."""
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    figure, axes = plt.subplots(3, 3, figsize=(14, 10), constrained_layout=True)
    for arm, trace in traces.items():
        epochs = trace["epochs"]
        cumulative_seconds, elapsed = [], 0.0
        for row in epochs:
            elapsed += row["fit_seconds"] + row["validation_seconds"]
            cumulative_seconds.append(elapsed / 60)
        coordinates = (
            [r["epoch"] for r in epochs],
            [r["step"] for r in epochs],
            cumulative_seconds,
        )
        series = (
            [r["training_mse_0_1"] for r in epochs],
            [r["validation"]["mse_0_1"] for r in epochs],
            [r["validation"]["spearman"] for r in epochs],
        )
        for column, x in enumerate(coordinates):
            for row, y in enumerate(series):
                axes[row, column].plot(x, y, label=arm.upper(), linewidth=1.8)
                axes[row, column].grid(alpha=0.2)
    for row, label in enumerate(
        (
            "Training MSE on rescaled ratings",
            "Validation MSE on rescaled ratings",
            "Validation Spearman",
        )
    ):
        axes[row, 0].set_ylabel(label)
    for column, label in enumerate(
        ("Epoch", "Optimizer updates", "Fit and validation minutes")
    ):
        axes[-1, column].set_xlabel(label)
    axes[0, 0].legend()
    restart = next((t["config"].get("start_epoch", 0) for t in traces.values()), 0)
    if restart:
        for axis in axes[:, 0]:
            axis.axvline(restart, color="0.5", linestyle="--", linewidth=1)
    figure.suptitle("Tranche 1 · seed 7 · checkpoints selected by validation Spearman")
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def build_report(results_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Check saved predictions, calculate paired intervals and write the report."""
    summary = read_json(results_dir / "summary.json")
    selection_path = results_dir / "selection.json"
    if summary["status"] != "complete":
        raise ValueError("The report requires a completed native comparison.")
    if (
        hashlib.sha256(selection_path.read_bytes()).hexdigest()
        != summary["selection_sha256"]
    ):
        raise ValueError("The selection document differs from its pre-test identity.")
    selection = read_json(selection_path)
    expected = summary["settings"]["splits"]["test"]
    candidates, results = {}, {}
    for name, candidate in selection["candidates"].items():
        rows = read_json(results_dir / f"{name}_predictions.json")
        if (
            len(rows) != expected["rows"]
            or len({r["group_id"] for r in rows}) != expected["groups"]
        ):
            raise ValueError("The test cohort differs from the frozen comparison.")
        for row in rows:
            if row["target"] != (row["rating"] - 1) / 4:
                raise ValueError("A saved test target differs from its human rating.")
            affine = candidate["calibration"]
            if not math.isclose(
                row["calibrated_prediction"],
                affine["a"] * row["prediction"] + affine["c"],
                rel_tol=0,
                abs_tol=1e-14,
            ):
                raise ValueError(
                    "A test calibration differs from its frozen validation fit."
                )
        candidates[name] = rows
        raw, calibrated = metrics(rows), metrics(rows, "calibrated_prediction")
        if not math.isclose(
            raw["spearman"], calibrated["spearman"], rel_tol=0, abs_tol=1e-12
        ):
            raise ValueError("Positive affine calibration changed the test ranking.")
        results[name] = {
            "selected_epoch": candidate["epoch"],
            "checkpoint_sha256": candidate["sha256"],
            "raw": raw,
            "calibrated": calibrated,
        }
    settings = summary["settings"]
    intervals = paired_intervals(
        candidates, settings["bootstrap_draws"], settings["bootstrap_seed"]
    )
    traces = {
        arm: read_json(results_dir / f"{arm}_trace.json") for arm in ("mse", "pearson")
    }
    timing = {
        arm: {
            "updates": trace["actual_updates"],
            "fit_seconds": sum(r["fit_seconds"] for r in trace["epochs"]),
            "validation_seconds": sum(r["validation_seconds"] for r in trace["epochs"]),
            "elapsed_seconds": trace["elapsed_seconds"],
            "nonpadding_input_tokens": trace["nonpadding_input_tokens_per_epoch"]
            * len(trace["epochs"]),
            "peak_cuda_memory_bytes": trace["peak_cuda_memory_bytes"],
        }
        for arm, trace in traces.items()
    }
    report = {
        "source_commit": summary["source_commit"],
        "evaluation_source_commit": summary.get(
            "evaluation_source_commit", summary["source_commit"]
        ),
        "settings": settings,
        "provisional_loss_selected_on_validation": selection["provisional_loss"],
        "candidates": results,
        "paired_intervals": intervals,
        "compute": timing,
        "gpu_stage_seconds_including_native_publication": summary["gpu_stage_seconds"],
        "native_runs": summary["runs"],
        "failed_evaluations": summary.get("failed_evaluations", []),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = "csts_tranche1"
    write_json(output_dir / f"{prefix}_results.json", report)
    write_json(output_dir / f"{prefix}_intervals.json", intervals)
    shutil.copyfile(selection_path, output_dir / f"{prefix}_selection.json")
    for arm in traces:
        shutil.copyfile(
            results_dir / f"{arm}_trace.json", output_dir / f"{prefix}_{arm}_trace.json"
        )
    fields = [
        "arm",
        "epoch",
        "step",
        "training_objective",
        "training_mse_0_1",
        "validation_mse_0_1",
        "validation_spearman",
        "fit_seconds",
        "validation_seconds",
    ]
    with (output_dir / f"{prefix}_epochs.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for arm, trace in traces.items():
            for row in trace["epochs"]:
                writer.writerow(
                    {
                        "arm": arm,
                        **{key: row[key] for key in fields[1:] if key in row},
                        "validation_mse_0_1": row["validation"]["mse_0_1"],
                        "validation_spearman": row["validation"]["spearman"],
                    }
                )
    for name in candidates:
        shutil.copyfile(
            results_dir / f"{name}_predictions.json",
            output_dir / f"{prefix}_{name}_predictions.json",
        )
    render_curves(traces, output_dir / f"{prefix}_curves.png")
    epoch_counts = ", ".join(
        f"{arm.upper()}: {len(trace['epochs'])} epochs" for arm, trace in traces.items()
    )
    lines = [
        "# Tranche 1: loss and convergence",
        "",
        f"Source: `{summary['source_commit']}`. One shared seed "
        f"({settings['training']['seed']}); {epoch_counts}.",
        "",
        f"Evaluation source: `{report['evaluation_source_commit']}`. Frozen training, checkpoint choices and validation calibration retain their original identities.",
        "",
        "The hypotheses are that continued rating training improves conditional ranking, and that Pearson can improve ranking over MSE under shared settings. This screen supplies a stronger rating-only reference for later evidence-supervision experiments. See the [experiment plan](../plans/csts-tranche-1.md).",
        "",
        "Both arms used the same initialization, batch order, model and optimizer settings, with BF16 forward computation and float32 loss arithmetic. Checkpoints were selected by highest validation Spearman within each window. Test scoring used native VIPER EVAL stages with independent metric workers. Training and checkpoint selection finished before testing.",
        "",
        "Test ratings are the Tu 2024 human reannotations distributed by LivNLP; the fixed cohort excludes 214 invalid comparisons. Training labels separately use human/LLM aggregation. Label provenance is documented in the [existing audit](csts_sol61_max_label_audit.json).",
        "",
        f"The provisional loss selected using validation Spearman is **{selection['provisional_loss'].upper()}**.",
        "",
        "MSE uses targets $y=(r-1)/4$ and raw cosine predictions: $n^{-1}\\sum_i(s_i-y_i)^2$. MSE on the original 1–5 rating scale equals 16 times this value.",
        "",
        "| Candidate | Selected epoch | Test Spearman | Raw MSE | Calibrated MSE | Condition ordering |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, result in results.items():
        raw = result["raw"]
        lines.append(
            f"| {name} | {result['selected_epoch']} | {raw['spearman']:.6f} | {raw['mse_0_1']:.6f} | {result['calibrated']['mse_0_1']:.6f} | {raw['condition_ordering_accuracy']:.2%} |"
        )
    lines.extend(
        [
            "",
            "Condition ordering compares the same passage pair under different conditions with distinct human ratings, assigning half credit to tied predictions. Counts and score distributions are retained in the result JSON.",
            "",
            f"Paired differences below use {intervals['draws']:,} shared bootstrap samples of connected test-caption groups; intervals are conditional on seed {settings['training']['seed']}.",
            "",
        ]
    )
    for name, contrast in intervals["contrasts"].items():
        rho = contrast["spearman"]
        lo, hi = rho["ci95"]
        mse = contrast["mse_0_1"]
        mse_lo, mse_hi = mse["ci95"]
        lines.append(
            f"- {name}: Spearman difference {rho['difference']:+.6f}, 95% interval [{lo:+.6f}, {hi:+.6f}]; MSE difference {mse['difference']:+.6f}, 95% interval [{mse_lo:+.6f}, {mse_hi:+.6f}]."
        )
    primary = intervals["contrasts"]["pearson_full_minus_mse_full"]["spearman"]
    if primary["ci95"][0] > 0:
        interpretation = "The primary paired test interval favors Pearson for ranking on this test cohort."
    elif primary["ci95"][1] < 0:
        interpretation = "The primary paired test interval favors MSE for ranking on this test cohort."
    else:
        interpretation = "The primary paired test interval includes zero; this screen leaves the ranking comparison uncertain."
    lines.extend(
        [
            "",
            interpretation,
            "",
            "This compares the objectives under one shared optimizer setting. Each objective's best achievable performance remains open.",
            "",
            "The predeclared practical target for expanding a change into repeated-seed confirmation is 0.02 Spearman. The two within-objective duration contrasts are exploratory.",
            "",
        ]
    )
    for arm, trace in traces.items():
        epoch = trace["selected"]["full"]["epoch"]
        if trace.get("stop_reason") == "validation_patience":
            conclusion = (
                f"Validation patience of {trace['config']['patience']} epochs was "
                f"exhausted at epoch {len(trace['epochs'])}. "
                "This establishes a validation plateau under the declared rule; "
                "training-loss stationarity remains unresolved."
            )
        elif epoch == trace["config"]["max_epochs"]:
            conclusion = "The strongest validation checkpoint occurred at the epoch limit, leaving convergence beyond this budget unresolved."
        elif (
            epoch >= trace["config"]["max_epochs"] - 2
            and epoch > trace["config"]["prefix_epochs"]
        ):
            conclusion = "The strongest validation checkpoint occurred near the epoch limit. The longer budget improved validation ranking; convergence beyond this budget remains unresolved."
        elif epoch <= trace["config"]["prefix_epochs"]:
            conclusion = (
                "The strongest validation checkpoint occurred within the prefix window."
            )
        else:
            conclusion = "The longer budget produced a stronger validation checkpoint beyond the prefix window."
        cost = timing[arm]
        lines.append(
            f"- **{arm.upper()}**: {conclusion} Fitting took {cost['fit_seconds'] / 60:.2f} minutes and validation {cost['validation_seconds'] / 60:.2f} minutes, with {cost['updates']:,} updates and {cost['nonpadding_input_tokens']:,} nonpadding input tokens."
        )
    lines.extend(
        [
            "",
            "![Learning curves](csts_tranche1_curves.png)",
            "",
            "The prefix and full windows share the declared maximum-epoch "
            "learning-rate schedule. Their contrast measures continued training "
            "under that schedule. Validation patience can yield different actual "
            "update counts between arms; consult the compute records. Each "
            "objective has its own loss units; the curves show common MSE and "
            "Spearman metrics, while the epoch CSV preserves training objectives.",
            "",
            "Positive affine calibration was fitted using validation data, with five caption-group folds for its held-out error estimate. Raw cosine supplies the primary ranking result. Calibration coefficients were frozen before testing.",
            "",
            f"Native GPU-stage wall time, including publication and failed scoring attempts: {summary['gpu_stage_seconds'] / 60:.2f} minutes against the original {settings['gpu_budget_seconds'] / 60:.0f}-minute ceiling. Successful runs and exact sealed checkpoint references are preserved in the result JSON and native verification receipts.",
            "",
            (
                "The first prefix evaluation failed VIPER's stored-model artifact-name check after inference. The failed graph and metric receipts were preserved. A CPU BUILD stage copied each prefix checkpoint byte for byte to canonical `model`, with matching SHA-256 checks. Recovery executed scoring from the original frozen checkpoints; both training arms and the selection document were retained."
                if report["failed_evaluations"]
                else "Native evaluation completed using the frozen checkpoint identities."
            ),
            "",
            "This is a follow-up screen on an already examined test set. One seed limits claims about training variation. Confirmation requires prospectively chosen comparisons, repeated seeds, fresh source groups and independent Spanish JEP review.",
            "",
        ]
    )
    (output_dir / f"{prefix}_report.md").write_text("\n".join(lines))
    return report


def main() -> None:
    """Run CPU reporting after the native training and test stages finish."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("convergence_results"))
    parser.add_argument("--output", type=Path, default=Path("training_outputs"))
    args = parser.parse_args()
    report = build_report(args.results, args.output)
    print(
        json.dumps(
            {
                "status": "complete",
                "source_commit": report["source_commit"],
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
