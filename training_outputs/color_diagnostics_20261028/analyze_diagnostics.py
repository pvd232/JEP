#!/usr/bin/env python3
"""Measure color readout and embedding contrasts in frozen model outputs."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import numpy as np

import probe as probe_module


SEEDS = (7, 8, 9)
STATE_NAMES = ("base",) + tuple(
    f"seed{k}_{arm}_{phase}" for k in SEEDS for phase in ("A", "B") for arm in ("R", "P")
)
METRICS = ("E", "M_G", "F", "C", "Q", "implicit_margin")
CONFIDENCE = 1.0 - 0.05 / 6.0


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def mean(values):
    values = list(values)
    return float(np.mean(values)) if values else None


def state_from_arrays(probe, predictions, ids, z, receipt=None):
    """Align each answer and embedding to its frozen caption-condition input."""
    expected = [x["id"] for x in probe["inputs"]]
    expected_set = set(expected)
    pids = [x["id"] for x in predictions]
    ids = [str(x) for x in ids]
    if len(set(pids)) != len(pids) or set(pids) != expected_set:
        raise ValueError("Prediction IDs differ from the frozen probe")
    if len(set(ids)) != len(ids) or set(ids) != expected_set:
        raise ValueError("Embedding IDs differ from the frozen probe")
    z = np.asarray(z, dtype=np.float64)
    if z.ndim != 2 or z.shape[0] != len(ids) or not np.isfinite(z).all():
        raise ValueError("Embedding matrix requires one finite vector per input")
    if not np.allclose(np.linalg.norm(z, axis=1), 1.0, rtol=2e-4, atol=2e-4):
        raise ValueError("Embedding vectors must have unit length")
    pi = {x["id"]: x for x in predictions}
    zi = dict(zip(ids, z, strict=True))
    parsed, literal, pragmatic, wrong_object = {}, {}, {}, {}
    answers = []
    for item in probe["inputs"]:
        uid = item["id"]
        prediction = pi[uid]
        if not isinstance(prediction.get("answer"), str):
            raise ValueError("Each prediction requires a decoded answer string")
        parsed[uid] = probe_module.parse_answer(prediction["answer"], item)
        literal[uid] = probe_module.is_correct(parsed[uid], item, "literal_colors")
        pragmatic[uid] = probe_module.is_correct(parsed[uid], item, "pragmatic_colors")
        wrong_object[uid] = bool(item.get("distractor_colors") and
            parsed[uid]["colors"] == item["distractor_colors"] and
            not parsed[uid]["qualified_or_uncertain"])
        answers.append(dict(id=uid, family=item["family"], caption=item["caption"],
                            condition=item["condition"], answer=prediction["answer"],
                            literal_colors=item["literal_colors"],
                            pragmatic_colors=item["pragmatic_colors"],
                            parsed=parsed[uid], literal_correct=literal[uid],
                            pragmatic_correct=pragmatic[uid], wrong_object=wrong_object[uid],
                            generated_tokens=prediction.get("generated_tokens"),
                            stopped_on_eos=prediction.get("stopped_on_eos")))
    families = {}
    for family in probe["families"]:
        fids = family["ids"]
        record = dict(stratum=family["stratum"],
            literal_accuracy=mean(literal[i] for i in fids),
            pragmatic_accuracy=mean(pragmatic[i] for i in fids),
            empty_color_fraction=mean(not parsed[i]["colors"] for i in fids),
            invented_color_fraction=mean(bool(parsed[i]["colors"]) for i in fids),
            other_role_named_fraction=mean(parsed[i]["other_role_named"] for i in fids),
            truncated_fraction=mean(bool(pi[i].get("generated_tokens", 0) >= 64 and
                                         not pi[i].get("stopped_on_eos", False)) for i in fids))
        if family["stratum"] in ("explicit", "multiple"):
            grid = family["grid"]
            margins = [float(zi[grid[j]] @ zi[grid[j ^ 1]] - zi[grid[j]] @ zi[grid[j ^ 2]])
                       for j in range(4)]
            record.update(margins=margins, margin=mean(margins))
        if family["stratum"] == "multiple":
            dgrid = family["distractor_grid"]
            dm = [float(zi[dgrid[j]] @ zi[dgrid[j ^ 2]] - zi[dgrid[j]] @ zi[dgrid[j ^ 1]])
                  for j in range(4)]
            record.update(F=mean(wrong_object[i] for i in fids),
                          target_condition_margin=mean(margins),
                          distractor_condition_margin=mean(dm), C=(mean(margins)+mean(dm))/2)
        if family["stratum"] == "implied":
            pos, neg = zi[family["positive"]], zi[family["negative"]]
            implicit = float(zi[family["implicit"]] @ pos - zi[family["implicit"]] @ neg)
            explicit = float(zi[family["explicit"]] @ pos - zi[family["explicit"]] @ neg)
            record.update(implicit_margin=implicit, explicit_margin=explicit, Q=explicit-implicit)
        families[family["id"]] = record
    primary = [f["id"] for f in probe["families"] if f["stratum"] in ("explicit", "multiple")]
    multi = [f["id"] for f in probe["families"] if f["stratum"] == "multiple"]
    implied = [f["id"] for f in probe["families"] if f["stratum"] == "implied"]
    unspecified = [f["id"] for f in probe["families"] if f["stratum"] == "unspecified"]
    summary = dict(
        E=mean(families[f]["literal_accuracy"] for f in primary),
        all_family_margin=mean(families[f]["margin"] for f in primary),
        F=mean(families[f]["F"] for f in multi), C=mean(families[f]["C"] for f in multi),
        target_condition_margin=mean(families[f]["target_condition_margin"] for f in multi),
        distractor_condition_margin=mean(families[f]["distractor_condition_margin"] for f in multi),
        Q=mean(families[f]["Q"] for f in implied),
        implicit_margin=mean(families[f]["implicit_margin"] for f in implied),
        explicit_margin=mean(families[f]["explicit_margin"] for f in implied),
        implied_literal_accuracy=mean(families[f]["literal_accuracy"] for f in implied),
        implied_pragmatic_accuracy=mean(families[f]["pragmatic_accuracy"] for f in implied),
        implicit_readout_literal_accuracy=mean(literal[f["implicit"]] for f in probe["families"] if f["stratum"]=="implied"),
        implicit_readout_pragmatic_accuracy=mean(pragmatic[f["implicit"]] for f in probe["families"] if f["stratum"]=="implied"),
        explicit_readout_literal_accuracy=mean(literal[f["explicit"]] for f in probe["families"] if f["stratum"]=="implied"),
        unspecified_invented_color_fraction=mean(families[f]["invented_color_fraction"] for f in unspecified),
        unspecified_empty_color_fraction=mean(families[f]["empty_color_fraction"] for f in unspecified),
        unspecified_literal_accuracy=mean(families[f]["literal_accuracy"] for f in unspecified),
        truncated_family_mean=mean(f["truncated_fraction"] for f in families.values()),
        stratum_literal_accuracy={s:mean(r["literal_accuracy"] for r in families.values() if r["stratum"]==s)
                                  for s in ("explicit", "multiple", "implied", "unspecified")})
    return dict(summary=summary, families=families, literal_correct=literal,
                parsed_answers=answers, receipt=receipt or {})


def load_state(probe, probe_hash, directory):
    receipt = json.loads((directory/"receipt.json").read_text())
    if receipt.get("status") != "complete":
        raise ValueError(f"State remains incomplete: {directory.name}")
    if receipt.get("probe_sha256") not in (None, probe_hash):
        raise ValueError(f"Probe digest differs: {directory.name}")
    files = {"predictions":directory/"predictions.json", "embeddings":directory/"embeddings.npz"}
    hashes = {k:file_sha256(v) for k,v in files.items()}
    for key, sha in hashes.items():
        if receipt.get(key+"_sha256") not in (None, sha):
            raise ValueError(f"Output digest differs: {directory.name}/{key}")
    predictions = json.loads(files["predictions"].read_text())
    with np.load(files["embeddings"], allow_pickle=False) as arrays:
        result = state_from_arrays(probe,predictions,arrays["ids"],arrays["z"],receipt)
    result["artifact_sha256"] = dict(**hashes,receipt=file_sha256(directory/"receipt.json"))
    return result


def gated_ratio_mean(sums, counts):
    """Average each seed's eligible-triplet ratio with equal seed weight."""
    sums, counts = np.asarray(sums), np.asarray(counts)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = sums / counts
    return np.mean(ratios, axis=0)


