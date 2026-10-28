"""Replay saved comparisons, audit individual errors and fit one frozen control head."""

import argparse
import copy
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    from csts_pilot.background_storage import _save

    _save(Path(path), value)


def pair_score(a, b, weights=None, bias=0.0):
    """Read the same unit vectors using cosine plus the saved symmetric correction."""
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    value = np.sum(a * b, axis=-1)
    if weights is not None:
        weights = np.asarray(weights, dtype=np.float64)
        width = a.shape[-1]
        if weights.shape != (2 * width,):
            raise ValueError("Comparison weights must match both feature blocks.")
        value = (
            value + np.abs(a - b) @ weights[:width] + (a * b) @ weights[width:] + bias
        )
    return value


def probe_scores(probe, ids, vectors, weights=None, bias=0.0):
    """Apply the original triplet and condition switch formulas to any saved scorer."""
    expected = [r["id"] for r in probe["inputs"]]
    ids = list(map(str, ids))
    if len(set(ids)) != len(ids) or set(ids) != set(expected):
        raise ValueError("The saved vectors must cover the frozen probe exactly.")
    vectors = np.asarray(vectors, dtype=np.float64)
    if (
        vectors.shape[0] != len(ids)
        or not np.isfinite(vectors).all()
        or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=2e-5)
    ):
        raise ValueError("Probe vectors must be finite unit vectors.")
    lookup = dict(zip(ids, vectors, strict=True))

    def score(left, right):
        return float(pair_score(lookup[left], lookup[right], weights, bias))

    families = {}
    for family in probe["families"]:
        result = {"stratum": family["stratum"]}
        if family["stratum"] in ("explicit", "multiple"):
            grid = family["grid"]
            margins = [
                score(grid[j], grid[j ^ 1]) - score(grid[j], grid[j ^ 2])
                for j in range(4)
            ]
            result.update(margins=margins, margin=float(np.mean(margins)))
        if family["stratum"] == "multiple":
            grid = family["distractor_grid"]
            margins = [
                score(grid[j], grid[j ^ 2]) - score(grid[j], grid[j ^ 1])
                for j in range(4)
            ]
            result["C"] = (result["margin"] + float(np.mean(margins))) / 2
        if family["stratum"] == "implied":
            positive, negative = family["positive"], family["negative"]
            implicit = score(family["implicit"], positive) - score(
                family["implicit"], negative
            )
            explicit = score(family["explicit"], positive) - score(
                family["explicit"], negative
            )
            result.update(
                implicit_margin=implicit,
                explicit_margin=explicit,
                Q=explicit - implicit,
                correct_order=float(implicit > 0) + 0.5 * float(implicit == 0),
            )
        families[family["id"]] = result
    summary = {
        key: float(np.mean([v[key] for v in families.values() if key in v]))
        for key in ("implicit_margin", "explicit_margin", "Q", "C", "correct_order")
        if any(key in v for v in families.values())
    }
    summary["implied_families"] = sum(
        v["stratum"] == "implied" for v in families.values()
    )
    return {"summary": summary, "families": families}


def family_interval(differences, confidence=1 - 0.05 / 3, draws=10000):
    """Keep all comparison fits together while resampling whole probe families."""
    values = np.asarray(differences, dtype=np.float64)
    if values.ndim == 2:
        values = values.mean(axis=0)
    generator = np.random.default_rng(61028)
    means = values[generator.integers(len(values), size=(draws, len(values)))].mean(
        axis=1
    )
    tail = (1 - confidence) / 2
    return {
        "mean": float(values.mean()),
        "low": float(np.quantile(means, tail)),
        "high": float(np.quantile(means, 1 - tail)),
        "confidence": confidence,
        "draws": draws,
        "families": len(values),
    }


