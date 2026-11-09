"""Encode conditioned passages and fit scorers over one frozen representation."""

import hashlib
import math
from collections.abc import Sequence
from typing import Any, Literal

import numpy as np
import torch
from peft import LoraConfig, TaskType, get_peft_model
from pydantic import ConfigDict, Field, model_validator
from scipy.linalg import eigh
from torch import nn
from torch.nn import functional as F
from transformers import AutoModel, AutoTokenizer
from viper.config import BuildConfig, EvalConfig, TrainConfig

PROMPT = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
EOD = "<|endoftext|>"


class EncoderConfig(BuildConfig):
    """Pin the representation shared by every Tranche 2 scorer."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    model_id: str = Field(
        default="Qwen/Qwen3-Embedding-8B",
        description="Public pretrained embedding model repository.",
    )
    revision: str = Field(
        default="c90816d848505624c2434128dfc61132162a0ee9",
        pattern=r"^[0-9a-f]{40}$",
        description="Immutable model and tokenizer repository commit.",
    )
    max_length: int = Field(
        default=160,
        ge=8,
        description="Maximum tokens including the explicit end-of-document token; longer inputs fail.",
    )
    embedding_dimension: int = Field(
        default=4096, ge=1, description="Expected full backbone output width."
    )
    encode_batch_size: int = Field(
        default=4,
        ge=1,
        description="Conditioned passages encoded in one inference call.",
    )
    device: Literal["cpu", "cuda"] = Field(
        default="cuda",
        description="Device used for backbone inference or adapter training.",
    )


class FitConfig(EncoderConfig, TrainConfig):
    """Declare one scorer's fitting procedure and epoch-boundary continuation."""

    kind: Literal["mean", "cosine", "ridge", "projection", "lora"] = Field(
        description="Scorer fitted by this native training stage."
    )
    seed: int = Field(
        default=7, ge=0, description="Initialization and training permutation seed."
    )
    projection_dimension: int = Field(
        default=128,
        ge=1,
        description="Width of the bias-free learned passage projection.",
    )
    ridge_alphas: tuple[float, ...] = Field(
        default=(1e-5, 1e-4, 1e-3, 1e-2, 0.1, 1.0),
        description="Positive penalties for mean squared error plus alpha times squared coefficients.",
    )
    learning_rate: float = Field(
        default=1e-3,
        gt=0,
        allow_inf_nan=False,
        description="AdamW rate for the projection or LoRA parameters.",
    )
    batch_size: int = Field(
        default=32,
        ge=1,
        description="Comparisons contributing to each optimizer update.",
    )
    microbatch_size: int = Field(
        default=32,
        ge=1,
        description="Comparisons processed before each gradient accumulation step.",
    )
    max_epochs: int = Field(
        default=48,
        ge=1,
        description="Total epoch ceiling including a declared parent phase.",
    )
    start_epoch: int = Field(
        default=0,
        ge=0,
        description="Completed parent epochs restored before this phase.",
    )
    patience: int = Field(
        default=5,
        ge=1,
        description="Successive validation checks without a strict Spearman improvement before stopping.",
    )
    weight_decay: float = Field(
        default=0.01,
        ge=0,
        allow_inf_nan=False,
        description="AdamW decoupled weight decay.",
    )
    schedule: Literal["constant", "linear"] = Field(
        default="constant",
        description="Predeclared learning-rate schedule for this phase.",
    )
    warmup_fraction: float = Field(
        default=0.0,
        ge=0,
        lt=1,
        description="Fraction of declared updates reserved for a fresh linear warmup.",
    )
    max_seconds: float = Field(
        default=1800,
        gt=0,
        allow_inf_nan=False,
        description="Wall-time allowance for fitting and validation inside this stage.",
    )
    lora_rank: int = Field(
        default=32, ge=1, description="Rank of each attention-projection adapter."
    )
    lora_alpha: int = Field(default=32, ge=1, description="LoRA scaling numerator.")
    lora_dropout: float = Field(
        default=0.05,
        ge=0,
        lt=1,
        description="Dropout within the LoRA branch during training.",
    )

    @model_validator(mode="after")
    def validate_fit(self) -> "FitConfig":
        """Reject ambiguous penalty grids and unsupported continuation schedules."""
        if not self.ridge_alphas or len(set(self.ridge_alphas)) != len(
            self.ridge_alphas
        ):
            raise ValueError("Ridge penalties must be a nonempty unique sequence.")
        if any(not math.isfinite(a) or a <= 0 for a in self.ridge_alphas):
            raise ValueError("Ridge penalties must be finite and positive.")
        if self.start_epoch >= self.max_epochs:
            raise ValueError("The epoch ceiling must exceed the restored epoch.")
        if self.start_epoch and (
            self.kind not in {"projection", "lora"}
            or self.schedule != "constant"
            or self.warmup_fraction != 0
        ):
            raise ValueError(
                "Continuation requires a neural scorer, constant rates and zero new warmup."
            )
        if self.schedule == "constant" and self.warmup_fraction:
            raise ValueError("Constant-rate training requires zero warmup.")
        return self


