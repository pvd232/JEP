"""Compare original passages and source-only propositions with a frozen encoder."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

PROMPT = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
MODEL_ID = "Qwen/Qwen3-Embedding-8B"
REVISION = "c90816d848505624c2434128dfc61132162a0ee9"
EOD = "<|endoftext|>"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_extra(value: Any) -> Any:
    """Serialize Transformers loading-info sets in a stable order."""
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=lambda item: json.dumps(
            item, sort_keys=True, allow_nan=False, default=_json_extra,
        ))
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False, default=_json_extra) + "\n").encode()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_inputs(inputs: dict[str, Any]) -> None:
    protocol = inputs["protocol"]
    if (protocol["model_id"], protocol["revision"], protocol["prompt"]) != (MODEL_ID, REVISION, PROMPT):
        raise ValueError("The model revision and shared prompt must match the fixed comparison.")
    if not isinstance(protocol["max_length"], int) or protocol["max_length"] < 8:
        raise ValueError("Invalid token ceiling.")
    if not isinstance(protocol["batch_size"], int) or protocol["batch_size"] < 1:
        raise ValueError("Invalid batch size.")
    sources = inputs["sources"]
    pairs = inputs["pairs"]
    if not sources or not pairs:
        raise ValueError("Sources and pairs must be nonempty.")
    ids = [source["id"] for source in sources]
    if any(not _nonempty(i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Source IDs must be unique nonempty strings.")
    for source in sources:
        if any(not _nonempty(source[k]) for k in ("passage", "condition")):
            raise ValueError("Original passages and conditions must be nonempty strings.")
        if source["status"] not in {"answered", "not_specified", "ambiguous"}:
            raise ValueError("Unknown proposition status.")
        if not isinstance(source["evidence_text"], str):
            raise ValueError("Canonical evidence must be a string.")
    pair_ids = [pair["id"] for pair in pairs]
    if any(not _nonempty(i) for i in pair_ids) or len(set(pair_ids)) != len(pair_ids):
        raise ValueError("Pair IDs must be unique nonempty strings.")
    by_id = {source["id"]: source for source in sources}
    for pair in pairs:
        if not _nonempty(pair["group_id"]):
            raise ValueError("Each comparison requires its connected-source group.")
        if pair["source_a"] not in by_id or pair["source_b"] not in by_id:
            raise ValueError("A comparison references an unknown source.")
        if by_id[pair["source_a"]]["condition"] != by_id[pair["source_b"]]["condition"]:
            raise ValueError("The two sources in a comparison must share its condition.")


def token_sequences(tokenizer: Any, keys: Sequence[tuple[str, str]], max_length: int) -> list[list[int]]:
    """Append one explicit EOD; inspect every full sequence before any inference."""
    encoded = tokenizer(
        [PROMPT.format(condition=condition, passage=passage) for condition, passage in keys],
        padding=False, truncation=False, add_special_tokens=False,
    )
    eod = tokenizer.get_vocab().get(EOD)
    if eod is None:
        raise ValueError("The tokenizer lacks the required EOD token.")
    sequences = [[*ids, eod] for ids in encoded["input_ids"]]
    if any(len(ids) > max_length for ids in sequences):
        raise ValueError("A complete input exceeds the frozen token ceiling; no inputs were truncated.")
    return sequences


def last_token_pool(hidden: Any, attention_mask: Any) -> Any:
    """Pool the last attended token with either padding side, then normalize in FP32."""
    import torch
    from torch.nn import functional as F

    if hidden.shape[:2] != attention_mask.shape or not attention_mask.bool().any(1).all():
        raise ValueError("Pooling requires matching shapes and nonempty attention masks.")
    positions = torch.arange(hidden.shape[1], device=hidden.device).expand_as(attention_mask)
    last = positions.masked_fill(~attention_mask.bool(), -1).max(1).values
    with torch.autocast(hidden.device.type, enabled=False):
        pooled = hidden[torch.arange(len(hidden), device=hidden.device), last].float()
        if not torch.isfinite(pooled).all() or (pooled.norm(dim=-1) == 0).any():
            raise ValueError("Embeddings must be finite and nonzero.")
        return F.normalize(pooled, dim=-1)


def pair_predictions(inputs: dict[str, Any], cosine_by_key: Mapping[tuple[str, str, str], float]) -> list[dict[str, Any]]:
    """Use a symmetric raw-passage fallback when either source lacks an answered claim."""
    validate_inputs(inputs)
    sources = {source["id"]: source for source in inputs["sources"]}
    output = []
    for pair in inputs["pairs"]:
        a, b = pair["source_a"], pair["source_b"]
        fallback = any(sources[i]["status"] != "answered" or not sources[i]["evidence_text"].strip() for i in (a, b))
        raw = float(cosine_by_key[("raw", a, b)])
        evidence = raw if fallback else float(cosine_by_key[("evidence", a, b)])
        if any(not math.isfinite(value) or not -1.00001 <= value <= 1.00001 for value in (raw, evidence)):
            raise ValueError("Cosine scores must be finite and in range.")
        output.append({"id": pair["id"], "raw_cosine": raw, "evidence_cosine": evidence, "fallback": fallback})
    return output


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + end - 1) / 2 + 1
        for index in order[start:end]:
            result[index] = rank
        start = end
    return result


def spearman(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("Spearman requires equally sized vectors with at least two observations.")
    a, b = _ranks(left), _ranks(right)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    aa = sum((x - ma) ** 2 for x in a)
    bb = sum((y - mb) ** 2 for y in b)
    if not aa or not bb:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(aa * bb)


def _metrics(predictions: Sequence[float], targets: Sequence[float]) -> dict[str, Any]:
    mse = statistics.fmean((a - b) ** 2 for a, b in zip(predictions, targets))
    return {"n": len(predictions), "spearman": spearman(predictions, targets), "mse_0_1": mse, "mse_1_5": 16 * mse}


def component_resamples(group_ids: Sequence[str], draws: int, seed: int) -> list[list[int]]:
    """Sample connected groups with replacement and retain every row in each selected group."""
    if not group_ids or draws < 1:
        raise ValueError("Bootstrap requires groups and positive draw count.")
    groups: dict[str, list[int]] = defaultdict(list)
    for index, group in enumerate(group_ids):
        groups[group].append(index)
    keys = sorted(groups)
    rng = random.Random(seed)
    return [[i for group in rng.choices(keys, k=len(keys)) for i in groups[group]] for _ in range(draws)]


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def evaluate_predictions(
    predictions: Sequence[dict[str, Any]], labels_by_id: Mapping[str, float], group_ids: Mapping[str, str],
    draws: int = 2000, seed: int = 42, direct_by_id: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Evaluate sealed scores; labels and direct GPT scores use their original 1–5 scale."""
    ids = [p["id"] for p in predictions]
    if len(ids) < 2 or len(ids) != len(set(ids)) or set(ids) != set(labels_by_id) or set(ids) != set(group_ids):
        raise ValueError("Prediction, label and component IDs must match exactly and uniquely.")
    if direct_by_id is not None and set(direct_by_id) != set(ids):
        raise ValueError("Direct GPT scores must cover the same exact IDs.")
    ratings = [float(labels_by_id[i]) for i in ids]
    if any(not math.isfinite(v) or not 1 <= v <= 5 for v in ratings):
        raise ValueError("Ratings must be finite on the original 1–5 scale.")
    target = [(rating - 1) / 4 for rating in ratings]
    arms = {name: [float(p[field]) for p in predictions] for name, field in (("raw", "raw_cosine"), ("propositions_with_fallback", "evidence_cosine"))}
    if direct_by_id is not None:
        direct = [float(direct_by_id[i]) for i in ids]
        if any(not math.isfinite(v) or not 1 <= v <= 5 for v in direct):
            raise ValueError("Direct GPT scores must be finite on the original 1–5 scale.")
        arms["gpt_direct"] = [(score - 1) / 4 for score in direct]
    if any(not math.isfinite(v) for values in arms.values() for v in values):
        raise ValueError("Every prediction must be finite.")
    for p in predictions:
        if not isinstance(p["fallback"], bool) or (p["fallback"] and p["evidence_cosine"] != p["raw_cosine"]):
            raise ValueError("Fallback pairs must preserve the raw score exactly.")
    result: dict[str, Any] = {"n": len(ids), "groups": len(set(group_ids.values())), "fallback_pairs": sum(p["fallback"] for p in predictions), "metrics": {name: _metrics(values, target) for name, values in arms.items()}, "mse_policy": "Unclipped cosine against (rating-1)/4; no fitted calibration.", "bootstrap": {"draws": draws, "seed": seed, "unit": "connected_source_component", "interval": "paired percentile 95%", "comparisons": {}}}
    comparisons = [("propositions_minus_raw", "propositions_with_fallback", "raw")]
    if direct_by_id is not None:
        comparisons += [("propositions_minus_gpt_direct", "propositions_with_fallback", "gpt_direct"), ("raw_minus_gpt_direct", "raw", "gpt_direct")]
    values = {name: {"spearman": [], "mse_0_1": []} for name, _, _ in comparisons}
    for indexes in component_resamples([group_ids[i] for i in ids], draws, seed):
        sampled_target = [target[i] for i in indexes]
        sample = {name: _metrics([scores[i] for i in indexes], sampled_target) for name, scores in arms.items()}
        for name, a, b in comparisons:
            for metric in ("spearman", "mse_0_1"):
                x, y = sample[a][metric], sample[b][metric]
                if x is not None and y is not None:
                    values[name][metric].append(x - y)
    for name, a, b in comparisons:
        result["bootstrap"]["comparisons"][name] = {}
        for metric in ("spearman", "mse_0_1"):
            draws_values = values[name][metric]
            ma, mb = result["metrics"][a][metric], result["metrics"][b][metric]
            result["bootstrap"]["comparisons"][name][metric] = {"difference": None if ma is None or mb is None else ma - mb, "defined_draws": len(draws_values), "interval": [_percentile(draws_values, .025), _percentile(draws_values, .975)] if draws_values else None}
    answered = [i for i, p in enumerate(predictions) if not p["fallback"]]
    result["answered_pairs_only"] = {"n": len(answered), "role": "status-defined descriptive sensitivity; no fidelity-judge filtering", "metrics": {name: _metrics([scores[i] for i in answered], [target[i] for i in answered]) for name, scores in arms.items()} if len(answered) >= 2 else {}}
    return result


