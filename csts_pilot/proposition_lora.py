"""Warm-start answer-input LoRA from saved weights with fresh training state."""

from types import SimpleNamespace
from typing import Literal

from pydantic import Field, model_validator
from viper.stages import StageContext, train

from csts_pilot.answer_input import emit
from csts_pilot.baseline_models import (
    FitConfig,
    TokenPairs,
    load_backbone,
    load_tokenizer,
    restore_parameters,
    state_digest,
    trainable_state,
    validate_rows,
)
from csts_pilot.baseline_stages import fit_neural
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from jep_pilot.loaders import load_json, load_model


class PropositionLoraConfig(FitConfig):
    """Bind changed answer inputs to one selected adapter initialization."""

    kind: Literal["lora"] = "lora"
    start_epoch: Literal[0] = 0
    parent_model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_fresh_phase(self) -> "PropositionLoraConfig":
        """Keep this a fresh constant-rate phase rather than optimizer continuation."""
        if self.schedule != "constant" or self.warmup_fraction:
            raise ValueError(
                "Answer-input adaptation uses a fresh constant-rate phase."
            )
        return self

    def fit_config(self) -> FitConfig:
        """Exclude provenance-only fields from saved inference checkpoints."""
        return FitConfig.model_validate(
            {name: getattr(self, name) for name in FitConfig.model_fields}
        )


@train(config=PropositionLoraConfig)
def fit_proposition_lora(context: StageContext[PropositionLoraConfig]) -> None:
    """Restore adapter weights, then reuse the existing fresh rating-MSE trainer.

    Inputs are ``model``, ``training`` and ``validation``. In addition to the
    standard neural training outputs, declare ``warm_start`` for initialization
    evidence. No optimizer, scheduler, dataloader or RNG state is restored from
    the original passage-training run.
    """
    config = context.config
    for name, digest in (
        ("model", config.parent_model_sha256),
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed proposition-LoRA input: {name}.")
    saved = load_model(context.inputs["model"])
    parent = FitConfig.model_validate(saved["config"])
    if saved.get("kind") != "lora" or parent.kind != "lora":
        raise ValueError("Answer-input adaptation requires a saved LoRA checkpoint.")
    fit = config.fit_config()
    for name in (
        "model_id",
        "revision",
        "max_length",
        "embedding_dimension",
        "lora_rank",
        "lora_alpha",
        "lora_dropout",
    ):
        if getattr(parent, name) != getattr(fit, name):
            raise ValueError(f"Parent adapter or encoder setting differs: {name}.")

    rows = {
        name: load_json(context.inputs[name]) for name in ("training", "validation")
    }
    for selected in rows.values():
        validate_rows(selected)
    for identity in ("row_id", "group_id"):
        if {r[identity] for r in rows["training"]} & {
            r[identity] for r in rows["validation"]
        }:
            raise ValueError(f"Answer training and validation share {identity}.")

    reset_rng(fit.seed)
    tokenizer = load_tokenizer(fit)
    # TokenPairs checks every sequence without truncation before GPU allocation.
    training = TokenPairs(rows["training"], fit, tokenizer)
    validation = TokenPairs(rows["validation"], fit, tokenizer)
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    initial_state = trainable_state(model)
    expected_state = {
        name: value.to(dtype=initial_state[name].dtype)
        for name, value in saved["state"].items()
    }
    initial_digest = state_digest(initial_state)
    if initial_digest != state_digest(expected_state):
        raise ValueError("Restored adapter weights differ from their saved values.")
    audit = {
        "status": "initialized",
        "parent_model_sha256": config.parent_model_sha256,
        "parent_state_sha256": state_digest(saved["state"]),
        "initial_trainable_sha256": initial_digest,
        "training_sha256": config.training_sha256,
        "validation_sha256": config.validation_sha256,
        "fresh_optimizer": True,
        "restored_optimizer_state": False,
        "start_epoch": 0,
        "optimizer_updates_at_start": 0,
        "attention_targets": ["q_proj", "k_proj", "v_proj", "o_proj"],
        "parent_config": parent.model_dump(),
        "protocol_config": config.model_dump(),
    }
    context.outputs["warm_start"].parent.mkdir(parents=True, exist_ok=True)
    write_json(context.outputs["warm_start"], audit)
    del initial_state, expected_state, saved
    # Model loading does not determine dropout or batch-order randomness.
    reset_rng(fit.seed)
    inner = SimpleNamespace(
        config=fit,
        inputs=context.inputs,
        outputs=context.outputs,
        metrics=context.metrics,
        numpy_generators=context.numpy_generators,
    )
    emit("proposition_lora_live_trace", trace_path=str(context.outputs["trace"]))
    fit_neural(inner, model, training, validation)
    trace = load_json(context.outputs["trace"])
    if trace["initial_trainable_sha256"] != initial_digest:
        raise ValueError("The training trace starts from different adapter weights.")
    if trace["config"] != fit.model_dump():
        raise ValueError("The training trace uses a different fit configuration.")
    audit["status"] = "complete"
    audit["selected_model_sha256"] = trace["selected"]["sha256"]
    audit["actual_updates"] = trace["actual_updates"]
    trace["warm_start"] = audit
    write_json(context.outputs["warm_start"], audit)
    write_json(context.outputs["trace"], trace)
