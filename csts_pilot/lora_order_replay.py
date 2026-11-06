"""Replay the original standalone LoRA protocol with condition tokens after the passage."""

import argparse
import fcntl
import json
import re
from pathlib import Path
from typing import Any

from viper.repository import resolve_root

from csts_pilot.baseline_models import PROMPT
from csts_pilot.baseline_run import run_study, validate_settings
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path, check_inputs
from jep_pilot.loaders import load_json


def replay_settings(
    root: Path, protocol: dict[str, Any], gpu_model: str
) -> list[dict[str, Any]]:
    """Load exact historical settings and bind replay limits and the recorded runtime."""
    if PROMPT != protocol["prompt_after"]:
        raise ValueError("The encoder prompt differs from the declared condition-last replay.")
    phases = protocol["phases"]
    if [(phase["name"], phase["stop_after_epoch"]) for phase in phases] != [
        ("initial", 1),
        ("continuation", 7),
    ]:
        raise ValueError("Replay requires the original one-epoch start and seven-epoch ceiling.")
    configurations = []
    for phase in phases:
        path = root / phase["settings"]
        if file_sha256(path) != phase["settings_sha256"]:
            raise ValueError("The historical training configuration changed.")
        settings = load_json(path)
        settings["fits"]["lora"]["stop_after_epoch"] = phase["stop_after_epoch"]
        settings["gpu_model"] = gpu_model
        settings["environment_lockfile"] = protocol["environment_lockfile"]
        validate_settings(settings)
        configurations.append(settings)
    return configurations


def run_replay(
    root: Path,
    protocol: dict[str, Any],
    configurations: list[dict[str, Any]],
    name: str,
    resume: bool,
) -> None:
    """Reuse native training, continuation, frozen selection and evaluation for both phases."""
    directory = root / "baseline_results" / "lora" / name
    directory.mkdir(parents=True, exist_ok=True)
    identity_path = directory / "protocol.json"
    identity = {"protocol": protocol, "settings": configurations}
    if identity_path.exists():
        if not resume or load_json(identity_path) != identity:
            raise ValueError("Inspect the existing replay; resume requires the same protocol.")
    else:
        write_json(identity_path, identity)
    parent_path = None
    phases = []
    for phase, settings in zip(protocol["phases"], configurations, strict=True):
        phase_name = f"{name}_{phase['name']}"
        run_study(
            root,
            settings,
            phase="lora",
            name=phase_name,
            resume=resume,
            parent_path=parent_path,
            standalone_lora=True,
        )
        parent_path = root / "baseline_results" / "lora" / phase_name / "summary.json"
        summary = load_json(parent_path)
        training = next(record for record in summary["runs"] if record["name"] == "train_lora")
        trace = load_json(artifact_path(training, "train", "trace", "trace.json"))
        if trace["stop_reason"] not in {"replay_epoch_limit", "validation_patience"}:
            raise RuntimeError("The replay hit a resource limit; preserve its incomplete result.")
        phases.append(
            {
                "phase": phase["name"],
                "summary": str(parent_path),
                "summary_sha256": file_sha256(parent_path),
                "completed_epochs": len(trace["epochs"]),
                "actual_updates": trace["actual_updates"],
                "stop_reason": trace["stop_reason"],
                "selected": trace["selected"],
                "test": summary["live_scores"]["lora"],
            }
        )
        write_json(
            directory / "replay.json",
            {
                "status": "complete" if len(phases) == len(configurations) else "running",
                "protocol_sha256": file_sha256(identity_path),
                "phases": phases,
                "publication_status": "queued_separately",
            },
        )
    print(
        json.dumps(
            {
                "status": "complete",
                "replay": str(directory / "replay.json"),
                "scores": phases[-1]["test"],
                "publication_status": "queued_separately",
            }
        ),
        flush=True,
    )


def main() -> None:
    """Show the pinned replay by default, or execute it under the existing GPU lock."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--check-inputs", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--name", default="condition_last_20261106")
    parser.add_argument("--gpu-model", default="NVIDIA L4")
    parser.add_argument("--settings", default="configs/csts-lora-condition-order-replay.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.name):
        parser.error("Run names may contain letters, numbers, underscores and hyphens.")
    root = resolve_root()
    protocol = load_json(root / args.settings)
    configurations = replay_settings(root, protocol, args.gpu_model)
    if args.check_inputs:
        check_inputs(root, configurations[0])
        print(json.dumps({"status": "input_identities_verified"}))
    if not args.execute:
        print(json.dumps({"status": "review", "protocol": protocol, "settings": configurations}, indent=2))
        return
    (root / "baseline_results").mkdir(exist_ok=True)
    with (root / "baseline_results" / "run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_replay(root, protocol, configurations, args.name, args.resume)


if __name__ == "__main__":
    main()
