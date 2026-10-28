"""Aggregate sealed inference results on CPU, retaining the observed budgets."""

import argparse
import importlib.util
import shutil
import time
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
from jep_pilot.loaders import load_json
from jep_pilot.stages import publish_evaluation_inputs
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef, ResolvedFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloud, ViperCloudDestination, publish_resolved_files


def report(root, references_path, scores_path, helper_path):
    spec = importlib.util.spec_from_file_location(
        "checked_comparison_analysis", helper_path
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    references = load_json(references_path)
    settings = load_json(root / "configs/csts-native-comparison.json")
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    directory = root / "qwen_evidence_results/native_final_20261028"
    directory.mkdir(parents=True, exist_ok=True)
    source, environment = read_source(root), observe_python_env()
    context_path = directory / "report-context.json"
    if context_path.exists():
        context = load_json(context_path)
    else:
        fitted = references["seed8_fitting"]
        configured = stage(
            publish_evaluation_inputs,
            stage_id="archive",
            config=BuildConfig(),
            inputs=(
                input(
                    "test",
                    source=stored_source(
                        {"reference": fitted["terminal"]["cloud_reference"]},
                        "train",
                        "trace",
                        "test",
                    ),
                ),
                input(
                    "holdout",
                    source=stored_source(
                        {"reference": references["historical_evaluation"]},
                        "evaluate",
                        "predictions",
                        "holdout",
                        "eval",
                    ),
                ),
            ),
            outputs=StageOutputs(
                **{
                    k: output(path=k + ".json", loader=load_json, data_role="eval")
                    for k in ("test", "holdout")
                }
            ),
            reuse="never",
        )
        trial = experiment(
            experiment_id="csts_saved_report_context_" + uuid.uuid4().hex[:10],
            variants=(
                variant(
                    "context",
                    stages=(configured,),
                    estimator=configured.outputs["test"],
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CPUComputeSpec(),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="gpu_runtime_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=3600,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        if result.status != "succeeded":
            raise RuntimeError("Inspect the retained CPU context archive.")
        context = {
            "reference": result.reference.model_dump(mode="json"),
            "path": str(result.path),
            "publication_queue": str(
                queue_publication(root, result.reference, destination)
            ),
        }
        _save(context_path, context)
    trace8 = load_json(artifact_path(context, "archive", "test", "test.json"))
    old = load_json(artifact_path(context, "archive", "holdout", "holdout.json"))
    print("CPU_REPORT_CONTEXT_READY", flush=True)
    while not scores_path.exists():
        time.sleep(2)
    scores = load_json(scores_path)
    if set(scores) != {"7", "8", "9"}:
        raise ValueError("Retain all three executed seeds in the report.")
    rows_path = root / settings["splits"]["test"]["path"]
    if file_sha256(rows_path) != settings["splits"]["test"]["sha256"]:
        raise ValueError("The test cohort changed.")
    rows = load_json(rows_path)
    fitting_groups = {
        r["group_id"]
        for split in ("training", "validation")
        for r in load_json(root / settings["splits"][split]["path"])
    }
    if fitting_groups & {r["group_id"] for r in rows}:
        raise ValueError("Test source groups overlap fitting groups.")

    def fetch(reference, target):
        ref = ResolvedFileRef.model_validate(reference)
        ViperCloud.for_reference(root, ref.stored_at).fetch_to_path(ref, target)
        return load_json(target)

    predictions, edits, diagnostics, traces = {}, {}, {}, {"8": trace8}
    for seed, completed in scores.items():
        summary, publication = completed["summary"], completed["publication"]
        if (
            summary["status"] != "complete"
            or summary["cloud_status"] != "published"
            or publication["status"] != "published"
        ):
            raise ValueError("Prediction publication must complete before aggregation.")
        values = {}
        for filename in (
            "test_predictions.json",
            "test_diagnostics.json",
            "edits_predictions.json",
        ):
            reference = next(
                v
                for k, v in publication["references"].items()
                if k.endswith("/" + filename)
            )
            values[filename] = fetch(
                reference, directory / ("seed" + seed + "_" + filename)
            )
        metadata = values["test_diagnostics.json"]
        if (
            metadata["model_sha256"] != summary["selected_model_sha256"]
            or metadata["rows_sha256"] != settings["splits"]["test"]["sha256"]
        ):
            raise ValueError("Selected model or test metadata changed.")
        shared, array = helper.align_reference(rows, values["test_predictions.json"])
        if len(shared) != len(rows):
            raise ValueError("Each saved model must cover the complete frozen test.")
        if (
            abs(metric_values(rows, array)["spearman"] - summary["test"]["spearman"])
            > 1e-12
        ):
            raise ValueError("Published test metrics disagree with predictions.")
        predictions[seed], diagnostics[seed] = array, metadata
        edits[seed] = helper.edit_diagnostics(values["edits_predictions.json"])
        if seed != "8":
            retained = summary["selection"]["retained_checkpoint"]
            reference = next(
                v
                for k, v in retained["checkpoint_receipt"]["references"].items()
                if k.endswith("/trace.json")
            )
            traces[seed] = fetch(
                reference, directory / ("seed" + seed + "_retained_trace.json")
            )
    control_dir = Path(references["ratings_control_directory"])
    control = load_json(control_dir / "ratings_predictions.json")
    shared, baseline = helper.align_reference(rows, control)
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
    draws = settings["bootstrap_draws"]
    results = {s: metric_values(rows, p) for s, p in predictions.items()}
    report = {
        "results": results,
        "mean": {
            k: float(np.mean([m[k] for m in results.values()]))
            for k in ("spearman", "mse_0_1")
        },
        "seed_sample_std_spearman": float(
            np.std([m["spearman"] for m in results.values()], ddof=1)
        ),
        "primary_against_saved_ratings_control": helper.contrast(
            shared, subset, baseline, draws
        ),
        "coverage": {
            "current_rows": len(rows),
            "reference_rows": len(control),
            "common_rows": len(shared),
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
        "selected_and_retained_epochs": {
            s: {
                "selected": scores[s]["summary"]["selected_epoch"],
                "retained": scores[s]["summary"]["terminal_epoch"],
                "training_status": scores[s]["summary"].get(
                    "training_status", "validation_patience_complete"
                ),
            }
            for s in scores
        },
        "input_sha256": {
            "test": file_sha256(rows_path),
            "ratings_control_predictions": file_sha256(
                control_dir / "ratings_predictions.json"
            ),
            "cohorts": file_sha256(cohorts_path),
        },
        "scope": "The user ended seeds 7 and 9 after seed 8 test reporting and requested inference from their existing validation selections. Seed 8 completed the original stopping rule. The three seed summary is conditional on the initial validation decision. Intervals describe test source uncertainty for these retained models. The historical control retains its original training history.",
    }
    if old["row_ids"] != [r["row_id"] for r in rows]:
        raise ValueError("Historical prediction order changed.")
    report["secondary_A"] = helper.contrast(
        rows, predictions, np.asarray(old["seeds"]["7"]["A_parent"]), draws
    )
    report["secondary_A_comparison"] = {
        "per_seed": {
            s: metric_values(rows, old["seeds"][s]["parent_comparison"]) for s in scores
        },
        "native_mean_spearman": report["mean"]["spearman"],
        "historical_mean_spearman": float(
            np.mean(
                [
                    metric_values(rows, old["seeds"][s]["parent_comparison"])[
                        "spearman"
                    ]
                    for s in scores
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
                for s in scores
            },
            draws,
            61028,
            {"native": 1, "reference": -1},
        ),
    }
    _save(directory / "results.json", report)
    _save(directory / "fit-traces.json", traces)
    _save(
        directory / "selection.json",
        {s: v["summary"]["selection"] for s, v in scores.items()},
    )
    _save(
        directory / "predictions.json",
        {
            "row_ids": old["row_ids"],
            "seeds": {s: p.tolist() for s, p in predictions.items()},
        },
    )
    text = "# Fresh Qwen LoRA and learned comparison\n\nSaved validation selections received test inference. The user ended the remaining training budgets after seed 8 test reporting.\n\n| Seed | Test Spearman | Normalized MSE | Selected epoch | Retained epoch |\n| --- | --- | --- | --- | --- |\n"
    for seed, metrics in results.items():
        summary = scores[seed]["summary"]
        text += f"| {seed} | {metrics['spearman']:.9f} | {metrics['mse_0_1']:.9f} | {summary['selected_epoch']} | {summary['terminal_epoch']} |\n"
    text += f"| Mean | {report['mean']['spearman']:.9f} | {report['mean']['mse_0_1']:.9f} | | |\n"
    primary = report["primary_against_saved_ratings_control"]
    ci = primary["group_bootstrap_95"]
    text += f"\nOn {len(shared):,} verified common test rows, mean Spearman gain over the saved ratings control is **{primary['mean_spearman_difference']:.6f}**, with paired source group 95% interval **[{ci['low']:.6f}, {ci['high']:.6f}]** from 2,000 draws.\n\n"
    text += (
        report["scope"]
        + "\n\n[Methods](../../plans/csts-native-comparison-methods.md) · [Diagnostics](results.json) · [Fit traces](fit-traces.json) · [Cloud receipts](cloud-receipts.json)\n"
    )
    (directory / "results.md").write_text(text)
    shutil.copyfile(__file__, directory / "report.py")
    shutil.copyfile(helper_path, directory / "analysis_helpers.py")
    drain_publications(root, retry_failed=True)
    receipt = load_json(Path(context["publication_queue"]))
    if receipt["status"] != "published":
        raise RuntimeError(
            "Retain the report worker until its context publication completes."
        )
    _save(
        directory / "cloud-receipts.json",
        {
            "inference": scores,
            "context_archive": receipt,
            "historical_evaluation": references["historical_evaluation"],
        },
    )
    _save(
        directory / "summary.json",
        {"status": "complete", "cloud_status": "published", "mean": report["mean"]},
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
    print("SAVED_CHECKPOINT_REPORT_COMPLETE", report["mean"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "references", "scores", "helpers"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    report(args.root, args.references, args.scores, args.helpers)


if __name__ == "__main__":
    main()
