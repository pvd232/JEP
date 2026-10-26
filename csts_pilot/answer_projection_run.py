"""Fit one conditional answer-input projection using the existing training owner."""

import argparse
import fcntl
import math
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
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloudDestination

from csts_pilot.answer_input import baseline_scores, emit
from csts_pilot.answer_projection import AnswerProjectionConfig, extract
from csts_pilot.background_storage import queue_publication
from csts_pilot.baseline_models import FitConfig
from csts_pilot.baseline_stages import fit_projection
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
from csts_pilot.evidence_run import evidence_training_outputs
from jep_pilot.loaders import load_json, load_model


def original_predictions(
    original: list[dict[str, Any]],
    transformed: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Restore original passage text only after checking every transformed row."""
    lookup = {row["row_id"]: row for row in predictions}
    if (
        len(lookup) != len(predictions)
        or len(original) != len(transformed)
        or set(lookup) != {row["row_id"] for row in original}
    ):
        raise ValueError("Projection prediction coverage or row identities differ.")
    result = []
    for before, after in zip(original, transformed, strict=True):
        if {k: v for k, v in before.items() if k not in {"sentence1", "sentence2"}} != {
            k: v for k, v in after.items() if k not in {"sentence1", "sentence2"}
        }:
            raise ValueError("Answer transformation changed comparison metadata.")
        selected = lookup[after["row_id"]]
        if {k: v for k, v in selected.items() if k != "prediction"} != after:
            raise ValueError("Selected predictions differ from transformed inputs.")
        score = float(selected["prediction"])
        if not math.isfinite(score):
            raise ValueError("Projection predictions must be finite.")
        result.append(dict(before, prediction=score))
    return result


def run(root: Path, parent_root: Path, name: str) -> None:
    """Extract answer features once and train one bounded projection candidate."""
    root = root.resolve(strict=True)
    parent_root = parent_root.resolve(strict=True)
    settings = load_json(parent_root / "configs/csts-qwen-evidence.json")
    original_study = load_json(
        parent_root / "qwen_evidence_results/initial/summary.json"
    )
    parent = next(r for r in original_study["runs"] if r["name"] == "ratings_ratings")
    if file_sha256(artifact_path(parent, "train", "model", "model.pt")) != MODEL_SHA256:
        raise ValueError("Selected saved LoRA checkpoint changed.")
    (root / "csts_data").mkdir(exist_ok=True)
    for relative in (
        settings["splits"]["training"]["path"],
        settings["splits"]["validation"]["path"],
        settings["answers"]["path"],
    ):
        destination = root / relative
        if not destination.exists():
            shutil.copyfile(parent_root / relative, destination)
    directory = root / "answer_input_results" / name
    directory.mkdir(parents=True, exist_ok=False)
    events = directory / "events.jsonl"
    events.touch()
    os.environ["CSTS_ANSWER_INPUT_EVENTS"] = str(events)
    source = read_source(root)
    environment = observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "started_unix": time.time(),
        "runs": [],
        "baseline_rerun": False,
        "native_control_head_fitted": False,
    }
    summary_path = directory / "summary.json"
    write_json(summary_path, summary)

    def execute(stage_name: str, configured: Any, timeout: int) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_answer_projection_{source.commit[:8]}_{uuid.uuid4().hex[:8]}_{stage_name}",
            variants=(
                variant(
                    stage_name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["current_stage"] = stage_name
        summary["in_flight"] = trial.experiment_id
        write_json(summary_path, summary)
        emit("stage_started", stage=stage_name)
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
                f"Native projection stage failed: {stage_name}; {result.path}"
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        emit("stage_complete", stage=stage_name, seconds=record["seconds"])
        return record

    try:
        extracted = execute(
            "extract",
            stage(
                extract,
                stage_id="extract",
                config=AnswerProjectionConfig(
                    **settings["encoder"],
                    training_sha256=settings["splits"]["training"]["sha256"],
                    validation_sha256=settings["splits"]["validation"]["sha256"],
                    answers_sha256=settings["answers"]["sha256"],
                    model_sha256=MODEL_SHA256,
                ),
                inputs=(
                    *(
                        input(
                            key,
                            path=settings["splits"][key]["path"],
                            data_role="training",
                        )
                        for key in ("training", "validation")
                    ),
                    input(
                        "answers",
                        path=settings["answers"]["path"],
                        data_role="training",
                    ),
                    input("model", source=artifact_source(parent, "train", "model")),
                ),
                outputs=StageOutputs(
                    embeddings=output(
                        path="embeddings.pt", loader=load_model, data_role="training"
                    ),
                    training=output(
                        path="training.json", loader=load_json, data_role="training"
                    ),
                    validation=output(
                        path="validation.json", loader=load_json, data_role="training"
                    ),
                    audit=output(
                        path="audit.json", loader=load_json, data_role="training"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            ),
            1800,
        )
        for artifact_name, filename in (
            ("audit", "audit.json"),
            ("timing", "timing.json"),
        ):
            shutil.copyfile(
                artifact_path(extracted, "extract", artifact_name, filename),
                directory / filename,
            )
        fit_config = FitConfig(
            **settings["encoder"],
            kind="projection",
            seed=7,
            projection_dimension=128,
            learning_rate=1e-3,
            batch_size=32,
            microbatch_size=32,
            max_epochs=48,
            patience=5,
            max_seconds=600,
            weight_decay=0.01,
            schedule="constant",
            warmup_fraction=0.0,
        )
        measures = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        trained = execute(
            "fit",
            stage(
                fit_projection,
                stage_id="train",
                config=fit_config,
                inputs=tuple(
                    input(key, source=artifact_source(extracted, "extract", key))
                    for key in ("training", "validation", "embeddings")
                ),
                outputs=evidence_training_outputs(),
                metrics=measures,
                objective=maximize(measures[-1]),
                reuse="never",
            ),
            900,
        )
        for artifact_name, filename in (
            ("trace", "trace.json"),
            ("validation_predictions", "predictions.json"),
        ):
            shutil.copyfile(
                artifact_path(trained, "train", artifact_name, filename),
                directory / filename,
            )
        trace = load_json(directory / "trace.json")
        selected = trace["selected"]
        if (
            file_sha256(artifact_path(trained, "train", "model", "model.pt"))
            != selected["sha256"]
        ):
            raise ValueError("Selected projection checkpoint differs from its trace.")
        original_rows = load_json(root / settings["splits"]["validation"]["path"])
        transformed = load_json(
            artifact_path(extracted, "extract", "validation", "validation.json")
        )
        scored = original_predictions(
            original_rows, transformed, load_json(directory / "predictions.json")
        )
        if summarize(scored) != selected["validation"]:
            raise ValueError("Selected projection predictions differ from their trace.")
        baseline_path = artifact_path(
            parent, "train", "validation_predictions", "predictions.json"
        )
        baseline = baseline_scores(original_rows, load_json(baseline_path))
        native_cutoff = recall_cutoff(original_rows, baseline)
        native = arm_metrics(original_rows, baseline, native_cutoff)
        values = np.asarray([row["prediction"] for row in scored])
        cutoff = recall_cutoff(
            original_rows, values, recall=native["operating_point"]["recall"] - 1e-12
        )
        candidate = arm_metrics(original_rows, values, cutoff)
        eligible = (
            candidate["spearman"] is not None
            and candidate["spearman"] >= native["spearman"] + 0.005 - 1e-12
            and candidate["operating_point"]["false_positive_rate"]
            <= native["operating_point"]["false_positive_rate"] + 0.01 + 1e-12
            and candidate["condition_changes"]["accuracy_ties_half"] is not None
            and candidate["condition_changes"]["accuracy_ties_half"]
            >= native["condition_changes"]["accuracy_ties_half"] - 0.01 - 1e-12
        )
        audit = load_json(directory / "audit.json")
        counts = audit["coverage"]["validation"]["accepted_count_per_row"]
        if len(counts) != len(original_rows) or any(
            count not in (0, 1, 2) for count in counts
        ):
            raise ValueError(
                "Answer coverage differs from the selected validation cohort."
            )
        coverage = {}
        for count, cohort in ((2, "both"), (1, "one"), (0, "neither")):
            indices = [i for i, value in enumerate(counts) if value == count]
            coverage[cohort] = {
                "rows": len(indices),
                "candidate": summarize([scored[i] for i in indices])
                if indices
                else None,
                "baseline": summarize(
                    [
                        dict(original_rows[i], prediction=float(baseline[i]))
                        for i in indices
                    ]
                )
                if indices
                else None,
            }
        result = {
            "metrics": {"saved_qwen": native, "answer_projection": candidate},
            "coverage": coverage,
            "selected_epoch": selected["epoch"],
            "selection": {
                "eligible": bool(eligible),
                "selected_arm": "answer_projection" if eligible else None,
                "test_scores_used_for_selection": False,
                "thresholds": {
                    "saved_qwen": native_cutoff,
                    "answer_projection": cutoff,
                },
            },
            "baseline_rerun": False,
            "native_control_head_fitted": False,
            "representation": "Conditioned cached answer inputs with original-passage fallback, all scored through one trained projection.",
            "expert_verified": False,
        }
        write_json(directory / "original_predictions.json", scored)
        write_json(directory / "result.json", result)
        summary.update(status="complete", current_stage=None, result=result)
        write_json(summary_path, summary)
        emit("arm_result", arm="answer_projection", split="validation", **candidate)
        emit("validation_selection", **result["selection"])
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
    args = parser.parse_args()
    print(
        "Waiting for the existing GPU lock before the answer-projection follow-up.",
        flush=True,
    )
    with (args.parent_root / ".viper/overnight_gpu.lock").open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        run(args.root, args.parent_root, args.name)
