"""Expert-supervised claim coding with matched centroid/multiple-prototype heads."""

import hashlib
import math
import time
from typing import Any

import torch
from pydantic import Field, model_validator
from torch import nn
from torch.nn import functional as F
from viper.config import MetricConfig, TrainConfig
from viper.metrics import MetricContext, metric
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, train

from csts_pilot.baseline_models import state_digest
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from csts_pilot.data import canonical
from csts_pilot.early_stopping import ValidationPatience
from jep_pilot.loaders import load_json, load_model

ARMS = ("centroid", "multiple_prototype")


class MultipleCodebookConfig(TrainConfig):
    """Freeze one development-only, CPU head-fitting screen."""

    seeds: tuple[int, ...] = (7, 8, 9)
    output_dim: int = Field(default=128, ge=2)
    prototypes_per_code: int = Field(default=2, ge=2)
    temperature: float = Field(default=0.2, gt=0, allow_inf_nan=False)
    logit_scale: float = Field(default=5.0, gt=0, allow_inf_nan=False)
    thresholds: tuple[float, ...] = (0.3, 0.5, 0.7)
    learning_rate: float = Field(default=0.001, gt=0, allow_inf_nan=False)
    weight_decay: float = Field(default=0.01, ge=0, allow_inf_nan=False)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    seconds_per_fit: float = Field(default=600, gt=0, allow_inf_nan=False)
    min_groups_per_condition: int = Field(default=10, ge=2)
    min_class_groups: int = Field(default=2, ge=2)
    annotations_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    training_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    validation_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    model_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def validate_choices(self) -> "MultipleCodebookConfig":
        """Reject ambiguous seed schedules or threshold searches."""
        if not self.seeds or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Seeds must be nonempty and unique.")
        if any(seed < 0 for seed in self.seeds):
            raise ValueError("Seeds must be nonnegative.")
        if not self.thresholds or len(set(self.thresholds)) != len(self.thresholds):
            raise ValueError("Thresholds must be nonempty and unique.")
        if any(not math.isfinite(t) or not 0 < t < 1 for t in self.thresholds):
            raise ValueError(
                "Thresholds must be finite and strictly between zero and one."
            )
        return self


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a nonempty trimmed string.")
    return value


