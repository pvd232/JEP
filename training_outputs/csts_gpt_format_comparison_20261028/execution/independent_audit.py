#!/usr/bin/env python3
"""Independent CPU audit of saved matched-format scores; imports no experiment code."""
import argparse, collections, hashlib, json, math, random
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

ARMS = ("raw", "propositions", "json", "python")
CKPT = "d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f"
LEGACY = "1e2939bb6d5c42ff6df6590ab46db805371256b649e8b720abec3637492f14ea"
REV = "c90816d848505624c2434128dfc61132162a0ee9"
CODE = "223e8f83c3081f9ff4e2aa70a9f193bd4cc1a4f248a3cf46a55e207525cbc8b1"
def load(path): return json.loads(Path(path).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def near(a,b, tol=1e-10):
    if a is None or b is None: assert a is None and b is None, (a,b)
    else: assert math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tol, (a,b,tol)
def metrics(x,y):
    r = float(spearmanr(x,y).statistic)
    mse = float(np.mean(np.square(np.asarray(x)-y)))
    return {"n":len(x), "spearman":None if math.isnan(r) else r, "mse_0_1":mse, "mse_1_5":16*mse}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scoring", required=True, type=Path)
    p.add_argument("--labels", required=True, type=Path)
    p.add_argument("--direct", required=True, type=Path)
    p.add_argument("--results", type=Path)
    p.add_argument("--output", required=True, type=Path)
    args=p.parse_args()
    root=args.scoring; inputs=load(root/"inputs.json"); rows=load(root/"predictions.json")
    receipt=load(root/"receipt.json"); tok=load(root/"tokenized_inputs.json")
    assert receipt["status"]=="complete"
    assert digest(root/"inputs.json")=="1e6ca27338e47b57a2b6784fad0d0b2f7399f2463e2ceb4d031be4141eaa65bb"
    matched=inputs["protocol"]["matched_generation"]
    assert matched["protocol_sha256"]=="bbcc27cd1ab9cd821c76d20bbae297f945a9d3c4d273162f34ec58e585506f56"
    assert len(matched["batch_schedule"])==19 and matched["fresh_proposition_records"]==239
    assert receipt["checkpoint_sha256"]==CKPT
    assert receipt["incumbent_baseline_code_sha256"]==LEGACY
    assert receipt["code_sha256"]==CODE
    assert receipt["adapter_state_before_sha256"]==receipt["adapter_state_after_sha256"]
    assert receipt["optimizer_updates"]==0 and receipt["truncated_inputs"]==0
    assert "A100" in receipt["gpu"]
    assert receipt["checkpoint_config"]["revision"]==REV
    assert receipt["checkpoint_config"]["max_length"]==160
    assert receipt["checkpoint_config"]["embedding_dimension"]==4096
    for name in ("inputs","tokenized_inputs","predictions","embeddings"):
        suffix=".npz" if name=="embeddings" else ".json"
        assert digest(root/(name+suffix))==receipt[name+"_sha256"], name
    pairs=inputs["pairs"]; sources={s["id"]:s for s in inputs["sources"]}
    ids=[p["id"] for p in pairs]
    assert len(ids)==len(set(ids))==120 and len(sources)==239
    assert len(set(p["group_id"] for p in pairs))==110
    assert [r["id"] for r in rows]==ids
    assert not any(k in inputs for k in ("labels","ratings","targets","direct"))
    assert all(not any(k in p for k in ("rating","target","label")) for p in pairs)
    expected={(arm,sid) for arm in ARMS for sid in sources}
    by_tok={(t["arm"],t["source_id"]):t for t in tok}
    assert len(tok)==len(by_tok)==956 and set(by_tok)==expected
    source_fallbacks={}; fallback={}
    for arm in ARMS:
        for sid,s in sources.items():
            t=by_tok[arm,sid]; reason=t["fallback_reason"]
            assert t["condition"]==s["condition"]
            assert 1<=len(t["input_ids"])<=160
            if arm=="raw":
                assert reason is None and t["text"]==s["passage"]
                continue
            e=s["arms"][arm]
            if reason:
                assert t["text"]==s["passage"]
                assert t["input_ids"]==by_tok["raw",sid]["input_ids"]
                if e.get("failure"): assert reason=="failure:"+e["failure"]
                elif e["status"]!="answered": assert reason==e["status"]
                elif not e["text"].strip(): assert reason=="empty_evidence"
                else:
                    assert reason=="token_overflow" and t["requested_token_length"]>160
            else:
                assert not e.get("failure") and e["status"]=="answered"
                assert e["text"].strip() and t["text"]==e["text"]
                assert t["requested_token_length"]==len(t["input_ids"])
        if arm!="raw":
            counts=collections.Counter(by_tok[arm,s]["fallback_reason"] for s in sources if by_tok[arm,s]["fallback_reason"])
            source_fallbacks[arm]=dict(counts)
            assert receipt["source_fallbacks"][arm]==dict(counts)
            reasons=[]
            for pair,row in zip(pairs,rows):
                wanted=[by_tok[arm,pair["source_"+side]]["fallback_reason"] for side in ("a","b")]
                assert row["fallback_by_arm"][arm]==wanted
                reasons.append(wanted)
            n=[sum(x is not None for x in r) for r in reasons]
            fallback[arm]={"side_occurrences":sum(n),"pairs_with_any":sum(x>0 for x in n),
                           "pairs_with_one":n.count(1),"pairs_with_both":n.count(2),
                           "reason_counts":dict(collections.Counter(x for r in reasons for x in r if x))}
    z=np.load(root/"embeddings.npz",allow_pickle=False)
    assert z["pair_ids"].tolist()==ids
    assert z["source_a"].tolist()==[p["source_a"] for p in pairs]
    assert z["source_b"].tolist()==[p["source_b"] for p in pairs]
    vector_errors={}
    for arm in ARMS:
        a,b=z[arm+"_left"],z[arm+"_right"]
        assert a.shape==b.shape==(120,4096) and np.isfinite(a).all() and np.isfinite(b).all()
        norm_error=max(float(np.max(np.abs(np.linalg.norm(a,axis=1)-1))),
                       float(np.max(np.abs(np.linalg.norm(b,axis=1)-1))))
        assert norm_error<2e-6
        scores=np.sum(a.astype(np.float64)*b.astype(np.float64),axis=1)
        error=float(np.max(np.abs(scores-[r[arm] for r in rows])))
        assert error<1e-6
        vector_errors[arm]={"max_cosine_absolute_error":error,"max_unit_norm_error":norm_error}
    label_rows=load(args.labels)
    labels={r.get("id",r.get("row_id")):r["rating"] for r in label_rows}
    direct=load(args.direct)
    assert len(labels)==len(label_rows)==120 and set(labels)==set(direct)==set(ids)
    target=np.asarray([(labels[i]-1)/4 for i in ids])
    assert np.isfinite(target).all() and (target>=0).all() and (target<=1).all()
    scores={a:np.asarray([r[a] for r in rows]) for a in ARMS}
    scores["gpt_direct"]=np.asarray([(direct[i]-1)/4 for i in ids])
    assert (scores["gpt_direct"]>=0).all() and (scores["gpt_direct"]<=1).all()
    point={a:metrics(s,target) for a,s in scores.items()}
    comparisons=[("json_minus_propositions","json","propositions"),
                 ("python_minus_propositions","python","propositions"),
                 ("python_minus_json","python","json"),
                 ("propositions_minus_raw","propositions","raw")]
    comparisons += [(a+"_minus_gpt_direct",a,"gpt_direct") for a in ARMS]
    groups=collections.defaultdict(list)
    for i,pair in enumerate(pairs): groups[pair["group_id"]].append(i)
    rng=random.Random(42); keys=sorted(groups); draws=2000
    samples={name:{"spearman":[],"mse_0_1":[]} for name,_,_ in comparisons}
    for _ in range(draws):
        ix=[i for g in rng.choices(keys,k=len(keys)) for i in groups[g]]
        m={a:metrics(s[ix],target[ix]) for a,s in scores.items()}
        for name,a,b in comparisons:
            for metric in ("spearman","mse_0_1"):
                x,y=m[a][metric],m[b][metric]
                if x is not None and y is not None: samples[name][metric].append(x-y)
    contrasts={}
    for name,a,b in comparisons:
        contrasts[name]={}
        for metric,values in samples[name].items():
            x,y=point[a][metric],point[b][metric]
            contrasts[name][metric]={"difference":None if x is None or y is None else x-y,
                                    "defined_draws":len(values),
                                    "interval":np.quantile(values,[.025,.975]).tolist() if values else None}
    if args.results:
        reported=load(args.results)
        assert reported["n"]==120 and reported["groups"]==110 and reported["fallback"]==fallback
        for arm,m in point.items():
            for key,value in m.items(): near(value,reported["metrics"][arm][key])
        assert reported["bootstrap"]["draws"]==draws and reported["bootstrap"]["seed"]==42
        for name,c in contrasts.items():
            for metric,stat in c.items():
                expected=reported["bootstrap"]["comparisons"][name][metric]
                near(stat["difference"],expected["difference"])
                assert stat["defined_draws"]==expected["defined_draws"]
                for a,b in zip(stat["interval"],expected["interval"]): near(a,b)
    result={"status":"verified","n":120,"groups":110,"sources":239,"checkpoint_sha256":CKPT,
            "receipt_sha256":digest(root/"receipt.json"),"vectors":vector_errors,
            "metrics":point,"source_fallbacks":source_fallbacks,"fallback":fallback,"comparisons":contrasts,
            "limits":["Conditional on frozen generations; shared batch-context variation excluded.",
                      "Previously exposed validation set; no teacher retraining or semantic fidelity measurement."]}
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"verified","output":str(args.output),"metrics":point},sort_keys=True))
if __name__=="__main__": main()
