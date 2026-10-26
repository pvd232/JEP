"""Consume separately released proposition test inputs through native frozen EVAL.

The full benchmark capture/import producer remains deferred. This consumer does
not authorize generation or supply that missing producer; it requires a prior
eligible validation decision and its separately released, checked test inputs.
"""

import argparse
from pathlib import Path
from typing import Any

from pydantic import Field, model_validator
from viper.authoring import input, stage
from viper.config import BuildConfig, EvalConfig
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, output
from viper.stages import StageContext, build, eval

from csts_pilot.answer_input import emit
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import validate_rows
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence import test_mse as artifact_test_mse
from csts_pilot.convergence import test_spearman as artifact_test_spearman
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.proposition_inputs import (
    PropositionInferenceConfig,
    frozen_test_thresholds,
    infer,
    source_inventory,
)
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
    """Fail closed until a reviewed full-test capture/import producer exists."""
    raise NotImplementedError(
        "Full proposition test preparation is deferred: the reviewed raw-provenance "
        "capture/import producer is not implemented."
    )


class TestEvaluationConfig(EvalConfig):
    """Reuse frozen inference settings under the canonical native EVAL contract."""

    inference: PropositionInferenceConfig

    @model_validator(mode="after")
    def require_test_selection(self) -> "TestEvaluationConfig":
        """Prevent validation cutoff fitting from being used by this test wrapper."""
        if self.inference.evaluation_split != "test":
            raise ValueError(
                "Native proposition test EVAL requires frozen test inference."
            )
        return self


@eval(config=TestEvaluationConfig)
def evaluate_frozen_test(context: StageContext[TestEvaluationConfig]) -> None:
    """Validate the frozen release before reading the complete native held-out split."""
    config = context.config.inference
    if file_sha256(context.inputs["selection"]) != config.selection_sha256:
        raise ValueError("The frozen validation selection bytes changed.")
    frozen_test_thresholds(
        load_json(context.inputs["selection"]), config.parent_model_sha256
    )
    if file_sha256(context.inputs["test"]) != config.original_rows_sha256:
        raise ValueError("Published native test bytes differ from the released cohort.")
    rows = load_json(context.inputs["test"])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError(
            "Native test indices differ from the complete released cohort."
        )
    # The shared zero-update scorer retains its selection-first checks and fixed
    # cutoffs. Only its input alias changes; this calls no separate BUILD stage.
    infer(
        StageContext(
            run_id=context.run_id,
            attempt_id=context.attempt_id,
            stage_id=context.stage_id,
            config=config,
            inputs={**context.inputs, "original_rows": context.inputs["test"]},
            outputs=context.outputs,
            metrics=context.metrics,
            numpy_generators=context.numpy_generators,
        )
    )


def frozen_test_stage(
    config: TestEvaluationConfig,
    model: dict[str, Any],
    published: dict[str, Any],
    prepared: dict[str, Any],
    baseline: dict[str, Any],
    selection_path: str,
) -> Any:
    """Bind frozen native producers and artifact-recomputed test metrics once."""
    dependency = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    metrics = tuple(
        measure(
            metric,
            dependencies=dependency,
            comparator=FloatComparator(mode="absolute", tolerance=1e-12),
        )
        for metric in (artifact_test_mse, artifact_test_spearman)
    )
    return stage(
        evaluate_frozen_test,
        stage_id="infer",
        eval_id="csts_proposition_frozen_test",
        config=config,
        inputs=(
            input("model", source=artifact_source(model, "train", "model")),
            input("test", source=artifact_source(published, "publish", "test", "eval")),
            input(
                "holdout",
                source=artifact_source(published, "publish", "holdout", "eval"),
            ),
            input("selection", path=selection_path, data_role="training"),
            input(
                "transformed_rows",
                source=artifact_source(prepared, "prepare", "transformed_rows", "eval"),
            ),
            input(
                "baseline_predictions",
                source=artifact_source(baseline, "predict", "predictions", "eval"),
            ),
        ),
        split_inputs=("holdout",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            result=output(path="result.json", loader=load_json, data_role="eval"),
            timing=output(path="timing.json", loader=load_json, data_role="eval"),
        ),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )


def evaluate_test(
    root: Path,
    parent_root: Path,
    validation_name: str,
    name: str,
    answers: Path,
    manifest: Path,
) -> None:
    """Fail before opening test inputs while the full-test producer is deferred."""
    raise NotImplementedError(
        "Full proposition test evaluation is deferred: the reviewed raw-provenance "
        "capture/import producer is not implemented. The canonical EVAL consumer "
        "is reserved for a future separately reviewed release protocol."
    )


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
        evaluate_test(
            args.root,
            args.parent_root,
            args.validation_name,
            args.name,
            args.answers,
            args.manifest,
        )
