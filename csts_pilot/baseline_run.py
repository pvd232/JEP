"""Prepare and run Tranche 2 baselines with explicit, separate execution phases."""

import argparse
import fcntl
import json
import re
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.metrics import min as minimize
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
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    ScoreConfig,
    encoder_settings,
)
from csts_pilot.baseline_stages import (
    cache_embeddings,
    capture_predictions,
    evaluate_baseline,
    fit_lora,
    fit_projection,
    fit_static,
    ranking_value,
)
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
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs

SCORER_ORDER = ("mean", "cosine", "ridge", "projection", "lora")


def fit_config(
    settings: dict[str, Any], kind: str, remaining_seconds: float | None = None
) -> FitConfig:
    """Combine the common representation with one scorer's declared optimizer."""
    values = {
        **settings["encoder"],
        "seed": settings["seed"],
        **settings["fits"].get(kind, {}),
        "kind": kind,
    }
    if remaining_seconds is not None:
        values["max_seconds"] = min(values.get("max_seconds", 1800), remaining_seconds)
    return FitConfig.model_validate(values)


def validate_settings(settings: dict[str, Any]) -> None:
    """Validate the displayed configuration before data access or model loading."""
    EncoderConfig.model_validate(settings["encoder"])
    for kind in ("mean", "cosine", "ridge", "projection", "lora"):
        if fit_config(settings, kind).seed != settings["seed"]:
            raise ValueError("All scorers must use the declared study seed.")
    for phase in ("frozen", "lora"):
        if settings["gpu_budget_seconds"][phase] <= 0:
            raise ValueError("Each phase requires a positive native GPU-stage ceiling.")
    if set(settings["splits"]) != {"training", "validation", "test"}:
        raise ValueError("Declare training, validation and test input identities.")


def training_stage(
    settings: dict[str, Any],
    kind: str,
    cache: dict[str, Any] | None,
    remaining_seconds: float,
    parent: dict[str, Any] | None = None,
) -> Any:
    """Bind training inputs and optional terminal state through native producer refs."""
    config = fit_config(settings, kind, remaining_seconds)
    inputs = [
        input(name, path=settings["splits"][name]["path"], data_role="training")
        for name in ("training", "validation")
    ]
    if cache is not None:
        inputs.append(
            input("embeddings", source=artifact_source(cache, "embed", "embeddings"))
        )
    if parent is not None:
        saved = load_model(artifact_path(parent, "train", "last_model", "model.pt"))
        config = config.model_copy(
            update={
                "start_epoch": saved["epoch"],
                "schedule": "constant",
                "warmup_fraction": 0.0,
            }
        )
        config = FitConfig.model_validate(config.model_dump())
        for name, artifact in (
            ("parent_last_model", "last_model"),
            ("parent_resume", "resume_state"),
            ("parent_trace", "trace"),
            ("parent_model", "model"),
            ("parent_validation_predictions", "validation_predictions"),
        ):
            inputs.append(
                input(name, source=artifact_source(parent, "train", artifact))
            )
    outputs = {
        "model": output(path="model.pt", loader=load_model, data_role="training"),
        "resume_state": output(
            path="resume.pt", loader=load_state, data_role="training"
        ),
        "trace": output(path="trace.json", loader=load_json, data_role="training"),
        "validation_predictions": output(
            path="predictions.json", loader=load_json, data_role="training"
        ),
    }
    implementation = fit_static
    if kind in {"projection", "lora"}:
        implementation = fit_projection if kind == "projection" else fit_lora
        outputs.update(
            last_model=output(path="model.pt", loader=load_model, data_role="training"),
            resume_state=output(
                path="resume.pt", loader=load_state, data_role="training"
            ),
        )
    metrics = (measure(validation_mse), measure(validation_spearman))
    if kind in {"projection", "lora"}:
        metrics = (measure(training_objective), *metrics)
    objective = minimize(metrics[0]) if kind == "mean" else maximize(metrics[-1])
    return stage(
        implementation,
        stage_id="train",
        config=config,
        inputs=tuple(inputs),
        outputs=TrainOutputs(**outputs),
        metrics=metrics,
        objective=objective,
        reuse="never",
    )


