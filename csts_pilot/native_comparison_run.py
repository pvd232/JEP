"""Execute one reviewed joint fit using native VIPER transport and publication."""

import argparse
import fcntl
import json
import subprocess
import uuid
from pathlib import Path

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloudDestination, publish_resolved_files

from csts_pilot.background_storage import _save, drain_publications, queue_publication
from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
)
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_readout_run import checked_source, gpu_idle
from csts_pilot.native_comparison import NativeComparisonConfig, fit_native_comparison
from jep_pilot.loaders import load_json, load_model, load_state


def fit_outputs():
    return TrainOutputs(
        **{
            name: output(path=filename, loader=loader, data_role="training")
            for name, filename, loader in (
                ("model", "model.pt", load_model),
                ("last_model", "last_model.pt", load_model),
                ("resume_state", "resume.pt", load_state),
                ("trace", "trace.json", load_json),
                ("validation_predictions", "predictions.json", load_json),
                ("initial_vectors", "initial_vectors.pt", load_model),
                ("checkpoint_receipts", "checkpoint_receipts.json", load_json),
            )
        }
    )


def matching_predictions(predictions, rows):
    """Join exact input identities and targets while retaining declared row order."""
    fields = ("condition", "sentence1", "sentence2", "target")
    lookup = {r["row_id"]: r for r in predictions}
    if len(lookup) != len(predictions) or set(lookup) != {r["row_id"] for r in rows}:
        raise ValueError("Validation reference must cover the identical frozen rows.")
    result = []
    for row in rows:
        reference = lookup[row["row_id"]]
        if any(reference[k] != row[k] for k in fields):
            raise ValueError("Reference text or target differs from the frozen input.")
        result.append(reference)
    return result


def continuation_decision(training_rows, reference_rows, validation_rows):
    """Use full precision validation Spearman to release the two follow on seeds."""
    trained = summarize(matching_predictions(training_rows, validation_rows))
    reference = summarize(matching_predictions(reference_rows, validation_rows))
    if trained["spearman"] is None or reference["spearman"] is None:
        raise ValueError("The continuation comparison requires defined correlations.")
    gain = trained["spearman"] - reference["spearman"]
    return {
        "status": "positive" if gain > 0 else "initial_trial_complete",
        "metric": "validation Spearman",
        "seed7": trained,
        "ratings_control": reference,
        "difference": gain,
        "follow_on_seeds": [8, 9] if gain > 0 else [],
        "test_scores_used": False,
    }