def encode_inputs(inputs_path: Path, output: Path, model_cache: Path | None = None) -> None:
    """Run one frozen, label-free GPU encoding job; refuse to overwrite a prior run."""
    import platform
    import subprocess
    import sys
    import numpy as np
    import torch
    import transformers
    from transformers import AutoModel, AutoTokenizer

    started = time.time()
    inputs = json.loads(inputs_path.read_text())
    validate_inputs(inputs)
    protocol = inputs["protocol"]
    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs.json").write_bytes(inputs_path.read_bytes())
    receipt: dict[str, Any] = {"status": "started", "started_unix": started, "inputs_sha256": sha256(inputs_path), "protocol_sha256": hashlib.sha256(json_bytes(protocol)).hexdigest(), "code_sha256": sha256(Path(__file__)), "model_id": MODEL_ID, "revision": REVISION, "prompt": PROMPT, "pooling": "last_nonpadding_eod_float32_unit_norm", "dtype": "bfloat16", "attention": "sdpa", "training": "none", "versions": {"python": sys.version, "torch": torch.__version__, "transformers": transformers.__version__, "numpy": np.__version__, "platform": platform.platform()}}
    (output / "receipt.json").write_bytes(json_bytes(receipt))
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("This declared run requires a CUDA GPU.")
        gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"], text=True).strip()
        receipt["gpu"] = gpu
        torch.manual_seed(protocol.get("seed", 42))
        torch.cuda.manual_seed_all(protocol.get("seed", 42))
        torch.backends.cuda.matmul.allow_tf32 = False
        source = MODEL_ID
        kwargs: dict[str, Any] = {"revision": REVISION, "trust_remote_code": False}
        if model_cache is not None:
            model_cache = model_cache.resolve()
            if model_cache.name != REVISION or not model_cache.is_dir():
                raise ValueError("Local model cache must be the pinned immutable snapshot directory.")
            source = str(model_cache)
            kwargs["local_files_only"] = True
            receipt["model_snapshot"] = str(model_cache)
            receipt["model_files"] = [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(model_cache.iterdir()) if p.is_file() and (p.suffix in {".json", ".safetensors"} or p.name in {"merges.txt", "vocab.json"})]
        tokenizer = AutoTokenizer.from_pretrained(source, padding_side="left", **kwargs)
        sources = inputs["sources"]
        raw_keys = [(s["condition"], s["passage"]) for s in sources]
        evidence_eligible = [s["status"] == "answered" and bool(s["evidence_text"].strip()) for s in sources]
        evidence_keys = [(s["condition"], s["evidence_text"]) for s, eligible in zip(sources, evidence_eligible) if eligible]
        keys = sorted(set(raw_keys + evidence_keys))
        sequences = token_sequences(tokenizer, keys, protocol["max_length"])
        receipt["token_lengths"] = {"min": min(map(len, sequences)), "max": max(map(len, sequences)), "total": sum(map(len, sequences)), "unique_inputs": len(keys), "limit": protocol["max_length"], "truncated": 0}
        (output / "tokenized_inputs.json").write_bytes(json_bytes([
            {"condition": condition, "passage": passage, "text_sha256": hashlib.sha256(PROMPT.format(condition=condition, passage=passage).encode()).hexdigest(), "input_ids": ids}
            for (condition, passage), ids in zip(keys, sequences)
        ]))
        receipt["tokenized_inputs_sha256"] = sha256(output / "tokenized_inputs.json")
        receipt["evidence_sources"] = sum(evidence_eligible)
        receipt["sources"] = len(sources)
        (output / "receipt.json").write_bytes(json_bytes(receipt))
        model, loading_info = AutoModel.from_pretrained(source, torch_dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": "cuda"}, output_loading_info=True, **kwargs)
        receipt["model_loading"] = loading_info
        if any(loading_info.get(key) for key in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")):
            raise ValueError("The pinned embedding backbone did not load exactly.")
        if model.config.hidden_size != 4096:
            raise ValueError("The frozen Qwen embedding width must be 4096.")
        model.config.use_cache = False
        model.eval()
        model.requires_grad_(False)
        vectors = []
        infer_started = time.time()
        for start in range(0, len(keys), protocol["batch_size"]):
            selected = sequences[start:start + protocol["batch_size"]]
            batch = tokenizer.pad({"input_ids": selected, "attention_mask": [[1] * len(ids) for ids in selected]}, padding=True, return_tensors="pt")
            batch = {k: v.to("cuda") for k, v in batch.items() if k in {"input_ids", "attention_mask"}}
            with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                hidden = model(**batch).last_hidden_state
                vector = last_token_pool(hidden, batch["attention_mask"])
            vectors.append(vector.cpu().numpy())
            print(json.dumps({"encoded": min(start + protocol["batch_size"], len(keys)), "total": len(keys)}), flush=True)
        encoded = np.concatenate(vectors)
        by_key = {key: index for index, key in enumerate(keys)}
        raw = np.stack([encoded[by_key[key]] for key in raw_keys])
        evidence = np.zeros_like(raw)
        for i, (s, eligible) in enumerate(zip(sources, evidence_eligible)):
            if eligible:
                evidence[i] = encoded[by_key[(s["condition"], s["evidence_text"])]]
        np.savez_compressed(output / "embeddings.npz", source_ids=np.asarray([s["id"] for s in sources]), raw=raw, evidence=evidence, evidence_eligible=np.asarray(evidence_eligible), unique_keys=np.asarray(keys), unique_vectors=encoded)
        indexes = {s["id"]: i for i, s in enumerate(sources)}
        cosines = {}
        for pair in inputs["pairs"]:
            a, b = pair["source_a"], pair["source_b"]
            ia, ib = indexes[a], indexes[b]
            cosines[("raw", a, b)] = float(np.dot(raw[ia], raw[ib]))
            if evidence_eligible[ia] and evidence_eligible[ib]:
                cosines[("evidence", a, b)] = float(np.dot(evidence[ia], evidence[ib]))
        predictions = pair_predictions(inputs, cosines)
        (output / "predictions.json").write_bytes(json_bytes(predictions))
        receipt.update(status="complete", completed_unix=time.time(), seconds=time.time() - started, encoding_seconds=time.time() - infer_started, pairs=len(predictions), fallback_pairs=sum(p["fallback"] for p in predictions), embeddings_sha256=sha256(output / "embeddings.npz"), predictions_sha256=sha256(output / "predictions.json"))
        (output / "receipt.json").write_bytes(json_bytes(receipt))
    except Exception as exc:
        receipt.update(status="failed", error_type=type(exc).__name__, error=str(exc), completed_unix=time.time())
        (output / "receipt.json").write_bytes(json_bytes(receipt))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    encode = commands.add_parser("encode")
    encode.add_argument("--inputs", type=Path, required=True)
    encode.add_argument("--output", type=Path, required=True)
    encode.add_argument("--model-cache", type=Path)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--inputs", type=Path, required=True)
    evaluate.add_argument("--predictions", type=Path, required=True)
    evaluate.add_argument("--labels", type=Path, required=True)
    evaluate.add_argument("--direct", type=Path)
    evaluate.add_argument("--output", type=Path, required=True)
    evaluate.add_argument("--draws", type=int, default=2000)
    evaluate.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.command == "encode":
        encode_inputs(args.inputs, args.output, args.model_cache)
    else:
        inputs = json.loads(args.inputs.read_text())
        validate_inputs(inputs)
        labels = json.loads(args.labels.read_text())
        labels_by_id = {row.get("id", row.get("row_id")): row["rating"] for row in labels}
        if len(labels_by_id) != len(labels):
            raise ValueError("Duplicate label IDs.")
        direct = json.loads(args.direct.read_text()) if args.direct else None
        result = evaluate_predictions(json.loads(args.predictions.read_text()), labels_by_id, {p["id"]: p["group_id"] for p in inputs["pairs"]}, args.draws, args.seed, direct)
        args.output.write_bytes(json_bytes(result))


if __name__ == "__main__":
    main()
