"""Continue the two frozen rating arms through native VIPER training and evaluation."""

import argparse
import fcntl
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import StageOutputs, TrainOutputs, output
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
    ConvergenceConfig,
    file_sha256,
    fit,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_analysis import calibration
from csts_pilot.convergence_run import (
    artifact_path,
    artifact_source,
    check_inputs,
    evaluation_stage,
    verify_matched_arms,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def training_stage(arm: str, settings: dict[str, Any], remaining: float) -> Any:
    """Bind every continuation input to its original sealed producer run."""
    parent = settings["parents"][arm]["training_run"]
    metrics = (
        measure(training_objective),
        measure(validation_mse),
        measure(validation_spearman),
    )
    bindings = (
        ("initial_model", "last_model"),
        ("parent_resume", "resume_state"),
        ("parent_trace", "trace"),
        ("incumbent_model", "model"),
        ("incumbent_validation_predictions", "validation_predictions"),
    )
    return stage(
        fit,
        stage_id="train",
        config=ConvergenceConfig(
            **settings["training"],
            rating_objective=arm,
            max_seconds=max(1.0, remaining),
        ),
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
            *(
                input(name, source=artifact_source(parent, "train", artifact))
                for name, artifact in bindings
            ),
        ),
        outputs=TrainOutputs(
            model=output(path="model.pt", loader=load_model, data_role="training"),
            last_model=output(path="model.pt", loader=load_model, data_role="training"),
            resume_state=output(
                path="resume.pt", loader=load_state, data_role="training"
            ),
            trace=output(path="trace.json", loader=load_json, data_role="training"),
            validation_predictions=output(
                path="predictions.json", loader=load_json, data_role="training"
            ),
        ),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )


def freeze_continued_selection(
    records: dict[str, dict[str, Any]], destination: Path
) -> dict[str, Any]:
    """Freeze the historical-or-improved winners using validation alone."""
    traces = {
        arm: load_json(artifact_path(record, "train", "trace", "trace.json"))
        for arm, record in records.items()
    }
    verify_matched_arms(traces)
    candidates = {}
    for arm, record in records.items():
        trace = traces[arm]
        write_json(destination.parent / f"{arm}_trace.json", trace)
        selected = trace["selected"]["full"]
        if (
            file_sha256(artifact_path(record, "train", "model", "model.pt"))
            != selected["sha256"]
        ):
            raise ValueError("The continuation selected checkpoint identity differs.")
        rows = load_json(
            artifact_path(record, "train", "validation_predictions", "predictions.json")
        )
        write_json(destination.parent / f"{arm}_validation.json", rows)
        candidates[f"{arm}_full"] = {
            **selected,
            "arm": arm,
            "run": record,
            "calibration": calibration(rows),
            "historical_best": trace["continuation"]["historical_best"],
            "completed_epochs": len(trace["epochs"]),
            "actual_updates": trace["actual_updates"],
        }
    selection = {
        "status": "checkpoints_frozen",
        "candidates": candidates,
        "choice_split": "validation",
        "test_scores_used_for_selection": False,
        "comparison_regime": "constant_rate_continuation_with_validation_patience",
        "provisional_loss": "pearson"
        if candidates["pearson_full"]["validation"]["spearman"]
        > candidates["mse_full"]["validation"]["spearman"]
        else "mse",
    }
    if destination.exists() and load_json(destination) != selection:
        raise ValueError(
            "Preserve the existing continuation selection before resuming."
        )
    write_json(destination, selection)
    return selection


