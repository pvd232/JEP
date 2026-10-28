"""Capture fixed ratings control vectors for comparison diagnostics."""

import argparse
import fcntl
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import torch
from csts_pilot.background_storage import _save
from csts_pilot.baseline_models import (
    FitConfig,
    encode,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    passage_keys,
    restore_parameters,
    token_sequences,
)
from csts_pilot.evidence_readout import metric_values
from viper.storage import ViperCloudDestination, publish_resolved_files


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()
    torch.set_num_threads(4)
    root, directory = args.root, args.output
    directory.mkdir(parents=True, exist_ok=True)
    expected = "667c124a49be72a6fd8e9fa3df6974830e4ab6a46a10243c360dd46bcc75b534"
    if digest(args.model) != expected:
        raise ValueError("The control checkpoint identity changed.")
    saved = torch.load(args.model, map_location="cpu", weights_only=True)
    config = FitConfig.model_validate(
        {k: v for k, v in saved["config"].items() if k in FitConfig.model_fields}
        | {"kind": "lora", "device": "cuda", "encode_batch_size": args.batch_size}
    )
    settings = json.loads((root / "configs/csts-native-comparison.json").read_text())
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    pool = ThreadPoolExecutor(max_workers=1)
    publications = []
    summary = {
        "status": "encoding",
        "model_sha256": expected,
        "splits": {},
        "encoder_updates": 0,
    }
    _save(directory / "capture-status.json", summary)
    lock_path = Path("/tmp/jep-gpu.lock")
    if not lock_path.exists():
        lock_path.touch(mode=0o664)
    with lock_path.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        tokenizer = load_tokenizer(config)
        model = load_backbone(config, adapters=config)
        restore_parameters(model, saved["state"])
        model.gradient_checkpointing_disable()
        model.eval().requires_grad_(False)
        for split in ("test", "training", "validation"):
            item = settings["splits"][split]
            path = root / item["path"]
            if digest(path) != item["sha256"]:
                raise ValueError("The frozen rating inputs changed.")
            rows = json.loads(path.read_text())
            keys = passage_keys(rows)
            sequences = token_sequences(tokenizer, keys, config)
            vectors = torch.empty(
                (len(keys), config.embedding_dimension), dtype=torch.float32
            )
            cursor, batch_size, started = 0, args.batch_size, time.monotonic()
            with torch.inference_mode():
                while cursor < len(keys):
                    stop = min(cursor + batch_size, len(keys))
                    try:
                        batch = pad_sequences(tokenizer, sequences[cursor:stop], config)
                        vectors[cursor:stop] = encode(model, batch).float().cpu()
                    except torch.cuda.OutOfMemoryError:
                        if batch_size <= 4:
                            raise
                        batch_size //= 2
                        torch.cuda.empty_cache()
                        continue
                    cursor = stop
                    summary["in_flight"] = {
                        "split": split,
                        "sentences": cursor,
                        "total": len(keys),
                        "seconds": time.monotonic() - started,
                        "batch_size": batch_size,
                    }
                    _save(directory / "capture-status.json", summary)
            if not torch.isfinite(vectors).all() or not torch.allclose(
                vectors.norm(dim=1), torch.ones(len(keys)), atol=2e-5, rtol=2e-5
            ):
                raise ValueError("Captured sentence vectors must have unit length.")
            lookup = {tuple(key): i for i, key in enumerate(keys)}
            left = [lookup[(r["condition"], r["sentence1"])] for r in rows]
            right = [lookup[(r["condition"], r["sentence2"])] for r in rows]
            cosine = (vectors[left] * vectors[right]).sum(-1).numpy()
            target = directory / ("control_" + split + ".pt")
            torch.save(
                {
                    "vectors": vectors,
                    "keys": keys,
                    "left": left,
                    "right": right,
                    "row_ids": [r["row_id"] for r in rows],
                    "model_sha256": expected,
                    "rows_sha256": item["sha256"],
                    "encoder": config.model_dump(),
                },
                target,
            )
            summary["splits"][split] = {
                "path": str(target),
                "sha256": digest(target),
                "rows": len(rows),
                "sentences": len(keys),
                "cosine": metric_values(rows, cosine),
                "seconds": time.monotonic() - started,
            }
            _save(directory / "capture-status.json", summary)
            publications.append(
                pool.submit(
                    publish_resolved_files,
                    root,
                    destination,
                    {
                        "csts_comparison_diagnosis_20261028/inputs/"
                        + target.name: target
                    },
                )
            )
            print(
                "CONTROL_VECTORS_CAPTURED",
                split,
                summary["splits"][split]["cosine"],
                flush=True,
            )
        if any(p.requires_grad or p.grad is not None for p in model.parameters()):
            raise ValueError("Capture must leave every encoder parameter frozen.")
        del model
        torch.cuda.empty_cache()
        summary.update(status="complete", in_flight=None, cloud_status="pending")
        _save(directory / "capture-status.json", summary)
    receipts = {}
    for future in publications:
        receipts.update(
            {k: v.model_dump(mode="json") for k, v in future.result().items()}
        )
    pool.shutdown(wait=True)
    summary["cloud_status"] = "published"
    _save(directory / "capture-status.json", summary)
    _save(
        directory / "capture-publication.json",
        {"status": "published", "references": receipts},
    )


if __name__ == "__main__":
    main()
