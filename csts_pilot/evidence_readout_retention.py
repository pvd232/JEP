"""Measure writing retention before fitting the revised frozen readout experiment."""

from typing import Any

import numpy as np
import torch
from pydantic import Field
from viper.stages import StageContext, build

from csts_pilot import evidence_readout_progress as progress
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EOD,
    EncoderConfig,
    FitConfig,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    trainable_state,
)
from csts_pilot.condition_reference import native_layout
from csts_pilot.convergence import write_json
from csts_pilot.evidence_readout_stages import checked, emit
from csts_pilot.qwen_evidence import (
    QwenEvidenceConfig,
    answer_loss_sum,
    evidence_tokens,
    load_head,
)
from jep_pilot.loaders import load_json, load_model


class ReadoutRetentionConfig(EncoderConfig):
    """Keep the existing writing targets and vocabulary projection fixed."""

    writing_model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    progress_path: str | None = None
    final_model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    targets_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    head_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_targets: int = Field(default=121, ge=1)
    max_answer_tokens: int = Field(default=64, ge=2)
    generated_samples: int = Field(default=32, ge=1)


def retention_summary(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> dict[str, Any]:
    """Keep reference likelihood, exact agreement, and semantic fidelity distinct."""
    if not before or [r["id"] for r in before] != [r["id"] for r in after]:
        raise ValueError(
            "Retention comparisons need identical ordered target identities."
        )
    result = {}
    for label, records in (("writing", before), ("after_ratings", after)):
        ce = np.asarray([r["answer_mean_ce"] for r in records], dtype=float)
        if not np.isfinite(ce).all():
            raise ValueError("Retention CE must be finite.")
        generated = [r for r in records if r["generated"] is not None]
        result[label] = {
            "targets": len(records),
            "mean_answer_ce": float(ce.mean()),
            "generated_samples": len(generated),
            "whitespace_normalized_exact_match": float(
                np.mean(
                    [
                        " ".join(r["generated"].split())
                        == " ".join(r["reference"].split())
                        for r in generated
                    ]
                )
            )
            if generated
            else None,
            "generation_cap_hits": sum(not r["ended_with_eod"] for r in generated),
        }
    result["paired_mean_ce_after_minus_before"] = float(
        np.mean(
            [
                b["answer_mean_ce"] - a["answer_mean_ce"]
                for a, b in zip(before, after, strict=True)
            ]
        )
    )
    result["scope"] = (
        "Previously used writing-validation references; exact match is not semantic factual accuracy. No teacher calls or model selection."
    )
    return result


def restore_frozen_adapter(
    model: torch.nn.Module, state: dict[str, torch.Tensor]
) -> str:
    """Restore the legacy trainable-only checkpoint, then disable every gradient."""
    for name, parameter in model.named_parameters():
        parameter.requires_grad_("lora_" in name)
    restore_parameters(model, state)
    digest = state_digest(trainable_state(model))
    model.requires_grad_(False)
    return digest


@build(config=ReadoutRetentionConfig)
def audit_writing_retention(context: StageContext[ReadoutRetentionConfig]) -> None:
    """Compare fixed writer/final adapters, using no gradients and no new teacher labels."""
    config = context.config
    progress.configure(config.progress_path)
    for name, digest in (
        ("writing_model", config.writing_model_sha256),
        ("final_model", config.final_model_sha256),
        ("targets", config.targets_sha256),
        ("head", config.head_sha256),
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
    ):
        checked(context.inputs[name], digest)
    targets = sorted(load_json(context.inputs["targets"]), key=lambda r: r["id"])
    validation_keys = native_layout(load_json(context.inputs["validation"]))[0]
    training_keys = native_layout(load_json(context.inputs["training"]))[0]
    allowed = {answer_id(p, c): (p, c) for c, p in validation_keys}
    forbidden = {answer_id(p, c) for c, p in training_keys}
    identities = [r["id"] for r in targets]
    if len(targets) != config.expected_targets or len(set(identities)) != len(targets):
        raise ValueError("The frozen writing-validation cohort changed.")
    for record in targets:
        if (
            record["id"] in forbidden
            or allowed.get(record["id"]) != (record["passage"], record["condition"])
            or not isinstance(record["answer"], str)
            or not record["answer"].strip()
        ):
            raise ValueError(
                "A writing probe is foreign, empty, or a training identity."
            )
    saved = load_model(context.inputs["writing_model"])
    fit = FitConfig.model_validate(
        {k: saved["config"][k] for k in FitConfig.model_fields if k in saved["config"]}
    )
    fit = fit.model_copy(update={"device": config.device})
    for name in ("model_id", "revision", "embedding_dimension", "max_length"):
        if getattr(config, name) != getattr(fit, name):
            raise ValueError(f"Writing-probe encoder differs: {name}.")
    tokenizer = load_tokenizer(config)
    rows = [
        {
            "condition": r["condition"],
            "sentence1": r["passage"],
            "sentence2": r["passage"],
        }
        for r in targets
    ]
    mapping = {r["id"]: r["answer"] for r in targets}
    sequences = evidence_tokens(rows, mapping, tokenizer, fit, config.max_answer_tokens)
    head_config = QwenEvidenceConfig(
        **fit.model_dump(),
        arm="evidence",
        phase="pretrain",
        training_sha256=config.training_sha256,
        validation_sha256=config.validation_sha256,
        prepared_sha256=config.targets_sha256,
        head_sha256=config.head_sha256,
    )
    head = load_head(context.inputs["head"], head_config)
    model = load_backbone(fit, adapters=fit).eval()
    all_records = {}
    eod = tokenizer.get_vocab()[EOD]
    for label, binding in (
        ("writing", "writing_model"),
        ("after_ratings", "final_model"),
    ):
        checkpoint = (
            saved if label == "writing" else load_model(context.inputs[binding])
        )
        if {
            k: checkpoint["config"].get(k)
            for k in (
                "model_id",
                "revision",
                "embedding_dimension",
                "max_length",
                "lora_rank",
                "lora_alpha",
            )
        } != {
            k: saved["config"].get(k)
            for k in (
                "model_id",
                "revision",
                "embedding_dimension",
                "max_length",
                "lora_rank",
                "lora_alpha",
            )
        }:
            raise ValueError("The writing/final adapter architectures differ.")
        initial_digest = restore_frozen_adapter(model, checkpoint["state"])
        records = []
        with torch.inference_mode():
            for i, record in enumerate(targets):
                ids, labels = sequences[record["id"]]
                prefix = ids[
                    : next(j for j, value in enumerate(labels) if value != -100)
                ]
                # A single occurrence avoids the pair sampler's duplicate exposure.
                batch = pad_sequences(tokenizer, [ids], fit)
                gold = torch.tensor([labels], device=config.device)
                with torch.autocast(
                    config.device,
                    enabled=config.device == "cuda",
                    dtype=torch.bfloat16,
                    cache_enabled=False,
                ):
                    hidden = model(**batch).last_hidden_state
                    ce = float(answer_loss_sum(hidden, gold, head))
                generated, ended = None, None
                if i < min(config.generated_samples, len(targets)):
                    answer_tokens = []
                    for _ in range(config.max_answer_tokens):
                        batch = pad_sequences(tokenizer, [prefix + answer_tokens], fit)
                        with torch.autocast(
                            config.device,
                            enabled=config.device == "cuda",
                            dtype=torch.bfloat16,
                            cache_enabled=False,
                        ):
                            last = model(**batch).last_hidden_state[:, -1]
                            token = int(head(last).argmax(-1).item())
                        if token == eod:
                            break
                        answer_tokens.append(token)
                    ended = token == eod
                    generated = tokenizer.decode(
                        answer_tokens, skip_special_tokens=False
                    )
                records.append(
                    {
                        "id": record["id"],
                        "answer_mean_ce": ce,
                        "reference": record["answer"],
                        "generated": generated,
                        "ended_with_eod": ended,
                    }
                )
                if (i + 1) % 16 == 0 or i + 1 == len(targets):
                    emit(
                        "writing_retention",
                        checkpoint=label,
                        completed=i + 1,
                        total=len(targets),
                    )
        if (
            state_digest({n: p for n, p in model.named_parameters() if "lora_" in n})
            != initial_digest
        ):
            raise ValueError(
                "Adapter bytes changed during writing retention inference."
            )
        all_records[label] = records
    report = retention_summary(all_records["writing"], all_records["after_ratings"])
    write_json(context.outputs["report"], report)
    emit("writing_retention_scores", results=report)
    write_json(context.outputs["predictions"], all_records)
