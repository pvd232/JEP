"""Extract and evaluate the six frozen Tranche 4 representations."""

import json
import math
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from pydantic import Field
from scipy.linalg import eigvalsh
from scipy.stats import spearmanr
from viper.config import EvalConfig, MetricConfig
from viper.metrics import MetricContext
from viper.metrics import metric as viper_metric
from viper.stages import StageContext, build, eval

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
    token_sequences,
    trainable_state,
    validate_rows,
)
from csts_pilot.convergence import file_sha256, synchronize, write_json
from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_json, load_model

ARMS = ("A", "B_u", "B_r", "C_u", "C_r", "D")
MODEL_SHA256 = "8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff"
MIN_NORM = 1e-8


@viper_metric(metric_id="condition_reference_native_spearman", mode="stateless")
def native_spearman(context: MetricContext[MetricConfig]) -> float:
    """Recompute the native arm's ranking in a separate metric worker."""
    rows = load_json(context.artifacts["predictions"])["A"]
    value = summarize(rows)["spearman"]
    if value is None or not math.isfinite(value):
        raise ValueError("Native Spearman is undefined.")
    return float(value)


def emit(event: str, **values: Any) -> None:
    """Flush each result immediately to the native worker log."""
    message = json.dumps({"event": event, **values}, allow_nan=False)
    print(message, flush=True)
    if destination := os.environ.get("CSTS_TRANCHE4_EVENTS"):
        with Path(destination).open("a") as stream:
            stream.write(message + "\n")
            stream.flush()


class ExtractionConfig(EncoderConfig):
    """Bind one zero-update extraction to its exact checkpoint and cohort."""

    model_sha256: str = Field(default=MODEL_SHA256, pattern=r"^[0-9a-f]{64}$")
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split: str
    arms: tuple[str, ...] = ARMS
    max_seconds: float = 1800


class AnalysisConfig(EvalConfig):
    """Fix the scoring cohort, validation thresholds and paired uncertainty."""

    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: str = MODEL_SHA256
    split: str
    arms: tuple[str, ...] = ARMS
    thresholds: dict[str, float] = Field(default_factory=dict)
    bootstrap_draws: int = 2000
    bootstrap_seed: int = 61024
    selected_arm: str | None = None


def native_layout(
    rows: list[dict[str, Any]],
) -> tuple[list[tuple[str, str]], list[int], list[int]]:
    """Retain the original two-pair left-then-right forward batch order."""
    keys: list[tuple[str, str]] = []
    left, right = [], []
    for start in range(0, len(rows), 2):
        selected = rows[start : start + 2]
        left.extend(range(len(keys), len(keys) + len(selected)))
        keys.extend((r["condition"], r["sentence1"]) for r in selected)
        right.extend(range(len(keys), len(keys) + len(selected)))
        keys.extend((r["condition"], r["sentence2"]) for r in selected)
    return keys, left, right


def sentence_tokens(
    tokenizer: Any, keys: list[tuple[str, str]], config: EncoderConfig
) -> tuple[list[list[int]], list[list[bool]]]:
    """Select positive offset overlap with passage characters; exclude specials."""
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
    masks = []
    for (condition, passage), text, ids, offsets, sequence in zip(
        keys,
        texts,
        encoded["input_ids"],
        encoded["offset_mapping"],
        sequences,
        strict=True,
    ):
        start = len(PROMPT.format(condition=condition, passage=""))
        end = len(text)
        if text[start:end] != passage or sequence[:-1] != ids:
            raise ValueError("Tokenizer offsets and native prompt tokens disagree.")
        mask = [
            token not in special and max(a, start) < min(b, end)
            for token, (a, b) in zip(ids, offsets, strict=True)
        ] + [False]
        if not any(mask):
            raise ValueError(f"Empty passage mask: {(condition, passage)!r}")
        masks.append(mask)
    return sequences, masks


