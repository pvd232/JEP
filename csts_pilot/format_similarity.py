"""Score matched evidence formats with the saved, frozen proposition model."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence


ARMS = ("raw", "propositions", "json", "python")
EVIDENCE_ARMS = ARMS[1:]
MODEL_ID = "Qwen/Qwen3-Embedding-8B"
REVISION = "c90816d848505624c2434128dfc61132162a0ee9"
CHECKPOINT_SHA256 = "d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f"
PROMPT = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
EOD = "<|endoftext|>"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_extra(value: Any) -> Any:
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=lambda item: json.dumps(item, sort_keys=True, default=_json_extra))
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, sort_keys=True, indent=2, allow_nan=False, default=_json_extra) + "\n"
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(payload)
    temporary.replace(path)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_inputs(inputs: dict[str, Any]) -> None:
    """Require the fixed model contract and complete, label-free source joins."""
    protocol = inputs["protocol"]
    expected = {"model_id": MODEL_ID, "revision": REVISION, "max_length": 160,
                "checkpoint_sha256": CHECKPOINT_SHA256, "prompt": PROMPT}
    if any(protocol.get(key) != value for key, value in expected.items()) or protocol.get("eod", EOD) != EOD:
        raise ValueError("The saved model, prompt and 160-token contract must remain fixed.")
    if any(key in inputs for key in ("labels", "ratings", "targets", "direct")):
        raise ValueError("GPU inputs must not contain evaluation labels or direct scores.")
    sources, pairs = inputs["sources"], inputs["pairs"]
    source_ids = [source["id"] for source in sources]
    pair_ids = [pair["id"] for pair in pairs]
    if not sources or not pairs or len(source_ids) != len(set(source_ids)) or len(pair_ids) != len(set(pair_ids)):
        raise ValueError("Source and pair IDs must be nonempty and unique.")
    if any(not _text(identity) for identity in source_ids + pair_ids):
        raise ValueError("Source and pair IDs must be nonempty strings.")
    by_source = {source["id"]: source for source in sources}
    for source in sources:
        if not _text(source["passage"]) or not _text(source["condition"]):
            raise ValueError("Original source text and condition are required.")
        if set(source["arms"]) != set(EVIDENCE_ARMS):
            raise ValueError("Every source requires all three evidence arms.")
        for arm in EVIDENCE_ARMS:
            record = source["arms"][arm]
            failure = record.get("failure")
            if failure is not None and not _text(failure):
                raise ValueError("A failed source requires a nonempty failure reason.")
            if record.get("status") not in {"answered", "not_specified", "ambiguous"} and failure is None:
                raise ValueError("A source needs a valid status or an explicit failure.")
            if not isinstance(record.get("text"), str):
                raise ValueError("Rendered evidence must be a string, including for failures.")
    for pair in pairs:
        if any(key in pair for key in ("rating", "target", "label")):
            raise ValueError("Pair records must remain label-free.")
        if not _text(pair["group_id"]):
            raise ValueError("Every pair requires its connected group.")
        if pair["source_a"] not in by_source or pair["source_b"] not in by_source:
            raise ValueError("Unknown source in a comparison.")
        if by_source[pair["source_a"]]["condition"] != by_source[pair["source_b"]]["condition"]:
            raise ValueError("Both comparison sources must share a condition.")


def effective_inputs(inputs: dict[str, Any], tokenizer: Any):
    """Freeze per-side fallback before inference; inspect full sequences without truncation."""
    validate_inputs(inputs)
    eod = tokenizer.get_vocab().get(EOD)
    if eod is None:
        raise ValueError("The pinned tokenizer lacks the required EOD token.")
    candidates = {(s["condition"], s["passage"]) for s in inputs["sources"]}
    for source in inputs["sources"]:
        candidates.update((source["condition"], record["text"]) for record in source["arms"].values()
                          if not record.get("failure") and record.get("status") == "answered" and _text(record["text"]))
    keys = sorted(candidates)
    encoded = tokenizer([PROMPT.format(condition=c, passage=p) for c, p in keys],
                        padding=False, truncation=False, add_special_tokens=False)
    sequences = {key: [*ids, eod] for key, ids in zip(keys, encoded["input_ids"], strict=True)}
    texts = {arm: {} for arm in ARMS}
    reasons = {arm: {} for arm in ARMS}
    retained = []
    for source in inputs["sources"]:
        identity, condition, raw = source["id"], source["condition"], source["passage"]
        if len(sequences[condition, raw]) > 160:
            raise ValueError("An original passage exceeds the saved model's token ceiling.")
        for arm in ARMS:
            reason, text, requested_length = None, raw, None
            if arm != "raw":
                record = source["arms"][arm]
                if record.get("failure"):
                    reason = "failure:" + record["failure"]
                elif record["status"] != "answered":
                    reason = record["status"]
                elif not _text(record["text"]):
                    reason = "empty_evidence"
                else:
                    requested_length = len(sequences[condition, record["text"]])
                    if requested_length > 160:
                        reason = "token_overflow"
                    else:
                        text = record["text"]
            texts[arm][identity], reasons[arm][identity] = text, reason
            retained.append({"arm": arm, "source_id": identity, "condition": condition,
                             "text": text, "fallback_reason": reason,
                             "requested_token_length": requested_length,
                             "input_ids": sequences[condition, text]})
    return texts, reasons, retained


def inference_rows(inputs: dict[str, Any], texts: dict[str, str]) -> list[dict[str, Any]]:
    """Supply constant shape-validation placeholders, never evaluation ratings."""
    sources = {source["id"]: source for source in inputs["sources"]}
    return [{"row_id": pair["id"], "pair_id": pair["id"], "group_id": pair["group_id"],
             "condition": sources[pair["source_a"]]["condition"],
             "sentence1": texts[pair["source_a"]], "sentence2": texts[pair["source_b"]],
             "rating": 1.0, "target": 0.0} for pair in inputs["pairs"]]


def evaluate_formats(
    predictions: Sequence[dict[str, Any]], labels_by_id: Mapping[str, float],
    groups_by_id: Mapping[str, str], direct_by_id: Mapping[str, float],
    draws: int = 2000, seed: int = 42,
) -> dict[str, Any]:
    """Compare sealed format scores with exact joins and paired component resampling."""
    from csts_pilot.proposition_similarity import _metrics, _percentile, component_resamples

    ids = [row["id"] for row in predictions]
    if (len(ids) < 2 or len(ids) != len(set(ids)) or
            any(set(mapping) != set(ids) for mapping in (labels_by_id, groups_by_id, direct_by_id))):
        raise ValueError("Predictions, ratings, groups and direct scores must cover identical unique IDs.")
    if any(not _text(groups_by_id[identity]) for identity in ids):
        raise ValueError("Every prediction requires a connected source group.")
    ratings = [float(labels_by_id[identity]) for identity in ids]
    direct = [float(direct_by_id[identity]) for identity in ids]
    if any(not math.isfinite(value) or not 1 <= value <= 5 for value in ratings + direct):
        raise ValueError("Ratings and direct scores must be finite on the original 1–5 scale.")
    target = [(rating - 1) / 4 for rating in ratings]
    arms = {arm: [float(row[arm]) for row in predictions] for arm in ARMS}
    if any(not math.isfinite(value) or not -1.00001 <= value <= 1.00001 for values in arms.values() for value in values):
        raise ValueError("Every encoder prediction must be a finite cosine.")
    arms["gpt_direct"] = [(value - 1) / 4 for value in direct]
    fallback = {}
    for arm in EVIDENCE_ARMS:
        rows = [row["fallback_by_arm"][arm] for row in predictions]
        if any(not isinstance(row, list) or len(row) != 2 or
               any(reason is not None and not _text(reason) for reason in row) for row in rows):
            raise ValueError("Fallback audit requires exactly two optional per-side reasons per arm.")
        sides = [reason for row in rows for reason in row if reason is not None]
        counts = [sum(reason is not None for reason in row) for row in rows]
        fallback[arm] = {"side_occurrences": len(sides), "pairs_with_any": sum(count > 0 for count in counts),
                         "pairs_with_one": counts.count(1), "pairs_with_both": counts.count(2),
                         "reason_counts": dict(Counter(sides))}
    comparisons = [
        ("json_minus_propositions", "json", "propositions", "primary"),
        ("python_minus_propositions", "python", "propositions", "primary"),
        ("python_minus_json", "python", "json", "primary"),
        ("propositions_minus_raw", "propositions", "raw", "reference"),
        *((arm + "_minus_gpt_direct", arm, "gpt_direct", "reference") for arm in ARMS),
    ]
    result = {"n": len(ids), "groups": len(set(groups_by_id.values())),
              "metrics": {arm: _metrics(values, target) for arm, values in arms.items()},
              "fallback": fallback,
              "mse_policy": "Unclipped cosine against (rating-1)/4; no fitted calibration.",
              "bootstrap": {"draws": draws, "seed": seed, "unit": "connected_source_component",
                            "interval": "paired percentile 95%", "comparisons": {}}}
    samples = {name: {"spearman": [], "mse_0_1": []} for name, _, _, _ in comparisons}
    for indexes in component_resamples([groups_by_id[identity] for identity in ids], draws, seed):
        gold = [target[index] for index in indexes]
        metrics = {arm: _metrics([scores[index] for index in indexes], gold) for arm, scores in arms.items()}
        for name, left, right, _ in comparisons:
            for metric in ("spearman", "mse_0_1"):
                a, b = metrics[left][metric], metrics[right][metric]
                if a is not None and b is not None:
                    samples[name][metric].append(a - b)
    for name, left, right, role in comparisons:
        summary = {"role": role}
        for metric in ("spearman", "mse_0_1"):
            values = samples[name][metric]
            a, b = result["metrics"][left][metric], result["metrics"][right][metric]
            summary[metric] = {"difference": None if a is None or b is None else a - b,
                               "defined_draws": len(values),
                               "interval": [_percentile(values, .025), _percentile(values, .975)] if values else None}
        result["bootstrap"]["comparisons"][name] = summary
    return result


def score(inputs_path: Path, output: Path, incumbent_repo: Path, checkpoint: Path) -> None:
    """Call the incumbent TokenPairs scorer with frozen parameters and retained vectors."""
    inputs = json.loads(inputs_path.read_text())
    validate_inputs(inputs)
    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs.json").write_bytes(inputs_path.read_bytes())
    receipt = {"status": "starting", "started_unix": time.time(), "inputs_sha256": sha256(inputs_path),
               "code_sha256": sha256(Path(__file__)), "optimizer_updates": 0,
               "label_policy": "No evaluation labels supplied; constant rating=1,target=0 placeholders satisfy legacy row validation only.",
               "batch_layout": "two comparisons: left1,left2,right1,right2",
               "fallback": "original passage per unavailable side", "truncated_inputs": 0}
    write_json(output / "receipt.json", receipt)
    try:
        import numpy as np
        import torch
        import transformers
        import peft

        incumbent_repo = incumbent_repo.resolve()
        sys.path.insert(0, str(incumbent_repo))
        legacy = importlib.import_module("csts_pilot.baseline_models")
        if not Path(legacy.__file__).resolve().is_relative_to(incumbent_repo):
            raise ValueError("Run as a standalone script so incumbent imports cannot resolve to another checkout.")
        if legacy.PROMPT != PROMPT or getattr(legacy, "EOD", None) != EOD:
            raise ValueError("The incumbent prompt or EOD changed.")
        if not torch.cuda.is_available():
            raise RuntimeError("The declared scoring job requires CUDA.")
        if sha256(checkpoint) != CHECKPOINT_SHA256:
            raise ValueError("The trained checkpoint changed.")
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        fit = legacy.FitConfig.model_validate(saved["config"])
        if saved.get("kind") != "lora" or fit.kind != "lora":
            raise ValueError("The incumbent must be the saved LoRA model.")
        if (fit.model_id, fit.revision, fit.max_length, fit.embedding_dimension) != (MODEL_ID, REVISION, 160, 4096):
            raise ValueError("The checkpoint encoder contract differs.")
        fit = fit.model_copy(update={"device": "cuda"})
        receipt.update(checkpoint_sha256=CHECKPOINT_SHA256, checkpoint_config=saved["config"],
                       checkpoint_epoch=saved.get("epoch"), checkpoint_step=saved.get("step"),
                       incumbent_baseline_code=str(Path(legacy.__file__).resolve()),
                       incumbent_baseline_code_sha256=sha256(Path(legacy.__file__)),
                       gpu=subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"], text=True).strip(),
                       versions={"python": sys.version, "torch": str(torch.__version__),
                                 "transformers": transformers.__version__, "peft": peft.__version__, "numpy": np.__version__})
        torch.manual_seed(7)
        torch.cuda.manual_seed_all(7)
        tokenizer = legacy.load_tokenizer(fit)
        texts, reasons, tokenized = effective_inputs(inputs, tokenizer)
        write_json(output / "tokenized_inputs.json", tokenized)
        receipt["source_fallbacks"] = {arm: dict(Counter(reason for reason in reasons[arm].values() if reason)) for arm in EVIDENCE_ARMS}
        receipt["tokenized_inputs_sha256"] = sha256(output / "tokenized_inputs.json")
        receipt["status"] = "loading_model"
        write_json(output / "receipt.json", receipt)
        model = legacy.load_backbone(fit, adapters=fit)
        legacy.restore_parameters(model, saved["state"])
        before = legacy.state_digest(legacy.trainable_state(model))
        parameters = {name: value for name, value in model.named_parameters() if value.requires_grad}
        del saved
        model.eval()
        model.requires_grad_(False)
        receipt.update(status="scoring", adapter_state_before_sha256=before)
        write_json(output / "receipt.json", receipt)
        results, vectors = {}, {}
        original_encode = legacy.encode
        captured = []

        def retain_encode(*args, **kwargs):
            embeddings = original_encode(*args, **kwargs)
            captured.append(embeddings.detach().float().cpu().numpy())
            return embeddings

        legacy.encode = retain_encode
        try:
            with torch.inference_mode():
                for arm in ARMS:
                    rows = inference_rows(inputs, texts[arm])
                    pairs = legacy.TokenPairs(rows, fit, tokenizer)
                    expected = {(row["condition"], row["text"]): row["input_ids"] for row in tokenized if row["arm"] == arm}
                    if pairs.sequences != expected:
                        raise ValueError("Legacy scorer tokenization differs from the frozen effective inputs.")
                    scores, left, right = [], [], []
                    for start in range(0, len(rows), 2):
                        captured.clear()
                        indices = torch.arange(start, min(start + 2, len(rows)))
                        values = pairs.scores(model, indices).float().cpu().tolist()
                        if len(captured) != 1 or captured[0].shape != (2 * len(values), 4096):
                            raise ValueError("The incumbent scorer's encoding layout changed.")
                        a, b = np.split(captured[0], 2)
                        left.append(a)
                        right.append(b)
                        scores.extend(values)
                        print(json.dumps({"arm": arm, "done": len(scores), "total": len(rows)}), flush=True)
                    if any(not math.isfinite(value) or not -1.00001 <= value <= 1.00001 for value in scores):
                        raise ValueError("The incumbent returned a nonfinite or invalid cosine.")
                    results[arm] = scores
                    vectors[arm + "_left"], vectors[arm + "_right"] = np.concatenate(left), np.concatenate(right)
        finally:
            legacy.encode = original_encode
        after = legacy.state_digest(parameters)
        if after != before:
            raise ValueError("Adapter parameters changed during scoring.")
        predictions = [{"id": pair["id"], **{arm: results[arm][i] for arm in ARMS},
                        "fallback_by_arm": {arm: [reasons[arm][pair["source_a"]], reasons[arm][pair["source_b"]]] for arm in EVIDENCE_ARMS}}
                       for i, pair in enumerate(inputs["pairs"])]
        np.savez_compressed(output / "embeddings.npz", pair_ids=np.asarray([p["id"] for p in inputs["pairs"]]),
                            source_a=np.asarray([p["source_a"] for p in inputs["pairs"]]),
                            source_b=np.asarray([p["source_b"] for p in inputs["pairs"]]), **vectors)
        write_json(output / "predictions.json", predictions)
        receipt.update(status="complete", completed_unix=time.time(), seconds=time.time() - receipt["started_unix"],
                       adapter_state_after_sha256=after, comparisons=len(predictions), sources=len(inputs["sources"]),
                       embeddings_sha256=sha256(output / "embeddings.npz"), predictions_sha256=sha256(output / "predictions.json"))
        write_json(output / "receipt.json", receipt)
    except Exception as exc:
        receipt.update(status="failed", completed_unix=time.time(), error_type=type(exc).__name__, error=str(exc))
        write_json(output / "receipt.json", receipt)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scoring = sub.add_parser("score")
    for name in ("inputs", "output", "incumbent-repo", "checkpoint"):
        scoring.add_argument("--" + name, type=Path, required=True)
    evaluation = sub.add_parser("evaluate")
    for name in ("inputs", "predictions", "labels", "direct", "output"):
        evaluation.add_argument("--" + name, type=Path, required=True)
    evaluation.add_argument("--draws", type=int, default=2000)
    evaluation.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.command == "score":
        score(args.inputs, args.output, args.incumbent_repo, args.checkpoint)
    else:
        inputs = json.loads(args.inputs.read_text())
        validate_inputs(inputs)
        labels = json.loads(args.labels.read_text())
        label_map = {row.get("id", row.get("row_id")): row["rating"] for row in labels}
        if len(label_map) != len(labels):
            raise ValueError("Duplicate rating IDs.")
        groups = {pair["id"]: pair["group_id"] for pair in inputs["pairs"]}
        if any(row.get("group_id", groups.get(row.get("id", row.get("row_id")))) != groups.get(row.get("id", row.get("row_id"))) for row in labels):
            raise ValueError("Rating and input component identities differ.")
        result = evaluate_formats(json.loads(args.predictions.read_text()), label_map, groups,
                                  json.loads(args.direct.read_text()), args.draws, args.seed)
        write_json(args.output, result)


if __name__ == "__main__":
    main()