class ScoreConfig(EncoderConfig, EvalConfig):
    """Bind test scoring to a frozen model, selection document and input cohort."""

    kind: Literal["mean", "cosine", "ridge", "projection", "lora"] = Field(
        description="Frozen scorer evaluated by this stage."
    )
    model_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$", description="Exact selected model artifact digest."
    )
    selection_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
        description="Selection document frozen before test access.",
    )
    test_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$", description="Exact prepared test JSON digest."
    )


def encoder_settings(config: EncoderConfig) -> dict[str, Any]:
    """Describe the semantic representation independently of runtime batch size."""
    return {
        "model_id": config.model_id,
        "revision": config.revision,
        "max_length": config.max_length,
        "embedding_dimension": config.embedding_dimension,
        "prompt": PROMPT,
        "pooling": "last_nonpadding_eod_float32_unit_norm",
    }


def validate_rows(rows: list[dict[str, Any]]) -> None:
    """Require unique comparison IDs, finite ratings and complete passage identities."""
    if not rows or len({r["row_id"] for r in rows}) != len(rows):
        raise ValueError("Comparisons require nonempty unique row IDs.")
    for row in rows:
        if any(
            not isinstance(row[key], str) or not row[key].strip()
            for key in (
                "row_id",
                "group_id",
                "pair_id",
                "condition",
                "sentence1",
                "sentence2",
            )
        ):
            raise ValueError(
                "Comparison identity and text fields must be nonempty strings."
            )
        target, rating = float(row["target"]), float(row["rating"])
        if (
            not math.isfinite(target)
            or not 0 <= target <= 1
            or abs(target - (rating - 1) / 4) > 1e-12
        ):
            raise ValueError(
                "Ratings must agree with targets rescaled through (rating - 1) / 4."
            )


def passage_keys(rows: Sequence[dict[str, Any]]) -> list[tuple[str, str]]:
    """Sort unique condition and passage identities for deterministic inference batches."""
    return sorted(
        {
            (row["condition"], row[side])
            for row in rows
            for side in ("sentence1", "sentence2")
        }
    )


def token_sequences(
    tokenizer: Any, keys: Sequence[tuple[str, str]], config: EncoderConfig
) -> list[list[int]]:
    """Tokenize unique passages once, append EOD and check every token ceiling."""
    texts = [
        PROMPT.format(condition=condition, passage=passage)
        for condition, passage in keys
    ]
    encoded = tokenizer(
        texts, padding=False, truncation=False, add_special_tokens=False
    )
    eod = tokenizer.get_vocab().get(EOD)
    if eod is None:
        raise ValueError("The pinned tokenizer lacks the required EOD token.")
    sequences = []
    for ids in encoded["input_ids"]:
        if len(ids) + 1 > config.max_length:
            raise ValueError(
                "A conditioned passage exceeds the token ceiling; review the ceiling before execution."
            )
        sequences.append([*ids, eod])
    return sequences


def pad_sequences(
    tokenizer: Any, sequences: list[list[int]], config: EncoderConfig
) -> dict[str, torch.Tensor]:
    """Pad a selected set of prevalidated token sequences on the target device."""
    masks = [[1] * len(ids) for ids in sequences]
    padded = tokenizer.pad(
        {"input_ids": sequences, "attention_mask": masks},
        padding=True,
        return_tensors="pt",
    )
    return {
        key: value.to(config.device)
        for key, value in padded.items()
        if key in {"input_ids", "attention_mask"}
    }


def token_batch(
    tokenizer: Any, keys: Sequence[tuple[str, str]], config: EncoderConfig
) -> dict[str, torch.Tensor]:
    """Prepare one token batch from raw conditioned passages."""
    return pad_sequences(tokenizer, token_sequences(tokenizer, keys, config), config)