def pooled_states(
    hidden: torch.Tensor, attention: torch.Tensor, sentence_mask: torch.Tensor | None
) -> tuple[torch.Tensor, torch.Tensor | None]:
    """Read attended EOD and average the requested contextual passage states."""
    positions = torch.arange(hidden.shape[1], device=hidden.device).expand_as(attention)
    last = positions.masked_fill(~attention.bool(), -1).max(1).values
    if (last < 0).any():
        raise ValueError("An input has no attended token.")
    raw = hidden[torch.arange(len(hidden), device=hidden.device), last].float()
    mean = None
    if sentence_mask is not None:
        mask = sentence_mask.bool() & attention.bool()
        counts = mask.sum(1)
        if (counts == 0).any():
            raise ValueError("An attended passage mask is empty.")
        mean = (hidden.float() * mask.unsqueeze(-1)).sum(1) / counts.unsqueeze(-1)
    return raw, mean


@build(config=ExtractionConfig)
def extract(context: StageContext[ExtractionConfig]) -> None:
    """Share the same passage forwards across every prespecified scoring arm."""
    config = context.config
    started = time.monotonic()
    if file_sha256(context.inputs["model"]) != config.model_sha256:
        raise ValueError("Selected adapter checkpoint bytes changed.")
    if file_sha256(context.inputs["rows"]) != config.rows_sha256:
        raise ValueError("Input comparison bytes changed.")
    rows = load_json(context.inputs["rows"])
    validate_rows(rows)
    keys, left_indices, right_indices = native_layout(rows)
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    for name in ("model_id", "revision", "embedding_dimension", "max_length"):
        if getattr(fit, name) != getattr(config, name):
            raise ValueError(f"Checkpoint encoder setting changed: {name}.")
    tokenizer = load_tokenizer(config)
    sequences, masks = sentence_tokens(tokenizer, keys, config)
    conditions = sorted({c for c, _ in keys})
    reference_keys = [(c, "") for c in conditions] + [("", "")]
    reference_sequences = token_sequences(tokenizer, reference_keys, config)
    emit(
        "loading_model",
        split=config.split,
        passages=len(keys),
        references=len(reference_keys),
    )
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    del saved
    model.eval()
    model.requires_grad_(False)
    # Adapter identities were checked while their original requires_grad flags remained set.
    named_adapters = {n: p for n, p in model.named_parameters() if "lora_" in n}
    torch.cuda.reset_peak_memory_stats()
    raw, means, references = [], [], []
    tokens = 0
    last_emit = time.monotonic()
    inference_started = time.monotonic()
    with torch.inference_mode():
        for kind, seqs, target in (
            ("passages", sequences, raw),
            ("references", reference_sequences, references),
        ):
            for start in range(0, len(seqs), config.encode_batch_size):
                if time.monotonic() - started > config.max_seconds:
                    raise TimeoutError("Fixed extraction allowance exhausted.")
                selected = seqs[start : start + config.encode_batch_size]
                batch = pad_sequences(tokenizer, selected, config)
                mask = None
                if kind == "passages":
                    width = batch["input_ids"].shape[1]
                    chosen = masks[start : start + config.encode_batch_size]
                    padded = [
                        [False] * (width - len(m)) + m
                        if tokenizer.padding_side == "left"
                        else m + [False] * (width - len(m))
                        for m in chosen
                    ]
                    mask = torch.tensor(padded, device=config.device)
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    hidden = model(**batch).last_hidden_state
                value, mean = pooled_states(hidden, batch["attention_mask"], mask)
                target.append(value.cpu())
                if mean is not None:
                    means.append(mean.cpu())
                tokens += int(batch["attention_mask"].sum())
                now = time.monotonic()
                if now - last_emit >= 15 or start + len(selected) == len(seqs):
                    emit(
                        "extraction_progress",
                        split=config.split,
                        kind=kind,
                        done=start + len(selected),
                        total=len(seqs),
                        elapsed_seconds=round(now - started, 2),
                    )
                    last_emit = now
    synchronize(config.device)
    after = state_digest(named_adapters)
    if before != after:
        raise ValueError("Adapter bytes changed during fixed-checkpoint inference.")
    cache = {
        "keys": keys,
        "row_left_indices": left_indices,
        "row_right_indices": right_indices,
        "batching": "original_two_pairs_left_then_right",
        "raw": torch.cat(raw),
        "means": torch.cat(means),
        "reference_keys": reference_keys,
        "references": torch.cat(references),
        "passage_token_counts": [sum(m) for m in masks],
        "rows_sha256": config.rows_sha256,
        "model_sha256": config.model_sha256,
        "prompt": PROMPT,
        "eod": EOD,
        "max_length": config.max_length,
        "revision": config.revision,
    }
    torch.save(cache, context.outputs["cache"])
    write_json(
        context.outputs["timing"],
        {
            "split": config.split,
            "rows": len(rows),
            "unique_passages": len(set(keys)),
            "passage_occurrences": len(keys),
            "references": len(reference_keys),
            "nonpadding_tokens": tokens,
            "model_sha256": config.model_sha256,
            "rows_sha256": config.rows_sha256,
            "adapter_state_before_sha256": before,
            "adapter_state_after_sha256": after,
            "optimizer_updates": 0,
            "inference_seconds": time.monotonic() - inference_started,
            "total_seconds": time.monotonic() - started,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
            "cache_sha256": file_sha256(context.outputs["cache"]),
        },
    )
    emit("extraction_complete", split=config.split, seconds=time.monotonic() - started)


