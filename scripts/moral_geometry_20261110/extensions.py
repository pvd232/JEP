"""Predeclared fixed-harm/theory, invariance and restorative-relation screen."""
import hashlib,json
from pathlib import Path
from prepare import RUN,save,digest
from transformers import AutoTokenizer
THEORIES=[
 ("Utilitarianism","Compare harm by expected suffering and loss of life, counting every person's welfare equally."),
 ("Deontology","Compare harm as interference with persons' rights, consent and duties owed to them, not merely aggregate outcomes."),
 ("Care Ethics","Compare harm through vulnerability, dependency and failures of care within the relationships described.")]
REPAIR=[
 ("land","An armed group took a family's farmland and prevented them from earning a living.","The family regains secure access to its farmland and the means to earn a living.","The responsible commander must report weekly to a court."),
 ("home","Fighters destroyed a family's home and forced its members to sleep outdoors.","A safe home is rebuilt for the displaced family with its participation.","The responsible fighter receives a restriction on movement."),
 ("health","An assault left a worker with pain and injuries that prevented ordinary activity.","The injured worker receives continuing treatment and rehabilitation chosen with informed consent.","The perpetrator must serve a custodial sentence."),
 ("school","Threats closed a village school and stopped the children from attending classes.","The village reopens a safe school and restores the children's access to education.","The person who made the threats pays a punitive fine."),
 ("water","A military operation ruined a community's water source and left households without safe drinking water.","The community helps restore a protected source of clean drinking water for its households.","The responsible officer loses military rank."),
 ("truth","A family was left without information about the fate of a disappeared relative.","A search establishes the relative's fate and the family receives truthful information and dignified support.","The responsible official faces a court-imposed travel ban.")]
def main():
 if (RUN/"extension_freeze.json").exists():
  x=json.loads((RUN/"extension_freeze.json").read_text());assert digest(RUN/"extension_cases.json")==x["cases_sha256"];return
 d=json.loads((RUN/"design_v2.json").read_text());tasks=json.loads((RUN/"tasks.json").read_text());lookup={x["key"]:x for x in tasks}
 tokenizer=AutoTokenizer.from_pretrained(d["model"],revision=d["revision"],cache_dir=str(RUN/"qwen-tokenizer"),padding_side="left")
 eod=tokenizer.convert_tokens_to_ids("<|endoftext|>");cases=[]
 def add(text,condition,layers=True):
  prompt=d["prompt"].format(passage=text,condition=condition);key=hashlib.sha256(prompt.encode()).hexdigest()
  tokens=len(tokenizer(prompt,add_special_tokens=False)["input_ids"])+1
  assert tokens<=160,(tokens,prompt)
  if key not in lookup:lookup[key]=dict(key=key,prompt=prompt,tokens=tokens)
  if layers:lookup[key]["layers"]=True
  return key
 for family,harm,repair,sanction in REPAIR:
  for theory,description in THEORIES:
   condition="Moral value: care/harm. Ethical theory: "+theory+". "+description
   # These are supplied frames, not generated reasoning or MET-D training.
   variants=[("harm",harm),("repair",repair),("sanction",sanction),("irrelevant_prefix","An observer recorded this account. "+harm),("irrelevant_suffix",harm+" The account was written on a Tuesday.")]
   for variant,text in variants:
    key=add(text,condition);cases.append(dict(family=family,theory=theory,condition=condition,type=variant,text=text,key=key))
 # Explicit harm→restoration comparisons under four separate restorative concerns.
 for family,harm,repair,sanction in REPAIR:
  for aspect in ["material restitution for the harm described","acknowledgment and truthful information about the harm","restoration of affected people's agency","prevention of repetition of the harm"]:
   for variant,text in [("harm",harm),("repair",repair),("sanction",sanction)]:
    key=add(text,aspect);cases.append(dict(family=family,theory="restorative_aspect",condition=aspect,type=variant,text=text,key=key))
 tasks=sorted(lookup.values(),key=lambda x:x["key"]);save(RUN/"tasks.json",tasks);save(RUN/"extension_cases.json",cases)
 encoder=json.loads((RUN/"encoder_identity.json").read_text());encoder["tasks_sha256"]=digest(RUN/"tasks.json");encoder["layer_probe"]="EOD pooled layers 0,9,18,27,final36; layer0 is null (identical EOD input embedding)"
 save(RUN/"encoder_identity.json",encoder)
 spec=dict(created_before_scoring=True,cases_sha256=digest(RUN/"extension_cases.json"),tasks_sha256=digest(RUN/"tasks.json"),theories=THEORIES,framework="MET-inspired factorial prompting only; no grounds-selection model, rejection sampling or MET-D self-distillation",fixed_value="care/harm",other_dimensions="Reason-based authority; supplied ground only; no generated ethical rationale.",invariants=["Irrelevant narrator prefix/suffix with no changed moral facts. Not claimed to exhaust semantic invariance.","No role-reversal invariance assumed."],restorative_relation="Typed harm→response analogy, not assumed reflection/inverse. Repairs are authored illustrative candidates, not expert-approved sufficient reparation.",layers=[0,9,18,27,36],layer_selection="report entire prespecified curve; final layer primary, no best-test-layer selection",references=["https://github.com/aylee2008/met/tree/130007d875fbb8a19bdebe8091c8925a694849c9","https://aclanthology.org/K19-1085/","https://aclanthology.org/2020.coling-main.300/","https://arxiv.org/abs/2506.05687"],counts=dict(tasks=len(tasks),extension_cases=len(cases),layer_tasks=sum(bool(x.get("layers")) for x in tasks)))
 save(RUN/"extension_freeze.json",spec);save(Path(__file__).resolve().parents[2]/"plans/moral_geometry_20261110/extension.json",spec);print(spec["counts"])
if __name__=="__main__":main()
