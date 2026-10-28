"""Reuse frozen native caches for validation selected readouts on the Colab A100."""

import argparse
import fcntl
import time
import uuid
from pathlib import Path
from typing import Any

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import EvalOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloudDestination

from csts_pilot import evidence_readout_progress as progress
from csts_pilot.background_storage import _save, queue_publication
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
)
from csts_pilot.convergence_run import artifact_path
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout_convergence import (
    ConvergedEvaluationConfig,
    ConvergedFitConfig,
    evaluate_converged_readouts,
    fit_converged_readouts,
    refit_evaluation_metric,
)
from csts_pilot.evidence_readout_run import checked_source, gpu_idle, validate_settings
from jep_pilot.loaders import load_json, load_model, load_state


def fit_outputs():
    return TrainOutputs(
        model=output(path="model.pt", loader=load_model, data_role="training"),
        resume_state=output(path="resume.pt", loader=load_state, data_role="training"),
        candidates=output(
            path="candidates.pt", loader=load_model, data_role="training"
        ),
        selection=output(path="selection.json", loader=load_json, data_role="training"),
        trace=output(path="trace.json", loader=load_json, data_role="training"),
        validation_predictions=output(
            path="predictions.json", loader=load_json, data_role="training"
        ),
    )


def initialize_progress(path: Path, source: str, hardware: str):
    path.write_text(
        "# JEP readouts trained to a validation plateau\n\n"
        f"Source: `{source}`. Hardware: {hardware}.\n\n"
        "Rates: 0.00001, 0.00003, 0.0001. Seeds: 7, 8, 9. "
        "Select one rate per objective by mean best validation Spearman. "
        "Continue until ten epochs pass without validation improvement. "
        "An epoch ceiling is reported as an incomplete fit.\n\n"
        "Fit D, E and the same comparison on A's final vectors after selecting B/C. "
        "Qwen stays frozen. Sentence vectors retain all 4,096 coordinates.\n\n"
        "## Progress\n\n| UTC | Event | Seed | Step | Metrics or progress |\n"
        "| --- | --- | --- | --- | --- |\n"
    )


