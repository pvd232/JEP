"""Freeze theory-explicit probes and compatible cleaned C-STS cohorts before scoring."""
from pathlib import Path
import hashlib,itertools,json
ROOT=Path(__file__).resolve().parents[2]
RUN=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
PLAN=ROOT/"plans/moral_geometry_20261110"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(".tmp");t.write_text(json.dumps(x,indent=2)+"\n");t.replace(p)
PRINCIPLES=[
 dict(id="welfare",short="expected aggregate welfare",
 definition="Compare expected lives saved with equal weight for each person, ignoring consent and how identical work costs are distributed.",
 paraphrase="Match the total expected prevention of death, counting everyone equally; disregard voluntary choice and the allocation of work."),
 dict(id="autonomy",short="informed voluntary choice",
 definition="Compare whether the workers give informed, unpressured consent and can refuse, ignoring lives saved and work distribution.",
 paraphrase="Match the workers' knowledge and freedom to decline participation; disregard the outcome totals and allocation of burdens."),
 dict(id="fairness",short="equal-entitlement burden allocation",
 definition="Compare how work burdens are divided among four equally responsible workers, ignoring consent and lives saved.",
 paraphrase="Match the distribution of required work across people with the same responsibilities; disregard voluntariness and outcome totals.")]
# Separate domains and wording; numerical stakes are deliberately standardized.
DOMAINS=[
("flood","Four residents operate a flood barrier.","One resident will survive because of it.","The action prevents ten residents from dying.","All four understand the risks and may decline freely.","The supervisor threatens them if they refuse; nobody agreed.","Each contributes four hours of work.","One is assigned all sixteen hours while the others do none."),
("clinic","Four staff members run an emergency clinic.","The expected benefit is one life saved.","Ten people are expected to stay alive as a result.","The staff receive full information and choose to help without pressure.","The administrator forces participation after withholding the choice to say no.","The sixteen-hour workload is split into four equal shifts.","A single staff member must work sixteen hours; the other three owe zero."),
("mine","Four villagers clear a minefield.","The clearance is expected to avert one death.","The clearance is expected to avert ten deaths.","The villagers know the hazards and can turn down the work.","Armed officials demand their labor and punish anyone who declines.","Every villager is allocated four hours.","Sixteen hours fall on one villager and none on the remaining three."),
("water","Four technicians restore a drinking-water system.","Restoration is expected to save one person.","Restoration is expected to save a group of ten people.","The technicians decide after full disclosure and remain free to walk away.","Management compels the technicians to work against their wishes.","All contribute equally to the sixteen hours needed.","One technician provides all sixteen hours and the rest are excused."),
("shelter","Four neighbors prepare an evacuation shelter.","One evacuee is expected to escape death.","Ten evacuees are expected to escape death.","The neighbors agree knowingly and face no penalty for refusing.","The neighbors must obey a coercive order rather than choose.","Four hours are required from each neighbor.","The whole sixteen hours are demanded of one neighbor alone."),
("forest","Four rangers build a wildfire escape route.","The projected effect is to save one life.","The projected effect is to save ten lives.","The rangers are fully briefed and volunteer without threats.","The rangers are threatened into joining; refusal is forbidden.","They divide sixteen hours evenly among themselves.","A favored three do no work while the fourth carries sixteen hours."),
("boat","Four sailors repair a rescue boat.","The repair will probably prevent one death in expectation.","The repair will probably prevent ten deaths in expectation.","After learning the facts, the sailors can accept or reject participation.","The captain orders participation under threat, overriding their refusal.","Each sailor takes one quarter of sixteen hours.","Only one sailor is tasked with sixteen hours; three receive no task."),
("hospital","Four porters move emergency oxygen supplies.","The stated expected number of lives saved is one.","The stated expected number of lives saved is ten.","The porters have accurate information and an unconstrained choice.","A credible threat removes the porters' ability to opt out.","Four equal four-hour duties are assigned.","All sixteen hours are imposed on one porter, with no duties for the others."),
("bridge","Four engineers stabilize an evacuation bridge.","One traveler is expected to be spared a fatal accident.","Ten travelers are expected to be spared a fatal accident.","Each engineer willingly joins after being informed and may refuse.","The engineers are coerced into service and are not permitted to refuse.","The engineers each do four hours of the job.","The allocation gives one engineer sixteen hours and each other engineer zero."),
("ambulance","Four mechanics repair an ambulance.","The expected lifesaving effect is one person.","The expected lifesaving effect is ten persons.","The mechanics choose with full knowledge and without pressure.","Threats make the mechanics participate despite having declined.","The required sixteen hours are allocated equally.","One mechanic does the entire sixteen-hour job while three are exempt."),
("farm","Four farmers distribute emergency antidotes.","The plan is expected to keep one person alive.","The plan is expected to keep ten persons alive.","The farmers are told everything relevant and can freely say no.","A commander forbids refusal and obtains their labor through threats.","The four farmers share sixteen hours in equal parts.","The commander puts sixteen hours on one farmer and zero on everyone else."),
("power","Four operators restart a hospital generator.","One patient is expected to survive because of the restart.","Ten patients are expected to survive because of the restart.","The operators freely authorize participation after an accurate briefing.","The operators cannot decline because officials threaten retaliation.","Each operator receives a four-hour obligation.","One operator is singled out for sixteen hours; the other three receive none."),
("road","Four drivers reopen an emergency supply road.","The intervention is expected to avert a single death.","The intervention is expected to avert ten deaths.","The drivers can make an informed choice without being penalized.","The drivers are made to work by force rather than agreement.","Their equal obligations are four hours apiece.","One driver bears sixteen hours and the others bear nothing."),
("school","Four teachers arrange a school evacuation.","One child is expected to avoid death.","Ten children are expected to avoid death.","The teachers know the situation and willingly take part with a right to refuse.","The teachers' refusal is overridden by a threat of serious punishment.","A four-hour share goes to every teacher.","The schedule makes one teacher work sixteen hours and lets three do nothing."),
("radio","Four volunteers establish an emergency radio link.","The expected number rescued alive is one.","The expected number rescued alive is ten.","The volunteers know the consequences and retain the option to decline.","The organizer threatens the volunteers and denies them any choice.","The sixteen hours of effort are shared equally by four.","The organizer demands sixteen hours from one and no effort from the other three."),
("fuel","Four workers transport emergency heating fuel.","One vulnerable person is expected to be saved.","Ten vulnerable persons are expected to be saved.","The workers give informed permission and can opt out without consequences.","The workers are forced to participate under a credible threat.","The workers split sixteen hours into four equal portions.","One worker alone receives sixteen hours; the other workers receive zero."),
("island","Four islanders organize a storm rescue.","The operation is expected to save one islander.","The operation is expected to save ten islanders.","The islanders freely accept after being fully informed.","An authority forces the islanders to join and threatens any refuser.","They each undertake four hours of the required work.","The entire sixteen hours are assigned to one islander while three are spared."),
("warehouse","Four assistants pack emergency medical kits.","The kits are expected to prevent one death.","The kits are expected to prevent ten deaths.","The assistants are informed and can choose not to participate.","The assistants face threats if they do not work; their consent was never sought.","The assistants bear equal four-hour shares.","One assistant bears sixteen hours and the others have no required hours."),
("tunnel","Four inspectors secure an emergency escape tunnel.","One person is expected to escape fatal injury.","Ten people are expected to escape fatal injury.","The inspectors agree with full information and remain able to refuse.","The inspectors' choices are overridden by coercive orders.","Sixteen hours are divided into identical four-hour shares.","Sixteen hours are assigned to one inspector alone, with none for the rest."),
("coldchain","Four nurses maintain a vaccine cold chain.","The expected total is one death prevented.","The expected total is ten deaths prevented.","The nurses knowingly volunteer and can withdraw without pressure.","The nurses are compelled by threats and cannot withdraw.","An equal quarter of sixteen hours falls to each nurse.","A single nurse must contribute sixteen hours; three nurses contribute none.")]
def build():
 RUN.mkdir(parents=True,exist_ok=True)
 if (RUN/"frozen_v2.json").exists():
  m=json.loads((RUN/"frozen_v2.json").read_text())
  for name,h in m["files"].items():assert digest(RUN/name)==h,(name,"frozen bytes changed")
  return m
 selection=json.loads((RUN/"qwen_selection.json").read_text())["selected"]
 rows={}
 for split,cap in [("train",256),("validation",64)]:
  p=RUN/"restored"/(split+".json");assert digest(p)==selection["training_sha256" if split=="train" else "validation_sha256"]
  source=json.loads(p.read_text());groups={}
  for r in source:groups.setdefault(r["group_id"],[]).append(r)
  out=[]
  for g,rr in sorted(groups.items()):
   if len(out)+len(rr)<=cap:out.extend(rr)
  rows["train" if split=="train" else "dev"]=out
 # Reconstruct cleaned v1.1 locally, keeping its original test partition.
 import subprocess,sys
 outdir=RUN/"cleaned_v1_1"
 subprocess.run([sys.executable,str(ROOT/"datasets/csts-jep-revision-v1-1/reconstruct.py"),"--source",str(RUN.parent/"color-clustering/source"),"--output",str(outdir)],check=True,capture_output=True)
 source=json.loads((outdir/"test.json").read_text());groups={}
 for r in source:groups.setdefault(r["group_id"],[]).append(r)
 out=[]
 for g,rr in sorted(groups.items()):
  if len(out)+len(rr)<=128:out.extend(rr)
 rows["test"]=out
 for name,rs in rows.items():save(RUN/("cleaned_"+name+".json"),rs)
 cs=[{r[k].strip().lower() for r in rs for k in ["sentence1","sentence2"]} for rs in rows.values()]
 assert not any(cs[i]&cs[j] for i in range(3) for j in range(i))
 cases=[]
 for fi,t in enumerate(DOMAINS):
  domain,story,*clauses=t
  for bits in itertools.product(range(2),repeat=3):
   evidence=[clauses[bits[0]],clauses[2+bits[1]],clauses[4+bits[2]]]
   # Avoid a fixed position for welfare/autonomy/fairness evidence.
   order=[(j+fi)%3 for j in range(3)]
   text=story+" "+" ".join(evidence[j] for j in order)
   cases.append(dict(id=domain+"_"+"".join(map(str,bits)),family=domain,split="dev" if fi<4 else "primary" if fi<16 else "reserve",bits=bits,text=text,evidence=evidence))
 save(RUN/"cases_v2.json",cases);save(RUN/"principles_v2.json",PRINCIPLES)
 design=dict(version=2,created_before_scoring=True,protocol_sha256=digest(PLAN/"protocol.json"),model="Qwen/Qwen3-Embedding-8B",revision="c90816d848505624c2434128dfc61132162a0ee9",adapter_sha256=selection["model_sha256"],adapter_trial=selection["trial_id"],source_revision="925d26ea2040161d3b5847984f705281761de9cd",max_length=160,prompt=selection.get("prompt_template","Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"),principles=PRINCIPLES,assumptions=["Synthetic outcome numbers are expected deaths averted; equal value per life.","All workers are equally responsible and face identical linear disutility per work hour; sixteen work hours total in every case.","Autonomy of the four workers is separate from recipients' outcomes.","Partial resemblance orders under declared interpretations, not complete ethical theories or uniquely determined moral ratings."],methods=["unconditioned adapted Qwen","neutral-condition adapted Qwen","short-condition cosine","defined-condition cosine","paraphrased-definition cosine","situation condition displacement","conditional-minus-neutral pair score","oracle extractive evidence cards","counterfactual response vectors","equal-weight multi-principle kernel"],geometry=dict(features="64-dimensional train-only PCA basis per paired bootstrap seed10,11,12; normalized projected Qwen vectors",objective="mean squared error to cleaned [0,1] targets plus .001*mean((w-1)^2)",intervention="same diagonal bilinear features; signed weights versus nonnegative weights; exact convex ridge/bounded least squares",training_sizes=[64,256],no_test_label_projection=True),limits=dict(max_gpus=1,gpu_seconds=7200,max_recovery_launches=2,deadline="2026-11-10T13:00:00Z"),labels=dict(synthetic="author operational hypotheses",reference="cleaned JEP v1.1 audited LLM-derived labels; not original human groundtruth",human="no new verified conditional human labels"),reference_counts={k:len(v) for k,v in rows.items()},primary="Cross-family conditional retrieval and condition-switch accuracy, paired family bootstrap2000 draws, lexical control",reserve="Four frozen untouched families used for confirmation only of a single method selected on development; all choices logged before reserve evaluation.",leakage="Retain cleaned preexisting partitions. Backbone previously trained on cleaned train; validation/test remain previously examined exploratory reference evidence.",novelty="Conditional embeddings, moral geometry, CASE/SCS contrasts already exist. Test utility and controlled restrictions, no broad novelty/moral-reasoning claim.",references=["https://aclanthology.org/2023.emnlp-main.345/","https://aclanthology.org/2026.eacl-long.231/","https://aclanthology.org/2026.acl-long.50/","https://link.springer.com/article/10.1007/s13164-020-00495-5","https://link.springer.com/article/10.1007/s43681-026-01368-w"])
 save(PLAN/"design_v2.json",design);save(RUN/"design_v2.json",design)
 files=["cleaned_train.json","cleaned_dev.json","cleaned_test.json","cases_v2.json","principles_v2.json","design_v2.json"]
 manifest=dict(files={n:digest(RUN/n) for n in files},source_inputs={"train":selection["training_sha256"],"validation":selection["validation_sha256"],"test_v1_1":digest(outdir/"test.json")},no_caption_overlap=True)
 save(RUN/"frozen_v2.json",manifest);return manifest
if __name__=="__main__":print(json.dumps(build(),indent=2))