def run_fit(root, settings, directory, commit, seed, gate_path=None):
    checked_source(root, commit)
    if seed not in (7, 8, 9):
        raise ValueError("Use a declared study seed.")
    if seed != 7:
        gate = load_json(gate_path) if gate_path else {}
        if (
            gate.get("status") != "positive"
            or seed not in gate.get("follow_on_seeds", [])
            or gate.get("settings_sha256")
            != file_sha256(root / "configs/csts-native-comparison.json")
        ):
            raise ValueError(
                "Follow on seeds require the saved positive validation decision under this configuration."
            )
    directory.mkdir(parents=True, exist_ok=False)
    hardware = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
    ).strip()
    if not gpu_idle(hardware):
        raise RuntimeError("The selected GPU has another active job.")
    source, environment = read_source(root), observe_python_env()
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    report = directory / "progress.md"
    report.write_text(
        f"# Joint LoRA and comparison training\n\nSeed: {seed}. Hardware: {hardware}. Source: `{commit}`.\n\n| UTC | Event | Seed | Epoch | Progress |\n| --- | --- | --- | --- | --- |\n"
    )
    summary = {
        "status": "running",
        "seed": seed,
        "source_commit": commit,
        "hardware": hardware,
        "runs": [],
        "in_flight": None,
    }
    summary_path = directory / "summary.json"
    parent = None
    ceiling = settings["training"]["max_epochs"]
    start_epoch = 0
    while True:
        config = NativeComparisonConfig(
            **settings["encoder"],
            **{
                **settings["training"],
                "max_epochs": ceiling,
                "start_epoch": start_epoch,
            },
            seed=seed,
            checkpoint_root=str(root),
            checkpoint_destination=destination.model_dump(mode="json"),
            progress_path=str(report),
            **{
                s + "_sha256": settings["splits"][s]["sha256"]
                for s in ("training", "validation")
            },
        )
        bindings = [
            input(s, path=settings["splits"][s]["path"], data_role="training")
            for s in ("training", "validation")
        ]
        if parent is not None:
            bindings.extend(
                input(binding, source=artifact_source(parent, "train", name))
                for binding, name in (
                    ("parent_last_model", "last_model"),
                    ("parent_resume", "resume_state"),
                    ("parent_model", "model"),
                    ("parent_validation_predictions", "validation_predictions"),
                    ("parent_initial_vectors", "initial_vectors"),
                )
            )
        metrics = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        configured = stage(
            fit_native_comparison,
            stage_id="train",
            config=config,
            inputs=tuple(bindings),
            outputs=fit_outputs(),
            metrics=metrics,
            objective=maximize(metrics[-1]),
            reuse="never",
        )
        identity = (
            f"csts_native_{commit[:8]}_s{seed}_e{start_epoch}_{uuid.uuid4().hex[:8]}"
        )
        trial = experiment(
            experiment_id=identity,
            variants=(
                variant(
                    "joint", stages=(configured,), estimator=configured.outputs["model"]
                ),
            ),
            replicates=(replicate(seed=seed),),
        )
        summary["in_flight"] = {"experiment_id": identity, "start_epoch": start_epoch}
        _save(summary_path, summary)
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CUDAComputeSpec(model=hardware, count=1),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="gpu_runtime_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=settings["stage_timeout_seconds"],
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": f"joint_seed{seed}_epoch{start_epoch}",
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        if result.status != "succeeded":
            summary["status"] = "failed"
            _save(summary_path, summary)
            raise RuntimeError(
                "Native fit failed; retain its epoch checkpoint publications."
            )
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        trace = load_json(artifact_path(record, "train", "trace", "trace.json"))
        summary["selected"] = trace["selected"]
        summary["trace"] = str(artifact_path(record, "train", "trace", "trace.json"))
        _save(summary_path, summary)
        if not trace["budget_censored"]:
            break
        parent, start_epoch = record, trace["completed_epoch"]
        ceiling += settings["training"]["max_epochs"]
    summary.update(
        status="succeeded",
        terminal=record,
        selected_model=str(artifact_path(record, "train", "model", "model.pt")),
        validation_predictions=str(
            artifact_path(record, "train", "validation_predictions", "predictions.json")
        ),
    )
    if seed == 7:
        reference = root / settings["ratings_validation_predictions"]
        gate = continuation_decision(
            load_json(Path(summary["validation_predictions"])),
            load_json(reference),
            load_json(root / settings["splits"]["validation"]["path"]),
        )
        gate.update(
            settings_sha256=file_sha256(root / "configs/csts-native-comparison.json"),
            validation_sha256=settings["splits"]["validation"]["sha256"],
            reference_predictions_sha256=file_sha256(reference),
            model_sha256=summary["selected"]["sha256"],
            source_commit=commit,
        )
        _save(directory / "continuation.json", gate)
        summary["continuation"] = gate
    _save(summary_path, summary)
    # Fitting has ended. The worker remains owned until every native run is durable.
    drain_publications(root, retry_failed=True)
    for item in summary["runs"]:
        publication = load_json(Path(item["publication_queue"]))
        if publication["status"] != "published":
            raise RuntimeError(
                "Keep this worker until its native run publication succeeds."
            )
        item["cloud_reference"] = publication["reference"]
    summary["cloud_status"] = "published"
    _save(summary_path, summary)
    files = {
        f"csts_native_comparison_20261028/seed{seed}/{directory.name}/{name}": path
        for name, path in {
            "summary.json": summary_path,
            "progress.md": report,
            **(
                {"continuation.json": directory / "continuation.json"}
                if seed == 7
                else {}
            ),
        }.items()
    }
    refs = publish_resolved_files(root, destination, files)
    _save(
        directory / "final-publication.json",
        {
            "status": "published",
            "references": {
                name: ref.model_dump(mode="json") for name, ref in refs.items()
            },
        },
    )
    print(
        json.dumps(
            {
                "seed": seed,
                "status": summary["status"],
                "selected": summary["selected"],
                "cloud_status": summary["cloud_status"],
                "continuation": summary.get("continuation"),
            }
        ),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--gate", type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    lock_path = Path("/tmp/jep-gpu.lock")
    if not lock_path.exists():
        lock_path.touch(mode=0o664)
    with lock_path.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_fit(
            root,
            load_json(root / "configs/csts-native-comparison.json"),
            args.output,
            args.commit,
            args.seed,
            args.gate,
        )


if __name__ == "__main__":
    main()
