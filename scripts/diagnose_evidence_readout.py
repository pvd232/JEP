"""Inspect retained readout artifacts using training, validation and fixed edits.

Run with the original experiment environment. This command reads existing
artifacts and writes aggregate diagnostics; it leaves selected models intact.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csts_pilot.evidence_readout import (
    EvidenceReadout,
    gradient_diagnostic,
    matched_initial_heads,
    metric_values,
    pack_batch,
    selection_loss,
    validate_cache,
)


def quantiles(values):
    return np.quantile(values, [0, 0.1, 0.5, 0.9, 1]).tolist()


def position_summary(weights):
    """Summarize actual sentence positions, respecting each sentence's length."""
    if not weights or any(w.ndim != 1 or not len(w) for w in weights):
        raise ValueError("Expected a weight vector for every sentence occurrence.")
    if any(not torch.isfinite(w).all() or (w < 0).any() for w in weights):
        raise ValueError("Expected finite nonnegative weights.")
    if any(not torch.isclose(w.sum(), w.new_tensor(1.0), atol=1e-5) for w in weights):
        raise ValueError("Sentence weights must sum to one.")
    top = [int(w.argmax()) for w in weights]
    relative = [i / max(len(w) - 1, 1) for i, w in zip(top, weights, strict=True)]
    return {
        "occurrences": len(weights),
        "top_token_first_fraction": float(np.mean([i == 0 for i in top])),
        "top_token_last_fraction": float(
            np.mean([i == len(w) - 1 for i, w in zip(top, weights, strict=True)])
        ),
        "top_position_deciles": np.histogram(relative, np.linspace(0, 1, 11))[
            0
        ].tolist(),
        "mean_first_token_mass": float(np.mean([float(w[0]) for w in weights])),
        "mean_last_token_mass": float(np.mean([float(w[-1]) for w in weights])),
        "mean_entropy": float(
            np.mean([float(-(w * w.clamp_min(1e-30).log()).sum()) for w in weights])
        ),
        "top_mass_quantiles": quantiles([float(w.max()) for w in weights]),
        "mass_over_099_fraction": float(
            np.mean([float(w.max()) > 0.99 for w in weights])
        ),
    }


def score_vectors(vectors, cache, rows, subset=None):
    left, right = cache["left"], cache["right"]
    scores = (vectors[left] * vectors[right]).sum(1).numpy()
    ix = np.arange(len(rows)) if subset is None else np.asarray(subset, dtype=int)
    result = metric_values([rows[i] for i in ix], scores[ix])
    result["prediction_quantiles"] = quantiles(scores[ix])
    return result


def simple_vectors(cache):
    """Compare pooling rules on exactly the same retained token states."""
    values = {
        name: [] for name in ("first", "last", "mean", "mean_unit_tokens", "quotation")
    }
    for a, b in zip(cache["pointers"][:-1], cache["pointers"][1:], strict=True):
        h = cache["token_values"][a:b].float()
        values["first"].append(h[0])
        values["last"].append(h[-1])
        values["mean"].append(h.mean(0))
        values["mean_unit_tokens"].append(F.normalize(h, dim=1).mean(0))
        target = cache["span_targets"][a:b]
        values["quotation"].append((h * target[:, None]).sum(0))
    result = {name: F.normalize(torch.stack(v), dim=1) for name, v in values.items()}
    result["A"] = cache["eod_vectors"].float()
    return result


