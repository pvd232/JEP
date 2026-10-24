"""Recompute Tranche 2 metrics and paired uncertainty from verified small files."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from csts_pilot.convergence_analysis import metrics, paired_intervals


def read_json(path: Path) -> Any:
    """Read a report input through the CPU analysis environment."""
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    """Write finite machine-readable analysis results."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def verify_files(directory: Path) -> dict[str, Any]:
    """Check all collected bytes and the native verification's summary identity."""
    manifest = read_json(directory / "files.json")
    for name, expected in manifest.items():
        if Path(name).name != name:
            raise ValueError("The report manifest requires flat file names.")
        raw = (directory / name).read_bytes()
        if (
            len(raw) != expected["bytes"]
            or hashlib.sha256(raw).hexdigest() != expected["sha256"]
        ):
            raise ValueError(f"Collected file bytes differ: {name}.")
    receipt = read_json(directory / "native_verification.json")
    if (
        receipt["status"] != "verified"
        or hashlib.sha256((directory / "summary.json").read_bytes()).hexdigest()
        != receipt["summary_sha256"]
    ):
        raise ValueError("The native receipt refers to a different summary.")
    summary = read_json(directory / "summary.json")
    required = {"summary.json", "selection.json", "native_verification.json"}
    for record in summary["test"]:
        name = f"{record['candidate']}_predictions.json"
        required.add(name)
        if receipt["exports"].get(name, {}).get("sha256") != manifest.get(name, {}).get(
            "sha256"
        ):
            raise ValueError(
                "A prediction export lacks its verified native producer identity."
            )
    if not required <= manifest.keys():
        raise ValueError("The collection manifest omits a required report input.")
    if (
        hashlib.sha256((directory / "selection.json").read_bytes()).hexdigest()
        != summary["selection_sha256"]
    ):
        raise ValueError("The report selection differs from the frozen computation.")
    return receipt


def same_comparisons(candidates: dict[str, list[dict[str, Any]]]) -> None:
    """Require the same ordered rows, labels, conditions, pairs and source groups."""
    reference = None
    for rows in candidates.values():
        identity = [
            (
                row["row_id"],
                row["target"],
                row["rating"],
                row["group_id"],
                row["pair_id"],
                row["condition"],
                row["sentence1"],
                row["sentence2"],
            )
            for row in rows
        ]
        if len({row[0] for row in identity}) != len(identity):
            raise ValueError("Report comparisons require unique row IDs.")
        if reference is None:
            reference = identity
        elif reference != identity:
            raise ValueError(
                "Report candidate IDs, labels or source comparisons differ."
            )


