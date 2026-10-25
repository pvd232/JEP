"""Inspect saved FLAN/Qwen evidence checkpoints on one fixed development cohort."""

import collections
import datetime
import gc
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace

os.environ.setdefault("HF_HOME", "/home/machina/jep-model-cache")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
QROOT = Path("/home/machina/jep-csts-qwen-evidence-20261024")
FROOT = Path("/home/machina/jep-csts-tranche3-20261024")
OUT = Path("/home/machina/jep-qwen-evidence-control-20261024/answer-inspection-20261025")
sys.path.insert(0, str(QROOT))

import torch
from transformers import AutoTokenizer

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EOD,
    FitConfig,
    load_backbone,
    load_tokenizer,
    restore_parameters,
    token_sequences,
)
from csts_pilot.evidence_controls import checked_cache
from csts_pilot.joint import AnswerEncoder
from csts_pilot.qwen_evidence import answer_loss_sum, load_head
from csts_pilot.training import CstsConfig, prepare_tokens


def write(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def state(**kw):
    write(OUT / "progress.json", {
        "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pid": os.getpid(), **kw,
    })
    print(json.dumps(kw), flush=True)


def normalized(text):
    return re.findall(r"\w+", text.casefold())


def agreement(pred, reference):
    a, b = normalized(pred), normalized(reference)
    n = sum((collections.Counter(a) & collections.Counter(b)).values())
    f1 = 2 * n / (len(a) + len(b)) if a or b else 1.0
    return {"teacher_exact_match": a == b, "teacher_token_f1": f1}


def checkpoint(root, arm, phase):
    artifact = "last_model" if phase == "pretrain" else "model"
    found = list((root / "experiments").glob(
        f"*_{arm}_{phase}/runs/*/*/artifacts/train/{artifact}/model.pt"
    ))
    if len(found) != 1:
        raise ValueError(f"Expected exactly one checkpoint: {root}, {arm}, {phase}")
    path = found[0]
    trace = json.loads((path.parents[1] / "trace/trace.json").read_text())
    expected = (trace.get("terminal_sha256") or trace.get("terminal_model_sha256")) \
        if phase == "pretrain" else trace["selected"]["sha256"]
    if sha(path) != expected:
        raise ValueError("Checkpoint differs from the actual phase transition or selection")
    if phase == "pretrain":
        directory = root / ("qwen_evidence_results" if root == QROOT else "evidence_results") / "initial"
        next_trace = json.loads((directory / f"{arm}_ratings_trace.json").read_text())
        parent = next_trace.get("parent_sha256") or next_trace.get("initial_sha256")
        if expected != parent:
            raise ValueError("Phase-A checkpoint differs from the actual phase-B input")
    return path


def cohort():
    settings = json.loads((QROOT / "configs/csts-qwen-evidence.json").read_text())
    dev = json.loads((QROOT / settings["splits"]["validation"]["path"]).read_text())
    train = json.loads((QROOT / settings["splits"]["training"]["path"]).read_text())
    for name in ("training", "validation"):
        info = settings["splits"][name]
        if sha(QROOT / info["path"]) != info["sha256"]:
            raise ValueError("Source split changed")
    cache = checked_cache(QROOT / settings["answers"]["path"])
    if sha(QROOT / settings["answers"]["path"]) != settings["answers"]["sha256"]:
        raise ValueError("Teacher cache changed")
    training_groups = {r["group_id"] for r in train}
    training_keys = {answer_id(r[s], r["condition"]) for r in train
                     for s in ("sentence1", "sentence2")}
    items = {}
    for row in dev:
        if row["group_id"] in training_groups:
            raise ValueError("Training source group overlaps development")
        for side in ("sentence1", "sentence2"):
            key = answer_id(row[side], row["condition"])
            if key in training_keys:
                raise ValueError("Training passage-condition overlaps development")
            if cache[key]["valid"]:
                items[key] = {
                    "id": key, "row_id": row["row_id"], "group_id": row["group_id"],
                    "condition": row["condition"], "passage": row[side],
                    "teacher_answer": cache[key]["answer"],
                }
    ordered = sorted(items.values(), key=lambda x: hashlib.sha256(
        ("heldout-answer-inspection-20261025:" + x["id"]).encode()).hexdigest())
    selected, seen, counts = [], set(), collections.Counter()
    for item in ordered:
        if item["group_id"] in seen or counts[item["condition"]] >= 2:
            continue
        selected.append(item)
        seen.add(item["group_id"])
        counts[item["condition"]] += 1
        if len(selected) == 50:
            break
    if len(selected) != 50:
        raise ValueError("Insufficient distinct development groups")
    return settings, selected


def existing_records():
    p = OUT / "generations.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def save_record(record):
    with (OUT / "generations.jsonl").open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@torch.inference_mode()
def qwen_generate(model, head, prefix, eos, max_tokens=64, cached=True):
    generated, past = [], None
    for _ in range(max_tokens):
        ids = prefix + generated if past is None or not cached else generated[-1:]
        batch = {
            "input_ids": torch.tensor([ids], device="cuda"),
            "attention_mask": torch.ones((1, len(prefix) + len(generated)),
                                          device="cuda", dtype=torch.long),
            "use_cache": cached,
        }
        if past is not None and cached:
            batch["past_key_values"] = past
        result = model(**batch)
        next_id = int(head(result.last_hidden_state[:, -1]).float().argmax(-1).item())
        generated.append(next_id)
        if next_id in eos:
            break
        past = result.past_key_values if cached else None
    return generated


def run_qwen(settings, items, done):
    paths = {p: checkpoint(QROOT, "evidence", p) for p in ("pretrain", "ratings")}
    saved = torch.load(paths["pretrain"], map_location="cpu", weights_only=True)
    config = FitConfig.model_validate(saved["config"])
    state(status="loading", model="qwen", phase="pretrain")
    tokenizer = load_tokenizer(config)
    model = load_backbone(config, adapters=config)
    model.gradient_checkpointing_disable()
    model.eval()
    head = load_head(QROOT / settings["head"]["path"], SimpleNamespace(
        head_sha256=settings["head"]["sha256"],
        embedding_dimension=config.embedding_dimension, device="cuda",
    ))
    prefixes = token_sequences(tokenizer, [(x["condition"], x["passage"]) for x in items], config)
    end = tokenizer.get_vocab()[EOD]
    eos = {end, tokenizer.eos_token_id}
    for token in ("<|im_end|>",):
        if token in tokenizer.get_vocab():
            eos.add(tokenizer.get_vocab()[token])
    metadata = {"model_id": config.model_id,
                "parameters_with_adapters": sum(p.numel() for p in model.parameters()),
                "generation_head_parameters": sum(p.numel() for p in head.parameters())}
    for phase in ("pretrain", "ratings"):
        saved = torch.load(paths[phase], map_location="cpu", weights_only=True)
        restore_parameters(model, saved["state"])
        model.eval()
        model.config.use_cache = True
        if phase == "pretrain":
            a = qwen_generate(model, head, prefixes[0], eos, max_tokens=4, cached=True)
            b = qwen_generate(model, head, prefixes[0], eos, max_tokens=4, cached=False)
            if a != b:
                raise ValueError(f"Cached decoding changed greedy tokens: {a}, {b}")
            metadata["cache_smoke_tokens_match"] = True
        for index, (item, prefix) in enumerate(zip(items, prefixes, strict=True)):
            if ("qwen", phase, item["id"]) in done:
                continue
            started = time.monotonic()
            with torch.inference_mode():
                tokens = qwen_generate(model, head, prefix, eos)
                answer = tokenizer.decode(tokens, skip_special_tokens=True).strip()
                targets = tokenizer(item["teacher_answer"], add_special_tokens=False)["input_ids"] + [end]
                all_ids = prefix + targets
                labels = torch.tensor([[-100] * len(prefix) + targets], device="cuda")
                hidden = model(input_ids=torch.tensor([all_ids], device="cuda"),
                               attention_mask=torch.ones((1, len(all_ids)), device="cuda", dtype=torch.long),
                               use_cache=False).last_hidden_state
                ce = float(answer_loss_sum(hidden, labels, head))
            record = {**item, "model": "qwen", "phase": phase, "answer": answer,
                      "teacher_answer_ce": ce, "tokens": len(tokens),
                      "stopped_on_eos": tokens[-1] in eos,
                      "seconds": time.monotonic() - started,
                      **agreement(answer, item["teacher_answer"])}
            save_record(record)
            if index % 10 == 9:
                state(status="running", model="qwen", phase=phase, completed=index + 1, total=50)
        metadata[phase] = {"checkpoint": str(paths[phase]), "sha256": sha(paths[phase]),
                           "checkpoint_epoch": saved["epoch"]}
    del model, head, saved
    gc.collect()
    torch.cuda.empty_cache()
    return metadata


def run_flan(items, done):
    paths = {p: checkpoint(FROOT, "evidence", p) for p in ("pretrain", "ratings")}
    saved = torch.load(paths["pretrain"], map_location="cpu", weights_only=True)
    config = CstsConfig.model_validate({k: v for k, v in saved["config"].items()
                                       if k in CstsConfig.model_fields})
    state(status="loading", model="flan", phase="pretrain")
    tokenizer = AutoTokenizer.from_pretrained(config.model_id, revision=config.revision, use_fast=True)
    model = AnswerEncoder(config).to("cuda").eval()
    metadata = {"model_id": config.model_id,
                "parameters_with_projection": sum(p.numel() for p in model.parameters()),
                "t5_parameters": sum(p.numel() for p in model.t5.parameters())}
    for phase in ("pretrain", "ratings"):
        saved = torch.load(paths[phase], map_location="cpu", weights_only=True)
        model.load_state_dict(saved["state"], strict=True)
        model.eval()
        for index, item in enumerate(items):
            if ("flan", phase, item["id"]) in done:
                continue
            started = time.monotonic()
            row = {"sentence1": item["passage"], "sentence2": item["passage"],
                   "condition": item["condition"]}
            batch = prepare_tokens([row], config, tokenizer)
            input_ids, attention = batch["input_ids"][:1], batch["attention_mask"][:1]
            with torch.inference_mode():
                tokens = model.t5.generate(input_ids=input_ids, attention_mask=attention,
                                           max_new_tokens=64, do_sample=False, num_beams=1,
                                           use_cache=True)[0]
                answer = tokenizer.decode(tokens, skip_special_tokens=True).strip()
                labels = tokenizer(item["teacher_answer"], return_tensors="pt")["input_ids"].to("cuda")
                ce = float(model.t5(input_ids=input_ids, attention_mask=attention,
                                    labels=labels, use_cache=False).loss)
            record = {**item, "model": "flan", "phase": phase, "answer": answer,
                      "teacher_answer_ce": ce, "tokens": len(tokens) - 1,
                      "stopped_on_eos": int(tokens[-1]) == tokenizer.eos_token_id,
                      "seconds": time.monotonic() - started,
                      **agreement(answer, item["teacher_answer"])}
            save_record(record)
            if index % 10 == 9:
                state(status="running", model="flan", phase=phase, completed=index + 1, total=50)
        metadata[phase] = {"checkpoint": str(paths[phase]), "sha256": sha(paths[phase]),
                           "checkpoint_epoch": saved["epoch"]}
    del model, saved
    gc.collect()
    torch.cuda.empty_cache()
    return metadata


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    active = subprocess.check_output(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
        text=True,
    ).strip()
    if active:
        raise RuntimeError("Another CUDA process is active; preserve its work")
    settings, items = cohort()
    manifest = {
        "items": items, "unit": "one passage plus condition", "count": 50,
        "selection": "Fixed hash order; distinct held-out development source groups; at most two examples per condition; accepted cached teacher targets only.",
        "max_new_tokens": 64, "decoding": "greedy", "new_training": False,
        "test_data_used": False, "expert_gold": False,
        "teacher_metrics": "Agreement with cached teacher answers, not human accuracy.",
    }
    mpath = OUT / "manifest.json"
    if mpath.exists() and json.loads(mpath.read_text()) != manifest:
        raise ValueError("Saved inspection cohort differs")
    write(mpath, manifest)
    rows = existing_records()
    done = {(x["model"], x["phase"], x["id"]) for x in rows}
    state(status="starting", completed_generations=len(done), expected_generations=200)
    previous = json.loads((OUT / "summary.json").read_text()) if (OUT / "summary.json").exists() else {}
    metadata = {}
    for name, root in (("flan", FROOT), ("qwen", QROOT)):
        complete = all((name, phase, x["id"]) in done for phase in ("pretrain", "ratings") for x in items)
        prior = previous.get("metadata", {}).get(name)
        if complete and prior:
            for phase in ("pretrain", "ratings"):
                path = checkpoint(root, "evidence", phase)
                if prior[phase]["sha256"] != sha(path):
                    raise ValueError("Completed inference refers to different checkpoint weights")
                prior[phase]["checkpoint"] = str(path)
            metadata[name] = prior
        else:
            metadata[name] = run_flan(items, done) if name == "flan" else run_qwen(settings, items, done)
    rows = existing_records()
    keys = {(x["model"], x["phase"], x["id"]) for x in rows}
    if len(rows) != 200 or len(keys) != 200:
        raise ValueError("Incomplete or duplicate generations")
    summary = {}
    for model in ("flan", "qwen"):
        for phase in ("pretrain", "ratings"):
            selected = [x for x in rows if x["model"] == model and x["phase"] == phase]
            summary[model + "_" + phase] = {
                "n": len(selected),
                "teacher_exact_matches": sum(x["teacher_exact_match"] for x in selected),
                "mean_teacher_token_f1": sum(x["teacher_token_f1"] for x in selected) / len(selected),
                "mean_teacher_answer_ce": sum(x["teacher_answer_ce"] for x in selected) / len(selected),
                "empty_answers": sum(not x["answer"] for x in selected),
                "generation_seconds": sum(x["seconds"] for x in selected),
            }
    write(OUT / "summary.json", {"status": "complete", "metadata": metadata,
                                 "automatic_teacher_agreement": summary,
                                 "scope": "Assistant inspection on a selected 50-item development cohort. Teacher agreement is distinct from correctness; no expert or Spanish evaluation."})
    state(status="complete", completed_generations=200, summary=summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        if OUT.exists():
            state(status="failed", error=repr(error))
        raise
