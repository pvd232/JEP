"""Full-width condition-guided readouts over one frozen Qwen checkpoint."""

import copy
import hashlib
import itertools
import json
import math
from collections import Counter
from typing import Any

import numpy as np
import torch
from scipy.stats import spearmanr
from torch import nn
from torch.nn import functional as F

from csts_pilot.answers import answer_id

ARMS = ("ratings", "evidence")
COMPARATOR_ARMS = ("ratings_comparison", "evidence_comparison")
CONTRASTS = {
    "C_minus_B": {"evidence": 1, "ratings": -1},
    "E_minus_D": {"evidence_comparison": 1, "ratings_comparison": -1},
    "D_minus_B": {"ratings_comparison": 1, "ratings": -1},
    "E_minus_C": {"evidence_comparison": 1, "evidence": -1},
    "interaction": {
        "evidence_comparison": 1,
        "ratings_comparison": -1,
        "evidence": -1,
        "ratings": 1,
    },
}
SCHEMA_VERSION = 1


def object_sha256(value: Any) -> str:
    """Hash a deterministic, finite JSON description, independently of file formatting."""
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def clone_state(module: nn.Module) -> dict[str, torch.Tensor]:
    """Keep selected parameters independent of later optimizer mutations."""
    return {
        name: value.detach().cpu().clone()
        for name, value in module.state_dict().items()
    }


