"""Release one eligible proposition system to generation and frozen test scoring."""

import argparse
import fcntl
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import Field
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
from viper.stages import StageContext, build
from viper.storage import (
    LocalStorageDestination,
    ViperCloudDestination,
    load_storage_settings,
)

from csts_pilot.answer_input import emit
from csts_pilot.answers import answer_id
from csts_pilot.background_storage import queue_publication
from csts_pilot.baseline_models import validate_rows
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.proposition_capture import checked_records
from csts_pilot.proposition_inputs import (
    PropositionInferenceConfig,
    frozen_test_thresholds,
    infer,
    source_inventory,
    transform_rows,
)
from csts_pilot.proposition_run import relative_input
from jep_pilot.loaders import load_json

POLICY_FIELDS = (
    "generation_template_sha256",
    "schema_sha256",
    "model_alias",
    "reasoning_effort",
)


def single_name(value: str) -> str:
    """Reject path traversal for attempt and validation-directory identities."""
    if Path(value).name != value or value in {"", ".", ".."}:
        raise ValueError("Use a single attempt-directory name.")
    return value


def write_once(path: Path, value: Any) -> None:
    """Keep the exact first inventory and release decision on repeated reads."""
    if path.exists():
        if load_json(path) != value:
            raise ValueError(
                f"Preserve the existing frozen test artifact: {path.name}."
            )
    else:
        write_json(path, value)


def require_policy(manifest: dict[str, Any], selection: dict[str, Any]) -> None:
    """Reject generation changes after validation chose the model and cutoffs."""
    policy = selection.get("generation_policy", {})
    for name in POLICY_FIELDS:
        value = policy.get(name)
        if (
            not isinstance(value, str)
            or not value.strip()
            or manifest.get(name) != value
        ):
            raise ValueError(
                f"The test generation policy differs from frozen validation: {name}."
            )


def frozen_context(
    root: Path, parent_root: Path, validation_name: str
) -> dict[str, Any]:
    """Check the complete validation decision before any test input is opened."""
    directory = root / "answer_input_results" / single_name(validation_name)
    summary = load_json(directory / "summary.json")
    selection_path = directory / "selection.json"
    selection_sha256 = file_sha256(selection_path)
    selection = load_json(selection_path)
    if (
        summary.get("status") != "validation_complete"
        or summary.get("next_phase") != "eligible_test_pending"
        or summary.get("selection_sha256") != selection_sha256
        or summary.get("result", {}).get("selection") != selection
    ):
        raise ValueError(
            "Test requires the completed eligible validation selection and its sealed hash."
        )
    model = selection.get("selected_model") or {}
    frozen_test_thresholds(selection, model.get("sha256", ""))
    if model.get("stage_id") != "train" or model.get("artifact_name") != "model":
        raise ValueError(
            "The selected model must be a sealed native training model artifact."
        )
    settings = load_json(parent_root / "configs/csts-qwen-evidence.json")
    original = load_json(parent_root / "qwen_evidence_results/initial/summary.json")
    if selection["selected_arm"] == "epoch_zero":
        record = next(r for r in original["runs"] if r["name"] == "ratings_ratings")
    else:
        record = next(r for r in summary["runs"] if r["name"] == "fit")
    if (
        record["reference"] != model.get("run")
        or file_sha256(artifact_path(record, "train", "model", "model.pt"))
        != model["sha256"]
    ):
        raise ValueError(
            "The frozen selected model differs from its completed native source."
        )
    baseline = next(r for r in original["runs"] if r["name"] == "predict_ratings")
    return {
        "selection": selection,
        "selection_path": selection_path,
        "selection_sha256": selection_sha256,
        "settings": settings,
        "model_record": record,
        "baseline_record": baseline,
        "validation_directory": directory,
    }