def run_study(root: Path, settings: dict[str, Any], resume: bool = False) -> None:
    """Run a separately budgeted continuation with background native storage."""
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise ValueError("Continuation requires the configured local immutable store.")
    directory = root / "continuation_results"
    directory.mkdir(exist_ok=True)
    summary_path = directory / "summary.json"
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    if summary_path.exists():
        if not resume:
            raise ValueError("Inspect the saved continuation before using --resume.")
        summary = load_json(summary_path)
        if summary["source_commit"] != source.commit or summary["settings"] != settings:
            raise ValueError(
                "Resume requires the same continuation source and settings."
            )
    else:
        summary = {
            "source_commit": source.commit,
            "settings": settings,
            "attempt": uuid.uuid4().hex[:8],
            "runs": [],
            "test": [],
            "gpu_stage_seconds": 0.0,
            "status": "running",
        }
    if summary["status"] == "complete":
        return
    check_inputs(root, settings)
    environment = observe_python_env()
    write_json(
        directory / "operator.json",
        {"pid": os.getpid(), "source_commit": source.commit},
    )

    def execute(
        name: str, configured: Any, estimator: Any, gpu: bool
    ) -> dict[str, Any]:
        for record in summary["runs"]:
            if record["name"] == name:
                if record["status"] != "succeeded":
                    raise ValueError(
                        "Inspect the saved unsuccessful native invocation."
                    )
                api.verify_run(
                    api.VerifyRunRequest(
                        root=root,
                        path=Path(record["path"]),
                        trusted_source_repositories=trusted,
                    )
                )
                queue_publication(
                    root,
                    ResolvedRunRef.model_validate(record["reference"]),
                    destination,
                )
                return record
        if summary.get("in_flight"):
            raise ValueError(
                "Reconcile the interrupted native invocation before resuming."
            )
        remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
        if gpu and remaining <= 0:
            raise TimeoutError(
                "The separate continuation resource ceiling was reached."
            )
        trial = experiment(
            experiment_id=f"csts_continue_{source.commit[:7]}_{summary['attempt']}_{name}",
            variants=(variant(name, stages=(configured,), estimator=estimator),),
            replicates=(replicate(seed=settings["training"]["seed"]),),
        )
        summary.update(
            status="running",
            current_stage=name,
            in_flight={"name": name, "experiment_id": trial.experiment_id},
        )
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
            elapsed = time.monotonic() - started
            if gpu:
                summary["gpu_stage_seconds"] += elapsed
            write_json(summary_path, summary)
        record = {
            "name": name,
            "path": str(result.path),
            "status": result.status,
            "reference": result.reference.model_dump(mode="json"),
            "local_run_seconds": elapsed,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise ValueError("The native continuation invocation failed.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        return record

    try:
        trained = {}
        for arm in ("mse", "pearson"):
            configured = training_stage(
                arm,
                settings,
                settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"],
            )
            trained[arm] = execute(
                f"train_{arm}", configured, configured.outputs["model"], True
            )
        selection = freeze_continued_selection(trained, directory / "selection.json")
        summary["selection_sha256"] = file_sha256(directory / "selection.json")
        write_json(summary_path, summary)
        configured = stage(
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
            "publish_test", configured, configured.outputs["test"], False
        )
        summary["test"] = []
        for arm in ("mse", "pearson"):
            candidate = selection["candidates"][f"{arm}_full"]
            baseline = settings["parents"][arm]
            if candidate["sha256"] == baseline["baseline_checkpoint"]["sha256"]:
                record = baseline["baseline_evaluation"]
                rows = load_json(root / baseline["baseline_predictions"])
                reused = True
            else:
                configured = evaluation_stage(
                    candidate["sha256"],
                    candidate["run"],
                    "train",
                    published,
                    settings,
                    summary["selection_sha256"],
                    "continuation_results/selection.json",
                )
                record = execute(
                    f"test_{arm}", configured, configured.outputs["predictions"], True
                )
                rows = load_json(
                    artifact_path(record, "test", "predictions", "predictions.json")
                )
                reused = False
            write_json(directory / f"{arm}_predictions.json", rows)
            summary["test"].append(
                {"arm": arm, "run": record, "reused_original_evaluation": reused}
            )
            write_json(summary_path, summary)
        summary.update(
            status="complete",
            current_stage=None,
            publication_status="queued_separately",
        )
        write_json(summary_path, summary)
    except BaseException as error:
        summary.update(
            status="failed",
            failure={"type": type(error).__name__, "message": str(error)},
        )
        write_json(summary_path, summary)
        raise


def main() -> None:
    """Display the continuation settings unless execution is explicitly requested."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = resolve_root()
    settings = load_json(root / "configs/csts-continuation.json")
    if not args.execute:
        print(json.dumps({"status": "review", "settings": settings}, indent=2))
        return
    directory = root / "continuation_results"
    directory.mkdir(exist_ok=True)
    with (directory / "run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_study(root, settings, resume=args.resume)


if __name__ == "__main__":
    main()
