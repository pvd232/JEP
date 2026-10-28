"""Score the three sealed joint fits, publish their report, and retain receipts.

Run against the original clean fitting checkout. Native prediction stages retain
that checkout's scorer provenance. This orchestration file is copied into the
final publication so its analysis is independently reviewable.
"""

import argparse
import fcntl
import json
import shutil
import subprocess
import uuid
from pathlib import Path

import numpy as np
from csts_pilot.background_storage import _save, drain_publications, queue_publication
from csts_pilot.convergence import file_sha256
from csts_pilot.convergence_run import artifact_path
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout import metric_values, paired_intervals
from csts_pilot.evidence_readout_stages import (
    condition_diagnostics,
    family_diagnostics,
    paired_condition_diagnostics,
)
from csts_pilot.native_comparison import NativeScoreConfig, capture_native_comparison
from jep_pilot.loaders import load_json
from jep_pilot.stages import publish_evaluation_inputs
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)
from viper.storage import ViperCloudDestination, publish_resolved_files


def align_reference(rows, reference):
    """Join complete archived inputs, retaining an explicitly reported subset."""
    fields = (
        "group_id",
        "pair_id",
        "condition",
        "sentence1",
        "sentence2",
        "rating",
        "target",
    )
    current = {r["row_id"]: r for r in rows}
    archived = {r["row_id"]: r for r in reference}
    if len(current) != len(rows) or len(archived) != len(reference):
        raise ValueError("Prediction row identities must be unique.")
    shared = [r for r in rows if r["row_id"] in archived]
    if not shared or set(archived) - set(current):
        raise ValueError("Archived reference rows must belong to the frozen test.")
    for row in shared:
        if any(archived[row["row_id"]][key] != row[key] for key in fields):
            raise ValueError("Archived reference text or target changed.")
    values = np.asarray([archived[r["row_id"]]["prediction"] for r in shared])
    metric_values(shared, values)
    return shared, values


def contrast(rows, predictions, reference, draws=2000):
    """Report seed variation separately from paired source group uncertainty."""
    baseline = metric_values(rows, reference)
    metrics = {
        seed: metric_values(rows, values) for seed, values in predictions.items()
    }
    paired = {
        seed: {"native": values.tolist(), "reference": reference.tolist()}
        for seed, values in predictions.items()
    }
    intervals = paired_intervals(
        rows, paired, draws, 61028, {"native": 1, "reference": -1}
    )
    deltas = [v["spearman"] - baseline["spearman"] for v in metrics.values()]
    return {
        "rows": len(rows),
        "groups": len({r["group_id"] for r in rows}),
        "reference": baseline,
        "per_seed": metrics,
        "spearman_difference_per_seed": dict(zip(metrics, deltas, strict=True)),
        "mean_spearman_difference": float(np.mean(deltas)),
        "seed_difference_sample_std": float(np.std(deltas, ddof=1))
        if len(deltas) > 1
        else None,
        "group_bootstrap_95": intervals,
        "per_seed_group_bootstrap_95": {
            seed: paired_intervals(
                rows, {seed: arms}, draws, 61028, {"native": 1, "reference": -1}
            )
            for seed, arms in paired.items()
        },
    }


def edit_diagnostics(rows):
    cases = {}
    for row in rows:
        cases.setdefault(row["case"], {})[row["edit"]] = row["prediction"]
    return [
        {
            "case": case,
            "scores": values,
            "irrelevant_absolute_change": abs(values["irrelevant"] - values["base"]),
            "relevant_score_decrease": values["base"] - values["relevant"],
            "missing_score": values["missing"],
        }
        for case, values in cases.items()
    ]


