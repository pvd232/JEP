#!/usr/bin/env python3
"""Evaluate frozen JEP checkpoints with a shared color probe and vocabulary head."""

import argparse
from contextlib import nullcontext
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import socket
import sys
import time
import traceback

import numpy as np


MODEL_ID = "Qwen/Qwen3-Embedding-8B"
REVISION = "c90816d848505624c2434128dfc61132162a0ee9"
HEAD_SHA256 = "a36df847ac68cb10d636cac54bdd99c1d1b6627e98aca62dd5716bb87e6fee4d"
PROMPT = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
EOD = "<|endoftext|>"
WIDTH = 4096
MAX_LENGTH = 160
MAX_NEW_TOKENS = 64
STATE_RE = re.compile(r"seed([789])_([RP])_([AB])$")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def object_sha256(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("wb") as f:
        f.write(canonical(value))
        f.flush()
        os.fsync(f.fileno())
    temporary.replace(path)


def atomic_embeddings(path, ids, z):
    path = Path(path)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("wb") as f:
        np.savez(f, ids=np.asarray(ids, dtype=str), z=np.asarray(z, dtype=np.float32))
        f.flush()
        os.fsync(f.fileno())
    temporary.replace(path)


def validated_probe(path, preliminary):
    probe = json.loads(Path(path).read_text())
    rows = probe.get("inputs")
    if not isinstance(rows, list) or not rows:
        raise ValueError("The probe requires conditioned caption inputs.")
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Probe input identities must be unique.")
    for row in rows:
        if not all(isinstance(row.get(k), str) and row[k] for k in ["id", "caption", "condition"]):
            raise ValueError("Each input requires an identity, caption and condition.")
    review = probe.get("human_review")
    complete = (isinstance(review, dict) and review.get("status") == "two_humans_agree"
                and len(set(review.get("raters", []))) == 2)
    if not preliminary and not complete:
        raise ValueError("Human review is pending. Pass --preliminary for the model-authored diagnostic.")
    return probe


def validated_models(path):
    value = json.loads(Path(path).read_text())
    if isinstance(value, dict):
        value = value.get("models", value.get("states"))
    if not isinstance(value, list):
        raise ValueError("The models manifest requires a list or a models/states list field.")
    if not any(x.get("name") == "base" for x in value):
        value = [{"name": "base", "seed": None, "arm": None, "phase": None}, *value]
    names = [s["name"] for s in value]
    expected = {"base"} | {f"seed{k}_{a}_{p}" for k in [7, 8, 9] for a in "RP" for p in "AB"}
    if len(names) != 13 or set(names) != expected:
        raise ValueError("The manifest must identify the shared base and four checkpoints for each of seeds 7, 8 and 9.")
    result = []
    for supplied in value:
        s = dict(supplied)
        if s["name"] == "base":
            if s.get("path") or s.get("sha256"):
                raise ValueError("The shared pretrained state uses the pinned base model.")
            s.update(seed=None, arm=None, phase=None, sha256=None)
        else:
            match = STATE_RE.fullmatch(s["name"])
            seed, arm, phase = int(match[1]), match[2], match[3]
            for key, required in [("seed", seed), ("arm", arm), ("phase", phase)]:
                if key in s and s[key] != required:
                    raise ValueError(f"Model identity disagrees with its name: {s['name']} {key}")
                s[key] = required
            if not re.fullmatch(r"[0-9a-f]{64}", s.get("sha256", "")):
                raise ValueError("Each adapter checkpoint requires a SHA-256 identity.")
            checkpoint = Path(s["path"]).resolve()
            if sha256(checkpoint) != s["sha256"]:
                raise ValueError(f"Checkpoint bytes differ: {s['name']}")
            s["path"] = str(checkpoint)
            s["bytes"] = checkpoint.stat().st_size
        result.append(s)
    order = ["base"] + [f"seed{k}_{a}_{p}" for k in [7, 8, 9] for p in "AB" for a in "RP"]
    return sorted(result, key=lambda s: order.index(s["name"]))


def validate_arrays(ids, z, expected_ids):
    ids = list(map(str, ids))
    if ids != list(expected_ids):
        raise ValueError("Saved embedding input order differs from the frozen probe.")
    if z.shape != (len(ids), WIDTH) or z.dtype != np.float32:
        raise ValueError("Embeddings require the original width and float32 storage.")
    if not np.isfinite(z).all() or not np.allclose(np.linalg.norm(z, axis=1), 1, atol=2e-5, rtol=2e-5):
        raise ValueError("Embeddings require finite values and unit norms.")


def read_saved(directory, expected_ids, contract_sha, state_sha, complete=False):
    directory = Path(directory)
    receipt_path = directory / "receipt.json"
    if not receipt_path.exists():
        return None
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") != ("complete" if complete else "batch_complete"):
        raise ValueError("Saved inference receipt has an unexpected completion status.")
    if receipt.get("contract_sha256") != contract_sha or receipt.get("state_sha256") != state_sha:
        raise ValueError("Saved inference belongs to a different frozen run or model state.")
    for name, key in [("predictions.json", "predictions_sha256"), ("embeddings.npz", "embeddings_sha256")]:
        if sha256(directory / name) != receipt.get(key):
            raise ValueError(f"Saved inference bytes differ: {directory / name}")
    predictions = json.loads((directory / "predictions.json").read_text())
    if [r["id"] for r in predictions] != list(expected_ids):
        raise ValueError("Saved readout input order differs from the frozen probe.")
    with np.load(directory / "embeddings.npz", allow_pickle=False) as data:
        z = data["z"].copy()
        validate_arrays(data["ids"], z, expected_ids)
    return predictions, z, receipt


def write_saved(directory, predictions, z, receipt):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    ids = [r["id"] for r in predictions]
    z = np.asarray(z, dtype=np.float32)
    validate_arrays(ids, z, ids)
    atomic_json(directory / "predictions.json", predictions)
    atomic_embeddings(directory / "embeddings.npz", ids, z)
    receipt = dict(receipt, predictions_sha256=sha256(directory / "predictions.json"),
                   embeddings_sha256=sha256(directory / "embeddings.npz"), input_count=len(ids))
    atomic_json(directory / "receipt.json", receipt)
    return receipt


class GenerationTracker:
    """Retain each sequence through its first stop token or the shared token ceiling."""

    def __init__(self, count, stop_ids):
        self.ids = [[] for _ in range(count)]
        self.stopped = [False] * count
        self.stop_ids = set(stop_ids)

    def append(self, next_ids):
        if len(next_ids) != len(self.ids):
            raise ValueError("Generation changed batch width.")
        for n, token in enumerate(next_ids):
            if not self.stopped[n]:
                self.ids[n].append(int(token))
                if token in self.stop_ids:
                    self.stopped[n] = True
        return all(self.stopped)


def token_sequences(tokenizer, rows):
    texts = [PROMPT.format(condition=r["condition"], passage=r["caption"]) for r in rows]
    sequences = tokenizer(texts, padding=False, truncation=False, add_special_tokens=False)["input_ids"]
    eod = tokenizer.get_vocab().get(EOD)
    if eod is None:
        raise ValueError("The pinned tokenizer requires its original EOD token.")
    if any(len(ids) + 1 > MAX_LENGTH for ids in sequences):
        raise ValueError("A probe prefix exceeds the frozen 160-token ceiling.")
    return [[*ids, eod] for ids in sequences]


def generate_batch(model, head, tokenizer, sequences, stop_ids, torch, max_tokens=MAX_NEW_TOKENS):
    """Pool the prefix EOD and greedily decode its continuation with a KV cache."""
    batch = tokenizer.pad({"input_ids": sequences, "attention_mask": [[1] * len(s) for s in sequences]},
                          padding=True, return_tensors="pt")
    input_ids = batch["input_ids"].to("cuda")
    mask = batch["attention_mask"].to("cuda")
    prefix_width = input_ids.shape[1]
    # Match Qwen's original forward default: padded positions use the batch's
    # absolute arange. All attended tokens retain their relative positions.
    positions = torch.arange(prefix_width, device="cuda").unsqueeze(0)
    tracker = GenerationTracker(len(sequences), stop_ids)
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
        output = model(input_ids=input_ids, attention_mask=mask, position_ids=positions,
                       use_cache=True, return_dict=True)
        raw = output.last_hidden_state[:, -1, :]
        pooled = raw.float()
        norms = pooled.norm(dim=-1, keepdim=True)
        if not torch.isfinite(pooled).all().item() or (norms == 0).any().item():
            raise ValueError("The model returned an invalid prefix embedding.")
        z = (pooled / norms).cpu().numpy().astype(np.float32, copy=False)
        if output.past_key_values is None:
            raise ValueError("Cached generation requires model past_key_values.")
        for step in range(max_tokens):
            chosen = head(raw).argmax(dim=-1)
            if tracker.append(chosen.tolist()) or step + 1 == max_tokens:
                break
            # Finished rows stay in the batch. Their later logits are ignored.
            mask = torch.cat([mask, torch.ones((len(sequences), 1), device="cuda", dtype=mask.dtype)], dim=1)
            positions = torch.full((1, 1), prefix_width + step, dtype=torch.long, device="cuda")
            output = model(input_ids=chosen[:, None], attention_mask=mask, position_ids=positions,
                           past_key_values=output.past_key_values, use_cache=True, return_dict=True)
            raw = output.last_hidden_state[:, -1, :]
    answers = [dict(answer=tokenizer.decode(tokens, skip_special_tokens=True),
                    generated_tokens=len(tokens), generated_token_ids=tokens, stopped_on_eos=stopped)
               for tokens, stopped in zip(tracker.ids, tracker.stopped)]
    return answers, z


def load_runtime(args):
    import torch
    from peft import LoraConfig, TaskType, get_peft_model
    from safetensors.torch import load_file
    from transformers import AutoModel, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("The frozen BF16 run requires a CUDA GPU.")
    free, total = torch.cuda.mem_get_info()
    if free < args.minimum_free_gib * 1024 ** 3:
        raise RuntimeError(f"GPU has {free / 1024**3:.2f} GiB free; {args.minimum_free_gib:.2f} GiB requested.")
    torch.set_num_threads(args.cpu_threads)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    source = MODEL_ID
    if args.model_dir:
        source = str(args.model_dir.resolve())
        if Path(source).name != REVISION:
            raise ValueError("A local model directory must identify the exact pinned snapshot revision.")
    tokenizer = AutoTokenizer.from_pretrained(source, revision=REVISION, padding_side="left",
                                               trust_remote_code=False, local_files_only=args.offline)
    if tokenizer.padding_side != "left":
        raise ValueError("Cached generation requires left-padded prefixes.")
    started = time.monotonic()
    backbone = AutoModel.from_pretrained(source, revision=REVISION, dtype=torch.bfloat16,
                                         attn_implementation="sdpa", device_map={"": "cuda"},
                                         trust_remote_code=False, local_files_only=args.offline)
    if backbone.config.hidden_size != WIDTH:
        raise ValueError("The base model width differs from the frozen encoder.")
    model = get_peft_model(backbone, LoraConfig(task_type=TaskType.FEATURE_EXTRACTION,
        r=32, lora_alpha=32, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], bias="none"))
    adapters = {n: p for n, p in model.named_parameters() if p.requires_grad}
    if not adapters or any("lora_" not in n for n in adapters):
        raise ValueError("The model requires the original attention-only LoRA parameters.")
    model.requires_grad_(False)
    model.eval()
    model.config.use_cache = True
    weight = load_file(str(args.head), device="cpu")
    if set(weight) != {"weight"} or weight["weight"].ndim != 2 or weight["weight"].shape[1] != WIDTH:
        raise ValueError("The shared vocabulary head differs from the frozen head layout.")
    vocab_weight = weight["weight"]
    if max(tokenizer.get_vocab().values()) >= vocab_weight.shape[0]:
        raise ValueError("The shared head does not cover the pinned tokenizer's vocabulary.")
    head = torch.nn.Linear(WIDTH, vocab_weight.shape[0], bias=False, device="meta")
    head.weight = torch.nn.Parameter(vocab_weight.to("cuda", dtype=torch.bfloat16), requires_grad=False)
    head.eval()
    torch.cuda.synchronize()
    load_seconds = time.monotonic() - started
    stop_ids = {tokenizer.get_vocab()[EOD]}
    for value in [tokenizer.eos_token_id, getattr(model.config, "eos_token_id", None)]:
        stop_ids.update(value if isinstance(value, list) else ([] if value is None else [value]))
    versions = {}
    for name in ["torch", "transformers", "peft", "safetensors", "numpy", "accelerate"]:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "unavailable"
    environment = dict(hostname=socket.gethostname(), python=sys.version, platform=platform.platform(),
        packages=versions, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(),
        gpu_total_bytes=total, gpu_initial_free_bytes=free, model_source=source,
        head_vocabulary_rows=int(head.weight.shape[0]), stop_token_ids=sorted(stop_ids))
    return torch, model, adapters, head, tokenizer, stop_ids, environment, load_seconds


