"""CPU analysis of immutable Qwen predictions; no inference or prompt selection here."""
import argparse,collections,datetime as dt,fcntl,hashlib,json,os,sys,time
from pathlib import Path
import numpy as np
from scipy.optimize import lsq_linear
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
ROOT=Path(__file__).resolve().parents[2];RUN=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
OUT=ROOT/"training_outputs/moral_geometry_20261110";OUT.mkdir(parents=True,exist_ok=True)
def save(p,x):
 p=Path(p);t=p.with_suffix(".tmp");t.write_text(json.dumps(x,indent=2,allow_nan=False)+"\n");t.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(x):
 n=np.linalg.norm(x,axis=-1,keepdims=True);return np.divide(x,n,out=np.zeros_like(x),where=n>1e-8)
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def boot(values,seed=20261110):
 values=np.array(values,float);rng=np.random.default_rng(seed)
 samples=np.mean(rng.choice(values,(2000,len(values)),replace=True),axis=1)
 return np.quantile(samples,[.025,.975]).tolist()
def correlation(x,y):
 v=float(spearmanr(x,y).statistic);return v if np.isfinite(v) else None
def family_summary(records):
 by=collections.defaultdict(list)
 for r in records:by[r["family"]].append(r["accuracy"])
 means={k:float(np.mean(v)) for k,v in by.items()}
 return dict(n=len(records),families=len(means),accuracy=float(np.mean(list(means.values()))),ci95=boot(list(means.values())),by_family=means,recall1=float(np.mean([r["recall1"] for r in records])),mrr=float(np.mean([r["mrr"] for r in records])))
def ranking(scores):
 pos=scores[0];others=scores[1:];wins=[1. if pos>x+1e-7 else 0. if pos<x-1e-7 else .5 for x in others]
 above=sum(x>pos+1e-7 for x in scores);equal=sum(abs(x-pos)<=1e-7 for x in scores)
 recall=(1/equal if above==0 else 0.)
 return float(np.mean(wins)),float(recall),float(np.mean([1/i for i in range(above+1,above+equal+1)]))
