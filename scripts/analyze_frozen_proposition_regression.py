"""Reproduce the retained frozen diagnostic and bootstrap paired source groups."""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

ARMS = ("saved_qwen_sample", "old_spans", "checked_generated_v1")


def midranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + end - 1) / 2 + 1
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def spearman(x, y):
    a, b = midranks(x), midranks(y)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    numerator = sum((u - ma) * (v - mb) for u, v in zip(a, b))
    denominator = math.sqrt(sum((u - ma) ** 2 for u in a) * sum((v - mb) ** 2 for v in b))
    return numerator / denominator if denominator else None


def mse(x, y):
    return sum((u - v) ** 2 for u, v in zip(x, y)) / len(x)


def percentile(values, p):
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] * (high - position) + ordered[high] * (position - low) if low != high else ordered[low]


def analysis(data, draws=10000, seed=61031):
    pairs = data["pairs"]
    if len(pairs) != 60 or len({p["group_id"] for p in pairs}) != 60:
        raise ValueError("Expected exactly 60 pairs from distinct source groups.")
    y = [p["target"] for p in pairs]
    predictions = {arm: [p["predictions"][arm] for p in pairs] for arm in ARMS}
    points = {arm: {"spearman": spearman(y, values), "mse": mse(y, values)} for arm, values in predictions.items()}
    for arm in ARMS:
        native = data["sample_metrics"][arm]
        assert abs(points[arm]["spearman"] - native["spearman"]) < 1e-12
        assert abs(points[arm]["mse"] - native["mse_0_1"]) < 1e-12
    base, generated = predictions[ARMS[0]], predictions[ARMS[2]]
    point_rank = points[ARMS[2]]["spearman"] - points[ARMS[0]]["spearman"]
    point_mse = points[ARMS[2]]["mse"] - points[ARMS[0]]["mse"]
    rng, rank_deltas, mse_deltas = random.Random(seed), [], []
    for _ in range(draws):
        indices = rng.choices(range(len(pairs)), k=len(pairs))
        target, a, b = ([values[i] for i in indices] for values in (y, base, generated))
        ra, rb = spearman(target, a), spearman(target, b)
        if ra is not None and rb is not None:
            rank_deltas.append(rb - ra)
        mse_deltas.append(mse(target, b) - mse(target, a))
    coverage = {}
    for count, name in ((2, "both"), (1, "one"), (0, "neither")):
        indices = [i for i, p in enumerate(pairs) if sum(p["replacement_status"][ARMS[2]]) == count]
        a, b, target = ([values[i] for i in indices] for values in (base, generated, y))
        coverage[name] = {"n": len(indices), "baseline_mse": mse(target, a), "generated_mse": mse(target, b), "net_mse_contribution": sum((generated[i] - y[i]) ** 2 - (base[i] - y[i]) ** 2 for i in indices) / len(pairs)}
    rating_groups = {}
    for rating in sorted({p["rating"] for p in pairs}):
        indices = [i for i, p in enumerate(pairs) if p["rating"] == rating]
        contribution = sum((generated[i] - y[i]) ** 2 - (base[i] - y[i]) ** 2 for i in indices) / len(pairs)
        rating_groups[str(rating)] = {"n": len(indices), "net_mse_contribution": contribution, "share_of_total_mse_increase": contribution / point_mse}
    influences = []
    for index, pair in enumerate(pairs):
        remaining = [i for i in range(len(pairs)) if i != index]
        target, a, b = ([values[i] for i in remaining] for values in (y, base, generated))
        without = spearman(target, b) - spearman(target, a)
        influences.append({**pair, "mse_delta": (generated[index] - y[index]) ** 2 - (base[index] - y[index]) ** 2, "spearman_delta_without_pair": without, "removal_change_in_spearman_delta": without - point_rank})
    bootstrap = {
        "unit": "source group; exactly one comparison per group",
        "draws": draws,
        "seed": seed,
        "method": "paired percentile bootstrap; within-draw Spearman midranks include duplicated observations and original rating ties",
        "valid_rank_draws": len(rank_deltas),
        "spearman_delta": point_rank,
        "spearman_delta_95_percentile_interval": [percentile(rank_deltas, p) for p in (0.025, 0.975)],
        "bootstrap_fraction_rank_delta_negative": sum(v < 0 for v in rank_deltas) / len(rank_deltas),
        "mse_delta": point_mse,
        "mse_delta_95_percentile_interval": [percentile(mse_deltas, p) for p in (0.025, 0.975)],
        "bootstrap_fraction_mse_delta_positive": sum(v > 0 for v in mse_deltas) / len(mse_deltas),
        "interpretation": "Conditional development-sample uncertainty for this fixed generation, screening, fallback and encoder policy; one training seed. Bootstrap sign fractions describe resampling outcomes.",
    }
    return {"cohort": "earlier 60-pair v1 frozen source diagnostic", "n": len(pairs), "source_groups": 60, "point_metrics": points, "bootstrap": bootstrap, "coverage_groups": coverage, "rating_groups": rating_groups, "leave_one_out_spearman_delta_range": [min(p["spearman_delta_without_pair"] for p in influences), max(p["spearman_delta_without_pair"] for p in influences)], "largest_mse_regressions": sorted(influences, key=lambda p: p["mse_delta"], reverse=True)[:10], "largest_mse_improvements": sorted(influences, key=lambda p: p["mse_delta"])[:5], "most_influential_rank_regressions": sorted(influences, key=lambda p: p["removal_change_in_spearman_delta"], reverse=True)[:5], "new_v2_subset_separate": data["subset"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=61031)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result = analysis(json.loads(raw), args.draws, args.seed)
    result["input_sha256"] = hashlib.sha256(raw).hexdigest()
    result["source_code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"bootstrap": result["bootstrap"], "coverage_groups": result["coverage_groups"], "rating_groups": result["rating_groups"], "leave_one_out_spearman_delta_range": result["leave_one_out_spearman_delta_range"]}, indent=2))