class EvidenceReadout(nn.Module):
    """Use condition queries and source keys; retain full-width contextual values.

    The joint source/null softmax learns answerability. A second softmax over
    source logits constructs the conditional content vector stably even when
    the null outcome has almost all joint probability. Null probability is
    reported separately and never used to remove comparisons from the metric.
    """

    def __init__(self, input_dim: int = 4096, query_dim: int = 128):
        super().__init__()
        if input_dim < 2 or query_dim < 1:
            raise ValueError(
                "Readout dimensions must be positive; values need width >= 2."
            )
        self.input_dim = input_dim
        self.query = nn.Linear(input_dim, query_dim, bias=False)
        self.key = nn.Linear(input_dim, query_dim, bias=False)
        self.null_key = nn.Parameter(torch.zeros(query_dim))
        self.null_bias = nn.Parameter(torch.zeros(1))

    def forward(
        self, tokens: torch.Tensor, condition: torch.Tensor, mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Return unit content vectors, masked source/null logits, and probabilities."""
        if (
            tokens.ndim != 3
            or tokens.shape[-1] != self.input_dim
            or condition.shape != (len(tokens), self.input_dim)
            or mask.shape != tokens.shape[:2]
            or mask.dtype != torch.bool
            or not mask.any(1).all()
        ):
            raise ValueError(
                "Readout requires matching states and nonempty source masks."
            )
        if not torch.isfinite(tokens).all() or not torch.isfinite(condition).all():
            raise ValueError("Readout states must be finite, including padding.")
        with torch.autocast(tokens.device.type, enabled=False):
            dtype = self.query.weight.dtype
            values, context = tokens.to(dtype), condition.to(dtype)
            q = self.query(F.layer_norm(context, (self.input_dim,)))
            k = self.key(F.layer_norm(values, (self.input_dim,)))
            scores = (k * q[:, None]).sum(-1) / math.sqrt(q.shape[-1])
            scores = scores.masked_fill(~mask, -torch.inf)
            null = (q * self.null_key).sum(-1) / math.sqrt(q.shape[-1]) + self.null_bias
            logits = torch.cat((null[:, None], scores), dim=1)
            probabilities = logits.softmax(1)
            content_weights = scores.softmax(1)
            pooled = (content_weights[:, :, None] * values).sum(1)
            if not torch.isfinite(pooled).all() or (pooled.norm(dim=1) <= 1e-8).any():
                raise ValueError("The selected content vector has no finite direction.")
            return F.normalize(pooled, dim=1), logits, probabilities


class SymmetricComparison(nn.Module):
    """Learn a full-coordinate residual score, starting at exactly cosine.

    This is a deliberately limited comparator intervention: symmetric diagonal
    products and absolute differences, without a new sentence projection.
    """

    def __init__(self, input_dim: int = 4096):
        super().__init__()
        self.residual = nn.Linear(2 * input_dim, 1)
        nn.init.zeros_(self.residual.weight)
        nn.init.zeros_(self.residual.bias)

    def forward(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        features = torch.cat(((left - right).abs(), left * right), dim=-1)
        return (left * right).sum(-1) + self.residual(features).squeeze(-1)


def quotation_target(
    passage: str, offsets: list[tuple[int, int]], record: dict[str, Any] | None
) -> tuple[torch.Tensor, str]:
    """Align complete, unique literal quotations; missing labels never mean negative."""
    target = torch.zeros(len(offsets) + 1, dtype=torch.float32)
    if not offsets or any(not 0 <= a < b <= len(passage) for a, b in offsets):
        raise ValueError("Evidence offsets must cover real source tokens.")
    if record is None:
        return target, "uncaptured"
    status = record.get("status")
    evidence = record.get("evidence")
    if status not in {"answered", "not_specified", "ambiguous"}:
        raise ValueError("Unknown evidence status.")
    if not isinstance(evidence, list) or any(not isinstance(q, str) for q in evidence):
        raise ValueError("Evidence quotations must be strings.")
    if status != "answered":
        if record.get("answer") != "" or evidence:
            raise ValueError("Abstentions must have empty answer and evidence.")
        if status == "not_specified":
            target[0] = 1
        return target, status
    if any(
        not isinstance(record.get(k), str) or not record[k].strip()
        for k in ("target", "attribute", "answer")
    ):
        raise ValueError("Answered evidence needs a nonempty answer.")
    if not evidence or len(evidence) != len(set(evidence)):
        raise ValueError("Answered evidence needs nonempty, distinct quotations.")
    spans = []
    for quote in evidence:
        start = passage.find(quote)
        if not quote.strip() or start < 0:
            return target, "quotation_absent_from_variant"
        if passage.find(quote, start + 1) >= 0:
            return target, "ambiguous_quotation_occurrence"
        end = start + len(quote)
        covered = [j for j, (a, b) in enumerate(offsets) if max(a, start) < min(b, end)]
        if not covered:
            return target, "unaligned_quotation"
        spans.append((start, end))
    for j, (a, b) in enumerate(offsets, start=1):
        target[j] = float(any(max(a, start) < min(b, end) for start, end in spans))
    if target.sum() <= 0:
        raise ValueError("Aligned answered evidence needs source-token mass.")
    return target / target.sum(), "answered"


def bind_records(
    keys: list[tuple[str, str]], records: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Reject duplicates and foreign/held-out identities before any teacher use."""
    allowed = {answer_id(passage, condition) for condition, passage in keys}
    bound = {}
    expected = {"id", "status", "target", "attribute", "answer", "evidence"}
    for record in records:
        if (
            not isinstance(record, dict)
            or set(record) != expected
            or not isinstance(record["id"], str)
            or not record["id"]
            or any(
                not isinstance(record[k], str)
                for k in ("target", "attribute", "answer")
            )
        ):
            raise ValueError("Evidence records must follow the captured schema.")
        identity = record["id"]
        if identity not in allowed or identity in bound:
            raise ValueError("Duplicate or foreign evidence identity.")
        bound[identity] = record
    return bound


def validate_capture(
    provenance: dict[str, Any],
    gate: dict[str, Any],
    records_sha256: str,
    training_sha256: str,
    gate_sha256: str,
    items: int,
) -> None:
    """Bind teacher bytes to the audited generation policy, without claiming human gold."""
    if (
        provenance.get("records_sha256") != records_sha256
        or provenance.get("source_training_sha256") != training_sha256
        or type(provenance.get("items")) is not int
        or provenance["items"] != items
        or provenance.get("audit_gate_sha256") != gate_sha256
    ):
        raise ValueError(
            "Teacher provenance differs from the captured training inputs."
        )
    if gate.get("passed") is not True or gate.get("generation_frozen") is not True:
        raise ValueError("A passed frozen generation gate is required.")
    for key in (
        "generation_template_sha256",
        "schema_sha256",
        "model_alias",
        "reasoning_effort",
        "capture_source_sha256",
    ):
        if not provenance.get(key) or gate.get(key) != provenance[key]:
            raise ValueError(
                f"The teacher and audited generation policy differ: {key}."
            )


def validate_cache(cache: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    """Check packed tensor boundaries, exact comparison bindings, and supervision roles."""
    if cache.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unknown readout cache schema.")
    keys, pointers = cache["keys"], cache["pointers"]
    n, width = len(keys), cache["embedding_dimension"]
    if (
        not n
        or not isinstance(width, int)
        or isinstance(width, bool)
        or width < 2
        or any(
            len(k) != 2 or any(not isinstance(v, str) or not v.strip() for v in k)
            for k in keys
        )
        or len(pointers) != n + 1
        or pointers[0] != 0
        or any(not isinstance(p, int) or isinstance(p, bool) for p in pointers)
        or any(a >= b for a, b in itertools.pairwise(pointers))
        or cache["token_values"].shape != (pointers[-1], width)
        or cache["condition_states"].shape != (n, width)
        or cache["eod_vectors"].shape != (n, width)
        or cache["span_targets"].shape != (pointers[-1],)
        or cache["null_targets"].shape != (n,)
        or len(cache["metadata"]) != n
    ):
        raise ValueError("Invalid packed readout cache shapes or boundaries.")
    for name in (
        "token_values",
        "condition_states",
        "eod_vectors",
        "span_targets",
        "null_targets",
    ):
        if not torch.isfinite(cache[name]).all():
            raise ValueError(f"Nonfinite readout cache: {name}.")
    if (cache["span_targets"] < 0).any() or (cache["null_targets"] < 0).any():
        raise ValueError("Evidence targets must be nonnegative.")
    for i, (a, b) in enumerate(itertools.pairwise(pointers)):
        total = float(cache["span_targets"][a:b].sum() + cache["null_targets"][i])
        if not (
            math.isclose(total, 0, abs_tol=1e-6) or math.isclose(total, 1, abs_tol=1e-6)
        ):
            raise ValueError("Evidence distributions need zero or unit target mass.")
        offsets = cache["metadata"][i]["passage_offsets"]
        if b - a != len(offsets) or any(
            not 0 <= start < end <= len(keys[i][1]) for start, end in offsets
        ):
            raise ValueError("Source offsets differ from packed token states.")
    if not torch.allclose(
        cache["eod_vectors"].float().norm(dim=1), torch.ones(n), atol=1e-5, rtol=1e-5
    ):
        raise ValueError("Parent EOD vectors must retain their unit normalization.")
    if cache["split"] != "training" and (
        cache.get("records_sha256") is not None
        or cache["span_targets"].count_nonzero()
        or cache["null_targets"].count_nonzero()
    ):
        raise ValueError("Held-out caches cannot contain teacher targets.")
    if len(cache["left"]) != len(rows) or len(cache["right"]) != len(rows):
        raise ValueError("Comparison cache has incomplete coverage.")
    used = set()
    for row, left, right in zip(rows, cache["left"], cache["right"], strict=True):
        for side, position in (("sentence1", left), ("sentence2", right)):
            if (
                not isinstance(position, int)
                or isinstance(position, bool)
                or not 0 <= position < n
            ):
                raise ValueError("Invalid comparison occurrence index.")
            if tuple(keys[position]) != (row["condition"], row[side]):
                raise ValueError(
                    "Cache occurrence is bound to another sentence/condition."
                )
            used.add(position)
    if used != set(range(n)):
        raise ValueError("Cache has orphan source occurrences.")


def pack_batch(
    cache: dict[str, Any], positions: list[int], device: str
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Materialize only requested occurrences and add the null target in column zero."""
    if not positions or any(
        not isinstance(i, int) or not 0 <= i < len(cache["keys"]) for i in positions
    ):
        raise ValueError("A readout batch needs valid occurrence indices.")
    tokens, targets = [], []
    for i in positions:
        a, b = cache["pointers"][i : i + 2]
        tokens.append(cache["token_values"][a:b])
        targets.append(cache["span_targets"][a:b])
    values = nn.utils.rnn.pad_sequence(tokens, batch_first=True).to(
        device, torch.float32
    )
    lengths = torch.tensor([len(t) for t in tokens], device=device)
    mask = torch.arange(values.shape[1], device=device)[None] < lengths[:, None]
    source_targets = nn.utils.rnn.pad_sequence(targets, batch_first=True).to(device)
    gold = torch.cat(
        (cache["null_targets"][positions, None].to(device), source_targets), dim=1
    )
    return (
        values,
        cache["condition_states"][positions].to(device, torch.float32),
        mask,
        gold,
    )


def selection_loss(
    logits: torch.Tensor, mask: torch.Tensor, target: torch.Tensor
) -> tuple[torch.Tensor, int]:
    """Average CE over labeled occurrences; unknown/ambiguous records contribute zero."""
    valid = torch.cat(
        (torch.ones(len(mask), 1, device=mask.device, dtype=torch.bool), mask), dim=1
    )
    if logits.shape != valid.shape or target.shape != valid.shape:
        raise ValueError("Evidence logit and target shapes disagree.")
    if (
        not torch.isfinite(target).all()
        or (target < 0).any()
        or target[~valid].count_nonzero()
    ):
        raise ValueError("Invalid evidence target support.")
    if not torch.isfinite(logits[valid]).all():
        raise ValueError("Evidence logits must be finite on permitted positions.")
    totals = target.sum(1)
    supervised = totals > 0
    if not torch.allclose(
        totals[supervised], torch.ones_like(totals[supervised]), atol=1e-6, rtol=0
    ):
        raise ValueError("Supervised evidence distributions must have unit mass.")
    count = int(supervised.sum())
    if not count:
        return logits[valid].sum() * 0, 0
    logp = logits.masked_fill(~valid, -torch.inf).log_softmax(1).masked_fill(~valid, 0)
    return -(target * logp).sum(1)[supervised].mean(), count


def gradient_diagnostic(
    head: nn.Module, rating: torch.Tensor, evidence: torch.Tensor, weight: float
) -> dict[str, Any]:
    """Measure loss alignment without accumulating gradients or changing any RNG state."""
    named = tuple(head.named_parameters())
    parameters = tuple(p for _, p in named)
    gradients = []
    for objective in (rating, weight * evidence):
        gs = torch.autograd.grad(
            objective, parameters, retain_graph=True, allow_unused=True
        )
        gradients.append(
            torch.cat(
                [
                    (torch.zeros_like(p) if g is None else g).flatten()
                    for (name, p), g in zip(named, gs, strict=True)
                    if name.startswith(("query.", "key."))
                ]
            )
        )
    a, b = gradients
    na, nb = float(a.norm()), float(b.norm())
    return {
        "scope": "query_and_key_weights_that_affect_similarity",
        "rating_norm": na,
        "weighted_evidence_norm": nb,
        "evidence_to_rating_ratio": nb / na if na else None,
        "cosine": float(F.cosine_similarity(a, b, dim=0)) if na and nb else None,
    }


def readout_vectors(
    head: EvidenceReadout | None, cache: dict[str, Any], device: str = "cpu"
) -> tuple[torch.Tensor, list[torch.Tensor], np.ndarray]:
    """Encode occurrences once; comparator fitting consumes detached full-width states."""
    if head is None:
        vectors = cache["eod_vectors"].float()
        return (
            vectors,
            [],
            np.full(len(vectors), np.nan),
        )
    head.eval()
    vectors, weights, null = [], [], []
    with torch.no_grad():
        for start in range(0, len(cache["keys"]), 64):
            positions = list(range(start, min(start + 64, len(cache["keys"]))))
            tokens, condition, mask, _ = pack_batch(cache, positions, device)
            vector, logits, probabilities = head(tokens, condition, mask)
            vectors.append(vector.cpu())
            null.extend(probabilities[:, 0].cpu().tolist())
            content = logits[:, 1:].softmax(1).cpu()
            for row, i in enumerate(positions):
                length = cache["pointers"][i + 1] - cache["pointers"][i]
                weights.append(content[row, :length].clone())
    return torch.cat(vectors), weights, np.asarray(null)


def predict(
    head: EvidenceReadout | None,
    cache: dict[str, Any],
    device: str = "cpu",
    comparator: SymmetricComparison | None = None,
) -> tuple[np.ndarray, list[torch.Tensor], np.ndarray]:
    """Score every comparison; a comparator never changes the selected vectors."""
    z, weights, null = readout_vectors(head, cache, device)
    with torch.no_grad():
        left, right = z[cache["left"]], z[cache["right"]]
        values = (
            (left * right).sum(1)
            if comparator is None
            else comparator(left.to(device), right.to(device)).cpu()
        )
    return (
        values.numpy(),
        weights,
        null,
    )


def metric_values(
    rows: list[dict[str, Any]], predictions: np.ndarray
) -> dict[str, Any]:
    """Keep normalized MSE and rank correlation definitions independent of the trainer."""
    gold = np.asarray([row["target"] for row in rows], dtype=np.float64)
    predicted = np.asarray(predictions, dtype=np.float64)
    if (
        gold.shape != predicted.shape
        or not len(gold)
        or not np.isfinite(predicted).all()
        or not np.isfinite(gold).all()
        or (gold < 0).any()
        or (gold > 1).any()
    ):
        raise ValueError("Predictions need exact, finite comparison coverage.")
    rho = (
        float(spearmanr(gold, predicted).statistic)
        if np.ptp(gold) and np.ptp(predicted)
        else None
    )
    return {
        "n": len(gold),
        "mse_0_1": float(np.mean((predicted - gold) ** 2)),
        "spearman": rho,
    }


def paired_intervals(
    rows: list[dict[str, Any]],
    predictions: dict[str, dict[str, list[float]]],
    draws: int,
    seed: int,
    contrast: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Bootstrap source groups jointly and average per-seed paired Spearman differences."""
    if draws < 1 or not predictions:
        raise ValueError(
            "Bootstrap requires positive draws and frozen seed predictions."
        )
    groups: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        groups.setdefault(row["group_id"], []).append(i)
    members = list(groups.values())
    if len(members) < 2:
        raise ValueError("Source-group uncertainty requires at least two groups.")
    contrast = contrast or CONTRASTS["C_minus_B"]
    arrays = {
        s: {a: np.asarray(arms[a], dtype=np.float64) for a in contrast}
        for s, arms in predictions.items()
    }
    for arms in arrays.values():
        for values in arms.values():
            metric_values(rows, values)
    gold = np.asarray([r["target"] for r in rows])
    rng = np.random.default_rng(seed)
    differences, mse_differences, skipped = [], [], 0
    for _ in range(draws):
        ix = np.concatenate(
            [members[i] for i in rng.integers(len(members), size=len(members))]
        )
        if not np.ptp(gold[ix]) or any(
            not np.ptp(v[ix]) for arms in arrays.values() for v in arms.values()
        ):
            skipped += 1
            continue
        delta = []
        for arms in arrays.values():
            delta.append(
                float(
                    sum(
                        weight * spearmanr(gold[ix], arms[arm][ix]).statistic
                        for arm, weight in contrast.items()
                    )
                )
            )
        differences.append(float(np.mean(delta)))
        mse_differences.append(
            float(
                np.mean(
                    [
                        sum(
                            weight * np.mean((arms[a][ix] - gold[ix]) ** 2)
                            for a, weight in contrast.items()
                        )
                        for arms in arrays.values()
                    ]
                )
            )
        )
    if not differences:
        raise ValueError("All group bootstrap draws have undefined correlations.")
    return {
        "groups": len(groups),
        "requested_draws": draws,
        "defined_draws": len(differences),
        "skipped_draws": skipped,
        "low": float(np.quantile(differences, 0.025)),
        "high": float(np.quantile(differences, 0.975)),
        "mse_low": float(np.quantile(mse_differences, 0.025)),
        "mse_high": float(np.quantile(mse_differences, 0.975)),
        "scope": "Test-source uncertainty conditional on the retained training seeds; no checkpoint-selection correction.",
    }


def training_targets(
    keys: list[tuple[str, str]],
    metadata: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> tuple[list[torch.Tensor], dict[str, int]]:
    """Produce source/null distributions without converting uncaptured entries to negatives."""
    bound = bind_records(keys, records)
    targets, counts = [], Counter()
    for (condition, passage), meta in zip(keys, metadata, strict=True):
        target, reason = quotation_target(
            passage, meta["passage_offsets"], bound.get(answer_id(passage, condition))
        )
        targets.append(target)
        counts[reason] += 1
    return targets, dict(counts)


def matched_initial_heads(
    input_dim: int, query_dim: int, seed: int
) -> dict[str, EvidenceReadout]:
    """Use identical initialization for the two heads without sharing live tensors."""
    torch.manual_seed(seed)
    initial = EvidenceReadout(input_dim, query_dim)
    return {arm: copy.deepcopy(initial) for arm in ARMS}