def main():
 start=time.monotonic()
 folder=RUN/"gpu_return"
 if not (folder/"embeddings.npz").exists():
  failure=json.loads((folder/"compute.json").read_text()) if (folder/"compute.json").exists() else {"status":"no retained inference"}
  save(OUT/"partial.json",dict(status="partial",failure=failure,missing=["Qwen embedding completion","conditioning evaluation","geometry comparison"],recommendation="revise execution; scientific questions unresolved"))
  (OUT/"REPORT.md").write_text("# Moral geometry pilot: partial\n\nNo completed Qwen predictions are available. Scientific questions remain unresolved. See partial.json for the observed failure. No training was repeated.\n")
  return
 collection=json.loads((RUN/"collection.json").read_text())
 for name,proof in collection["files"].items():assert sha(folder/name)==proof["sha256"]
 data=np.load(folder/"embeddings.npz");keys=[str(k) for k in data["keys"]];vectors=data["vectors"]
 assert len(set(keys))==len(keys) and vectors.shape==(len(keys),4096) and np.isfinite(vectors).all()
 lookup=dict(zip(keys,vectors));design=json.loads((RUN/"design_v2.json").read_text());principles=design["principles"]
 def enc(text,c=None):
  prompt=text if c is None else design["prompt"].format(passage=text,condition=c)
  return lookup[hashlib.sha256(prompt.encode()).hexdigest()]
 def transformed(cases,kind,dim):
  condition=principles[dim]["definition"]
  if kind=="unconditioned":return np.stack([enc(c["text"]) for c in cases])
  if kind=="neutral":return np.stack([enc(c["text"],"overall semantic content") for c in cases])
  if kind=="short":return np.stack([enc(c["text"],principles[dim]["short"]) for c in cases])
  if kind=="paraphrase":return np.stack([enc(c["text"],principles[dim]["paraphrase"]) for c in cases])
  if kind=="oracle_cards":return np.stack([enc(c["evidence"][dim],condition) for c in cases])
  x=np.stack([enc(c["text"],condition) for c in cases])
  if kind=="residual":x=norm(x-np.stack([enc(c["text"],"overall semantic content") for c in cases]))
  return x
 original_transform=transformed;feature_cache={}
 def transformed(cases,kind,dim):
  key=(kind,dim)
  if key not in feature_cache:feature_cache[key]=original_transform(cases,kind,dim)
  return feature_cache[key]
 # Geometry heads: cached, label-compatible, train-only PCA and identical convex objectives.
 train=json.loads((RUN/"cleaned_train.json").read_text());dev=json.loads((RUN/"cleaned_dev.json").read_text());test=json.loads((RUN/"cleaned_test.json").read_text())
 train_vectors=np.stack([enc(r[k],r["condition"]) for r in train for k in ["sentence1","sentence2"]])
 trained=[];geometry_ref=[];head_receipts=[];basis_cache={};bases={}
 for seed in [10,11,12]:
  for size in [64,256]:
   for psd in [False,True]:
    ident=f"{'psd' if psd else 'signed'}_s{seed}_n{size}"
    artifact=RUN/("head_v2_"+ident+".npz");receipt=RUN/("head_v2_"+ident+".json")
    compatibility=hashlib.sha256((sha(folder/"embeddings.npz")+sha(RUN/"encoder_identity.json")+sha(folder/"embeddings.npz")+sha(RUN/"cleaned_train.json")+str(seed)+str(size)+str(psd)+".001/64/pca-v1").encode()).hexdigest()
    if artifact.exists() and receipt.exists():
     record=json.loads(receipt.read_text());assert record["compatibility"]==compatibility and sha(artifact)==record["sha256"]
     f=np.load(artifact);mean,components,w=f["mean"],f["components"],f["weights"]
    else:
     if dt.datetime.now(dt.timezone.utc)>=dt.datetime(2026,11,10,13,tzinfo=dt.timezone.utc):
      head_receipts.append(dict(arm=ident,status="missing_deadline"));continue
     if seed not in bases:
      pca=PCA(n_components=64,svd_solver="randomized",random_state=seed,iterated_power=2).fit(train_vectors)
      bases[seed]=(pca.mean_,pca.components_)
     mean,components=bases[seed];fit=train[:size]
     left=norm((np.stack([enc(r["sentence1"],r["condition"]) for r in fit])-mean)@components.T)
     right=norm((np.stack([enc(r["sentence2"],r["condition"]) for r in fit])-mean)@components.T)
     x=left*right;y=np.array([(r["rating"]-1)/4 for r in fit])
     penalty=np.sqrt(len(fit)*.001/64);a=np.vstack([x,penalty*np.eye(64)]);b=np.concatenate([y,penalty*np.ones(64)])
     if psd:
      solved=lsq_linear(a,b,bounds=(0,np.inf),method="bvls",tol=1e-10,max_iter=1000);assert solved.success,solved.message;w=solved.x
     else:w=np.linalg.lstsq(a,b,rcond=None)[0]
     temp=artifact.with_suffix(".tmp.npz");np.savez(temp,mean=mean,components=components,weights=w);temp.replace(artifact)
     record=dict(arm=ident,seed=seed,train_rows=len(fit),basis_fit_unlabeled_rows=len(train),basis="randomized training-only PCA, seed varies basis approximation",constraint="w>=0" if psd else "signed",negative_weights=int((w< -1e-8).sum()),objective=float(np.mean((x@w-y)**2)+.001*np.mean((w-1)**2)),compatibility=compatibility,sha256=sha(artifact))
     save(receipt,record)
    trained.append((ident,mean,components,w));head_receipts.append(record)
 for split,rr in [("dev",dev),("test",test)]:
  for r in rr:
   left,right=enc(r["sentence1"],r["condition"]),enc(r["sentence2"],r["condition"])
   scores={"restored_Qwen_cosine":float(np.dot(left,right))}
   for ident,mean,components,w in trained:
    a=norm((left-mean)@components.T);b=norm((right-mean)@components.T);scores[ident]=float(np.dot(a*w,b))
   geometry_ref.append(dict(id=r["row_id"],family=r["group_id"],split=split,target=(r["rating"]-1)/4,scores=scores))
 save(RUN/"reference_predictions_v2.json",geometry_ref);save(RUN/"head_receipts.json",head_receipts)
 reference={}
 for arm in geometry_ref[0]["scores"]:
  rr=[r for r in geometry_ref if r["split"]=="test"];x=[r["scores"][arm] for r in rr];y=[r["target"] for r in rr]
  reference[arm]=dict(n=len(rr),spearman=correlation(x,y),mse=float(np.mean((np.array(x)-y)**2)),source="cleaned JEP v1.1 audited labels; exploratory reference evaluation")
 # Cross-family retrieval. Every method uses the same candidate pools.
 cases=json.loads((RUN/"cases_v2.json").read_text());case_index={c["id"]:i for i,c in enumerate(cases)}
 baseline=TfidfVectorizer(ngram_range=(1,2),lowercase=True).fit_transform([c["text"] for c in cases]);lex=(baseline@baseline.T).toarray()
 methods=["unconditioned","neutral","short","defined","paraphrase","residual","difference","oracle_cards","lexical"]
 grams={}
 for dim in range(3):
  for method in methods:
   if method=="lexical":g=lex
   elif method=="difference":
    a=transformed(cases,"defined",dim);b=transformed(cases,"neutral",dim);g=a@a.T-b@b.T
   else:a=transformed(cases,method,dim);g=a@a.T
   grams[(method,dim)]=g
  for ident,mean,components,w in trained:
   a=norm((transformed(cases,"defined",dim)-mean)@components.T);grams[(ident,dim)]=(a*w)@a.T
 predictions=[];byid={c["id"]:c for c in cases}
 def case_id(f,bits):return f+"_"+"".join(map(str,bits))
 for split in ["dev","primary","reserve"]:
  families=list(dict.fromkeys(c["family"] for c in cases if c["split"]==split))
  for fi,family in enumerate(families):
   other=families[(fi+1)%len(families)];third=families[(fi+2)%len(families)]
   for anchor in [c for c in cases if c["family"]==family]:
    bits=anchor["bits"]
    for dim in range(3):
     good=[v if j==dim else 1-v for j,v in enumerate(bits)];bad=list(bits);bad[dim]=1-bad[dim]
     candidates=[case_id(other,good),case_id(family,bad),case_id(third,bad)]
     for method in methods+[x[0] for x in trained]:
      g=grams[(method,dim)];scores=[float(g[case_index[anchor["id"]],case_index[x]]) for x in candidates]
      accuracy,recall,mrr=ranking(scores)
      predictions.append(dict(method=method,family=family,split=split,condition=principles[dim]["id"],anchor=anchor["id"],candidates=candidates,relevant_index=0,scores=scores,accuracy=accuracy,recall1=recall,mrr=mrr,label_source="synthetic operational hypothesis"))
 save(RUN/"retrieval_predictions_v2.json",predictions)
 # Freeze a single dev choice before any reserve metric is computed.
 eligible=["short","defined","paraphrase","residual","difference"]
 dev_scores={m:family_summary([r for r in predictions if r["split"]=="dev" and r["method"]==m])["accuracy"] for m in eligible}
 selected=max(eligible,key=lambda m:(dev_scores[m],-eligible.index(m)))
 choice=dict(selected=selected,dev_scores=dev_scores,rule="Maximum dev family accuracy; fixed eligible-method tie order. Oracle excluded.",at=now(),reserve_metrics_not_used=True)
 if (RUN/"dev_selection.json").exists():assert json.loads((RUN/"dev_selection.json").read_text())["selected"]==selected
 else:save(RUN/"dev_selection.json",choice)
 summary={}
 for split in ["dev","primary","reserve"]:
  summary[split]={m:family_summary([r for r in predictions if r["split"]==split and r["method"]==m]) for m in methods+[x[0] for x in trained]}
 effects={}
 for split in ["primary","reserve"]:
  for a,b in [(selected,"defined"),("defined","unconditioned"),("defined","neutral"),("residual","defined"),("oracle_cards","defined")]+[(f"psd_s{s}_n{n}",f"signed_s{s}_n{n}") for s in [10,11,12] for n in [64,256] if any(t[0]==f"psd_s{s}_n{n}" for t in trained)]:
   av,bv=summary[split][a]["by_family"],summary[split][b]["by_family"];delta=[av[f]-bv[f] for f in av]
   effects[split+"/"+a+" minus "+b]=dict(mean=float(np.mean(delta)),ci95=boot(delta),families=len(delta))
 # Fixed-candidate condition switches and relation-vector analogies use cached outputs only.
 switch_records=[];change_records=[]
 lexical_vectors=baseline.toarray()
 for split in ["dev","primary","reserve"]:
  families=list(dict.fromkeys(c["family"] for c in cases if c["split"]==split))
  for fi,family in enumerate(families):
   other=families[(fi+1)%len(families)]
   for anchor in [c for c in cases if c["family"]==family]:
    for aa in range(3):
     for bb in range(aa):
      one=list(anchor["bits"]);two=list(one);one[aa]=1-one[aa];two[bb]=1-two[bb]
      ids=[case_id(other,one),case_id(other,two)];ix=case_index[anchor["id"]]
      for method in methods:
       gap_a=float(grams[(method,aa)][ix,case_index[ids[1]]]-grams[(method,aa)][ix,case_index[ids[0]]])
       gap_b=float(grams[(method,bb)][ix,case_index[ids[0]]]-grams[(method,bb)][ix,case_index[ids[1]]])
       switch_records.append(dict(method=method,family=family,split=split,both_correct=bool(gap_a>1e-7 and gap_b>1e-7),gaps=[gap_a,gap_b]))
   for dim in range(3):
    base_id=case_id(family,[0,0,0]);edit=[0,0,0];edit[dim]=1;edit_id=case_id(family,edit)
    for method in ["defined","neutral","unconditioned","lexical"]:
     vv=lexical_vectors if method=="lexical" else transformed(cases,method,dim)
     direction=norm(vv[case_index[edit_id]]-vv[case_index[base_id]])
     other_base=case_index[case_id(other,[0,0,0])];scores=[]
     for edit_dim in [dim]+[d for d in range(3) if d!=dim]:
      b=[0,0,0];b[edit_dim]=1;delta=norm(vv[case_index[case_id(other,b)]]-vv[other_base]);scores.append(float(direction@delta))
     acc,r1,mrr=ranking(scores);change_records.append(dict(method=method,family=family,split=split,condition=principles[dim]["id"],scores=scores,accuracy=acc,recall1=r1,mrr=mrr))
 switch_summary={sp:{m:float(np.mean([r["both_correct"] for r in switch_records if r["split"]==sp and r["method"]==m])) for m in methods} for sp in ["primary","reserve"]}
 changes_summary={sp:{m:family_summary([r for r in change_records if r["split"]==sp and r["method"]==m]) for m in ["defined","neutral","unconditioned","lexical"]} for sp in ["primary","reserve"]}
 save(RUN/"condition_switch_predictions.json",switch_records);save(RUN/"change_analogy_predictions.json",change_records)
 # Model-only Gram diagnostics, not test-label matrix completion.
 diagnostics={}
 for (method,dim),g in grams.items():
  # One fixed condition on all primary families; bounded80 points for diagnostics.
  ix=[i for i,c in enumerate(cases) if c["split"]=="primary"][:80];matrix=g[np.ix_(ix,ix)];eig=np.linalg.eigvalsh(matrix)
  diag=np.diag(matrix)
  diagnostics[method+"/"+principles[dim]["id"]]=dict(min_eigenvalue=float(eig.min()),negative_eigenvalues=int((eig< -1e-5).sum()),min_diagonal=float(diag.min()),max_diagonal=float(diag.max()),note="Raw Gram/kernel. No unit-diagonal overwrite or projection used for prediction.")
 # Extensions: descriptive only; no unique theory-derived numeric gold.
 extension=json.loads((RUN/"extension_cases.json").read_text());extensions={}
 layers=np.load(folder/"layers.npz") if (folder/"layers.npz").exists() else None
 if layers is not None:
  layer_keys=[str(x) for x in layers["keys"]]
  for layer in [0,9,18,27,36]:
   lv=dict(zip(layer_keys,layers["layer_"+str(layer)]));invariance=[];typed=[]
   for theory in ["Utilitarianism","Deontology","Care Ethics"]:
    rows=[r for r in extension if r["theory"]==theory];families=list(dict.fromkeys(r["family"] for r in rows))
    repairs=[];sanctions=[];harms=[]
    for f in families:
     rr={r["type"]:r for r in rows if r["family"]==f};h=lv[rr["harm"]["key"]];re=lv[rr["repair"]["key"]];s=lv[rr["sanction"]["key"]]
     invariance.extend([float(h@lv[rr[k]["key"]]) for k in ["irrelevant_prefix","irrelevant_suffix"]])
     repairs.append(norm(re-h));sanctions.append(norm(s-h));harms.append(h)
    repairs=np.stack(repairs);sanctions=np.stack(sanctions)
    for i,f in enumerate(families):
     others=[j for j in range(len(families)) if j!=i]
     reference_axis=norm(np.mean(repairs[others],axis=0));repair_score=float(reference_axis@repairs[i]);sanction_score=float(reference_axis@sanctions[i])
     typed.append(dict(theory=theory,family=f,repair_alignment=repair_score,sanction_alignment=sanction_score,margin=repair_score-sanction_score))
   extensions[str(layer)]=dict(invariance_mean_cosine=float(np.mean(invariance)),invariance_min_cosine=float(np.min(invariance)),repair_vs_sanction_direction_margin=float(np.mean([r["margin"] for r in typed])),typed=typed,layer0_is_identical_EOD_null=layer==0)
  # Same-harm theory sensitivity measured using within-layer cosine matrices.
  theory_distances={}
  for layer in [0,9,18,27,36]:
   lv=dict(zip(layer_keys,layers["layer_"+str(layer)]));values=[]
   for family in sorted({r["family"] for r in extension}):
    rr=[r for r in extension if r["family"]==family and r["type"]=="harm" and r["theory"]!="restorative_aspect"]
    values.extend([1-float(lv[a["key"]]@lv[b["key"]]) for i,a in enumerate(rr) for b in rr[:i]])
   theory_distances[str(layer)]=dict(mean_same_harm_between_theories_cosine_distance=float(np.mean(values)),note="Prompt-framing sensitivity only; not a correctness score.")
  extensions["theory_sensitivity"]=theory_distances
 generated=json.loads((folder/"generated_tasks.json").read_text()) if (folder/"generated_tasks.json").exists() else []
 reasoning=[]
 for r in generated:
  reasoning.append(dict(family=r["family"],theory=r["theory"],raw_view_cosine=float(lookup[r["source_key"]]@lookup[r["key"]]),truncated=r["truncated"],view_was_shortened=r["view_was_shortened"],word_count=len(r["view"].split())))
 original=json.loads((RUN/"original_validation_predictions.json").read_text());old={r["row_id"]:r["prediction"] for r in original}
 replay=[abs(r["scores"]["restored_Qwen_cosine"]-old[r["id"]]) for r in geometry_ref if r["split"]=="dev"]
 replay_receipt=dict(rows=len(replay),max_abs_difference=float(max(replay)),mean_abs_difference=float(np.mean(replay)),original_predictions_sha256=sha(RUN/"original_validation_predictions.json"),compatible_numeric_replay=max(replay)<.005)
 save(RUN/"behavioral_replay.json",replay_receipt)
 reference_effects={}
 for seed in [10,11,12]:
  for size in [64,256]:
   aa=f"psd_s{seed}_n{size}";bb=f"signed_s{seed}_n{size}"
   if aa not in reference or bb not in reference:continue
   values=collections.defaultdict(list)
   for r in geometry_ref:
    if r["split"]=="test":values[r["family"]].append((r["scores"][aa]-r["target"])**2-(r["scores"][bb]-r["target"])**2)
   delta=[float(np.mean(v)) for v in values.values()]
   reference_effects[aa+" minus "+bb]=dict(family_mean_mse_difference=float(np.mean(delta)),ci95=boot(delta),families=len(delta),negative_favors_psd=True)
 result=dict(status="complete",condition_switch=switch_summary,change_analogy=changes_summary,behavioral_replay=replay_receipt,reference_effects=reference_effects,selection=choice,retrieval=summary,paired_effects=effects,reference=reference,geometry_diagnostics=diagnostics,extensions=extensions,reasoning_views=reasoning,head_receipts=head_receipts,counts=dict(embeddings=len(keys),synthetic_cases=len(cases),retrieval_predictions=len(predictions)),limits=["Synthetic operational hypotheses, no new human/expert moral validation.","Reserve only4families; no best-layer selection. Original cleaned reference test previously examined.","Oracle cards contain authored relevant source spans; upper bound, not autonomous evidence selection.","MET-D released weights used with forced grounds; no selector or new self-distillation; short generated views may truncate.","Harm→repair is typed and contextual, not assumed reflection or moral cancellation."],analysis_seconds=time.monotonic()-start)
 save(RUN/"results_v2.json",result);save(OUT/"results.json",result)
 # Public derived predictions omit restricted C-STS source text; synthetic cases are authored.
 save(OUT/"synthetic_cases.json",cases);save(OUT/"synthetic_predictions.json",predictions);save(OUT/"reference_predictions.json",geometry_ref)
 save(OUT/"extension_cases.json",extension);save(OUT/"reasoning_views.json",generated)
 subprocess_command=[sys.executable,str(Path(__file__).with_name("verify_metrics.py"))]
 import subprocess
 subprocess.run(subprocess_command,check=True)
 from report import write_report
 write_report(result)
 try:subprocess.run([sys.executable,str(Path(__file__).with_name("visualize.py"))],check=True)
 except Exception as error:save(OUT/"visualization_pending.json",dict(error=repr(error),scientific_report_preserved=True))
if __name__=="__main__":
 with (RUN/"execution.lock").open("a") as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise SystemExit("Live pipeline owner; no duplicate CPU work")
  main()