def freeze_selection(
    records: dict[str, dict[str, Any]], destination: Path, settings: dict[str, Any]
) -> dict[str, Any]:
    """Freeze every model and choose the provisional winner from validation alone."""
    candidates = {}
    for kind in SCORER_ORDER:
        if kind not in records:
            continue
        record = records[kind]
        model_path = artifact_path(record, "train", "model", "model.pt")
        saved = load_model(model_path)
        rows = load_json(
            artifact_path(record, "train", "validation_predictions", "predictions.json")
        )
        if saved["kind"] != kind:
            raise ValueError("A training run returned a different scorer identity.")
        if encoder_settings(
            FitConfig.model_validate(saved["config"])
        ) != encoder_settings(EncoderConfig.model_validate(settings["encoder"])):
            raise ValueError(
                "A selected scorer uses a different frozen representation."
            )
        from_diagnostics = saved.get("validation")
        if from_diagnostics is None:
            trace = load_json(artifact_path(record, "train", "trace", "trace.json"))
            from_diagnostics = trace["selected"]["validation"]
            if trace["selected"]["sha256"] != file_sha256(model_path):
                raise ValueError(
                    "The selected neural model differs from the epoch trace."
                )
        if summarize(rows) != from_diagnostics:
            raise ValueError(
                "Saved validation predictions differ from the selected metrics."
            )
        candidates[kind] = {
            "sha256": file_sha256(model_path),
            "run": record,
            "epoch": saved["epoch"],
            "validation": from_diagnostics,
        }
        shutil.copyfile(
            artifact_path(record, "train", "trace", "trace.json"),
            destination.parent / f"{kind}_trace.json",
        )
        shutil.copyfile(
            artifact_path(
                record, "train", "validation_predictions", "predictions.json"
            ),
            destination.parent / f"{kind}_validation_predictions.json",
        )
    eligible = [kind for kind in SCORER_ORDER if kind in candidates and kind != "mean"]
    winner = max(
        eligible, key=lambda kind: ranking_value(candidates[kind]["validation"])
    )
    selection = {
        "status": "checkpoints_frozen",
        "candidates": candidates,
        "provisional_winner": winner,
        "choice_split": "validation",
        "tie_rule": "earlier declared scorer; earlier epoch; larger ridge alpha",
        "test_scores_used_for_selection": False,
        "encoder": encoder_settings(EncoderConfig.model_validate(settings["encoder"])),
    }
    if destination.exists() and load_json(destination) != selection:
        raise ValueError(
            "The saved selection differs; preserve it and inspect the run."
        )
    if not destination.exists():
        write_json(destination, selection)
    return selection


def scoring_inputs(
    kind: str,
    candidate: dict[str, Any],
    published: dict[str, Any],
    cache: dict[str, Any] | None,
    settings: dict[str, Any],
    selection_path: str,
    selection_sha256: str,
) -> tuple[ScoreConfig, list[Any]]:
    """Bind one frozen scorer to its canonical model and reserved test cohort."""
    config = fit_config(settings, kind)
    encoder = {key: getattr(config, key) for key in EncoderConfig.model_fields}
    inputs = [
        input("model", source=artifact_source(candidate["run"], "train", "model")),
        input("selection", path=selection_path, data_role="training"),
        input("test", source=artifact_source(published, "publish", "test", "eval")),
        input(
            "holdout", source=artifact_source(published, "publish", "holdout", "eval")
        ),
    ]
    if cache is not None:
        inputs.append(
            input(
                "embeddings",
                source=artifact_source(cache, "embed", "embeddings", "eval"),
            )
        )
    return ScoreConfig(
        **encoder,
        kind=kind,
        model_sha256=candidate["sha256"],
        selection_sha256=selection_sha256,
        test_sha256=settings["splits"]["test"]["sha256"],
    ), inputs