def audit_head(head, cache, rows, device):
    head.eval()
    vectors, weights, nulls, spreads, qnorms, knorms, logit_gradient = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    ce_total, units_total, hits, target_mass = 0.0, 0, 0, 0.0
    with torch.no_grad():
        for start in range(0, len(cache["keys"]), 64):
            ix = list(range(start, min(start + 64, len(cache["keys"]))))
            h, u, mask, gold = pack_batch(cache, ix, device)
            z, logits, probabilities = head(h, u, mask)
            source = logits[:, 1:].softmax(1)
            vectors.append(z.cpu())
            q = head.query(F.layer_norm(u, (head.input_dim,)))
            k = head.key(F.layer_norm(h, (head.input_dim,)))
            qnorms.extend(q.norm(dim=1).cpu().tolist())
            knorms.extend(k.norm(dim=2)[mask].cpu().tolist())
            nulls.extend(probabilities[:, 0].cpu().tolist())
            for j, i in enumerate(ix):
                n = cache["pointers"][i + 1] - cache["pointers"][i]
                w = source[j, :n].cpu()
                weights.append(w)
                spreads.append(
                    float(logits[j, 1 : n + 1].max() - logits[j, 1 : n + 1].min())
                )
                # This bounds the largest derivative of an individual softmax weight.
                logit_gradient.append(float((w * (1 - w)).max()))
            loss, units = selection_loss(logits, mask, gold)
            ce_total += float(loss) * units
            units_total += units
            supervised = gold.sum(1) > 0
            hits += int(
                (
                    gold.gather(1, logits.argmax(1)[:, None]).squeeze(1)[supervised] > 0
                ).sum()
            )
            target_mass += float((probabilities * (gold > 0)).sum(1)[supervised].sum())
    vectors = torch.cat(vectors)
    diagnostics = {
        **position_summary(weights),
        "scores": score_vectors(vectors, cache, rows),
        "query_norm_quantiles": quantiles(qnorms),
        "key_norm_quantiles": quantiles(knorms),
        "source_logit_range_quantiles": quantiles(spreads),
        "largest_softmax_diagonal_derivative_quantiles": quantiles(logit_gradient),
        "mean_null_probability": float(np.mean(nulls)),
        "teacher_units": units_total,
        "teacher_ce": ce_total / units_total if units_total else None,
        "teacher_top1_agreement": hits / units_total if units_total else None,
        "teacher_support_mass": target_mass / units_total if units_total else None,
        "query_weight_norm": float(head.query.weight.detach().norm()),
        "key_weight_norm": float(head.key.weight.detach().norm()),
    }
    return diagnostics, weights, vectors


def gradient_probe(head, cache, rows, seed, device):
    order = torch.randperm(
        len(rows), generator=torch.Generator().manual_seed(seed)
    ).tolist()[:32]
    positions = [cache["left"][i] for i in order] + [cache["right"][i] for i in order]
    h, u, mask, gold = pack_batch(cache, positions, device)
    z, logits, _ = head(h, u, mask)
    target = torch.tensor([rows[i]["target"] for i in order], device=device)
    rating = F.mse_loss((z[: len(order)] * z[len(order) :]).sum(1), target)
    evidence, _ = selection_loss(logits, mask, gold)
    return gradient_diagnostic(head, rating, evidence, 0.1)


