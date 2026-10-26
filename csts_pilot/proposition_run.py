"""Run checked-proposition preparation, frozen scoring and one LoRA adaptation."""

import argparse
import fcntl
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
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

from csts_pilot.answer_input import baseline_scores, emit
from csts_pilot.answer_projection_run import original_predictions
from csts_pilot.background_storage import queue_publication
from csts_pilot.condition_reference import MODEL_SHA256, arm_metrics, recall_cutoff
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.diagnostics import summarize
from csts_pilot.proposition_inputs import (
    PropositionInferenceConfig,
    PropositionPreparationConfig,
    infer,
    prepare,
)
from csts_pilot.proposition_lora import PropositionLoraConfig, fit_proposition_lora
from csts_pilot.proposition_sample import release_verified_model_cache
from jep_pilot.loaders import load_json, load_model, load_state


def relative_input(root: Path, relative: Path) -> str:
    """Keep declared local inputs inside the physical task workspace."""
    if relative.is_absolute() or not (root / relative).resolve().is_relative_to(root):
        raise ValueError(
            "Proposition input paths must remain relative to this workspace."
        )
    return relative.as_posix()


def candidate_eligibility(
    candidate: dict[str, Any], native: dict[str, Any]
) -> dict[str, Any]:
    """Apply the unchanged validation ranking and operating-point guards."""
    rank = candidate["spearman"]
    ordering = candidate["condition_changes"]["accuracy_ties_half"]
    gain = None if rank is None else rank - native["spearman"]
    fpr_change = (
        candidate["operating_point"]["false_positive_rate"]
        - native["operating_point"]["false_positive_rate"]
    )
    order_change = (
        None
        if ordering is None
        else ordering - native["condition_changes"]["accuracy_ties_half"]
    )
    return {
        "eligible": bool(
            gain is not None
            and gain >= 0.005 - 1e-12
            and fpr_change <= 0.01 + 1e-12
            and order_change is not None
            and order_change >= -0.01 - 1e-12
        ),
        "spearman_change": gain,
        "false_positive_rate_change": fpr_change,
        "condition_ordering_change": order_change,
    }


