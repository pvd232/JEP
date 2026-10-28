"""Score an existing published validation checkpoint after training is stopped."""

import argparse
import fcntl
import shutil
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from csts_pilot.background_storage import _save, drain_publications, queue_publication
from csts_pilot.convergence import file_sha256
from csts_pilot.convergence_run import artifact_path
from csts_pilot.diagnostics import summarize
from csts_pilot.native_comparison import NativeScoreConfig, capture_native_comparison
from jep_pilot.loaders import load_json
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef, ResolvedFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloud, ViperCloudDestination, publish_resolved_files


def score(root, record_path, test_reference, reporting_commit):
    retained = load_json(record_path)
    settings = load_json(root / "configs/csts-native-comparison.json")
    seed = retained["seed"]
    receipt = retained["checkpoint_receipt"]
    if receipt["status"] != "published" or receipt["state"]["seed"] != seed:
        raise ValueError("Scoring requires the retained seed's published checkpoint.")
    selected = retained["selected"]
    model = Path(retained["model_path"])
    model_ref = next(
        v for k, v in receipt["references"].items() if k.endswith("/model.pt")
    )
    if (
        model_ref["sha256"] != selected["sha256"]
        or file_sha256(model) != selected["sha256"]
    ):
        raise ValueError("The retained checkpoint must match validation selection.")
    frozen_model = root / "csts_data/native" / f"retained_seed{seed}_model.pt"
    frozen_model.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(model, frozen_model)
    model = frozen_model
    rows = root / settings["splits"]["test"]["path"]
    if not rows.exists():
        rows.parent.mkdir(parents=True, exist_ok=True)
        reference = ResolvedFileRef.model_validate(test_reference)
        ViperCloud.for_reference(root, reference.stored_at).fetch_to_path(
            reference, rows
        )
    if file_sha256(rows) != settings["splits"]["test"]["sha256"]:
        raise ValueError("The frozen test input hash changed.")
    directory = root / "qwen_evidence_results" / f"native_seed{seed}_test_20261028"
    directory.mkdir(parents=True, exist_ok=False)
    selection = {
        "executed_seeds": [7, 8, 9],
        "selected_model_sha256": {str(seed): selected["sha256"]},
        "selection": selected,
        "training_status": "stopped_by_request",
        "stopping_amendment": "Score the existing best validation checkpoints immediately.",
        "amendment_after_seed8_test": True,
        "retained_checkpoint": retained,
        "reporting_source_commit": reporting_commit,
        "test_reference": test_reference,
    }
    selected_path = directory / "selection.json"
    _save(selected_path, selection)
    shutil.copyfile(__file__, directory / "score.py")
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    prefix = f"csts_native_comparison_20261028/seed{seed}/completed_test"
    pool = ThreadPoolExecutor(max_workers=1)
    evidence = pool.submit(
        publish_resolved_files,
        root,
        destination,
        {prefix + "/" + n: directory / n for n in ("selection.json", "score.py")},
    )
    source, environment = read_source(root), observe_python_env()
    hardware = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
    ).strip()
    summary = {
        "status": "scoring",
        "seed": seed,
        "selected_model_sha256": selected["sha256"],
        "selected_epoch": selected["epoch"],
        "terminal_epoch": retained["completed_epoch"],
        "training_status": "stopped_by_request",
        "selection": selection,
        "test_sha256": settings["splits"]["test"]["sha256"],
        "runs": {},
    }
    try:
        for split in ("test", "edits"):
            row_path = (
                rows if split == "test" else root / settings["interventions"]["path"]
            )
            row_sha = (
                settings["splits"]["test"]["sha256"]
                if split == "test"
                else settings["interventions"]["sha256"]
            )
            configured = stage(
                capture_native_comparison,
                stage_id="predict",
                config=NativeScoreConfig(
                    **settings["encoder"],
                    model_sha256=selected["sha256"],
                    rows_sha256=row_sha,
                    selection_sha256=file_sha256(selected_path),
                ),
                inputs=(
                    input(
                        "model",
                        path=model.relative_to(root).as_posix(),
                        data_role="training",
                    ),
                    input(
                        "selection",
                        path=selected_path.relative_to(root).as_posix(),
                        data_role="training",
                    ),
                    input(
                        "rows",
                        path=row_path.relative_to(root).as_posix(),
                        data_role="eval",
                    ),
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
            )
            identity = f"native_snapshot_s{seed}_{split}_{uuid.uuid4().hex[:10]}"
            summary["in_flight"] = identity
            _save(directory / "summary.json", summary)
            trial = experiment(
                experiment_id=identity,
                variants=(
                    variant(
                        split,
                        stages=(configured,),
                        estimator=configured.outputs["predictions"],
                    ),
                ),
                replicates=(replicate(seed=seed),),
            )
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
                timeout_seconds=3600,
                trusted_source_repositories=frozenset({str(source.repository)}),
            )
            record = {
                "name": split,
                "status": result.status,
                "path": str(result.path),
                "reference": result.reference.model_dump(mode="json"),
            }
            summary["runs"][split] = record
            if result.status != "succeeded":
                raise RuntimeError("Saved checkpoint inference failed.")
            record["publication_queue"] = str(
                queue_publication(root, result.reference, destination)
            )
            for name in ("predictions", "diagnostics"):
                shutil.copyfile(
                    artifact_path(record, "predict", name, name + ".json"),
                    directory / (split + "_" + name + ".json"),
                )
            if split == "test":
                summary["test"] = summarize(
                    load_json(directory / "test_predictions.json")
                )
                if summary["test"]["n"] != settings["splits"]["test"]["rows"]:
                    raise ValueError("Test prediction coverage changed.")
                print(
                    "COMPLETED_TEST_SCORE",
                    seed,
                    summary["test"]["spearman"],
                    flush=True,
                )
            summary["in_flight"] = None
            _save(directory / "summary.json", summary)
        refs = evidence.result()
        pool.shutdown(wait=True)
        _save(
            directory / "selection-publication.json",
            {
                "status": "published",
                "references": {k: v.model_dump(mode="json") for k, v in refs.items()},
            },
        )
        drain_publications(root, retry_failed=True)
        for record in summary["runs"].values():
            publication = load_json(Path(record["publication_queue"]))
            if publication["status"] != "published":
                raise RuntimeError(
                    "Retain the runtime until prediction publication completes."
                )
            record["cloud_reference"] = publication["reference"]
        summary.update(status="complete", cloud_status="published")
        _save(directory / "summary.json", summary)
        refs = publish_resolved_files(
            root,
            destination,
            {
                prefix + "/" + p.name: p
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
    except Exception as error:
        summary.update(status="failed", error_type=type(error).__name__)
        _save(directory / "summary.json", summary)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "selection", "test-reference"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--reporting-commit", required=True)
    args = parser.parse_args()
    with Path("/tmp/jep-gpu.lock").open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        active = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
            text=True,
        ).strip()
        if active:
            raise RuntimeError("Release the stopped training process before inference.")
        score(
            args.root,
            args.selection,
            load_json(args.test_reference),
            args.reporting_commit,
        )


if __name__ == "__main__":
    main()
