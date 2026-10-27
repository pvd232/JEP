"""Train a concurrent ratings control and match the selected writing checkpoint's exposure."""

import argparse
import fcntl
import time
from pathlib import Path

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.convergence import (
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.evidence_run import evidence_training_outputs
from csts_pilot.proposition_evidence_run import phase_config
from csts_pilot.qwen_evidence import fit_qwen_evidence
from jep_pilot.loaders import load_json


def matched_control_record(records: list[dict], writing: dict) -> dict:
    """Select the sealed control epoch with the writing checkpoint's exact update count."""
    if not 1 <= writing["epoch"] <= len(records):
        raise ValueError("The matched control epoch has not completed.")
    chosen = records[writing["epoch"] - 1]
    trace = load_json(artifact_path(chosen, "train", "trace", "trace.json"))
    if (
        trace["completed_epoch"] != writing["epoch"]
        or trace["actual_updates"] != writing["step"]
    ):
        raise ValueError(
            "The control must match the selected writing checkpoint's epochs and updates."
        )
    return chosen


def writing_frontier(root: Path, directory: Path) -> int:
    """Keep the control at most one epoch ahead of the observed writing progress."""
    summary = load_json(directory / "summary.json")
    for record in summary["runs"]:
        if record["name"] == "evidence_pretrain":
            return (
                load_json(artifact_path(record, "train", "trace", "trace.json"))[
                    "completed_epoch"
                ]
                + 1
            )
    flight = summary.get("in_flight") or {}
    if flight.get("name") == "evidence_pretrain":
        paths = list(
            (
                root
                / "experiments"
                / flight["experiment_id"]
                / "runs/evidence_pretrain"
            ).glob("*/artifacts/train/trace/trace.json")
        )
        if len(paths) == 1:
            return load_json(paths[0]).get("completed_epoch", 0) + 1
    return 1


def run(root: Path, name: str) -> None:
    """Seal every control epoch independently and continue the matched parent to ratings patience."""
    directory = root / "qwen_evidence_results" / name
    with (directory / "ratings_worker.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        complete_path = directory / "ratings_arm_complete.json"
        if complete_path.exists():
            return
        summary = load_json(directory / "summary.json")
        settings = summary["settings"]
        prepared = next(r for r in summary["runs"] if r["name"] == "prepare")
        prepared_path = artifact_path(prepared, "prepare", "prepared", "prepared.json")
        source = read_source(root)
        if source.commit != summary["source_commit"]:
            raise ValueError("Control source differs from the writing run.")
        trusted = frozenset({str(source.repository)})
        environment = LocalEnvSpec(
            compute=CUDAComputeSpec(model=settings["gpu_model"], count=1),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
            ),
            python_env=observe_python_env(),
        )
        metrics = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        records_path = directory / "ratings_epoch_runs.json"
        records = load_json(records_path) if records_path.exists() else []
        for record in records:
            api.verify_run(
                api.VerifyRunRequest(
                    root=root,
                    path=Path(record["path"]),
                    trusted_source_repositories=trusted,
                )
            )

        def execute(phase: str, epoch: int, parent: dict | None) -> dict:
            """Run one frozen control stage with unchanged optimizer and RNG continuation."""
            parent_path = (
                artifact_path(parent, "train", "last_model", "model.pt")
                if parent
                else None
            )
            cfg = phase_config(settings, "ratings", phase, prepared_path, parent_path)
            inputs = [
                input(k, path=settings["splits"][k]["path"], data_role="training")
                for k in ("training", "validation")
            ]
            inputs.append(
                input(
                    "prepared", source=artifact_source(prepared, "prepare", "prepared")
                )
            )
            if parent:
                bindings = {"parent_model": "last_model"}
                if phase == "pretrain":
                    bindings.update(parent_resume="resume_state", parent_trace="trace")
                inputs.extend(
                    input(k, source=artifact_source(parent, "train", v))
                    for k, v in bindings.items()
                )
            if phase == "pretrain":
                cfg = cfg.model_copy(
                    update={"start_epoch": epoch - 1, "max_epochs": epoch}
                )
            configured = stage(
                fit_qwen_evidence,
                stage_id="train",
                config=cfg,
                inputs=tuple(inputs),
                outputs=evidence_training_outputs(),
                metrics=metrics,
                objective=maximize(metrics[-1]),
                reuse="never",
            )
            trial = experiment(
                experiment_id=f"csts_full_control_{source.commit[:8]}_{summary['attempt']}_{phase}_{epoch}",
                variants=(
                    variant(
                        f"ratings_{phase}",
                        stages=(configured,),
                        estimator=configured.outputs["model"],
                    ),
                ),
                replicates=(replicate(seed=cfg.seed),),
            )
            marker = directory / "ratings_worker_stage.json"
            write_json(
                marker,
                {
                    "status": "running",
                    "phase": phase,
                    "epoch": epoch,
                    "experiment_id": trial.experiment_id,
                },
            )
            result = execution.run(
                plan(experiment=trial, source=source, env=environment),
                timeout_seconds=None,
                trusted_source_repositories=trusted,
            )
            if result.status != "succeeded":
                raise RuntimeError(
                    "Preserve the incomplete native control stage before recovery."
                )
            record = {
                "name": f"ratings_{phase}",
                "status": result.status,
                "path": str(result.path),
                "reference": result.reference.model_dump(mode="json"),
            }
            trace = artifact_path(record, "train", "trace", "trace.json")
            write_json(directory / f"ratings_{phase}_trace.json", load_json(trace))
            return record

        selected_path = directory / "writing_selected.json"
        while True:
            selected = (
                load_json(selected_path)["epoch"] if selected_path.exists() else None
            )
            if selected is not None and len(records) >= selected:
                chosen = matched_control_record(records, load_json(selected_path))
                break
            if len(records) >= writing_frontier(root, directory):
                time.sleep(10)
                continue
            record = execute(
                "pretrain", len(records) + 1, records[-1] if records else None
            )
            records.append(record)
            write_json(records_path, records)
        writing = load_json(selected_path)
        chosen_trace = load_json(artifact_path(chosen, "train", "trace", "trace.json"))
        write_json(directory / "ratings_pretrain_trace.json", chosen_trace)
        ratings = execute("ratings", 0, chosen)
        write_json(
            complete_path, {"runs": [chosen, ratings], "matched_writing": writing}
        )


def main() -> None:
    """Report worker failures without changing sealed measurements."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    try:
        run(args.root, args.name)
    except Exception as error:
        write_json(
            args.root
            / "qwen_evidence_results"
            / args.name
            / "ratings_worker_error.json",
            {"type": type(error).__name__, "message": str(error)},
        )
        raise


if __name__ == "__main__":
    main()