def last_token_pool(hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Pool the final attended token for either left or right padding."""
    if (
        hidden.shape[:2] != attention_mask.shape
        or not attention_mask.bool().any(1).all()
    ):
        raise ValueError(
            "Pooling requires matching shapes and an attended token in each sequence."
        )
    positions = torch.arange(hidden.shape[1], device=hidden.device).expand_as(
        attention_mask
    )
    last = positions.masked_fill(~attention_mask.bool(), -1).max(1).values
    with torch.autocast(hidden.device.type, enabled=False):
        pooled = hidden[torch.arange(len(hidden), device=hidden.device), last].float()
        if not torch.isfinite(pooled).all() or (pooled.norm(dim=-1) == 0).any():
            raise ValueError("Embeddings must have finite nonzero norms.")
        return F.normalize(pooled, dim=-1)


def load_backbone(
    config: EncoderConfig, adapters: FitConfig | None = None
) -> nn.Module:
    """Load the pinned backbone, optionally attaching attention-only LoRA adapters."""
    model = AutoModel.from_pretrained(
        config.model_id,
        revision=config.revision,
        dtype=torch.bfloat16 if config.device == "cuda" else torch.float32,
        attn_implementation="sdpa",
        device_map={"": config.device},
        trust_remote_code=False,
    )
    model.config.use_cache = False
    if model.config.hidden_size != config.embedding_dimension:
        raise ValueError(
            "The pinned backbone width differs from the frozen configuration."
        )
    if adapters is not None:
        model = get_peft_model(
            model,
            LoraConfig(
                task_type=TaskType.FEATURE_EXTRACTION,
                r=adapters.lora_rank,
                lora_alpha=adapters.lora_alpha,
                lora_dropout=adapters.lora_dropout,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                bias="none",
            ),
        )
        model.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )
        model.enable_input_require_grads()
    return model.to(config.device)


def load_tokenizer(config: EncoderConfig) -> Any:
    """Use the tokenizer from the same immutable revision as the model."""
    return AutoTokenizer.from_pretrained(
        config.model_id,
        revision=config.revision,
        padding_side="left",
        trust_remote_code=False,
    )


def encode(model: nn.Module, batch: dict[str, torch.Tensor]) -> torch.Tensor:
    """Run eligible backbone operations in BF16 and pool in float32."""
    device = batch["input_ids"].device.type
    with torch.autocast(
        device, enabled=device == "cuda", dtype=torch.bfloat16, cache_enabled=False
    ):
        hidden = model(**batch).last_hidden_state
    return last_token_pool(hidden, batch["attention_mask"])


def validate_cache(cache: dict[str, Any], config: EncoderConfig) -> None:
    """Check the cached representation, key uniqueness and unit-vector bytes."""
    vectors = cache["vectors"]
    keys = [tuple(key) for key in cache["keys"]]
    if cache["encoder"] != encoder_settings(config) or len(set(keys)) != len(keys):
        raise ValueError("Cached encoder settings or passage identities differ.")
    if (
        vectors.shape != (len(keys), config.embedding_dimension)
        or vectors.dtype != torch.float32
    ):
        raise ValueError("Cached embedding shape or dtype differs.")
    if not torch.isfinite(vectors).all() or not torch.allclose(
        vectors.norm(dim=1), torch.ones(len(keys)), atol=2e-5, rtol=0
    ):
        raise ValueError("Cached embeddings must be finite float32 unit vectors.")


class FrozenPairs:
    """Index both conditioned passage vectors for each immutable comparison."""

    def __init__(
        self, rows: list[dict[str, Any]], cache: dict[str, Any], config: EncoderConfig
    ) -> None:
        """Resolve passage identities after checking the cache representation."""
        validate_rows(rows)
        validate_cache(cache, config)
        lookup = {tuple(key): i for i, key in enumerate(cache["keys"])}
        self.rows = rows
        self.nonpadding_tokens = 0
        self.left = cache["vectors"][
            [lookup[(r["condition"], r["sentence1"])] for r in rows]
        ].to(config.device)
        self.right = cache["vectors"][
            [lookup[(r["condition"], r["sentence2"])] for r in rows]
        ].to(config.device)

    def scores(self, model: nn.Module, indices: torch.Tensor) -> torch.Tensor:
        """Project and normalize passages independently before taking their cosine."""
        with torch.autocast(
            self.left.device.type,
            enabled=self.left.is_cuda,
            dtype=torch.bfloat16,
            cache_enabled=False,
        ):
            left, right = model(self.left[indices]), model(self.right[indices])
        with torch.autocast(self.left.device.type, enabled=False):
            return (
                F.normalize(left.float(), dim=-1) * F.normalize(right.float(), dim=-1)
            ).sum(-1)


class TokenPairs:
    """Tokenize both sides together for adapter training and test prediction."""

    def __init__(
        self, rows: list[dict[str, Any]], config: EncoderConfig, tokenizer: Any
    ) -> None:
        """Cache CPU token sequences once and retain exact comparison identities."""
        validate_rows(rows)
        self.rows, self.config, self.tokenizer = rows, config, tokenizer
        self.nonpadding_tokens = 0

        keys = passage_keys(rows)
        self.sequences = dict(
            zip(keys, token_sequences(tokenizer, keys, config), strict=True)
        )

    def scores(self, model: nn.Module, indices: torch.Tensor) -> torch.Tensor:
        """Encode each passage under its own comparison condition and take cosine."""
        selected = [self.rows[i] for i in indices.cpu().tolist()]
        keys = [
            (row["condition"], row[side])
            for side in ("sentence1", "sentence2")
            for row in selected
        ]
        batch = pad_sequences(
            self.tokenizer, [self.sequences[key] for key in keys], self.config
        )
        self.nonpadding_tokens += int(batch["attention_mask"].sum())
        embeddings = encode(model, batch)
        left, right = embeddings.chunk(2)
        with torch.autocast(embeddings.device.type, enabled=False):
            return (left.float() * right.float()).sum(-1)


def pair_features(left: torch.Tensor, right: torch.Tensor) -> np.ndarray:
    """Construct symmetric absolute-difference and product features for ridge."""
    a, b = left.cpu().numpy().astype(np.float64), right.cpu().numpy().astype(np.float64)
    return np.concatenate((np.abs(a - b), a * b), axis=1)


def ridge_candidates(
    features: np.ndarray, targets: np.ndarray, alphas: Sequence[float]
) -> list[dict[str, Any]]:
    """Share one eigendecomposition across training-only standardized ridge fits."""
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(targets, dtype=np.float64)
    if (
        x.ndim != 2
        or y.shape != (len(x),)
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
    ):
        raise ValueError("Ridge requires aligned finite features and targets.")
    mean, scale, intercept = x.mean(0), x.std(0), float(y.mean())
    scale[scale < 1e-12] = 1.0
    standardized, centered = (x - mean) / scale, y - intercept
    dual = len(x) < x.shape[1]
    gram = standardized @ standardized.T if dual else standardized.T @ standardized
    eigenvalues, basis = eigh(gram / len(x), check_finite=False)
    eigenvalues = eigenvalues.clip(min=0)
    response = centered if dual else standardized.T @ centered / len(x)
    projected = basis.T @ response
    candidates = []
    for alpha in alphas:
        if not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("Ridge requires finite positive penalties.")
        coefficients = basis @ (projected / (eigenvalues + alpha))
        if dual:
            coefficients = standardized.T @ coefficients / len(x)
        candidates.append(
            {
                "alpha": float(alpha),
                "mean": torch.from_numpy(mean.copy()),
                "scale": torch.from_numpy(scale.copy()),
                "coefficients": torch.from_numpy(coefficients),
                "intercept": intercept,
            }
        )
    return candidates


def ridge_predict(model: dict[str, Any], features: np.ndarray) -> np.ndarray:
    """Apply training-fitted standardization, coefficients and unpenalized intercept."""
    return ((features - model["mean"].numpy()) / model["scale"].numpy()) @ model[
        "coefficients"
    ].numpy() + model["intercept"]


def trainable_state(model: nn.Module) -> dict[str, torch.Tensor]:
    """Copy only trainable parameters so adapter artifacts exclude base weights."""
    return {
        name: p.detach().cpu().clone()
        for name, p in model.named_parameters()
        if p.requires_grad
    }


def restore_parameters(model: nn.Module, saved: dict[str, torch.Tensor]) -> None:
    """Restore every trainable parameter while rejecting missing or extra names."""
    parameters = {name: p for name, p in model.named_parameters() if p.requires_grad}
    if parameters.keys() != saved.keys():
        raise ValueError("Checkpoint trainable parameter names differ.")
    with torch.no_grad():
        for name, parameter in parameters.items():
            if parameter.shape != saved[name].shape:
                raise ValueError("Checkpoint trainable parameter shapes differ.")
            parameter.copy_(
                saved[name].to(device=parameter.device, dtype=parameter.dtype)
            )


def state_digest(state: dict[str, torch.Tensor]) -> str:
    """Hash tensor names, shapes, dtypes and exact bytes in deterministic order."""
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(repr((name, tuple(value.shape), str(value.dtype))).encode())
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()
