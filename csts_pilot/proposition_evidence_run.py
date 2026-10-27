"""Run matched Qwen proposition-generation supervision and ratings control."""

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.metrics import min as minimize
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
from csts_pilot.baseline_models import ScoreConfig
from csts_pilot.baseline_stages import capture_predictions, evaluate_baseline
from csts_pilot.convergence import (
    file_sha256,
    test_mse,
    test_spearman,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, artifact_source, check_inputs
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_run import evidence_training_outputs
from csts_pilot.proposition_evidence_report import build_report
from csts_pilot.proposition_pretraining_stage import (
    PropositionPretrainingPreparationConfig,
    prepare_proposition_pretraining_stage,
)
from csts_pilot.qwen_evidence import (
    QwenEvidenceConfig,
    fit_qwen_evidence,
    heldout_proposition_loss,
    validate_matched_phases,
)
from jep_pilot.loaders import load_json
from jep_pilot.stages import publish_evaluation_inputs

ARMS = ("ratings", "evidence")


def phase_config(
    settings: dict[str, Any], arm: str, phase: str, prepared: Path, parent: Path | None
) -> QwenEvidenceConfig:
    """Keep both phase schedules identical across arms."""
    return QwenEvidenceConfig.model_validate(
        {
            **settings["encoder"],
            **settings["training"],
            **settings["phases"][phase],
            "patience": settings.get("arm_patience", {}).get(
                arm, settings["training"]["patience"]
            ),
            "kind": "lora",
            "arm": arm,
            "phase": phase,
            "training_sha256": settings["splits"]["training"]["sha256"],
            "validation_sha256": settings["splits"]["validation"]["sha256"],
            "prepared_sha256": file_sha256(prepared),
            "parent_sha256": file_sha256(parent) if parent is not None else None,
            "head_sha256": settings["head"]["sha256"],
            "max_answer_tokens": settings["max_answer_tokens"],
            "proposition_until_patience": settings.get(
                "proposition_until_patience", False
            )
            and arm == "evidence"
            and phase == "pretrain",
            "proposition_validation_sha256": settings.get(
                "proposition_validation", {}
            ).get("sha256"),
        }
    )


def validate_settings(settings: dict[str, Any]) -> None:
    """Reject unreviewed loss, phase-length or stopping changes before execution."""
    if settings["head"]["sha256"] == "0" * 64:
        raise ValueError("Bind the restored pretrained head before execution.")
    if settings["arms"] != list(ARMS) or settings["training"]["patience"] not in (
        1,
        2,
        5,
    ):
        raise ValueError(
            "The comparison requires both arms and patience one, two or five."
        )
    if any(
        arm not in ARMS or value not in (1, 2, 5)
        for arm, value in settings.get("arm_patience", {}).items()
    ):
        raise ValueError(
            "Arm patience must name an existing arm and a supported patience."
        )
    if settings.get("allow_budget_censored_pilot") and (
        settings.get("dataset_revision") != "jep-csts-v1"
        or settings["training"]["patience"] != 2
    ):
        raise ValueError(
            "Budget-censored scoring is reserved for the declared jep-csts-v1 pilot."
        )
    if (
        settings["phases"]["pretrain"]["max_epochs"] not in (2, 4)
        and not settings.get("proposition_until_patience")
    ) or settings["phases"]["ratings"]["max_epochs"] != 24:
        raise ValueError(
            "Use two or four matched initial epochs and the declared ratings configuration."
        )
    if settings.get("proposition_until_patience") and (
        not settings["training"].get("train_until_patience")
        or settings["training"]["patience"] != 1
        or not settings.get("proposition_validation", {}).get("sha256")
    ):
        raise ValueError(
            "Full proposition training requires held-out writing references and patience one without ceilings."
        )
    for arm in ARMS:
        for phase in ("pretrain", "ratings"):
            cfg = QwenEvidenceConfig.model_validate(
                {
                    **settings["encoder"],
                    **settings["training"],
                    **settings["phases"][phase],
                    "patience": settings.get("arm_patience", {}).get(
                        arm, settings["training"]["patience"]
                    ),
                    "kind": "lora",
                    "arm": arm,
                    "phase": phase,
                    "training_sha256": settings["splits"]["training"]["sha256"],
                    "validation_sha256": settings["splits"]["validation"]["sha256"],
                    "prepared_sha256": "0" * 64,
                    "head_sha256": settings["head"]["sha256"],
                    "parent_sha256": "0" * 64 if phase == "ratings" else None,
                }
            )
            if (
                cfg.schedule != "constant"
                or cfg.learning_rate != 2e-5
                or cfg.warmup_fraction
                or cfg.start_epoch
            ):
                raise ValueError(
                    "Keep the common constant 2e-5 rate and fresh phase optimizers."
                )
    minimum = sum(p["max_seconds"] for p in settings["phases"].values()) * len(ARMS)
    if settings["gpu_budget_seconds"] < minimum + 1800:
        raise ValueError(
            "Aggregate budget must permit both declared phases and final scoring."
        )


def run_study(
    root: Path, settings: dict[str, Any], name: str, resume: bool = False
) -> None:
    """Run native stages once; freeze both candidates before publishing test inputs."""
    validate_settings(settings)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Use local native sealing and asynchronous cloud publication.")
    check_inputs(root, settings)
    for item in (
        settings["answers"],
        settings["provenance"],
        settings["audit_gate"],
        settings["head"],
    ):
        if file_sha256(root / item["path"]) != item["sha256"]:
            raise ValueError("Auxiliary input identity changed.")
    directory = root / "qwen_evidence_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "summary.json"
    source = read_source(root)
    trusted = frozenset(
        {str(source.repository)}
        | {str(read_source(Path(settings["continuation_parent_root"])).repository)}
        if settings.get("continuation_parent_root")
        else {str(source.repository)}
    )
    if settings.get("completed_arm_root"):
        trusted = trusted | {
            str(read_source(Path(settings["completed_arm_root"])).repository)
        }
    environment = observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    if path.exists():
        summary = load_json(path)
        if (
            not resume
            or summary["source_commit"] != source.commit
            or summary["settings"] != settings
            or summary.get("in_flight")
        ):
            raise ValueError(
                "Preserve the existing attempt; reconcile any uncertain stage before resuming."
            )
        if summary["status"] == "complete":
            build_report(root, directory)
            return
    else:
        summary = {
            "source_commit": source.commit,
            "settings": settings,
            "status": "running",
            "attempt": uuid.uuid4().hex[:8],
            "runs": [],
            "in_flight": None,
            "gpu_stage_seconds": 0.0,
            "live_scores": {},
        }
        write_json(path, summary)

    def execute(stage_name: str, configured: Any, gpu: bool = False) -> dict[str, Any]:
        previous = [r for r in summary["runs"] if r["name"] == stage_name]
        if previous:
            if len(previous) != 1 or previous[0]["status"] != "succeeded":
                raise ValueError("Inspect the existing native stage before recovery.")
            api.verify_run(
                api.VerifyRunRequest(
                    root=root,
                    path=Path(previous[0]["path"]),
                    trusted_source_repositories=trusted,
                )
            )
            queue_publication(
                root,
                ResolvedRunRef.model_validate(previous[0]["reference"]),
                destination,
            )
            return previous[0]
        until_patience = settings["training"].get("train_until_patience", False)
        remaining = settings["gpu_budget_seconds"] - summary["gpu_stage_seconds"]
        if gpu and not until_patience and remaining <= 0:
            raise TimeoutError("Aggregate compute allowance exhausted.")
        trial = experiment(
            experiment_id=f"csts_qwen_proposition_evidence_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
            variants=(
                variant(
                    stage_name,
                    stages=(configured,),
                    estimator=configured.outputs["model"]
                    if "model" in configured.outputs
                    else next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=settings["training"]["seed"]),),
        )
        summary.update(
            current_stage=stage_name,
            in_flight={"name": stage_name, "experiment_id": trial.experiment_id},
        )
        write_json(path, summary)
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(
                model=settings.get("gpu_model", "NVIDIA L4"), count=1
            )
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
                timeout_seconds=None
                if gpu and until_patience
                else max(1, int(remaining))
                if gpu
                else 1800,
                trusted_source_repositories=trusted,
            )
        finally:
            if gpu:
                summary["gpu_stage_seconds"] += time.monotonic() - started
            write_json(path, summary)
        record = {
            "name": stage_name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "local_run_seconds": time.monotonic() - started,
            "data_role": configured.spec.outputs.values()[0].data_role,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native stage failed: {stage_name}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(path, summary)
        print(
            json.dumps(
                {
                    "stage": stage_name,
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
            prepare_proposition_pretraining_stage,
            stage_id="prepare",
            config=PropositionPretrainingPreparationConfig(
                audit_gate_sha256=settings["audit_gate"]["sha256"],
                provenance_sha256=settings["provenance"]["sha256"],
                answers_sha256=settings["answers"]["sha256"],
                training_sha256=settings["splits"]["training"]["sha256"],
                validation_sha256=settings["splits"]["validation"]["sha256"],
            ),
            inputs=tuple(
                input(
                    k,
                    path=settings[k]["path"]
                    if k in ("answers", "provenance", "audit_gate")
                    else settings["splits"][k]["path"],
                    data_role="training",
                )
                for k in (
                    "answers",
                    "training",
                    "validation",
                    "provenance",
                    "audit_gate",
                )
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
    metrics = tuple(
        measure(m) for m in (training_objective, validation_mse, validation_spearman)
    )
    train_outputs = evidence_training_outputs()
    trained = {}
    traces = {arm: {} for arm in ARMS}
    concurrent = settings.get("concurrent_ratings_control", False)
    if concurrent:
        receipt = directory / "ratings_worker_launch.json"
        if not receipt.exists():
            with (directory / "ratings_worker.log").open("ab", buffering=0) as log:
                worker = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "csts_pilot.full_proposition_control",
                        "--root",
                        str(root),
                        "--name",
                        name,
                    ],
                    cwd=root,
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            write_json(receipt, {"pid": worker.pid, "source_commit": source.commit})
        else:
            if not (directory / "ratings_arm_complete.json").exists():
                os.kill(load_json(receipt)["pid"], 0)
    schedule = [("pretrain", ARMS), ("ratings", ARMS)]
    if settings.get("proposition_until_patience"):
        schedule = (
            [
                ("pretrain", ("evidence",)),
                ("ratings", ("evidence",)),
                ("pretrain", ("ratings",)),
                ("ratings", ("ratings",)),
            ]
            if concurrent
            else [("pretrain", ("evidence", "ratings")), ("ratings", ARMS)]
        )
    for phase, arms in schedule:
        for arm in arms:
            if concurrent and arm == "ratings" and phase == "pretrain":
                completed = directory / "ratings_arm_complete.json"
                while not completed.exists():
                    if (directory / "ratings_worker_error.json").exists():
                        raise RuntimeError(
                            "The concurrent control failed; inspect its retained worker error and native outputs."
                        )
                    os.kill(
                        load_json(directory / "ratings_worker_launch.json")["pid"], 0
                    )
                    time.sleep(10)
                records = load_json(completed)["runs"]
                for existing in records:
                    if not any(r["name"] == existing["name"] for r in summary["runs"]):
                        summary["runs"].append(existing)
                write_json(path, summary)
            parent = trained.get(arm)
            parent_output = (
                "model"
                if arm == "evidence" and settings.get("proposition_until_patience")
                else "last_model"
            )
            parent_path = (
                artifact_path(parent, "train", parent_output, "model.pt")
                if parent is not None
                else None
            )
            cfg = phase_config(settings, arm, phase, prepared_path, parent_path)
            if (
                arm == "ratings"
                and phase == "pretrain"
                and settings.get("proposition_until_patience")
            ):
                cfg = cfg.model_copy(
                    update={
                        "max_epochs": traces["evidence"]["pretrain"][
                            "selected_proposition"
                        ]["epoch"]
                    }
                )
            inputs = [
                input(k, path=settings["splits"][k]["path"], data_role="training")
                for k in ("training", "validation")
            ]
            inputs.append(
                input(
                    "prepared", source=artifact_source(prepared, "prepare", "prepared")
                )
            )
            if phase == "pretrain" and arm == "evidence":
                inputs.append(
                    input("head", path=settings["head"]["path"], data_role="training")
                )
                if settings.get("proposition_until_patience"):
                    inputs.append(
                        input(
                            "proposition_validation",
                            path=settings["proposition_validation"]["path"],
                            data_role="validation",
                        )
                    )
            if parent is not None:
                inputs.append(
                    input(
                        "parent_model",
                        source=artifact_source(parent, "train", parent_output),
                    )
                )
            stage_metrics = (
                metrics + (measure(heldout_proposition_loss),)
                if cfg.proposition_until_patience
                else metrics
            )
            record = execute(
                f"{arm}_{phase}",
                stage(
                    fit_qwen_evidence,
                    stage_id="train",
                    config=cfg,
                    inputs=tuple(inputs),
                    outputs=TrainOutputs[OutputDraft](
                        **{
                            key: value.model_copy(update={"data_role": "validation"})
                            for key, value in train_outputs.items()
                        }
                    )
                    if arm == "evidence" and settings.get("proposition_until_patience")
                    else train_outputs,
                    metrics=stage_metrics,
                    objective=minimize(stage_metrics[-1])
                    if cfg.proposition_until_patience
                    else maximize(metrics[-1]),
                    reuse="never",
                ),
                gpu=True,
            )
            traces[arm][phase] = load_json(
                artifact_path(record, "train", "trace", "trace.json")
            )
            shutil.copyfile(
                artifact_path(record, "train", "trace", "trace.json"),
                directory / f"{arm}_{phase}_trace.json",
            )
            trained[arm] = record
            if (
                arm == "evidence"
                and phase == "pretrain"
                and settings.get("proposition_until_patience")
            ):
                write_json(
                    directory / "writing_selected.json",
                    traces[arm][phase]["selected_proposition"],
                )
                summary["matched_pretrain_epochs"] = traces[arm][phase][
                    "selected_proposition"
                ]["epoch"]
                write_json(path, summary)
    validate_matched_phases(
        traces,
        traces["evidence"]["pretrain"]["selected_proposition"]["epoch"]
        if settings.get("proposition_until_patience")
        else settings["phases"]["pretrain"]["max_epochs"],
        allow_budget_censoring=settings.get("allow_budget_censored_pilot") is True,
        converged_propositions=settings.get("proposition_until_patience", False),
    )
    candidates = {}
    for arm, record in trained.items():
        selected = traces[arm]["ratings"]["selected"]
        model = artifact_path(record, "train", "model", "model.pt")
        predictions = load_json(
            artifact_path(record, "train", "validation_predictions", "predictions.json")
        )
        if (
            file_sha256(model) != selected["sha256"]
            or summarize(predictions) != selected["validation"]
        ):
            raise ValueError(
                "Selected checkpoint, trace and validation predictions disagree."
            )
        shutil.copyfile(
            artifact_path(
                record, "train", "validation_predictions", "predictions.json"
            ),
            directory / f"{arm}_validation_predictions.json",
        )
        candidates[arm] = dict(selected, run=record)
    selection = {
        "status": "checkpoints_frozen",
        "candidates": candidates,
        "test_scores_used_for_selection": False,
    }
    selection_path = directory / "selection.json"
    if selection_path.exists() and load_json(selection_path) != selection:
        raise ValueError("Changed frozen selection.")
    write_json(selection_path, selection)
    summary["selection_sha256"] = file_sha256(selection_path)
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
        # The existing scorer expects a lora key. Each arm's view is bound to the
        # global two-arm selection, which was frozen before publishing test data.
        arm_selection = directory / f"{arm}_selection.json"
        view = {
            **selection,
            "candidates": {"lora": candidate},
            "arm": arm,
            "global_selection_sha256": summary["selection_sha256"],
        }
        if arm_selection.exists() and load_json(arm_selection) != view:
            raise ValueError("Changed frozen arm selection.")
        write_json(arm_selection, view)
        cfg = ScoreConfig(
            **settings["encoder"],
            kind="lora",
            model_sha256=candidate["sha256"],
            selection_sha256=file_sha256(arm_selection),
            test_sha256=settings["splits"]["test"]["sha256"],
        )
        common = (
            input("model", source=artifact_source(candidate["run"], "train", "model")),
            input(
                "selection",
                path=str(arm_selection.relative_to(root)),
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
                capture_predictions,
                stage_id="predict",
                config=cfg,
                inputs=common,
                outputs=StageOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            gpu=True,
        )
        summary["live_scores"][arm] = summarize(
            load_json(
                artifact_path(snapshot, "predict", "predictions", "predictions.json")
            )
        )
        write_json(path, summary)
        print(
            json.dumps({"arm": arm, "TEST_SCORES": summary["live_scores"][arm]}),
            flush=True,
        )
        deps = (
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        )
        test_metrics = tuple(
            measure(
                m,
                dependencies=deps,
                comparator=FloatComparator(mode="absolute", tolerance=1e-12),
            )
            for m in (test_mse, test_spearman)
        )
        evaluated = execute(
            f"evaluate_{arm}",
            stage(
                evaluate_baseline,
                stage_id="test",
                eval_id="csts_qwen_evidence",
                config=cfg.model_copy(update={"device": "cpu"}),
                inputs=common
                + (
                    input(
                        "snapshot_predictions",
                        source=artifact_source(
                            snapshot, "predict", "predictions", "eval"
                        ),
                    ),
                    input(
                        "snapshot_timing",
                        source=artifact_source(snapshot, "predict", "timing", "eval"),
                    ),
                ),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="eval"
                    ),
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
    build_report(root, directory)


def main() -> None:
    """Require an explicit execution flag and one owner of the comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--settings",
        type=Path,
        default=Path("configs/csts-qwen-proposition-evidence.json"),
    )
    parser.add_argument("--name", default="propositions_v41")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = resolve_root()
    settings = load_json(root / args.settings)
    validate_settings(settings)
    if not args.execute:
        print(json.dumps(settings, indent=2))
        return
    if not args.name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Run names must be simple identifiers.")
    (root / "qwen_evidence_results").mkdir(exist_ok=True)
    with (root / "qwen_evidence_results/run.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_study(root, settings, args.name, args.resume)


if __name__ == "__main__":
    main()
