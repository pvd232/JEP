"""Optional historical KnowCoder vLLM probe; one checkpoint per process.

Copies the fixed v2 repair prompts unchanged. This is prepared tooling, not a
claim of author-runtime reproduction until its declared version gates and run
complete. Generated Python is handled exclusively by the copied AST parser.
"""
from __future__ import annotations

import argparse
import collections
from datetime import datetime, timezone
from importlib import metadata
import json
import math
import hashlib
from pathlib import Path
import platform
import sys
import time
import traceback
from types import SimpleNamespace

from modern_parser_support import expected_shapes, list_node, parse, sha, write

REQUIRED_VERSIONS = {
    "vllm": "0.2.2+cu118", "torch": "2.1.0+cu118",
    "transformers": "4.34.1", "tokenizers": "0.14.1",
}
PACKAGES = tuple(REQUIRED_VERSIONS) + (
    "xformers", "huggingface-hub", "numpy", "ray", "pandas", "pyarrow",
    "sentencepiece", "einops", "psutil", "ninja", "pydantic", "protobuf",
)
METADATA_FILES = (
    "config.json", "generation_config.json", "tokenizer_config.json",
    "special_tokens_map.json", "tokenizer.json", "pytorch_model.bin.index.json",
)


def versions():
    """Reject an approximate modern runtime before any GPU/model imports."""
    actual = {}
    for name in PACKAGES:
        try:
            actual[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            actual[name] = None
    for name, required in REQUIRED_VERSIONS.items():
        if actual[name] != required:
            raise ValueError("Historical runtime gate: " + name + " requires "
                             + required + ", found " + str(actual[name]))
    return actual


def snapshot_metadata(snapshot, identity, pinned):
    """Check exact saved metadata and 291 indexed parameter names without load."""
    snapshot = snapshot.resolve()
    if snapshot.name != identity["revision"] or not snapshot.is_dir():
        raise ValueError("Existing snapshot directory must end with the pinned revision")
    for name in METADATA_FILES:
        if sha((snapshot / name).read_bytes()) != sha((pinned / name).read_bytes()):
            raise ValueError("Pinned snapshot metadata differs: " + name)
    config = json.loads((snapshot / "config.json").read_text())
    fields = {
        "architectures": ["LlamaForCausalLM"], "model_type": "llama",
        "hidden_size": 4096, "intermediate_size": 11008, "num_hidden_layers": 32,
        "num_attention_heads": 32, "num_key_value_heads": 32, "vocab_size": 32000,
        "max_position_embeddings": 4096, "rms_norm_eps": 1e-5, "hidden_act": "silu",
        "attention_bias": False, "tie_word_embeddings": False, "pretraining_tp": 1,
        "rope_theta": 10000.0, "rope_scaling": None, "torch_dtype": "float16",
        "bos_token_id": 1, "eos_token_id": 2,
    }
    for name, value in fields.items():
        if config.get(name) != value:
            raise ValueError("Pinned architecture mismatch: " + name)
    if config.get("auto_map") or config.get("mlp_bias", False):
        raise ValueError("Unexpected custom model mapping or MLP bias")
    shapes = expected_shapes(SimpleNamespace(**config))
    index = json.loads((snapshot / "pytorch_model.bin.index.json").read_text())
    if len(shapes) != 291 or set(index["weight_map"]) != set(shapes):
        raise ValueError("Pinned index must contain all 291 exact parameter names")
    if index["metadata"]["total_size"] != 13476831232:
        raise ValueError("Unexpected indexed FP16 tensor bytes")
    expected_shards = {"pytorch_model-00001-of-00002.bin", "pytorch_model-00002-of-00002.bin"}
    if set(index["weight_map"].values()) != expected_shards:
        raise ValueError("Unexpected checkpoint shard selection")
    info = json.loads((pinned / "model-info.json").read_text())
    if info["sha"] != identity["revision"]:
        raise ValueError("Pinned primary checkpoint metadata revision differs")
    weights = {
        row["rfilename"]: row for row in info["siblings"]
        if row["rfilename"] in expected_shards
    }
    if set(weights) != expected_shards:
        raise ValueError("Missing primary shard identities")
    return {
        "snapshot_path": str(snapshot), "config": config,
        "indexed_parameter_tensors": len(shapes),
        "architecture_derived_parameter_shapes": {k: list(v) for k, v in shapes.items()},
        "selected_shards": weights,
        "metadata_sha256": {name: sha((snapshot / name).read_bytes()) for name in METADATA_FILES},
        "verification_scope": "Pinned metadata and indexed names/shapes; individual live vLLM "
                              "tensor values and dtypes are not introspected.",
    }


def verify_weight_files(snapshot, audit):
    """Require existing complete shards; validate official cache object identities."""
    result = {}
    for name, primary in audit["selected_shards"].items():
        path = snapshot / name
        if not path.is_file() or path.stat().st_size != primary["lfs"]["size"]:
            raise ValueError("Pinned shard absent or has unexpected byte size: " + name)
        target = path.resolve()
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(block)
        recomputed = digest.hexdigest()
        if recomputed != primary["lfs"]["sha256"]:
            raise ValueError("Actual shard SHA256 differs from pinned identity: " + name)
        result[name] = {
            "size": path.stat().st_size, "expected_sha256": primary["lfs"]["sha256"],
            "resolved_path": str(target),
            "cache_basename_matches_expected_sha256": target.name == primary["lfs"]["sha256"],
            "full_file_hash_recomputed": True, "recomputed_sha256": recomputed,
        }
    return result


def diagnostic_number(value):
    """Retain nonfinite log-probability diagnostics without losing raw token IDs."""
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_float": repr(value)}
    return value


def author_projection(tokenizer, prompt_ids, output_ids):
    """Match author extract_generated_code for a prompt-token-ID request."""
    decoded = tokenizer.decode(prompt_ids + output_ids).strip()
    return decoded.split("Output:\n")[-1].strip().replace("</s>", "")


def parse_record(payload, fixture, variant):
    """Keep actual empty lists, schema failures and semantic review separate."""
    record = {"parse_status": "schema_or_literal_validation_failed",
              "empty_list_emitted": None, "semantic_status": "unreviewed"}
    try:
        try:
            record["empty_list_emitted"] = len(list_node(payload).elts) == 0
        except (ValueError, SyntaxError, RecursionError):
            pass
        rows = parse(payload, fixture, variant)
        target = [row for row in rows if fixture["target_class"] is None
                  or row[0] == fixture["target_class"]]
        anchors = variant["minimal_expected_anchors"]
        record.update(
            parse_status="valid", parsed_relations=rows, nonempty=bool(rows),
            target_class_records=target, target_class_nonempty=bool(target),
            anchors_present=all(row in rows for row in anchors) if anchors else None,
            exact_anchor_match=sorted(rows) == sorted(anchors),
            exact_target_anchor_match=sorted(target) == sorted(anchors),
            anchor_matches_are_descriptive_only=True,
        )
    except (ValueError, SyntaxError, RecursionError) as exc:
        record["error"] = str(exc)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", choices=("base", "ie"), required=True)
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    seal = json.loads((root / "seal.json").read_text())
    for name, digest in seal["files"].items():
        if sha((root / name).read_bytes()) != digest:
            raise ValueError("Sealed legacy probe changed: " + name)
    design = json.loads((root / "design.json").read_text())
    fixtures = json.loads((root / "fixtures.json").read_text())
    sources = json.loads((root / "sources.json").read_text())
    for fixture in fixtures:
        if fixture["source"] is not None and sources[fixture["source_index"]] != fixture["source"]:
            raise ValueError("Fixed source fixture changed")
    identity = design["checkpoints"][args.checkpoint]
    installed = versions()
    snapshot = args.snapshot_path.resolve()
    audit = snapshot_metadata(snapshot, identity, root / "pinned-metadata" / args.checkpoint)
    audit["shard_file_checks"] = verify_weight_files(snapshot, audit)
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "start.json", {
        "started_at": datetime.now(timezone.utc).isoformat(), "checkpoint": identity,
        "probe_seal_sha256": sha((root / "seal.json").read_bytes()),
        "installed_versions": installed, "snapshot_audit": audit,
        "primary_screen_unchanged": True, "expected_annotations_in_model_input": False,
        "purpose": "Optional historical-runtime diagnostic using unchanged v2 repair fixtures.",
        "generation_limit_amendment": "Author 640 output tokens replaces modern diagnostic 1024.",
        "attempts_per_cell": 1, "one_checkpoint_per_process": True,
        "representative_quality_score": False,
    })
    # Version and artifact gates complete before importing the GPU runtime.
    import torch
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tokenizer = AutoTokenizer.from_pretrained(
        str(snapshot), use_fast=True, legacy=False, padding_side="left",
        trust_remote_code=True,
    )
    cells = [(fixture, vid, variant) for fixture in fixtures
             for vid, variant in fixture["variants"].items()]
    provided_ids = [tokenizer.encode(variant["prompt"]) for _, _, variant in cells]
    for ids in provided_ids:
        if not ids or ids[0] != 1 or ids.count(1) != 1 or 2 in ids:
            raise ValueError("Author prompt must have one BOS and no EOS")
        if len(ids) + 640 > 4096:
            raise ValueError("No source truncation: prompt plus generation budget exceeds 4096")
    llm_kwargs = {
        "model": str(snapshot), "tokenizer_mode": "auto", "trust_remote_code": True,
        "max_num_seqs": 4, "max_model_len": 4096,
        "max_num_batched_tokens": 4 * 4096, "dtype": "auto",
        "gpu_memory_utilization": 0.6,
    }
    sampling_kwargs = {"n": 1, "best_of": 1, "temperature": 0.0,
                       "stop": '"""', "max_tokens": 640}
    write(args.output / "inputs.json", [
        {"fixture_id": fixture["fixture_id"], "variant": vid,
         "prompt": variant["prompt"], "provided_prompt_token_ids": ids}
        for (fixture, vid, variant), ids in zip(cells, provided_ids)
    ])
    llm = LLM(**llm_kwargs)
    engine_tokenizer = llm.get_tokenizer()
    for (_, _, variant), ids in zip(cells, provided_ids):
        if engine_tokenizer.encode(variant["prompt"]) != ids:
            raise ValueError("Engine tokenizer IDs differ from author input tokenizer")
    actual_dtype = str(llm.llm_engine.model_config.dtype)
    if actual_dtype != "torch.float16":
        raise ValueError("dtype=auto did not resolve to checkpoint float16")
    write(args.output / "runtime.json", {
        "python": sys.version, "platform": platform.platform(),
        "installed_versions": installed, "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "gpu_devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
        "llm_constructor_kwargs": llm_kwargs, "sampling_kwargs": sampling_kwargs,
        "resolved_model_dtype": actual_dtype,
        "engine_max_model_len": llm.llm_engine.model_config.max_model_len,
        "hf_config": llm.llm_engine.model_config.hf_config.to_dict(),
        "tokenizer_class": type(tokenizer).__name__,
        "engine_tokenizer_class": type(engine_tokenizer).__name__,
        "tokenizer_settings": {"use_fast": True, "legacy": False, "padding_side": "left"},
        "model_generation_config_applied": False,
        "individual_live_tensors_inspected": False,
        "runtime_status": "Historical declared core package versions; host driver/OS remain current.",
    })
    sampling = SamplingParams(**sampling_kwargs)
    started = time.monotonic()
    responses = llm.generate(prompt_token_ids=provided_ids, sampling_params=sampling)
    # Preserve every returned completion before enforcing any response invariant.
    write(args.output / "raw-batch.json", [
        {"request_id": response.request_id, "prompt": response.prompt,
         "actual_prompt_token_ids": list(response.prompt_token_ids),
         "finished": response.finished,
         "outputs": [
             {"index": item.index, "text": item.text,
              "token_ids": list(item.token_ids), "finish_reason": item.finish_reason,
              "cumulative_logprob": diagnostic_number(item.cumulative_logprob)}
             for item in response.outputs
         ]}
        for response in responses
    ])
    if len(responses) != len(cells):
        raise ValueError("Incomplete returned request count")
    completed = schema_failures = 0
    for (fixture, vid, variant), ids, response in zip(cells, provided_ids, responses):
        if list(response.prompt_token_ids) != ids:
            raise ValueError("Returned actual prompt token IDs differ from supplied IDs")
        if len(response.outputs) != 1 or not response.finished:
            raise ValueError("Expected exactly one finished completion per cell")
        completion = response.outputs[0]
        output_ids = list(completion.token_ids)
        raw = tokenizer.decode(output_ids, skip_special_tokens=False)
        decoded_no_specials = tokenizer.decode(output_ids, skip_special_tokens=True)
        author_payload = author_projection(tokenizer, ids, output_ids)
        generated = {
            "checkpoint": identity, "fixture_id": fixture["fixture_id"], "variant": vid,
            "prompt": variant["prompt"], "provided_prompt_token_ids": ids,
            "actual_prompt_token_ids": list(response.prompt_token_ids),
            "output_token_ids": output_ids, "input_tokens": len(ids), "output_tokens": len(output_ids),
            "api_text": completion.text, "raw_decode_with_special_tokens": raw,
            "raw_decode_without_special_tokens": decoded_no_specials,
            "author_extracted_code": author_payload,
            "finish_reason": completion.finish_reason, "request_id": response.request_id,
            "cumulative_logprob": diagnostic_number(completion.cumulative_logprob),
            "truncated": completion.finish_reason == "length",
        }
        stem = args.checkpoint + "-" + fixture["fixture_id"] + "-" + vid
        write(args.output / (stem + "-generation.json"), generated)
        result = {
            "checkpoint": identity, "fixture_id": fixture["fixture_id"], "variant": vid,
            "expected_nonempty": fixture["expected_nonempty"],
            "expected_anchor_relations": variant["minimal_expected_anchors"],
            "api_text_parse": parse_record(completion.text, fixture, variant),
            "author_projection_parse": parse_record(author_payload, fixture, variant),
            "truncated": generated["truncated"], "semantic_review_required": True,
            "parser_inputs_predeclared": "API text and exact author token-ID projection both retained; "
                                        "neither representation selected after results.",
        }
        write(args.output / (stem + "-result.json"), result)
        completed += 1
        schema_failures += int(result["api_text_parse"]["parse_status"] != "valid")
        print(json.dumps({"fixture_id": fixture["fixture_id"], "variant": vid,
                          "api_parse": result["api_text_parse"]["parse_status"],
                          "empty": result["api_text_parse"]["empty_list_emitted"]}), flush=True)
    write(args.output / "complete.json", {
        "completed_cells": completed, "api_schema_failures": schema_failures,
        "elapsed_batch_generation_seconds": time.monotonic() - started,
        "representative_quality_score": False,
    })
    # Process exit releases this checkpoint's GPU context; no second checkpoint loaded here.


if __name__ == "__main__":
    main()
