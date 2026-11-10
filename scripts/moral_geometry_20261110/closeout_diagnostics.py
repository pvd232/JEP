"""Add transparent post-run diagnostics without new inference or fitting a model."""
import hashlib,json
from pathlib import Path
import numpy as np
from report import write_report
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110");O=Path(__file__).resolve().parents[2]/"training_outputs/moral_geometry_20261110"
x=json.loads((R/"results_v2.json").read_text())
x["runtime_replay_diagnostic"]=json.loads((R/"replay_probe_receipt.json").read_text())
case=json.loads((R/"extension_cases.json").read_text());data=np.load(R/"gpu_return/embeddings.npz");v=dict(zip([str(k) for k in data["keys"]],data["vectors"]))
rows=[r for r in case if r["condition"]=="material restitution for the harm described"];families=sorted({r["family"] for r in rows})
h=[];re=[]
for f in families:
 d={r["type"]:r for r in rows if r["family"]==f};h.append(v[d["harm"]["key"]]);re.append(v[d["repair"]["key"]])
h=np.stack(h);re=np.stack(re);diagnostic=[]
for i,f in enumerate(families):
 others=[j for j in range(len(families)) if j!=i]
 delta=np.mean(re[others]-h[others],axis=0);query=h[i]+delta;query=query/max(np.linalg.norm(query),1e-8)
 plain=h[i]@re.T;translated=query@re.T
 diagnostic.append(dict(family=f,plain_rank=int(1+sum(plain>plain[i]+1e-7)),translated_rank=int(1+sum(translated>translated[i]+1e-7))))
x["restorative_transfer_diagnostic"]=dict(status="post_hoc_diagnostic_not_confirmation",rationale="High repair-versus-sanction alignment might be generic positive valence. Check whether translation adds anything beyond raw topic similarity among equally positive candidate repairs.",families=diagnostic,plain_recall1=sum(r["plain_rank"]==1 for r in diagnostic)/len(diagnostic),translated_recall1=sum(r["translated_rank"]==1 for r in diagnostic)/len(diagnostic),limits="Same six previously inspected authored families; no valence-matched non-reparative benefit control; no expert sufficiency judgments.")
for p in [R/"results_v2.json",O/"results.json"]:p.write_text(json.dumps(x,indent=2,allow_nan=False)+"\n")
write_report(x)
extra="\n## Outcome and follow-up decision\n\n"
extra+=f"Defined conditioning reached {x['retrieval']['primary']['defined']['accuracy']:.1%} pairwise ranking accuracy, compared with {x['retrieval']['primary']['unconditioned']['accuracy']:.1%} without a condition and {x['retrieval']['primary']['lexical']['accuracy']:.1%} for the unconditioned lexical control. The development-selected paraphrase added no reserve gain over the defined-condition baseline; both reached the synthetic ceiling. This demonstrates aspect-following in these deliberately structured cases, not a new moral reasoning capability. A rule given the authored factual profiles could solve this screen perfectly.\n\n"
extra+="PSD improved the small compressed heads relative to their signed counterparts, especially with 64 labels, but every head remained worse than the unchanged Qwen cosine baseline on this reference subset. This supports investigating ordinary regularization, not claiming a new moral metric advantage over the existing encoder.\n\n"
extra+=f"The post-hoc repair-translation diagnostic retrieved the authored matched response at rank 1 in {x['restorative_transfer_diagnostic']['plain_recall1']:.0%} of cases using ordinary cosine and {x['restorative_transfer_diagnostic']['translated_recall1']:.0%} after a leave-one-family-out translation. It is an exploratory control, not a fresh confirmation result. Generic valence and shared topic remain alternative explanations for the apparent relation direction.\n\n"
extra+="**Strict historical numerical replay did not pass.** The original runtime was PyTorch 2.14.0+cu130 / Transformers 5.20.2 / PEFT 0.21.2; this run used 2.9.1+cu129 /4.57.1 /0.17.1. Restoring the original batch layout still left a maximum absolute cosine difference of 0.016163 on the diagnostic batch. The exact adapter weights were verified, but these are new-runtime outputs, not an exact reproduction of historical predictions. All comparisons in the pilot share the current runtime.\n\n"
extra+="All 18 short MET-D views hit the 96-token bound and often retained introductory meta-reasoning. The decoder-view arm therefore remains incomplete as a test of useful grounded reasoning. Preserve its outputs and improve the generation protocol on fresh scenarios before evaluating a reasoning-to-encoder gain.\n\n"
extra+="The next useful study is a harder, independently reviewed cross-family dataset: implicit harms, competing principles, role-sensitive responsibility, irrelevant-fact and linguistic invariants, and valence-matched alternative remedies. Keep fixed harm under alternative explicit theories, test selective sensitivity, and compare raw text, well-formed reasoning views and matched factual extraction. All cases here are English; Spanish/Colombian cultural transfer remains untested. These changes need fresh held-outs rather than tuning this screen.\n"
for p in [R/"REPORT.md",O/"REPORT.md",O/"README.md"]:p.write_text(p.read_text()+extra)
print("CLOSEOUT_DIAGNOSTIC",x["restorative_transfer_diagnostic"])
