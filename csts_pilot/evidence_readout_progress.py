"""Append aggregate experiment progress to a shared Markdown report."""

import fcntl
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_path: Path | None = None


def configure(path: str | None) -> None:
    """Bind this worker to its controller's report."""
    global _path
    _path = Path(path) if path else None


def initialize(path: Path, source: str, gpu: str) -> None:
    """Create the report before the first native stage starts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(
            "# JEP evidence selection and sentence comparison\n\n"
            f"Source: `{source}`\n\nHardware: {gpu}\n\n"
            "Seeds: 7, 8, 9. Training: 6,051 comparisons. "
            "Validation: 1,576. Test: 2,431.\n\n"
            "A: saved cosine score. B: token weighting trained with ratings. "
            "C: token weighting trained with ratings and evidence. "
            "D: fitted comparison of B vectors. E: fitted comparison of C vectors.\n\n"
            "## Live progress\n\n"
            "| UTC | Event | Seed | Step | Metrics or progress |\n"
            "| --- | --- | --- | --- | --- |\n"
        )


def _number(value: Any) -> str:
    return f"{value:.6f}" if isinstance(value, (int, float)) else "pending"


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def append(event: str, **values: Any) -> None:
    """Write completed measurements using a process shared append lock."""
    if _path is None:
        return
    aliases = {"ratings": "B", "evidence": "C"}
    if event == "comparison_epoch":
        aliases = {"ratings": "D", "evidence": "E"}
    details = []
    for arm, metrics in values.get("validation", {}).items():
        details.append(
            f"{aliases.get(arm, arm)} validation rho {_number(metrics.get('spearman'))}, "
            f"MSE {_number(metrics.get('mse_0_1'))}"
        )
    for key in ("name", "split", "checkpoint", "status", "error_type"):
        if key in values:
            details.append(f"{key}: {values[key]}")
    completed = values.get("completed", values.get("done"))
    if completed is not None:
        details.append(f"{completed}/{values.get('total', '?')}")
    if "report" in values:
        details.append(f"report: {values['report']}")
    if event == "writing_retention_scores":
        report = values["results"]
        for name in ("writing", "after_ratings"):
            details.append(
                f"{name} answer CE {_number(report[name]['mean_answer_ce'])}, "
                f"exact agreement {_number(report[name]['whitespace_normalized_exact_match'])}"
            )
        details.append(
            "paired CE change " + _number(report["paired_mean_ce_after_minus_before"])
        )
    row = [
        datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        event.replace("_", " "),
        values.get("seed", ""),
        values.get("epoch", ""),
        "; ".join(details),
    ]
    text = "| " + " | ".join(_cell(v) for v in row) + " |\n"
    if event == "readout_final_scores":
        text += "\n## Test results\n\n| Seed | Model | Spearman | MSE |\n"
        text += "| --- | --- | --- | --- |\n"
        for seed, result in values["results"].items():
            models = result if seed in {"7", "8", "9"} else {seed: result}
            for name, metrics in models.items():
                label = {
                    "ratings": "B",
                    "evidence": "C",
                    "ratings_comparison": "D",
                    "evidence_comparison": "E",
                    "A_parent": "A",
                    "R_ratings_parent": "Ratings reference",
                }.get(name, name)
                text += (
                    f"| {seed if seed in {'7', '8', '9'} else 'reference'} | {label} | "
                    f"{_number(metrics.get('spearman'))} | {_number(metrics.get('mse_0_1'))} |\n"
                )
        contrast = values["primary_C_minus_B"]
        interval = contrast["group_bootstrap_95"]
        text += (
            f"\nMean C−B Spearman: {_number(contrast['mean'])}. "
            f"95% interval: [{_number(interval['low'])}, {_number(interval['high'])}].\n\n"
        )
        text += "| Comparison | Mean Spearman change | Mean MSE change | Spearman 95% interval |\n"
        text += "| --- | --- | --- | --- |\n"
        for name, result in values.get("contrasts", {}).items():
            bounds = result["group_bootstrap_95"]
            text += (
                f"| {_cell(name)} | {_number(result['mean'])} | "
                f"{_number(result['mse_delta_mean'])} | "
                f"[{_number(bounds['low'])}, {_number(bounds['high'])}] |\n"
            )
    if event == "stage_finished" and values.get("name") == "evaluate":
        text = f"\nEvaluation status: {_cell(values['status'])}.\n"
    with _path.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.write(text)
        stream.flush()