def finite_or_none(value):
    return float(value) if np.isfinite(value) else None


def sign_met(contrast, direction):
    interval = contrast.get("interval")
    if interval is None:
        return False
    if direction == "negative":
        return interval[1] < 0
    return interval[0] > 0


def contrasts(probe, states, draws=10000, seed=61028):
    """Resample complete families within strata while retaining all training seeds."""
    families = probe["families"]
    fids = [f["id"] for f in families]
    index = {fid:i for i,fid in enumerate(fids)}
    strata = {s:np.array([i for i,f in enumerate(families) if f["stratum"]==s],dtype=int)
              for s in ("explicit", "multiple", "implied", "unspecified")}
    rng = np.random.default_rng(seed)
    sampled = {s:values[rng.integers(0,len(values),size=(draws,len(values)))]
               for s,values in strata.items() if len(values)}
    selected = dict(E=np.concatenate([strata["explicit"],strata["multiple"]]),
                    F=strata["multiple"],C=strata["multiple"],Q=strata["implied"],
                    implicit_margin=strata["implied"])
    sampled_selected = dict(E=np.concatenate([sampled["explicit"],sampled["multiple"]],axis=1),
                            F=sampled["multiple"],C=sampled["multiple"],Q=sampled["implied"],
                            implicit_margin=sampled["implied"])
    family_fields = dict(E="literal_accuracy",F="F",C="C",Q="Q",implicit_margin="implicit_margin")
    primary = [f for f in families if f["stratum"] in ("explicit", "multiple")]
    gate_counts = np.zeros((len(SEEDS),len(fids)),dtype=np.int64)
    gate_sums = np.zeros_like(gate_counts,dtype=float)
    gate_records, per_seed = {}, {}
    for si,k in enumerate(SEEDS):
        p, r = states[f"seed{k}_P_B"],states[f"seed{k}_R_B"]
        rows = []
        for family in primary:
            fid, grid = family["id"],family["grid"]
            gates = [all(s["literal_correct"][grid[jj]] for s in (p,r) for jj in (j,j^1,j^2))
                     for j in range(4)]
            differences = np.array(p["families"][fid]["margins"])-np.array(r["families"][fid]["margins"])
            gate_counts[si,index[fid]] = sum(gates)
            gate_sums[si,index[fid]] = sum(float(d) for d,g in zip(differences,gates,strict=True) if g)
            rows.append(dict(family=fid,eligible_orientations=[j for j,g in enumerate(gates) if g],
                             eligible_count=sum(gates),difference_sum=gate_sums[si,index[fid]]))
        count = int(gate_counts[si].sum())
        represented = int(np.count_nonzero(gate_counts[si]))
        gate_records[str(k)] = dict(eligible_triplets=count,represented_families=represented,
                                   geometry_threshold_met=represented>=20,families=rows)
        per_seed[str(k)] = {metric:float(p["summary"][metric]-r["summary"][metric]) for metric in selected}
        per_seed[str(k)]["M_G"] = float(gate_sums[si].sum()/count) if count else None
        per_seed[str(k)]["all_family_margin"] = p["summary"]["all_family_margin"]-r["summary"]["all_family_margin"]
    output, family_deltas = {}, {}
    for metric, field in family_fields.items():
        values = np.zeros((len(SEEDS),len(fids)),dtype=float)
        for si,k in enumerate(SEEDS):
            for fi in selected[metric]:
                fid=fids[fi]
                values[si,fi] = states[f"seed{k}_P_B"]["families"][fid][field]-states[f"seed{k}_R_B"]["families"][fid][field]
        averaged = values[:,selected[metric]].mean(axis=0)
        mean_by_family = values.mean(axis=0)
        estimates = mean_by_family[sampled_selected[metric]].mean(axis=1)
        tail = (1.0-CONFIDENCE)/2
        output[metric] = dict(estimate=float(averaged.mean()),
                             interval=[float(x) for x in np.quantile(estimates,[tail,1-tail])],
                             undefined_draws=0, families=len(selected[metric]))
        family_deltas[metric] = {fids[fi]:[float(x) for x in values[:,fi]] for fi in selected[metric]}
    primary_draws = sampled_selected["E"]
    sampled_sums = np.stack([gate_sums[si][primary_draws].sum(axis=1) for si in range(len(SEEDS))])
    sampled_counts = np.stack([gate_counts[si][primary_draws].sum(axis=1) for si in range(len(SEEDS))])
    estimates = gated_ratio_mean(sampled_sums,sampled_counts)
    undefined = int(np.count_nonzero(~np.isfinite(estimates)))
    tail = (1.0-CONFIDENCE)/2
    eligible = all(x["geometry_threshold_met"] for x in gate_records.values())
    output["M_G"] = dict(
        estimate=finite_or_none(gated_ratio_mean(gate_sums.sum(axis=1),gate_counts.sum(axis=1))),
        interval=None if undefined else [float(x) for x in np.quantile(estimates,[tail,1-tail])],
        undefined_draws=undefined,geometry_threshold_met=eligible,
        gate_by_seed={k:{x:v for x,v in row.items() if x!="families"} for k,row in gate_records.items()})
    patterns = dict(
        readout_loss=sign_met(output["E"],"negative"),
        distance_loss_among_correct_readouts=eligible and sign_met(output["M_G"],"negative"),
        object_confusion=sign_met(output["F"],"positive") and sign_met(output["C"],"negative"),
        implied_color_loss=sign_met(output["Q"],"positive") and sign_met(output["implicit_margin"],"negative"))
    stages = {}
    for k in SEEDS:
        per_family = []
        for family in primary:
            fid=family["id"]
            pa,ra,pb,rb = (states[f"seed{k}_{a}_{b}"]["families"][fid]["margin"]
                           for a,b in (("P","A"),("R","A"),("P","B"),("R","B")))
            da,db,total = pa-ra,(pb-pa)-(rb-ra),pb-rb
            if not np.isclose(da+db,total,atol=1e-12):
                raise ValueError("Stage accounting identity failed")
            per_family.append(dict(family=fid,D_A=da,D_B=db,final_gap=total))
        stages[str(k)] = {name:mean(f[name] for f in per_family) for name in ("D_A","D_B","final_gap")}
        stages[str(k)]["families"] = per_family
    return dict(contrasts=output,per_seed=per_seed,patterns=patterns,gate=gate_records,
                stage_accounting=stages,family_deltas=family_deltas,
                bootstrap=dict(draws=draws,seed=seed,confidence=CONFIDENCE,
                               familywise_alpha=0.05,number_of_contrasts=6,
                               sampling="whole families within strata; all variants and seeds retained",
                               seed_averaging="equal seed weight conditional on seeds 7, 8 and 9"))


