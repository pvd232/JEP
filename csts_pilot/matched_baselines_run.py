"""Run the frozen-encoder matched-baseline study through native VIPER stages."""

import argparse
import fcntl
import json
import math
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field
from viper import execution
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
from viper.config import BuildConfig, EvalConfig, MetricConfig
from viper.metrics import FloatComparator, MetricContext, MetricDependency, measure
from viper.metrics import max as maximize
from viper.metrics import metric as declare_metric
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef, ResolvedRunRef
from viper.repository import read_source
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)
from viper.stages import StageContext, build, eval
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.background_storage import queue_publication
from csts_pilot.condition_reference import arm_metrics, paired_bootstrap, recall_cutoff
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
)
from csts_pilot.convergence_run import artifact_path, check_inputs
from csts_pilot.diagnostics import summarize
from csts_pilot.matched_baselines import (
    ARMS,
    MODEL_SHA256,
    ExtractionConfig,
    HeadConfig,
    PreparationConfig,
    emit,
    extract,
    fit_head,
    prepare,
    scores_from_cache,
    select_candidates,
    validate_cache_rows,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs

FITTED_ARMS = ARMS[1:]


def save_json(path: Path, value: Any) -> None:
    """Atomically replace one controller record after its complete contents exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def stored_source(
    record: dict[str, Any],
    stage_id: str,
    artifact_name: str,
    binding: str,
    role: Literal["training", "eval"] = "training",
) -> Any:
    """Give every stored artifact a unique materialization path for its binding."""
    return run_artifact(
        ResolvedRunRef.model_validate(record["reference"]),
        StageArtifactRef(stage_id=stage_id, artifact_name=artifact_name),
        path=f"inputs/{binding}",
        data_role=role,
    )


def scored_rows(rows: list[dict[str, Any]], values: Any) -> list[dict[str, Any]]:
    """Attach exactly one finite prediction to each original comparison."""
    result = [
        dict(row, prediction=float(value))
        for row, value in zip(rows, values, strict=True)
    ]
    if not all(math.isfinite(row["prediction"]) for row in result):
        raise ValueError("A scorer returned a nonfinite prediction.")
    return result


def check_predictions(
    rows: list[dict[str, Any]], predictions: list[dict[str, Any]]
) -> None:
    """Require exact comparison identities, contents, multiplicity, and order."""
    if len(rows) != len(predictions) or any(
        {k: v for k, v in prediction.items() if k != "prediction"} != row
        for row, prediction in zip(rows, predictions, strict=True)
    ):
        raise ValueError("Predictions differ from the complete input cohort.")
    scored_rows(rows, [row["prediction"] for row in predictions])


class SelectionConfig(BuildConfig):
    """Bind validation selection to the parent, bank, and captured feature bytes."""

    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def load_saved_baseline(context: Any) -> tuple[list[dict[str, Any]], list[float]]:
    """Read the sealed comparator and require the original validation identities."""
    if file_sha256(context.inputs["validation"]) != context.config.validation_sha256:
        raise ValueError("Changed validation cohort.")
    rows = load_json(context.inputs["validation"])
    previous = load_json(context.inputs["native_predictions"])
    check_predictions(rows, previous)
    return rows, [row["prediction"] for row in previous]


@build(config=SelectionConfig)
def freeze_selection(context: StageContext[SelectionConfig]) -> None:
    """Freeze all head identities and validation cutoffs before test input access."""
    config = context.config
    rows, native = load_saved_baseline(context)
    for name, digest in (
        ("cache", config.validation_cache_sha256),
        ("bank", config.bank_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed selection input: {name}.")
    cache = load_model(context.inputs["cache"])
    validate_cache_rows(cache, rows)
    for key, expected in (
        ("model_sha256", config.model_sha256),
        ("bank_sha256", config.bank_sha256),
        ("rows_sha256", config.validation_sha256),
    ):
        if cache[key] != expected:
            raise ValueError(f"Selected feature provenance differs: {key}.")
    values = {"native_direct": native}
    models, identities, matched = {}, {}, None
    for arm in FITTED_ARMS:
        model = load_model(context.inputs[f"model_{arm}"])
        if model["config"]["arm"] != arm:
            raise ValueError("A head checkpoint is bound under a different arm name.")
        for key, expected in (
            ("model_sha256", config.model_sha256),
            ("bank_sha256", config.bank_sha256),
            ("validation_sha256", config.validation_sha256),
            ("validation_cache_sha256", config.validation_cache_sha256),
        ):
            if model["config"][key] != expected:
                raise ValueError(f"Selected head provenance differs: {arm}/{key}.")
        captured = load_json(context.inputs[f"predictions_{arm}"])
        trace = load_json(context.inputs[f"trace_{arm}"])
        check_predictions(rows, captured)
        reproduced = scores_from_cache(model, cache, device="cpu")
        if (
            max(
                abs(a - b["prediction"])
                for a, b in zip(reproduced, captured, strict=True)
            )
            > 1e-5
        ):
            raise ValueError(
                f"Selected head and captured validation predictions disagree: {arm}."
            )
        signature = tuple(
            trace[key]
            for key in ("initial_head_sha256", "head_fit_ids_sha256", "training_rows")
        )
        if matched is not None and signature != matched:
            raise ValueError(
                "Heads differ in initialization or fitted comparison cohort."
            )
        matched = signature
        values[arm], models[arm] = reproduced, model
        identities[arm] = {
            "model_sha256": file_sha256(context.inputs[f"model_{arm}"]),
            "predictions_sha256": file_sha256(context.inputs[f"predictions_{arm}"]),
            "trace_sha256": file_sha256(context.inputs[f"trace_{arm}"]),
            "initial_head_sha256": trace["initial_head_sha256"],
            "head_fit_ids_sha256": trace["head_fit_ids_sha256"],
            "training_rows": trace["training_rows"],
        }
    metrics = {
        name: arm_metrics(
            rows, np.asarray(scores), recall_cutoff(rows, np.asarray(scores))
        )
        for name, scores in values.items()
    }
    decision = select_candidates(metrics)
    selection = {
        **decision,
        "status": "validation_frozen",
        "metrics": metrics,
        "heads": identities,
        "model_sha256": config.model_sha256,
        "bank_sha256": config.bank_sha256,
        "validation_sha256": config.validation_sha256,
        "validation_cache_sha256": config.validation_cache_sha256,
        "native_predictions_sha256": file_sha256(context.inputs["native_predictions"]),
    }
    save_json(context.outputs["selection"], selection)
    torch.save(
        {
            "models": models,
            "model_sha256": config.model_sha256,
            "bank_sha256": config.bank_sha256,
        },
        context.outputs["models"],
    )
    save_json(
        context.outputs["predictions"],
        {name: scored_rows(rows, scores) for name, scores in values.items()},
    )
    for arm, result in metrics.items():
        emit("validation_result", arm=arm, **result)
    emit("validation_selection", **decision)


class PredictionConfig(BuildConfig):
    """Bind CPU head prediction to the frozen validation selection and test cache."""

    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    models_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@build(config=PredictionConfig)
def capture_test(context: StageContext[PredictionConfig]) -> None:
    """Capture the candidate and reuse the sealed native test comparator."""
    config = context.config
    for name, digest in (
        ("test", config.rows_sha256),
        ("cache", config.cache_sha256),
        ("model", config.models_sha256),
        ("selection", config.selection_sha256),
        ("bank", config.bank_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed frozen prediction input: {name}.")
    rows, cache = load_json(context.inputs["test"]), load_model(context.inputs["cache"])
    validate_cache_rows(cache, rows)
    for key, expected in (
        ("model_sha256", config.model_sha256),
        ("bank_sha256", config.bank_sha256),
        ("rows_sha256", config.rows_sha256),
    ):
        if cache[key] != expected:
            raise ValueError(f"Test feature provenance differs: {key}.")
    selection, bundle = (
        load_json(context.inputs["selection"]),
        load_model(context.inputs["model"]),
    )
    selected = selection["selected_arm"]
    if selected not in set(FITTED_ARMS) or selection["test_scores_used_for_selection"]:
        raise ValueError(
            "Test prediction requires a frozen eligible validation candidate."
        )
    if (
        bundle["model_sha256"] != config.model_sha256
        or bundle["bank_sha256"] != config.bank_sha256
    ):
        raise ValueError(
            "Head bundle provenance differs from the configured parent or bank."
        )
    previous = load_json(context.inputs["native_predictions"])
    check_predictions(rows, previous)
    values = {
        "native_direct": [row["prediction"] for row in previous],
        "candidate": scores_from_cache(bundle["models"][selected], cache, device="cpu"),
    }
    result = {
        "selected_arm": selected,
        "predictions": {
            name: scored_rows(rows, scores) for name, scores in values.items()
        },
    }
    save_json(context.outputs["predictions"], result)
    save_json(
        context.outputs["timing"],
        {
            **config.model_dump(),
            "predictions_sha256": file_sha256(context.outputs["predictions"]),
            "native_predictions_sha256": file_sha256(
                context.inputs["native_predictions"]
            ),
            "optimizer_updates": 0,
            "rows": len(rows),
        },
    )
    emit("test_predictions_captured", selected_arm=selected, rows=len(rows))


class EvaluationConfig(EvalConfig):
    """Verify frozen snapshots and recompute every test comparison on CPU."""

    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    models_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bootstrap_draws: int = 2000
    bootstrap_seed: int = 61024


@declare_metric(metric_id="matched_baseline_test_spearman", mode="stateless")
def selected_test_spearman(context: MetricContext[MetricConfig]) -> float:
    """Calculate the selected method's Spearman in the separate metric worker."""
    value = summarize(
        load_json(context.artifacts["predictions"])["predictions"]["candidate"]
    )["spearman"]
    if value is None or not math.isfinite(value):
        raise ValueError("The selected test correlation is undefined.")
    return float(value)


@eval(config=EvaluationConfig)
def evaluate(context: StageContext[EvaluationConfig]) -> None:
    """Recompute held-out metrics and fixed-cutoff paired source-group intervals."""
    config = context.config
    for name, digest in (
        ("test", config.rows_sha256),
        ("model", config.models_sha256),
        ("selection", config.selection_sha256),
        ("bank", config.bank_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed evaluation input: {name}.")
    rows, selection = (
        load_json(context.inputs["test"]),
        load_json(context.inputs["selection"]),
    )
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Evaluation indices differ from the complete frozen cohort.")
    snapshot, binding = (
        load_json(context.inputs["snapshot_predictions"]),
        load_json(context.inputs["snapshot_timing"]),
    )
    if binding["predictions_sha256"] != file_sha256(
        context.inputs["snapshot_predictions"]
    ) or any(
        binding[key] != getattr(config, key)
        for key in ("rows_sha256", "models_sha256", "selection_sha256", "bank_sha256")
    ):
        raise ValueError(
            "Prediction snapshot identities differ from evaluation bindings."
        )
    selected = selection["selected_arm"]
    if snapshot["selected_arm"] != selected:
        raise ValueError("Test capture uses a different validation-selected method.")
    expected = {"native_direct", "candidate"}
    if set(snapshot["predictions"]) != expected:
        raise ValueError(
            "The test snapshot must contain the saved native comparator and candidate."
        )
    thresholds = dict(selection["thresholds"])
    thresholds["candidate"] = thresholds[selected]
    metrics, scores = {}, {}
    for name, predictions in snapshot["predictions"].items():
        check_predictions(rows, predictions)
        scores[name] = np.asarray([row["prediction"] for row in predictions])
        metrics[name] = arm_metrics(rows, scores[name], thresholds[name])
        emit("test_result", arm=name, selected_arm=selected, **metrics[name])
    candidate, transfer = metrics["candidate"], {}
    for control in ("native_direct",):
        baseline = metrics[control]
        differences: dict[str, Any] = {
            "spearman": candidate["spearman"] - baseline["spearman"],
            "mse": candidate["mse_0_1"] - baseline["mse_0_1"],
            "false_positive_rate": candidate["operating_point"]["false_positive_rate"]
            - baseline["operating_point"]["false_positive_rate"],
            "recall": candidate["operating_point"]["recall"]
            - baseline["operating_point"]["recall"],
            "condition_ordering": candidate["condition_changes"]["accuracy_ties_half"]
            - baseline["condition_changes"]["accuracy_ties_half"],
        }
        differences["passes"] = (
            differences["spearman"] >= 0.005 - 1e-12
            and differences["false_positive_rate"] <= 0.01 + 1e-12
            and differences["recall"] >= -0.01 - 1e-12
            and differences["condition_ordering"] >= -0.01 - 1e-12
        )
        differences["paired_intervals"] = paired_bootstrap(
            rows,
            {"A": scores[control], "candidate": scores["candidate"]},
            {"A": thresholds[control], "candidate": thresholds["candidate"]},
            config.bootstrap_draws,
            config.bootstrap_seed,
        )
        transfer[control] = differences
    shutil.copyfile(
        context.inputs["snapshot_predictions"], context.outputs["predictions"]
    )
    save_json(
        context.outputs["report"],
        {
            "selected_arm": selected,
            "metrics": metrics,
            "native_test_predictions_sha256": binding["native_predictions_sha256"],
            "comparisons": transfer,
            "passes": all(comparison["passes"] for comparison in transfer.values()),
            "selection_sha256": config.selection_sha256,
            "thresholds_fixed_from_validation": True,
            "test_sha256": config.rows_sha256,
        },
    )


def validate_settings(settings: dict[str, Any]) -> None:
    """Reject unreviewed arm, encoder, coefficient, or exposure changes."""
    if (
        settings["arms"] != list(FITTED_ARMS)
        or settings["model_sha256"] != MODEL_SHA256
    ):
        raise ValueError("Keep the four alternative arms and selected parent identity.")
    if settings["bank"] != {"bank_size": 16, "seed": 7}:
        raise ValueError("Use the common 16-source-group training bank and fixed seed.")
    required = {
        "seed": 7,
        "output_dim": 512,
        "dropout": 0.15,
        "learning_rate": 0.001,
        "weight_decay": 0.01,
        "batch_size": 32,
        "max_epochs": 48,
        "patience": 5,
        "max_seconds": 600,
    }
    if any(settings["training"].get(key) != value for key, value in required.items()):
        raise ValueError("The matched head-fitting settings changed.")
    ExtractionConfig(
        **settings["encoder"],
        rows_sha256="0" * 64,
        bank_sha256="0" * 64,
        model_sha256=MODEL_SHA256,
        split="validation",
    )
    PreparationConfig(
        **settings["bank"],
        training_sha256=settings["splits"]["training"]["sha256"],
        validation_sha256=settings["splits"]["validation"]["sha256"],
    )
    for arm in FITTED_ARMS:
        HeadConfig(
            **settings["training"],
            arm=arm,
            **{
                key: "0" * 64
                for key in (
                    "training_sha256",
                    "validation_sha256",
                    "bank_sha256",
                    "model_sha256",
                    "training_cache_sha256",
                    "validation_cache_sha256",
                )
            },
        )


def run(root: Path, name: str, preflight: bool = False) -> None:
    """Execute only after resolving every runtime binding to sealed stage outputs."""
    root = root.resolve(strict=True)
    if name in {"", ".", ".."} or Path(name).name != name:
        raise ValueError("An attempt name must be one nonempty path component.")
    settings_path = root / "configs/csts-tranche-5.json"
    settings = load_json(settings_path)
    validate_settings(settings)
    check_inputs(root, settings)
    original = load_json(root / "qwen_evidence_results/initial/summary.json")
    parent = next(
        record for record in original["runs"] if record["name"] == "ratings_ratings"
    )
    if file_sha256(artifact_path(parent, "train", "model", "model.pt")) != MODEL_SHA256:
        raise ValueError("The selected parent checkpoint bytes differ from the plan.")
    saved_validation = artifact_path(
        parent, "train", "validation_predictions", "predictions.json"
    )
    check_predictions(
        load_json(root / settings["splits"]["validation"]["path"]),
        load_json(saved_validation),
    )
    emit(
        "saved_baseline_identity_checked",
        validation_sha256=settings["splits"]["validation"]["sha256"],
        predictions_sha256=file_sha256(saved_validation),
    )
    source = read_source(root)
    if preflight:
        emit(
            "preflight_passed",
            source_commit=source.commit,
            model_sha256=MODEL_SHA256,
            arms=list(FITTED_ARMS),
            inference_started=False,
            training_started=False,
            scope="settings, data hashes/cohorts, configuration schemas and parent identity; stored output bindings are resolved before each native stage",
        )
        return
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Use local native sealing before asynchronous cloud promotion.")
    directory = root / "matched_baseline_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "summary.json"
    if path.exists():
        raise FileExistsError(
            "Preserve the existing attempt and reconcile it before recovery."
        )
    events = directory / "events.jsonl"
    events.touch(exist_ok=False)
    os.environ["CSTS_TRANCHE5_EVENTS"] = str(events)
    environment, trusted = observe_python_env(), frozenset({str(source.repository)})
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "attempt": uuid.uuid4().hex[:8],
        "settings_sha256": file_sha256(settings_path),
        "model_sha256": MODEL_SHA256,
        "runs": [],
        "in_flight": None,
        "resource_seconds": {},
        "events_path": str(events),
        "backbone_optimizer_updates": 0,
    }
    save_json(path, summary)

    def execute(
        label: str,
        configured: Any,
        resource: str = "analysis",
        limit: float | None = None,
    ) -> dict[str, Any]:
        budget_key = {
            "extraction": "extraction_seconds",
            "test_extraction": "test_extraction_seconds",
            "heads": None,
            "analysis": "analysis_seconds",
        }[resource]
        ceiling = (
            2400.0 if resource == "heads" else float(settings["budgets"][budget_key])
        )
        used = summary["resource_seconds"].get(resource, 0.0)
        allowance = min(ceiling - used, limit if limit is not None else ceiling)
        if allowance <= 0:
            raise TimeoutError(f"The declared {resource} allowance is exhausted.")
        trial = experiment(
            experiment_id=f"csts_matched_{source.commit[:8]}_{summary['attempt']}_{label}",
            variants=(
                variant(
                    label,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["in_flight"] = {"name": label, "experiment_id": trial.experiment_id}
        save_json(path, summary)
        emit("stage_started", stage=label, resource=resource)
        gpu = resource in {"extraction", "test_extraction", "heads"}
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
                timeout_seconds=max(1, int(allowance)),
                trusted_source_repositories=trusted,
            )
        finally:
            summary["resource_seconds"][resource] = used + time.monotonic() - started
            save_json(path, summary)
        record = {
            "name": label,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        save_json(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native stage failed: {label}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        save_json(path, summary)
        emit("stage_complete", stage=label, seconds=record["seconds"])
        return record

    try:
        preparation = execute(
            "prepare",
            stage(
                prepare,
                stage_id="prepare",
                config=PreparationConfig(
                    **settings["bank"],
                    training_sha256=settings["splits"]["training"]["sha256"],
                    validation_sha256=settings["splits"]["validation"]["sha256"],
                ),
                inputs=tuple(
                    input(
                        key, path=settings["splits"][key]["path"], data_role="training"
                    )
                    for key in ("training", "validation")
                ),
                outputs=StageOutputs(
                    bank=output(
                        path="bank.json", loader=load_json, data_role="training"
                    ),
                    audit=output(
                        path="audit.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            ),
        )
        bank_sha = file_sha256(
            artifact_path(preparation, "prepare", "bank", "bank.json")
        )
        summary["bank_sha256"] = bank_sha
        save_json(path, summary)
        extracted = {}

        def extract_split(split: str) -> dict[str, Any]:
            spec = settings["splits"][split]
            resource = "test_extraction" if split == "test" else "extraction"
            remaining = settings["budgets"][resource + "_seconds"] - summary[
                "resource_seconds"
            ].get(resource, 0.0)
            return execute(
                f"extract_{split}",
                stage(
                    extract,
                    stage_id="extract",
                    config=ExtractionConfig(
                        **settings["encoder"],
                        model_sha256=MODEL_SHA256,
                        rows_sha256=spec["sha256"],
                        bank_sha256=bank_sha,
                        split=split,
                        max_seconds=max(1, remaining),
                    ),
                    inputs=(
                        input(
                            "model",
                            source=stored_source(parent, "train", "model", "model"),
                        ),
                        input(
                            "rows",
                            path=spec["path"],
                            data_role="eval" if split == "test" else "training",
                        ),
                        input(
                            "bank",
                            source=stored_source(
                                preparation, "prepare", "bank", "bank"
                            ),
                        ),
                    ),
                    outputs=StageOutputs(
                        cache=output(
                            path="cache.pt",
                            loader=load_model,
                            data_role="eval" if split == "test" else "training",
                        ),
                        timing=output(
                            path="timing.json",
                            loader=load_json,
                            data_role="eval" if split == "test" else "training",
                        ),
                    ),
                    reuse="never",
                ),
                resource,
            )

        for split in ("training", "validation"):
            extracted[split] = extract_split(split)
        caches = {
            split: artifact_path(record, "extract", "cache", "cache.pt")
            for split, record in extracted.items()
        }
        selection_config = SelectionConfig(
            model_sha256=MODEL_SHA256,
            bank_sha256=bank_sha,
            validation_sha256=settings["splits"]["validation"]["sha256"],
            validation_cache_sha256=file_sha256(caches["validation"]),
        )
        baseline_inputs = (
            input(
                "validation",
                path=settings["splits"]["validation"]["path"],
                data_role="training",
            ),
            input(
                "cache",
                source=stored_source(
                    extracted["validation"], "extract", "cache", "cache"
                ),
            ),
            input("bank", source=stored_source(preparation, "prepare", "bank", "bank")),
            input(
                "native_predictions",
                source=stored_source(
                    parent, "train", "validation_predictions", "native_predictions"
                ),
            ),
        )
        heads = {}
        metrics = tuple(
            measure(metric)
            for metric in (training_objective, validation_mse, validation_spearman)
        )
        for arm in FITTED_ARMS:
            heads[arm] = execute(
                f"train_{arm}",
                stage(
                    fit_head,
                    stage_id="train",
                    config=HeadConfig(
                        **settings["training"],
                        arm=arm,
                        training_sha256=settings["splits"]["training"]["sha256"],
                        validation_sha256=settings["splits"]["validation"]["sha256"],
                        bank_sha256=bank_sha,
                        model_sha256=MODEL_SHA256,
                        training_cache_sha256=file_sha256(caches["training"]),
                        validation_cache_sha256=file_sha256(caches["validation"]),
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
                        input(
                            "bank",
                            source=stored_source(
                                preparation, "prepare", "bank", "bank"
                            ),
                        ),
                        input(
                            "training_cache",
                            source=stored_source(
                                extracted["training"],
                                "extract",
                                "cache",
                                "training_cache",
                            ),
                        ),
                        input(
                            "validation_cache",
                            source=stored_source(
                                extracted["validation"],
                                "extract",
                                "cache",
                                "validation_cache",
                            ),
                        ),
                    ),
                    outputs=TrainOutputs(
                        model=output(
                            path="model.pt", loader=load_model, data_role="training"
                        ),
                        resume_state=output(
                            path="resume.pt", loader=load_state, data_role="training"
                        ),
                        trace=output(
                            path="trace.json", loader=load_json, data_role="training"
                        ),
                        validation_predictions=output(
                            path="predictions.json",
                            loader=load_json,
                            data_role="training",
                        ),
                    ),
                    metrics=metrics,
                    objective=maximize(metrics[-1]),
                    reuse="never",
                ),
                "heads",
                limit=600,
            )
            saved_head = load_model(
                artifact_path(heads[arm], "train", "model", "model.pt")
            )
            emit(
                "matched_head_complete",
                arm=arm,
                selected_epoch=saved_head["epoch"],
                alpha=saved_head["alpha"],
                validation=saved_head["validation"],
                native_run=heads[arm]["reference"],
            )
        selection_inputs = list(baseline_inputs)
        for arm, record in heads.items():
            for artifact, binding in (
                ("model", f"model_{arm}"),
                ("validation_predictions", f"predictions_{arm}"),
                ("trace", f"trace_{arm}"),
            ):
                selection_inputs.append(
                    input(
                        binding,
                        source=stored_source(record, "train", artifact, binding),
                    )
                )
        selection_run = execute(
            "freeze_selection",
            stage(
                freeze_selection,
                stage_id="selection",
                config=selection_config,
                inputs=tuple(selection_inputs),
                outputs=StageOutputs(
                    selection=output(
                        path="selection.json", loader=load_json, data_role="training"
                    ),
                    models=output(
                        path="models.pt", loader=load_model, data_role="training"
                    ),
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            ),
        )
        selection_path = artifact_path(
            selection_run, "selection", "selection", "selection.json"
        )
        selection = load_json(selection_path)
        summary["selection"] = selection
        summary["selection_sha256"] = file_sha256(selection_path)
        shutil.copyfile(selection_path, directory / "selection.json")
        save_json(path, summary)
        if selection["selected_arm"] is None:
            summary.update(
                status="complete",
                stop_reason="no_validation_candidate_eligible",
                publication_status="queued_separately",
            )
            save_json(path, summary)
            emit("study_complete", stop_reason=summary["stop_reason"])
            return
        extracted["test"] = extract_split("test")
        test_spec = settings["splits"]["test"]
        indices = directory / "test_indices.json"
        save_json(indices, list(range(test_spec["rows"])))
        published = execute(
            "publish_test",
            stage(
                publish_evaluation_inputs,
                stage_id="publish",
                inputs=(
                    input("test", path=test_spec["path"], data_role="eval"),
                    input(
                        "holdout", path=str(indices.relative_to(root)), data_role="eval"
                    ),
                ),
                outputs=StageOutputs(
                    test=output(path="test.json", loader=load_json, data_role="eval"),
                    holdout=output(
                        path="indices.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
        )
        test_cache_sha = file_sha256(
            artifact_path(extracted["test"], "extract", "cache", "cache.pt")
        )
        models_sha = file_sha256(
            artifact_path(selection_run, "selection", "models", "models.pt")
        )
        common = (
            input(
                "test",
                source=stored_source(published, "publish", "test", "test", "eval"),
            ),
            input(
                "model",
                source=stored_source(selection_run, "selection", "models", "model"),
            ),
            input(
                "selection",
                source=stored_source(
                    selection_run, "selection", "selection", "selection"
                ),
            ),
            input("bank", source=stored_source(preparation, "prepare", "bank", "bank")),
        )
        capture = execute(
            "capture_test",
            stage(
                capture_test,
                stage_id="capture",
                config=PredictionConfig(
                    model_sha256=MODEL_SHA256,
                    bank_sha256=bank_sha,
                    rows_sha256=test_spec["sha256"],
                    cache_sha256=test_cache_sha,
                    models_sha256=models_sha,
                    selection_sha256=summary["selection_sha256"],
                ),
                inputs=common
                + (
                    input(
                        "cache",
                        source=stored_source(
                            extracted["test"], "extract", "cache", "cache", "eval"
                        ),
                    ),
                    input(
                        "native_predictions",
                        source=stored_source(
                            next(
                                record
                                for record in original["runs"]
                                if record["name"] == "predict_ratings"
                            ),
                            "predict",
                            "predictions",
                            "native_predictions",
                            "eval",
                        ),
                    ),
                ),
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
        )
        measured = measure(
            selected_test_spearman,
            dependencies=(
                MetricDependency(
                    source="artifact", name="predictions", data_role="eval"
                ),
            ),
            comparator=FloatComparator(mode="absolute", tolerance=1e-12),
        )
        evaluated = execute(
            "evaluate_test",
            stage(
                evaluate,
                stage_id="evaluate",
                eval_id="csts_matched_baselines",
                config=EvaluationConfig(
                    rows_sha256=test_spec["sha256"],
                    models_sha256=models_sha,
                    selection_sha256=summary["selection_sha256"],
                    bank_sha256=bank_sha,
                    bootstrap_draws=settings["bootstrap_draws"],
                    bootstrap_seed=settings["bootstrap_seed"],
                ),
                inputs=common
                + (
                    input(
                        "holdout",
                        source=stored_source(
                            published, "publish", "holdout", "holdout", "eval"
                        ),
                    ),
                    input(
                        "snapshot_predictions",
                        source=stored_source(
                            capture,
                            "capture",
                            "predictions",
                            "snapshot_predictions",
                            "eval",
                        ),
                    ),
                    input(
                        "snapshot_timing",
                        source=stored_source(
                            capture, "capture", "timing", "snapshot_timing", "eval"
                        ),
                    ),
                ),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    report=output(
                        path="report.json", loader=load_json, data_role="eval"
                    ),
                ),
                metrics=(measured,),
                objective=maximize(measured),
                reuse="never",
            ),
        )
        report = artifact_path(evaluated, "evaluate", "report", "report.json")
        summary.update(
            status="complete",
            stop_reason="frozen_test_evaluated",
            test=load_json(report),
            publication_status="queued_separately",
        )
        shutil.copyfile(report, directory / "test_report.json")
        save_json(path, summary)
        emit(
            "study_complete",
            stop_reason=summary["stop_reason"],
            passes=summary["test"]["passes"],
        )
    except Exception as error:
        summary.update(
            status="failed", error_type=type(error).__name__, error=str(error)
        )
        save_json(path, summary)
        emit("study_failed", error_type=type(error).__name__, error=str(error))
        raise


def main() -> None:
    """Validate or execute one exclusive study attempt without overwriting prior work."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--name", default="initial")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        run(args.root, args.name, preflight=True)
        return
    if not args.execute:
        settings = load_json(args.root / "configs/csts-tranche-5.json")
        validate_settings(settings)
        emit(
            "configuration_only",
            settings=settings,
            inference_started=False,
            training_started=False,
            next_command="Use --preflight for input identity checks; --execute starts the reviewed study.",
        )
        return
    lock_path = args.root / ".viper" / "matched_baselines.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.root, args.name)


if __name__ == "__main__":
    main()
