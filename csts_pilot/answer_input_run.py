"""Run the bounded cached-answer screen with native artifacts and live events."""

import argparse
import fcntl
import os
import shutil
import time
import uuid
from pathlib import Path

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.storage import ViperCloudDestination

from csts_pilot.answer_input import AnswerInputConfig, emit, infer
from csts_pilot.background_storage import queue_publication
from csts_pilot.condition_reference import MODEL_SHA256
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path, artifact_source
from jep_pilot.loaders import load_json, load_model


def run(root: Path, parent_root: Path, name: str) -> None:
    """Reuse saved comparator scores and perform one frozen validation screen."""
    root = root.resolve(strict=True)
    parent_root = parent_root.resolve(strict=True)
    settings = load_json(parent_root / "configs/csts-qwen-evidence.json")
    original = load_json(parent_root / "qwen_evidence_results/initial/summary.json")
    parent = next(r for r in original["runs"] if r["name"] == "ratings_ratings")
    model_path = artifact_path(parent, "train", "model", "model.pt")
    baseline_path = artifact_path(
        parent, "train", "validation_predictions", "validation_predictions.json"
    )
    if not baseline_path.exists():
        candidates = list(baseline_path.parent.glob("*.json"))
        if len(candidates) != 1:
            raise ValueError("Cannot identify saved validation predictions.")
        baseline_path = candidates[0]
    if file_sha256(model_path) != MODEL_SHA256:
        raise ValueError("Selected saved model changed.")
    spec = settings["splits"]["validation"]
    inputs = root / "csts_data"
    inputs.mkdir(exist_ok=True)
    for relative in (spec["path"], settings["answers"]["path"]):
        destination = root / relative
        if not destination.exists():
            shutil.copyfile(parent_root / relative, destination)
    directory = root / "answer_input_results" / name
    directory.mkdir(parents=True, exist_ok=False)
    events = directory / "events.jsonl"
    events.touch()
    os.environ["CSTS_ANSWER_INPUT_EVENTS"] = str(events)
    config = AnswerInputConfig(
        **settings["encoder"],
        rows_sha256=spec["sha256"],
        answers_sha256=settings["answers"]["sha256"],
        model_sha256=MODEL_SHA256,
        baseline_sha256=file_sha256(baseline_path),
    )
    source = read_source(root)
    configured = stage(
        infer,
        stage_id="answer_input",
        config=config,
        inputs=(
            input("rows", path=spec["path"], data_role="eval"),
            input("answers", path=settings["answers"]["path"], data_role="eval"),
            input("model", source=artifact_source(parent, "train", "model")),
            input(
                "baseline_predictions",
                source=artifact_source(parent, "train", "validation_predictions"),
            ),
        ),
        outputs=StageOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            result=output(path="result.json", loader=load_json, data_role="eval"),
            vectors=output(path="vectors.pt", loader=load_model, data_role="eval"),
            timing=output(path="timing.json", loader=load_json, data_role="eval"),
        ),
        reuse="never",
    )
    trial = experiment(
        experiment_id=f"csts_answer_input_{source.commit[:8]}_{uuid.uuid4().hex[:8]}",
        variants=(
            variant(
                "validation",
                stages=(configured,),
                estimator=configured.outputs["result"],
            ),
        ),
        replicates=(replicate(seed=7),),
    )
    env = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="tranche2_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    summary = {
        "status": "running",
        "source_commit": source.commit,
        "config": config.model_dump(),
        "started_unix": time.time(),
    }
    write_json(directory / "summary.json", summary)
    emit("study_started", **summary)
    try:
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=1800,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
        }
        summary["run"] = record
        if result.status != "succeeded":
            raise RuntimeError(f"Native answer-input stage failed: {result.path}")
        for artifact_name, filename in (
            ("result", "result.json"),
            ("predictions", "predictions.json"),
            ("timing", "timing.json"),
        ):
            shutil.copyfile(
                artifact_path(record, "answer_input", artifact_name, filename),
                directory / filename,
            )
        summary["result"] = load_json(directory / "result.json")
        summary["status"] = "complete"
        summary["publication_queue"] = str(
            queue_publication(
                root,
                result.reference,
                ViperCloudDestination.model_validate(
                    settings["publication_destination"]
                ),
            )
        )
        write_json(directory / "summary.json", summary)
        emit("study_complete", result=summary["result"])
    except Exception as exc:
        summary.update(status="failed", error=str(exc))
        write_json(directory / "summary.json", summary)
        emit("study_failed", error=str(exc))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    lock = args.parent_root / ".viper/overnight_gpu.lock"
    with lock.open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.root, args.parent_root, args.name)