def replay_color(directory, color_root, models, inputs):

    probe = inputs["color_probe"]
    source = color_root / "results/seed7_P_B/embeddings.npz"
    if (
        digest(source)
        != inputs["color_metrics"]["state_artifacts"]["seed7_P_B"]["embeddings"]
    ):
        raise ValueError("The saved color embeddings changed.")
    with np.load(source, allow_pickle=False) as cached:
        ids, vectors = cached["ids"].copy(), cached["z"].copy()
    cosine = probe_scores(probe, ids, vectors)
    original = inputs["color_metrics"]["state_metrics"]["seed7_P_B"]
    for key in ("implicit_margin", "Q", "C"):
        if abs(cosine["summary"][key] - original[key]) > 1e-10:
            raise ValueError("The replay must reproduce the published cosine margins.")
    learned = {}
    for seed, fitted in models["seeds"].items():
        if (
            fitted["parent_model_sha256"]
            != "d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f"
        ):
            raise ValueError("Use comparisons trained on this exact frozen encoder.")
        state = fitted["comparisons"]["selected"]["parent"]["state"]
        weights = state["residual.weight"].numpy().reshape(-1)
        bias = float(state["residual.bias"].item())
        learned[seed] = replay = probe_scores(probe, ids, vectors, weights, bias)
        replay["selected_epoch"] = fitted["comparisons"]["selected"]["parent"]["epoch"]
    contrasts = {}
    for key in ("implicit_margin", "Q", "C"):
        selected = [k for k, v in cosine["families"].items() if key in v]
        values = [
            [arm["families"][f][key] - cosine["families"][f][key] for f in selected]
            for arm in learned.values()
        ]
        contrasts[key] = family_interval(values)
    result = {
        "encoder_sha256": "d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f",
        "embeddings_sha256": digest(source),
        "cosine": cosine,
        "learned": learned,
        "contrasts": contrasts,
        "scope": "Exploratory replay of three saved comparison fits on one fixed encoder. Intervals resample probe families and correct the three reported margin contrasts. Implied labels retain their pending human review.",
    }
    save(directory / "color-comparison.json", result)
    print(
        "COLOR_REPLAY_COMPLETE",
        json.dumps(
            {
                "cosine": cosine["summary"],
                "learned": {k: v["summary"] for k, v in learned.items()},
                "contrasts": contrasts,
            }
        ),
        flush=True,
    )
    return result


def error_records(rows, cosine, learned, fresh):
    """Preserve each original rating and record the exact squared error difference."""
    output = []
    for i, row in enumerate(rows):
        target = row["target"]
        a = np.asarray([values[i] for values in learned.values()])
        b = np.asarray([values[i] for values in fresh.values()])
        correction = a - cosine[i]
        encoder_error = target - cosine[i]
        gain = encoder_error**2 - float(np.mean((a - target) ** 2))
        if not np.isclose(
            gain,
            float(np.mean(2 * encoder_error * correction - correction**2)),
            atol=1e-12,
        ):
            raise ValueError("The residual error decomposition changed.")
        output.append(
            {
                **row,
                "cosine": float(cosine[i]),
                "learned": dict(zip(learned, a.tolist(), strict=True)),
                "fresh": dict(zip(fresh, b.tolist(), strict=True)),
                "learned_mean": float(a.mean()),
                "fresh_mean": float(b.mean()),
                "comparison_correction_mean": float(correction.mean()),
                "comparison_mse_gain": gain,
                "fresh_minus_learned_mse": float(
                    np.mean((b - target) ** 2) - np.mean((a - target) ** 2)
                ),
                "all_fresh_errors_larger": bool(
                    np.all((b - target) ** 2 > float(np.mean((a - target) ** 2)))
                ),
            }
        )
    return output


