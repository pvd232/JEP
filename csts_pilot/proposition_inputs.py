"""Prepare source-bound proposition inputs and measure their frozen readout."""

import math
import time
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field, model_validator
from viper.config import BuildConfig
from viper.stages import StageContext, build

from csts_pilot.answer_input import baseline_scores, emit
from csts_pilot.answer_projection import validate_original_split
from csts_pilot.answer_projection_run import original_predictions
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    TokenPairs,
    load_backbone,
    load_tokenizer,
    restore_parameters,
    state_digest,
    trainable_state,
    validate_rows,
)
from csts_pilot.condition_reference import arm_metrics, recall_cutoff
from csts_pilot.convergence import file_sha256, synchronize, write_json
from csts_pilot.data import canonical
from csts_pilot.proposition_capture import checked_records
from jep_pilot.loaders import load_json, load_model


class PropositionPreparationConfig(BuildConfig):
    """Pin complete source partitions, captured records and the fidelity gate."""

    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    capture_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    audit_gate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PropositionInferenceConfig(EncoderConfig):
    """Bind zero-update scoring to original rows and their exact replacements."""

    parent_model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    original_rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    transformed_rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    baseline_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evaluation_split: Literal["validation", "test"] = "validation"
    selection_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    encode_batch_size: Literal[4] = 4
    max_seconds: float = Field(default=1200, gt=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def bind_test_selection(self) -> "PropositionInferenceConfig":
        """Require an explicit frozen selection for test-only inference."""
        if (self.evaluation_split == "test") != (self.selection_sha256 is not None):
            raise ValueError(
                "Test inference requires a frozen selection SHA; validation does not."
            )
        return self


def frozen_test_thresholds(
    selection: dict[str, Any], model_sha256: str
) -> dict[str, float]:
    """Validate the eligible frozen decision without consulting any test rows."""
    arm = selection.get("selected_arm")
    if (
        arm not in {"epoch_zero", "adapted"}
        or selection.get("test_scores_used_for_selection") is not False
        or selection.get("eligibility", {}).get(arm, {}).get("eligible") is not True
        or selection.get("selected_model", {}).get("sha256") != model_sha256
    ):
        raise ValueError("Test inference requires an eligible validation-frozen model.")
    thresholds = selection.get("thresholds", {})
    result = {}
    for name in ("saved_qwen", arm):
        value = thresholds.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError("A frozen validation cutoff is missing or nonfinite.")
        result[name] = float(value)
    return {"saved_qwen": result["saved_qwen"], "propositions": result[arm]}


def source_inventory(
    training: list[dict[str, Any]], validation: list[dict[str, Any]]
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Keep the first raw representative of each existing canonical identity."""
    items: dict[str, dict[str, str]] = {}
    groups: dict[str, str] = {}
    variants: dict[str, set[tuple[str, str]]] = {}
    for rows in (training, validation):
        for row in rows:
            for side in ("sentence1", "sentence2"):
                passage, condition = row[side], row["condition"]
                identity = answer_id(passage, condition)
                item = {"id": identity, "passage": passage, "condition": condition}
                if identity in items:
                    old = items[identity]
                    if (
                        canonical(old["passage"]) != canonical(passage)
                        or canonical(old["condition"]) != canonical(condition)
                        or groups[identity] != row["group_id"]
                    ):
                        raise ValueError(
                            "Canonical proposition identity changes source semantics or group."
                        )
                else:
                    items[identity] = item
                    groups[identity] = row["group_id"]
                    variants[identity] = set()
                variants[identity].add((passage, condition))
    aliases = [
        {
            "id": identity,
            "group_id": groups[identity],
            "representative": items[identity],
            "variants": [
                {"passage": passage, "condition": condition}
                for passage, condition in sorted(variants[identity])
            ],
        }
        for identity in sorted(items)
        if len(variants[identity]) > 1
    ]
    return [items[key] for key in sorted(items)], {
        "canonical_items": len(items),
        "raw_identity_variants": sum(len(value) for value in variants.values()),
        "aliased_identities": len(aliases),
        "raw_variant_groups": aliases,
        "representative_policy": "First occurrence in training, then validation, original row/side order.",
    }


def transform_rows(
    rows: list[dict[str, Any]], records: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replace answered passages only, preserving full comparison identities."""
    transformed, accepted_counts = [], []
    for row in rows:
        changed = dict(row)
        count = 0
        for side in ("sentence1", "sentence2"):
            record = records[answer_id(row[side], row["condition"])]
            if record["status"] == "answered":
                changed[side] = record["answer"]
                count += 1
        transformed.append(changed)
        accepted_counts.append(count)
    return transformed, {
        "comparisons": len(rows),
        "accepted_side_occurrences": sum(accepted_counts),
        "fallback_side_occurrences": 2 * len(rows) - sum(accepted_counts),
        "comparison_coverage": {
            name: accepted_counts.count(count)
            for count, name in ((2, "both"), (1, "one"), (0, "neither"))
        },
        "accepted_count_per_row": accepted_counts,
    }


@build(config=PropositionPreparationConfig)
def prepare(context: StageContext[PropositionPreparationConfig]) -> None:
    """Validate a complete captured bank before publishing transformed inputs."""
    config = context.config
    hashes = {}
    for name in ("training", "validation", "answers", "capture_manifest", "audit_gate"):
        hashes[name] = file_sha256(context.inputs[name])
        if hashes[name] != getattr(config, f"{name}_sha256"):
            raise ValueError(f"Changed proposition preparation input: {name}.")
    manifest = load_json(context.inputs["capture_manifest"])
    gate = load_json(context.inputs["audit_gate"])
    if gate.get("passed") is not True:
        raise ValueError("The proposition fidelity gate did not pass.")
    for name in ("generation_template_sha256", "schema_sha256"):
        value = manifest.get(name)
        if not isinstance(value, str) or len(value) != 64 or gate.get(name) != value:
            raise ValueError(f"Generation and fidelity-gate settings differ: {name}.")
    for name in ("model_alias", "reasoning_effort"):
        value = manifest.get(name)
        if not isinstance(value, str) or not value.strip() or gate.get(name) != value:
            raise ValueError(f"Generation and fidelity-gate settings differ: {name}.")
    if manifest.get("records_sha256") != hashes["answers"]:
        raise ValueError("The generation manifest refers to different records.")
    if set(manifest.get("partitions", {})) != {"training", "validation"}:
        raise ValueError(
            "Full proposition preparation requires both source partitions."
        )
    training = load_json(context.inputs["training"])
    validation = load_json(context.inputs["validation"])
    validate_original_split(training, validation)
    items, inventory = source_inventory(training, validation)
    records = checked_records(items, {"records": load_json(context.inputs["answers"])})
    lookup = {record["id"]: record for record in records}
    coverage = {}
    transformed_hashes = {}
    for name, original in (("training", training), ("validation", validation)):
        transformed, coverage[name] = transform_rows(original, lookup)
        validate_rows(transformed)
        write_json(context.outputs[name], transformed)
        transformed_hashes[name] = file_sha256(context.outputs[name])
    write_json(
        context.outputs["audit"],
        {
            "source_inputs": hashes,
            "transformed_inputs": transformed_hashes,
            "capture_manifest": manifest,
            "fidelity_gate": gate,
            "inventory": inventory,
            "coverage": coverage,
            "expert_verified": False,
            "supervision": "Model-generated propositions with source quotations and model-assisted fidelity screening.",
            "fallback": "Original passage and original condition for not_specified or ambiguous records.",
        },
    )
    emit(
        "proposition_inputs_prepared",
        coverage={
            name: {
                key: value
                for key, value in values.items()
                if key != "accepted_count_per_row"
            }
            for name, values in coverage.items()
        },
        canonical_items=len(items),
    )


def validate_replacements(
    original: list[dict[str, Any]], transformed: list[dict[str, Any]]
) -> None:
    """Reject changed identities, labels, order or fields before model loading."""
    validate_rows(original)
    validate_rows(transformed)
    if len(original) != len(transformed):
        raise ValueError("Proposition replacements changed the comparison count.")
    for before, after in zip(original, transformed, strict=True):
        if set(before) != set(after) or {
            key: value
            for key, value in before.items()
            if key not in {"sentence1", "sentence2"}
        } != {
            key: value
            for key, value in after.items()
            if key not in {"sentence1", "sentence2"}
        }:
            raise ValueError(
                "Proposition replacements changed comparison metadata or order."
            )


@build(config=PropositionInferenceConfig)
def infer(context: StageContext[PropositionInferenceConfig]) -> None:
    """Score checked answer inputs with the saved encoder and no optimizer updates."""
    started = time.monotonic()
    config = context.config
    frozen = None
    if config.evaluation_split == "test":
        if file_sha256(context.inputs["selection"]) != config.selection_sha256:
            raise ValueError("The frozen validation selection bytes changed.")
        # Check the selected model and cutoffs before opening test input rows.
        frozen = frozen_test_thresholds(
            load_json(context.inputs["selection"]), config.parent_model_sha256
        )
    for name, digest in (
        ("model", config.parent_model_sha256),
        ("original_rows", config.original_rows_sha256),
        ("transformed_rows", config.transformed_rows_sha256),
        ("baseline_predictions", config.baseline_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed proposition inference input: {name}.")
    original = load_json(context.inputs["original_rows"])
    transformed = load_json(context.inputs["transformed_rows"])
    validate_replacements(original, transformed)
    identities = {row["row_id"] for row in original}
    saved_baseline = [
        row
        for row in load_json(context.inputs["baseline_predictions"])
        if row["row_id"] in identities
    ]
    baseline = baseline_scores(original, saved_baseline)
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    if saved.get("kind") != "lora" or fit.kind != "lora":
        raise ValueError("Frozen proposition inference requires the saved LoRA model.")
    for name in ("model_id", "revision", "max_length", "embedding_dimension"):
        if getattr(fit, name) != getattr(config, name):
            raise ValueError(f"Frozen proposition encoder setting differs: {name}.")
    fit = fit.model_copy(update={"device": config.device})
    tokenizer = load_tokenizer(fit)
    pairs = TokenPairs(transformed, fit, tokenizer)
    emit("proposition_inference_loading", comparisons=len(original))
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    parameters = {
        name: value for name, value in model.named_parameters() if value.requires_grad
    }
    del saved
    model.eval()
    model.requires_grad_(False)
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    values = []
    last_emit = time.monotonic()
    with torch.inference_mode():
        for start in range(0, len(transformed), 2):
            if time.monotonic() - started > config.max_seconds:
                raise TimeoutError("Frozen proposition inference allowance exhausted.")
            indices = torch.arange(start, min(start + 2, len(transformed)))
            values.extend(pairs.scores(model, indices).float().cpu().tolist())
            now = time.monotonic()
            if now - last_emit >= 15 or start + 2 >= len(transformed):
                emit(
                    "proposition_inference_progress",
                    done=len(values),
                    total=len(transformed),
                    elapsed_seconds=round(now - started, 2),
                )
                last_emit = now
    synchronize(config.device)
    after = state_digest(parameters)
    if before != after:
        raise ValueError("Adapter bytes changed during frozen proposition inference.")
    predictions = original_predictions(
        original,
        transformed,
        [
            dict(row, prediction=float(score))
            for row, score in zip(transformed, values, strict=True)
        ],
    )
    scores = np.asarray(values, dtype=float)
    baseline_cutoff = (
        recall_cutoff(original, baseline) if frozen is None else frozen["saved_qwen"]
    )
    native = arm_metrics(original, baseline, baseline_cutoff)
    cutoff = (
        recall_cutoff(
            original, scores, recall=native["operating_point"]["recall"] - 1e-12
        )
        if frozen is None
        else frozen["propositions"]
    )
    candidate = arm_metrics(original, scores, cutoff)
    write_json(context.outputs["predictions"], predictions)
    write_json(
        context.outputs["result"],
        {
            "metrics": {"saved_qwen": native, "propositions": candidate},
            "optimizer_updates": 0,
            "baseline_rerun": False,
            "selection_use": (
                "Diagnostic only; semantic fidelity, not frozen cosine improvement, governs adaptation."
                if frozen is None
                else "Selected model and both cutoffs frozen on validation before test access."
            ),
            "test_cutoffs_refitted": False,
            "expert_verified": False,
            "config": config.model_dump(),
        },
    )
    write_json(
        context.outputs["timing"],
        {
            "total_seconds": time.monotonic() - started,
            "nonpadding_tokens": pairs.nonpadding_tokens,
            "adapter_state_before_sha256": before,
            "adapter_state_after_sha256": after,
            "optimizer_updates": 0,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
        },
    )
    emit("proposition_inference_result", **candidate)