def prediction_stage(
    kind: str,
    candidate: dict[str, Any],
    published: dict[str, Any],
    cache: dict[str, Any] | None,
    settings: dict[str, Any],
    selection_path: str,
    selection_sha256: str,
) -> Any:
    """Capture predictions in a sealed BUILD run before native metric verification."""
    config, inputs = scoring_inputs(
        kind, candidate, published, cache, settings, selection_path, selection_sha256
    )
    return stage(
        capture_predictions,
        stage_id="predict",
        config=config,
        inputs=tuple(inputs),
        outputs=StageOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            timing=output(path="timing.json", loader=load_json, data_role="eval"),
        ),
        reuse="never",
    )


def evaluation_stage(
    kind: str,
    candidate: dict[str, Any],
    published: dict[str, Any],
    snapshot: dict[str, Any],
    settings: dict[str, Any],
    selection_path: str,
    selection_sha256: str,
) -> Any:
    """Verify a sealed prediction snapshot using CPU EVAL and independent metrics."""
    config, inputs = scoring_inputs(
        kind, candidate, published, None, settings, selection_path, selection_sha256
    )
    inputs.extend(
        (
            input(
                "snapshot_predictions",
                source=artifact_source(snapshot, "predict", "predictions", "eval"),
            ),
            input(
                "snapshot_timing",
                source=artifact_source(snapshot, "predict", "timing", "eval"),
            ),
        )
    )
    dependencies = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    metrics = [measure(test_mse, dependencies=dependencies, comparator=comparator)]
    if kind != "mean":
        metrics.append(
            measure(test_spearman, dependencies=dependencies, comparator=comparator)
        )
    return stage(
        evaluate_baseline,
        stage_id="test",
        eval_id="csts_tranche2",
        config=config.model_copy(update={"device": "cpu"}),
        inputs=tuple(inputs),
        split_inputs=("holdout",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            timing=output(path="timing.json", loader=load_json, data_role="eval"),
        ),
        metrics=tuple(metrics),
        objective=maximize(metrics[-1]) if kind != "mean" else minimize(metrics[0]),
        reuse="never",
    )


def require_frozen_phase(path: Path, settings: dict[str, Any]) -> str:
    """Require completed frozen baselines before starting the separate LoRA phase."""
    frozen = load_json(path)
    if (
        frozen["status"] != "complete"
        or frozen["phase"] != "frozen"
        or frozen["settings"]["seed"] != settings["seed"]
        or frozen["settings"]["splits"] != settings["splits"]
        or encoder_settings(EncoderConfig.model_validate(frozen["settings"]["encoder"]))
        != encoder_settings(EncoderConfig.model_validate(settings["encoder"]))
    ):
        raise ValueError(
            "LoRA requires a completed frozen phase on the same cohort and representation."
        )
    return file_sha256(path)


def validate_recovery_parent(
    parent: dict[str, Any], settings: dict[str, Any], phase: str
) -> None:
    """Authorize source-code recovery only after the previous native invocation is resolved."""
    if parent.get("in_flight") is not None or parent.get("status") not in {
        "complete",
        "failed",
    }:
        raise ValueError("Reconcile the parent's native invocation before recovery.")
    if parent["settings"] != settings or parent["phase"] != phase:
        raise ValueError(
            "Recovery requires the original measurement settings and phase."
        )


def reusable_parent_stage(
    parent: dict[str, Any], name: str, recovery: bool
) -> dict[str, Any] | None:
    """Reuse successful measurements and permit only CPU evaluation failures to retry."""
    records = [record for record in parent["runs"] if record["name"] == name]
    if not records and recovery:
        return None
    if len(records) != 1:
        raise ValueError(
            "The parent requires exactly one producer for each reused stage."
        )
    record = records[0]
    if recovery and record["status"] != "succeeded":
        if name.startswith("test_") and name != "test_embeddings":
            return None
        raise ValueError(
            "Inspect the failed measurement artifact before retrying model work."
        )
    return record