def number(value):
    return "unresolved" if value is None else f"{value:+.4f}"


def report_markdown(metrics):
    """Write the measured contrasts beside their interpretation limits."""
    provenance = ("Preliminary results use color labels proposed by one model author. Human review remains pending."
                  if metrics["preliminary"] else "Two human raters agreed on the stored color labels.")
    text = ["# Color diagnostic results", "", provenance,
            "All 13 model states were evaluated on the same 100 families. Each family contains four caption variants.",
            "The 520 caption-condition inputs are reused across states.","",
            "Each contrast is the proposition arm minus the ratings control, averaged over seeds 7, 8 and 9.",
            "Paired intervals resample whole families within strata. Their 99.1667% level corrects six contrasts by Bonferroni.",
            "Intervals describe fresh-family variation conditional on these three trained seeds.","",
            "| Contrast | Mean difference | 99.1667% interval | Seed 7 | Seed 8 | Seed 9 |",
            "|---|---:|---|---:|---:|---:|"]
    names = dict(E="Exact color readout E",M_G="Margin among correct readouts M_G",F="Wrong-object answer rate F",
                 C="Condition-switch margin C",Q="Explicit-cue benefit Q",implicit_margin="Implicit color margin")
    for metric in METRICS:
        contrast = metrics["contrasts"][metric]
        ci=contrast["interval"]
        interval="unresolved" if ci is None else f"[{ci[0]:+.4f}, {ci[1]:+.4f}]"
        seeds=" | ".join(number(metrics["per_seed"][str(k)][metric]) for k in SEEDS)
        text.append(f"| {names[metric]} | {number(contrast['estimate'])} | {interval} | {seeds} |")
    all_margins=[metrics["per_seed"][str(k)]["all_family_margin"] for k in SEEDS]
    text += ["",f"The descriptive all-family margin difference is {number(mean(all_margins))}; "
             + ", ".join(f"seed {k}: {number(v)}" for k,v in zip(SEEDS,all_margins,strict=True))+".",
             "","The following decisions apply the predeclared interval signs to the proposed labels:","",
             "| Pattern | Interval signs |","|---|---|"]
    names2 = dict(readout_loss="Readout loss",distance_loss_among_correct_readouts="Distance loss among correct readouts",
                  object_confusion="Confusion between objects",implied_color_loss="Loss on implied colors")
    for key,value in metrics["patterns"].items():
        text.append(f"| {names2[key]} | {'Required signs met' if value else 'Unresolved'} |")
    text += ["","Geometry requires at least 20 represented families in each seed's shared correct-readout set.",
             "","| Seed | Eligible triplets | Represented families | Threshold |","|---|---:|---:|---|"]
    for k,row in metrics["contrasts"]["M_G"]["gate_by_seed"].items():
        text.append(f"| {k} | {row['eligible_triplets']} | {row['represented_families']} | {'Met' if row['geometry_threshold_met'] else 'Unresolved'} |")
    text += ["","Stage accounting describes the saved training trajectories:","",
             "| Seed | First phase D_A | Ratings phase D_B | Final gap |","|---|---:|---:|---:|"]
    for k,row in metrics["stage_accounting"].items():
        text.append(f"| {k} | {number(row['D_A'])} | {number(row['D_B'])} | {number(row['final_gap'])} |")
    text += ["","The primary readout score weights each explicit and multiple-object family equally.",
             "M_G weights eligible triplets within each seed, then weights the three seed ratios equally.",
             "The margin identity is m = s(anchor, matching) − s(anchor, mismatching) = (d_mismatch² − d_match²)/2.",
             "C averages the target-condition and distractor-condition margins; condition-independent scores give C = 0.",
             "Q = m_explicit − m_implicit. Stage contrasts satisfy final gap = D_A + D_B.",
             "The JSON files retain per-state readouts, implied-label scores, control color-invention rates, family margins and source hashes.",
             "Human label review and the recorded probe-provenance checks determine eligibility for a confirmatory interpretation.",""]
    return "\n".join(x for i,x in enumerate(text) if x or i==0 or text[i-1])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--probe",type=Path,required=True)
    parser.add_argument("--results",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--draws",type=int,default=10000)
    parser.add_argument("--bootstrap-seed",type=int,default=61028)
    parser.add_argument("--preliminary",action="store_true")
    args=parser.parse_args()
    if args.draws<100:
        raise ValueError("Analysis requires at least 100 bootstrap draws")
    probe=json.loads(args.probe.read_text())
    human_review=probe.get("human_review")
    reviewed=isinstance(human_review,dict) and human_review.get("status")=="two_humans_agree"
    if not reviewed and not args.preliminary:
        raise ValueError("Human label review remains pending; use --preliminary for exploratory analysis")
    probe_hash=file_sha256(args.probe)
    states={name:load_state(probe,probe_hash,args.results/name) for name in STATE_NAMES}
    result=contrasts(probe,states,args.draws,args.bootstrap_seed)
    result.update(preliminary=bool(args.preliminary or not reviewed),created_unix=time.time(),
                  label_source=probe.get("label_source"),human_review=human_review,
                  counts=dict(families=len(probe["families"]),inputs=len(probe["inputs"]),states=len(states),
                              strata=dict(Counter(f["stratum"] for f in probe["families"]))),
                  source_sha256=dict(probe=probe_hash,parser=file_sha256(probe_module.__file__),
                                     analysis=file_sha256(__file__)),
                  state_metrics={name:s["summary"] for name,s in states.items()},
                  state_artifacts={name:s["artifact_sha256"] for name,s in states.items()},
                  interpretation="exploratory labels; stage comparisons are descriptive")
    result["formulas"]=dict(E="mean_family(mean_input[decoded exact color set equals literal label])",
        M_G="mean_seed(sum eligible triplet P-minus-R margins / eligible triplet count)",
        F="mean_multiple_family(mean_input[decoded color set equals distractor color set])",
        C="mean_family(mean_anchor[(target-condition margin + distractor-condition margin)/2])",
        Q="mean_implied_family[explicit margin - implicit margin]",
        implicit_margin="mean_implied_family[cos(implicit, matching anchor)-cos(implicit, mismatching anchor)]",
        D_A="P_A - R_A",D_B="(P_B-P_A)-(R_B-R_A)")
    args.output.mkdir(parents=True,exist_ok=True)
    family_deltas=result.pop("family_deltas")
    gate=result.pop("gate")
    family_stage={k:row.pop("families") for k,row in result["stage_accounting"].items()}
    dump_json(args.output/"family_metrics.json",dict(
        state_families={name:s["families"] for name,s in states.items()},
        family_contrasts=family_deltas,gated_triplets=gate,stage_accounting=family_stage))
    dump_json(args.output/"parsed_answers.json",{name:s["parsed_answers"] for name,s in states.items()})
    dump_json(args.output/"metrics.json",result)
    (args.output/"report.md").write_text(report_markdown(result))
    print(json.dumps(dict(status="complete",preliminary=result["preliminary"],
                          report=str(args.output/"report.md"),patterns=result["patterns"])))


if __name__ == "__main__":
    main()