def release_inventory(
    root: Path, parent_root: Path, validation_name: str
) -> dict[str, Any]:
    """Write only single-passage source fields after the eligible release check."""
    root, parent_root = root.resolve(strict=True), parent_root.resolve(strict=True)
    frozen = frozen_context(root, parent_root, validation_name)
    spec = frozen["settings"]["splits"]["test"]
    source_path = parent_root / spec["path"]
    if file_sha256(source_path) != spec["sha256"]:
        raise ValueError("The reserved test source bytes changed.")
    rows = load_json(source_path)
    validate_rows(rows)
    groups = {r["group_id"] for r in rows}
    if len(rows) != spec["rows"] or len(groups) != spec["groups"]:
        raise ValueError("The complete reserved test comparison cohort differs.")
    for split in ("training", "validation"):
        previous = frozen["settings"]["splits"][split]
        path = parent_root / previous["path"]
        if file_sha256(path) != previous["sha256"]:
            raise ValueError(
                f"Original {split} source bytes changed before test release."
            )
        if groups & {r["group_id"] for r in load_json(path)}:
            raise ValueError("The test source groups overlap training or validation.")
    items, aliases = source_inventory([], rows)
    group_ids = {}
    for row in rows:
        for side in ("sentence1", "sentence2"):
            identity = answer_id(row[side], row["condition"])
            if identity in group_ids and group_ids[identity] != row["group_id"]:
                raise ValueError(
                    "A canonical test generation identity spans source groups."
                )
            group_ids[identity] = row["group_id"]
    directory = frozen["validation_directory"] / "test_inventory"
    directory.mkdir(parents=True, exist_ok=True)
    write_once(directory / "generation_inputs.json", items)
    write_once(directory / "group_ids.json", group_ids)
    write_once(directory / "aliases_audit.json", aliases)
    pre_generation = {
        "status": "eligible_test_generation_released",
        "selection_sha256": frozen["selection_sha256"],
        "selected_arm": frozen["selection"]["selected_arm"],
        "selected_model_sha256": frozen["selection"]["selected_model"]["sha256"],
        "thresholds": frozen["selection"]["thresholds"],
        "generation_policy": frozen["selection"]["generation_policy"],
        "source_test_sha256": spec["sha256"],
        "source_comparisons": len(rows),
        "source_groups": len(groups),
        "unique_passage_conditions": len(items),
        "generation_inputs_sha256": file_sha256(directory / "generation_inputs.json"),
        "external_group_ids_sha256": file_sha256(directory / "group_ids.json"),
        "labels_or_companions_in_generation_inputs": False,
        "test_scores_used_for_selection": False,
    }
    write_once(directory / "pre_generation.json", pre_generation)
    emit("eligible_test_generation_released", **pre_generation)
    return {"directory": str(directory), **pre_generation}


class TestPreparationConfig(BuildConfig):
    """Bind test replacements to one released source and frozen generation policy."""

    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    original_rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    capture_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    release_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@build(config=TestPreparationConfig)
def prepare_test(context: StageContext[TestPreparationConfig]) -> None:
    """Check every test answer and keep all original comparisons and labels."""
    for name in (
        "selection",
        "original_rows",
        "answers",
        "capture_manifest",
        "release",
    ):
        if file_sha256(context.inputs[name]) != getattr(
            context.config, f"{name}_sha256"
        ):
            raise ValueError(f"Changed frozen test preparation input: {name}.")
    selection = load_json(context.inputs["selection"])
    frozen_test_thresholds(selection, selection["selected_model"]["sha256"])
    release = load_json(context.inputs["release"])
    if (
        release.get("status") != "eligible_test_generation_released"
        or release.get("selection_sha256") != context.config.selection_sha256
        or release.get("source_test_sha256") != context.config.original_rows_sha256
        or release.get("generation_policy") != selection["generation_policy"]
        or release.get("test_scores_used_for_selection") is not False
    ):
        raise ValueError(
            "The test generation release does not match frozen validation."
        )
    manifest = load_json(context.inputs["capture_manifest"])
    require_policy(manifest, selection)
    if (
        manifest.get("selection_sha256") != context.config.selection_sha256
        or manifest.get("records_sha256") != context.config.answers_sha256
        or set(manifest.get("partitions", {})) != {"test"}
    ):
        raise ValueError(
            "The captured test records are not bound to the released selection."
        )
    partition = manifest["partitions"]["test"]
    if (
        partition.get("status") != "complete"
        or partition.get("input_file_sha256") != release["generation_inputs_sha256"]
        or partition.get("group_file_sha256") != release["external_group_ids_sha256"]
        or partition.get("items") != release["unique_passage_conditions"]
    ):
        raise ValueError(
            "The test capture used a different source-only generation inventory."
        )
    rows = load_json(context.inputs["original_rows"])
    validate_rows(rows)
    if (
        len(rows) != release["source_comparisons"]
        or len({r["group_id"] for r in rows}) != release["source_groups"]
    ):
        raise ValueError("Test generation changed the released comparison cohort.")
    items, inventory = source_inventory([], rows)
    if len(items) != release["unique_passage_conditions"]:
        raise ValueError(
            "The canonical test generation inventory differs from its release."
        )
    records = checked_records(items, {"records": load_json(context.inputs["answers"])})
    transformed, coverage = transform_rows(rows, {r["id"]: r for r in records})
    validate_rows(transformed)
    write_json(context.outputs["transformed_rows"], transformed)
    write_json(
        context.outputs["audit"],
        {
            "selection_sha256": context.config.selection_sha256,
            "generation_policy": selection["generation_policy"],
            "capture_manifest": manifest,
            "release": release,
            "inventory": inventory,
            "coverage": coverage,
            "expert_verified": False,
            "test_cutoffs_refitted": False,
        },
    )
    emit("proposition_test_prepared", comparisons=len(rows), canonical_items=len(items))


