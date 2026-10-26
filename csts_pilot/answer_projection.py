"""Extract frozen answer inputs for one supervised conditional projection."""

import time
from typing import Any, Literal

import torch
from pydantic import Field
from viper.stages import StageContext, build

from csts_pilot.answer_input import emit
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    encode,
    encoder_settings,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    passage_keys,
    restore_parameters,
    state_digest,
    token_sequences,
    trainable_state,
    validate_cache,
    validate_rows,
)
from csts_pilot.convergence import file_sha256, synchronize, write_json
from csts_pilot.data import canonical
from csts_pilot.evidence_controls import checked_cache
from jep_pilot.loaders import load_json, load_model


class AnswerProjectionConfig(EncoderConfig):
    """Pin source comparisons, existing teacher answers and selected adapters."""

    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    encode_batch_size: Literal[4] = 4
    max_seconds: float = Field(default=1200, gt=0, allow_inf_nan=False)


def validate_original_split(
    training: list[dict[str, Any]], validation: list[dict[str, Any]]
) -> None:
    """Reject original source overlap before any answer transformation."""
    validate_rows(training)
    validate_rows(validation)
    for name in ("row_id", "group_id"):
        if {row[name] for row in training} & {row[name] for row in validation}:
            raise ValueError(f"Original training and validation overlap in {name}.")
    captions = [
        {canonical(row[side]) for row in rows for side in ("sentence1", "sentence2")}
        for rows in (training, validation)
    ]
    if captions[0] & captions[1]:
        raise ValueError("Original source captions cross training and validation.")


def transform_rows(
    rows: list[dict[str, Any]], records: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replace accepted answers without changing labels, source groups or fields."""
    transformed = []
    counts = {"both": 0, "one": 0, "neither": 0}
    accepted_count_per_row = []
    accepted_sides = 0
    for row in rows:
        changed = dict(row)
        accepted = 0
        for side in ("sentence1", "sentence2"):
            record = records.get(answer_id(row[side], row["condition"]))
            if record is not None and record["valid"]:
                changed[side] = record["answer"]
                accepted += 1
        accepted_sides += accepted
        accepted_count_per_row.append(accepted)
        counts[("neither", "one", "both")[accepted]] += 1
        transformed.append(changed)
    validate_rows(transformed)
    return transformed, {
        "comparisons": len(rows),
        "accepted_side_occurrences": accepted_sides,
        "fallback_side_occurrences": 2 * len(rows) - accepted_sides,
        "comparison_coverage": counts,
        "accepted_count_per_row": accepted_count_per_row,
    }


@build(config=AnswerProjectionConfig)
def extract(context: StageContext[AnswerProjectionConfig]) -> None:
    """Write standard frozen-feature artifacts for the existing projection fitter."""
    config = context.config
    started = time.monotonic()
    original_inputs = {}
    for name in ("training", "validation", "answers", "model"):
        digest = file_sha256(context.inputs[name])
        if digest != getattr(config, f"{name}_sha256"):
            raise ValueError(f"Changed answer-projection input: {name}.")
        original_inputs[name] = digest
    training = load_json(context.inputs["training"])
    validation = load_json(context.inputs["validation"])
    validate_original_split(training, validation)
    records = checked_cache(context.inputs["answers"])
    rows, coverage = {}, {}
    for name, original in (("training", training), ("validation", validation)):
        rows[name], coverage[name] = transform_rows(original, records)
        context.outputs[name].parent.mkdir(parents=True, exist_ok=True)
        write_json(context.outputs[name], rows[name])
    inputs = {
        name: file_sha256(context.outputs[name]) for name in ("training", "validation")
    }
    keys = passage_keys(rows["training"] + rows["validation"])
    tokenizer = load_tokenizer(config)
    sequences = token_sequences(tokenizer, keys, config)
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    if fit.kind != "lora":
        raise ValueError("Answer projection requires the selected frozen LoRA model.")
    for name in ("model_id", "revision", "embedding_dimension", "max_length"):
        if getattr(fit, name) != getattr(config, name):
            raise ValueError(f"Selected encoder setting differs: {name}.")
    fit = fit.model_copy(update={"device": config.device})
    coverage_counts = {
        name: {
            key: value
            for key, value in values.items()
            if key != "accepted_count_per_row"
        }
        for name, values in coverage.items()
    }
    emit("answer_projection_loading", unique_inputs=len(keys), coverage=coverage_counts)
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    del saved
    model.eval()
    model.requires_grad_(False)
    adapters = {name: p for name, p in model.named_parameters() if "lora_" in name}
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    vectors, tokens = [], 0
    inference_started = last_emit = time.monotonic()
    with torch.inference_mode():
        for start in range(0, len(keys), config.encode_batch_size):
            if time.monotonic() - started > config.max_seconds:
                raise TimeoutError("Answer-projection extraction allowance exhausted.")
            batch = pad_sequences(
                tokenizer, sequences[start : start + config.encode_batch_size], config
            )
            tokens += int(batch["attention_mask"].sum())
            vectors.append(encode(model, batch).cpu())
            now = time.monotonic()
            if now - last_emit >= 15 or start + config.encode_batch_size >= len(keys):
                emit(
                    "answer_projection_progress",
                    done=min(start + config.encode_batch_size, len(keys)),
                    total=len(keys),
                    elapsed_seconds=round(now - started, 2),
                )
                last_emit = now
    synchronize(config.device)
    after = state_digest(adapters)
    if before != after:
        raise ValueError("Frozen adapters changed during answer-projection extraction.")
    audit = {
        "original_inputs": original_inputs,
        "transformed_inputs": inputs,
        "frozen_model_sha256": config.model_sha256,
        "adapter_state_before_sha256": before,
        "adapter_state_after_sha256": after,
        "coverage": coverage,
        "unique_inputs": len(keys),
        "optimizer_updates": 0,
        "condition": "Original condition retained for every side.",
        "fallback": "Original passage for each unavailable or rejected answer.",
        "expert_verified": False,
        "original_split_disjoint": True,
    }
    cache = {
        "encoder": encoder_settings(config),
        "keys": keys,
        "vectors": torch.cat(vectors),
        "inputs": inputs,
        "audit": audit,
    }
    validate_cache(cache, config)
    for name in ("embeddings", "audit", "timing"):
        context.outputs[name].parent.mkdir(parents=True, exist_ok=True)
    torch.save(cache, context.outputs["embeddings"])
    audit["embeddings_sha256"] = file_sha256(context.outputs["embeddings"])
    write_json(context.outputs["audit"], audit)
    write_json(
        context.outputs["timing"],
        {
            "total_seconds": time.monotonic() - started,
            "inference_seconds": time.monotonic() - inference_started,
            "nonpadding_tokens": tokens,
            "unique_inputs": len(keys),
            "optimizer_updates": 0,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
        },
    )
    emit(
        "answer_projection_extraction_complete",
        unique_inputs=len(keys),
        coverage=coverage_counts,
        optimizer_updates=0,
        elapsed_seconds=round(time.monotonic() - started, 2),
    )