def prepare_data(
    annotations: dict[str, Any], caches: dict[str, Any], config: MultipleCodebookConfig
) -> dict[str, Any]:
    """Validate actual supplied annotations, support, feature provenance and isolation."""
    required = {
        "schema_version",
        "expert_reviewed",
        "annotation_protocol",
        "codebook_version",
        "reviewer_ids",
        "codes",
        "training",
        "validation",
    }
    if set(annotations) != required or annotations["schema_version"] != 1:
        raise ValueError("Require the exact version-1 expert annotation schema.")
    if annotations["expert_reviewed"] is not True:
        raise ValueError("Expert-reviewed labels must be supplied before fitting.")
    for name in ("annotation_protocol", "codebook_version"):
        _text(annotations[name], name)
    reviewers = annotations["reviewer_ids"]
    if not isinstance(reviewers, list) or not reviewers:
        raise ValueError("Require opaque reviewer IDs for annotation provenance.")
    if len({_text(value, "reviewer_id") for value in reviewers}) != len(reviewers):
        raise ValueError("Reviewer IDs must be unique.")
    codes = annotations["codes"]
    if not isinstance(codes, list) or not codes:
        raise ValueError("Require fixed expert code definitions.")
    for code in codes:
        if not isinstance(code, dict) or set(code) != {"id", "condition", "definition"}:
            raise ValueError("Each expert code needs id, condition and definition.")
        for name in code:
            _text(code[name], "code " + name)
    ids = [code["id"] for code in codes]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate expert code IDs.")
    conditions = {code["condition"] for code in codes}
    if len({canonical(c) for c in conditions}) != len(conditions):
        raise ValueError("Condition names must not be canonical aliases.")
    code_index = {name: i for i, name in enumerate(ids)}
    result: dict[str, Any] = {"codes": codes, "splits": {}}
    previous: dict[str, set[str]] = {}
    width = None
    for split in ("training", "validation"):
        rows = annotations[split]
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"Empty {split} claim annotations.")
        identities: set[str] = set()
        keys: list[tuple[str, str]] = []
        groups: set[str] = set()
        passages: dict[str, str] = {}
        labels = torch.zeros(len(rows), len(codes))
        mask = torch.zeros_like(labels, dtype=torch.bool)
        applicability = torch.zeros_like(mask)
        for i, row in enumerate(rows):
            fields = {
                "claim_id",
                "passage_id",
                "source_group",
                "condition",
                "text",
                "labels",
            }
            if not isinstance(row, dict) or set(row) != fields:
                raise ValueError(
                    "Each claim needs exact identity, provenance, text and labels."
                )
            for name in fields - {"labels"}:
                _text(row[name], name)
            if row["claim_id"] in identities:
                raise ValueError("Duplicate claim IDs.")
            identities.add(row["claim_id"])
            if row["condition"] not in conditions:
                raise ValueError("Unseen condition without expert code definitions.")
            keys.append((row["condition"], row["text"]))
            groups.add(row["source_group"])
            old_group = passages.setdefault(row["passage_id"], row["source_group"])
            if old_group != row["source_group"]:
                raise ValueError("A passage cannot belong to multiple source groups.")
            applicability[i] = torch.tensor(
                [code["condition"] == row["condition"] for code in codes]
            )
            if not isinstance(row["labels"], dict):
                raise TypeError("Labels must map expert code IDs to 0, 1 or null.")
            for name, value in row["labels"].items():
                if name not in code_index:
                    raise ValueError(f"Unseen expert code label: {name}.")
                j = code_index[name]
                if not applicability[i, j]:
                    raise ValueError("Code labels cannot cross conditions.")
                if value is not None:
                    if type(value) is not int or value not in (0, 1):
                        raise ValueError("Expert labels must be integer 0/1 or null.")
                    labels[i, j], mask[i, j] = value, True
            if not mask[i].any():
                raise ValueError("Each included claim needs an observed expert label.")
        texts = {canonical(row["text"]) for row in rows}
        if len({(condition, canonical(text)) for condition, text in keys}) != len(keys):
            raise ValueError(
                "Duplicate condition/claim inputs would overweight one claim."
            )
        if split == "validation" and (
            groups & previous["groups"]
            or texts & previous["texts"]
            or identities & previous["identities"]
            or set(passages) & previous["passages"]
        ):
            raise ValueError(
                "Training/validation groups, passages, claim IDs and texts must be disjoint."
            )
        previous = {
            "groups": groups,
            "texts": texts,
            "identities": identities,
            "passages": set(passages),
        }
        cache = caches[split]
        if not isinstance(cache, dict) or set(cache) != {
            "keys",
            "vectors",
            "provenance",
        }:
            raise ValueError("Require a compact frozen claim-feature cache.")
        if cache["provenance"].get("model_sha256") != config.model_sha256:
            raise ValueError(
                "Frozen feature model digest differs from the pinned model."
            )
        raw_keys = cache["keys"]
        if not isinstance(raw_keys, list) or any(
            not isinstance(key, (list, tuple)) or len(key) != 2 for key in raw_keys
        ):
            raise ValueError("Feature keys must be condition/text pairs.")
        feature_keys = [tuple(key) for key in raw_keys]
        if len(set(feature_keys)) != len(feature_keys) or set(feature_keys) != set(
            keys
        ):
            raise ValueError(
                "Feature keys must cover exactly the unique annotated claims."
            )
        vectors = cache["vectors"]
        if not isinstance(vectors, torch.Tensor) or vectors.dtype != torch.float32:
            raise ValueError("Frozen vectors must be FP32 tensors.")
        if (
            vectors.device.type != "cpu"
            or vectors.ndim != 2
            or vectors.shape[0] != len(keys)
        ):
            raise ValueError(
                "Frozen vectors must be a CPU matrix aligned to feature keys."
            )
        if vectors.shape[1] < 2 or (width is not None and vectors.shape[1] != width):
            raise ValueError("Frozen feature widths must agree and be at least two.")
        width = vectors.shape[1]
        if not torch.isfinite(vectors).all() or not torch.allclose(
            vectors.norm(dim=1), torch.ones(len(keys)), atol=1e-5, rtol=1e-5
        ):
            raise ValueError("Frozen claim features must be finite unit vectors.")
        positions = {key: i for i, key in enumerate(feature_keys)}
        data = {
            "rows": rows,
            "vectors": vectors[[positions[key] for key in keys]],
            "labels": labels,
            "mask": mask,
            "applicability": applicability,
        }
        support: dict[str, Any] = {}
        unsupported = []
        for condition in sorted(conditions):
            n = len(
                {row["source_group"] for row in rows if row["condition"] == condition}
            )
            if n < config.min_groups_per_condition:
                unsupported.append(f"{condition}: {n} independent {split} groups")
        for j, name in enumerate(ids):
            counts = [
                len(
                    {
                        row["source_group"]
                        for i, row in enumerate(rows)
                        if mask[i, j] and labels[i, j] == value
                    }
                )
                for value in (0, 1)
            ]
            positive_rows = int((mask[:, j] & (labels[:, j] == 1)).sum())
            support[name] = {
                "negative_groups": counts[0],
                "positive_groups": counts[1],
                "observed_claims": int(mask[:, j].sum()),
            }
            if min(counts) < config.min_class_groups or (
                split == "training" and positive_rows < config.prototypes_per_code
            ):
                unsupported.append(
                    f"{name}: negative/positive groups={counts}, positive claims={positive_rows}"
                )
        if unsupported:
            raise ValueError(
                f"Unsupported {split} labels/conditions: " + "; ".join(unsupported)
            )
        data["support"] = support
        result["splits"][split] = data
    return result