def evaluate_test(
    root: Path,
    parent_root: Path,
    validation_name: str,
    name: str,
    answers: Path,
    manifest: Path,
) -> None:
    """Run one new-input test scorer at the sealed validation operating points."""
    root, parent_root = root.resolve(strict=True), parent_root.resolve(strict=True)
    frozen = frozen_context(root, parent_root, validation_name)
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError(
            "Seal native test artifacts locally before asynchronous promotion."
        )
    spec = frozen["settings"]["splits"]["test"]
    original_path = relative_input(root, Path(spec["path"]))
    if not (root / original_path).exists():
        shutil.copyfile(parent_root / spec["path"], root / original_path)
    if file_sha256(root / original_path) != spec["sha256"]:
        raise ValueError("The original test bytes changed.")
    release_path = frozen["validation_directory"] / "test_inventory/pre_generation.json"
    if not release_path.is_file():
        raise ValueError("Test generation was not released before capture.")
    paths = {
        "selection": frozen["selection_path"].relative_to(root).as_posix(),
        "original_rows": original_path,
        "answers": relative_input(root, answers),
        "capture_manifest": relative_input(root, manifest),
        "release": release_path.relative_to(root).as_posix(),
    }
    hashes = {key: file_sha256(root / value) for key, value in paths.items()}
    if hashes["selection"] != frozen["selection_sha256"]:
        raise ValueError("The eligible validation selection changed before evaluation.")
    directory = root / "answer_input_results" / single_name(name)
    directory.mkdir(parents=True, exist_ok=False)
    events = directory / "events.jsonl"
    events.touch()
    os.environ["CSTS_ANSWER_INPUT_EVENTS"] = str(events)
    source, environment = read_source(root), observe_python_env()
    destination = ViperCloudDestination.model_validate(
        frozen["settings"]["publication_destination"]
    )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "runs": [],
        "attempt": uuid.uuid4().hex[:8],
        "validation_name": validation_name,
        "selection_sha256": frozen["selection_sha256"],
        "selected_arm": frozen["selection"]["selected_arm"],
        "baseline_rerun": False,
        "test_cutoffs_refitted": False,
    }
    summary_path = directory / "summary.json"
    write_json(summary_path, summary)

    def execute(stage_name: str, configured: Any, gpu: bool) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_proposition_test_{source.commit[:8]}_{summary['attempt']}_{stage_name}",
            variants=(
                variant(
                    stage_name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        summary["in_flight"] = {
            "name": stage_name,
            "experiment_id": trial.experiment_id,
        }
        write_json(summary_path, summary)
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(model="NVIDIA L4", count=1)
            if gpu
            else CPUComputeSpec(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
            ),
            python_env=environment,
        )
        started = time.monotonic()
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=2400,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": stage_name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native proposition test stage failed: {stage_name}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        write_json(summary_path, summary)
        emit("stage_complete", stage=stage_name, seconds=record["seconds"])
        return record

    try:
        prepared = execute(
            "prepare_test",
            stage(
                prepare_test,
                stage_id="prepare",
                config=TestPreparationConfig(
                    **{f"{key}_sha256": value for key, value in hashes.items()}
                ),
                inputs=tuple(
                    input(
                        key,
                        path=path,
                        data_role="training" if key == "selection" else "eval",
                    )
                    for key, path in paths.items()
                ),
                outputs=StageOutputs(
                    transformed_rows=output(
                        path="test.json", loader=load_json, data_role="eval"
                    ),
                    audit=output(path="audit.json", loader=load_json, data_role="eval"),
                ),
                reuse="never",
            ),
            False,
        )
        transformed = artifact_path(
            prepared, "prepare", "transformed_rows", "test.json"
        )
        baseline = frozen["baseline_record"]
        baseline_path = artifact_path(
            baseline, "predict", "predictions", "predictions.json"
        )
        evaluated = execute(
            "frozen_test",
            stage(
                infer,
                stage_id="infer",
                config=PropositionInferenceConfig(
                    **frozen["settings"]["encoder"],
                    evaluation_split="test",
                    parent_model_sha256=frozen["selection"]["selected_model"]["sha256"],
                    original_rows_sha256=hashes["original_rows"],
                    transformed_rows_sha256=file_sha256(transformed),
                    baseline_sha256=file_sha256(baseline_path),
                    selection_sha256=frozen["selection_sha256"],
                    max_seconds=2100,
                ),
                inputs=(
                    input(
                        "model",
                        source=artifact_source(
                            frozen["model_record"], "train", "model"
                        ),
                    ),
                    input("selection", path=paths["selection"], data_role="training"),
                    input(
                        "original_rows", path=paths["original_rows"], data_role="eval"
                    ),
                    input(
                        "transformed_rows",
                        source=artifact_source(
                            prepared, "prepare", "transformed_rows", "eval"
                        ),
                    ),
                    input(
                        "baseline_predictions",
                        source=artifact_source(
                            baseline, "predict", "predictions", "eval"
                        ),
                    ),
                ),
                outputs=StageOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                    result=output(
                        path="result.json", loader=load_json, data_role="eval"
                    ),
                    timing=output(
                        path="timing.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            True,
        )
        for artifact_name, filename in (
            ("predictions", "predictions.json"),
            ("result", "result.json"),
            ("timing", "timing.json"),
        ):
            shutil.copyfile(
                artifact_path(evaluated, "infer", artifact_name, filename),
                directory / filename,
            )
        shutil.copyfile(
            artifact_path(prepared, "prepare", "audit", "audit.json"),
            directory / "preparation_audit.json",
        )
        summary.update(
            status="complete",
            result=load_json(directory / "result.json"),
            next_phase=None,
        )
        write_json(summary_path, summary)
        validation_summary_path = frozen["validation_directory"] / "summary.json"
        validation_summary = load_json(validation_summary_path)
        if validation_summary.get("selection_sha256") != frozen["selection_sha256"]:
            raise ValueError(
                "The parent validation selection changed during test scoring."
            )
        validation_summary.update(
            status="complete",
            next_phase=None,
            candidate_test_evaluation_ran=True,
            frozen_test={
                "name": name,
                "summary": str(summary_path),
                "result": summary["result"],
            },
        )
        write_json(validation_summary_path, validation_summary)
        emit("proposition_frozen_test_complete", **summary["result"])
    except Exception as exc:
        summary.update(status="failed", error=str(exc))
        write_json(summary_path, summary)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("inventory", "evaluate"), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--validation-name", required=True)
    parser.add_argument("--name")
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.phase == "inventory":
        release_inventory(args.root, args.parent_root, args.validation_name)
    else:
        if not args.name or args.answers is None or args.manifest is None:
            parser.error("Evaluation requires --name, --answers and --manifest.")
        with (args.parent_root / ".viper/overnight_gpu.lock").open("a") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            evaluate_test(
                args.root,
                args.parent_root,
                args.validation_name,
                args.name,
                args.answers,
                args.manifest,
            )
