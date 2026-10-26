"""Preflight supplied expert JEP labels; explicitly opt in to a native CPU pilot."""

import argparse
import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.background_storage import queue_publication
from csts_pilot.convergence import file_sha256, training_objective, write_json
from csts_pilot.convergence_run import artifact_path
from csts_pilot.matched_baselines_run import stored_source
from csts_pilot.multiple_codebook import (
    MultipleCodebookConfig,
    fit_multiple_codebooks,
    prepare_data,
    validation_macro_f1,
)
from csts_pilot.multiple_codebook_analysis import (
    MultipleEvaluationConfig,
    evaluate_multiple_codebooks,
    mean_macro_f1_gain,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def preflight(
    settings: dict[str, Any], manifest: Path
) -> tuple[MultipleCodebookConfig, dict[str, Path], dict[str, Any]]:
    """Require actual expert annotations and immutable precomputed features before launch."""
    supplied = load_json(manifest)
    if set(supplied) != {"annotations", "training", "validation", "model_sha256"}:
        raise ValueError(
            "Inputs must contain annotations, training/validation features and frozen model SHA."
        )
    paths = {}
    digests = {}
    for name in ("annotations", "training", "validation"):
        spec = supplied[name]
        if not isinstance(spec, dict) or set(spec) != {"path", "sha256"}:
            raise ValueError(
                "Each input must supply path and independently pinned SHA256."
            )
        path = Path(spec["path"])
        path = (
            (manifest.parent / path).resolve(strict=True)
            if not path.is_absolute()
            else path.resolve(strict=True)
        )
        if file_sha256(path) != spec["sha256"]:
            raise ValueError(f"Changed pinned input: {name}.")
        paths[name] = path
        digests[name + "_sha256"] = spec["sha256"]
    config = MultipleCodebookConfig(
        **settings["training"], **digests, model_sha256=supplied["model_sha256"]
    )
    prepared = prepare_data(
        load_json(paths["annotations"]),
        {name: load_model(paths[name]) for name in ("training", "validation")},
        config,
    )
    return (
        config,
        paths,
        {
            name: prepared["splits"][name]["support"]
            for name in ("training", "validation")
        },
    )


def evaluation_inputs(
    root: Path,
    copied: dict[str, Path],
    trained: dict[str, Any],
    published: dict[str, Any],
) -> tuple[Any, ...]:
    """Bind native reserved names to sealed selected-model and development producers."""
    return tuple(
        input(key, path=str(path.relative_to(root)), data_role="training")
        for key, path in copied.items()
    ) + (
        input("model", source=stored_source(trained, "train", "model", "models")),
        input(
            "test",
            source=stored_source(
                published, "publish", "test", "development_rows", "eval"
            ),
        ),
        input(
            "holdout",
            source=stored_source(published, "publish", "holdout", "indices", "eval"),
        ),
    )


def run(root: Path, manifest: Path, name: str, execute: bool = False) -> None:
    """Default to validation; execute a new immutable local attempt only on explicit opt-in."""
    root = root.resolve(strict=True)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("Attempt name must be a short filename-safe identifier.")
    settings = load_json(root / "configs/csts-multiple-codebook.json")
    config, paths, support = preflight(settings, manifest.resolve(strict=True))
    if not execute:
        print(
            json.dumps(
                {
                    "status": "preflight_passed",
                    "support": support,
                    "test_accessed": False,
                    "backbone_inference": False,
                }
            ),
            flush=True,
        )
        return
    if subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout:
        raise ValueError(
            "Execution requires a clean reviewed Git checkout; commit the reviewed changes first."
        )
    source = read_source(root)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal native runs locally before asynchronous cloud promotion.")
    attempt = root / "multiple_codebook_results" / name
    attempt.mkdir(parents=True, exist_ok=False)
    summary_path = attempt / "summary.json"
    summary: dict[str, Any] = {
        "status": "preparing",
        "source_commit": source.commit,
        "config": config.model_dump(mode="json"),
        "support": support,
        "test_accessed": False,
        "backbone_inference": False,
        "runs": [],
    }
    write_json(summary_path, summary)
    try:
        data = root / "multiple_codebook_data" / name
        data.mkdir(parents=True, exist_ok=False)
        copied = {}
        for key, path in paths.items():
            destination = data / (key + (".json" if key == "annotations" else ".pt"))
            shutil.copyfile(path, destination)
            if file_sha256(destination) != getattr(config, key + "_sha256"):
                raise ValueError(f"Input changed during immutable copy: {key}.")
            copied[key] = destination
        metrics = (measure(training_objective), measure(validation_macro_f1))
        configured = stage(
            fit_multiple_codebooks,
            stage_id="train",
            config=config,
            inputs=tuple(
                input(key, path=str(path.relative_to(root)), data_role="training")
                for key, path in copied.items()
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
        environment = observe_python_env()
        publication = ViperCloudDestination.model_validate(
            settings["publication_destination"]
        )

        def execute_stage(label: str, configured: Any, timeout: int) -> dict[str, Any]:
            trial = experiment(
                experiment_id=f"multiple_codebook_{source.commit[:8]}_{uuid.uuid4().hex[:8]}_{label}",
                variants=(
                    variant(
                        label,
                        stages=(configured,),
                        estimator=next(iter(configured.outputs.values())),
                    ),
                ),
                replicates=(replicate(seed=config.seeds[0]),),
            )
            summary.update(status="running", in_flight=label)
            write_json(summary_path, summary)
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
                "reference": result.reference.model_dump(mode="json"),
                "path": str(result.path),
            }
            summary["runs"].append(record)
            write_json(summary_path, summary)
            if result.status != "succeeded":
                raise RuntimeError(
                    f"Native expert codebook stage failed: {label}; preserve this attempt."
                )
            record["publication_queue"] = str(
                queue_publication(root, result.reference, publication)
            )
            write_json(summary_path, summary)
            return record

        trained = execute_stage(
            "fit", configured, int(2 * len(config.seeds) * config.seconds_per_fit + 300)
        )
        rows = load_json(copied["annotations"])["validation"]
        write_json(data / "validation_rows.json", rows)
        write_json(data / "indices.json", list(range(len(rows))))
        published = execute_stage(
            "publish_validation",
            stage(
                publish_evaluation_inputs,
                stage_id="publish",
                inputs=(
                    input(
                        "test",
                        path=str((data / "validation_rows.json").relative_to(root)),
                        data_role="eval",
                    ),
                    input(
                        "holdout",
                        path=str((data / "indices.json").relative_to(root)),
                        data_role="eval",
                    ),
                ),
                outputs=StageOutputs(
                    test=output(
                        path="validation.json", loader=load_json, data_role="eval"
                    ),
                    holdout=output(
                        path="indices.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            120,
        )
        metric = measure(
            mean_macro_f1_gain,
            dependencies=(
                MetricDependency(
                    source="artifact", name="predictions", data_role="eval"
                ),
            ),
            comparator=FloatComparator(mode="absolute", tolerance=1e-12),
        )
        evaluated = execute_stage(
            "evaluate_validation",
            stage(
                evaluate_multiple_codebooks,
                stage_id="evaluate",
                eval_id="expert_claim_development_replay",
                config=MultipleEvaluationConfig(
                    models_sha256=file_sha256(
                        artifact_path(trained, "train", "model", "models.pt")
                    ),
                    fitting=config,
                ),
                inputs=evaluation_inputs(root, copied, trained, published),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    report=output(
                        path="report.json", loader=load_json, data_role="eval"
                    ),
                ),
                metrics=(metric,),
                objective=maximize(metric),
                reuse="never",
            ),
            600,
        )
        for artifact in ("report", "predictions"):
            shutil.copyfile(
                artifact_path(evaluated, "evaluate", artifact, artifact + ".json"),
                attempt / (artifact + ".json"),
            )
        summary.update(
            status="complete",
            in_flight=None,
            evaluation_split="selected_development",
            publication_status="queued_separately",
        )
        write_json(summary_path, summary)
    except Exception as error:
        summary.update(status="failed", error_type=type(error).__name__)
        write_json(summary_path, summary)
        raise


def main() -> None:
    """Expose an explicit execution gate; there are no default or invented expert inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--name", default="expert-claim-pilot")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run(args.root, args.inputs, args.name, args.execute)


if __name__ == "__main__":
    main()
