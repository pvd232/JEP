"""Triage answer-input LoRA on completed training answers and 30 audited pairs."""

import argparse
import fcntl
import os
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import Field
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
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
from viper.stages import StageContext, build
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.answer_input import baseline_scores, emit
from csts_pilot.answer_projection import validate_original_split
from csts_pilot.answer_projection_run import original_predictions
from csts_pilot.answers import answer_id
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
from csts_pilot.proposition_capture import checked_records
from csts_pilot.proposition_inputs import (
    PropositionInferenceConfig,
    infer,
    source_inventory,
    transform_rows,
)
from csts_pilot.proposition_lora import PropositionLoraConfig, fit_proposition_lora
from csts_pilot.proposition_run import relative_input
from csts_pilot.proposition_sample import release_verified_model_cache
from jep_pilot.loaders import load_json, load_model, load_state

POLICY = (
    "generation_template_sha256",
    "schema_sha256",
    "model_alias",
    "reasoning_effort",
)
AUDIT = Path("training_outputs/proposition_audit")


class SubsetPreparationConfig(BuildConfig):
    """Bind original sources and already-generated, frozen-policy answers."""

    input_sha256: dict[str, str]
    expected_validation_pairs: int = Field(default=30, ge=1)


def select_rows(
    training: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    training_records: list[dict[str, Any]],
    left: list[dict[str, str]],
    right: list[dict[str, str]],
    validation_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Select by captured identities only, never by similarity labels or scores."""
    validate_original_split(training, validation)
    train_items, _ = source_inventory(training, [])
    available = {record["id"] for record in training_records}
    chosen_items = [item for item in train_items if item["id"] in available]
    checked_records(chosen_items, {"records": training_records})
    if any(
        answer_id(item["passage"], item["condition"]) != item["id"]
        for item in left + right
    ):
        raise ValueError("An audited source does not match its canonical identity.")
    checked_records(left + right, {"records": validation_records})
    chosen_training = [
        row
        for row in training
        if all(
            answer_id(row[side], row["condition"]) in available
            for side in ("sentence1", "sentence2")
        )
    ]
    if not chosen_training:
        raise ValueError("No training comparison has both generated identities.")
    chosen_validation = []
    for a, b in zip(left, right, strict=True):
        matches = [
            row
            for row in validation
            if answer_id(row["sentence1"], row["condition"]) == a["id"]
            and answer_id(row["sentence2"], row["condition"]) == b["id"]
        ]
        if len(matches) != 1:
            raise ValueError(
                "An audited validation pair does not identify one original comparison."
            )
        chosen_validation.append(matches[0])
    validate_original_split(chosen_training, chosen_validation)
    if len({row["group_id"] for row in chosen_validation}) != len(chosen_validation):
        raise ValueError(
            "The diagnostic requires one validation pair per source group."
        )
    needed, _ = source_inventory(chosen_training, chosen_validation)
    lookup = {record["id"]: record for record in training_records + validation_records}
    records = [lookup[item["id"]] for item in needed]
    # Quotations above were checked against their actual generation inputs.
    # A canonical alias in an original row can have different raw whitespace.
    return chosen_training, chosen_validation, records


@build(config=SubsetPreparationConfig)
def prepare_subset(context: StageContext[SubsetPreparationConfig]) -> None:
    """Publish the exact subset, replacements and selection provenance natively."""
    config = context.config
    for name, digest in config.input_sha256.items():
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed subset input: {name}.")
    values = {name: load_json(path) for name, path in context.inputs.items()}
    gate = values["gate"]
    if gate.get("passed") is not True or gate.get("generation_frozen") is not True:
        raise ValueError("The frozen proposition fidelity gate has not passed.")
    for key, filename in (
        ("left", "proposition_fresh60_left.json"),
        ("right", "proposition_fresh60_right.json"),
        ("fresh_records", "proposition_fresh60_records.json"),
        ("fresh_manifest", "proposition_fresh60_manifest.json"),
    ):
        if gate.get("audit_files", {}).get(filename) != config.input_sha256[key]:
            raise ValueError(
                "The selected validation audit bytes differ from the passed gate."
            )
    manifest = values["training_manifest"]
    if manifest.get("records_sha256") != config.input_sha256["training_records"]:
        raise ValueError("The captured training manifest identifies different records.")
    if manifest.get("items") != len(values["training_records"]):
        raise ValueError("The captured training-record count differs.")
    if manifest.get("source_training_sha256") != config.input_sha256["training"]:
        raise ValueError("The captured training source differs.")
    fresh = values["fresh_manifest"]
    if manifest.get("capture_source_sha256") != gate.get(
        "capture_source_sha256"
    ) or fresh.get("capture_source_sha256") != gate.get("capture_source_sha256"):
        raise ValueError(
            "The captured sources differ from the audited generation source."
        )
    fresh_policy = {
        "generation_template_sha256": fresh.get("prompt_template_sha256"),
        "schema_sha256": fresh.get("schema_content_sha256"),
        "model_alias": fresh.get("model_alias"),
        "reasoning_effort": fresh.get("reasoning_effort"),
    }
    if any(
        gate.get(key) != manifest.get(key) or gate.get(key) != fresh_policy[key]
        for key in POLICY
    ):
        raise ValueError(
            "The training and audited validation generation policies differ."
        )
    if fresh.get("source_validation_sha256") != config.input_sha256["validation"]:
        raise ValueError("The audited validation source differs.")
    training, validation, records = select_rows(
        values["training"],
        values["validation"],
        values["training_records"],
        values["left"],
        values["right"],
        values["fresh_records"],
    )
    if len(validation) != config.expected_validation_pairs:
        raise ValueError("The frozen diagnostic validation-pair count differs.")
    lookup = {record["id"]: record for record in records}
    coverage = {}
    for name, rows in (("training", training), ("validation", validation)):
        write_json(context.outputs[f"original_{name}"], rows)
        transformed, coverage[name] = transform_rows(rows, lookup)
        write_json(context.outputs[name], transformed)
    write_json(
        context.outputs["audit"],
        {
            "source_inputs": config.input_sha256,
            "training_capture": manifest,
            "validation_capture": fresh,
            "generation_policy": fresh_policy,
            "fidelity_gate": gate,
            "coverage": coverage,
            "source_groups": {
                "training": len({row["group_id"] for row in training}),
                "validation": len({row["group_id"] for row in validation}),
            },
            "training_available_records": len(values["training_records"]),
            "selected_records": len(records),
            "training_selection": "Original comparisons whose two canonical passage-condition identities are in completed capture batches; labels and predictions do not select rows.",
            "validation_selection": "The 30 disjoint source pairs selected before the frozen v2 fidelity audit; no judgment-based answer filtering.",
            "limitations": "This model-assisted audit sample was used during development and is reused for epoch selection. It is a small development triage, not independent confirmation or test eligibility.",
            "test_inputs_opened": False,
        },
    )
    emit(
        "subset_inputs_prepared",
        training_comparisons=len(training),
        validation_comparisons=len(validation),
        completed_training_answers=len(values["training_records"]),
    )


def promising(candidate: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    """A provisional continuation signal; missing ordering cannot authorize test."""
    rank, native_rank = candidate["spearman"], native["spearman"]
    gain = None if rank is None or native_rank is None else rank - native_rank
    candidate_fpr = candidate["operating_point"]["false_positive_rate"]
    native_fpr = native["operating_point"]["false_positive_rate"]
    fpr = (
        None
        if candidate_fpr is None or native_fpr is None
        else candidate_fpr - native_fpr
    )
    return {
        "promising_for_full_generation": bool(
            gain is not None
            and gain >= 0.005 - 1e-12
            and fpr is not None
            and fpr <= 0.01 + 1e-12
        ),
        "spearman_change": gain,
        "false_positive_rate_change": fpr,
        "condition_ordering_measured": candidate["condition_changes"]["n"] > 0,
        "test_eligible": False,
        "interpretation": "Provisional point-estimate screen on 30 development pairs; one false positive can move the rate substantially. Full validation is still required.",
    }


def run(root: Path, parent_root: Path, name: str, training_records: Path) -> None:
    """Run frozen scoring and one weight-only LoRA trial, without test access."""
    root, parent_root = root.resolve(strict=True), parent_root.resolve(strict=True)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal native stages locally before asynchronous promotion.")
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("Use a single new attempt-directory name.")
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
        raise ValueError("Selected parent checkpoint differs.")
    paths = {
        "training": settings["splits"]["training"]["path"],
        "validation": settings["splits"]["validation"]["path"],
        "training_records": relative_input(root, training_records),
        "training_manifest": relative_input(
            root,
            training_records.with_name("proposition_subset_training_manifest.json"),
        ),
        "left": str(AUDIT / "proposition_fresh60_left.json"),
        "right": str(AUDIT / "proposition_fresh60_right.json"),
        "fresh_records": str(AUDIT / "proposition_fresh60_records.json"),
        "fresh_manifest": str(AUDIT / "proposition_fresh60_manifest.json"),
        "gate": str(AUDIT / "fresh_gate.json"),
    }
    paths = {key: relative_input(root, Path(path)) for key, path in paths.items()}
    hashes = {key: file_sha256(root / path) for key, path in paths.items()}
    for split in ("training", "validation"):
        if hashes[split] != settings["splits"][split]["sha256"]:
            raise ValueError(f"Original {split} source bytes differ.")
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
        "runs": [],
        "source_inputs": hashes,
        "parent_model_sha256": MODEL_SHA256,
        "baseline_rerun": False,
        "test_inputs_opened": False,
        "subset_triage_only": True,
    }
    summary_path = directory / "summary.json"
    write_json(summary_path, summary)

    def execute(
        stage_name: str, configured: Any, gpu: bool, timeout: int
    ) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_subset_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
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
                f"Native subset stage failed: {stage_name}; {result.path}"
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        return record

    try:
        prepared = execute(
            "prepare",
            stage(
                prepare_subset,
                stage_id="prepare",
                config=SubsetPreparationConfig(input_sha256=hashes),
                inputs=tuple(
                    input(key, path=path, data_role="training")
                    for key, path in paths.items()
                ),
                outputs=StageOutputs(
                    **{
                        key: output(
                            path=f"{key}.json", loader=load_json, data_role="training"
                        )
                        for key in (
                            "training",
                            "validation",
                            "original_training",
                            "original_validation",
                            "audit",
                        )
                    }
                ),
                reuse="never",
            ),
            False,
            1200,
        )
        audit = load_json(artifact_path(prepared, "prepare", "audit", "audit.json"))
        summary["preparation"] = audit
        write_json(directory / "preparation_audit.json", audit)
        transformed = {
            split: artifact_path(prepared, "prepare", split, f"{split}.json")
            for split in ("training", "validation")
        }
        original_validation = artifact_path(
            prepared, "prepare", "original_validation", "original_validation.json"
        )
        zero = execute(
            "epoch_zero",
            stage(
                infer,
                stage_id="infer",
                config=PropositionInferenceConfig(
                    **settings["encoder"],
                    parent_model_sha256=MODEL_SHA256,
                    original_rows_sha256=file_sha256(original_validation),
                    transformed_rows_sha256=file_sha256(transformed["validation"]),
                    baseline_sha256=file_sha256(baseline_path),
                ),
                inputs=(
                    input("model", source=artifact_source(parent, "train", "model")),
                    input(
                        "original_rows",
                        source=artifact_source(
                            prepared, "prepare", "original_validation"
                        ),
                    ),
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
                    **{
                        key: output(
                            path=f"{key}.json", loader=load_json, data_role="eval"
                        )
                        for key in ("predictions", "result", "timing")
                    }
                ),
                reuse="never",
            ),
            True,
            1800,
        )
        initial = load_json(artifact_path(zero, "infer", "result", "result.json"))
        summary["epoch_zero"] = initial
        summary["epoch_zero_cache_release"] = release_verified_model_cache(
            root, model_path, directory / "epoch_zero_cache_release.json"
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
        outputs = {
            key: output(path=filename, loader=loader, data_role="training")
            for key, filename, loader in (
                ("model", "model.pt", load_model),
                ("last_model", "model.pt", load_model),
                ("resume_state", "resume.pt", load_state),
                ("trace", "trace.json", load_json),
                ("validation_predictions", "predictions.json", load_json),
                ("warm_start", "warm_start.json", load_json),
            )
        }
        trained = execute(
            "fit",
            stage(
                fit_proposition_lora,
                stage_id="train",
                config=fit,
                inputs=(
                    input("initial_model", source=artifact_source(parent, "train", "model")),
                    *(
                        input(split, source=artifact_source(prepared, "prepare", split))
                        for split in ("training", "validation")
                    ),
                ),
                outputs=TrainOutputs(**outputs),
                metrics=measures,
                objective=maximize(measures[-1]),
                reuse="never",
            ),
            True,
            15000,
        )
        trace = load_json(artifact_path(trained, "train", "trace", "trace.json"))
        selected = trace["selected"]
        if (
            file_sha256(artifact_path(trained, "train", "model", "model.pt"))
            != selected["sha256"]
        ):
            raise ValueError("The selected subset model differs from its trace.")
        rows = load_json(original_validation)
        scored = original_predictions(
            rows,
            load_json(transformed["validation"]),
            load_json(
                artifact_path(
                    trained, "train", "validation_predictions", "predictions.json"
                )
            ),
        )
        if summarize(scored) != selected["validation"]:
            raise ValueError("The selected subset predictions differ from their trace.")
        native = initial["metrics"]["saved_qwen"]
        identities = {row["row_id"] for row in rows}
        baseline = baseline_scores(
            rows,
            [row for row in load_json(baseline_path) if row["row_id"] in identities],
        )
        if arm_metrics(rows, baseline, recall_cutoff(rows, baseline)) != native:
            raise ValueError("The saved comparator differs across subset stages.")
        predictions = np.asarray([row["prediction"] for row in scored])
        adapted = arm_metrics(
            rows,
            predictions,
            recall_cutoff(
                rows, predictions, recall=native["operating_point"]["recall"] - 1e-12
            ),
        )
        metrics = {
            "saved_qwen": native,
            "epoch_zero": initial["metrics"]["propositions"],
            "adapted": adapted,
        }
        screening = {
            arm: promising(metrics[arm], native) for arm in ("epoch_zero", "adapted")
        }
        result = {
            "metrics": metrics,
            "screening": screening,
            "promising_for_full_generation": any(
                value["promising_for_full_generation"] for value in screening.values()
            ),
            "training_comparisons": audit["coverage"]["training"]["comparisons"],
            "validation_comparisons": len(rows),
            "source_groups": audit["source_groups"],
            "coverage": audit["coverage"],
            "completed_training_answers": audit["training_available_records"],
            "selected_training_epoch": selected["epoch"],
            "selected_training_step": selected["step"],
            "completed_epochs": len(trace["epochs"]),
            "actual_updates": trace["actual_updates"],
            "stop_reason": trace["stop_reason"],
            "subset_triage_only": True,
            "test_eligible": False,
            "test_inputs_opened": False,
            "full_generation_automatically_resumed": False,
            "limitations": audit["limitations"],
        }
        write_json(directory / "trained_trace.json", trace)
        write_json(directory / "adapted_original_predictions.json", scored)
        write_json(directory / "result.json", result)
        summary.update(status="complete", in_flight=None, result=result)
        write_json(summary_path, summary)
        emit("subset_triage_complete", **result)
    except Exception as error:
        summary.update(status="failed", error=str(error))
        write_json(summary_path, summary)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--training-records",
        type=Path,
        default=Path("csts_data/proposition_subset_training_records.json"),
    )
    args = parser.parse_args()
    with (args.parent_root / ".viper/overnight_gpu.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        run(args.root, args.parent_root, args.name, args.training_records)
