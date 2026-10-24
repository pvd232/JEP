"""Measure real evidence gradients, loss reduction and memory before the full comparison."""

import argparse
import json
import subprocess
import time
from pathlib import Path

import torch

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    load_backbone,
    load_tokenizer,
    state_digest,
    trainable_state,
)
from csts_pilot.convergence import file_sha256, reset_rng, synchronize, write_json
from csts_pilot.evidence_controls import checked_cache
from csts_pilot.qwen_evidence import (
    QwenEvidenceConfig,
    answer_loss_sum,
    evidence_batch,
    evidence_tokens,
    load_head,
)
from jep_pilot.loaders import load_json


def preflight(root: Path, settings: dict, output: Path) -> dict:
    """Fit a tiny training-only batch; do not read validation or test labels."""
    processes = subprocess.check_output(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"], text=True
    ).strip()
    if processes:
        raise RuntimeError("Another CUDA process is active; preserve its job.")
    for item in (settings["answers"], settings["head"], settings["splits"]["training"]):
        if file_sha256(root / item["path"]) != item["sha256"]:
            raise ValueError("Preflight input identity changed.")
    config = QwenEvidenceConfig.model_validate(
        {
            **settings["encoder"],
            **settings["training"],
            **settings["phases"]["pretrain"],
            "kind": "lora",
            "arm": "evidence",
            "phase": "pretrain",
            "training_sha256": settings["splits"]["training"]["sha256"],
            "validation_sha256": settings["splits"]["validation"]["sha256"],
            "prepared_sha256": "0" * 64,
            "head_sha256": settings["head"]["sha256"],
        }
    )
    rows = load_json(root / settings["splits"]["training"]["path"])
    records = checked_cache(root / settings["answers"]["path"])
    mapping = {key: value["answer"] for key, value in records.items() if value["valid"]}
    chosen = [
        r
        for r in rows
        if all(
            answer_id(r[s], r["condition"]) in mapping
            for s in ("sentence1", "sentence2")
        )
    ][:2]
    if len(chosen) != 2:
        raise ValueError(
            "Insufficient fully supported training pairs for the preflight."
        )
    reset_rng(config.seed)
    fit = config.fit_config()
    tokenizer = load_tokenizer(fit)
    model = load_backbone(fit, adapters=fit)
    head = load_head(root / settings["head"]["path"], config)
    sequences = evidence_tokens(
        chosen, mapping, tokenizer, fit, settings["max_answer_tokens"]
    )
    batch, labels = evidence_batch(chosen, sequences, tokenizer, fit)
    params = [p for p in model.parameters() if p.requires_grad]
    initial_sha = state_digest(trainable_state(model))
    optimizer = torch.optim.AdamW(
        params, lr=config.learning_rate, weight_decay=config.weight_decay
    )

    def objective():
        with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
            return answer_loss_sum(
                model(**batch).last_hidden_state, labels, head
            ) / len(labels)

    model.eval()
    with torch.no_grad():
        before = float(objective())
    times, norms = [], []
    torch.cuda.reset_peak_memory_stats()
    for _ in range(12):
        model.train()
        synchronize("cuda")
        started = time.monotonic()
        optimizer.zero_grad(set_to_none=True)
        loss = objective()
        if not torch.isfinite(loss):
            raise ValueError("Nonfinite evidence preflight loss.")
        loss.backward()
        norm = float(
            torch.nn.utils.clip_grad_norm_(params, 1.0, error_if_nonfinite=True)
        )
        norms.append(norm)
        if norm <= 0 or head.weight.grad is not None:
            raise ValueError(
                "Evidence gradients must reach only the shared trainable adapters."
            )
        optimizer.step()
        synchronize("cuda")
        times.append(time.monotonic() - started)
    model.eval()
    with torch.no_grad():
        after = float(objective())
    # Stress the longest accepted training sequence at the declared number of
    # passages, so a short sanity example cannot hide a later memory failure.
    all_sequences = evidence_tokens(
        rows, mapping, tokenizer, fit, settings["max_answer_tokens"]
    )
    longest = max(all_sequences, key=lambda key: len(all_sequences[key][0]))
    long_pair = next(
        r
        for r in rows
        if any(
            answer_id(r[side], r["condition"]) == longest
            for side in ("sentence1", "sentence2")
        )
    )
    long_key = next(
        side
        for side in ("sentence1", "sentence2")
        if answer_id(long_pair[side], long_pair["condition"]) == longest
    )
    stress_row = {
        **long_pair,
        "sentence1": long_pair[long_key],
        "sentence2": long_pair[long_key],
    }
    stress_batch, stress_labels = evidence_batch(
        [stress_row] * config.microbatch_size, all_sequences, tokenizer, fit
    )
    optimizer.zero_grad(set_to_none=True)
    model.train()
    with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
        stress_loss = answer_loss_sum(
            model(**stress_batch).last_hidden_state, stress_labels, head
        ) / len(stress_labels)
    stress_loss.backward()
    synchronize("cuda")
    del stress_loss
    peak = torch.cuda.max_memory_allocated()
    if not after < before * 0.99 or initial_sha == state_digest(trainable_state(model)):
        raise ValueError(
            "Evidence learning did not pass the declared one-percent loss-reduction check."
        )
    total = torch.cuda.get_device_properties(0).total_memory
    if peak > total * 0.94:
        raise ValueError("Insufficient CUDA memory margin for the reviewed microbatch.")
    result = {
        "status": "passed",
        "training_pairs": [r["row_id"] for r in chosen],
        "validation_or_test_labels_used": False,
        "loss_before": before,
        "loss_after": after,
        "gradient_norms": norms,
        "steady_microbatch_seconds": sum(times[2:]) / len(times[2:]),
        "peak_cuda_allocated_bytes": peak,
        "cuda_total_bytes": total,
        "longest_training_sequence_tokens": len(all_sequences[longest][0]),
        "trainable_parameters": sum(p.numel() for p in params),
        "frozen_head_sha256": config.head_sha256,
        "settings_sha256": file_sha256(root / "configs/csts-qwen-evidence.json"),
        "scope": "Training-only feasibility check; these adapters are discarded before the experiment.",
    }
    write_json(output, result)
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    preflight(
        args.root, load_json(args.root / "configs/csts-qwen-evidence.json"), args.output
    )
