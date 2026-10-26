"""Launch the reviewed masked-feature refresh pilot and native development replay."""

import argparse
import fcntl
import time
import uuid
from pathlib import Path
from typing import Any

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.background_storage import queue_publication
from csts_pilot.codebook import check_disjoint
from csts_pilot.codebook_run import evaluation_inputs
from csts_pilot.condition_reference import MODEL_SHA256
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path
from csts_pilot.iterative_codebook import IterativeConfig, fit_iterative_codebooks
from csts_pilot.iterative_codebook_analysis import (
    ReplayConfig,
    evaluate_iterative_codebooks,
    mean_spearman_gain,
)
from csts_pilot.matched_baselines_run import stored_source
from jep_pilot.loaders import load_json, load_model, load_state


def fitting_stage(prepared: dict[str, Any], config: IterativeConfig) -> Any:
    """Reuse the existing native artifact bindings and canonical TRAIN outputs."""
    metrics = tuple(
        measure(metric)
        for metric in (training_objective, validation_mse, validation_spearman)
    )
    return stage(
        fit_iterative_codebooks,
        stage_id="train",
        config=config,
        inputs=tuple(
            input(split, source=stored_source(record, "prepare", "cache", split))
            for split, record in prepared.items()
        ),
        outputs=TrainOutputs(
            model=output(path="models.pt", loader=load_model, data_role="training"),
            resume_state=output(
                path="resume.pt", loader=load_state, data_role="training"
            ),
            trace=output(path="trace.json", loader=load_json, data_role="training"),
        ),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )


def replay_stage(
    prepared: dict[str, Any],
    trained: dict[str, Any],
    published: dict[str, Any],
    config: ReplayConfig,
) -> Any:
    """Bind reserved model/test inputs to frozen models and published DEV rows."""
    metric = measure(
        mean_spearman_gain,
        dependencies=(
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        ),
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
    )
    return stage(
        evaluate_iterative_codebooks,
        stage_id="evaluate",
        eval_id="iterative_codebook_validation",
        config=config,
        inputs=evaluation_inputs(prepared, trained, published),
        split_inputs=("holdout",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            report=output(path="report.json", loader=load_json, data_role="eval"),
        ),
        metrics=(metric,),
        objective=maximize(metric),
        reuse="never",
    )


def run(root: Path, name: str, prepared_summary: Path, preflight: bool = False) -> None:
    """Preserve each attempt and queue cloud publication after each local success."""
    root = root.resolve(strict=True)
    settings_path = root / "configs/csts-iterative-codebook.json"
    settings, prior = load_json(settings_path), load_json(prepared_summary)
    prepared, hashes, caches = {}, {}, {}
    for split in ("training", "validation"):
        matches = [
            record for record in prior["runs"] if record["name"] == "prepare_" + split
        ]
        if len(matches) != 1 or matches[0]["status"] != "succeeded":
            raise ValueError(f"Require one succeeded native preparation for {split}.")
        prepared[split] = matches[0]
        path = artifact_path(matches[0], "prepare", "cache", "cache.pt")
        hashes[split + "_cache_sha256"] = file_sha256(path)
        caches[split] = load_model(path)
        provenance, expected = caches[split]["provenance"], settings["splits"][split]
        if (
            provenance["rows_sha256"] != expected["sha256"]
            or len(caches[split]["rows"]) != expected["rows"]
            or provenance["model_sha256"] != MODEL_SHA256
            or provenance["source_cache_sha256"]
            != prior["inputs"][split]["cache_sha256"]
        ):
            raise ValueError(f"Changed frozen cohort or parent model: {split}.")
    check_disjoint(caches["training"], caches["validation"])
    matches = [
        record for record in prior["runs"] if record["name"] == "publish_validation"
    ]
    if len(matches) != 1 or matches[0]["status"] != "succeeded":
        raise ValueError(
            "Require the existing succeeded native development publication."
        )
    published = matches[0]
    if load_json(
        artifact_path(published, "publish", "test", "validation.json")
    ) != caches["validation"]["rows"] or load_json(
        artifact_path(published, "publish", "holdout", "indices.json")
    ) != list(range(len(caches["validation"]["rows"]))):
        raise ValueError("Published development cohort differs from the sealed cache.")
    config = IterativeConfig(**settings["training"], **hashes)
    configured = fitting_stage(prepared, config)
    source = read_source(root)
    summary: dict[str, Any] = {
        "status": "preflight_passed",
        "source_commit": source.commit,
        "settings_sha256": file_sha256(settings_path),
        "prepared_summary_sha256": file_sha256(prepared_summary),
        "inputs": prepared,
        "published_validation": published,
        "config": config.model_dump(mode="json"),
        "parent_model_sha256": MODEL_SHA256,
        "test_accessed": False,
        "backbone_inference": False,
        "runs": [],
    }
    if preflight:
        print(summary)
        return
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal locally before asynchronous cloud promotion.")
    directory = root / "iterative_codebook_results" / name
    directory.mkdir(parents=True, exist_ok=False)
    summary_path = directory / "summary.json"
    summary.update(status="running", attempt=uuid.uuid4().hex[:8])
    write_json(summary_path, summary)
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    environment = observe_python_env()

    def execute(label: str, configured: Any, timeout: int) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_iterative_{source.commit[:8]}_{summary['attempt']}_{label}",
            variants=(
                variant(
                    label,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["in_flight"] = label
        write_json(summary_path, summary)
        started = time.monotonic()
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CPUComputeSpec(),
                    python_env=environment,
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="tranche2_requirements.txt",
                    ),
                ),
            ),
            timeout_seconds=timeout,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": label,
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
                f"Native {label} failed; preserve the attempt for review."
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        return record

    try:
        trained = execute(
            "fit", configured, int(len(config.seeds) * config.seconds_per_pair + 300)
        )
        models_sha = file_sha256(artifact_path(trained, "train", "model", "models.pt"))
        summary["model_sha256"] = models_sha
        evaluated = execute(
            "evaluate_validation",
            replay_stage(
                prepared,
                trained,
                published,
                ReplayConfig(models_sha256=models_sha, **hashes),
            ),
            600,
        )
        summary["paired"] = load_json(
            artifact_path(evaluated, "evaluate", "report", "report.json")
        )["paired"]
        summary.update(status="complete", publication_status="queued_separately")
        write_json(summary_path, summary)
    except Exception as error:
        summary.update(
            status="failed", error_type=type(error).__name__, error=str(error)
        )
        write_json(summary_path, summary)
        raise


def main() -> None:
    """Keep launches serialized in the physical workspace; preflight never trains."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--name", default="initial")
    parser.add_argument("--prepared-summary", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in {"", ".", ".."}:
        raise ValueError("Attempt name must be a single directory component.")
    directory = args.root / "iterative_codebook_results"
    directory.mkdir(exist_ok=True)
    with (directory / "launch.lock").open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.root, args.name, args.prepared_summary, args.preflight)


if __name__ == "__main__":
    main()
