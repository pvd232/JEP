"""Verify saved embeddings after a receipt-only failure; never load model weights."""

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time

import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recover(root):
    root = Path(root)
    output = root / "output"
    seal = json.loads((root / "execution_seal.json").read_text())
    for name, digest in seal.items():
        if sha(root / name) != digest:
            raise ValueError("Executed asset changed: " + name)
    original = json.loads((output / "receipt.json").read_text())
    if sha(root / "inputs.json") != original["inputs_sha256"] or sha(output / "inputs.json") != original["inputs_sha256"]:
        raise ValueError("Encoding input identity differs")
    status = json.loads((root / "status.json").read_text())
    log = (root / "encoding.log").read_text()
    if status["status"] != "failed" or "Object of type set is not JSON serializable" not in log:
        raise ValueError("Failure is outside the declared receipt recovery")
    if '{"encoded": 449, "total": 449}' not in log:
        raise ValueError("Encoding completion proof absent")
    inputs = json.loads((root / "inputs.json").read_text())
    predictions = json.loads((output / "predictions.json").read_text())
    sources = inputs["sources"]
    by_source = {s["id"]: i for i, s in enumerate(sources)}
    by_prediction = {p["id"]: p for p in predictions}
    if len(predictions) != len(by_prediction) or set(by_prediction) != {p["id"] for p in inputs["pairs"]}:
        raise ValueError("Prediction IDs differ")
    with np.load(output / "embeddings.npz", allow_pickle=False) as data:
        if data["source_ids"].tolist() != [s["id"] for s in sources]:
            raise ValueError("Embedding source order differs")
        raw, evidence = data["raw"], data["evidence"]
        mask = np.asarray([s["status"] == "answered" and bool(s["evidence_text"].strip()) for s in sources])
        if not np.array_equal(mask, data["evidence_eligible"]) or raw.shape != (239, 4096) or evidence.shape != raw.shape:
            raise ValueError("Embedding coverage differs")
        vectors = np.concatenate([raw, evidence[mask]])
        if not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=2e-6):
            raise ValueError("Embedding vectors are invalid")
        keys = [tuple(k) for k in data["unique_keys"].tolist()]
        index = {key: i for i, key in enumerate(keys)}
        if len(index) != 449 or data["unique_vectors"].shape != (449, 4096):
            raise ValueError("Unique encoder input coverage differs")
        for i, source in enumerate(sources):
            if not np.array_equal(raw[i], data["unique_vectors"][index[source["condition"], source["passage"]]]):
                raise ValueError("Raw source embedding binding differs")
            if mask[i] and not np.array_equal(evidence[i], data["unique_vectors"][index[source["condition"], source["evidence_text"]]]):
                raise ValueError("Proposition embedding binding differs")
        errors = []
        for pair in inputs["pairs"]:
            a, b = by_source[pair["source_a"]], by_source[pair["source_b"]]
            fallback = not (mask[a] and mask[b])
            pred = by_prediction[pair["id"]]
            expected_raw = float(np.dot(raw[a], raw[b]))
            expected_evidence = expected_raw if fallback else float(np.dot(evidence[a], evidence[b]))
            if pred["fallback"] != bool(fallback):
                raise ValueError("Fallback policy differs")
            errors.extend([abs(pred["raw_cosine"] - expected_raw), abs(pred["evidence_cosine"] - expected_evidence)])
        if max(errors) > 1e-7:
            raise ValueError("Saved predictions differ from independent cosine replay")
    tokenized = json.loads((output / "tokenized_inputs.json").read_text())
    if len(tokenized) != 449 or [(x["condition"], x["passage"]) for x in tokenized] != keys:
        raise ValueError("Token inputs do not bind to vector order")
    if any(x["input_ids"][-1] != 151643 or len(x["input_ids"]) > 512 for x in tokenized):
        raise ValueError("EOD or token ceiling differs")
    if sha(output / "tokenized_inputs.json") != original["tokenized_inputs_sha256"]:
        raise ValueError("Tokenized inputs changed")
    result = {
        "status": "recovered_saved_outputs_after_receipt_serialization_failure",
        "recovered_unix": time.time(), "additional_model_calls": 0,
        "cause": "Transformers model-loading metadata contains a set; JSON receipt serialization failed after predictions were saved.",
        "original_receipt_preserved": True, "original_failure_preserved": True,
        "original_receipt_sha256": sha(output / "receipt.json"),
        "executed_code_sha256": sha(root / "csts_pilot/proposition_similarity.py"),
        "recovery_code_sha256": sha(__file__), "inputs_sha256": sha(root / "inputs.json"),
        "embeddings_sha256": sha(output / "embeddings.npz"), "predictions_sha256": sha(output / "predictions.json"),
        "tokenized_inputs_sha256": sha(output / "tokenized_inputs.json"),
        "sources": 239, "answered_sources": int(mask.sum()), "pairs": len(predictions),
        "fallback_pairs": sum(p["fallback"] for p in predictions),
        "unique_encoded_inputs": 449, "cosine_replay_max_error": max(errors),
        "model_loading_guard": "Passed in the executed code before all 449 encoding inputs completed; raw loading-info object was not serialized.",
    }
    (root / "recovery.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    archive_path = Path(str(root) + "-outputs.tar.gz")
    with tarfile.open(archive_path, "w:gz") as archive:
        for name in ["output", "inputs.json", "plan.md", "execution_seal.json", "dispatch.json", "worker.py", "status.json", "tests.log", "encoding.log", "recovery.json", "recover.py", "csts_pilot/proposition_similarity.py", "tests/test_proposition_similarity.py"]:
            archive.add(root / name, arcname=name)
    print(json.dumps({"recovery": result, "archive": str(archive_path), "sha256": sha(archive_path), "bytes": archive_path.stat().st_size}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    recover(parser.parse_args().run)
