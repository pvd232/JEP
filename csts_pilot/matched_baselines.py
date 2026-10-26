"""Fit matched semantic-reference representations over frozen Qwen states."""

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any

import torch
from pydantic import Field
from torch import nn
from torch.nn import functional as F
from viper.config import BuildConfig, TrainConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, train

from csts_pilot.baseline_models import (
    EOD,
    PROMPT,
    EncoderConfig,
    FitConfig,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    trainable_state,
    validate_rows,
)
from csts_pilot.baseline_stages import scored_rows
from csts_pilot.condition_reference import (
    MODEL_SHA256,
    native_layout,
    pooled_states,
)
from csts_pilot.convergence import file_sha256, reset_rng, synchronize, write_json
from csts_pilot.data import canonical
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from jep_pilot.loaders import load_json, load_model

ARMS = ("native", "same_passage", "population", "projection", "case")
FITTED_ARMS = ARMS[1:]
GENERIC_CONDITION = "overall meaning"
MIN_NORM = 1e-8


def emit(event: str, **values: Any) -> None:
    """Flush one event to stdout and the current Tranche 5 sidecar."""
    message = json.dumps({"event": event, **values}, allow_nan=False)
    print(message, flush=True)
    if destination := os.environ.get("CSTS_TRANCHE5_EVENTS"):
        with Path(destination).open("a") as stream:
            stream.write(message + "\n")
            stream.flush()


class PreparationConfig(BuildConfig):
    """Bind the reference bank to disjoint prepared training/validation inputs."""

    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_size: int = Field(default=16, ge=1)
    seed: int = 7


class ExtractionConfig(EncoderConfig):
    """Bound a frozen-model feature extraction and its reference populations."""

    model_sha256: str = MODEL_SHA256
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split: str
    max_seconds: float = Field(default=5400, gt=0)


class HeadConfig(TrainConfig):
    """Fix the shared scorer and exact training/cache identities for one arm."""

    arm: str
    seed: int = 7
    device: str = "cuda"
    output_dim: int = Field(default=512, ge=1)
    dropout: float = Field(default=0.15, ge=0, lt=1)
    learning_rate: float = Field(default=1e-3, gt=0)
    weight_decay: float = Field(default=0.01, ge=0)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    max_seconds: float = Field(default=600, gt=0)
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: str = MODEL_SHA256
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def choose_bank(
    training: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    bank_size: int = 16,
    seed: int = 7,
) -> dict[str, Any]:
    """Select one text per hashed source group without reading any ratings."""
    validate_rows(training)
    validate_rows(validation)
    group_sets = [{r["group_id"] for r in rows} for rows in (training, validation)]
    if group_sets[0] & group_sets[1]:
        raise ValueError("Training and validation source groups overlap.")
    seen: dict[str, str] = {}
    groups: dict[str, set[str]] = {}
    for row in training:
        group = row["group_id"]
        for side in ("sentence1", "sentence2"):
            text = row[side]
            key = canonical(text)
            if key in seen and seen[key] != group:
                raise ValueError(
                    "A canonical caption occurs in multiple source groups."
                )
            seen[key] = group
            groups.setdefault(group, set()).add(text)
    if any(
        canonical(r[s]) in seen for r in validation for s in ("sentence1", "sentence2")
    ):
        raise ValueError("Training and validation captions overlap.")
    if not 1 <= bank_size < len(groups):
        raise ValueError(
            "The bank must leave source groups available for head fitting."
        )

    def order(text: str) -> str:
        return hashlib.sha256(f"matched-bank-61026:{seed}:{text}".encode()).hexdigest()

    chosen = sorted(groups, key=lambda g: (order(g), g))[:bank_size]
    passages = [min(groups[g], key=lambda p: (order(canonical(p)), p)) for g in chosen]
    return {
        "passages": passages,
        "groups": chosen,
        "excluded_training_groups": chosen,
        "seed": seed,
        "bank_size": bank_size,
        "selection_salt": "matched-bank-61026",
    }


def head_fit_rows(
    rows: list[dict[str, Any]], bank: dict[str, Any]
) -> list[dict[str, Any]]:
    """Use the same bank-disjoint head-fitting cohort for every representation."""
    excluded = set(bank["excluded_training_groups"])
    selected = [r for r in rows if r["group_id"] not in excluded]
    if not selected:
        raise ValueError("No training comparisons remain after bank reservation.")
    return selected