def restore_checkpoint(state, parameters, torch):
    if state["name"] == "base":
        return {}
    saved = torch.load(state["path"], map_location="cpu", weights_only=True)
    config = saved.get("config", {})
    required = dict(model_id=MODEL_ID, revision=REVISION, embedding_dimension=WIDTH,
                    max_length=MAX_LENGTH, lora_rank=32, lora_alpha=32, lora_dropout=0.05)
    if any(config.get(k) != value for k, value in required.items()) or saved.get("kind") != "lora":
        raise ValueError(f"Saved checkpoint settings differ: {state['name']}")
    weights = saved["state"]
    if weights.keys() != parameters.keys():
        raise ValueError(f"Adapter parameter names differ: {state['name']}")
    with torch.no_grad():
        for name, parameter in parameters.items():
            value = weights[name]
            if value.shape != parameter.shape or not torch.isfinite(value).all().item():
                raise ValueError("Invalid saved adapter tensor: " + name)
            parameter.copy_(value.to(device=parameter.device, dtype=parameter.dtype))
    return dict(epoch=saved["epoch"], step=saved["step"])


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    lock = (args.output / "run.lock").open("w")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise RuntimeError("A diagnostic inference process already owns this output directory.") from error
    lock.write(str(os.getpid()) + "\n")
    lock.flush()
    probe = validated_probe(args.probe, args.preliminary)
    states = validated_models(args.models)
    if sha256(args.head) != HEAD_SHA256:
        raise ValueError("The vocabulary-head bytes differ from the frozen shared head.")
    probe_sha = sha256(args.probe)
    contract = dict(schema_version=1, probe_sha256=probe_sha, models_manifest_sha256=sha256(args.models),
        runner_sha256=sha256(__file__), parser_sha256=sha256(Path(__file__).with_name("probe.py")),
        model_id=MODEL_ID, revision=REVISION, head_sha256=HEAD_SHA256,
        max_length=MAX_LENGTH, max_new_tokens=MAX_NEW_TOKENS, prompt=PROMPT, eod=EOD,
        dtype="bfloat16", attention="sdpa", pooling="prefix_final_eod_float32_unit_norm",
        positions="padded_absolute_arange_matching_original_encoder_forward",
        batch_size=args.batch_size, preliminary=args.preliminary,
        label_source=probe.get("label_source"), human_review=probe.get("human_review"),
        states=[{k: s.get(k) for k in ["name", "seed", "arm", "phase", "sha256"]} for s in states])
    contract_sha = object_sha256(contract)
    existing = args.output / "run_contract.json"
    if existing.exists() and json.loads(existing.read_text()) != contract:
        raise ValueError("This output directory belongs to a different frozen run. Choose a new output directory.")
    atomic_json(existing, contract)
    rows = probe["inputs"]
    ids = [r["id"] for r in rows]
    state_shas = {s["name"]: object_sha256({k: s.get(k) for k in ["name", "seed", "arm", "phase", "sha256"]}) for s in states}
    completed = {}
    for state in states:
        saved = read_saved(args.output/state["name"], ids, contract_sha, state_shas[state["name"]], complete=True)
        if saved:
            completed[state["name"]] = saved[2]
    selected = states[:args.max_states] if args.max_states else states
    started = time.monotonic()
    status = dict(pid=os.getpid(), status="preflight_complete", preliminary=args.preliminary,
                  label_source=probe.get("label_source"), human_review=probe.get("human_review"),
                  contract_sha256=contract_sha, probe_sha256=probe_sha,
                  total_states=len(states), inputs_per_state=len(rows), completed_states=list(completed))

    def progress(**changes):
        status.update(changes)
        status["updated_unix"] = time.time()
        status["session_elapsed_seconds"] = time.monotonic()-started
        atomic_json(args.output/"status.json", status)
        print(json.dumps(status, sort_keys=True, ensure_ascii=False, allow_nan=False), flush=True)

    progress()
    remaining = [s for s in selected if s["name"] not in completed]
    if not remaining:
        progress(status="complete" if len(completed)==len(states) else "requested_state_limit_complete")
        return
    torch, model, parameters, head, tokenizer, stop_ids, environment, load_seconds = load_runtime(args)
    atomic_json(args.output/"environment.json", environment)
    sequences = token_sequences(tokenizer, rows)
    progress(status="model_loaded", model_load_seconds=load_seconds, environment=environment)
    # Separate initial GPU kernel warm-up from the measured inference batches.
    warm = time.monotonic()
    with model.disable_adapter():
        generate_batch(model, head, tokenizer, sequences[:min(2,len(rows))], stop_ids, torch, max_tokens=4)
    torch.cuda.synchronize()
    warmup_seconds = time.monotonic()-warm
    generated_inputs = sum(r.get("input_count", 0) for r in completed.values())
    generation_seconds = sum(r.get("generation_seconds", 0) for r in completed.values())
    benchmark_batches = 0
    try:
        for state in remaining:
            directory = args.output/state["name"]
            directory.mkdir(parents=True, exist_ok=True)
            checkpoint_started = time.monotonic()
            counters = restore_checkpoint(state, parameters, torch)
            torch.cuda.synchronize()
            checkpoint_seconds = time.monotonic()-checkpoint_started
            torch.cuda.reset_peak_memory_stats()
            state_predictions, state_z, batch_receipts = [], [], []
            context = model.disable_adapter() if state["name"] == "base" else nullcontext()
            with context:
                for start in range(0, len(rows), args.batch_size):
                    stop = min(start+args.batch_size, len(rows))
                    batch_directory = directory/"batches"/f"{start:05d}"
                    saved = read_saved(batch_directory, ids[start:stop], contract_sha, state_shas[state["name"]])
                    if saved:
                        predictions, z, receipt = saved
                    else:
                        torch.cuda.synchronize()
                        before = time.monotonic()
                        answers, z = generate_batch(model, head, tokenizer, sequences[start:stop], stop_ids, torch)
                        torch.cuda.synchronize()
                        elapsed = time.monotonic()-before
                        predictions = [dict(id=row["id"], **answer) for row, answer in zip(rows[start:stop], answers)]
                        receipt = write_saved(batch_directory, predictions, z,
                            dict(status="batch_complete", probe_sha256=probe_sha, contract_sha256=contract_sha,
                                 state_sha256=state_shas[state["name"]], state=state, preliminary=args.preliminary,
                                 generation_seconds=elapsed, created_unix=time.time()))
                        benchmark_batches += 1
                    state_predictions.extend(predictions)
                    state_z.append(z)
                    batch_receipts.append(receipt)
                    current_inputs = sum(r["input_count"] for r in batch_receipts)
                    current_seconds = sum(r["generation_seconds"] for r in batch_receipts)
                    measured_inputs = generated_inputs+current_inputs
                    measured_seconds = generation_seconds+current_seconds
                    completed_inputs = len(completed)*len(rows)+current_inputs
                    eta = max(0, len(states)*len(rows)-completed_inputs)*measured_seconds/measured_inputs
                    progress(status="running", current_state=state["name"],
                             current_state_completed_inputs=current_inputs, completed_inputs=completed_inputs,
                             completed_states=list(completed), warmup_seconds=warmup_seconds,
                             measured_generation_seconds=measured_seconds, measured_generation_inputs=measured_inputs,
                             eta_remaining_generation_seconds=eta,
                             generated_tokens_current_batch=sum(r["generated_tokens"] for r in predictions),
                             gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated())
                    if args.benchmark_batches and benchmark_batches >= args.benchmark_batches:
                        progress(status="benchmark_complete")
                        return
            final = write_saved(directory, state_predictions, np.concatenate(state_z, axis=0),
                dict(status="complete", state=state, probe_sha256=probe_sha, contract_sha256=contract_sha,
                     state_sha256=state_shas[state["name"]], preliminary=args.preliminary,
                     label_source=probe.get("label_source"), human_review=probe.get("human_review"),
                     generation_seconds=sum(r["generation_seconds"] for r in batch_receipts),
                     checkpoint_load_seconds=checkpoint_seconds, checkpoint_counters=counters,
                     batch_receipts_sha256=[object_sha256(r) for r in batch_receipts],
                     gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(), completed_unix=time.time()))
            completed[state["name"]] = final
            generated_inputs += final["input_count"]
            generation_seconds += final["generation_seconds"]
            progress(status="state_complete", completed_states=list(completed),
                     current_state_completed_inputs=len(rows), completed_inputs=len(completed)*len(rows))
        progress(status="complete" if len(completed)==len(states) else "requested_state_limit_complete",
                 completed_states=list(completed), completed_inputs=len(completed)*len(rows),
                 eta_remaining_generation_seconds=0 if len(completed)==len(states) else status.get("eta_remaining_generation_seconds"))
    except BaseException as error:
        progress(status="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                 error_type=type(error).__name__, error=str(error))
        raise


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--head", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preliminary", action="store_true")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--cpu-threads", type=int, default=2)
    parser.add_argument("--minimum-free-gib", type=float, default=18)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--max-states", type=int)
    parser.add_argument("--benchmark-batches", type=int)
    args = parser.parse_args()
    for name in ["batch_size", "cpu_threads"]:
        if getattr(args, name) < 1:
            parser.error(name+" requires a positive integer")
    for name in ["max_states", "benchmark_batches"]:
        value = getattr(args, name)
        if value is not None and value < 1:
            parser.error(name+" requires a positive integer")
    return args


if __name__ == "__main__":
    try:
        run(parse_args())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