def edit_tokens(cache, rows, weights):
    by_case = {}
    for i, row in enumerate(rows):
        by_case.setdefault(row["case"], {})[row["edit"]] = i
    results = []
    for case, cases in by_case.items():
        base = cache["left"][cases["base"]]
        edit = cache["left"][cases["relevant"]]
        ib, ie = int(weights[base].argmax()), int(weights[edit].argmax())
        a, b = cache["pointers"][base], cache["pointers"][edit]
        hb, he = (
            cache["token_values"][a + ib].float(),
            cache["token_values"][b + ie].float(),
        )
        results.append(
            {
                "case": case,
                "base_top_position": ib + 1,
                "relevant_top_position": ie + 1,
                "base_top_mass": float(weights[base].max()),
                "relevant_top_mass": float(weights[edit].max()),
                "selected_state_exactly_equal": bool(torch.equal(hb, he)),
                "selected_state_cosine": float(F.cosine_similarity(hb, he, dim=0)),
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda", choices=("cpu", "cuda"))
    args = parser.parse_args()
    torch.set_num_threads(4)
    summary = json.loads(args.summary.read_text())
    runs = {r["name"]: Path(r["path"]).parent for r in summary["runs"]}
    report = {
        "status": "running",
        "analysis_script_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "study_source": summary.get("source"),
        "study_summary_sha256": hashlib.sha256(args.summary.read_bytes()).hexdigest(),
        "role": "exploratory diagnosis of the completed study",
        "splits": {},
        "seeds": {},
    }
    caches, rows = {}, {}
    for split in ("training", "validation", "interventions"):
        path = (
            runs[f"extract_{split}_proposition_final"]
            / "artifacts/extract/cache/cache.pt"
        )
        caches[split] = torch.load(
            path, map_location="cpu", weights_only=True, mmap=True
        )
        rowpath = args.root / (
            "configs/csts-readout-interventions.json"
            if split == "interventions"
            else f"csts_data/readout/{'train' if split == 'training' else split}.json"
        )
        rows[split] = json.loads(rowpath.read_text())
        validate_cache(caches[split], rows[split])
        vectors = simple_vectors(caches[split])
        report["splits"][split] = {
            "rows": len(rows[split]),
            "cache_rows_sha256": caches[split]["rows_sha256"],
            "parent_model_sha256": caches[split]["model_sha256"],
            "pooling": {
                name: score_vectors(v, caches[split], rows[split])
                for name, v in vectors.items()
                if name != "quotation"
            },
        }
        if split == "training":
            cache = caches[split]
            answered = [
                float(cache["span_targets"][a:b].sum()) > 0
                for a, b in zip(
                    cache["pointers"][:-1], cache["pointers"][1:], strict=True
                )
            ]
            subset = [
                i
                for i, (l, r) in enumerate(
                    zip(cache["left"], cache["right"], strict=True)
                )
                if answered[l] and answered[r]
            ]
            report["training_teacher_pooling"] = {
                name: score_vectors(vectors[name], cache, rows[split], subset)
                for name in ("A", "mean", "quotation")
            }
        print(json.dumps({"event": "pooling_complete", "split": split}), flush=True)
    for seed in (7, 8, 9):
        path = runs[f"fit_{seed}"] / "artifacts/fit/model/model.pt"
        saved = torch.load(path, map_location="cpu", weights_only=True)
        trace = json.loads(
            (runs[f"fit_{seed}"] / "artifacts/fit/trace/trace.json").read_text()
        )
        result = {
            "selected_epoch": trace["selected_epoch"],
            "epochs": trace["epochs"],
            "gradient_diagnostics": trace["gradient_diagnostics"],
            "arms": {},
        }
        initial = matched_initial_heads(
            saved["embedding_dimension"], saved["config"]["query_dim"], seed
        )["ratings"].to(args.device)
        result["initial_validation"] = audit_head(
            initial, caches["validation"], rows["validation"], args.device
        )[0]
        result["initial_gradient_probe"] = gradient_probe(
            initial, caches["training"], rows["training"], seed, args.device
        )
        for arm in ("ratings", "evidence"):
            head = EvidenceReadout(
                saved["embedding_dimension"], saved["config"]["query_dim"]
            ).to(args.device)
            head.load_state_dict(saved["selected"][arm]["state"], strict=True)
            value = {
                "gradient_probe": gradient_probe(
                    head, caches["training"], rows["training"], seed, args.device
                )
            }
            for split in ("training", "validation", "interventions"):
                diagnostics, weights, _ = audit_head(
                    head, caches[split], rows[split], args.device
                )
                value[split] = diagnostics
                if split == "interventions":
                    value["selected_tokens_under_relevant_edits"] = edit_tokens(
                        caches[split], rows[split], weights
                    )
            result["arms"][arm] = value
            print(
                json.dumps({"event": "head_complete", "seed": seed, "arm": arm}),
                flush=True,
            )
        report["seeds"][str(seed)] = result
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    report["status"] = "complete"
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps({"event": "diagnosis_complete", "output": str(args.output)}),
        flush=True,
    )


if __name__ == "__main__":
    main()