def unit(vectors: np.ndarray) -> np.ndarray:
    """Normalize finite float32 vectors and reject undefined residual directions."""
    vectors = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    bad = (
        (~np.isfinite(vectors).all(1))
        | (~np.isfinite(norms[:, 0]))
        | (norms[:, 0] <= MIN_NORM)
    )
    if bad.any():
        raise ValueError(
            f"Invalid embedding/residual indices: {np.flatnonzero(bad).tolist()}"
        )
    return vectors / norms


def representations(cache: dict[str, Any]) -> dict[str, np.ndarray]:
    """Apply each normalization order to the exact shared extracted states."""
    raw = cache["raw"].numpy()
    refs = cache["references"].numpy()
    lookup = {tuple(k): i for i, k in enumerate(cache["reference_keys"])}
    condition = refs[[lookup[(c, "")] for c, _ in cache["keys"]]]
    generic = np.broadcast_to(refs[lookup[("", "")]], raw.shape)
    native = unit(raw)
    return {
        "A": native,
        "B_u": unit(native - unit(condition)),
        "B_r": unit(raw - condition),
        "C_u": unit(native - unit(generic)),
        "C_r": unit(raw - generic),
        "D": unit(cache["means"].numpy()),
    }


def confusion(
    rows: list[dict[str, Any]], scores: np.ndarray, cutoff: float
) -> dict[str, Any]:
    """Count dissimilar and similar pairs with the frozen inclusive threshold."""
    rating = np.asarray([r["rating"] for r in rows])
    positive, negative = rating >= 4, rating <= 2
    predicted = scores >= cutoff
    tp, fn = int((positive & predicted).sum()), int((positive & ~predicted).sum())
    fp, tn = int((negative & predicted).sum()), int((negative & ~predicted).sum())
    return {
        "cutoff": float(cutoff),
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "recall": tp / (tp + fn) if tp + fn else None,
        "false_negative_rate": fn / (tp + fn) if tp + fn else None,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "excluded_middle_rating": int((~positive & ~negative).sum()),
    }


def recall_cutoff(
    rows: list[dict[str, Any]], scores: np.ndarray, recall: float = 0.9
) -> float:
    """Return the largest observed cutoff retaining at least the required positives."""
    positives = np.sort(scores[[r["rating"] >= 4 for r in rows]])[::-1]
    if not len(positives):
        raise ValueError("A recall cutoff requires positive validation pairs.")
    return float(positives[math.ceil(recall * len(positives)) - 1])


def arm_metrics(
    rows: list[dict[str, Any]], scores: np.ndarray, cutoff: float
) -> dict[str, Any]:
    """Recompute all predictive diagnostics from the captured comparison scores."""
    scored = [
        dict(row, prediction=float(s)) for row, s in zip(rows, scores, strict=True)
    ]
    result = summarize(scored)
    result["operating_point"] = confusion(rows, scores, cutoff)
    result["descriptive_cutoffs"] = {
        str(x): confusion(rows, scores, x) for x in (0.5, 0.75)
    }
    result["errors_by_rating"] = {
        str(rating): {
            "n": len(selected),
            "signed_error": float(
                np.mean([r["prediction"] - r["target"] for r in selected])
            ),
            "mse": float(
                np.mean([(r["prediction"] - r["target"]) ** 2 for r in selected])
            ),
        }
        for rating in sorted({r["rating"] for r in rows})
        if (selected := [r for r in scored if r["rating"] == rating])
    }
    return result


