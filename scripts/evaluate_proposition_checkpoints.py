"""Measure held-out answer loss and preserve free generations from frozen checkpoints."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EOD,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    token_sequences,
)
from csts_pilot.qwen_evidence import (
    QwenEvidenceConfig,
    answer_loss_sum,
    evidence_tokens,
    load_head,
)


def sha(path: Path) -> str:
    """Bind each reusable measurement to its exact input bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, obj: dict) -> None:
    """Commit one completed measurement atomically before any downstream processing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    temporary.replace(path)


@torch.inference_mode()
def generate(model, head, tokenizer, config, item: dict) -> dict:
    """Greedily decode after the identical embedding prefix, stopping at EOD or 64 tokens."""
    prefix = token_sequences(tokenizer, [(item["condition"], item["passage"])], config)[
        0
    ]
    output = []
    eod = tokenizer.get_vocab()[EOD]
    ended = False
    for _ in range(64):
        ids = torch.tensor([prefix + output], device=config.device)
        hidden = model(
            input_ids=ids, attention_mask=torch.ones_like(ids)
        ).last_hidden_state
        token = int(head(hidden[:, -1]).float().argmax(-1).item())
        if token == eod:
            ended = True
            break
        output.append(token)
    return {
        "answer": tokenizer.decode(output, skip_special_tokens=True),
        "tokens": len(output),
        "ended_at_eod": ended,
    }


def measure_one(
    model, head, tokenizer, fit, item, sequence, binding, destination, wants_generation
):
    """Persist the loss before generation so a generation failure cannot repeat a completed forward."""
    loss_path = destination / (item["id"] + ".json")
    generation_path = destination / (item["id"] + "_generation.json")
    if not loss_path.exists():
        ids, labels = sequence
        batch = pad_sequences(tokenizer, [ids], fit)
        with torch.inference_mode():
            hidden = model(**batch).last_hidden_state
            loss = float(
                answer_loss_sum(hidden, torch.tensor([labels], device=fit.device), head)
            )
        save(
            loss_path, {**binding, "id": item["id"], "mean_answer_cross_entropy": loss}
        )
    if wants_generation and not generation_path.exists():
        generated = generate(model, head, tokenizer, fit, item)
        save(generation_path, {**binding, "id": item["id"], "generated": generated})


def evaluate(job: dict) -> None:
    """Reuse independently saved per-input forwards and compare epochs on identical references."""
    refs_path = Path(job["references"])
    refs = json.loads(refs_path.read_text())
    items = json.loads(Path(job["inputs"]).read_text())
    reference = {r["id"]: r for r in refs if r["status"] == "answered"}
    output = Path(job["output"])
    binding = {
        "references_sha256": sha(refs_path),
        "inputs_sha256": sha(Path(job["inputs"])),
        "evaluator_sha256": sha(Path(__file__)),
        "head_sha256": sha(Path(job["head"])),
    }
    for checkpoint in job["checkpoints"]:
        model_path = Path(checkpoint["model"])
        saved = torch.load(model_path, map_location="cpu", weights_only=True)
        if saved["epoch"] != checkpoint["epoch"]:
            raise ValueError(
                "Checkpoint is not the declared completed proposition-writing epoch."
            )
        config = QwenEvidenceConfig.model_validate(
            json.loads(Path(checkpoint["trace"]).read_text())["config"]
        )
        if (
            config.arm != "evidence"
            or config.phase != "pretrain"
            or binding["head_sha256"] != config.head_sha256
        ):
            raise ValueError(
                "Evaluation requires the original proposition checkpoint and vocabulary head."
            )
        fit = config.fit_config()
        fit = fit.model_copy(update={"device": "cuda"})
        tokenizer = load_tokenizer(fit)
        accepted = [
            r
            for r in items
            if r["id"] in reference
            and 0
            < len(
                tokenizer(reference[r["id"]]["answer"], add_special_tokens=False)[
                    "input_ids"
                ]
            )
            + 1
            <= config.max_answer_tokens
        ]
        if not accepted:
            raise ValueError("No held-out answers fit the frozen token limit.")
        facts = {
            r["id"]
            for r in sorted(
                accepted,
                key=lambda r: hashlib.sha256(
                    ("factual-validation-v1:" + r["id"]).encode()
                ).hexdigest(),
            )[:64]
        }
        row_binding = {
            **binding,
            "checkpoint_sha256": sha(model_path),
            "epoch": saved["epoch"],
        }
        destination = output / ("epoch_" + str(saved["epoch"]))
        manifest = destination / "binding.json"
        if manifest.exists() and json.loads(manifest.read_text()) != row_binding:
            raise ValueError(
                "Saved measurement inputs changed; refusing to repeat forwards."
            )
        save(manifest, row_binding)
        pending = [
            r
            for r in accepted
            if not (destination / (r["id"] + ".json")).exists()
            or (
                r["id"] in facts
                and not (destination / (r["id"] + "_generation.json")).exists()
            )
        ]
        if pending:
            model = load_backbone(fit, fit)
            restore_parameters(model, saved["state"])
            model.eval()
            head = load_head(Path(job["head"]), config)
            head.eval()
            rows = [
                {
                    "condition": r["condition"],
                    "sentence1": r["passage"],
                    "sentence2": r["passage"],
                }
                for r in accepted
            ]
            mapping = {
                answer_id(r["passage"], r["condition"]): reference[r["id"]]["answer"]
                for r in accepted
            }
            sequences = evidence_tokens(
                rows, mapping, tokenizer, fit, config.max_answer_tokens
            )
            for item in pending:
                key = answer_id(item["passage"], item["condition"])
                measure_one(
                    model,
                    head,
                    tokenizer,
                    fit,
                    item,
                    sequences[key],
                    row_binding,
                    destination,
                    item["id"] in facts,
                )
            del model, head
            torch.cuda.empty_cache()
        measurements = [
            json.loads((destination / (r["id"] + ".json")).read_text())
            for r in accepted
        ]
        if any(any(m[k] != v for k, v in row_binding.items()) for m in measurements):
            raise ValueError("A cached forward belongs to different evaluation inputs.")
        candidates = [
            {
                **r,
                **json.loads(
                    (destination / (r["id"] + "_generation.json")).read_text()
                )["generated"],
            }
            for r in accepted
            if r["id"] in facts
        ]
        result = {
            **row_binding,
            "n": len(accepted),
            "sample_inputs": len(items),
            "excluded_nonanswered_or_over_token_limit": len(items) - len(accepted),
            "mean_answer_cross_entropy": sum(
                r["mean_answer_cross_entropy"] for r in measurements
            )
            / len(measurements),
            "generated_candidates": candidates,
            "status": "complete",
        }
        save(output / ("epoch_" + str(saved["epoch"]) + "_result.json"), result)
    save(
        output / "status.json",
        {"status": "complete", "epochs": [c["epoch"] for c in job["checkpoints"]]},
    )


def main() -> None:
    """Evaluate only the explicitly supplied job while its caller owns the GPU lease."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    args = parser.parse_args()
    job = json.loads(args.job.read_text())
    try:
        evaluate(job)
    except Exception as exc:
        save(
            Path(job["output"]) / "status.json",
            {
                "status": "failed",
                "error": str(exc),
                "completed_measurements_preserved": True,
            },
        )
        raise


if __name__ == "__main__":
    main()