@build(config=PreparationConfig)
def prepare(context: StageContext[PreparationConfig]) -> None:
    """Seal the training-only bank and record the shared head-fitting cohort."""
    config = context.config
    for name in ("training", "validation"):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed preparation input: {name}.")
    training, validation = (
        load_json(context.inputs[n]) for n in ("training", "validation")
    )
    bank = choose_bank(training, validation, config.bank_size, config.seed)
    bank.update(
        training_sha256=config.training_sha256,
        validation_sha256=config.validation_sha256,
    )
    fitted = head_fit_rows(training, bank)
    write_json(context.outputs["bank"], bank)
    write_json(
        context.outputs["audit"],
        {
            "training_rows": len(training),
            "head_fit_rows": len(fitted),
            "excluded_groups": bank["groups"],
            "head_fit_row_ids": [r["row_id"] for r in fitted],
            "bank_sha256": file_sha256(context.outputs["bank"]),
            "validation_labels_used_for_bank_selection": False,
            "frozen_parent_previously_trained_on_bank_groups": True,
        },
    )


def prompt_text(passage: str, condition: str, case: bool = False) -> str:
    """Match CASE's text roles while retaining our declared explicit EOD readout."""
    if not case:
        return PROMPT.format(passage=passage, condition=condition)
    if not passage:
        return f"Instruct : Retrieve semantically similar texts Query : {condition}"
    return (
        "Instruct : Retrieve semantically similar texts to a given Query, under the given Condition "
        f"Query : {condition}\nCondition : {passage}"
    )