def select_arm(metrics: dict[str, Any]) -> dict[str, Any]:
    """Apply frozen validation eligibility and tie rules without consulting test."""
    baseline = metrics["A"]
    eligibility = {}
    for arm, result in metrics.items():
        if arm == "A":
            continue
        drop = (
            baseline["operating_point"]["false_positive_rate"]
            - result["operating_point"]["false_positive_rate"]
        )
        rank_change = result["spearman"] - baseline["spearman"]
        eligibility[arm] = {
            "false_positive_rate_reduction": drop,
            "spearman_change": rank_change,
            "eligible": drop >= 0.02 - 1e-12 and rank_change >= -0.005 - 1e-12,
        }
    eligible = [a for a in eligibility if eligibility[a]["eligible"]]

    def key(arm: str) -> tuple[Any, ...]:
        m = metrics[arm]
        return (
            m["operating_point"]["false_positive_rate"],
            -m["spearman"],
            arm == "D",
            0 if arm in {"C_u", "C_r", "D"} else 1,
            ARMS.index(arm),
        )

    selected = min(eligible, key=key) if eligible else "A"
    return {
        "selected_arm": selected,
        "eligibility": eligibility,
        "thresholds": {a: m["operating_point"]["cutoff"] for a, m in metrics.items()},
        "test_scores_used_for_selection": False,
    }


def geometry(vectors: np.ndarray) -> dict[str, Any]:
    """Compute the full covariance spectrum on the unique-input cohort."""
    x = vectors.astype(np.float64)
    n, width = x.shape
    mean = x.mean(0)
    centered = x - mean
    gram = centered @ centered.T if n <= width else centered.T @ centered
    spectrum = np.clip(eigvalsh(gram / n, check_finite=False), 0, None)[::-1]
    trace = float(spectrum.sum())
    return {
        "n_unique_inputs": n,
        "width": width,
        "sample_covariance_rank_ceiling": min(n - 1, width),
        "mean_vector_norm": float(np.linalg.norm(mean)),
        "mean_pairwise_cosine": float(
            ((x.sum(0) ** 2).sum() - (x * x).sum()) / (n * (n - 1))
        )
        if n > 1
        else None,
        "covariance_eigenvalues": spectrum.tolist(),
        "covariance_trace": trace,
        "leading_variance_share": float(spectrum[0] / trace) if trace > 0 else None,
        "participation_rank": float(trace**2 / np.square(spectrum).sum())
        if trace > 0
        else None,
    }


def array_summary(values: np.ndarray) -> dict[str, float]:
    """Retain norms and alignment distributions without losing their extremes."""
    return {
        "min": float(values.min()),
        "mean": float(values.mean()),
        "max": float(values.max()),
        "p05": float(np.quantile(values, 0.05)),
        "median": float(np.median(values)),
        "p95": float(np.quantile(values, 0.95)),
    }