class MultiplePrototypeHead(nn.Module):
    """Shared parameterization; only prototype pooling differs between arms."""

    def __init__(self, width: int, codes: int, config: MultipleCodebookConfig):
        super().__init__()
        self.projection = nn.Linear(width, config.output_dim, bias=False)
        self.prototypes = nn.Parameter(
            torch.empty(codes, config.prototypes_per_code, config.output_dim)
        )
        self.bias = nn.Parameter(torch.zeros(codes))
        self.temperature = config.temperature
        self.scale = config.logit_scale

    def forward(self, vectors: torch.Tensor, arm: str) -> torch.Tensor:
        """Return independent code logits, allowing zero or multiple assignments."""
        z = F.normalize(self.projection(vectors), dim=1)
        similarities = torch.einsum(
            "nd,kmd->nkm", z, F.normalize(self.prototypes, dim=2)
        )
        if arm == "centroid":
            pooled = similarities.mean(dim=2)
        elif arm == "multiple_prototype":
            pooled = self.temperature * (
                torch.logsumexp(similarities / self.temperature, dim=2)
                - math.log(similarities.shape[2])
            )
        else:
            raise ValueError(f"Unknown prototype pooling arm: {arm}.")
        return self.scale * pooled + self.bias


def initialize(
    training: dict[str, Any], config: MultipleCodebookConfig, seed: int
) -> MultiplePrototypeHead:
    """Initialize every code from its training-only expert-positive claim features."""
    reset_rng(seed)
    model = MultiplePrototypeHead(
        training["vectors"].shape[1], training["labels"].shape[1], config
    )
    generator = torch.Generator().manual_seed(seed + 1)
    with torch.no_grad():
        z = F.normalize(model.projection(training["vectors"]), dim=1)
        for j in range(len(model.prototypes)):
            positions = torch.where(
                training["mask"][:, j] & (training["labels"][:, j] == 1)
            )[0]
            chosen = positions[
                torch.randperm(len(positions), generator=generator)[
                    : config.prototypes_per_code
                ]
            ]
            model.prototypes[j].copy_(z[chosen])
    return model


def masked_loss(
    logits: torch.Tensor, labels: torch.Tensor, mask: torch.Tensor
) -> torch.Tensor:
    """Weight each claim equally; unobserved and inapplicable labels have no gradient."""
    losses = F.binary_cross_entropy_with_logits(logits, labels, reduction="none")
    return ((losses * mask).sum(1) / mask.sum(1).clamp_min(1)).mean()


