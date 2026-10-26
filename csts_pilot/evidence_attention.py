"""Read condition-relevant Qwen token states with a small supervised attention head."""

import hashlib
import json
import math
import os
import time
from itertools import pairwise
from typing import Any, Literal

import torch
from pydantic import Field
from torch import nn
from torch.nn import functional as F
from viper.config import TrainConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, train

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    PROMPT,
    EncoderConfig,
    FitConfig,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    token_sequences,
    trainable_state,
    validate_rows,
)
from csts_pilot.baseline_stages import scored_rows
from csts_pilot.condition_reference import MODEL_SHA256, native_layout
from csts_pilot.convergence import file_sha256, reset_rng, synchronize, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from csts_pilot.evidence_controls import checked_cache
from csts_pilot.matched_baselines import head_fit_rows
from jep_pilot.loaders import load_json, load_model

ARMS = ("attention_ratings", "attention_evidence")
MIN_NORM = 1e-8
TEACHER_SHA256 = "1dcd743762cfad9f42b78775510c526e3ce6dd0c51716caf4df3234442ac1c94"


def emit(event: str, **values: Any) -> None:
    """Publish each completed measurement immediately to stdout and the sidecar."""
    message = json.dumps({"event": event, **values}, allow_nan=False)
    print(message, flush=True)
    if destination := os.environ.get("CSTS_ATTENTION_EVENTS"):
        with open(destination, "a") as stream:
            stream.write(message + "\n")
            stream.flush()


class AttentionExtractionConfig(EncoderConfig):
    """Pin the raw frozen-token representation and optional training evidence."""

    model_sha256: str = MODEL_SHA256
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split: Literal["training", "validation", "test"]
    answers_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    max_seconds: float = Field(default=4800, gt=0)