def audit_cases(root, directory, old):
    from csts_pilot.evidence_readout import metric_values

    rows = load(root / "csts_data/readout/test.json")
    fresh_bundle = load(
        root / "qwen_evidence_results/native_final_20261028/predictions.json"
    )
    expected = [r["row_id"] for r in rows]
    if old["row_ids"] != expected or fresh_bundle["row_ids"] != expected:
        raise ValueError("Audit predictions must retain the frozen row order.")
    cosine = np.asarray(old["seeds"]["7"]["A_parent"])
    learned = {s: np.asarray(v["parent_comparison"]) for s, v in old["seeds"].items()}
    fresh = {s: np.asarray(v) for s, v in fresh_bundle["seeds"].items()}
    records = error_records(rows, cosine, learned, fresh)
    cohorts = load(root / "datasets/csts-proposition-evidence-report-cohorts.json")
    mapping = cohorts["splits"]["test"]["condition_families"]
    for record in records:
        record["family"] = mapping.get(record["condition"], "unmapped")
        if re.search(cohorts["colour_regex"], record["condition"], re.IGNORECASE):
            record["family"] = "colour"
    groups = {}
    for name in (
        "quantity-and-count",
        "entity-and-object-type",
        "location-and-spatial-configuration",
        "colour",
    ):
        candidates = [r for r in records if r["family"] == name]
        selected, seen = [], set()
        for row in sorted(candidates, key=lambda r: -r["fresh_minus_learned_mse"]):
            if row["group_id"] in seen:
                continue
            selected.append(row)
            seen.add(row["group_id"])
            if len(selected) == 5:
                break
        groups[name] = selected
    for label, sign in (
        ("comparison_rescues", 1),
        ("comparison_harms", -1),
        ("fresh_rescues", -1),
    ):
        key = (
            "fresh_minus_learned_mse"
            if label == "fresh_rescues"
            else "comparison_mse_gain"
        )
        selected, seen = [], set()
        for row in sorted(records, key=lambda r: -sign * r[key]):
            if row["group_id"] in seen:
                continue
            selected.append(row)
            seen.add(row["group_id"])
            if len(selected) == 5:
                break
        groups[label] = selected
    result = {
        "rows": len(rows),
        "selection_rule": "Five largest signed error differences per listed group, with one row per source group. Original labels retained.",
        "groups": groups,
        "models": {
            "cosine": metric_values(rows, cosine),
            "learned": {s: metric_values(rows, p) for s, p in learned.items()},
            "fresh": {s: metric_values(rows, p) for s, p in fresh.items()},
        },
        "mean_comparison_correction": float(
            np.mean([r["comparison_correction_mean"] for r in records])
        ),
    }
    save(directory / "case-audit.json", result)
    save(directory / "row-errors.json", records)
    text = "# Sentence pair review\n\nPredictions use the original 1 to 5 rating scale. Each group contains five examples selected by the stated error rule, with one example per source group. The human ratings retain their frozen values.\n"
    for group, cases in groups.items():
        text += "\n## " + group.replace("-", " ").replace("_", " ").capitalize() + "\n"
        for row in cases:
            text += f"\n### {row['row_id']}: {row['condition']}\n\n**Sentence 1:** {row['sentence1']}\n\n**Sentence 2:** {row['sentence2']}\n\n| Human | A cosine | A learned mean | Fresh mean | Learned correction |\n| --- | --- | --- | --- | --- |\n"
            text += f"| {row['rating']:.1f} | {1 + 4 * row['cosine']:.3f} | {1 + 4 * row['learned_mean']:.3f} | {1 + 4 * row['fresh_mean']:.3f} | {4 * row['comparison_correction_mean']:+.3f} |\n"
    (directory / "cases.md").write_text(text)
    print("CASE_AUDIT_COMPLETE", len(records), flush=True)
    return result


def fit_control(root, directory, epochs=21):
    """Match the original seed 7 comparison's fixed 21 epoch CPU fitting budget."""
    import torch
    from csts_pilot.evidence_readout import SymmetricComparison, metric_values

    torch.set_num_threads(1)
    caches = {
        s: torch.load(
            directory / ("control_" + s + ".pt"), map_location="cpu", weights_only=True
        )
        for s in ("training", "validation", "test")
    }
    paths = {"training": "train", "validation": "validation", "test": "test"}
    rows = {
        s: load(root / ("csts_data/readout/" + name + ".json"))
        for s, name in paths.items()
    }
    for split, cache in caches.items():
        if cache["row_ids"] != [r["row_id"] for r in rows[split]] or cache[
            "rows_sha256"
        ] != digest(root / ("csts_data/readout/" + paths[split] + ".json")):
            raise ValueError("The control cache and frozen rating inputs must agree.")
    comparator = SymmetricComparison(4096).cpu()
    optimizer = torch.optim.AdamW(comparator.parameters(), lr=0.001, weight_decay=0.01)
    target = torch.tensor([r["target"] for r in rows["training"]], dtype=torch.float32)
    generator = torch.Generator().manual_seed(10007)

    def predict(split):
        cache = caches[split]
        with torch.inference_mode():
            return comparator(
                cache["vectors"][cache["left"]], cache["vectors"][cache["right"]]
            ).numpy()

    best = {
        "epoch": 0,
        "state": copy.deepcopy(comparator.state_dict()),
        "validation": metric_values(rows["validation"], predict("validation")),
    }
    history = []
    for epoch in range(1, epochs + 1):
        order = torch.randperm(len(target), generator=generator).tolist()
        for start in range(0, len(order), 32):
            ix = order[start : start + 32]
            cache = caches["training"]
            left, right = (
                [cache["left"][i] for i in ix],
                [cache["right"][i] for i in ix],
            )
            loss = torch.nn.functional.mse_loss(
                comparator(cache["vectors"][left], cache["vectors"][right]), target[ix]
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                comparator.parameters(), 1, error_if_nonfinite=True
            )
            optimizer.step()
        metrics = metric_values(rows["validation"], predict("validation"))
        history.append({"epoch": epoch, "validation": metrics})
        if metrics["spearman"] > best["validation"]["spearman"]:
            best = {
                "epoch": epoch,
                "state": copy.deepcopy(comparator.state_dict()),
                "validation": metrics,
            }
    last = copy.deepcopy(comparator.state_dict())
    comparator.load_state_dict(best["state"])
    values = predict("test")
    cache = caches["test"]
    cosine = (
        (cache["vectors"][cache["left"]] * cache["vectors"][cache["right"]])
        .sum(-1)
        .numpy()
    )
    torch.save(
        {
            "selected": best,
            "last_state": last,
            "optimizer": optimizer.state_dict(),
            "generator_state": generator.get_state(),
            "epochs": epochs,
            "seed": 7,
            "model_sha256": cache["model_sha256"],
            "history": history,
        },
        directory / "control-comparison.pt",
    )
    result = {
        "selected_epoch": best["epoch"],
        "epochs": epochs,
        "seed": 7,
        "encoder_updates": 0,
        "parameter_count": sum(p.numel() for p in comparator.parameters()),
        "validation": best["validation"],
        "test_cosine": metric_values(rows["test"], cosine),
        "test_learned": metric_values(rows["test"], values),
        "history": history,
        "test_predictions": values.tolist(),
        "cosine_predictions": cosine.tolist(),
        "rows_sha256": cache["rows_sha256"],
    }
    save(directory / "control-comparison.json", result)
    print(
        "CONTROL_COMPARISON_COMPLETE",
        json.dumps(
            {
                k: result[k]
                for k in ("selected_epoch", "epochs", "test_cosine", "test_learned")
            }
        ),
        flush=True,
    )
    return result