def classification_metrics(
    predicted: torch.Tensor, labels: torch.Tensor, mask: torch.Tensor
) -> dict[str, Any]:
    """Report coding agreement only on expert-observed entries, including rare codes."""
    per_code = []
    for j in range(labels.shape[1]):
        known = mask[:, j]
        gold, pred = labels[:, j].bool() & known, predicted[:, j] & known
        tp, fp, fn = (
            int((pred & gold).sum()),
            int((pred & ~gold).sum()),
            int((~pred & gold).sum()),
        )
        denom = 2 * tp + fp + fn
        per_code.append(
            {
                "observed": int(known.sum()),
                "positives": int(gold.sum()),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "f1": 2 * tp / denom if denom else 0.0,
            }
        )
    covered = [code for code in per_code if code["observed"]]
    tp, fp, fn = (sum(code[name] for code in covered) for name in ("tp", "fp", "fn"))
    denom = 2 * tp + fp + fn
    return {
        "macro_f1": sum(code["f1"] for code in covered) / len(covered)
        if covered
        else None,
        "micro_f1": 2 * tp / denom if denom else 0.0,
        "per_code": per_code,
        "observed_entries": int(mask.sum()),
    }


def passage_or(
    data: dict[str, Any], probabilities: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """OR claim predictions; gold negatives require all passage claims to be known zero."""
    members: dict[tuple[str, str], list[int]] = {}
    for i, row in enumerate(data["rows"]):
        members.setdefault((row["passage_id"], row["condition"]), []).append(i)
    predicted, labels, masks = [], [], []
    for indices in members.values():
        known, gold = data["mask"][indices], data["labels"][indices]
        positive = (known & gold.bool()).any(0)
        negative = (known & ~gold.bool()).all(0)
        predicted.append(probabilities[indices].amax(0))
        labels.append(positive.float())
        masks.append(positive | negative)
    return torch.stack(predicted), torch.stack(labels), torch.stack(masks)


def evaluate(
    data: dict[str, Any], probabilities: torch.Tensor, threshold: float
) -> dict[str, Any]:
    """Measure claim and passage coding; preserve condition-specific observation coverage."""
    report = classification_metrics(
        probabilities >= threshold, data["labels"], data["mask"]
    )
    p, y, m = passage_or(data, probabilities)
    report["passage_or"] = classification_metrics(p >= threshold, y, m)
    report["passage_or_scope"] = "supplied_claims_only"
    report["observation_coverage"] = float(
        data["mask"].sum() / data["applicability"].sum()
    )
    report["per_condition"] = {}
    for condition in sorted({row["condition"] for row in data["rows"]}):
        indices = [
            i for i, row in enumerate(data["rows"]) if row["condition"] == condition
        ]
        report["per_condition"][condition] = classification_metrics(
            probabilities[indices] >= threshold,
            data["labels"][indices],
            data["mask"][indices],
        )
    return report


@torch.no_grad()
def predict(
    model: MultiplePrototypeHead, data: dict[str, Any], arm: str
) -> torch.Tensor:
    """Use a fixed CPU scoring layout for selection and independent artifact replay."""
    model.eval()
    return torch.cat(
        [model(batch, arm).sigmoid() for batch in data["vectors"].split(512)]
    )


def fit_one(
    training: dict[str, Any],
    validation: dict[str, Any],
    config: MultipleCodebookConfig,
    seed: int,
    arm: str,
    observer: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Select checkpoint and one global threshold using development labels only."""
    model = initialize(training, config, seed)
    initial = state_digest(model.state_dict())
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    generator = torch.Generator().manual_seed(seed + 100)
    stopping = ValidationPatience(config.patience)
    selected: dict[str, Any] = {}
    history = []
    started, updates = time.monotonic(), 0

    def checkpoint(epoch: int) -> dict[str, Any]:
        probabilities = predict(model, validation, arm)
        choices = [
            (evaluate(validation, probabilities, threshold), threshold)
            for threshold in config.thresholds
        ]
        measured, threshold = max(
            choices,
            key=lambda item: (item[0]["macro_f1"], item[0]["micro_f1"], item[1]),
        )
        if not selected or measured["macro_f1"] > selected["validation"]["macro_f1"]:
            selected.update(
                state={
                    name: value.detach().clone()
                    for name, value in model.state_dict().items()
                },
                epoch=epoch,
                threshold=threshold,
                validation=measured,
                seed=seed,
                arm=arm,
                initial_state_sha256=initial,
                parameter_count=sum(p.numel() for p in model.parameters()),
            )
        return measured

    initial_metrics = checkpoint(0)
    stopping.observe(initial_metrics["macro_f1"])
    reason = "epoch_budget"
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        order = torch.randperm(len(training["rows"]), generator=generator)
        total = 0.0
        for batch in order.split(config.batch_size):
            if time.monotonic() - started > config.seconds_per_fit:
                raise TimeoutError(
                    "Fit budget ended; preserve the failed native attempt."
                )
            optimizer.zero_grad(set_to_none=True)
            loss = masked_loss(
                model(training["vectors"][batch], arm),
                training["labels"][batch],
                training["mask"][batch],
            )
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite expert coding objective.")
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step()
            total += float(loss.detach()) * len(batch)
            updates += 1
        measured = checkpoint(epoch)
        if time.monotonic() - started > config.seconds_per_fit:
            raise TimeoutError(
                "Validation exceeded the fit budget; preserve the failed attempt."
            )
        record = {
            "epoch": epoch,
            "training_objective": total / len(order),
            "validation": measured,
            "batch_order_sha256": hashlib.sha256(order.numpy().tobytes()).hexdigest(),
        }
        history.append(record)
        observer(seed, arm, record)
        if stopping.observe(measured["macro_f1"]):
            reason = "validation_patience"
            break
    terminal = {
        "state": {
            name: value.detach().clone() for name, value in model.state_dict().items()
        },
        "torch_rng": torch.get_rng_state(),
        "optimizer": optimizer.state_dict(),
        "generator": generator.get_state(),
        "updates": updates,
    }
    model.load_state_dict(selected["state"])
    selected["validation_probabilities"] = predict(model, validation, arm)
    if time.monotonic() - started > config.seconds_per_fit:
        raise TimeoutError("Selected prediction replay exceeded the fit budget.")
    trace = {
        "epochs": history,
        "stop_reason": reason,
        "selected_epoch": selected["epoch"],
        "initial_state_sha256": initial,
        "elapsed_seconds": time.monotonic() - started,
    }
    return selected, trace, terminal


@metric(metric_id="validation_macro_f1", mode="stateless")
def validation_macro_f1(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record expert-observed claim coding agreement used for checkpoint selection."""
    return value


@train(config=MultipleCodebookConfig)
def fit_multiple_codebooks(context: StageContext[MultipleCodebookConfig]) -> None:
    """Fit both paired heads only after immutable inputs pass expert-data preflight."""
    torch.set_num_threads(1)
    config = context.config
    for name in ("annotations", "training", "validation"):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed expert experiment input: {name}.")
    annotations = load_json(context.inputs["annotations"])
    prepared = prepare_data(
        annotations,
        {name: load_model(context.inputs[name]) for name in ("training", "validation")},
        config,
    )
    training, validation = (
        prepared["splits"][name] for name in ("training", "validation")
    )
    models, traces, terminal = {}, {}, {}
    run_index = 0

    def observe(seed: int, arm: str, record: dict[str, Any]) -> None:
        step = run_index * (config.max_epochs + 1) + record["epoch"]
        context.metrics["training_objective"].record(
            record["training_objective"], step=step
        )
        context.metrics["validation_macro_f1"].record(
            record["validation"]["macro_f1"], step=step
        )
        write_json(
            context.outputs["trace"],
            {
                "status": "running",
                "completed": traces,
                "current": {"seed": seed, "arm": arm, **record},
            },
        )

    for seed in config.seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            models[key], traces[key], terminal[key] = fit_one(
                training, validation, config, seed, arm, observe
            )
            run_index += 1
        a, b = (traces[f"{seed}:{arm}"] for arm in ARMS)
        if a["initial_state_sha256"] != b["initial_state_sha256"] or any(
            x["batch_order_sha256"] != y["batch_order_sha256"]
            for x, y in zip(a["epochs"], b["epochs"])
        ):
            raise ValueError("Paired initialization or shared-epoch orders differ.")
    torch.save(
        {
            "config": config.model_dump(mode="json"),
            "codes": prepared["codes"],
            "models": models,
            "validation_claim_ids": [row["claim_id"] for row in validation["rows"]],
        },
        context.outputs["model"],
    )
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "fits": traces,
            "support": {
                name: prepared["splits"][name]["support"]
                for name in ("training", "validation")
            },
            "test_accessed": False,
            "backbone_updates": 0,
        },
    )
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={"terminal_runs": terminal},
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={"completed_runs": list(models)},
            ),
        ),
    )