def run_study(
    root: Path,
    settings: dict[str, Any],
    phase: str,
    name: str,
    resume: bool = False,
    parent_path: Path | None = None,
    frozen_summary: Path | None = None,
    recovery: bool = False,
) -> None:
    """Execute one declared phase while preserving every successful native stage."""
    storage = load_storage_settings(root)
    if not isinstance(storage.destination, LocalStorageDestination):
        raise ValueError(
            "Tranche 2 requires local VIPER sealing before background promotion."
        )
    prerequisite_sha = (
        require_frozen_phase(
            frozen_summary or root / "baseline_results/frozen/initial/summary.json",
            settings,
        )
        if phase == "lora"
        else None
    )
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    environment = observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    directory = root / "baseline_results" / phase / name
    directory.mkdir(parents=True, exist_ok=True)
    summary_path = directory / "summary.json"
    parent = load_json(parent_path) if parent_path is not None else None
    if parent is not None:
        if recovery:
            validate_recovery_parent(parent, settings, phase)
        elif (
            parent["status"] != "complete"
            or parent["phase"] != phase
            or parent["settings"]["splits"] != settings["splits"]
            or encoder_settings(
                EncoderConfig.model_validate(parent["settings"]["encoder"])
            )
            != encoder_settings(EncoderConfig.model_validate(settings["encoder"]))
        ):
            raise ValueError(
                "Continuation requires a completed parent with the same phase, cohort and representation."
            )
        if parent_path.resolve() == summary_path.resolve():
            raise ValueError(
                "Continuation requires a separate run name to preserve the parent."
            )
    parent_sha = file_sha256(parent_path) if parent_path is not None else None
    if summary_path.exists():
        if not resume:
            raise ValueError(
                "Inspect the saved run and use --resume to reuse completed stages."
            )
        summary = load_json(summary_path)
        if (
            summary["source_commit"] != source.commit
            or summary["settings"] != settings
            or summary["parent_summary_sha256"] != parent_sha
            or summary["frozen_prerequisite_sha256"] != prerequisite_sha
            or summary["recovery"] != recovery
        ):
            raise ValueError(
                "Pipeline resume requires identical source, settings and parent."
            )
    else:
        summary = {
            "source_commit": source.commit,
            "settings": settings,
            "phase": phase,
            "name": name,
            "attempt": uuid.uuid4().hex[:8],
            "runs": [],
            "gpu_stage_seconds": parent["gpu_stage_seconds"]
            if recovery and parent is not None
            else 0.0,
            "in_flight": None,
            "parent_summary_sha256": parent_sha,
            "frozen_prerequisite_sha256": prerequisite_sha,
            "recovery": recovery,
            "failed_parent_records": [
                record for record in parent["runs"] if record["status"] != "succeeded"
            ]
            if recovery and parent is not None
            else [],
        }
    if summary.get("status") == "complete":
        print(
            json.dumps(
                {
                    "status": "complete",
                    "summary": str(summary_path),
                    "publication_status": "inspect_queue_receipts",
                }
            )
        )
        return
    check_inputs(root, settings)

    def verify_record(record: dict[str, Any]) -> None:
        """Recheck native evidence before reusing a stage or parent artifact."""
        if record["status"] != "succeeded":
            raise ValueError("A failed stage requires inspection before retrying.")
        api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=Path(record["path"]),
                trusted_source_repositories=trusted,
            )
        )

    def parent_record(stage_name: str) -> dict[str, Any] | None:
        """Locate a verified producer from the explicitly selected completed parent."""
        if parent is None:
            return None
        record = reusable_parent_stage(parent, stage_name, recovery)
        if record is not None:
            verify_record(record)
        return record

    def execute(
        stage_name: str,
        configured: Any,
        gpu: bool,
        reused: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Commit invocation intent before execution and queue each successful local run."""
        records = [record for record in summary["runs"] if record["name"] == stage_name]
        if len(records) > 1:
            raise ValueError("Duplicate native stage records require inspection.")
        if records or reused is not None:
            record = records[0] if records else dict(reused)
            verify_record(record)
            if not records:
                record["reused_from_parent"] = True
                summary["runs"].append(record)
        else:
            if summary.get("in_flight"):
                raise ValueError(
                    "Reconcile the interrupted native invocation before executing another stage."
                )
            remaining = (
                settings["gpu_budget_seconds"][phase] - summary["gpu_stage_seconds"]
            )
            if gpu and remaining <= 0:
                raise TimeoutError("The phase's native GPU-stage budget is exhausted.")
            trial = experiment(
                experiment_id=f"csts_tranche2_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
                variants=(
                    variant(
                        stage_name,
                        stages=(configured,),
                        estimator=configured.outputs["model"]
                        if "model" in configured.outputs
                        else next(iter(configured.outputs.values())),
                    ),
                ),
                replicates=(replicate(seed=settings["seed"]),),
            )
            summary.update(
                status="running",
                current_stage=stage_name,
                in_flight={"stage": stage_name, "experiment_id": trial.experiment_id},
            )
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
            try:
                result = execution.run(
                    plan(experiment=trial, source=source, env=env),
                    timeout_seconds=max(1, int(remaining))
                    if gpu
                    else settings["cpu_stage_timeout_seconds"],
                    trusted_source_repositories=trusted,
                )
            finally:
                if gpu:
                    summary["gpu_stage_seconds"] += time.monotonic() - started
                write_json(summary_path, summary)
            record = {
                "name": stage_name,
                "status": result.status,
                "path": str(result.path),
                "reference": result.reference.model_dump(mode="json"),
                "local_run_seconds": time.monotonic() - started,
            }
            summary["runs"].append(record)
            summary["in_flight"] = None
            write_json(summary_path, summary)
            if result.status != "succeeded":
                raise RuntimeError(
                    f"Native stage {stage_name} failed; preserve and inspect its attempt."
                )
        record["publication_queue"] = str(
            queue_publication(
                root, ResolvedRunRef.model_validate(record["reference"]), destination
            )
        )
        write_json(summary_path, summary)
        return record

    try:
        cache = None
        kinds = (
            ("mean", "cosine", "ridge", "projection")
            if phase == "frozen"
            else ("lora",)
        )
        if phase == "frozen":
            configured = stage(
                cache_embeddings,
                stage_id="embed",
                config=EncoderConfig.model_validate(settings["encoder"]),
                inputs=tuple(
                    input(
                        split,
                        path=settings["splits"][split]["path"],
                        data_role="training",
                    )
                    for split in ("training", "validation")
                ),
                outputs=StageOutputs(
                    embeddings=output(
                        path="embeddings.pt", loader=load_model, data_role="training"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            )
            cache = execute(
                "train_validation_embeddings",
                configured,
                gpu=True,
                reused=parent_record("train_validation_embeddings"),
            )
        trained = {}
        for kind in kinds:
            parent_training = parent_record(f"train_{kind}")
            if recovery and parent_training is not None:
                trained[kind] = execute(
                    f"train_{kind}", None, gpu=kind == "lora", reused=parent_training
                )
                continue
            remaining = (
                settings["gpu_budget_seconds"][phase] - summary["gpu_stage_seconds"]
                if kind == "lora"
                else settings["cpu_stage_timeout_seconds"]
            )
            configured = training_stage(
                settings,
                kind,
                cache,
                remaining,
                parent_training if kind in {"projection", "lora"} else None,
            )
            trained[kind] = execute(
                f"train_{kind}",
                configured,
                gpu=kind == "lora",
                reused=parent_training if kind in {"mean", "cosine", "ridge"} else None,
            )
        selection_path = directory / "selection.json"
        selection = freeze_selection(trained, selection_path, settings)
        summary["selection_sha256"] = file_sha256(selection_path)
        summary["provisional_winner"] = selection["provisional_winner"]
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
            reuse="never",
        )
        published = execute(
            "publish_test", configured, gpu=False, reused=parent_record("publish_test")
        )
        test_cache = None
        if phase == "frozen":
            configured = stage(
                cache_embeddings,
                stage_id="embed",
                config=EncoderConfig.model_validate(settings["encoder"]),
                inputs=(
                    input(
                        "test",
                        source=artifact_source(published, "publish", "test", "eval"),
                    ),
                ),
                outputs=StageOutputs(
                    embeddings=output(
                        path="embeddings.pt", loader=load_model, data_role="eval"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            )
            test_cache = execute(
                "test_embeddings",
                configured,
                gpu=True,
                reused=parent_record("test_embeddings"),
            )
        summary["test"] = []
        for kind, candidate in selection["candidates"].items():
            configured = prediction_stage(
                kind,
                candidate,
                published,
                test_cache,
                settings,
                str(selection_path.relative_to(root)),
                summary["selection_sha256"],
            )
            snapshot = execute(
                f"predict_{kind}",
                configured,
                gpu=kind == "lora",
                reused=parent_record(f"predict_{kind}")
                if recovery or kind in {"mean", "cosine", "ridge"}
                else None,
            )
            configured = evaluation_stage(
                kind,
                candidate,
                published,
                snapshot,
                settings,
                str(selection_path.relative_to(root)),
                summary["selection_sha256"],
            )
            record = execute(
                f"test_{kind}",
                configured,
                gpu=False,
                reused=parent_record(f"test_{kind}")
                if parent is not None
                and (recovery or kind in {"mean", "cosine", "ridge"})
                else None,
            )
            shutil.copyfile(
                artifact_path(record, "test", "predictions", "predictions.json"),
                directory / f"{kind}_predictions.json",
            )
            shutil.copyfile(
                artifact_path(record, "test", "timing", "timing.json"),
                directory / f"{kind}_evaluation_timing.json",
            )
            summary["test"].append(
                {
                    "candidate": kind,
                    "checkpoint_sha256": candidate["sha256"],
                    "run": record,
                }
            )
            scores = summarize(load_json(directory / f"{kind}_predictions.json"))
            summary.setdefault("live_scores", {})[kind] = scores
            print(
                json.dumps(
                    {
                        "candidate": kind,
                        "scores": scores,
                        "publication": "queued_separately",
                    }
                ),
                flush=True,
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
    """Print the review plan by default; execute only the explicitly chosen phase."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--check-inputs", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--phase", choices=("frozen", "lora"), default="frozen")
    parser.add_argument("--name", default="initial")
    parser.add_argument("--settings", default="configs/csts-tranche-2.json")
    parent_options = parser.add_mutually_exclusive_group()
    parent_options.add_argument("--continue-from", type=Path)
    parent_options.add_argument("--recover-from", type=Path)
    parser.add_argument("--frozen-summary", type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.name):
        parser.error("Run names may contain letters, numbers, underscores and hyphens.")
    root = resolve_root()
    settings = load_json(root / args.settings)
    validate_settings(settings)
    if args.check_inputs:
        check_inputs(root, settings)
        print(json.dumps({"status": "input_identities_verified"}))
    if not args.execute:
        print(
            json.dumps(
                {"status": "review", "phase": args.phase, "settings": settings},
                indent=2,
            )
        )
        return
    directory = root / "baseline_results" / args.phase / args.name
    directory.mkdir(parents=True, exist_ok=True)
    with (root / "baseline_results" / "run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_study(
            root,
            settings,
            args.phase,
            args.name,
            resume=args.resume,
            parent_path=args.continue_from or args.recover_from,
            frozen_summary=args.frozen_summary,
            recovery=args.recover_from is not None,
        )


if __name__ == "__main__":
    main()