def paired_bootstrap(
    rows: list[dict[str, Any]],
    scores: dict[str, np.ndarray],
    thresholds: dict[str, float],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    """Resample connected source groups together and keep every cutoff fixed."""
    groups: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row["group_id"]].append(i)
    indices = [np.asarray(groups[g]) for g in sorted(groups)]
    rng = np.random.default_rng(seed)
    target = np.asarray([r["target"] for r in rows])
    rating = np.asarray([r["rating"] for r in rows])
    changes: dict[str, dict[str, list[float]]] = {
        a: {m: [] for m in ("spearman", "mse", "false_positive_rate", "recall")}
        for a in scores
        if a != "A"
    }
    for draw in range(draws):
        ix = np.concatenate(
            [indices[i] for i in rng.integers(0, len(indices), len(indices))]
        )
        y, r = target[ix], rating[ix]
        positive, negative = r >= 4, r <= 2
        result = {}
        for arm, full in scores.items():
            s = full[ix]
            result[arm] = {
                "spearman": float(spearmanr(y, s).statistic),
                "mse": float(np.mean((s - y) ** 2)),
                "false_positive_rate": float((s[negative] >= thresholds[arm]).mean())
                if negative.any()
                else math.nan,
                "recall": float((s[positive] >= thresholds[arm]).mean())
                if positive.any()
                else math.nan,
            }
        for arm, metric_lists in changes.items():
            for metric, values in metric_lists.items():
                difference = result[arm][metric] - result["A"][metric]
                if math.isfinite(difference):
                    values.append(difference)
        if (draw + 1) % 500 == 0:
            emit("bootstrap_progress", done=draw + 1, total=draws)
    result = {}
    for arm, metrics in changes.items():
        result[arm] = {}
        for metric, values in metrics.items():
            if len(values) < 0.95 * draws:
                raise ValueError("Insufficient valid paired bootstrap draws.")
            result[arm][metric] = {
                "valid_draws": len(values),
                "percentile_95": np.quantile(values, [0.025, 0.975]).tolist(),
            }
    return {
        "groups": len(indices),
        "draws": draws,
        "seed": seed,
        "thresholds_fixed": True,
        "candidate_minus_A": result,
    }


