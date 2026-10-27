"""Extend sealed first-phase checkpoints to four epochs, then compare both rating models."""

import argparse
import fcntl
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, artifact_source, check_inputs
from csts_pilot.evidence_run import evidence_training_outputs
from csts_pilot.proposition_evidence_run import (
    phase_config,
    run_study,
    validate_settings,
)
from csts_pilot.qwen_evidence import fit_qwen_evidence
from jep_pilot.loaders import load_json

ARMS = ("ratings", "evidence")


def run_extension(root: Path, settings: dict[str, Any], name: str) -> None:
    """Reuse the first two epochs, add two matched epochs, then run fresh full-data ratings."""
    parent_root = Path(settings["continuation_parent_root"])
    parent_dir = (
        parent_root / "qwen_evidence_results" / settings["continuation_parent_name"]
    )
    parent = load_json(parent_dir / "summary.json")
    if parent["status"] != "complete":
        raise ValueError("Inspect the parent study before continuing its sealed runs.")
    validate_settings(settings)
    if (
        settings["phases"]["pretrain"]["max_epochs"] != 4
        or parent["settings"]["phases"]["pretrain"]["max_epochs"] != 2
    ):
        raise ValueError("This follow-up extends two saved epochs to four.")
    if settings["training"] != {
        **parent["settings"]["training"],
        "train_until_patience": True,
    }:
        raise ValueError("The follow-up must preserve the matched optimizer settings.")
    for key in ("splits", "answers", "provenance", "audit_gate", "encoder", "head"):
        if parent["settings"][key] != settings[key]:
            raise ValueError(f"The follow-up changed frozen inputs: {key}.")
    check_inputs(root, settings)
    source = read_source(root)
    trusted = frozenset(
        {str(source.repository), str(read_source(parent_root).repository)}
    )
    directory = root / "qwen_evidence_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "summary.json"
    if path.exists():
        summary = load_json(path)
        if (
            summary["source_commit"] != source.commit
            or summary["settings"] != settings
            or summary.get("in_flight")
        ):
            raise ValueError(
                "Inspect the existing attempt before resuming an uncertain stage."
            )
        if summary["status"] == "complete":
            return
    else:
        summary = {
            "source_commit": source.commit,
            "settings": settings,
            "status": "running",
            "attempt": uuid.uuid4().hex[:8],
            "runs": [
                r for r in parent["runs"] if r["name"] in {"prepare", "publish_test"}
            ],
            "gpu_stage_seconds": 0.0,
            "live_scores": {},
            "preparation": parent["preparation"],
            "continuation": {
                "parent_summary_sha256": file_sha256(parent_dir / "summary.json"),
                "parent_source_commit": parent["source_commit"],
                "test_scores_used_for_training": False,
            },
        }
        write_json(path, summary)
    environment = observe_python_env()
    metrics = tuple(
        measure(m) for m in (training_objective, validation_mse, validation_spearman)
    )
    parents = {r["name"]: r for r in parent["runs"]}
    for arm in ARMS:
        stage_name = f"{arm}_pretrain"
        if any(r["name"] == stage_name for r in summary["runs"]):
            continue
        record = parents[stage_name]
        api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=Path(record["path"]),
                trusted_source_repositories=trusted,
            )
        )
        trace = load_json(artifact_path(record, "train", "trace", "trace.json"))
        if (
            trace["completed_epoch"] != 2
            or trace["stop_reason"] != "fixed_update_budget"
        ):
            raise ValueError(
                "The phase-one parent must contain exactly two completed epochs."
            )
        prepared = parents["prepare"]
        prepared_path = artifact_path(prepared, "prepare", "prepared", "prepared.json")
        parent_model = artifact_path(record, "train", "last_model", "model.pt")
        cfg = phase_config(
            settings, arm, "pretrain", prepared_path, parent_model
        ).model_copy(update={"start_epoch": 2})
        bindings = {
            "parent_model": "last_model",
            "parent_resume": "resume_state",
            "parent_trace": "trace",
        }
        configured = stage(
            fit_qwen_evidence,
            stage_id="train",
            config=cfg,
            inputs=tuple(
                input(k, path=settings["splits"][k]["path"], data_role="training")
                for k in ("training", "validation")
            )
            + tuple(
                input(k, source=artifact_source(record, "train", v))
                for k, v in bindings.items()
            )
            + (
                input(
                    "prepared", source=artifact_source(prepared, "prepare", "prepared")
                ),
            )
            + (
                (input("head", path=settings["head"]["path"], data_role="training"),)
                if arm == "evidence"
                else ()
            ),
            outputs=evidence_training_outputs(),
            metrics=metrics,
            objective=maximize(metrics[-1]),
            reuse="never",
        )
        trial = experiment(
            experiment_id=f"csts_finish_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
            variants=(
                variant(
                    stage_name,
                    stages=(configured,),
                    estimator=configured.outputs["model"],
                ),
            ),
            replicates=(replicate(seed=cfg.seed),),
        )
        summary.update(
            current_stage=stage_name,
            in_flight={"name": stage_name, "experiment_id": trial.experiment_id},
        )
        write_json(path, summary)
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
            ),
            python_env=environment,
        )
        started = time.monotonic()
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=None,
            trusted_source_repositories=trusted,
        )
        continued = {
            "name": stage_name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "local_run_seconds": time.monotonic() - started,
        }
        summary["runs"].append(continued)
        summary["in_flight"] = None
        summary["gpu_stage_seconds"] += continued["local_run_seconds"]
        write_json(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(
                f"Native continuation failed for {arm}; preserve its artifacts."
            )
        completed = artifact_path(continued, "train", "trace", "trace.json")
        if (
            load_json(completed)["completed_epoch"] != 4
            or load_json(completed)["stop_reason"] != "fixed_update_budget"
        ):
            raise ValueError("The matched first phase must finish all four epochs.")
        shutil.copyfile(completed, directory / f"{arm}_pretrain_trace.json")
    write_json(path, summary)
    run_study(root, settings, name, resume=True)


def main() -> None:
    """Require explicit execution and retain a single owner of native continuation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = resolve_root()
    settings = load_json(root / args.settings)
    if args.execute:
        (root / "qwen_evidence_results").mkdir(exist_ok=True)
        with (root / "qwen_evidence_results/run.lock").open("a+") as owner:
            fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
            run_extension(root, settings, args.name)


if __name__ == "__main__":
    main()
