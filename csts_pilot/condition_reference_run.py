"""Run Tranche 4 with immediate local event streaming and native provenance."""

import argparse
import fcntl
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, StageOutputs, output
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

from csts_pilot.background_storage import queue_publication
from csts_pilot.condition_reference import (
    ARMS,
    MODEL_SHA256,
    AnalysisConfig,
    ExtractionConfig,
    analyze,
    emit,
    extract,
    native_spearman,
)
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path, artifact_source
from jep_pilot.loaders import load_json, load_model


def run(root: Path, name: str, reuse_extraction: Path | None = None) -> None:
    """Freeze the validation decision before permitting test extraction."""
    root = root.resolve(strict=True)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError(
            "Native sealing must use the local store before asynchronous promotion."
        )
    settings = load_json(root / "configs/csts-qwen-evidence.json")
    original = load_json(root / "qwen_evidence_results/initial/summary.json")
    parent = next(r for r in original["runs"] if r["name"] == "ratings_ratings")
    model = artifact_path(parent, "train", "model", "model.pt")
    if file_sha256(model) != MODEL_SHA256:
        raise ValueError("Selected checkpoint identity differs from the proposal.")
    directory = root / "condition_reference_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    summary_path = directory / "summary.json"
    if summary_path.exists():
        raise FileExistsError(
            "Preserve this attempt; use a new name for a reconciled recovery."
        )
    events = directory / "events.jsonl"
    events.touch(exist_ok=False)
    os.environ["CSTS_TRANCHE4_EVENTS"] = str(events)
    source = read_source(root)
    environment = observe_python_env()
    trusted = frozenset({str(source.repository)})
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "attempt": uuid.uuid4().hex[:8],
        "model_sha256": MODEL_SHA256,
        "runs": [],
        "optimizer_updates": 0,
        "plan_sha256": file_sha256(
            root / "plans/csts-tranche-4-condition-component.md"
        ),
        "events_path": str(events),
        "current_stage": None,
    }
    write_json(summary_path, summary)

    reused = None
    if reuse_extraction is not None:
        earlier = load_json(reuse_extraction)
        reused = next(r for r in earlier["runs"] if r["name"] == "extract_validation")
        if reused["status"] != "succeeded" or earlier["model_sha256"] != MODEL_SHA256:
            raise ValueError("Recovery extraction identity differs.")
        api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=Path(reused["path"]),
                trusted_source_repositories=trusted,
            )
        )
        summary["reused_validation_extraction"] = reused
        write_json(summary_path, summary)
        emit(
            "reusing_extraction",
            source_summary=str(reuse_extraction),
            reference=reused["reference"],
        )

    def execute(name: str, configured: Any, gpu: bool) -> dict[str, Any]:
        summary["current_stage"] = name
        write_json(summary_path, summary)
        emit("stage_started", stage=name, gpu=gpu)
        trial = experiment(
            experiment_id=f"csts_condition_ref_{source.commit[:8]}_{summary['attempt']}_{name}",
            variants=(
                variant(
                    name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
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
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=1800,
            trusted_source_repositories=trusted,
        )
        record = {
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native stage failed: {name}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        emit("stage_complete", stage=name, seconds=record["seconds"])
        return record

    try:
        selected_arms = ARMS
        thresholds: dict[str, float] = {}
        selected = None
        for split in ("validation", "test"):
            spec = settings["splits"][split]
            if file_sha256(root / spec["path"]) != spec["sha256"]:
                raise ValueError(f"Changed {split} input bytes.")
            baseline = (
                parent
                if split == "validation"
                else next(r for r in original["runs"] if r["name"] == "predict_ratings")
            )
            baseline_stage = "train" if split == "validation" else "predict"
            baseline_output = (
                "validation_predictions" if split == "validation" else "predictions"
            )
            extracted = (
                reused
                if split == "validation" and reused is not None
                else execute(
                    f"extract_{split}",
                    stage(
                        extract,
                        stage_id="extract",
                        config=ExtractionConfig(
                            **settings["encoder"],
                            rows_sha256=spec["sha256"],
                            split=split,
                            arms=selected_arms,
                        ),
                        inputs=(
                            input(
                                "model",
                                source=artifact_source(parent, "train", "model"),
                            ),
                            input("rows", path=spec["path"], data_role="eval"),
                        ),
                        outputs=StageOutputs(
                            cache=output(
                                path="cache.pt", loader=load_model, data_role="eval"
                            ),
                            timing=output(
                                path="timing.json", loader=load_json, data_role="eval"
                            ),
                        ),
                        reuse="never",
                    ),
                    True,
                )
            )
            native_metric = measure(
                native_spearman,
                dependencies=(
                    MetricDependency(
                        source="artifact", name="predictions", data_role="eval"
                    ),
                ),
                comparator=FloatComparator(mode="absolute", tolerance=1e-12),
            )
            evaluated = execute(
                f"analyze_{split}",
                stage(
                    analyze,
                    stage_id="analyze",
                    eval_id="csts_condition_reference",
                    config=AnalysisConfig(
                        rows_sha256=spec["sha256"],
                        split=split,
                        arms=selected_arms,
                        thresholds=thresholds,
                        selected_arm=selected,
                    ),
                    inputs=(
                        input(
                            "model", source=artifact_source(parent, "train", "model")
                        ),
                        input("rows", path=spec["path"], data_role="eval"),
                        input(
                            "cache",
                            source=artifact_source(
                                extracted, "extract", "cache", "eval"
                            ),
                        ),
                        input(
                            "timing",
                            source=artifact_source(
                                extracted, "extract", "timing", "eval"
                            ),
                        ),
                        input(
                            "baseline_predictions",
                            source=artifact_source(
                                baseline, baseline_stage, baseline_output, "eval"
                            ),
                        ),
                    ),
                    split_inputs=("rows",),
                    metrics=(native_metric,),
                    objective=maximize(native_metric),
                    outputs=EvalOutputs(
                        predictions=output(
                            path="predictions.json", loader=load_json, data_role="eval"
                        ),
                        report=output(
                            path="report.json", loader=load_json, data_role="eval"
                        ),
                        geometry=output(
                            path="geometry.json", loader=load_json, data_role="eval"
                        ),
                        agreement=output(
                            path="agreement.json", loader=load_json, data_role="eval"
                        ),
                    ),
                    reuse="never",
                ),
                False,
            )
            report_path = artifact_path(evaluated, "analyze", "report", "report.json")
            report = load_json(report_path)
            for output_name, filename in (
                ("report", "report.json"),
                ("geometry", "geometry.json"),
                ("predictions", "predictions.json"),
            ):
                shutil.copyfile(
                    artifact_path(evaluated, "analyze", output_name, filename),
                    directory / f"{split}_{filename}",
                )
            summary[split] = report
            write_json(summary_path, summary)
            if split == "validation":
                selected = report["decision"]["selected_arm"]
                thresholds = report["decision"]["thresholds"]
                selection = {
                    **report["decision"],
                    "model_sha256": MODEL_SHA256,
                    "validation_report_sha256": file_sha256(report_path),
                    "source_commit": source.commit,
                }
                write_json(directory / "selection.json", selection)
                summary["selection_sha256"] = file_sha256(directory / "selection.json")
                write_json(summary_path, summary)
                if selected == "A":
                    summary["stop_reason"] = "no_validation_candidate_eligible"
                    break
                selected_arms = ("A", selected)
            else:
                summary["continuation_gate"] = {
                    "passes": report["transfer"]["passes"]
                    and selected in {"B_u", "B_r", "C_u", "C_r"},
                    "selected_arm": selected,
                }
                summary["stop_reason"] = "diagnostic_complete"
        summary.update(
            status="complete",
            current_stage=None,
            publication_status="queued_separately",
        )
        write_json(summary_path, summary)
        emit(
            "diagnostic_complete",
            stop_reason=summary["stop_reason"],
            continuation_gate=summary.get("continuation_gate"),
        )
    except Exception as error:
        summary.update(
            status="failed", error_type=type(error).__name__, error=str(error)
        )
        write_json(summary_path, summary)
        emit("diagnostic_failed", error_type=type(error).__name__, error=str(error))
        raise


def main() -> None:
    """Keep an exclusive job lock while producing the inspectable event log."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--name", default="initial")
    parser.add_argument("--reuse-extraction", type=Path)
    args = parser.parse_args()
    with (args.root / ".viper" / "condition_reference.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.root, args.name, args.reuse_extraction)


if __name__ == "__main__":
    main()
