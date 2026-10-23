"""Recover test scoring from completed training, preserving the original failure."""

import argparse
import fcntl
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

import yaml
from viper import api, execution
from viper.authoring import experiment, plan, replicate, variant
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)

from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import (
    artifact_path,
    canonical_checkpoint,
    check_inputs,
    evaluation_stage,
    verify_matched_arms,
)
from jep_pilot.loaders import load_json


def reconcile_failure(root: Path, summary: dict[str, Any]) -> None:
    """Keep a failed invocation failed, and record its exact sealed references."""
    invocation = summary.get("in_flight")
    if not invocation:
        return
    if summary["status"] != "failed" or not invocation["stage"].startswith("test_"):
        raise ValueError("Recovery requires a completed, failed evaluation invocation.")
    paths = list(
        (root / "experiments" / invocation["experiment_id"] / "runs").glob(
            "*/*/resolved.yaml"
        )
    )
    if len(paths) != 1:
        raise ValueError("Inspect ambiguous native evaluation state before recovery.")
    path = paths[0]
    resolved = yaml.safe_load(path.read_text())
    if resolved["status"] != "failed":
        raise ValueError("The interrupted invocation has unresolved native status.")
    summary.setdefault("failed_evaluations", []).append(
        {
            "name": invocation["stage"],
            "path": str(path),
            "resolved": resolved,
            "failure": summary.get("failure"),
            "gpu_seconds_already_charged": True,
        }
    )
    summary["in_flight"] = None


def evaluate(root: Path) -> None:
    """Run CPU checkpoint handoffs and EVAL stages, with zero training calls."""
    directory = root / "convergence_results"
    path = directory / "summary.json"
    summary = load_json(path)
    settings = load_json(root / "configs/csts-tranche-1.json")
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    if settings != summary["settings"]:
        raise ValueError("The original experiment settings must remain fixed.")
    if summary.get("status") == "complete":
        return
    check_inputs(root, settings)
    selection_path = directory / "selection.json"
    if file_sha256(selection_path) != summary["selection_sha256"]:
        raise ValueError("Recovery requires the original frozen selection bytes.")
    selection = load_json(selection_path)
    expected_names = {
        f"{arm}_{window}" for arm in ("mse", "pearson") for window in ("prefix", "full")
    }
    if (
        selection["status"] != "checkpoints_frozen"
        or set(selection["candidates"]) != expected_names
    ):
        raise ValueError("Recovery requires all four frozen checkpoint candidates.")
    records = {record["name"]: record for record in summary["runs"]}
    for name in ("initialize", "train_mse", "train_pearson", "publish_test"):
        record = records[name]
        if record["status"] != "succeeded":
            raise ValueError("Recovery requires both completed native training arms.")
        api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=Path(record["path"]),
                trusted_source_repositories=trusted,
            )
        )
    traces = {
        arm: load_json(
            artifact_path(records[f"train_{arm}"], "train", "trace", "trace.json")
        )
        for arm in ("mse", "pearson")
    }
    verify_matched_arms(traces)
    for candidate in selection["candidates"].values():
        original = records[f"train_{candidate['arm']}"]
        if candidate["run"] != original:
            raise ValueError("A frozen checkpoint points to a different training run.")
        checkpoint = artifact_path(
            original, "train", candidate["artifact_name"], "model.pt"
        )
        if file_sha256(checkpoint) != candidate["sha256"]:
            raise ValueError("Frozen checkpoint bytes changed before recovery.")
    backup = directory / "pre_evaluation_recovery_summary.json"
    if not backup.exists():
        shutil.copyfile(path, backup)
    reconcile_failure(root, summary)
    summary.update(
        evaluation_source_commit=source.commit,
        training_source_commit=summary["source_commit"],
        recovery="canonical model artifact handoff; frozen training and selection retained",
    )
    summary.pop("failure", None)
    write_json(path, summary)
    write_json(
        directory / "operator.json",
        {"pid": os.getpid(), "source_commit": source.commit, "mode": "evaluation_only"},
    )
    environment = observe_python_env()

    def execute(
        name: str, configured: Any, estimator: Any, gpu: bool
    ) -> dict[str, Any]:
        for record in summary["runs"]:
            if record["name"] == name and record["status"] == "succeeded":
                api.verify_run(
                    api.VerifyRunRequest(
                        root=root,
                        path=Path(record["path"]),
                        trusted_source_repositories=trusted,
                    )
                )
                return record
        if summary.get("in_flight"):
            raise RuntimeError(
                "Inspect the outstanding native invocation before continuing."
            )
        remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
        if gpu and remaining <= 0:
            raise TimeoutError("The original GPU-stage ceiling is exhausted.")
        trial = experiment(
            experiment_id=f"csts_tranche1_{source.commit[:7]}_{summary['attempt']}_{name}",
            variants=(variant(name, stages=(configured,), estimator=estimator),),
            replicates=(replicate(seed=settings["training"]["seed"]),),
        )
        summary.update(
            status="running",
            current_stage=name,
            in_flight={"stage": name, "experiment_id": trial.experiment_id},
        )
        write_json(path, summary)
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(model="NVIDIA L4", count=1)
            if gpu
            else CPUComputeSpec(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="pilot_requirements.txt",
            ),
            python_env=environment,
        )
        started = time.monotonic()
        try:
            result = execution.run(
                plan(experiment=trial, source=source, env=env),
                timeout_seconds=max(1, int(remaining)) if gpu else 1800,
                trusted_source_repositories=trusted,
            )
        finally:
            if gpu:
                summary["gpu_stage_seconds"] += time.monotonic() - started
            write_json(path, summary)
        record = {
            "name": name,
            "path": str(result.path),
            "status": result.status,
            "reference": result.reference.model_dump(mode="json"),
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native evaluation failed: {result.path}")
        return record

    try:
        scored = {entry["checkpoint_sha256"]: entry["run"] for entry in summary["test"]}
        summary["test"] = []
        for name, candidate in selection["candidates"].items():
            identity = candidate["sha256"]
            if identity not in scored:
                model, model_stage = canonical_checkpoint(candidate, execute)
                configured = evaluation_stage(
                    identity,
                    model,
                    model_stage,
                    records["publish_test"],
                    settings,
                    summary["selection_sha256"],
                )
                scored[identity] = execute(
                    f"test_{name}",
                    configured,
                    configured.outputs["predictions"],
                    gpu=True,
                )
            record = scored[identity]
            shutil.copyfile(
                artifact_path(record, "test", "predictions", "predictions.json"),
                directory / f"{name}_predictions.json",
            )
            summary["test"].append(
                {"candidate": name, "checkpoint_sha256": identity, "run": record}
            )
            write_json(path, summary)
        summary.update(status="complete", current_stage=None)
        write_json(path, summary)
    except BaseException as error:
        summary.update(
            status="failed",
            failure={"type": type(error).__name__, "message": str(error)},
        )
        write_json(path, summary)
        raise


def main() -> None:
    """Require an explicit execution flag and the existing runner's process lock."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"mode": "evaluation_only", "execution": "--execute"}))
        return
    root = resolve_root()
    with (root / "convergence_results/run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        evaluate(root)


if __name__ == "__main__":
    main()
