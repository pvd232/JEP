"""Compare three declared step sizes for one epoch on retained training states.

This is a numerical diagnostic using validation only. It keeps the original
study outputs intact and records every declared learning rate.
"""

import argparse
import fcntl
import hashlib
import json
import sys
from pathlib import Path

import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csts_pilot.evidence_readout import (
    clone_state,
    matched_initial_heads,
    pack_batch,
    selection_loss,
    validate_cache,
)
from scripts.diagnose_evidence_readout import audit_head


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with Path("/tmp/jep-gpu.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_probe(args)


def run_probe(args):
    torch.set_num_threads(4)
    summary = json.loads(args.summary.read_text())
    runs = {r["name"]: Path(r["path"]).parent for r in summary["runs"]}
    caches, rows = {}, {}
    for split in ("training", "validation"):
        path = (
            runs[f"extract_{split}_proposition_final"]
            / "artifacts/extract/cache/cache.pt"
        )
        caches[split] = torch.load(
            path, map_location="cpu", weights_only=True, mmap=True
        )
        rowpath = (
            args.root
            / f"csts_data/readout/{'train' if split == 'training' else split}.json"
        )
        rows[split] = json.loads(rowpath.read_text())
        validate_cache(caches[split], rows[split])
    seed, batch_size = 7, 32
    order = torch.randperm(
        len(rows["training"]), generator=torch.Generator().manual_seed(seed)
    ).tolist()
    target = torch.tensor([r["target"] for r in rows["training"]], device="cuda")
    updates = (len(order) + batch_size - 1) // batch_size
    output = {
        "status": "running",
        "role": "one epoch numerical probe, training and validation only",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "diagnostic_script_sha256": hashlib.sha256(
            (args.root / "scripts/diagnose_evidence_readout.py").read_bytes()
        ).hexdigest(),
        "study_summary_sha256": hashlib.sha256(args.summary.read_bytes()).hexdigest(),
        "seed": seed,
        "learning_rates": [0.001, 0.0001, 0.00001],
        "batch_size": batch_size,
        "epochs": 1,
        "updates_per_arm": updates,
        "weight_decay": 0.01,
        "evidence_weight": 0.1,
        "gradient_clip": 1.0,
        "order_sha256": hashlib.sha256(
            json.dumps(order, separators=(",", ":")).encode()
        ).hexdigest(),
        "results": {},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for rate in output["learning_rates"]:
        heads = {
            a: h.cuda()
            for a, h in matched_initial_heads(
                caches["training"]["embedding_dimension"], 128, seed
            ).items()
        }
        optimizers = {
            a: torch.optim.AdamW(h.parameters(), lr=rate, weight_decay=0.01)
            for a, h in heads.items()
        }
        measurements = []

        def snapshot(step, heads=heads, measurements=measurements, rate=rate):
            record = {
                "step": step,
                "arms": {
                    a: audit_head(h, caches["validation"], rows["validation"], "cuda")[
                        0
                    ]
                    for a, h in heads.items()
                },
            }
            measurements.append(record)
            print(
                json.dumps(
                    {
                        "rate": rate,
                        "step": step,
                        "validation": {
                            a: v["scores"] for a, v in record["arms"].items()
                        },
                    }
                ),
                flush=True,
            )

        snapshot(0)
        for step, start in enumerate(range(0, len(order), batch_size), start=1):
            ix = order[start : start + batch_size]
            positions = [caches["training"]["left"][i] for i in ix] + [
                caches["training"]["right"][i] for i in ix
            ]
            h, u, mask, gold = pack_batch(caches["training"], positions, "cuda")
            for arm, head in heads.items():
                head.train()
                z, logits, _ = head(h, u, mask)
                rating = F.mse_loss((z[: len(ix)] * z[len(ix) :]).sum(1), target[ix])
                evidence, _ = selection_loss(logits, mask, gold)
                loss = rating + (0.1 * evidence if arm == "evidence" else 0)
                optimizers[arm].zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    head.parameters(), 1.0, error_if_nonfinite=True
                )
                optimizers[arm].step()
            if step in {10, 50, updates}:
                snapshot(step)
        output["results"][str(rate)] = measurements
        torch.save(
            {
                "states": {a: clone_state(h) for a, h in heads.items()},
                "optimizers": {a: o.state_dict() for a, o in optimizers.items()},
                "config": {k: v for k, v in output.items() if k != "results"},
                "learning_rate": rate,
            },
            args.output.with_name(f"step_probe_{rate}.pt"),
        )
        args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    output["status"] = "complete"
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