def build_report(
    root: Path, directories: list[Path], output: Path, draws: int | None = None
) -> dict[str, Any]:
    """Analyze frozen candidates and references while retaining undefined mean rank."""
    candidates, sources, selections, summaries, training = {}, {}, {}, [], {}
    for directory in directories:
        verify_files(directory)
        summary = read_json(directory / "summary.json")
        selection = read_json(directory / "selection.json")
        if (
            summary["status"] != "complete"
            or selection["status"] != "checkpoints_frozen"
        ):
            raise ValueError("Report only completed, frozen phase outputs.")
        summaries.append(summary)
        selections[summary["phase"]] = selection["provisional_winner"]
        for kind in selection["candidates"]:
            if kind in candidates:
                raise ValueError("Choose one completed phase per scorer.")
            candidates[kind] = read_json(directory / f"{kind}_predictions.json")
            sources[kind] = {
                "orchestration_commit": summary["source_commit"],
                "model_run": selection["candidates"][kind]["run"]["reference"],
            }
            if kind in {"projection", "lora"}:
                trace = read_json(directory / f"{kind}_trace.json")
                phase_epochs = trace["epochs"][trace["config"]["start_epoch"] :]
                training[kind] = {
                    "completed_epoch": len(trace["epochs"]),
                    "selected_epoch": trace["selected"]["epoch"],
                    "stop_reason": trace["stop_reason"],
                    "total_updates": trace["actual_updates"],
                    "new_fit_seconds": sum(
                        epoch["fit_seconds"] for epoch in phase_epochs
                    ),
                    "new_validation_seconds": sum(
                        epoch["validation_seconds"] for epoch in phase_epochs
                    ),
                }
    seed = summaries[0]["settings"]["seed"]
    if draws is None:
        draws = summaries[0]["settings"]["bootstrap_draws"]
    if any(summary["settings"]["seed"] != seed for summary in summaries):
        raise ValueError("Phase training seeds differ.")
    references = summaries[0]["settings"]["references"]
    if any(summary["settings"]["references"] != references for summary in summaries):
        raise ValueError("Phase reference identities differ.")
    for kind, reference in references.items():
        path = root / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError("A saved reference prediction identity differs.")
        candidates[kind] = read_json(path)
        sources[kind] = {
            "path": str(path.relative_to(root)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    same_comparisons(candidates)
    if len(candidates["flan"]) != 2620:
        raise ValueError("The report requires all 2,620 frozen test comparisons.")
    ranked = {kind: rows for kind, rows in candidates.items() if kind != "mean"}
    contrasts = {}
    for kind in ("projection", "ridge", "lora"):
        if kind in candidates:
            for reference in ("cosine", "flan"):
                if reference in candidates:
                    contrasts[f"{kind}_minus_{reference}"] = (kind, reference)
    if "lora" in candidates and "projection" in candidates:
        contrasts["lora_minus_projection"] = ("lora", "projection")
    scores = {kind: metrics(rows) for kind, rows in ranked.items()}
    if "mean" in candidates:
        rows = candidates["mean"]
        error = sum((row["prediction"] - row["target"]) ** 2 for row in rows) / len(
            rows
        )
        scores["mean"] = {
            "n": len(rows),
            "mse_0_1": error,
            "mse_1_5": 16 * error,
            "spearman": None,
        }
    intervals = paired_intervals(
        ranked,
        draws=draws,
        seed=summaries[0]["settings"]["bootstrap_seed"],
        contrasts=contrasts,
    )
    result = {
        "scores": scores,
        "paired_intervals": intervals,
        "validation_choices": selections,
        "training": training,
        "sources": sources,
        "timing": [
            {
                "phase": summary["phase"],
                "gpu_stage_seconds": summary["gpu_stage_seconds"],
                "stages": [
                    {
                        "name": record["name"],
                        "local_run_seconds": record["local_run_seconds"],
                        "reused_from_parent": record.get("reused_from_parent", False),
                    }
                    for record in summary["runs"]
                ],
            }
            for summary in summaries
        ],
        "scope": "One-seed follow-up on an already examined benchmark; GPT is a direct pair-judgment reference.",
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "csts_tranche2_results.json", result)
    lines = [
        "# Tranche 2: encoder baseline hierarchy",
        "",
        "All candidates were selected using validation before their test scoring. Native verification and collection manifests were checked before this independent analysis.",
        "",
        "| System | Test Spearman | Raw MSE |",
        "| --- | ---: | ---: |",
    ]
    for kind, score in scores.items():
        rank = (
            f"{score['spearman']:.6f}"
            if score["spearman"] is not None
            else "undefined (constant)"
        )
        lines.append(f"| {kind} | {rank} | {score['mse_0_1']:.6f} |")
    lines.extend(
        [
            "",
            "Targets are rescaled through `(rating - 1) / 4`. Raw cosine and ridge scores remain unclipped. The GPT reference judges both passages jointly; the embedding systems encode each passage independently under its condition.",
            "",
            "## Training and stopping",
            "",
        ]
    )
    for kind, trained in training.items():
        lines.append(
            f"{kind}: completed epoch {trained['completed_epoch']}, selected epoch {trained['selected_epoch']}; stop reason `{trained['stop_reason']}`. This phase used {trained['new_fit_seconds']:.2f} fitting seconds and {trained['new_validation_seconds']:.2f} validation seconds."
        )
        lines.append("")
    lines.extend(["## Paired uncertainty", ""])
    for name, contrast in intervals["contrasts"].items():
        point, interval = (
            contrast["spearman"]["difference"],
            contrast["spearman"]["ci95"],
        )
        lines.append(
            f"- {name}: {point:+.6f}; paired 95% interval [{interval[0]:+.6f}, {interval[1]:+.6f}]."
        )
    lines.extend(
        [
            "",
            f"The {draws:,} paired draws resample the same source components across candidates. Intervals describe test-sample uncertainty conditional on seed {seed}. Final confirmation requires prospective comparisons and independently reviewed Spanish JEP groups.",
            "",
            "Native GPU-stage wall times include the local native invocation. Promotion timing remains a separate CPU worker interval and includes upload plus native cloud verification. Persistent model and optimizer bytes remain available through the sealed references in each phase's native verification file.",
            "",
            "Validation patience supplies an empirical stopping observation. A stationary training minimum remains unresolved.",
            "",
        ]
    )
    (output / "csts_tranche2_report.md").write_text("\n".join(lines))
    return result


def main() -> None:
    """Analyze one or both collected phases in the existing CPU report environment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = build_report(args.root, args.directories, args.root / "training_outputs")
    print({"status": "reported", "candidates": list(result["scores"])})


if __name__ == "__main__":
    main()