def finalize(root, directory, summaries, published_test, historical, control_dir):
    directory.mkdir(parents=True, exist_ok=True)
    settings = load_json(root / "configs/csts-native-comparison.json")
    source, environment = read_source(root), observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    path = directory / "summary.json"
    summary = load_json(path) if path.exists() else {"status": "running", "runs": []}
    hardware = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
    ).strip()

    def execute(name, configured, gpu=False):
        previous = [r for r in summary["runs"] if r["name"] == name]
        if previous:
            if len(previous) != 1 or previous[0]["status"] != "succeeded":
                raise ValueError(
                    "Inspect an interrupted finalization stage before retrying."
                )
            return previous[0]
        if summary.get("in_flight"):
            raise ValueError(
                "Reconcile the recorded native invocation before retrying."
            )
        trial = experiment(
            experiment_id="csts_native_final_" + uuid.uuid4().hex[:12] + "_" + name,
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
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CUDAComputeSpec(model=hardware, count=1)
                    if gpu
                    else CPUComputeSpec(),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="gpu_runtime_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=7200,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        if result.status != "succeeded":
            summary["status"] = "failed"
            _save(path, summary)
            raise RuntimeError("Finalization failed: " + name)
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        _save(path, summary)
        return record

    def archive(name, left, right, role="training"):
        return execute(
            name,
            stage(
                publish_evaluation_inputs,
                stage_id="archive",
                config=BuildConfig(),
                inputs=(input("test", source=left), input("holdout", source=right)),
                outputs=StageOutputs(
                    **{
                        key: output(
                            path=key + ".json", loader=load_json, data_role=role
                        )
                        for key in ("test", "holdout")
                    }
                ),
                reuse="never",
            ),
        )

    if set(summaries) != {"7", "8", "9"}:
        raise ValueError("Finalize the declared executed seed set together.")
    traces, models = {}, {}
    for seed, fitted in summaries.items():
        if (
            fitted.get("status") != "succeeded"
            or fitted.get("cloud_status") != "published"
            or fitted.get("seed") != int(seed)
        ):
            raise ValueError(
                "Every selected fit must have completed Cloud publication."
            )
        record = dict(
            fitted["terminal"], reference=fitted["terminal"]["cloud_reference"]
        )
        models[seed] = record
        archived = archive(
            "fit_state_" + seed,
            stored_source(record, "train", "trace", "test"),
            stored_source(record, "train", "checkpoint_receipts", "holdout"),
        )
        trace = load_json(artifact_path(archived, "archive", "test", "test.json"))
        receipts = load_json(
            artifact_path(archived, "archive", "holdout", "holdout.json")
        )
        if (
            trace["budget_censored"]
            or trace["selected"]["sha256"] != fitted["selected"]["sha256"]
        ):
            raise ValueError(
                "Final evaluation requires completed and matching selections."
            )
        if (
            receipts.get("status") != "published"
            or not receipts.get("publications")
            or any(r["status"] != "published" for r in receipts["publications"])
        ):
            raise ValueError("Each fitting checkpoint requires a publication receipt.")
        traces[seed] = trace
    selection = {
        "executed_seeds": [7, 8, 9],
        "selected_model_sha256": {
            s: v["selected"]["sha256"] for s, v in summaries.items()
        },
        "fitting_source_commits": {s: v["source_commit"] for s, v in summaries.items()},
        "settings_sha256": file_sha256(root / "configs/csts-native-comparison.json"),
        "follow_on_summary": "Conditional on seed 7 crossing the validation reference.",
    }
    selection_path = directory / "selection.json"
    if selection_path.exists() and load_json(selection_path) != selection:
        raise ValueError("The frozen executed seed list and selected states changed.")
    _save(selection_path, selection)
    # All models and the executed seed list are frozen above this boundary.
    published = {"reference": published_test}
    archived = archive(
        "test_inputs",
        stored_source(published, "publish", "test", "test", "eval"),
        stored_source(published, "publish", "holdout", "holdout", "eval"),
        "eval",
    )
    rows_path = artifact_path(archived, "archive", "test", "test.json")
    rows = load_json(rows_path)
    if (
        file_sha256(rows_path) != settings["splits"]["test"]["sha256"]
        or len(rows) != 2431
    ):
        raise ValueError("Test input bytes differ from the declared current cohort.")
    if load_json(artifact_path(archived, "archive", "holdout", "holdout.json")) != list(
        range(len(rows))
    ):
        raise ValueError("Test indices must cover the complete frozen cohort.")
    training_groups = {
        r["group_id"]
        for split in ("training", "validation")
        for r in load_json(root / settings["splits"][split]["path"])
    }
    if training_groups & {r["group_id"] for r in rows}:
        raise ValueError("Test source groups overlap fitting groups.")
    predictions, edits, diagnostics = {}, {}, {}
    for seed in summaries:
        for split in ("test", "edits"):
            if split == "test":
                rows_binding = input(
                    "rows",
                    source=stored_source(archived, "archive", "test", "rows", "eval"),
                )
                digest = settings["splits"]["test"]["sha256"]
            else:
                rows_binding = input(
                    "rows", path=settings["interventions"]["path"], data_role="eval"
                )
                digest = settings["interventions"]["sha256"]
            scored = execute(
                "score_" + seed + "_" + split,
                stage(
                    capture_native_comparison,
                    stage_id="predict",
                    config=NativeScoreConfig(
                        **settings["encoder"],
                        model_sha256=selection["selected_model_sha256"][seed],
                        rows_sha256=digest,
                        selection_sha256=file_sha256(selection_path),
                    ),
                    inputs=(
                        input(
                            "model",
                            source=stored_source(
                                models[seed], "train", "model", "model"
                            ),
                        ),
                        input(
                            "selection",
                            path=selection_path.relative_to(root).as_posix(),
                            data_role="training",
                        ),
                        rows_binding,
                    ),
                    outputs=StageOutputs(
                        **{
                            name: output(
                                path=name + ".json", loader=load_json, data_role="eval"
                            )
                            for name in ("predictions", "diagnostics")
                        }
                    ),
                    reuse="never",
                ),
                gpu=True,
            )
            values = load_json(
                artifact_path(scored, "predict", "predictions", "predictions.json")
            )
            if split == "test":
                checked, values_array = align_reference(rows, values)
                if len(checked) != len(rows):
                    raise ValueError("Native scoring must cover every frozen test row.")
                predictions[seed] = values_array
                diagnostics[seed] = load_json(
                    artifact_path(scored, "predict", "diagnostics", "diagnostics.json")
                )
            else:
                edits[seed] = edit_diagnostics(values)
    # CPU reporting uses the sealed predictions from the native BUILD stages.
    control = load_json(control_dir / "ratings_predictions.json")
    shared, reference = align_reference(rows, control)
    index = {r["row_id"]: i for i, r in enumerate(rows)}
    subset = {
        s: p[[index[r["row_id"]] for r in shared]] for s, p in predictions.items()
    }
    cohorts_path = root / "datasets/csts-proposition-evidence-report-cohorts.json"
    if (
        file_sha256(cohorts_path)
        != "7c5eaf349e6ef863db85b185f8f0c4e1f5192cf036a705eb79bd5435ced211a3"
    ):
        raise ValueError("The declared condition families changed.")
    cohorts = load_json(cohorts_path)
    report = {
        "selection": selection,
        "input_sha256": {
            "test": settings["splits"]["test"]["sha256"],
            "ratings_control_predictions": file_sha256(
                control_dir / "ratings_predictions.json"
            ),
            "cohorts": file_sha256(cohorts_path),
        },
        "results": {s: metric_values(rows, p) for s, p in predictions.items()},
        "primary_against_saved_ratings_control": contrast(
            shared, subset, reference, settings["bootstrap_draws"]
        ),
        "coverage": {
            "current_rows": len(rows),
            "reference_rows": len(control),
            "common_rows": len(shared),
            "excluded_current_row_ids": [
                r["row_id"]
                for r in rows
                if r["row_id"] not in {x["row_id"] for x in shared}
            ],
        },
        "interventions": edits,
        "diagnostics": diagnostics,
        "condition_ordering": {
            s: paired_condition_diagnostics(rows, p) for s, p in predictions.items()
        },
        "condition_families": {
            s: family_diagnostics(rows, p, cohorts) for s, p in predictions.items()
        },
        "conditions": {
            s: condition_diagnostics(rows, p) for s, p in predictions.items()
        },
        "selected_and_terminal_epochs": {
            s: {"selected": t["selected"], "terminal": t["completed_epoch"]}
            for s, t in traces.items()
        },
        "scope": "Exploratory existing test cohort; source group intervals condition on retained models. The three seed summary is conditional on the initial validation result. The historical ratings control retains its original training history.",
    }
    report["mean"] = {
        key: float(np.mean([v[key] for v in report["results"].values()]))
        for key in ("spearman", "mse_0_1")
    }
    report["seed_sample_std_spearman"] = float(
        np.std([v["spearman"] for v in report["results"].values()], ddof=1)
    )
    secondary = archive(
        "historical_predictions",
        stored_source(
            {"reference": historical}, "evaluate", "predictions", "test", "eval"
        ),
        stored_source(published, "publish", "holdout", "holdout", "eval"),
        "eval",
    )
    old = load_json(artifact_path(secondary, "archive", "test", "test.json"))
    if old["row_ids"] != [r["row_id"] for r in rows]:
        raise ValueError("Historical secondary predictions use another row order.")
    # A has one retained encoder; its learned comparisons have three head seeds.
    a = np.asarray(old["seeds"]["7"]["A_parent"])
    report["secondary_A"] = contrast(rows, predictions, a, settings["bootstrap_draws"])
    report["secondary_A_comparison"] = {
        "per_seed": {
            s: metric_values(rows, old["seeds"][s]["parent_comparison"])
            for s in summaries
        },
        "native_mean_spearman": float(
            np.mean([v["spearman"] for v in report["results"].values()])
        ),
        "historical_mean_spearman": float(
            np.mean(
                [
                    metric_values(rows, old["seeds"][s]["parent_comparison"])[
                        "spearman"
                    ]
                    for s in summaries
                ]
            )
        ),
        "group_bootstrap_95": paired_intervals(
            rows,
            {
                s: {
                    "native": predictions[s].tolist(),
                    "reference": old["seeds"][s]["parent_comparison"],
                }
                for s in summaries
            },
            settings["bootstrap_draws"],
            61028,
            {"native": 1, "reference": -1},
        ),
    }
    _save(directory / "results.json", report)
    _save(directory / "fit-traces.json", traces)
    _save(
        directory / "predictions.json",
        {
            "row_ids": [r["row_id"] for r in rows],
            "seeds": {s: p.tolist() for s, p in predictions.items()},
        },
    )
    shutil.copyfile(__file__, directory / "finalize.py")
    for name in (
        "selection.json",
        "ratings_ratings_trace.json",
        "checkpoint_manifest.json",
        "summary.json",
        "ratings_predictions.json",
    ):
        shutil.copyfile(control_dir / name, directory / ("control_" + name))
    text = "# Fresh Qwen LoRA and learned comparison\n\nAll three fits completed validation stopping.\n\n| Seed | Test Spearman | Normalized MSE | Selected epoch | Terminal epoch |\n| --- | --- | --- | --- | --- |\n"
    for seed, metrics in report["results"].items():
        text += f"| {seed} | {metrics['spearman']:.9f} | {metrics['mse_0_1']:.9f} | {traces[seed]['selected']['epoch']} | {traces[seed]['completed_epoch']} |\n"
    primary = report["primary_against_saved_ratings_control"]
    ci = primary["group_bootstrap_95"]
    text += f"| Mean | {report['mean']['spearman']:.9f} | {report['mean']['mse_0_1']:.9f} | | |\n"
    text += f"\nOn the {len(shared):,} verified common rows, mean Spearman gain over the saved ratings control is **{primary['mean_spearman_difference']:.6f}**, with paired source group 95% interval **[{ci['low']:.6f}, {ci['high']:.6f}]** from 2,000 draws.\n\n"
    text += (
        report["scope"]
        + "\n\n[Methods](../../plans/csts-native-comparison-methods.md) · [Full results and diagnostics](results.json) · [Fit traces](fit-traces.json) · [Cloud receipts](cloud-receipts.json)\n"
    )
    (directory / "results.md").write_text(text)
    drain_publications(root, retry_failed=True)
    for record in summary["runs"]:
        receipt = load_json(Path(record["publication_queue"]))
        if receipt["status"] != "published":
            raise RuntimeError(
                "Retain the final worker until all native publications complete."
            )
        record["cloud_reference"] = receipt["reference"]
    summary.update(
        status="complete",
        cloud_status="published",
        report=str(directory / "results.json"),
    )
    _save(path, summary)
    _save(
        directory / "cloud-receipts.json",
        {"fitting": summaries, "finalization": summary},
    )
    refs = publish_resolved_files(
        root,
        destination,
        {
            "csts_native_comparison_20261028/final/" + p.name: p
            for p in directory.iterdir()
            if p.is_file() and p.name != "final-publication.json"
        },
    )
    _save(
        directory / "final-publication.json",
        {
            "status": "published",
            "references": {k: v.model_dump(mode="json") for k, v in refs.items()},
        },
    )
    print(
        "NATIVE_FINALIZATION_COMPLETE",
        json.dumps({"directory": str(directory), "primary": primary}),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--summaries", required=True, type=Path)
    parser.add_argument("--references", required=True, type=Path)
    args = parser.parse_args()
    refs = load_json(args.references)
    with Path("/tmp/jep-gpu.lock").open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
            text=True,
        ).strip():
            raise RuntimeError("The final scoring GPU has another active process.")
        finalize(
            args.root,
            args.root / "qwen_evidence_results/native_final_20261028",
            load_json(args.summaries),
            refs["published_test"],
            refs["historical_evaluation"],
            Path(refs["ratings_control_directory"]),
        )


if __name__ == "__main__":
    main()