@eval(config=AnalysisConfig)
def analyze(context: StageContext[AnalysisConfig]) -> None:
    """Independently derive scores, decision thresholds and geometry on CPU."""
    config = context.config
    if file_sha256(context.inputs["test"]) != config.rows_sha256:
        raise ValueError("Analysis rows changed.")
    rows = load_json(context.inputs["test"])
    timing = load_json(context.inputs["timing"])
    if file_sha256(context.inputs["cache"]) != timing["cache_sha256"]:
        raise ValueError("Extracted cache differs from its timing receipt.")
    cache = load_model(context.inputs["cache"])
    if (
        cache["rows_sha256"] != config.rows_sha256
        or cache["model_sha256"] != config.model_sha256
    ):
        raise ValueError("Extracted cache identity differs.")
    keys = [tuple(k) for k in cache["keys"]]
    lookup = {k: i for i, k in enumerate(keys)}
    left = cache.get(
        "row_left_indices", [lookup[(r["condition"], r["sentence1"])] for r in rows]
    )
    right = cache.get(
        "row_right_indices", [lookup[(r["condition"], r["sentence2"])] for r in rows]
    )
    vectors = representations(cache)
    scores = {
        a: np.sum(vectors[a][left] * vectors[a][right], axis=1, dtype=np.float32)
        for a in config.arms
    }
    old = load_json(context.inputs["baseline_predictions"])
    old_map = {r["row_id"]: r for r in old}
    if len(old_map) != len(rows):
        raise ValueError("Sealed native prediction coverage changed.")
    for r in rows:
        if {k: v for k, v in old_map[r["row_id"]].items() if k != "prediction"} != r:
            raise ValueError("Sealed native prediction row identities differ.")
    differences = np.abs(
        scores["A"] - np.asarray([old_map[r["row_id"]]["prediction"] for r in rows])
    )
    agreement = {
        "max_absolute_error": float(differences.max()),
        "mean_absolute_error": float(differences.mean()),
        "tolerance": 0.001,
    }
    write_json(context.outputs["agreement"], agreement)
    emit("baseline_agreement", split=config.split, **agreement)
    if differences.max() > 0.001:
        raise ValueError(
            "Native scores need reconciliation before intervention interpretation."
        )
    metrics, thresholds = {}, {}
    for arm, values in scores.items():
        cutoff = (
            config.thresholds[arm]
            if config.split == "test"
            else recall_cutoff(rows, values)
        )
        thresholds[arm] = cutoff
        metrics[arm] = arm_metrics(rows, values, cutoff)
        emit("arm_result", split=config.split, arm=arm, **metrics[arm])
    predictions = {
        a: [dict(r, prediction=float(v)) for r, v in zip(rows, s, strict=True)]
        for a, s in scores.items()
    }
    write_json(context.outputs["predictions"], predictions)
    decision = (
        select_arm(metrics)
        if config.split == "validation"
        else {"selected_arm": config.selected_arm, "thresholds": thresholds}
    )
    report = {
        "split": config.split,
        "metrics": metrics,
        "decision": decision,
        "agreement": agreement,
        "model_sha256": config.model_sha256,
        "rows_sha256": config.rows_sha256,
        "timing": timing,
    }
    write_json(context.outputs["report"], report)
    emit("selection", split=config.split, **decision)
    if config.split == "test":
        report["paired_bootstrap"] = paired_bootstrap(
            rows, scores, thresholds, config.bootstrap_draws, config.bootstrap_seed
        )
        candidate = metrics[config.selected_arm]
        baseline = metrics["A"]
        fpr_drop = (
            baseline["operating_point"]["false_positive_rate"]
            - candidate["operating_point"]["false_positive_rate"]
        )
        recall_change = (
            candidate["operating_point"]["recall"]
            - baseline["operating_point"]["recall"]
        )
        spearman_change = candidate["spearman"] - baseline["spearman"]
        report["transfer"] = {
            "false_positive_rate_reduction": fpr_drop,
            "recall_change": recall_change,
            "spearman_change": spearman_change,
            "passes": fpr_drop >= 0.02 - 1e-12
            and recall_change >= -0.01 - 1e-12
            and spearman_change >= -0.005 - 1e-12,
        }
        write_json(context.outputs["report"], report)
        emit("transfer_result", **report["transfer"])
    first_occurrence: dict[tuple[str, str], int] = {}
    for i, key in enumerate(keys):
        first_occurrence.setdefault(key, i)
    unique_indices = list(first_occurrence.values())
    unique_keys = list(first_occurrence)
    geometry_vectors = {a: v[unique_indices] for a, v in vectors.items()}
    condition_indices: dict[str, list[int]] = defaultdict(list)
    source_groups: dict[str, set[str]] = defaultdict(set)
    for i, (c, _) in enumerate(unique_keys):
        condition_indices[c].append(i)
    for r in rows:
        source_groups[r["condition"]].add(r["group_id"])
    geometry_report = {}
    for arm in config.arms:
        condition_results = {}
        for c, ix in condition_indices.items():
            if len(ix) >= 16:
                condition_results[c] = {
                    **geometry(geometry_vectors[arm][ix]),
                    "source_groups": len(source_groups[c]),
                }
        geometry_report[arm] = {
            "global": geometry(geometry_vectors[arm]),
            "within_condition": condition_results,
            "smaller_condition_groups": {
                c: len(ix) for c, ix in condition_indices.items() if len(ix) < 16
            },
        }
        emit(
            "geometry_result",
            split=config.split,
            arm=arm,
            **{
                k: v
                for k, v in geometry_report[arm]["global"].items()
                if k != "covariance_eigenvalues"
            },
        )
    reference_lookup = {tuple(k): i for i, k in enumerate(cache["reference_keys"])}
    raw = cache["raw"].numpy()[unique_indices]
    reference = cache["references"].numpy()[
        [reference_lookup[(c, "")] for c, _ in unique_keys]
    ]
    raw_norm, reference_norm = (
        np.linalg.norm(raw, axis=1),
        np.linalg.norm(reference, axis=1),
    )
    alignments = {
        "raw_norm": array_summary(raw_norm),
        "condition_reference_norm": array_summary(reference_norm),
        "norm_ratio_reference_over_passage": array_summary(reference_norm / raw_norm),
        "condition_reference_cosine": array_summary(
            np.sum(unit(raw) * unit(reference), axis=1)
        ),
        "raw_condition_residual_norm": array_summary(
            np.linalg.norm(raw - reference, axis=1)
        ),
        "unit_condition_residual_norm": array_summary(
            np.linalg.norm(unit(raw) - unit(reference), axis=1)
        ),
        "passage_token_count": array_summary(
            np.asarray(cache["passage_token_counts"])[unique_indices]
        ),
    }
    write_json(
        context.outputs["geometry"],
        {"arms": geometry_report, "reference_alignment": alignments},
    )
    emit("analysis_complete", split=config.split)
