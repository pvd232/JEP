"""Read native VIPER metrics and traces while the C-STS study runs."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def resources(root: Path) -> dict[str, Any]:
    """Show free storage and current GPU use alongside training progress."""
    disk = shutil.disk_usage(root)
    result: dict[str, Any] = {
        "disk_free_gib": disk.free / 2**30,
        "disk_total_gib": disk.total / 2**30,
    }
    if shutil.which("nvidia-smi"):
        try:
            output = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
                timeout=3,
                stderr=subprocess.DEVNULL,
            )
            result["gpus"] = [
                dict(
                    zip(
                        ("utilization_percent", "memory_used_mib", "memory_total_mib"),
                        (float(value) for value in line.split(",")),
                        strict=True,
                    )
                )
                for line in output.strip().splitlines()
            ]
        except (OSError, ValueError, subprocess.SubprocessError):
            result["gpus"] = []
    return result


def read_json(path: Path) -> Any:
    """Allow a retry when an observer catches a file being written."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def measurements(path: Path) -> dict[int, float]:
    """Read completed JSONL records and tolerate a final incomplete append."""
    if not path.exists():
        return {}
    result = {}
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                break
            raise
        epoch = row.get("epoch") or row.get("step")
        if epoch is not None:
            result[int(epoch)] = float(row["value"])
    return result


def collect(root: Path) -> dict[str, Any]:
    """Collect the launched source version without opening evaluation inputs."""
    launcher = read_json(root / "csts_results/launcher.json")
    if launcher is None:
        raise FileNotFoundError("The study launcher record is missing.")
    source = launcher["source_commit"]
    summary = read_json(root / "csts_results/summary.json") or {}
    if summary.get("source_commit") != source:
        summary = {}
    verified = {row["name"]: row for row in summary.get("runs", [])}
    manifest = (
        summary.get("data_manifest")
        or read_json(root / "csts_data/manifest.json")
        or {}
    )
    controller_alive = False
    if launcher.get("pid", 0) > 0:
        try:
            os.kill(launcher["pid"], 0)
            controller_alive = True
        except (ProcessLookupError, PermissionError):
            pass
    trials = []
    pattern = f"experiments/csts_natural_20261021_{source[:7]}_*/runs/*/*"
    for folder in sorted(root.glob(pattern), key=lambda item: item.name):
        name = folder.parent.name
        if name.startswith("evaluate_") or name == "publish_evaluation":
            continue
        trace = read_json(folder / "artifacts/train/trace/trace.json")
        if trace:
            epochs = trace["epochs"]
            best = next(row for row in epochs if row["epoch"] == trace["best_epoch"])
            metrics = best["development"]
            config = trace["config"]
        else:
            logs = folder / "attempts/1/measurements"
            train = measurements(logs / "train.training_mse.jsonl")
            dev = measurements(logs / "train.development_mse.jsonl")
            epochs = [
                {
                    "epoch": epoch,
                    "training_mse": train.get(epoch),
                    "development": {"mse_0_1": dev[epoch]},
                }
                for epoch in sorted(dev)
            ]
            best = (
                min(epochs, key=lambda row: row["development"]["mse_0_1"])
                if epochs
                else None
            )
            metrics = best["development"] if best else {}
            config = {}
        status = (
            "verified"
            if name in verified
            else "trained"
            if trace
            else "training"
            if controller_alive
            else "stopped"
        )
        trials.append(
            {
                "name": name,
                "run_id": folder.name,
                "status": status,
                "epochs": epochs,
                "best_epoch": best["epoch"] if best else None,
                "best_development": metrics,
                "config": config,
                "seconds": trace.get("elapsed_seconds") if trace else None,
                "peak_cuda_memory_bytes": trace.get("peak_cuda_memory_bytes")
                if trace
                else None,
                "verified_measurements": verified.get(name, {}).get(
                    "verified_measurements"
                ),
                "native_record": str(folder / "resolved.yaml"),
            }
        )
    training = read_json(root / "csts_data/train.json")
    development = read_json(root / "csts_data/dev.json")
    reference = None
    if training and development:
        mean = sum(row["target"] for row in training) / len(training)
        reference = {
            "prediction": mean,
            "development_mse": sum((row["target"] - mean) ** 2 for row in development)
            / len(development),
        }
    failure = None
    log_path = root / "csts_results/launcher.log"
    if (
        not controller_alive
        and summary.get("status") != "complete"
        and log_path.exists()
    ):
        errors = [
            line
            for line in log_path.read_text().splitlines()
            if line.startswith(
                ("OSError:", "RuntimeError:", "ValueError:", "viper.execution.errors.")
            )
        ]
        failure = errors[-2:] or None
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": source,
        "controller_alive": controller_alive,
        "resources": resources(root),
        "failure": failure,
        "status": summary.get("status", "starting")
        if controller_alive or summary.get("status") == "complete"
        else "stopped",
        "data_manifest": manifest,
        "trials": trials,
        "selected": summary.get("selected", {}),
        "evaluation": summary.get("evaluation", []),
        "mean_predictor": summary.get("mean_predictor"),
        "development_reference": reference,
        "launcher_log": str(root / "csts_results/launcher.log"),
    }