def run(
    root: Path,
    parent_root: Path,
    name: str,
    answers: Path,
    manifest: Path,
    audit_gate: Path,
) -> None:
    """Fit only the new answer-input system; retain saved native comparisons."""
    root, parent_root = root.resolve(strict=True), parent_root.resolve(strict=True)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal native stages locally before asynchronous promotion.")
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("Use a single new attempt-directory name.")
    paths = {
        "answers": relative_input(root, answers),
        "capture_manifest": relative_input(root, manifest),
        "audit_gate": relative_input(root, audit_gate),
    }
    settings = load_json(parent_root / "configs/csts-qwen-evidence.json")
    original = load_json(parent_root / "qwen_evidence_results/initial/summary.json")
    parent = next(
        record for record in original["runs"] if record["name"] == "ratings_ratings"
    )
    model_path = artifact_path(parent, "train", "model", "model.pt")
    baseline_path = artifact_path(
        parent, "train", "validation_predictions", "predictions.json"
    )
    if file_sha256(model_path) != MODEL_SHA256:
        raise ValueError("Selected Qwen checkpoint differs from the fixed comparator.")
    parent_selected = load_json(artifact_path(parent, "train", "trace", "trace.json"))[
        "selected"
    ]
    if parent_selected["sha256"] != MODEL_SHA256:
        raise ValueError("The original checkpoint trace identifies a different model.")
    (root / "csts_data").mkdir(exist_ok=True)
    for split in ("training", "validation"):
        relative = relative_input(root, Path(settings["splits"][split]["path"]))
        if not (root / relative).exists():
            shutil.copyfile(parent_root / relative, root / relative)
        paths[split] = relative
    hashes = {key: file_sha256(root / value) for key, value in paths.items()}
    for split in ("training", "validation"):
        if hashes[split] != settings["splits"][split]["sha256"]:
            raise ValueError(f"Changed original {split} comparison bytes.")
    directory = root / "answer_input_results" / name
    directory.mkdir(parents=True, exist_ok=False)
    events = directory / "events.jsonl"
    events.touch()
    os.environ["CSTS_ANSWER_INPUT_EVENTS"] = str(events)
    source, environment = read_source(root), observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "attempt": uuid.uuid4().hex[:8],
        "started_unix": time.time(),
        "runs": [],
        "source_inputs": hashes,
        "parent_model_sha256": MODEL_SHA256,
        "parent_selected_epoch": parent_selected["epoch"],
        "parent_selected_step": parent_selected["step"],
        "adaptation_updates_at_start": 0,
        "baseline_rerun": False,
        "native_control_head_fitted": False,
    }
    summary_path = directory / "summary.json"
    write_json(summary_path, summary)

    def execute(
        stage_name: str, configured: Any, gpu: bool, timeout: int
    ) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_propositions_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
            variants=(
                variant(
                    stage_name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["in_flight"] = {
            "name": stage_name,
            "experiment_id": trial.experiment_id,
        }
        write_json(summary_path, summary)
        emit("stage_started", stage=stage_name, experiment_id=trial.experiment_id)
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
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=timeout,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": stage_name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise RuntimeError(
                f"Native proposition stage failed: {stage_name}; {result.path}"
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        emit("stage_complete", stage=stage_name, seconds=record["seconds"])
        return record

    try:
        prepared = execute(
            "prepare",
            stage(
                prepare,
                stage_id="prepare",
                config=PropositionPreparationConfig(
                    **{f"{key}_sha256": value for key, value in hashes.items()}
                ),
                inputs=tuple(
                    input(key, path=path, data_role="training")
                    for key, path in paths.items()
                ),
                outputs=StageOutputs(
                    training=output(
                        path="training.json", loader=load_json, data_role="training"
                    ),
                    validation=output(
                        path="validation.json", loader=load_json, data_role="training"
                    ),
                    audit=output(
                        path="audit.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            ),
            False,
            1200,
        )
        audit = load_json(artifact_path(prepared, "prepare", "audit", "audit.json"))
        write_json(directory / "preparation_audit.json", audit)
        transformed = {
            split: artifact_path(prepared, "prepare", split, f"{split}.json")
            for split in ("training", "validation")
        }
        baseline_hash = file_sha256(baseline_path)
        zero = execute(
            "epoch_zero",
            stage(
                infer,
                stage_id="infer",
                config=PropositionInferenceConfig(
                    **settings["encoder"],
                    parent_model_sha256=MODEL_SHA256,
                    original_rows_sha256=hashes["validation"],
                    transformed_rows_sha256=file_sha256(transformed["validation"]),
                    baseline_sha256=baseline_hash,
                ),
                inputs=(
                    input("model", source=artifact_source(parent, "train", "model")),
                    input("original_rows", path=paths["validation"], data_role="eval"),
                    input(
                        "transformed_rows",
                        source=artifact_source(prepared, "prepare", "validation"),
                    ),
                    input(
                        "baseline_predictions",
                        source=artifact_source(
                            parent, "train", "validation_predictions"
                        ),
                    ),
                ),
                outputs=StageOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    result=output(
                        path="result.json", loader=load_json, data_role="eval"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            True,
            1800,
        )
        for artifact_name, filename in (
            ("predictions", "predictions.json"),
            ("result", "result.json"),
            ("timing", "timing.json"),
        ):
            shutil.copyfile(
                artifact_path(zero, "infer", artifact_name, filename),
                directory / f"epoch_zero_{filename}",
            )
        initial = load_json(directory / "epoch_zero_result.json")
        summary["epoch_zero"] = initial
        write_json(summary_path, summary)
        emit(
            "arm_result",
            arm="epoch_zero",
            split="validation",
            **initial["metrics"]["propositions"],
        )
        summary["epoch_zero_cache_release"] = release_verified_model_cache(
            root, model_path, directory / "epoch-zero-model-cache-release.json"
        )
        write_json(summary_path, summary)
        fit = PropositionLoraConfig(
            **settings["encoder"],
            parent_model_sha256=MODEL_SHA256,
            training_sha256=file_sha256(transformed["training"]),
            validation_sha256=file_sha256(transformed["validation"]),
            seed=7,
            learning_rate=2e-5,
            batch_size=32,
            microbatch_size=2,
            patience=5,
            max_epochs=12,
            max_seconds=14400,
            schedule="constant",
            warmup_fraction=0,
            weight_decay=0.01,
            lora_rank=32,
            lora_alpha=32,
            lora_dropout=0.05,
        )
        measures = tuple(
            measure(metric)
            for metric in (training_objective, validation_mse, validation_spearman)
        )
        trained = execute(
            "fit",
            stage(
                fit_proposition_lora,
                stage_id="train",
                config=fit,
                inputs=(
                    input(
                        "initial_model",
                        source=artifact_source(parent, "train", "model"),
                    ),
                    *(
                        input(split, source=artifact_source(prepared, "prepare", split))
                        for split in ("training", "validation")
                    ),
                ),
                outputs=TrainOutputs(
                    model=output(
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
                    warm_start=output(
                        path="warm_start.json", loader=load_json, data_role="training"
                    ),
                ),
                metrics=measures,
                objective=maximize(measures[-1]),
                reuse="never",
            ),
            True,
            15000,
        )
        for artifact_name, filename in (
            ("trace", "trace.json"),
            ("validation_predictions", "predictions.json"),
            ("warm_start", "warm_start.json"),
        ):
            shutil.copyfile(
                artifact_path(trained, "train", artifact_name, filename),
                directory / f"trained_{filename}",
            )
        trace = load_json(directory / "trained_trace.json")
        selected = trace["selected"]
        selected_path = artifact_path(trained, "train", "model", "model.pt")
        if file_sha256(selected_path) != selected["sha256"]:
            raise ValueError("Selected adapted checkpoint differs from its trace.")
        original_rows = load_json(root / paths["validation"])
        scored = original_predictions(
            original_rows,
            load_json(transformed["validation"]),
            load_json(directory / "trained_predictions.json"),
        )
        if summarize(scored) != selected["validation"]:
            raise ValueError(
                "Adapted predictions differ from selected validation metrics."
            )
        baseline = baseline_scores(original_rows, load_json(baseline_path))
        native_cutoff = recall_cutoff(original_rows, baseline)
        native = arm_metrics(original_rows, baseline, native_cutoff)
        if native != initial["metrics"]["saved_qwen"]:
            raise ValueError(
                "The epoch-zero and adapted saved comparator metrics differ."
            )
        values = np.asarray([row["prediction"] for row in scored])
        trained_cutoff = recall_cutoff(
            original_rows, values, recall=native["operating_point"]["recall"] - 1e-12
        )
        adapted = arm_metrics(original_rows, values, trained_cutoff)
        metrics = {
            "saved_qwen": native,
            "epoch_zero": initial["metrics"]["propositions"],
            "adapted": adapted,
        }
        eligibility = {
            arm: candidate_eligibility(metrics[arm], native)
            for arm in ("epoch_zero", "adapted")
        }
        eligible = [
            arm for arm in ("epoch_zero", "adapted") if eligibility[arm]["eligible"]
        ]
        winner = (
            max(eligible, key=lambda arm: metrics[arm]["spearman"])
            if eligible
            else None
        )
        model_record = parent if winner == "epoch_zero" else trained
        model_digest = MODEL_SHA256 if winner == "epoch_zero" else selected["sha256"]
        selection = {
            "selected_arm": winner,
            "eligibility": eligibility,
            "thresholds": {
                arm: item["operating_point"]["cutoff"] for arm, item in metrics.items()
            },
            "selected_model": {
                "run": model_record["reference"],
                "stage_id": "train",
                "artifact_name": "model",
                "sha256": model_digest,
            }
            if winner
            else None,
            "test_scores_used_for_selection": False,
            "source_commit": source.commit,
            "source_inputs": hashes,
            "generation_policy": {
                key: audit["capture_manifest"][key]
                for key in (
                    "generation_template_sha256",
                    "schema_sha256",
                    "model_alias",
                    "reasoning_effort",
                )
            },
        }
        write_json(directory / "selection.json", selection)
        result = {
            "metrics": metrics,
            "coverage": audit["coverage"],
            "selection": selection,
            "selected_training_epoch": selected["epoch"],
            "selected_training_step": selected["step"],
            "completed_epochs": len(trace["epochs"]),
            "actual_updates": trace["actual_updates"],
            "stop_reason": trace["stop_reason"],
            "baseline_rerun": False,
            "candidate_test_evaluation_ran": False,
            "expert_verified": False,
        }
        write_json(directory / "adapted_original_predictions.json", scored)
        write_json(directory / "result.json", result)
        summary.update(
            status="validation_complete" if winner else "complete",
            in_flight=None,
            result=result,
            selection_sha256=file_sha256(directory / "selection.json"),
            next_phase="eligible_test_pending" if winner else None,
            stop_reason=None if winner else "no_validation_candidate_eligible",
        )
        write_json(summary_path, summary)
        emit("arm_result", arm="adapted", split="validation", **adapted)
        emit("validation_selection", **selection)
        emit(
            "study_complete", status=summary["status"], next_phase=summary["next_phase"]
        )
    except Exception as exc:
        summary.update(status="failed", error=str(exc))
        write_json(summary_path, summary)
        emit("study_failed", error=str(exc))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--answers", type=Path, default=Path("csts_data/propositions_tranche8.json")
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("csts_data/propositions_tranche8_manifest.json"),
    )
    parser.add_argument(
        "--audit-gate",
        type=Path,
        default=Path("csts_data/propositions_tranche8_audit_gate.json"),
    )
    args = parser.parse_args()
    print(
        "Waiting for the existing shared GPU lock before proposition adaptation.",
        flush=True,
    )
    with (args.parent_root / ".viper/overnight_gpu.lock").open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        run(
            args.root,
            args.parent_root,
            args.name,
            args.answers,
            args.manifest,
            args.audit_gate,
        )