def write_report(directory, result, probe):
    color = result["color"]
    cosine = color["cosine"]["summary"]
    learned = {
        key: float(np.mean([v["summary"][key] for v in color["learned"].values()]))
        for key in cosine
    }
    text = "# What the learned comparison adds\n\nThe analysis reuses the saved existing encoder and its three comparisons, reviews individual rating errors, and fits one comparison to the frozen ratings control. The interaction uses comparison seed 7 for the original saved encoder pair.\n\n## Color replay\n\n| Measurement | Cosine | Learned mean | Change |\n| --- | --- | --- | --- |\n"
    for key, label in (
        ("implicit_margin", "Implied color margin"),
        ("Q", "Additional benefit from explicitly naming the color"),
        ("C", "Condition switch margin"),
        (
            "correct_order",
            "Fraction of implied families with the proposed matching color ranked first",
        ),
    ):
        text += f"| {label} | {cosine[key]:.6f} | {learned[key]:.6f} | {learned[key] - cosine[key]:+.6f} |\n"
    text += (
        "\n| Contrast | Change | 98.33 percent family interval |\n| --- | --- | --- |\n"
    )
    for key, interval in color["contrasts"].items():
        text += f"| {key} | {interval['mean']:+.6f} | [{interval['low']:+.6f}, {interval['high']:+.6f}] |\n"
    text += f"\nThe cosine replay ranks the proposed matching color first in {cosine['correct_order'] * 30:g} of 30 implied families. The three learned comparisons average {learned['correct_order'] * 30:g} of 30. Margins measure preference strength; the ordering column records changes in preference. The labels retain their original pending human review.\n"
    text += "\n## The missing comparison\n\nAll four cells use the same 2,431 frozen test examples. The new comparison trains 8,193 parameters on CPU and selects its first best validation epoch within the original seed 7 comparison's 21 epoch budget.\n\n| Encoder and score | Spearman | Normalized MSE |\n| --- | --- | --- |\n"
    labels = {
        "A_cosine": "Existing encoder, cosine",
        "A_learned": "Existing encoder, learned comparison",
        "R_cosine": "Ratings control, cosine",
        "R_learned": "Ratings control, learned comparison",
    }
    for key, metrics in result["metrics"].items():
        text += f"| {labels[key]} | {metrics['spearman']:.9f} | {metrics['mse_0_1']:.9f} |\n"
    interval = result["interaction"]
    text += f"\nThe interaction in Spearman is **{interval['value']:+.6f}**, with a 95 percent paired source group interval **[{interval['low']:+.6f}, {interval['high']:+.6f}]**. Positive values indicate a larger comparison gain on the existing encoder. Negative values indicate a larger gain on the ratings control.\n"
    text += f"\nThe new control comparison selects epoch **{result['control_fit']['selected_epoch']}**. Its encoder receives zero parameter updates.\n"
    text += "\n## Individual examples\n\nThe [sentence pair review](cases.md) shows the original human ratings and the scores for counting, object type, spatial relations, color and the largest changes produced by each scoring choice. The [row errors](row-errors.json) preserve the full 2,431 example analysis.\n"
    text += (
        "\n## Methods and scope\n\n"
        + result["scope"]
        + "\n\n[Methods](../../plans/csts-comparison-diagnostics-methods.md) · [Numeric results](analysis.json) · [Color details](color-comparison.json) · [Cloud receipts](cloud-receipts.json)\n"
    )
    (directory / "report.md").write_text(text)
    index = {x["id"]: x for x in probe["inputs"]}
    review = "# Review of implied color labels\n\nThe expected colors are the original proposed pragmatic labels. Human review remains pending. Scores below are margins of the matching anchor over the mismatching anchor for the saved existing encoder.\n\n| Family | Caption | Condition | Proposed color | Cosine margin | Learned mean margin |\n| --- | --- | --- | --- | --- | --- |\n"
    for family in probe["families"]:
        if family["stratum"] != "implied":
            continue
        identifier = family["id"]
        item = index[family["implicit"]]
        margin = float(
            np.mean(
                [
                    v["families"][identifier]["implicit_margin"]
                    for v in color["learned"].values()
                ]
            )
        )
        review += f"| {identifier} | {item['caption']} | {item['condition']} | {', '.join(item['pragmatic_colors'])} | {color['cosine']['families'][identifier]['implicit_margin']:.6f} | {margin:.6f} |\n"
    (directory / "implied-label-review.md").write_text(review)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--color-root", required=True, type=Path)
    args = parser.parse_args()
    import torch
    from csts_pilot.convergence_run import artifact_path
    from csts_pilot.evidence_readout import paired_intervals

    directory, root = args.output, args.root
    inputs = load(directory / "input-references.json")
    models = torch.load(
        directory / "original-comparisons.pt", map_location="cpu", weights_only=True
    )
    color = replay_color(directory, args.color_root, models, inputs)
    context = load(
        root / "qwen_evidence_results/native_final_20261028/report-context.json"
    )
    old = load(artifact_path(context, "archive", "holdout", "holdout.json"))
    audit = audit_cases(root, directory, old)
    while (
        not (directory / "capture-status.json").exists()
        or load(directory / "capture-status.json").get("status") != "complete"
    ):
        time.sleep(2)
    control = fit_control(root, directory)
    rows = load(root / "csts_data/readout/test.json")
    predictions = {
        "A_cosine": old["seeds"]["7"]["A_parent"],
        "A_learned": old["seeds"]["7"]["parent_comparison"],
        "R_cosine": control["cosine_predictions"],
        "R_learned": control["test_predictions"],
    }
    interaction = paired_intervals(
        rows,
        {"7": predictions},
        2000,
        61028,
        {"A_learned": 1, "A_cosine": -1, "R_learned": -1, "R_cosine": 1},
    )
    from csts_pilot.evidence_readout import metric_values

    metrics = {
        name: metric_values(rows, values) for name, values in predictions.items()
    }
    interaction["value"] = (
        metrics["A_learned"]["spearman"]
        - metrics["A_cosine"]["spearman"]
        - metrics["R_learned"]["spearman"]
        + metrics["R_cosine"]["spearman"]
    )
    result = {
        "status": "complete",
        "metrics": metrics,
        "interaction": interaction,
        "color": color,
        "case_audit": {k: v for k, v in audit.items() if k != "groups"},
        "control_fit": {
            k: v
            for k, v in control.items()
            if k not in ("test_predictions", "cosine_predictions")
        },
        "scope": "Exploratory analysis after prior test reporting. The interaction uses the original seed 7 encoder pair and comparison fitting seed 7. The new comparison uses the original seed 7 comparison's 21 epoch budget and first best validation selection. Encoder parameters remain fixed.",
    }
    save(directory / "analysis.json", result)
    save(
        directory / "interaction-predictions.json",
        {"row_ids": old["row_ids"], **predictions},
    )
    write_report(directory, result, inputs["color_probe"])
    print(
        "COMPARISON_ANALYSIS_COMPLETE",
        json.dumps({"metrics": metrics, "interaction": interaction}),
        flush=True,
    )


if __name__ == "__main__":
    main()