def number(value: Any, digits: int = 4) -> str:
    """Format unfinished metrics explicitly."""
    return f"{value:.{digits}f}" if value is not None else "pending"


def render(progress: dict[str, Any]) -> str:
    """Print a compact table suitable for a live terminal."""
    lines = [
        f"C-STS | {progress['status']} | source {progress['source_commit'][:7]}",
        f"Observed {progress['observed_at_utc']}",
        f"{'Trial':40} {'Status':9} {'Epoch':>5} {'Dev MSE':>9} {'Spearman':>9} {'Q order':>9}",
    ]
    resource = progress.get("resources", {})
    if resource:
        lines.insert(2, f"Storage: {resource['disk_free_gib']:.1f} GiB free")
        for gpu in resource.get("gpus", []):
            lines.insert(
                3,
                f"GPU: {gpu['utilization_percent']:.0f}% | memory "
                f"{gpu['memory_used_mib']:.0f}/{gpu['memory_total_mib']:.0f} MiB",
            )
    for trial in progress["trials"]:
        metrics = trial["best_development"]
        accuracy = metrics.get("condition_changes", {}).get("accuracy_ties_half")
        lines.append(
            f"{trial['name']:40} {trial['status']:9} {len(trial['epochs']):>5} "
            f"{number(metrics.get('mse_0_1')):>9} {number(metrics.get('spearman')):>9} "
            f"{number(100 * accuracy, 1) + '%' if accuracy is not None else 'pending':>9}"
        )
    if progress["development_reference"]:
        lines.append(
            "Mean-rating development MSE: "
            + number(progress["development_reference"]["development_mse"])
        )
    lines.append(
        "Dev MSE, Spearman and question ordering refer to each trial's best development checkpoint."
    )
    lines.append(
        "Training and development MSE update each epoch. Completed traces add ranking diagnostics."
    )
    if progress["evaluation"]:
        lines.append(
            "Evaluation: " + json.dumps(progress["evaluation"], separators=(",", ":"))
        )
    if progress.get("failure"):
        lines.extend(progress["failure"])
    return "\n".join(lines)


def main() -> None:
    """Watch the experiment from a separate process using standard-library reads."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=float, default=15)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.interval < 1:
        parser.error("The refresh interval must be at least one second.")
    while True:
        progress = collect(args.root)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            temporary = args.output.with_suffix(".tmp")
            temporary.write_text(json.dumps(progress, indent=2, allow_nan=False) + "\n")
            temporary.replace(args.output)
        if args.watch and sys.stdout.isatty():
            print("\033[2J\033[H", end="")
        print(
            json.dumps(progress, indent=2) if args.json else render(progress),
            flush=True,
        )
        if not args.watch or progress["status"] in {"complete", "stopped"}:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