@build(config=ExtractionConfig)
def extract(context: StageContext[ExtractionConfig]) -> None:
    """Cache raw final states, matched generic states, and empirical references."""
    config = context.config
    started = time.monotonic()
    for name, expected in (
        ("model", config.model_sha256),
        ("rows", config.rows_sha256),
        ("bank", config.bank_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed feature extraction input: {name}.")
    rows, bank = load_json(context.inputs["rows"]), load_json(context.inputs["bank"])
    validate_rows(rows)
    if config.split != "training" and set(bank["groups"]) & {
        r["group_id"] for r in rows
    }:
        raise ValueError(
            "A reference-bank source group overlaps this evaluation cohort."
        )
    keys, left, right = native_layout(rows)
    conditions = sorted({c for c, _ in keys})
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    for name in ("model_id", "revision", "max_length", "embedding_dimension"):
        if getattr(config, name) != getattr(fit, name):
            raise ValueError(f"Frozen checkpoint setting changed: {name}.")
    if config.encode_batch_size != 4 or fit.microbatch_size != 2:
        raise ValueError("Native reproduction requires original two-pair forwards.")
    tokenizer = load_tokenizer(config)
    eod = tokenizer.get_vocab().get(EOD)
    if eod is None:
        raise ValueError("The pinned tokenizer lacks EOD.")
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    model.eval()
    model.requires_grad_(False)
    del saved
    tokens = 0
    last_report = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    def encode_texts(texts: list[str], label: str) -> torch.Tensor:
        nonlocal tokens, last_report
        encoded = tokenizer(
            texts, add_special_tokens=False, padding=False, truncation=False
        )["input_ids"]
        sequences = [[*ids, eod] for ids in encoded]
        if any(len(ids) > config.max_length for ids in sequences):
            raise ValueError(f"Token ceiling exceeded in {label}.")
        result = []
        with torch.inference_mode():
            for start in range(0, len(sequences), config.encode_batch_size):
                if time.monotonic() - started >= config.max_seconds:
                    raise TimeoutError("Extraction allowance exhausted.")
                batch = pad_sequences(
                    tokenizer,
                    sequences[start : start + config.encode_batch_size],
                    config,
                )
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    hidden = model(**batch).last_hidden_state
                raw, _ = pooled_states(hidden, batch["attention_mask"], None)
                result.append(raw.cpu())
                tokens += int(batch["attention_mask"].sum())
                now = time.monotonic()
                if now - last_report >= 15 or (
                    not label.startswith("bank_") and start + len(raw) == len(sequences)
                ):
                    emit(
                        "matched_extraction_progress",
                        split=config.split,
                        kind=label,
                        done=start + len(raw),
                        total=len(sequences),
                        seconds=now - started,
                    )
                    last_report = now
        return torch.cat(result)

    native = encode_texts([prompt_text(p, c) for c, p in keys], "native")
    generic = encode_texts(
        [prompt_text(p, GENERIC_CONDITION) for _, p in keys], "generic"
    )
    case = encode_texts([prompt_text(p, c, True) for c, p in keys], "case")
    case_references = encode_texts(
        [prompt_text("", c, True) for c in conditions], "case_reference"
    )
    bank_generic = encode_texts(
        [prompt_text(p, GENERIC_CONDITION) for p in bank["passages"]], "bank_generic"
    )
    corrections = []
    for i, condition in enumerate(conditions):
        states = encode_texts(
            [prompt_text(p, condition) for p in bank["passages"]],
            f"bank_{i + 1}/{len(conditions)}",
        )
        corrections.append((states - bank_generic).mean(0))
    synchronize(config.device)
    after = state_digest({n: p for n, p in model.named_parameters() if "lora_" in n})
    if before != after:
        raise ValueError("Frozen adapter bytes changed.")
    cache = {
        "keys": keys,
        "left": left,
        "right": right,
        "native": native,
        "generic": generic,
        "case": case,
        "condition_keys": conditions,
        "corrections": torch.stack(corrections),
        "case_references": case_references,
        "rows_sha256": config.rows_sha256,
        "bank_sha256": config.bank_sha256,
        "model_sha256": config.model_sha256,
        "embedding_dimension": config.embedding_dimension,
        "generic_condition": GENERIC_CONDITION,
        "revision": config.revision,
        "bank_passages": bank["passages"],
        "batching": "original_two_pairs_left_then_right",
        "adapter_before_sha256": before,
        "adapter_after_sha256": after,
    }
    validate_feature_cache(cache)
    torch.save(cache, context.outputs["cache"])
    write_json(
        context.outputs["timing"],
        {
            "split": config.split,
            "seconds": time.monotonic() - started,
            "nonpadding_tokens": tokens,
            "passage_occurrences": len(keys),
            "condition_count": len(conditions),
            "bank_size": len(bank["passages"]),
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
            "optimizer_updates": 0,
            "cache_sha256": file_sha256(context.outputs["cache"]),
            "rows_sha256": config.rows_sha256,
            "model_sha256": config.model_sha256,
            "bank_sha256": config.bank_sha256,
        },
    )


def validate_feature_cache(cache: dict[str, Any]) -> None:
    """Reject incomplete, nonfinite or ambiguous feature populations."""
    keys = [tuple(k) for k in cache["keys"]]
    for name in ("model_sha256", "rows_sha256", "bank_sha256"):
        digest = cache.get(name, "")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise ValueError(f"Invalid cache identity: {name}.")
    dimension = cache.get("embedding_dimension", 4096)
    conditions = cache["condition_keys"]
    if (
        not keys
        or len(conditions) != len(set(conditions))
        or set(conditions) != {c for c, _ in keys}
    ):
        raise ValueError("Condition-key coverage differs.")
    for name in ("native", "generic", "case", "corrections", "case_references"):
        values = cache[name]
        expected = (
            len(conditions)
            if name in {"corrections", "case_references"}
            else len(keys),
            dimension,
        )
        if values.shape != expected or not torch.isfinite(values).all():
            raise ValueError(f"Invalid feature shape or finite coverage: {name}.")
        if name != "corrections" and (values.norm(dim=1) <= MIN_NORM).any():
            raise ValueError(f"Zero feature vector: {name}.")
    if len(cache["left"]) != len(cache["right"]) or len(cache["left"]) * 2 != len(keys):
        raise ValueError("Comparison occurrence coverage differs.")
    indices = cache["left"] + cache["right"]
    if sorted(indices) != list(range(len(keys))):
        raise ValueError("Comparison indices must cover every passage occurrence once.")


def make_features(cache: dict[str, Any], arm: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Return raw states and the fixed subtraction term for the selected arm."""
    validate_feature_cache(cache)
    if arm not in ARMS:
        raise ValueError(f"Unknown representation arm: {arm}.")
    raw = cache["native"]
    if arm == "native":
        return raw, torch.zeros_like(raw)
    if arm == "same_passage":
        return raw, cache["generic"]
    lookup = {c: i for i, c in enumerate(cache["condition_keys"])}
    indices = [lookup[c] for c, _ in cache["keys"]]
    if arm == "case":
        return cache["case"], cache["case_references"][indices]
    bank = cache["corrections"][indices]
    squared_norm = bank.square().sum(1, keepdim=True)
    if (squared_norm <= MIN_NORM**2).any():
        raise ValueError("Zero population direction; fail the affected population arm.")
    return raw, bank


def validate_cache_rows(cache: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    """Bind both occurrence indices to the exact semantic comparison inputs."""
    validate_feature_cache(cache)
    if len(cache["left"]) != len(rows):
        raise ValueError("Cache/cohort comparison counts differ.")
    for row, left, right in zip(rows, cache["left"], cache["right"], strict=True):
        if tuple(cache["keys"][left]) != (row["condition"], row["sentence1"]) or tuple(
            cache["keys"][right]
        ) != (row["condition"], row["sentence2"]):
            raise ValueError(f"Cache semantic row binding differs: {row['row_id']}.")


class CorrectedHead(nn.Module):
    """Learn a bounded correction and the shared nonlinear projection."""

    def __init__(
        self,
        arm: str,
        input_dim: int = 4096,
        output_dim: int = 512,
        dropout: float = 0.15,
    ):
        super().__init__()
        if arm not in ARMS:
            raise ValueError("Unknown representation arm.")
        self.arm = arm
        self.linear = nn.Linear(input_dim, output_dim, bias=False)
        self.dropout = nn.Dropout(dropout)
        if arm in {"same_passage", "population", "projection"}:
            self.alpha_logit = nn.Parameter(torch.tensor(0.0))
        else:
            self.register_parameter("alpha_logit", None)

    @property
    def alpha(self) -> torch.Tensor:
        """Return a sigmoid strength or the fixed native/CASE endpoint."""
        if self.alpha_logit is not None:
            return self.alpha_logit.sigmoid()
        return self.linear.weight.new_tensor(1.0 if self.arm == "case" else 0.0)

    def residual(self, raw: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
        """Apply the prepared reference before projection and normalization."""
        if self.arm == "projection":
            denominator = reference.square().sum(1, keepdim=True)
            if (denominator <= MIN_NORM**2).any():
                raise ValueError("Undefined projection reference direction.")
            reference = (raw * reference).sum(1, keepdim=True) / denominator * reference
        return raw - self.alpha * reference

    def forward(self, raw: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
        """Score only finite, nonzero residuals and projected states."""
        # Native workers may enable autocast around the stage. Preserve the
        # cache/head dtype here, including float64 used by gradient checks.
        with torch.autocast(raw.device.type, enabled=False):
            residual = self.residual(raw, reference)
            if (
                not torch.isfinite(residual).all()
                or (residual.norm(dim=1) <= MIN_NORM).any()
            ):
                raise ValueError(
                    "Undefined residual direction; preserve full cohort coverage."
                )
            values = self.dropout(
                F.leaky_relu(self.linear(residual), negative_slope=0.01)
            )
            if (
                not torch.isfinite(values).all()
                or (values.norm(dim=1) <= MIN_NORM).any()
            ):
                raise ValueError("Undefined projected direction.")
            return F.normalize(values, dim=1)


def scores_from_cache(
    saved: dict[str, Any], cache: dict[str, Any], device: str = "cpu"
) -> list[float]:
    """Restore one selected small scorer and retain original comparison order."""
    for key in ("model_sha256", "bank_sha256"):
        if saved["config"][key] != cache[key]:
            raise ValueError(f"Scorer/cache identity changed: {key}.")
    config = saved["config"]
    head = CorrectedHead(
        config["arm"],
        cache["embedding_dimension"],
        config["output_dim"],
        config["dropout"],
    ).to(device)
    head.load_state_dict(saved["state"], strict=True)
    return predict_head(head, cache, device)


def predict_head(
    head: CorrectedHead, cache: dict[str, Any], device: str = "cpu"
) -> list[float]:
    """Run the current head in evaluation mode on every occurrence."""
    raw, reference = make_features(cache, head.arm)
    head.eval()
    vectors = []
    with torch.no_grad():
        for start in range(0, len(raw), 256):
            vectors.append(
                head(
                    raw[start : start + 256].to(device),
                    reference[start : start + 256].to(device),
                ).cpu()
            )
    z = torch.cat(vectors)
    return (z[cache["left"]] * z[cache["right"]]).sum(1).tolist()


def select_candidates(metrics: dict[str, Any]) -> dict[str, Any]:
    """Require a validation gain over the saved native comparator."""
    for measured in metrics.values():
        values = (
            measured["spearman"],
            measured["condition_changes"]["accuracy_ties_half"],
            measured["operating_point"]["false_positive_rate"],
        )
        if any(v is None or not math.isfinite(v) for v in values):
            raise ValueError("Candidate selection requires finite complete metrics.")
    controls = [metrics["native_direct"]]
    eligibility = {}
    for arm in ARMS[1:]:
        value = metrics[arm]
        rank = value["spearman"]
        ordering = value["condition_changes"]["accuracy_ties_half"]
        fpr = value["operating_point"]["false_positive_rate"]
        valid = rank is not None and ordering is not None and fpr is not None
        eligible = valid and all(
            rank >= c["spearman"] + 0.005 - 1e-12
            and ordering >= c["condition_changes"]["accuracy_ties_half"] - 0.01 - 1e-12
            and fpr <= c["operating_point"]["false_positive_rate"] + 0.01 + 1e-12
            for c in controls
        )
        eligibility[arm] = {"eligible": bool(eligible)}
    candidates = [a for a in ARMS[1:] if eligibility[a]["eligible"]]
    winner = (
        min(
            candidates,
            key=lambda a: (
                -metrics[a]["spearman"],
                metrics[a]["operating_point"]["false_positive_rate"],
                -metrics[a]["condition_changes"]["accuracy_ties_half"],
                ARMS.index(a),
            ),
        )
        if candidates
        else None
    )
    return {
        "selected_arm": winner,
        "eligibility": eligibility,
        "thresholds": {a: m["operating_point"]["cutoff"] for a, m in metrics.items()},
        "test_scores_used_for_selection": False,
    }


@train(config=HeadConfig)
def fit_head(context: StageContext[HeadConfig]) -> None:
    """Fit only the small projection and correction scalar on cached states."""
    config = context.config
    if config.arm not in FITTED_ARMS:
        raise ValueError("Only the four alternative heads are fitted in this study.")
    for name in (
        "training",
        "validation",
        "bank",
        "training_cache",
        "validation_cache",
    ):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed head-fitting input: {name}.")
    bank = load_json(context.inputs["bank"])
    training, validation = (
        load_json(context.inputs[n]) for n in ("training", "validation")
    )
    train_cache, val_cache = (
        load_model(context.inputs[n]) for n in ("training_cache", "validation_cache")
    )
    for rows, cache, expected in (
        (training, train_cache, config.training_sha256),
        (validation, val_cache, config.validation_sha256),
    ):
        if (
            cache["rows_sha256"] != expected
            or cache["model_sha256"] != config.model_sha256
            or cache["bank_sha256"] != config.bank_sha256
        ):
            raise ValueError("Feature cache provenance differs from the head contract.")
        validate_cache_rows(cache, rows)
    fitted = head_fit_rows(training, bank)
    fit_ids_sha = hashlib.sha256(
        json.dumps([r["row_id"] for r in fitted], separators=(",", ":")).encode()
    ).hexdigest()
    fit_ids = {r["row_id"] for r in fitted}
    included = torch.tensor(
        [i for i, r in enumerate(training) if r["row_id"] in fit_ids]
    )
    raw, reference = make_features(train_cache, config.arm)
    left = torch.tensor(train_cache["left"])
    right = torch.tensor(train_cache["right"])
    reset_rng(config.seed)
    head = CorrectedHead(
        config.arm,
        train_cache["embedding_dimension"],
        config.output_dim,
        config.dropout,
    ).to(config.device)
    initial = state_digest({"weight": head.linear.weight.detach()})
    parameter_groups = [
        {"params": [head.linear.weight], "weight_decay": config.weight_decay}
    ]
    if head.alpha_logit is not None:
        parameter_groups.append({"params": [head.alpha_logit], "weight_decay": 0.0})
    optimizer = torch.optim.AdamW(
        parameter_groups, lr=config.learning_rate, betas=(0.9, 0.999), eps=1e-8
    )
    generator = torch.Generator().manual_seed(config.seed + 100)
    targets = torch.tensor([r["target"] for r in training], device=config.device)
    stopping = ValidationPatience(config.patience)
    started = time.monotonic()
    history, best_score, selected_epoch = [], -math.inf, 0

    def checkpoint(epoch: int) -> dict[str, Any]:
        predictions = scored_rows(
            validation, predict_head(head, val_cache, config.device)
        )
        measured = summarize(predictions)
        score = measured["spearman"]
        if score is None:
            raise ValueError("Validation Spearman is undefined.")
        nonlocal best_score, selected_epoch
        if score > best_score:
            best_score, selected_epoch = score, epoch
            torch.save(
                {
                    "config": config.model_dump(),
                    "state": {
                        n: p.detach().cpu().clone()
                        for n, p in head.state_dict().items()
                    },
                    "epoch": epoch,
                    "alpha": float(head.alpha.detach()),
                    "initial_head_sha256": initial,
                    "head_fit_row_ids": [r["row_id"] for r in fitted],
                    "validation": measured,
                },
                context.outputs["model"],
            )
            write_json(context.outputs["validation_predictions"], predictions)
        context.metrics["validation_spearman"].record(score, step=epoch)
        context.metrics["validation_mse"].record(measured["mse_0_1"], step=epoch)
        return measured

    initial_metrics = checkpoint(0)
    stopping.observe(initial_metrics["spearman"])
    stop_reason, updates = "epoch_budget", 0
    for epoch in range(1, config.max_epochs + 1):
        if time.monotonic() - started >= config.max_seconds:
            stop_reason = "resource_budget"
            break
        head.train()
        order = included[torch.randperm(len(included), generator=generator)]
        squared_error = 0.0
        for start in range(0, len(order), config.batch_size):
            if time.monotonic() - started >= config.max_seconds:
                raise TimeoutError(
                    "Head budget ended within an epoch; preserve this failed attempt."
                )
            ix = order[start : start + config.batch_size]
            positions = torch.cat((left[ix], right[ix]))
            optimizer.zero_grad(set_to_none=True)
            vectors = head(
                raw[positions].to(config.device), reference[positions].to(config.device)
            )
            a, b = vectors.chunk(2)
            prediction = (a * b).sum(1)
            loss = F.mse_loss(prediction, targets[ix.to(config.device)])
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite head MSE.")
            loss.backward()
            nn.utils.clip_grad_norm_(head.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step()
            squared_error += float(loss.detach()) * len(ix)
            updates += 1
        measured = checkpoint(epoch)
        context.metrics["training_objective"].record(
            squared_error / len(included), step=epoch
        )
        record = {
            "epoch": epoch,
            "training_mse": squared_error / len(included),
            "validation": measured,
            "alpha": float(head.alpha.detach()),
            "seconds": time.monotonic() - started,
        }
        history.append(record)
        write_json(
            context.outputs["trace"],
            {
                "status": "running",
                "arm": config.arm,
                "epochs": history,
                "selected_epoch": selected_epoch,
            },
        )
        emit("matched_head_epoch", arm=config.arm, **record)
        if stopping.observe(measured["spearman"]):
            stop_reason = "validation_patience"
            break
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={
                "optimizer": optimizer.state_dict(),
                "terminal_head": head.state_dict(),
            },
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "updates": updates,
                    "generator_state": generator.get_state(),
                    "training_cache_sha256": config.training_cache_sha256,
                    "head_fit_row_ids": [r["row_id"] for r in fitted],
                    "epoch": len(history),
                },
            ),
        ),
    )
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "arm": config.arm,
            "epochs": history,
            "selected_epoch": selected_epoch,
            "stop_reason": stop_reason,
            "updates": updates,
            "initial_head_sha256": initial,
            "selected_model_sha256": file_sha256(context.outputs["model"]),
            "head_fit_ids_sha256": fit_ids_sha,
            "training_rows": len(fitted),
            "completed_epochs": len(history),
            "selected": {
                "epoch": selected_epoch,
                "validation": load_model(context.outputs["model"])["validation"],
            },
            "elapsed_seconds": time.monotonic() - started,
            "frozen_encoder_optimizer_updates": 0,
            "head_fit_rows": len(included),
            "bank_groups_excluded": bank["excluded_training_groups"],
        },
    )