def run(
    root: Path,
    previous_path: Path,
    settings: dict[str, Any],
    directory: Path,
    commit: str,
):
    checked_source(root, commit)
    previous = load_json(previous_path)
    if (
        previous["status"] != "complete"
        or previous["source_commit"] != settings["previous_source_commit"]
    ):
        raise ValueError("Require the completed pinned parent study.")
    old = previous["settings"]
    validate_settings(root, old)
    records = {r["name"]: r for r in previous["runs"]}
    source, environment = read_source(root), observe_python_env()
    destination = ViperCloudDestination.model_validate(old["publication_destination"])
    path = directory / "summary.json"
    if path.exists():
        raise ValueError(
            "Preserve the existing attempt and reconcile its checkpoint before relaunch."
        )
    progress_path = directory / "progress.md"
    initialize_progress(progress_path, source.commit, settings["gpu_model"])
    progress.configure(str(progress_path))
    summary = {
        "status": "running",
        "source_commit": source.commit,
        "settings": settings,
        "parent_summary_sha256": file_sha256(previous_path),
        "runs": [],
        "in_flight": None,
        "attempt": uuid.uuid4().hex[:8],
    }
    _save(path, summary)

    def execute(name, configured):
        trial = experiment(
            experiment_id=f"csts_refit_{source.commit[:8]}_{summary['attempt']}_{name}",
            variants=(
                variant(
                    name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["in_flight"] = {"name": name, "experiment_id": trial.experiment_id}
        _save(path, summary)
        progress.append("stage_started", name=name)
        started = time.monotonic()
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CUDAComputeSpec(model=settings["gpu_model"], count=1),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="tranche2_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=settings["stage_timeout_seconds"],
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        _save(path, summary)
        progress.append("stage_finished", name=name, status=result.status)
        if result.status != "succeeded":
            raise RuntimeError(f"Native convergence stage failed: {name}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        _save(path, summary)
        return record

    try:
        caches = {
            s: records[f"extract_{s}_proposition_final"]
            for s in ("training", "validation", "test", "interventions")
        }
        hashes = {
            s: file_sha256(artifact_path(r, "extract", "cache", "cache.pt"))
            for s, r in caches.items()
        }
        bindings = [
            input(s, path=old["splits"][s]["path"], data_role="training")
            for s in ("training", "validation")
        ]
        bindings.extend(
            input(
                f"{s}_cache",
                source=stored_source(caches[s], "extract", "cache", f"{s}_cache"),
            )
            for s in ("training", "validation")
        )
        metrics = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        fitted = execute(
            "fit",
            stage(
                fit_converged_readouts,
                stage_id="fit",
                config=ConvergedFitConfig(
                    **settings["fit"],
                    progress_path=str(progress_path),
                    **{
                        f"{s}_sha256": old["splits"][s]["sha256"]
                        for s in ("training", "validation")
                    },
                    **{
                        f"{s}_cache_sha256": hashes[s]
                        for s in ("training", "validation")
                    },
                ),
                inputs=tuple(bindings),
                outputs=fit_outputs(),
                metrics=metrics,
                objective=maximize(metrics[-1]),
                reuse="never",
            ),
        )
        model_path = artifact_path(fitted, "fit", "model", "model.pt")
        selection = {
            "status": "checkpoints_frozen",
            "test_scores_used_for_selection": False,
            "source_commit": source.commit,
            "model_sha256": file_sha256(model_path),
            "validation_selection": load_json(
                artifact_path(fitted, "fit", "selection", "selection.json")
            ),
        }
        selection_path = directory / "selection.json"
        _save(selection_path, selection)
        summary["selection_sha256"] = file_sha256(selection_path)
        _save(path, summary)
        # The fitting worker receives training and validation inputs exclusively.
        published = records["publish_test"]
        bindings = [
            input("model", source=stored_source(fitted, "fit", "model", "model")),
            input(
                "selection",
                path=selection_path.relative_to(root).as_posix(),
                data_role="training",
            ),
            input(
                "test",
                source=stored_source(published, "publish", "test", "test", "eval"),
            ),
            input(
                "holdout",
                source=stored_source(
                    published, "publish", "holdout", "holdout", "eval"
                ),
            ),
            input(
                "cache",
                source=stored_source(
                    caches["test"], "extract", "cache", "cache", "eval"
                ),
            ),
            input(
                "intervention_rows", path=old["interventions"]["path"], data_role="eval"
            ),
            input(
                "intervention_cache",
                source=stored_source(
                    caches["interventions"],
                    "extract",
                    "cache",
                    "intervention_cache",
                    "eval",
                ),
            ),
            input("cohorts", path=old["cohorts"]["path"], data_role="eval"),
        ]
        metric = refit_evaluation_metric()
        evaluated = execute(
            "evaluate",
            stage(
                evaluate_converged_readouts,
                stage_id="evaluate",
                eval_id="csts_converged_readouts",
                config=ConvergedEvaluationConfig(
                    device=settings["fit"]["device"],
                    progress_path=str(progress_path),
                    model_sha256=selection["model_sha256"],
                    selection_sha256=summary["selection_sha256"],
                    test_sha256=old["splits"]["test"]["sha256"],
                    cache_sha256=hashes["test"],
                    intervention_rows_sha256=old["interventions"]["sha256"],
                    intervention_cache_sha256=hashes["interventions"],
                    cohorts_sha256=old["cohorts"]["sha256"],
                    bootstrap_draws=settings["bootstrap_draws"],
                ),
                inputs=tuple(bindings),
                outputs=EvalOutputs(
                    report=output(
                        path="report.json", loader=load_json, data_role="eval"
                    ),
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                ),
                split_inputs=("holdout",),
                metrics=(metric,),
                objective=maximize(metric),
                reuse="never",
            ),
        )
        summary.update(
            status="complete",
            report=str(artifact_path(evaluated, "evaluate", "report", "report.json")),
        )
        _save(path, summary)
        with progress_path.open("a") as stream:
            stream.write("\nEvaluation status: succeeded.\n")
    except BaseException as exc:
        summary.update(status="failed", error_type=type(exc).__name__)
        _save(path, summary)
        progress.append("controller_failed", error_type=type(exc).__name__)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/csts-readout-convergence.json")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    settings = load_json(root / args.config)
    directory = root / "qwen_evidence_results" / args.attempt
    directory.mkdir(parents=True, exist_ok=True)
    with (
        (directory / "controller.lock").open("a") as controller,
        Path("/tmp/jep-gpu.lock").open("a") as gpu,
    ):
        fcntl.flock(controller.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(gpu.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not gpu_idle(settings["gpu_model"]):
            raise RuntimeError(
                "The expected A100 has an active process; preserve its work."
            )
        run(
            root,
            root / settings["previous_summary"],
            settings,
            directory,
            args.source_commit,
        )


if __name__ == "__main__":
    main()
