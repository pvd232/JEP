"""Evaluate the frozen directed-response diagnostic from retained embeddings only."""
import collections,hashlib,json,sys
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-followup-20261110")
O=Path(__file__).parent.parent/"benchmark_v2"
CPU_ONLY="--cpu-only" in sys.argv
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+"\n")
def boot(x):
 rng=np.random.default_rng(232);return np.quantile(rng.choice(x,(2000,len(x))).mean(1),[.025,.975]).tolist()
def main():
 d=json.loads((R/"dataset.json").read_text());f=R/"gpu_return";compute=json.loads((f/"compute.json").read_text()) if not CPU_ONLY else {"status":"complete","encoder":None,"torch":None}
 if compute["status"]!="complete":
  save(O/("cpu_results.json" if CPU_ONLY else "qwen_results.json"),dict(status="partial",error=compute.get("error")));return
 v={}
 if not CPU_ONLY:
  data=np.load(f/"embeddings.npz");v=dict(zip([str(k) for k in data["keys"]],data["vectors"]));assert len(v)==324
 def enc(text,condition):
  p="Instruct: Represent the passage for semantic similarity with respect to this condition: "+condition+"\nQuery: "+text
  return v[hashlib.sha256(p.encode()).hexdigest()]
 qmap={q["id"]:q for q in d["queries"]};cmap={c["id"]:c for c in d["candidates"]};gold={r["query_id"]:set(r["relevant_candidate_ids"]) for r in d["relevant_sets"]}
 corpus=[x["text"] for x in d["queries"]+d["candidates"]]+[q["condition"] for q in d["queries"]]
 lexical=TfidfVectorizer(ngram_range=(1,2)).fit(corpus)
 methods=["Qwen_conditioned","Qwen_neutral","lexical_query","lexical_with_condition","attribute_oracle"]
 if CPU_ONLY:methods=methods[2:]
 predictions=[]
 for q in d["queries"]:
  cs=[cmap[cid] for cid in q["candidate_ids"]];qlex=lexical.transform([q["text"]]);clex=lexical.transform([c["text"] for c in cs]);condlex=lexical.transform([q["condition"]]);aug=qlex+condlex
  aug=aug/max(float(np.sqrt(aug.multiply(aug).sum())),1e-8)
  for method in methods:
   if method.startswith("Qwen"):
    cond=q["condition"] if method=="Qwen_conditioned" else "overall semantic content"
    scores=[float(enc(q["text"],cond)@enc(c["text"],cond)) for c in cs]
   elif method=="lexical_query":scores=(qlex@clex.T).toarray()[0].tolist()
   elif method=="lexical_with_condition":scores=(aug@clex.T).toarray()[0].tolist()
   else:scores=[float((q["criterion_id"]=="completed_typed_response" and c["response_class"]=="completed") or (q["criterion_id"]=="acknowledgment_voice" and c["response_class"]=="voice")) for c in cs]
   target=next(i for i,c in enumerate(cs) if c["id"] in gold[q["id"]]);s=scores[target];above=sum(t>s+1e-7 for t in scores);tied=sum(abs(t-s)<=1e-7 for t in scores)
   top=[cs[i]["id"] for i,t in enumerate(scores) if abs(t-max(scores))<=1e-7]
   predictions.append(dict(query=q["id"],family=q["family"],split=q["split"],variant=q["variant"],criterion=q["criterion_id"],method=method,candidates=q["candidate_ids"],scores=scores,gold=list(gold[q["id"]]),top=top,recall1=1/tied if above==0 else 0,mrr=float(np.mean([1/k for k in range(above+1,above+tied+1)])),strict_correct=above==0 and tied==1))
 save(O/("cpu_predictions.json" if CPU_ONLY else "qwen_predictions.json"),predictions)
 results={}
 for method in methods:
  rows=[r for r in predictions if r["method"]==method and r["split"]=="test"];by=collections.defaultdict(list)
  for row in rows:by[row["family"]].append(row["recall1"])
  vals=[float(np.mean(x)) for x in by.values()]
  switches=[]
  for pair in d["criterion_switch_pairs"]:
   selected=[r for r in rows if r["query"] in pair["query_ids"]]
   if selected:switches.append(all(r["strict_correct"] for r in selected))
  invariant=[]
  for family in by:
   for criterion in {r["criterion"] for r in rows}:
    rr=[r for r in rows if r["family"]==family and r["criterion"]==criterion]
    invariant.append(set(rr[0]["top"])==set(rr[1]["top"]))
  results[method]=dict(test_queries=len(rows),test_families=len(by),recall1=float(np.mean(vals)),ci95=boot(vals),mrr=float(np.mean([r["mrr"] for r in rows])),joint_strict_switch_accuracy=float(np.mean(switches)),passive_topset_stability=float(np.mean(invariant)))
 # Independent observer reconstructs strict success directly from score comparisons.
 for row in predictions:
  gi=row["candidates"].index(row["gold"][0]);strict=all(row["scores"][gi]>s+1e-7 for i,s in enumerate(row["scores"]) if i!=gi)
  assert strict==row["strict_correct"]
 record=dict(status="complete",methods=results,epistemic_scope="Authored asserted attributes; not human moral/reparative adequacy.",lexical_scope="Unlabeled query/candidate corpus vocabulary and IDF; no gold labels used.",dataset_sha256=hashlib.sha256((R/"dataset.json").read_bytes()).hexdigest(),encoder=compute["encoder"],actual_runtime=compute["torch"],verification="Independent strict rank comparison passed",limitations=["English and structured synthetic cases","Only six test families","No expert validation","Directed victim/incident linking is distinct from cross-victim analogy","No theory/representation training or novel-architecture claim"])
 save(O/("cpu_results.json" if CPU_ONLY else "qwen_results.json"),record)
 fig,axes=plt.subplots(1,2,figsize=(10,4));labels=["Qwen + criterion","Qwen neutral","Lexical query","Lexical + criterion","Attribute oracle"]
 if CPU_ONLY:labels=labels[2:]
 for ax,metric,title in [(axes[0],"recall1","Response-linking Recall@1"),(axes[1],"joint_strict_switch_accuracy","Both criterion rankings correct")]:
  ax.bar(range(len(methods)),[results[m][metric] for m in methods],color=(["#aaa","#747f92","#c18c35"] if CPU_ONLY else ["#287e8e","#81909c","#aaa","#747f92","#c18c35"]));ax.set_xticks(range(len(methods)),labels,rotation=35,ha="right");ax.set_ylim(0,1.05);ax.set_title(title)
 fig.suptitle("Frozen response-attribute diagnostic · six test families");fig.tight_layout();fig.savefig(O/("cpu_diagnostic.svg" if CPU_ONLY else "qwen_diagnostic.svg"),bbox_inches="tight");plt.close(fig)
 lines=["# Follow-up execution results","", "This is an author-designed attribute diagnostic, not a validated JEP benchmark. Identical incident passages and seven response candidates are ranked under two criteria: completed named-party response versus acknowledged voice. All response candidates contain positive/supportive language; proposed, unknown-completion, other-beneficiary, sanction and non-repetition controls remain distinct.","","| Method | Test Recall@1 | Both criterion rankings correct | Passive top-set stability |","|---|---:|---:|---:|"]
 for method,r in results.items():lines.append(f"| {method} | {r['recall1']:.3f} | {r['joint_strict_switch_accuracy']:.3f} | {r['passive_topset_stability']:.3f} |")
 lines+=["","![Diagnostic](cpu_diagnostic.svg)" if CPU_ONLY else "![Diagnostic](qwen_diagnostic.svg)","","The attribute oracle consumes authored structured fields and is only an upper bound. The neutral retriever receives the same passage/pool for both criteria, so its inability to reverse rankings is expected by construction; criterion-aware lexical retrieval is the more informative control. Invariance alone can be achieved by a useless constant ranker. No supervised parameters were fitted or chosen on these test families.","","Results need Spanish testimony, independently judged relevance, and measured reviewer effort before any claim of JEP utility. This test links an actual response to a named party/incident; retrieving analogous repairs for other victims is a different relation and should not inherit these negative labels."]
 (O/("CPU_REPORT.md" if CPU_ONLY else "QWEN_REPORT.md")).write_text("\n".join(lines)+"\n")
 s=json.loads((R/"state.json").read_text());s.update(phase="cpu_controls_complete_qwen_capacity_blocked" if CPU_ONLY else "complete",next_action="Publish scoped literature review and retained follow-up results; no further inference.",owner_relinquished=True);save(R/"state.json",s)
 print(json.dumps(results))
if __name__=="__main__":main()
