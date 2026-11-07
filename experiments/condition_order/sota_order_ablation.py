#!/usr/bin/env python3
"""Matched C-STS condition-order ablation on the archived proposition-trained Qwen encoder.

Freeze the exact archived Qwen3-Embedding-8B LoRA checkpoint, extract final EOD
embeddings on the *same* 6051/1576/2431 readout cohort with condition last,
and fit three zero-initialized symmetric comparison models using original
comparator hyperparameters (seeds 7/8/9). No decoder or LoRA updates.

The source training commit stays immutable: fdbcb3461f63cf44d7cb3cde4de27332594e452d.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import time

import numpy as np
import torch
from torch.nn import functional as F

import csts_pilot.baseline_models as bm
from csts_pilot.condition_reference import native_layout
from csts_pilot.evidence_readout import (
    SymmetricComparison, clone_state, metric_values, object_sha256,
)
from jep_pilot.loaders import load_model

ROOT = pathlib.Path("/home/machina/jep-sota-order-20261107")
OUT = ROOT / "results"
DATA = pathlib.Path("/home/machina/jep-csts-evidence-readout-20261027")
CKPT = DATA / "csts_data/readout_revised/proposition_final.pt"
MODEL_SHA = "d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f"
EXPECTED = {
    "training": ("csts_data/readout/train.json", "9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4", 6051),
    "validation": ("csts_data/readout/validation.json", "e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff", 1576),
    "test": ("csts_data/readout/test.json", "d6b40b7b891ed147befb30801c2f85a8787775adebdd98d134157cbb2a6e9f76", 2431),
}
PROMPT = "Query: {passage}\nInstruct: Represent the passage for semantic similarity with respect to this condition: {condition}"
OLD_PROMPT = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
REVISION = "c90816d848505624c2434128dfc61132162a0ee9"
SOURCE_COMMIT = "fdbcb3461f63cf44d7cb3cde4de27332594e452d"
BASELINE = {
    "test_cosine_spearman": 0.863398,
    "mean_test_comparator_spearman": 0.865230,
    "seed_test_spearman": {"7": 0.864672, "8": 0.865373, "9": 0.865646},
    "mean_test_comparator_mse": 0.035131,
    "test_rows": 2431,
}
EMBED_BATCH = 4
FIT_BATCH = 32
FIT_LR = 0.001
FIT_WD = 0.01
FIT_PATIENCE = 10
FIT_MAX_EPOCHS = 256
SEEDS = (7, 8, 9)

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def emit(tag, **info):
    print(json.dumps({"utc": utc(), "event": tag, **info}, ensure_ascii=False), flush=True)

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4*1024*1024):
            h.update(chunk)
    return h.hexdigest()

def save_json(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    tmp.replace(path)

def rows_for(split):
    name, expected_hash, count = EXPECTED[split]
    path = DATA / name
    if sha(path) != expected_hash:
        raise RuntimeError(f"{split} input SHA differs from historical baseline")
    rows = json.loads(path.read_text())
    if len(rows) != count:
        raise RuntimeError(f"{split} count differs from historical baseline")
    bm.validate_rows(rows)
    return rows

def check():
    OUT.mkdir(parents=True, exist_ok=True)
    if sha(CKPT) != MODEL_SHA:
        raise RuntimeError("Wrong starting encoder: proposition_final.pt hash mismatch")
    for split in EXPECTED:
        if split == "test":
            path = DATA / EXPECTED[split][0]
            if sha(path) != EXPECTED[split][1]:
                raise RuntimeError("Held-out test SHA differs from the original benchmark")
            emit("test_identity_verified_without_loading_targets",
                 rows=EXPECTED[split][2], sha256=EXPECTED[split][1])
            continue
        r = rows_for(split)
        emit("input_verified", split=split, rows=len(r), sha256=EXPECTED[split][1])
    bm.PROMPT = PROMPT
    d = load_model(CKPT)
    cfg = bm.FitConfig.model_validate({k:v for k,v in d["config"].items() if k in bm.FitConfig.model_fields})
    if (cfg.model_id, cfg.revision, cfg.embedding_dimension, cfg.max_length, cfg.kind) != (
        "Qwen/Qwen3-Embedding-8B", REVISION, 4096, 160, "lora"
    ):
        raise RuntimeError(f"Wrong Qwen checkpoint model settings: {cfg}")
    emit("checkpoint_verified", model_sha256=MODEL_SHA, source_commit=SOURCE_COMMIT,
         configuration={"model":cfg.model_id,"revision":cfg.revision,"kind":cfg.kind,
                        "dimension":cfg.embedding_dimension,"max_length":cfg.max_length})
    return cfg

def cache_path(split):
    return OUT / f"{split}-condition-last-eod.pt"

def extract_all():
    cfg = check()
    saved = load_model(CKPT)
    cfg = bm.FitConfig.model_validate({k:v for k,v in saved["config"].items() if k in bm.FitConfig.model_fields})
    cfg = cfg.model_copy(update={"device":"cuda", "encode_batch_size":4})
    # First inspect planned input lengths without reading the held-out labels for fitting.
    bm.PROMPT = PROMPT
    tokenizer = bm.load_tokenizer(cfg)
    model = bm.load_backbone(cfg, adapters=cfg)
    bm.restore_parameters(model, saved["state"])
    del saved
    model.eval().requires_grad_(False)
    before = bm.state_digest({n:p for n,p in model.named_parameters() if "lora_" in n})
    del cfg
    for split in ("training","validation"):
        extract_one(split, model, tokenizer, before)
    del model
    torch.cuda.empty_cache()
    emit("train_validation_embedded", model_adapter_sha256=before)

def extract_one(split, model, tokenizer, before):
    path = cache_path(split)
    rows = rows_for(split)
    if path.exists():
        cached = torch.load(path, map_location="cpu", weights_only=True)
        if (cached["prompt"] != PROMPT or cached["model_sha256"] != MODEL_SHA or
            cached["rows_sha256"] != EXPECTED[split][1] or len(cached["left"]) != len(rows)):
            raise RuntimeError(f"Existing {split} cache mismatches the immutable experiment identity.")
        emit("existing_cache_verified", split=split, path=str(path), sha256=sha(path))
        return
    c = bm.EncoderConfig.model_validate({
        "model_id":"Qwen/Qwen3-Embedding-8B","revision":REVISION,
        "embedding_dimension":4096,"max_length":160,"encode_batch_size":4,
        "device":"cuda"})
    keys, left, right = native_layout(rows)
    bm.PROMPT = PROMPT
    seq = bm.token_sequences(tokenizer, keys, c)
    embeddings=[]
    start=time.monotonic()
    with torch.inference_mode():
        for i in range(0,len(seq),EMBED_BATCH):
            batch=bm.pad_sequences(tokenizer,seq[i:i+EMBED_BATCH],c)
            vec=bm.encode(model,batch)
            embeddings.append(vec.cpu())
            if i % 1000 == 0 or i+EMBED_BATCH>=len(seq):
                emit("embedding_progress", split=split, done=min(i+EMBED_BATCH,len(seq)),
                     total=len(seq), elapsed_seconds=round(time.monotonic()-start,2))
    vectors=torch.cat(embeddings).float()
    if vectors.shape != (len(keys),4096) or not torch.isfinite(vectors).all():
        raise RuntimeError(f"Invalid embeddings {split}: {vectors.shape}")
    norm=vectors.norm(dim=1)
    if (norm - 1).abs().max() > 1e-4:
        raise RuntimeError("Embeddings lost original final-token normalization")
    current=bm.state_digest({n:p for n,p in model.named_parameters() if "lora_" in n})
    if current != before:
        raise RuntimeError("Frozen LoRA weights unexpectedly changed")
    cache={"prompt":PROMPT,"source_commit":SOURCE_COMMIT,"model_sha256":MODEL_SHA,
           "adapter_sha256":before,"rows_sha256":EXPECTED[split][1],
           "keys":keys,"left":left,"right":right,
           "eod_vectors":vectors,"split":split}
    tmp=path.with_suffix(".pt.partial")
    torch.save(cache,tmp)
    tmp.replace(path)
    emit("embedding_saved", split=split, path=str(path), sha256=sha(path),
         duration_seconds=round(time.monotonic()-start,3), rows=len(rows), occurrences=len(keys))
    del cache,vectors,embeddings,seq
    torch.cuda.empty_cache()

def cache(split):
    p=cache_path(split)
    result=torch.load(p,map_location="cpu",weights_only=True)
    if (result["prompt"],result["model_sha256"],result["rows_sha256"]) != (
        PROMPT,MODEL_SHA,EXPECTED[split][1]):
        raise RuntimeError(f"Invalid {split} cache")
    return result

def predictions(comparator,z,left,right,step=2048):
    preds=[]
    with torch.inference_mode():
        for i in range(0,len(left),step):
            preds.append(comparator(z[left[i:i+step]],z[right[i:i+step]]).cpu())
    return torch.cat(preds).numpy()

def fit():
    train,valid=cache("training"),cache("validation")
    tr_rows,va_rows=rows_for("training"),rows_for("validation")
    train_z=train["eod_vectors"].cuda()
    valid_z=valid["eod_vectors"].cuda()
    train_left=torch.tensor(train["left"],device="cuda")
    train_right=torch.tensor(train["right"],device="cuda")
    val_left=torch.tensor(valid["left"],device="cuda")
    val_right=torch.tensor(valid["right"],device="cuda")
    target=torch.tensor([r["target"] for r in tr_rows],device="cuda",dtype=torch.float32)
    selected={}
    for seed in SEEDS:
        torch.manual_seed(seed)
        comparator=SymmetricComparison(4096).cuda()
        opt=torch.optim.AdamW(comparator.parameters(),lr=FIT_LR,weight_decay=FIT_WD)
        order_gen=torch.Generator().manual_seed(seed+10000)
        selected_path=OUT / f"comparison-seed-{seed}-selected.pt"
        epochs_path=OUT / f"comparison-seed-{seed}-epochs.json"
        if selected_path.exists():
            previous=torch.load(selected_path,map_location="cpu",weights_only=True)
            if previous["status"]=="complete":
                selected[str(seed)]={"epoch":previous["selected_epoch"],
                                    "validation_spearman":previous["validation"]["spearman"],
                                    "checkpoint_sha256":sha(selected_path)}
                emit("seed_fit_reused",seed=seed,**selected[str(seed)])
                continue
            raise RuntimeError("Interrupted comparison fit requires explicit optimizer-state recovery")
        val_scores=predictions(comparator,valid_z,val_left,val_right)
        best={"epoch":0,"validation":metric_values(va_rows,val_scores),"state":clone_state(comparator)}
        epochs=[]
        stale=0
        fit_start=time.monotonic()
        for epoch in range(1,FIT_MAX_EPOCHS+1):
            index=torch.randperm(len(tr_rows),generator=order_gen).tolist()
            losses=0.
            for start in range(0,len(index),FIT_BATCH):
                ix=index[start:start+FIT_BATCH]
                vals=comparator(train_z[train_left[ix]],train_z[train_right[ix]])
                loss=F.mse_loss(vals,target[ix])
                if not torch.isfinite(loss):
                    raise RuntimeError("Nonfinite comparison loss")
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(comparator.parameters(),1.0,error_if_nonfinite=True)
                opt.step()
                losses+=float(loss.detach())*len(ix)
            val_scores=predictions(comparator,valid_z,val_left,val_right)
            score=metric_values(va_rows,val_scores)
            improved=score["spearman"]>best["validation"]["spearman"]
            if improved:
                best={"epoch":epoch,"validation":score,"state":clone_state(comparator)}
            stale=0 if improved else stale+1
            ep={"epoch":epoch,"train_mse":losses/len(tr_rows),
                "val_spearman":score["spearman"],"val_mse":score["mse_0_1"],
                "selected_epoch":best["epoch"],"stale":stale,
                "order_sha256":object_sha256(index)}
            epochs.append(ep)
            emit("comparison_epoch",seed=seed,**ep)
            save_json(epochs_path,{"seed":seed,"status":"running","epochs":epochs})
            # Crash-safe epoch resume preserves optimizer, generator and selected states.
            state={"epoch":epoch,"model":clone_state(comparator),
                   "optimizer":opt.state_dict(),"rng":order_gen.get_state(),
                   "best":best,"epochs":epochs,"seed":seed}
            tmp=OUT / f"comparison-seed-{seed}-resume.pt.partial"
            torch.save(state,tmp)
            tmp.replace(OUT / f"comparison-seed-{seed}-resume.pt")
            if stale>=FIT_PATIENCE:
                break
        if stale < FIT_PATIENCE:
            raise RuntimeError(f"Seed {seed} hit comparison limit without patience convergence")
        result={"status":"complete","seed":seed,"selected_epoch":best["epoch"],
                "validation":best["validation"],"state":best["state"],
                "trained_epochs":epoch,"source_commit":SOURCE_COMMIT,
                "starting_model_sha256":MODEL_SHA,"prompt":PROMPT,
                "train_sha256":EXPECTED["training"][1],"validation_sha256":EXPECTED["validation"][1],
                "optimizer":{"type":"AdamW","learning_rate":FIT_LR,"weight_decay":FIT_WD},
                "duration_seconds":time.monotonic()-fit_start}
        tmp=selected_path.with_suffix(".pt.partial")
        torch.save(result,tmp)
        tmp.replace(selected_path)
        save_json(epochs_path,{"seed":seed,"status":"complete","epochs":epochs})
        selected[str(seed)]={"epoch":best["epoch"],"validation_spearman":best["validation"]["spearman"],
                             "checkpoint_sha256":sha(selected_path)}
        emit("comparison_seed_selected",seed=seed,**selected[str(seed)])
    save_json(OUT/"selection.json",{"status":"frozen","selected":selected,
                                   "test_scores_used_for_selection":False,
                                   "source_commit":SOURCE_COMMIT,"starting_model_sha256":MODEL_SHA,
                                   "train_sha256":EXPECTED["training"][1],
                                   "validation_sha256":EXPECTED["validation"][1],
                                   "prompt":PROMPT})
    emit("all_comparators_frozen",seeds=list(selected))

def test():
    selection=json.loads((OUT/"selection.json").read_text())
    if selection["status"]!="frozen" or selection["test_scores_used_for_selection"] is not False:
        raise RuntimeError("Test locked until all comparator heads selected by validation")
    for seed in SEEDS:
        p=OUT/f"comparison-seed-{seed}-selected.pt"
        if sha(p)!=selection["selected"][str(seed)]["checkpoint_sha256"]:
            raise RuntimeError("Selected checkpoint differs")
    saved=load_model(CKPT)
    config=bm.FitConfig.model_validate({k:v for k,v in saved["config"].items() if k in bm.FitConfig.model_fields})
    config=config.model_copy(update={"device":"cuda","encode_batch_size":4})
    bm.PROMPT=PROMPT
    tokenizer=bm.load_tokenizer(config)
    model=bm.load_backbone(config,adapters=config)
    bm.restore_parameters(model,saved["state"])
    model.eval().requires_grad_(False)
    before=bm.state_digest({n:p for n,p in model.named_parameters() if "lora_" in n})
    extract_one("test",model,tokenizer,before)
    del model,saved
    torch.cuda.empty_cache()
    held=cache("test")
    rows=rows_for("test")
    z=held["eod_vectors"].cuda()
    l=torch.tensor(held["left"],device="cuda")
    r=torch.tensor(held["right"],device="cuda")
    cosine=(z[l]*z[r]).sum(-1).cpu().numpy()
    summary={"status":"complete","utc":utc(),"source_commit":SOURCE_COMMIT,
             "starting_model_sha256":MODEL_SHA,"prompt_before":OLD_PROMPT,"prompt_after":PROMPT,
             "dataset":{"train":EXPECTED["training"][1],"validation":EXPECTED["validation"][1],
                        "test":EXPECTED["test"][1]},
             "epoch_selection":selection,"historical_baseline":BASELINE,
             "test_cosine":metric_values(rows,cosine),"comparators":{}}
    for seed in SEEDS:
        best=torch.load(OUT/f"comparison-seed-{seed}-selected.pt",map_location="cpu",weights_only=True)
        comparator=SymmetricComparison(4096).cuda()
        comparator.load_state_dict(best["state"],strict=True)
        comparator.eval()
        values=predictions(comparator,z,l,r)
        if len(values)!=len(rows):
            raise RuntimeError("Test row coverage incomplete")
        metrics=metric_values(rows,values)
        pred_path=OUT/f"test-seed-{seed}-predictions.json"
        save_json(pred_path,[{"row_id":row["row_id"],"pair_id":row["pair_id"],
                              "group_id":row["group_id"],"target":row["target"],
                              "prediction":float(value)}
                             for row,value in zip(rows,values,strict=True)])
        summary["comparators"][str(seed)]={"metrics":metrics,
            "predictions_sha256":sha(pred_path),"selected_epoch":best["selected_epoch"],
            "selected_checkpoint_sha256":sha(OUT/f"comparison-seed-{seed}-selected.pt")}
        emit("test_scored",seed=seed,spearman=metrics["spearman"],mse=metrics["mse_0_1"])
    mean_rho=float(np.mean([summary["comparators"][str(seed)]["metrics"]["spearman"] for seed in SEEDS]))
    mean_mse=float(np.mean([summary["comparators"][str(seed)]["metrics"]["mse_0_1"] for seed in SEEDS]))
    summary["mean_test_comparator_spearman"]=mean_rho
    summary["mean_test_comparator_mse"]=mean_mse
    summary["delta_vs_historical"]=mean_rho-BASELINE["mean_test_comparator_spearman"]
    summary["delta_vs_historical_mse"]=mean_mse-BASELINE["mean_test_comparator_mse"]
    save_json(OUT/"results.json",summary)
    emit("experiment_complete",new_mean_spearman=mean_rho,
         historical_mean_spearman=BASELINE["mean_test_comparator_spearman"],
         delta=summary["delta_vs_historical"],cosine_test=summary["test_cosine"]["spearman"])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("preflight","embed","fit","test","all"),default="all")
    args=parser.parse_args()
    cfg=check()
    if args.phase=="preflight":return
    if args.phase in ("embed","all"):
        extract_all()
    if args.phase in ("fit","all"):
        fit()
    if args.phase in ("test","all"):
        test()
if __name__=="__main__":
    main()