"""Restore a pinned Qwen vocabulary head without downloading the full language model."""

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from typing import Any

BASE = "Qwen/Qwen3-8B-Base"
REVISION = "49e3418fbbbca6ecbdf9608b4d22e5a407081db4"
EMBEDDING = "Qwen/Qwen3-Embedding-8B"
EMBEDDING_REVISION = "c90816d848505624c2434128dfc61132162a0ee9"


def digest(path: Path) -> str:
    """Hash bytes in bounded memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch(url: str, path: Path, byte_range: tuple[int, int] | None = None) -> None:
    """Use platform TLS roots; require exact byte counts for range responses."""
    args = [
        "curl",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--retry",
        "2",
        "--connect-timeout",
        "15",
        "--max-time",
        "1800",
    ]
    if byte_range is not None:
        start, end = byte_range
        args += [
            "--range",
            f"{start}-{end}",
            "--max-filesize",
            str(max(end - start + 1, 1_000_000)),
        ]
        url += f"?download=true&part={start}-{end}"
    subprocess.run([*args, "--output", str(path), url], check=True)
    if (
        byte_range is not None
        and path.stat().st_size != byte_range[1] - byte_range[0] + 1
    ):
        raise ValueError("The server did not return the exact requested tensor bytes.")


def vocabulary(document: dict[str, Any]) -> dict[str, int]:
    """Include added tokens when checking the vocabulary-to-head mapping."""
    result = dict(document["model"]["vocab"])
    result.update({token["content"]: token["id"] for token in document["added_tokens"]})
    return result


def prepare(directory: Path) -> dict[str, Any]:
    """Check token identities, then retain the supported pretrained head rows."""
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "qwen-evidence-head.safetensors"
    manifest = directory / "qwen-evidence-head.json"
    if output.exists() or manifest.exists():
        if not output.exists() or not manifest.exists():
            raise ValueError(
                "Incomplete head preparation; preserve and inspect the files."
            )
        saved = json.loads(manifest.read_text())
        if saved["sha256"] != digest(output) or saved["head_revision"] != REVISION:
            raise ValueError("Existing head identity differs.")
        return saved
    base_url = f"https://huggingface.co/{BASE}/resolve/{REVISION}/"
    embedding_url = f"https://huggingface.co/{EMBEDDING}/resolve/{EMBEDDING_REVISION}/"
    for name, url in (
        ("base-tokenizer.json", base_url + "tokenizer.json"),
        ("embedding-tokenizer.json", embedding_url + "tokenizer.json"),
        ("embedding-config.json", embedding_url + "config.json"),
        ("base-index.json", base_url + "model.safetensors.index.json"),
    ):
        fetch(url, directory / name)
    embedding_config = json.loads((directory / "embedding-config.json").read_text())
    n, width = embedding_config["vocab_size"], embedding_config["hidden_size"]
    source_vocab = vocabulary(
        json.loads((directory / "base-tokenizer.json").read_text())
    )
    target_vocab = vocabulary(
        json.loads((directory / "embedding-tokenizer.json").read_text())
    )
    supported = {token: index for token, index in target_vocab.items() if index < n}
    if set(supported.values()) != set(range(n)) or any(
        source_vocab.get(t) != i for t, i in supported.items()
    ):
        raise ValueError(
            "The embedding and generation vocabularies are not identical on every supported row."
        )
    index = json.loads((directory / "base-index.json").read_text())
    shard = index["weight_map"]["lm_head.weight"]
    url = base_url + shard
    print(
        json.dumps({"status": "tokenizers_verified", "rows": n, "head_shard": shard}),
        flush=True,
    )
    fetch(url, directory / "header-length.bin", (0, 7))
    header_length = struct.unpack("<Q", (directory / "header-length.bin").read_bytes())[
        0
    ]
    if not 0 < header_length < 10_000_000:
        raise ValueError("Unexpected safetensors header length.")
    fetch(url, directory / "header.json", (8, 7 + header_length))
    header = json.loads((directory / "header.json").read_bytes())
    tensor = header["lm_head.weight"]
    if (
        tensor["dtype"] != "BF16"
        or tensor["shape"][1] != width
        or tensor["shape"][0] < n
    ):
        raise ValueError("The original head has an incompatible shape or dtype.")
    start = 8 + header_length + tensor["data_offsets"][0]
    byte_count = n * width * 2
    raw = directory / "head-rows.bin"
    fetch(url, raw, (start, start + byte_count - 1))
    new_header = json.dumps(
        {
            "weight": {
                "dtype": "BF16",
                "shape": [n, width],
                "data_offsets": [0, byte_count],
            }
        },
        separators=(",", ":"),
    ).encode()
    new_header += b" " * (-len(new_header) % 8)
    temporary = output.with_suffix(".tmp")
    with temporary.open("wb") as stream, raw.open("rb") as source:
        stream.write(struct.pack("<Q", len(new_header)))
        stream.write(new_header)
        while chunk := source.read(8 * 1024 * 1024):
            stream.write(chunk)
    temporary.replace(output)
    result = {
        "head_model_id": BASE,
        "head_revision": REVISION,
        "head_shard": shard,
        "embedding_model_id": EMBEDDING,
        "embedding_revision": EMBEDDING_REVISION,
        "shape": [n, width],
        "all_supported_token_ids_identical": True,
        "tokenizer_sha256": {
            k: digest(directory / k)
            for k in ("base-tokenizer.json", "embedding-tokenizer.json")
        },
        "sha256": digest(output),
        "frozen_during_training": True,
    }
    manifest.write_text(json.dumps(result, indent=2) + "\n")
    raw.unlink()
    print(json.dumps({"status": "head_ready", **result}), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    prepare(args.directory)
