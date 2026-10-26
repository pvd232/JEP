"""Run the bounded CPU prototype screen using existing native feature artifacts."""

import argparse
import fcntl
import json
import shutil
import time
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
from csts_pilot.codebook import (
    CacheConfig,
    CodebookConfig,
    fit_codebooks,
    prepare_cache,
)
from csts_pilot.codebook_analysis import (
    EvaluationConfig,
    evaluate_codebooks,
    mean_spearman_gain,
)
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path
from csts_pilot.matched_baselines_run import stored_source
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def evaluation_inputs(
    prepared: dict[str, Any], trained: dict[str, Any], published: dict[str, Any]
) -> tuple[Any, ...]:
    """Bind VIPER's reserved model/test names to frozen training and development producers."""
    return tuple(
        input(name, source=stored_source(record, "prepare", "cache", name))
        for name, record in prepared.items()
    ) + (
        input("model", source=stored_source(trained, "train", "model", "models")),
        input(
            "test",
            source=stored_source(
                published, "publish", "test", "validation_rows", "eval"
            ),
        ),
        input(
            "holdout",
            source=stored_source(published, "publish", "holdout", "holdout", "eval"),
        ),
    )


def render_report(report: dict[str, Any], summary: dict[str, Any]) -> str:
    """Report selected-validation diagnostics and the exact scope of missing evidence."""
    lines = [
        "# Audio-inspired prototype screen",
        "",
        "This is a validation-only English C-STS mechanism screen. Both arms use the same frozen Qwen + LoRA states and rating supervision. No new backbone inference, test evaluation, JEP human judgments, or certified edits ran.",
        "",
        "| Seed | Method | Selected epoch | Validation Spearman | MSE | Used codes: train / dev | Negative pairs sharing a code |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for key, item in report["metrics"].items():
        seed, arm = key.split(":")
        codes = item["codes_validation"]
        lines.append(
            f"| {seed} | {arm} | {item['selected_epoch']} | {item['validation']['spearman']:.6f} | {item['validation']['mse_0_1']:.6f} | {item['codes_training']['occupied_codes']} / {codes['occupied_codes']} | {codes['negative_same_code']} / {codes['negative_pairs']} |"
        )
    result = report["bootstrap"]
    low, high = result["percentile_95"]
    lines += [
        "",
        f"Mean paired prototype-minus-projection Spearman: **{result['mean_seed_spearman_gain']:+.6f}**; source-group bootstrap interval **[{low:+.6f}, {high:+.6f}]**.",
        "",
        "The bootstrap holds the listed training seeds and chosen checkpoints fixed. These are validation diagnostics after epoch selection; the interval does not correct for selection or establish fresh-test performance. Seed-specific changes and their sample dispersion are retained in the JSON.",
        "",
        "The control fits spherical k-means after its projection is selected. The prototype arm learns its dictionary during rating training using a straight-through quantization objective. Both retain continuous cosine as the primary score; quantized-score metrics and complete usage histograms are reported separately.",
        "",
        "The 128 numeric prototypes are shared across condition-conditioned representations. This screen does not fit a separate dictionary for every sparsely repeated benchmark question. Prototype IDs have no assigned legal interpretation. JEP application requires claim-level or multiple assignments, explicit definitions, rare-demand checks, certified edits, and expert review.",
        "",
        "## Records",
        "",
        "[Method and frozen settings](../plans/csts-codebook.md) · [Results](csts_codebook_results.json) · [Unreviewed exemplars](csts_codebook_review.json) · [Native execution](csts_codebook_execution.json)",
        "",
        f"Source commit: `{summary['source_commit']}`. All native stages use CPU compute. Publication is queued independently of training and scoring.",
        "",
    ]
    return "\n".join(lines)


def run(
    root: Path,
    name: str,
    manifest: Path,
    preflight: bool = False,
    recover: Path | None = None,
) -> None:
    """Create a new immutable attempt; never restart a partial native experiment."""
    root = root.resolve(strict=True)
    settings_path = root / "configs/csts-codebook.json"
    settings = load_json(settings_path)
    inputs = load_json(manifest)
    if set(inputs) != {"training", "validation"}:
        raise ValueError("The initial screen accepts training and validation only.")
    for split, spec in inputs.items():
        CacheConfig(
            kind=spec["kind"],
            rows_sha256=spec["rows_sha256"],
            source_cache_sha256=spec["cache_sha256"],
        )
        original = Path(spec["rows_path"])
        if (
            file_sha256(original) != settings["splits"][split]["sha256"]
            or spec["rows_sha256"] != settings["splits"][split]["sha256"]
        ):
            raise ValueError(f"Changed prepared cohort: {split}.")
        if (
            file_sha256(artifact_path(spec["record"], "extract", "cache", "cache.pt"))
            != spec["cache_sha256"]
        ):
            raise ValueError(f"Changed sealed producer cache: {split}.")
    if shutil.disk_usage(root).free < 3 * 1024**3:
        raise OSError("Require 3 GiB free for the bounded native CPU screen.")
    source = read_source(root)
    recovered = load_json(recover) if recover is not None else None
    recovery_sha = file_sha256(recover) if recover is not None else None
    reused = {}
    if recovered is not None:
        if (
            recovered["status"] != "failed"
            or recovered["settings_sha256"] != file_sha256(settings_path)
            or recovered["inputs_manifest_sha256"] != file_sha256(manifest)
            or not recovered.get("frozen_models_sha256")
        ):
            raise ValueError(
                "Recovery requires a failed attempt with identical settings/inputs and frozen models."
            )
        reused = {record["name"]: record for record in recovered["runs"]}
        if set(reused) != {
            "prepare_training",
            "prepare_validation",
            "fit",
            "publish_validation",
        } or any(record["status"] != "succeeded" for record in reused.values()):
            raise ValueError(
                "Only the completed preparation, fitting and publication stages may be reused."
            )
        if (
            file_sha256(artifact_path(reused["fit"], "train", "model", "models.pt"))
            != recovered["frozen_models_sha256"]
        ):
            raise ValueError("Recovery model bytes differ from the frozen selection.")
    if preflight:
        print(
            json.dumps(
                {
                    "status": "passed",
                    "source_commit": source.commit,
                    "splits": list(inputs),
                    "test_accessed": False,
                    "backbone_inference": False,
                }
            ),
            flush=True,
        )
        return
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal native runs locally before asynchronous cloud promotion.")
    directory = root / "codebook_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    summary_path = directory / "summary.json"
    if summary_path.exists():
        raise FileExistsError(
            "Preserve the existing attempt; inspect it before a new launch."
        )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "attempt": uuid.uuid4().hex[:8],
        "settings_sha256": file_sha256(settings_path),
        "inputs_manifest_sha256": file_sha256(manifest),
        "inputs": inputs,
        "runs": [],
        "test_accessed": False,
        "backbone_inference": False,
        "recovery_of": {
            "path": str(recover),
            "sha256": recovery_sha,
            "source_commit": recovered["source_commit"],
            "error": recovered.get("error"),
        }
        if recovered is not None
        else None,
    }
    write_json(summary_path, summary)
    environment = observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )

    def execute(label: str, configured: Any, timeout: int = 600) -> dict[str, Any]:
        if label in reused:
            record = dict(reused[label], reused_from_summary_sha256=recovery_sha)
            summary["runs"].append(record)
            write_json(summary_path, summary)
            return record
        trial = experiment(
            experiment_id=f"csts_codebook_{source.commit[:8]}_{summary['attempt']}_{label}",
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
            raise RuntimeError(f"Native stage failed: {label}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        print(
            json.dumps(
                {
                    "event": "codebook_stage_complete",
                    "stage": label,
                    "seconds": record["seconds"],
                }
            ),
            flush=True,
        )
        return record

    try:
        prepared = {}
        data = root / "codebook_data"
        data.mkdir(exist_ok=True)
        for split, spec in inputs.items():
            copied = data / f"{split}.json"
            if copied.exists() and file_sha256(copied) != spec["rows_sha256"]:
                raise ValueError(
                    "Existing copied data differs; preserve it for inspection."
                )
            if not copied.exists():
                shutil.copyfile(spec["rows_path"], copied)
            prepared[split] = execute(
                f"prepare_{split}",
                stage(
                    prepare_cache,
                    stage_id="prepare",
                    config=CacheConfig(
                        kind=spec["kind"],
                        rows_sha256=spec["rows_sha256"],
                        source_cache_sha256=spec["cache_sha256"],
                    ),
                    inputs=(
                        input(
                            "rows",
                            path=str(copied.relative_to(root)),
                            data_role="training",
                        ),
                        input(
                            "source_cache",
                            source=stored_source(
                                spec["record"], "extract", "cache", f"source_{split}"
                            ),
                        ),
                    ),
                    outputs=StageOutputs(
                        cache=output(
                            path="cache.pt", loader=load_model, data_role="training"
                        )
                    ),
                    reuse="never",
                ),
            )
        cache_hashes = {
            name: file_sha256(artifact_path(record, "prepare", "cache", "cache.pt"))
            for name, record in prepared.items()
        }
        fitting = CodebookConfig(
            **settings["training"],
            **{f"{name}_cache_sha256": digest for name, digest in cache_hashes.items()},
        )
        metrics = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        trained = execute(
            "fit",
            stage(
                fit_codebooks,
                stage_id="train",
                config=fitting,
                inputs=tuple(
                    input(name, source=stored_source(record, "prepare", "cache", name))
                    for name, record in prepared.items()
                ),
                outputs=TrainOutputs(
                    model=output(
                        path="models.pt", loader=load_model, data_role="training"
                    ),
                    resume_state=output(
                        path="resume.pt", loader=load_state, data_role="training"
                    ),
                    trace=output(
                        path="trace.json", loader=load_json, data_role="training"
                    ),
                ),
                metrics=metrics,
                objective=maximize(metrics[-1]),
                reuse="never",
            ),
            timeout=int(2 * len(fitting.seeds) * fitting.seconds_per_fit + 300),
        )
        models_sha = file_sha256(artifact_path(trained, "train", "model", "models.pt"))
        summary["frozen_models_sha256"] = models_sha
        write_json(summary_path, summary)
        indices = directory / "indices.json"
        write_json(indices, list(range(settings["splits"]["validation"]["rows"])))
        published = execute(
            "publish_validation",
            stage(
                publish_evaluation_inputs,
                stage_id="publish",
                inputs=(
                    input(
                        "test", path="codebook_data/validation.json", data_role="eval"
                    ),
                    input(
                        "holdout", path=str(indices.relative_to(root)), data_role="eval"
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
        )
        metric = measure(
            mean_spearman_gain,
            dependencies=(
                MetricDependency(
                    source="artifact", name="predictions", data_role="eval"
                ),
            ),
            comparator=FloatComparator(mode="absolute", tolerance=1e-12),
        )
        evaluated = execute(
            "evaluate_validation",
            stage(
                evaluate_codebooks,
                stage_id="evaluate",
                eval_id="codebook_validation_screen",
                config=EvaluationConfig(
                    models_sha256=models_sha,
                    **{f"{n}_cache_sha256": d for n, d in cache_hashes.items()},
                    bootstrap_draws=settings["bootstrap_draws"],
                    bootstrap_seed=settings["bootstrap_seed"],
                ),
                inputs=evaluation_inputs(prepared, trained, published),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    report=output(
                        path="report.json", loader=load_json, data_role="eval"
                    ),
                    review=output(
                        path="review.json", loader=load_json, data_role="eval"
                    ),
                ),
                metrics=(metric,),
                objective=maximize(metric),
                reuse="never",
            ),
            timeout=900,
        )
        output_dir = root / "training_outputs"
        for artifact in ("predictions", "report", "review"):
            target = "results" if artifact == "report" else artifact
            shutil.copyfile(
                artifact_path(evaluated, "evaluate", artifact, artifact + ".json"),
                output_dir / f"csts_codebook_{target}.json",
            )
        shutil.copyfile(
            artifact_path(trained, "train", "trace", "trace.json"),
            output_dir / "csts_codebook_trace.json",
        )
        summary.update(
            status="complete",
            publication_status="queued_separately",
            evaluation_split="validation",
        )
        write_json(summary_path, summary)
        write_json(output_dir / "csts_codebook_execution.json", summary)
        report = load_json(output_dir / "csts_codebook_results.json")
        (output_dir / "csts_codebook_report.md").write_text(
            render_report(report, summary)
        )
        print(
            json.dumps({"event": "codebook_complete", **report["bootstrap"]}),
            flush=True,
        )
    except Exception as error:
        summary.update(
            status="failed", error_type=type(error).__name__, error=str(error)
        )
        write_json(summary_path, summary)
        raise


def main() -> None:
    """Keep concurrent launches out of the same physical native workspace."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--name", default="initial")
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument(
        "--recover",
        type=Path,
        help="Explicit failed-attempt summary whose sealed training must be reused.",
    )
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in {"", ".", ".."}:
        raise ValueError("An attempt name must be a single directory component.")
    lock = args.root / "codebook_results"
    lock.mkdir(exist_ok=True)
    with (lock / "launch.lock").open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.root, args.name, args.inputs, args.preflight, args.recover)


if __name__ == "__main__":
    main()
