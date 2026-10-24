"""Run the approved Tranche 1 comparison through native VIPER stages."""

import argparse
import fcntl
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from viper import api, execution
from viper.artifacts import StageArtifactRef
from viper.authoring import (
    experiment,
    input,
    plan,
    replicate,
    run_artifact,
    stage,
    variant,
)
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef, ResolvedRunRef
from viper.repository import read_source, resolve_root
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.background_storage import queue_publication
from csts_pilot.convergence import (
    CheckpointConfig,
    ConvergenceConfig,
    InitializationConfig,
    TestConfig,
    file_sha256,
    fit,
    initialize,
    promote_checkpoint,
    test_checkpoint,
    test_mse,
    test_spearman,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_analysis import calibration
from csts_pilot.early_stopping import ValidationPatience
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def check_inputs(root: Path, settings: dict[str, Any]) -> None:
    """Check exact input bytes; inspect only training and validation labels."""
    groups = {}
    for name, expected in settings["splits"].items():
        path = root / expected["path"]
        if file_sha256(path) != expected["sha256"]:
            raise ValueError(f"Input identity differs for {name}.")
        if name == "test":
            continue
        rows = load_json(path)
        groups[name] = {row["group_id"] for row in rows}
        if len(rows) != expected["rows"] or len(groups[name]) != expected["groups"]:
            raise ValueError(f"Input cohort differs for {name}.")
    if groups["training"] & groups["validation"]:
        raise ValueError("Training and validation caption groups overlap.")


def artifact_path(
    record: dict[str, Any], stage_id: str, name: str, filename: str
) -> Path:
    """Locate the local copy of a successfully published native artifact."""
    return Path(record["path"]).parent / "artifacts" / stage_id / name / filename


def artifact_source(
    record: dict[str, Any],
    stage_id: str,
    name: str,
    role: Literal["training", "eval"] = "training",
) -> Any:
    """Use sealed native references for every cross-stage artifact dependency."""
    return run_artifact(
        ResolvedRunRef.model_validate(record["reference"]),
        StageArtifactRef(stage_id=stage_id, artifact_name=name),
        path=f"inputs/{name}",
        data_role=role,
    )


def canonical_checkpoint(candidate: dict[str, Any], execute: Any) -> tuple[Any, str]:
    """Expose prefix bytes as model; VIPER requires this stored-input name."""
    if candidate["artifact_name"] == "model":
        return candidate["run"], "train"
    configured = stage(
        promote_checkpoint,
        stage_id="checkpoint",
        config=CheckpointConfig(model_sha256=candidate["sha256"]),
        inputs=(
            input(
                "checkpoint",
                source=artifact_source(
                    candidate["run"], "train", candidate["artifact_name"]
                ),
            ),
        ),
        outputs=StageOutputs(
            model=output(path="model.pt", loader=load_model, data_role="training")
        ),
        reuse="never",
    )
    record = execute(
        f"checkpoint_{candidate['arm']}_{candidate['window']}",
        configured,
        configured.outputs["model"],
        gpu=False,
    )
    return record, "checkpoint"


def evaluation_stage(
    identity: str,
    model_record: dict[str, Any],
    model_stage: str,
    published: dict[str, Any],
    settings: dict[str, Any],
    selection_sha256: str,
) -> Any:
    """Bind native scoring to a canonical model and the frozen test inputs."""
    dependencies = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    metrics = (
        measure(test_mse, dependencies=dependencies, comparator=comparator),
        measure(test_spearman, dependencies=dependencies, comparator=comparator),
    )
    return stage(
        test_checkpoint,
        stage_id="test",
        eval_id="csts_tranche1",
        config=TestConfig(
            model_sha256=identity,
            selection_sha256=selection_sha256,
            test_sha256=settings["splits"]["test"]["sha256"],
        ),
        inputs=(
            input(
                "model",
                source=artifact_source(model_record, model_stage, "model"),
            ),
            input(
                "selection",
                path="convergence_results/selection.json",
                data_role="training",
            ),
            input(
                "test",
                source=artifact_source(published, "publish", "test", "eval"),
            ),
            input(
                "holdout",
                source=artifact_source(published, "publish", "holdout", "eval"),
            ),
        ),
        split_inputs=("holdout",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            timing=output(path="timing.json", loader=load_json, data_role="eval"),
        ),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )


def verify_matched_arms(traces: dict[str, dict[str, Any]]) -> None:
    """Require shared setup and pair orders; validate each declared stop rule."""
    a, b = traces["mse"], traces["pearson"]
    common_a = {
        key: value
        for key, value in a["config"].items()
        if key not in {"rating_objective", "max_seconds"}
    }
    common_b = {
        key: value
        for key, value in b["config"].items()
        if key not in {"rating_objective", "max_seconds"}
    }
    if common_a != common_b:
        raise ValueError("The arms differ in their shared training configuration.")
    if (
        a["config"]["rating_objective"] != "mse"
        or b["config"]["rating_objective"] != "pearson"
    ):
        raise ValueError("The comparison requires one MSE arm and one Pearson arm.")
    for key in (
        "initial_model_sha256",
        "initial_rng",
        "updates_per_epoch",
        "total_updates",
        "warmup_updates",
        "nonpadding_input_tokens_per_epoch",
    ):
        if a[key] != b[key]:
            raise ValueError(f"The matched arms differ in {key}.")
    for trace in traces.values():
        epochs = trace["epochs"]
        cap = trace["config"]["max_epochs"]
        if trace["status"] != "complete" or not epochs or len(epochs) > cap:
            raise ValueError("Both arms require a completed, valid epoch trace.")
        if trace["total_updates"] != cap * trace["updates_per_epoch"]:
            raise ValueError("An arm changed its declared scheduler horizon.")
        if trace["actual_updates"] != len(epochs) * trace["updates_per_epoch"]:
            raise ValueError("An arm used an incomplete update budget.")
        stopping = ValidationPatience(
            trace["config"].get("patience"), trace["config"].get("min_delta", 0.0)
        )
        expected_stop = cap
        for epoch, record in enumerate(epochs, 1):
            if (
                record["epoch"] != epoch
                or record["step"] != epoch * trace["updates_per_epoch"]
            ):
                raise ValueError("The epoch trace has inconsistent update counters.")
            exhausted = stopping.observe(record["validation"]["spearman"])
            if exhausted and epoch >= trace["config"]["prefix_epochs"]:
                expected_stop = epoch
                break
        if len(epochs) != expected_stop:
            raise ValueError("An arm differs from its declared validation stop rule.")
        if len(epochs) < cap and trace.get("stop_reason") != "validation_patience":
            raise ValueError("An early stop requires its validation patience receipt.")
    shared_epochs = min(len(a["epochs"]), len(b["epochs"]))
    if [r["batch_order_sha256"] for r in a["epochs"][:shared_epochs]] != [
        r["batch_order_sha256"] for r in b["epochs"][:shared_epochs]
    ]:
        raise ValueError("The arms used different pair orders.")


def freeze_selection(
    records: dict[str, dict[str, Any]], destination: Path
) -> dict[str, Any]:
    """Select by validation alone, then freeze all four checkpoint identities."""
    traces = {
        arm: load_json(artifact_path(record, "train", "trace", "trace.json"))
        for arm, record in records.items()
    }
    verify_matched_arms(traces)
    candidates = {}
    for arm, record in records.items():
        shutil.copyfile(
            artifact_path(record, "train", "trace", "trace.json"),
            destination.parent / f"{arm}_trace.json",
        )
        for window in ("prefix", "full"):
            model_name = "prefix_model" if window == "prefix" else "model"
            predictions_name = (
                "prefix_validation_predictions"
                if window == "prefix"
                else "validation_predictions"
            )
            selected = traces[arm]["selected"][window]
            if (
                file_sha256(artifact_path(record, "train", model_name, "model.pt"))
                != selected["sha256"]
            ):
                raise ValueError("The selected checkpoint bytes differ from the trace.")
            rows = load_json(
                artifact_path(record, "train", predictions_name, "predictions.json")
            )
            write_json(destination.parent / f"{arm}_{window}_validation.json", rows)
            candidates[f"{arm}_{window}"] = {
                **selected,
                "arm": arm,
                "window": window,
                "artifact_name": model_name,
                "run": record,
                "calibration": calibration(rows),
            }
    mse_score = candidates["mse_full"]["validation"]["spearman"]
    pearson_score = candidates["pearson_full"]["validation"]["spearman"]
    selection = {
        "status": "checkpoints_frozen",
        "comparison_regime": (
            "validation_early_stopping"
            if traces["mse"]["config"].get("patience") is not None
            else "fixed_update_budget"
        ),
        "actual_updates": {
            arm: trace["actual_updates"] for arm, trace in traces.items()
        },
        "candidates": candidates,
        "provisional_loss": "pearson" if pearson_score > mse_score else "mse",
        "choice_split": "validation",
        "checkpoint_tie_rule": "earlier epoch",
        "loss_tie_rule": "mse",
        "test_scores_used_for_selection": False,
    }
    if destination.exists():
        if load_json(destination) != selection:
            raise ValueError(
                "The existing frozen selection differs. Preserve it and inspect the run."
            )
    else:
        write_json(destination, selection)
    return selection


def run_study(root: Path, settings: dict[str, Any], resume: bool = False) -> None:
    """Use verified local runs downstream while cloud publication proceeds separately."""
    storage = load_storage_settings(root)
    if not isinstance(storage.destination, LocalStorageDestination):
        raise ValueError(
            "Select destination = 'local' in viper.toml before this runner starts."
        )
    cloud_destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    result_dir = root / "convergence_results"
    result_dir.mkdir(exist_ok=True)
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    summary_path = result_dir / "summary.json"
    if summary_path.exists():
        if not resume:
            raise RuntimeError(
                "Prior run state exists. Inspect it and use --resume to continue."
            )
        summary = load_json(summary_path)
        if summary["source_commit"] != source.commit or summary["settings"] != settings:
            raise ValueError("Resume requires the same frozen source and settings.")
    else:
        summary = {
            "source_commit": source.commit,
            "attempt": uuid.uuid4().hex[:8],
            "settings": settings,
            "runs": [],
            "test": [],
            "gpu_stage_seconds": 0.0,
        }
    if summary.get("status") == "complete":
        print(json.dumps({"status": "complete", "summary": str(summary_path)}))
        return
    check_inputs(root, settings)
    write_json(
        result_dir / "operator.json",
        {"pid": os.getpid(), "source_commit": source.commit},
    )
    environment = observe_python_env()

    def execute(
        name: str, configured: Any, estimator: Any, gpu: bool
    ) -> dict[str, Any]:
        for record in summary["runs"]:
            if record["name"] != name:
                continue
            if record["status"] != "succeeded":
                raise RuntimeError(
                    f"The saved {name} stage failed. Inspect its native artifacts before retrying."
                )
            if record["status"] == "succeeded":
                api.verify_run(
                    api.VerifyRunRequest(
                        root=root,
                        path=Path(record["path"]),
                        trusted_source_repositories=trusted,
                    )
                )
                record["publication_queue"] = str(
                    queue_publication(
                        root,
                        ResolvedRunRef.model_validate(record["reference"]),
                        cloud_destination,
                    )
                )
                write_json(summary_path, summary)
                return record
        if summary.get("in_flight"):
            raise RuntimeError(
                "An interrupted native invocation needs reconciliation before another stage can start."
            )
        remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
        if gpu and remaining <= 0:
            raise TimeoutError("The common GPU budget is exhausted.")
        summary.update(status="running", current_stage=name)
        write_json(summary_path, summary)
        trial = experiment(
            experiment_id=f"csts_tranche1_{source.commit[:7]}_{summary['attempt']}_{name}",
            variants=(variant(name, stages=(configured,), estimator=estimator),),
            replicates=(replicate(seed=settings["training"]["seed"]),),
        )
        summary["in_flight"] = {"stage": name, "experiment_id": trial.experiment_id}
        write_json(summary_path, summary)
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
            write_json(summary_path, summary)
        record = {
            "name": name,
            "path": str(result.path),
            "status": result.status,
            "reference": result.reference.model_dump(mode="json"),
            "local_run_seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise RuntimeError(
                f"Native stage failed: {name}. Inspect {result.path} before resuming."
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, cloud_destination)
        )
        write_json(summary_path, summary)
        return record

    try:
        initial = stage(
            initialize,
            stage_id="initialize",
            config=InitializationConfig(
                **{
                    key: settings["training"][key]
                    for key in ("model_id", "revision", "projection_dimension", "seed")
                }
            ),
            outputs=StageOutputs(
                model=output(path="model.pt", loader=load_model, data_role="training")
            ),
            reuse="never",
        )
        initialized = execute(
            "initialize", initial, initial.outputs["model"], gpu=False
        )
        training_metrics = (
            measure(training_objective),
            measure(validation_mse),
            measure(validation_spearman),
        )
        trained = {}
        for arm in ("mse", "pearson"):
            remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
            config = ConvergenceConfig(
                **settings["training"],
                rating_objective=arm,
                max_seconds=max(1.0, remaining),
            )
            configured = stage(
                fit,
                stage_id="train",
                config=config,
                inputs=(
                    input(
                        "training",
                        path=settings["splits"]["training"]["path"],
                        data_role="training",
                    ),
                    input(
                        "validation",
                        path=settings["splits"]["validation"]["path"],
                        data_role="training",
                    ),
                    input(
                        "initial_model",
                        source=artifact_source(initialized, "initialize", "model"),
                    ),
                ),
                outputs=TrainOutputs(
                    model=output(
                        path="model.pt", loader=load_model, data_role="training"
                    ),
                    prefix_model=output(
                        path="model.pt", loader=load_model, data_role="training"
                    ),
                    last_model=output(
                        path="model.pt", loader=load_model, data_role="training"
                    ),
                    resume_state=output(
                        path="resume.pt", loader=load_state, data_role="training"
                    ),
                    trace=output(
                        path="trace.json", loader=load_json, data_role="training"
                    ),
                    validation_predictions=output(
                        path="predictions.json", loader=load_json, data_role="training"
                    ),
                    prefix_validation_predictions=output(
                        path="predictions.json", loader=load_json, data_role="training"
                    ),
                ),
                metrics=training_metrics,
                objective=maximize(training_metrics[-1]),
                reuse="never",
            )
            trained[arm] = execute(
                f"train_{arm}", configured, configured.outputs["model"], gpu=True
            )

        selection_path = result_dir / "selection.json"
        selection = freeze_selection(trained, selection_path)
        summary["selection_sha256"] = file_sha256(selection_path)
        summary["provisional_loss"] = selection["provisional_loss"]
        write_json(summary_path, summary)
        # Test labels enter the native graph only after all selections are frozen.
        publication = stage(
            publish_evaluation_inputs,
            stage_id="publish",
            inputs=(
                input(
                    "test", path=settings["splits"]["test"]["path"], data_role="eval"
                ),
                input(
                    "holdout",
                    path="csts_data/evaluation_indices.json",
                    data_role="eval",
                ),
            ),
            outputs=StageOutputs(
                test=output(path="test.json", loader=load_json, data_role="eval"),
                holdout=output(path="indices.json", loader=load_json, data_role="eval"),
            ),
        )
        published = execute(
            "publish_test", publication, publication.outputs["test"], gpu=False
        )
        scored = {}
        summary["test"] = []
        for name, candidate in selection["candidates"].items():
            identity = candidate["sha256"]
            if identity not in scored:
                model_record, model_stage = canonical_checkpoint(candidate, execute)
                configured = evaluation_stage(
                    identity,
                    model_record,
                    model_stage,
                    published,
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
                result_dir / f"{name}_predictions.json",
            )
            summary["test"].append(
                {"candidate": name, "checkpoint_sha256": identity, "run": record}
            )
            write_json(summary_path, summary)
        summary.update(status="complete", current_stage=None)
        summary["publication_status"] = "queued_separately"
        write_json(summary_path, summary)
    except BaseException as error:
        summary.update(
            status="failed",
            failure={"type": type(error).__name__, "message": str(error)},
        )
        write_json(summary_path, summary)
        raise


def main() -> None:
    """Show frozen settings by default; execution requires an explicit flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = resolve_root()
    settings = load_json(root / "configs/csts-tranche-1.json")
    if not args.execute:
        print(json.dumps({"status": "review", "settings": settings}, indent=2))
        return
    directory = root / "convergence_results"
    directory.mkdir(exist_ok=True)
    with (directory / "run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_study(root, settings, resume=args.resume)


if __name__ == "__main__":
    main()
