"""Run Tranche 3's reviewed three-arm evidence-supervision comparison."""

import argparse
import fcntl
import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, OutputDraft, StageOutputs, TrainOutputs, output
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
    InitializationConfig,
    file_sha256,
    initialize,
    test_mse,
    test_spearman,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, artifact_source, check_inputs
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_controls import (
    EvidenceConfig,
    EvidencePredictionConfig,
    EvidenceTestConfig,
    PreparationConfig,
    capture_evidence_predictions,
    evaluate_evidence,
    fit_evidence,
    prepare_evidence,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs

ARMS = ("ratings", "evidence", "shuffled")
PRETEST_STAGES = (
    "prepare",
    "initialize",
    *(f"{arm}_{phase}" for arm in ARMS for phase in ("pretrain", "ratings")),
    "publish_test",
)


def validate_evaluation_resume(directory: Path, summary: dict[str, Any]) -> None:
    """Permit recovery only after training and selection have finished."""
    records = summary["runs"]
    names = [r["name"] for r in records]
    allowed = set(PRETEST_STAGES) | {
        f"{phase}_{arm}" for arm in ARMS for phase in ("predict", "evaluate")
    }
    if (
        names[: len(PRETEST_STAGES)] != list(PRETEST_STAGES)
        or len(names) != len(set(names))
        or not set(names) <= allowed
        or any(r["status"] != "succeeded" for r in records)
    ):
        raise ValueError(
            "Evaluation-only recovery requires all completed native training stages."
        )
    selection = directory / "selection.json"
    if file_sha256(selection) != summary["selection_sha256"]:
        raise ValueError("Changed frozen selection during evaluation recovery.")
    frozen = load_json(selection)
    by_name = {r["name"]: r for r in records}
    if (
        frozen["status"] != "checkpoints_frozen"
        or frozen["test_scores_used_for_selection"] is not False
        or set(frozen["candidates"]) != set(ARMS)
        or any(
            frozen["candidates"][arm]["run"] != by_name[f"{arm}_ratings"]
            for arm in ARMS
        )
    ):
        raise ValueError("Frozen candidates differ from completed training records.")


def evidence_training_outputs() -> TrainOutputs[OutputDraft]:
    """Validate the native training contract before starting any study stages."""
    return TrainOutputs(
        model=output(path="model.pt", loader=load_model, data_role="training"),
        resume_state=output(path="resume.pt", loader=load_state, data_role="training"),
        last_model=output(path="model.pt", loader=load_model, data_role="training"),
        trace=output(path="trace.json", loader=load_json, data_role="training"),
        validation_predictions=output(
            path="predictions.json", loader=load_json, data_role="training"
        ),
    )


def validate_matched_traces(traces: dict[str, dict[str, Any]]) -> None:
    """Reject unequal exposure or a selected-weight first-phase transition."""
    first = traces["ratings"]["pretrain"]
    for arm in ARMS:
        pretrain, ratings = traces[arm]["pretrain"], traces[arm]["ratings"]
        for key in (
            "initial_sha256",
            "updates",
            "training_rows",
            "completed_epoch",
            "initial_rng",
        ):
            if pretrain[key] != first[key]:
                raise ValueError(f"Unmatched phase-A {key} in {arm}.")
        if [r["batch_order_sha256"] for r in pretrain["epochs"]] != [
            r["batch_order_sha256"] for r in first["epochs"]
        ]:
            raise ValueError("Phase-A batch orders differ.")
        if ratings["initial_sha256"] != pretrain["terminal_sha256"]:
            raise ValueError("Phase B did not restore its terminal phase-A weights.")
        reference = traces["ratings"]["ratings"]
        count = min(len(ratings["epochs"]), len(reference["epochs"]))
        if [r["batch_order_sha256"] for r in ratings["epochs"][:count]] != [
            r["batch_order_sha256"] for r in reference["epochs"][:count]
        ]:
            raise ValueError("Phase-B batch orders differ.")
        if ratings["initial_rng"] != reference["initial_rng"]:
            raise ValueError("Phase-B initial RNG differs.")


def validate_settings(settings: dict[str, Any]) -> None:
    """Reject a change to the three planned controls or the established schedule."""
    if settings["arms"] != list(ARMS):
        raise ValueError("The three matched arms must remain explicit and ordered.")
    if settings["pretrain_epochs"] != 6 or settings["training"]["max_epochs"] != 40:
        raise ValueError(
            "The reviewed screen uses six pretraining and at most forty rating epochs."
        )
    if (
        settings["training"]["linear_epochs"] != 24
        or settings["training"]["patience"] != 5
    ):
        raise ValueError(
            "Keep the 24-epoch schedule prefix and continuation patience five."
        )
    PreparationConfig(
        **{
            f"{k}_sha256": v["sha256"]
            for k, v in settings["splits"].items()
            if k != "test"
        },
        answers_sha256=settings["answers"]["sha256"],
    )


def run_study(
    root: Path,
    settings: dict[str, Any],
    name: str,
    resume: bool = False,
    evaluation_only: bool = False,
) -> None:
    """Seal each local stage and queue publication without waiting for cloud storage."""
    validate_settings(settings)
    train_outputs = evidence_training_outputs()
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError(
            "Use local native sealing and the asynchronous publication queue."
        )
    check_inputs(root, settings)
    if file_sha256(root / settings["answers"]["path"]) != settings["answers"]["sha256"]:
        raise ValueError("Teacher cache differs from the reviewed input.")
    directory = root / "evidence_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "summary.json"
    if evaluation_only and (not resume or not path.exists()):
        raise ValueError(
            "Evaluation-only recovery requires an existing run and --resume."
        )
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    environment = observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    if path.exists():
        summary = load_json(path)
        if (
            not resume
            or (summary["source_commit"] != source.commit and not evaluation_only)
            or summary["settings"] != settings
            or summary.get("in_flight")
        ):
            raise ValueError(
                "Preserve existing measurements; reconcile any uncertain invocation before resuming."
            )
        if evaluation_only:
            validate_evaluation_resume(directory, summary)
            if summary.get("evaluation_source_commit", source.commit) != source.commit:
                raise ValueError(
                    "Evaluation recovery source changed; reconcile before resuming."
                )
            summary["evaluation_source_commit"] = source.commit
            write_json(path, summary)
        if summary["status"] == "complete":
            print(json.dumps({"status": "complete", "summary": str(path)}))
            return
    else:
        summary = {
            "source_commit": source.commit,
            "settings": settings,
            "status": "running",
            "attempt": uuid.uuid4().hex[:8],
            "runs": [],
            "gpu_stage_seconds": 0.0,
            "in_flight": None,
            "live_scores": {},
        }
        write_json(path, summary)

    def execute(name: str, configured: Any, gpu: bool = False) -> dict[str, Any]:
        previous = [r for r in summary["runs"] if r["name"] == name]
        if len(previous) > 1:
            raise ValueError("Duplicate native stage records.")
        if previous:
            record = previous[0]
            if record["status"] != "succeeded":
                raise ValueError("Inspect a failed native stage before recovery.")
            api.verify_run(
                api.VerifyRunRequest(
                    root=root,
                    path=Path(record["path"]),
                    trusted_source_repositories=trusted,
                )
            )
            queue_publication(
                root, ResolvedRunRef.model_validate(record["reference"]), destination
            )
            return record
        if evaluation_only and name in PRETEST_STAGES:
            raise ValueError(
                "Evaluation-only recovery cannot execute a training or preparation stage."
            )
        trial = experiment(
            experiment_id=f"csts_tranche3_{source.commit[:8]}_{summary['attempt']}_{name}",
            variants=(
                variant(
                    name,
                    stages=(configured,),
                    estimator=configured.outputs["model"]
                    if "model" in configured.outputs
                    else next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=settings["training"]["seed"]),),
        )
        summary.update(
            current_stage=name,
            in_flight={"name": name, "experiment_id": trial.experiment_id},
        )
        write_json(path, summary)
        remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
        if gpu and remaining <= 0:
            raise TimeoutError(
                "The reviewed aggregate GPU-stage allowance is exhausted."
            )
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(model="NVIDIA L4", count=1)
            if gpu
            else CPUComputeSpec(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
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
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "local_run_seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native stage failed: {name}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(path, summary)
        print(
            json.dumps(
                {
                    "stage": name,
                    "status": "succeeded",
                    "seconds": record["local_run_seconds"],
                }
            ),
            flush=True,
        )
        return record

    prepared = execute(
        "prepare",
        stage(
            prepare_evidence,
            stage_id="prepare",
            config=PreparationConfig(
                answers_sha256=settings["answers"]["sha256"],
                training_sha256=settings["splits"]["training"]["sha256"],
                validation_sha256=settings["splits"]["validation"]["sha256"],
            ),
            inputs=tuple(
                input(
                    k,
                    path=settings["answers"]["path"]
                    if k == "answers"
                    else settings["splits"][k]["path"],
                    data_role="training",
                )
                for k in ("answers", "training", "validation")
            ),
            outputs=StageOutputs(
                prepared=output(
                    path="prepared.json", loader=load_json, data_role="training"
                )
            ),
            reuse="never",
        ),
    )
    prepared_path = artifact_path(prepared, "prepare", "prepared", "prepared.json")
    summary["preparation"] = load_json(prepared_path)["audit"]
    write_json(path, summary)
    print(json.dumps({"preparation": summary["preparation"]}), flush=True)
    initialized = execute(
        "initialize",
        stage(
            initialize,
            stage_id="initialize",
            config=InitializationConfig(
                **{
                    k: settings["training"][k]
                    for k in ("model_id", "revision", "projection_dimension", "seed")
                }
            ),
            outputs=StageOutputs(
                model=output(path="model.pt", loader=load_model, data_role="training")
            ),
            reuse="never",
        ),
    )
    metrics = tuple(
        measure(m) for m in (training_objective, validation_mse, validation_spearman)
    )
    trained, traces = {}, {}
    for arm in ARMS:
        traces[arm] = {}
        parent, parent_stage, parent_artifact = initialized, "initialize", "model"
        for phase in ("pretrain", "ratings"):
            initial_path = artifact_path(
                parent, parent_stage, parent_artifact, "model.pt"
            )
            config = EvidenceConfig(
                **{
                    **settings["training"],
                    "max_epochs": settings["pretrain_epochs"]
                    if phase == "pretrain"
                    else settings["training"]["max_epochs"],
                },
                arm=arm,
                phase=phase,
                training_sha256=settings["splits"]["training"]["sha256"],
                validation_sha256=settings["splits"]["validation"]["sha256"],
                prepared_sha256=file_sha256(prepared_path),
                initial_sha256=file_sha256(initial_path),
            )
            configured = stage(
                fit_evidence,
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
                        "prepared",
                        source=artifact_source(prepared, "prepare", "prepared"),
                    ),
                    input(
                        "initial_model",
                        source=artifact_source(parent, parent_stage, parent_artifact),
                    ),
                ),
                outputs=train_outputs,
                metrics=metrics,
                objective=maximize(metrics[-1]),
                reuse="never",
            )
            parent = execute(f"{arm}_{phase}", configured, gpu=True)
            parent_stage, parent_artifact = "train", "last_model"
            trace = load_json(artifact_path(parent, "train", "trace", "trace.json"))
            traces[arm][phase] = trace
            shutil.copyfile(
                artifact_path(parent, "train", "trace", "trace.json"),
                directory / f"{arm}_{phase}_trace.json",
            )
            if (
                phase == "pretrain"
                and trace["completed_epoch"] != settings["pretrain_epochs"]
            ):
                raise ValueError(
                    "Pretraining did not complete the common update budget."
                )
        trained[arm] = parent

    validate_matched_traces(traces)
    # All three candidates are selected before any test data is published here.
    candidates = {}
    for arm, record in trained.items():
        model = artifact_path(record, "train", "model", "model.pt")
        trace = load_json(artifact_path(record, "train", "trace", "trace.json"))
        scored = load_json(
            artifact_path(record, "train", "validation_predictions", "predictions.json")
        )
        selected = trace["selected"]
        if selected["sha256"] != file_sha256(model) or selected[
            "validation"
        ] != summarize(scored):
            raise ValueError("Checkpoint, trace and validation predictions disagree.")
        candidates[arm] = dict(selected, run=record)
    selection = {
        "status": "checkpoints_frozen",
        "candidates": candidates,
        "test_scores_used_for_selection": False,
    }
    selection_path = directory / "selection.json"
    if selection_path.exists() and load_json(selection_path) != selection:
        raise ValueError("A frozen selection already exists with different candidates.")
    write_json(selection_path, selection)
    selection_sha = file_sha256(selection_path)
    summary["selection_sha256"] = selection_sha
    write_json(path, summary)
    published = execute(
        "publish_test",
        stage(
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
            reuse="never",
        ),
    )
    for arm, candidate in candidates.items():
        config = EvidenceTestConfig(
            arm=arm,
            model_sha256=candidate["sha256"],
            selection_sha256=selection_sha,
            test_sha256=settings["splits"]["test"]["sha256"],
        )
        common = (
            input("model", source=artifact_source(candidate["run"], "train", "model")),
            input(
                "selection",
                path=str(selection_path.relative_to(root)),
                data_role="training",
            ),
            input("test", source=artifact_source(published, "publish", "test", "eval")),
            input(
                "holdout",
                source=artifact_source(published, "publish", "holdout", "eval"),
            ),
        )
        snapshot = execute(
            f"predict_{arm}",
            stage(
                capture_evidence_predictions,
                stage_id="predict",
                config=EvidencePredictionConfig(**config.model_dump()),
                inputs=common,
                outputs=StageOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    binding=output(
                        path="binding.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            gpu=True,
        )
        snapshot_path = artifact_path(
            snapshot, "predict", "predictions", "predictions.json"
        )
        summary["live_scores"][arm] = summarize(load_json(snapshot_path))
        write_json(path, summary)
        print(
            json.dumps(
                {
                    "arm": arm,
                    "TEST_SCORES": summary["live_scores"][arm],
                    "verification": "native_eval_pending",
                }
            ),
            flush=True,
        )
        dependencies = (
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        )
        comparator = FloatComparator(mode="absolute", tolerance=1e-12)
        test_metrics = tuple(
            measure(m, dependencies=dependencies, comparator=comparator)
            for m in (test_mse, test_spearman)
        )
        evaluated = execute(
            f"evaluate_{arm}",
            stage(
                evaluate_evidence,
                stage_id="test",
                eval_id="csts_tranche3",
                config=config,
                inputs=common
                + (
                    input(
                        "snapshot_predictions",
                        source=artifact_source(
                            snapshot, "predict", "predictions", "eval"
                        ),
                    ),
                    input(
                        "binding",
                        source=artifact_source(snapshot, "predict", "binding", "eval"),
                    ),
                ),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    )
                ),
                metrics=test_metrics,
                objective=maximize(test_metrics[-1]),
                reuse="never",
            ),
        )
        shutil.copyfile(
            artifact_path(evaluated, "test", "predictions", "predictions.json"),
            directory / f"{arm}_predictions.json",
        )
    summary.update(
        status="complete", current_stage=None, publication_status="queued_separately"
    )
    write_json(path, summary)
    print(
        json.dumps({"status": "complete", "scores": summary["live_scores"]}), flush=True
    )
    from csts_pilot.evidence_report import build_report

    build_report(root, directory)


def main() -> None:
    """Show the frozen settings unless execution was explicitly requested."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--settings", type=Path, default=Path("configs/csts-tranche-3.json")
    )
    parser.add_argument("--name", default="initial")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--evaluation-only", action="store_true")
    args = parser.parse_args()
    root = resolve_root()
    settings = load_json(root / args.settings)
    validate_settings(settings)
    if not args.execute:
        print(json.dumps(settings, indent=2))
        return
    if not args.name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Run names must be simple identifiers.")
    (root / "evidence_results").mkdir(exist_ok=True)
    with (root / "evidence_results/run.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_study(root, settings, args.name, args.resume, args.evaluation_only)


if __name__ == "__main__":
    main()
