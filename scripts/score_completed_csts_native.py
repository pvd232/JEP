"""Publish test scores for a completed joint fit while other fits continue."""

import argparse
import fcntl
import shutil
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloudDestination, publish_resolved_files

from csts_pilot.background_storage import _save, drain_publications, queue_publication
from csts_pilot.convergence import file_sha256
from csts_pilot.convergence_run import artifact_path
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout_run import checked_source
from csts_pilot.native_comparison import NativeScoreConfig, capture_native_comparison
from jep_pilot.loaders import load_json


def frozen_selection(fitted, trace, settings_sha256, protocol):
    """Require completed selection and preserve the committed remaining fit rules."""
    if (
        fitted.get("status") != "succeeded"
        or fitted.get("terminal", {}).get("status") != "succeeded"
    ):
        raise ValueError("Test scoring requires a completed, sealed native fit.")
    if trace.get("budget_censored", True) or trace["selected"] != fitted["selected"]:
        raise ValueError("The completed fit and selected checkpoint must agree.")
    if protocol["settings_sha256"] != settings_sha256 or protocol["executed_seeds"] != [
        7,
        8,
        9,
    ]:
        raise ValueError("Preserve the committed configuration and executed seed list.")
    if fitted["seed"] not in protocol["executed_seeds"]:
        raise ValueError("The completed fit must use an executed seed.")
    seed = str(fitted["seed"])
    return {
        "executed_seeds": protocol["executed_seeds"],
        "completed_seeds": [int(seed)],
        "selected_model_sha256": {seed: fitted["selected"]["sha256"]},
        "selection": fitted["selected"],
        "settings_sha256": settings_sha256,
        "fitting_source_commit": fitted["source_commit"],
        "reporting_protocol": protocol,
    }


def score(root, fit_path, references_path, protocol_path):
    settings = load_json(root / "configs/csts-native-comparison.json")
    fitted, references, protocol = map(
        load_json, (fit_path, references_path, protocol_path)
    )
    checked_source(root, fitted["source_commit"])
    trace = load_json(Path(fitted["trace"]))
    selection = frozen_selection(
        fitted,
        trace,
        file_sha256(root / "configs/csts-native-comparison.json"),
        protocol,
    )
    seed = fitted["seed"]
    directory = root / "qwen_evidence_results" / f"native_seed{seed}_test_20261028"
    directory.mkdir(parents=True, exist_ok=False)
    selected_path = directory / "selection.json"
    _save(selected_path, selection)
    shutil.copyfile(__file__, directory / "score.py")
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    prefix = f"csts_native_comparison_20261028/seed{seed}/completed_test"
    publications = ThreadPoolExecutor(max_workers=1)
    selected_future = publications.submit(
        publish_resolved_files,
        root,
        destination,
        {
            prefix + "/" + name: directory / name
            for name in ("selection.json", "score.py")
        },
    )
    # Native local inputs seal selection before inference. Cloud work overlaps it.
    source, environment = read_source(root), observe_python_env()
    hardware = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
    ).strip()
    model_record = fitted["terminal"]
    summary = {
        "status": "scoring",
        "seed": seed,
        "selected_model_sha256": fitted["selected"]["sha256"],
        "selected_epoch": fitted["selected"]["epoch"],
        "terminal_epoch": trace["completed_epoch"],
        "selection": selection,
        "test_sha256": settings["splits"]["test"]["sha256"],
        "runs": {},
    }
    for split in ("test", "edits"):
        rows_binding = (
            input(
                "rows",
                source=stored_source(
                    {"reference": references["published_test"]},
                    "publish",
                    "test",
                    "rows",
                    "eval",
                ),
            )
            if split == "test"
            else input("rows", path=settings["interventions"]["path"], data_role="eval")
        )
        rows_sha = (
            settings["splits"]["test"]["sha256"]
            if split == "test"
            else settings["interventions"]["sha256"]
        )
        configured = stage(
            capture_native_comparison,
            stage_id="predict",
            config=NativeScoreConfig(
                **settings["encoder"],
                model_sha256=fitted["selected"]["sha256"],
                rows_sha256=rows_sha,
                selection_sha256=file_sha256(selected_path),
            ),
            inputs=(
                input(
                    "model",
                    source=stored_source(model_record, "train", "model", "model"),
                ),
                input(
                    "selection",
                    path=selected_path.relative_to(root).as_posix(),
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
        )
        identity = f"native_completed_test_s{seed}_{split}_{uuid.uuid4().hex[:10]}"
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
        summary["in_flight"] = identity
        _save(directory / "summary.json", summary)
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
            summary["status"] = "failed"
            _save(directory / "summary.json", summary)
            raise RuntimeError("Native test prediction failed.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        predictions = artifact_path(
            record, "predict", "predictions", "predictions.json"
        )
        diagnostics = artifact_path(
            record, "predict", "diagnostics", "diagnostics.json"
        )
        shutil.copyfile(predictions, directory / (split + "_predictions.json"))
        shutil.copyfile(diagnostics, directory / (split + "_diagnostics.json"))
        if split == "test":
            summary["test"] = summarize(load_json(predictions))
            if summary["test"]["n"] != settings["splits"]["test"]["rows"]:
                raise ValueError(
                    "Test prediction coverage differs from the declared cohort."
                )
            print(
                "COMPLETED_TEST_SCORE",
                seed,
                summary["test"]["spearman"],
                summary["test"]["mse_0_1"],
                flush=True,
            )
        summary["in_flight"] = None
        _save(directory / "summary.json", summary)
    # GPU computation is complete. Publication completion now gates shutdown.
    selected_refs = selected_future.result()
    publications.shutdown(wait=True)
    _save(
        directory / "selection-publication.json",
        {
            "status": "published",
            "references": {
                k: v.model_dump(mode="json") for k, v in selected_refs.items()
            },
        },
    )
    drain_publications(root, retry_failed=True)
    for record in summary["runs"].values():
        receipt = load_json(Path(record["publication_queue"]))
        if receipt["status"] != "published":
            raise RuntimeError(
                "Retain the runtime until its test predictions are published."
            )
        record["cloud_reference"] = receipt["reference"]
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "fit", "references", "protocol"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--allow-completed-uploader", action="store_true")
    args = parser.parse_args()
    with Path("/tmp/jep-gpu.lock").open("r+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if not args.allow_completed_uploader:
                raise
            fitted = load_json(args.fit)
            frozen_selection(
                fitted,
                load_json(Path(fitted["trace"])),
                file_sha256(args.root / "configs/csts-native-comparison.json"),
                load_json(args.protocol),
            )
        active = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
            text=True,
        ).strip()
        if active:
            fitted = load_json(args.fit)
            for pid in active.splitlines():
                command = (
                    (Path("/proc") / pid.strip() / "cmdline")
                    .read_bytes()
                    .decode()
                    .split("\0")
                )
                if (
                    not args.allow_completed_uploader
                    or "csts_pilot.native_comparison_run" not in command
                    or "--root" not in command
                    or command[command.index("--root") + 1] != str(args.root)
                    or "--seed" not in command
                    or command[command.index("--seed") + 1] != str(fitted["seed"])
                ):
                    raise RuntimeError("The GPU has an unrelated active computation.")
        score(args.root, args.fit, args.references, args.protocol)


if __name__ == "__main__":
    main()