class AttentionFitConfig(TrainConfig):
    """Fit the same attention readout with zero or fixed evidence loss weight."""

    arm: Literal["attention_ratings", "attention_evidence"]
    seed: int = 7
    device: str = "cuda"
    query_dim: int = Field(default=128, ge=1)
    output_dim: int = Field(default=512, ge=1)
    dropout: float = Field(default=0.15, ge=0, lt=1)
    span_weight: float = Field(default=0.1, gt=0)
    learning_rate: float = Field(default=1e-3, gt=0)
    weight_decay: float = Field(default=0.01, ge=0)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    max_seconds: float = Field(default=900, gt=0)
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bank_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: str = MODEL_SHA256
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def token_metadata(
    tokenizer: Any, keys: list[tuple[str, str]], config: EncoderConfig
) -> list[dict[str, Any]]:
    """Bind character masks to the exact existing prompt/token IDs without truncation."""
    if not keys:
        raise ValueError("Token extraction needs nonempty passage keys.")
    texts = [PROMPT.format(condition=c, passage=p) for c, p in keys]
    encoded = tokenizer(
        texts,
        padding=False,
        truncation=False,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    sequences = token_sequences(tokenizer, keys, config)
    special = set(tokenizer.all_special_ids)
    prefix = PROMPT.split("{condition}", 1)[0]
    result = []
    for (condition, passage), text, ids, offsets, sequence in zip(
        keys,
        texts,
        encoded["input_ids"],
        encoded["offset_mapping"],
        sequences,
        strict=True,
    ):
        cstart, cend = len(prefix), len(prefix) + len(condition)
        pstart, pend = len(PROMPT.format(condition=condition, passage="")), len(text)
        if (
            text[cstart:cend] != condition
            or text[pstart:pend] != passage
            or ids != sequence[:-1]
        ):
            raise ValueError(
                "Prompt characters, tokenizer offsets and token IDs disagree."
            )
        condition_indices, passage_indices, passage_offsets = [], [], []
        for i, (token, offset) in enumerate(zip(ids, offsets, strict=True)):
            a, b = int(offset[0]), int(offset[1])
            if not 0 <= a <= b <= len(text):
                raise ValueError("Tokenizer returned an invalid character offset.")
            if token in special:
                continue
            if max(a, cstart) < min(b, cend):
                condition_indices.append(i)
            if max(a, pstart) < min(b, pend):
                passage_indices.append(i)
                passage_offsets.append((max(a, pstart) - pstart, min(b, pend) - pstart))
        if not condition_indices or not passage_indices:
            raise ValueError("Every input needs condition and passage token positions.")
        if set(condition_indices) & set(passage_indices):
            raise ValueError("Condition and passage masks overlap.")
        result.append(
            {
                "input_ids": sequence,
                "condition_indices": condition_indices,
                "passage_indices": passage_indices,
                "passage_offsets": passage_offsets,
            }
        )
    return result


def literal_span_targets(
    passage: str, answer: str, offsets: list[tuple[int, int]]
) -> torch.Tensor:
    """Distribute target mass across one unambiguous exact copied answer occurrence."""
    if any(not 0 <= a < b <= len(passage) for a, b in offsets):
        raise ValueError("Evidence offsets must lie inside the complete passage.")
    targets = torch.zeros(len(offsets), dtype=torch.float32)
    if not answer or answer == "NOT_SPECIFIED":
        return targets
    spans, start = [], 0
    while (found := passage.find(answer, start)) >= 0:
        spans.append((found, found + len(answer)))
        start = found + 1
    if len(spans) != 1:
        return targets
    for i, (a, b) in enumerate(offsets):
        targets[i] = float(any(max(a, s) < min(b, e) for s, e in spans))
    if targets.sum() > 0:
        targets /= targets.sum()
    return targets


class AttentionHead(nn.Module):
    """Query passage-token keys with condition-prefix states, then project the pooled value."""

    def __init__(
        self,
        input_dim: int = 4096,
        query_dim: int = 128,
        output_dim: int = 512,
        dropout: float = 0.15,
    ):
        super().__init__()
        self.query = nn.Linear(input_dim, query_dim, bias=False)
        self.key = nn.Linear(input_dim, query_dim, bias=False)
        self.projection = nn.Linear(input_dim, output_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        token_states: torch.Tensor,
        condition_states: torch.Tensor,
        token_mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Return unit passage vectors, masked attention logits and probability weights."""
        if (
            token_states.ndim != 3
            or condition_states.shape != (len(token_states), token_states.shape[-1])
            or token_mask.shape != token_states.shape[:2]
            or token_mask.dtype != torch.bool
            or not token_mask.any(1).all()
        ):
            raise ValueError(
                "Attention requires finite matching states and a nonempty Boolean token mask."
            )
        if (
            not torch.isfinite(token_states).all()
            or not torch.isfinite(condition_states).all()
        ):
            raise ValueError("Attention states must be finite, including padding.")
        with torch.autocast(token_states.device.type, enabled=False):
            dtype = self.query.weight.dtype
            tokens, condition = token_states.to(dtype), condition_states.to(dtype)
            width = tokens.shape[-1]
            query = self.query(F.layer_norm(condition, (width,)))
            keys = self.key(F.layer_norm(tokens, (width,)))
            logits = (keys * query[:, None, :]).sum(-1) / math.sqrt(query.shape[-1])
            logits = logits.masked_fill(~token_mask, -torch.inf)
            attention = logits.softmax(1)
            pooled = (tokens * attention.unsqueeze(-1)).sum(1)
            values = self.dropout(
                F.leaky_relu(self.projection(pooled), negative_slope=0.01)
            )
            if (
                not torch.isfinite(values).all()
                or (values.norm(dim=1) <= MIN_NORM).any()
            ):
                raise ValueError("Projected passage direction is undefined.")
            return F.normalize(values, dim=1), logits, attention


def span_loss(
    logits: torch.Tensor, token_mask: torch.Tensor, targets: torch.Tensor
) -> tuple[torch.Tensor, int]:
    """Average token-distribution cross-entropy over supplied evidence instances only."""
    if (
        logits.shape != token_mask.shape
        or targets.shape != logits.shape
        or token_mask.dtype != torch.bool
    ):
        raise ValueError("Span loss shapes or mask dtype differ.")
    if (
        not token_mask.any(1).all()
        or not torch.isfinite(targets).all()
        or (targets < 0).any()
    ):
        raise ValueError(
            "Span loss needs nonempty masks and finite nonnegative targets."
        )
    if (targets.masked_select(~token_mask) != 0).any() or not torch.isfinite(
        logits[token_mask]
    ).all():
        raise ValueError("Targets/logits disagree with the attended passage positions.")
    sums = targets.sum(1)
    supervised = sums > 0
    if not torch.allclose(
        sums[supervised], torch.ones_like(sums[supervised]), atol=1e-5, rtol=0
    ):
        raise ValueError("Every supplied evidence distribution must have unit mass.")
    count = int(supervised.sum())
    if not count:
        return logits[token_mask].sum() * 0, 0
    log_probabilities = (
        logits.masked_fill(~token_mask, -torch.inf)
        .log_softmax(1)
        .masked_fill(~token_mask, 0)
    )
    return -(targets * log_probabilities).sum(1)[supervised].mean(), count


def validate_token_cache(
    cache: dict[str, Any], rows: list[dict[str, Any]] | None = None
) -> None:
    """Validate packed feature coverage, exact semantic joins and training-only targets."""
    keys, pointers, values = cache["keys"], cache["pointers"], cache["token_values"]
    n = len(keys)
    if (
        not n
        or len(pointers) != n + 1
        or pointers[0] != 0
        or pointers[-1] != len(values)
    ):
        raise ValueError("Packed token boundaries do not cover the feature tensor.")
    if any(not isinstance(i, int) for i in pointers) or any(
        a >= b for a, b in pairwise(pointers)
    ):
        raise ValueError("Every token occurrence needs a positive packed length.")
    if (
        values.ndim != 2
        or values.shape[1] != cache["embedding_dimension"]
        or cache["condition_states"].shape != (n, cache["embedding_dimension"])
        or cache["span_targets"].shape != (len(values),)
    ):
        raise ValueError("Token-cache feature shapes differ.")
    for name in ("token_values", "condition_states", "span_targets"):
        if (
            not torch.is_floating_point(cache[name])
            or not torch.isfinite(cache[name]).all()
        ):
            raise ValueError(
                "Token-cache tensors must contain finite floating-point values."
            )
    if (cache["span_targets"] < 0).any() or len(cache["metadata"]) != n:
        raise ValueError("Invalid evidence weights or metadata coverage.")
    for key in ("rows_sha256", "bank_sha256", "model_sha256"):
        digest = cache[key]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            raise ValueError("Invalid token-cache content identity.")
    if cache["split"] not in {"training", "validation", "test"}:
        raise ValueError("Unknown token-cache partition.")
    expected_teacher = TEACHER_SHA256 if cache["split"] == "training" else None
    if cache.get("answers_sha256") != expected_teacher:
        raise ValueError(
            "Token-cache teacher identity differs from its partition contract."
        )
    for i, ((_, passage), meta) in enumerate(zip(keys, cache["metadata"], strict=True)):
        start, end = pointers[i : i + 2]
        if end - start != len(meta["passage_indices"]) or end - start != len(
            meta["passage_offsets"]
        ):
            raise ValueError("Packed state count differs from the passage-token mask.")
        if not meta["condition_indices"] or set(meta["condition_indices"]) & set(
            meta["passage_indices"]
        ):
            raise ValueError("Empty or overlapping condition/passage masks.")
        indices = meta["condition_indices"] + meta["passage_indices"]
        if any(
            not isinstance(v, int) or not 0 <= v < len(meta["input_ids"]) - 1
            for v in indices
        ):
            raise ValueError(
                "A selected token is padding, EOD or outside the source sequence."
            )
        if any(not 0 <= a < b <= len(passage) for a, b in meta["passage_offsets"]):
            raise ValueError("Saved passage offsets are invalid.")
        mass = float(cache["span_targets"][start:end].sum())
        if mass and abs(mass - 1) > 1e-5:
            raise ValueError("An evidence target has non-unit mass.")
    if cache["split"] != "training" and (cache["span_targets"] != 0).any():
        raise ValueError("Held-out token caches must contain zero teacher targets.")
    if rows is not None:
        validate_rows(rows)
        if n != 2 * len(rows):
            raise ValueError(
                "The token cache requires exactly two occurrences per comparison."
            )
        if len(cache["left"]) != len(rows) or len(cache["right"]) != len(rows):
            raise ValueError("Token-cache comparison coverage differs.")
        for row, left, right in zip(rows, cache["left"], cache["right"], strict=True):
            if (
                not isinstance(left, int)
                or not isinstance(right, int)
                or not (0 <= left < n and 0 <= right < n)
            ):
                raise ValueError("Invalid comparison token occurrence.")
            if tuple(keys[left]) != (row["condition"], row["sentence1"]) or tuple(
                keys[right]
            ) != (row["condition"], row["sentence2"]):
                raise ValueError(
                    "Token-cache indices attach the wrong passage/condition."
                )
        if set(cache["left"] + cache["right"]) != set(range(n)):
            raise ValueError(
                "Token-cache occurrences lack complete comparison coverage."
            )


def pack_batch(
    cache: dict[str, Any], positions: list[int] | torch.Tensor, device: str = "cpu"
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Pad just the requested packed occurrences and retain exact evidence masks."""
    selected = (
        positions.tolist() if isinstance(positions, torch.Tensor) else list(positions)
    )
    if not selected or any(
        not isinstance(i, int) or not 0 <= i < len(cache["keys"]) for i in selected
    ):
        raise ValueError("A batch needs valid token occurrence indices.")
    tokens, targets, masks = [], [], []
    for i in selected:
        a, b = cache["pointers"][i : i + 2]
        tokens.append(cache["token_values"][a:b])
        targets.append(cache["span_targets"][a:b])
        masks.append(torch.ones(b - a, dtype=torch.bool))
    return (
        nn.utils.rnn.pad_sequence(tokens, batch_first=True).to(
            device=device, dtype=torch.float32
        ),
        cache["condition_states"][selected].to(device=device, dtype=torch.float32),
        nn.utils.rnn.pad_sequence(masks, batch_first=True).to(device),
        nn.utils.rnn.pad_sequence(targets, batch_first=True).to(
            device=device, dtype=torch.float32
        ),
    )


@build(config=AttentionExtractionConfig)
def extract_tokens(context: StageContext[AttentionExtractionConfig]) -> None:
    """Cache passage tokens and causal condition-prefix means from the frozen selected LoRA."""
    config, started = context.config, time.monotonic()
    for name, expected in (
        ("model", config.model_sha256),
        ("rows", config.rows_sha256),
        ("bank", config.bank_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed attention extraction input: {name}.")
    rows, bank = load_json(context.inputs["rows"]), load_json(context.inputs["bank"])
    validate_rows(rows)
    if config.split != "training" and set(bank["groups"]) & {
        r["group_id"] for r in rows
    }:
        raise ValueError("A bank source group overlaps the held-out token cohort.")
    if config.split == "training":
        if (
            config.answers_sha256 != TEACHER_SHA256
            or file_sha256(context.inputs["answers"]) != TEACHER_SHA256
        ):
            raise ValueError("Use the existing pinned teacher evidence cache.")
        records = checked_cache(context.inputs["answers"])
    else:
        if config.answers_sha256 is not None or "answers" in context.inputs:
            raise ValueError(
                "Teacher targets are forbidden on held-out extraction inputs."
            )
        records = {}
    keys, left, right = native_layout(rows)
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    for name in ("model_id", "revision", "max_length", "embedding_dimension"):
        if getattr(config, name) != getattr(fit, name):
            raise ValueError(f"Frozen attention encoder setting changed: {name}.")
    if config.encode_batch_size != 4:
        raise ValueError("Keep the existing two-pair token extraction layout.")
    tokenizer = load_tokenizer(config)
    metadata = token_metadata(tokenizer, keys, config)
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    model.eval()
    model.requires_grad_(False)
    del saved
    values, queries, targets, pointers = [], [], [], [0]
    tokens, supervised, accepted, last_report = 0, 0, 0, started
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        for start in range(0, len(keys), config.encode_batch_size):
            if time.monotonic() - started >= config.max_seconds:
                raise TimeoutError("Frozen-token extraction allowance exhausted.")
            selected = metadata[start : start + config.encode_batch_size]
            batch = pad_sequences(tokenizer, [m["input_ids"] for m in selected], config)
            with torch.autocast(
                "cuda",
                dtype=torch.bfloat16,
                enabled=config.device == "cuda",
                cache_enabled=False,
            ):
                hidden = model(**batch).last_hidden_state
            for local, meta in enumerate(selected):
                index = start + local
                shift = (
                    hidden.shape[1] - len(meta["input_ids"])
                    if tokenizer.padding_side == "left"
                    else 0
                )
                p = torch.tensor(meta["passage_indices"], device=config.device) + shift
                c = (
                    torch.tensor(meta["condition_indices"], device=config.device)
                    + shift
                )
                value = hidden[local, p].detach().cpu().to(torch.bfloat16)
                query = hidden[local, c].float().mean(0).cpu()
                condition, passage = keys[index]
                record = records.get(answer_id(passage, condition))
                accepted += int(bool(record and record["valid"]))
                target = (
                    literal_span_targets(
                        passage, record["answer"], meta["passage_offsets"]
                    )
                    if record and record["valid"]
                    else torch.zeros(len(p), dtype=torch.float32)
                )
                supervised += int(float(target.sum()) > 0)
                values.append(value)
                queries.append(query)
                targets.append(target)
                pointers.append(pointers[-1] + len(p))
            tokens += int(batch["attention_mask"].sum())
            now = time.monotonic()
            if now - last_report >= 15 or start + len(selected) == len(keys):
                emit(
                    "attention_extraction_progress",
                    split=config.split,
                    done=start + len(selected),
                    total=len(keys),
                    seconds=now - started,
                )
                last_report = now
    synchronize(config.device)
    after = state_digest({n: p for n, p in model.named_parameters() if "lora_" in n})
    if before != after:
        raise ValueError("Frozen selected LoRA bytes changed during token extraction.")
    cache = {
        "keys": keys,
        "left": left,
        "right": right,
        "pointers": pointers,
        "token_values": torch.cat(values),
        "condition_states": torch.stack(queries),
        "span_targets": torch.cat(targets),
        "metadata": metadata,
        "embedding_dimension": config.embedding_dimension,
        "split": config.split,
        "rows_sha256": config.rows_sha256,
        "bank_sha256": config.bank_sha256,
        "model_sha256": config.model_sha256,
        "answers_sha256": config.answers_sha256,
        "revision": config.revision,
        "prompt": PROMPT,
        "adapter_before_sha256": before,
        "adapter_after_sha256": after,
        "query_rule": "mean_original_condition_token_states_before_passage_causal_prefix",
    }
    validate_token_cache(cache, rows)
    if config.split == "training" and not supervised:
        raise ValueError(
            "No literal teacher evidence spans survived exact token alignment."
        )
    torch.save(cache, context.outputs["cache"])
    write_json(
        context.outputs["timing"],
        {
            "split": config.split,
            "seconds": time.monotonic() - started,
            "passage_occurrences": len(keys),
            "passage_tokens": pointers[-1],
            "input_tokens": tokens,
            "teacher_accepted_occurrences": accepted,
            "literal_supervised_occurrences": supervised,
            "accepted_without_unambiguous_literal_alignment": accepted - supervised,
            "teacher_targets_used_for_held_out": False,
            "peak_cuda_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
            "cache_sha256": file_sha256(context.outputs["cache"]),
            "frozen_adapter_sha256": before,
        },
    )


def predict_head(
    head: AttentionHead, cache: dict[str, Any], device: str = "cpu"
) -> list[float]:
    """Read every cached occurrence once and score original comparison indices."""
    head.eval()
    vectors = []
    with torch.no_grad():
        for start in range(0, len(cache["keys"]), 64):
            tokens, queries, mask, _ = pack_batch(
                cache, list(range(start, min(start + 64, len(cache["keys"])))), device
            )
            vectors.append(head(tokens, queries, mask)[0].cpu())
    z = torch.cat(vectors)
    return (z[cache["left"]] * z[cache["right"]]).sum(1).tolist()


def scores_from_cache(
    saved: dict[str, Any], cache: dict[str, Any], device: str = "cpu"
) -> list[float]:
    """Restore an exact selected head while retaining frozen feature identities."""
    config = saved["config"]
    for key in ("model_sha256", "bank_sha256"):
        if config[key] != cache[key]:
            raise ValueError(f"Attention checkpoint/cache identity differs: {key}.")
    head = AttentionHead(
        cache["embedding_dimension"],
        config["query_dim"],
        config["output_dim"],
        config["dropout"],
    ).to(device)
    head.load_state_dict(saved["state"], strict=True)
    return predict_head(head, cache, device)


def select_candidates(metrics: dict[str, Any]) -> dict[str, Any]:
    """Use the existing native comparator and unchanged validation transfer guards."""
    baseline = metrics["native_direct"]
    eligibility = {}
    for arm in ARMS:
        candidate = metrics[arm]
        pairs = (
            (candidate["spearman"], baseline["spearman"]),
            (
                candidate["condition_changes"]["accuracy_ties_half"],
                baseline["condition_changes"]["accuracy_ties_half"],
            ),
            (
                candidate["operating_point"]["false_positive_rate"],
                baseline["operating_point"]["false_positive_rate"],
            ),
        )
        if any(v is None or not math.isfinite(v) for pair in pairs for v in pair):
            raise ValueError("Attention selection requires complete finite metrics.")
        eligibility[arm] = {
            "eligible": bool(
                pairs[0][0] >= pairs[0][1] + 0.005 - 1e-12
                and pairs[1][0] >= pairs[1][1] - 0.01 - 1e-12
                and pairs[2][0] <= pairs[2][1] + 0.01 + 1e-12
            )
        }
    eligible = [a for a in ARMS if eligibility[a]["eligible"]]
    selected = (
        min(
            eligible,
            key=lambda a: (
                -metrics[a]["spearman"],
                metrics[a]["operating_point"]["false_positive_rate"],
                ARMS.index(a),
            ),
        )
        if eligible
        else None
    )
    return {
        "selected_arm": selected,
        "eligibility": eligibility,
        "thresholds": {a: m["operating_point"]["cutoff"] for a, m in metrics.items()},
        "test_scores_used_for_selection": False,
    }


@train(config=AttentionFitConfig)
def fit_attention(context: StageContext[AttentionFitConfig]) -> None:
    """Train identical token attention heads, adding copied-span supervision in one arm."""
    config = context.config
    for name in (
        "training",
        "validation",
        "bank",
        "training_cache",
        "validation_cache",
    ):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed attention fitting input: {name}.")
    bank = load_json(context.inputs["bank"])
    training, validation = (
        load_json(context.inputs[n]) for n in ("training", "validation")
    )
    train_cache, val_cache = (
        load_model(context.inputs[n]) for n in ("training_cache", "validation_cache")
    )
    for rows, cache, digest, split in (
        (training, train_cache, config.training_sha256, "training"),
        (validation, val_cache, config.validation_sha256, "validation"),
    ):
        validate_token_cache(cache, rows)
        if (
            cache["rows_sha256"] != digest
            or cache["bank_sha256"] != config.bank_sha256
            or cache["model_sha256"] != config.model_sha256
            or cache["split"] != split
        ):
            raise ValueError(
                "Token-cache identity differs from the attention fit contract."
            )
    fitted = head_fit_rows(training, bank)
    fit_ids = {r["row_id"] for r in fitted}
    included = torch.tensor(
        [i for i, r in enumerate(training) if r["row_id"] in fit_ids]
    )
    fit_ids_sha = hashlib.sha256(
        json.dumps([r["row_id"] for r in fitted], separators=(",", ":")).encode()
    ).hexdigest()
    reset_rng(config.seed)
    head = AttentionHead(
        train_cache["embedding_dimension"],
        config.query_dim,
        config.output_dim,
        config.dropout,
    ).to(config.device)
    initial = state_digest(dict(head.state_dict()))
    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
        betas=(0.9, 0.999),
        eps=1e-8,
    )
    generator = torch.Generator().manual_seed(config.seed + 100)
    targets = torch.tensor([r["target"] for r in training], device=config.device)
    left, right = torch.tensor(train_cache["left"]), torch.tensor(train_cache["right"])
    stopping = ValidationPatience(config.patience)
    history, best_score, selected_epoch, updates = [], -math.inf, 0, 0
    started = time.monotonic()

    def checkpoint(epoch: int) -> dict[str, Any]:
        nonlocal best_score, selected_epoch
        predictions = scored_rows(
            validation, predict_head(head, val_cache, config.device)
        )
        measured = summarize(predictions)
        score = measured["spearman"]
        if score is None or not math.isfinite(score):
            raise ValueError("Attention validation Spearman is undefined.")
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
    stop_reason = "epoch_budget"
    for epoch in range(1, config.max_epochs + 1):
        if time.monotonic() - started >= config.max_seconds:
            stop_reason = "resource_budget"
            break
        head.train()
        order = included[torch.randperm(len(included), generator=generator)]
        squared_error, objective_total, span_total, span_count = 0.0, 0.0, 0.0, 0
        for start in range(0, len(order), config.batch_size):
            if time.monotonic() - started >= config.max_seconds:
                raise TimeoutError("Attention fitting budget ended within an epoch.")
            ix = order[start : start + config.batch_size]
            positions = torch.cat((left[ix], right[ix]))
            tokens, queries, mask, teacher = pack_batch(
                train_cache, positions, config.device
            )
            optimizer.zero_grad(set_to_none=True)
            vectors, logits, _ = head(tokens, queries, mask)
            a, b = vectors.chunk(2)
            mse = F.mse_loss((a * b).sum(1), targets[ix.to(config.device)])
            evidence, count = span_loss(logits, mask, teacher)
            objective = mse + (
                config.span_weight * evidence
                if config.arm == "attention_evidence"
                else 0
            )
            if not torch.isfinite(objective):
                raise ValueError("Attention objective is nonfinite.")
            objective.backward()
            nn.utils.clip_grad_norm_(head.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step()
            squared_error += float(mse.detach()) * len(ix)
            objective_total += float(objective.detach()) * len(ix)
            span_total += float(evidence.detach()) * count
            span_count += count
            updates += 1
        measured = checkpoint(epoch)
        context.metrics["training_objective"].record(
            objective_total / len(included), step=epoch
        )
        record = {
            "epoch": epoch,
            "training_mse": squared_error / len(included),
            "training_objective": objective_total / len(included),
            "span_cross_entropy": span_total / span_count if span_count else None,
            "supervised_occurrences": span_count,
            "validation": measured,
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
        emit("attention_head_epoch", arm=config.arm, **record)
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
    selected = load_model(context.outputs["model"])
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
            "selected": {"epoch": selected_epoch, "validation": selected["validation"]},
            "elapsed_seconds": time.monotonic() - started,
            "frozen_encoder_optimizer_updates": 0,
            "head_fit_rows": len(included),
            "bank_groups_excluded": bank["excluded_training_groups"],
            "effective_span_weight": config.span_weight
            if config.arm == "attention_evidence"
            else 0,
        },
    )
