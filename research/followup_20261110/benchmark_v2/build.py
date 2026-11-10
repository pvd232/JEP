"""Author-designed response-attribute diagnostic. No human or normative adequacy labels."""
import hashlib,json,platform,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
TOKENIZER=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110/qwen-tokenizer")
# Exact incident clauses; voice variation preserves explicit actor/patient and all supplied facts.
FAMILIES=[
("market","livelihood","Soldiers barred the farmers from the market. The farmers lost sales income.","The farmers were barred from the market by soldiers. Sales income was lost by the farmers.","the farmers","livelihood grants","market access"),
("tools","livelihood","An armed unit seized the mechanic's tools. The mechanic lost repair earnings.","The mechanic's tools were seized by an armed unit. Repair earnings were lost by the mechanic.","the mechanic","replacement work tools","safe access to the workshop"),
("checkpoint","liberty","Guards confined the driver for three days. The driver could not leave.","The driver was confined for three days by guards. Leaving was impossible for the driver.","the driver","release from confinement","unimpeded future travel"),
("abduction","liberty","Fighters abducted the nurse. The fighters prevented the nurse from returning home.","The nurse was abducted by fighters. Returning home was prevented by the fighters.","the nurse","safe return home","protection against renewed abduction"),
("threatened_home","displacement","A patrol threatened the household. The household fled its home.","The household was threatened by a patrol. The household fled its home.","the household","housing access in a safe location","protection against renewed threats"),
("burned_home","displacement","An armed group burned the family's house. The family moved to another town.","The family's house was burned by an armed group. The family moved to another town.","the family","replacement housing","protection against renewed house attacks"),
("missing_son","fate","Soldiers took away the son. The parents did not know whether their son was alive.","The son was taken away by soldiers. Whether their son was alive was unknown to the parents.","the parents","a verified report of their son's fate","safeguards against information concealment"),
("withheld_fate","fate","Officials withheld the detained woman's whereabouts. The children did not know whether she survived.","The detained woman's whereabouts were withheld by officials. Whether she survived was unknown to the children.","the children","a verified report of their mother's whereabouts","safeguards against information concealment"),
("sacred_site","cultural","An armed group destroyed the community's ceremonial site. The community stopped rituals there.","The community's ceremonial site was destroyed by an armed group. The community stopped rituals there.","the community","access to a rebuilt ceremonial site","protection of ceremonial sites"),
("language","cultural","A commander prohibited the elders from teaching the community language. The children stopped receiving those lessons.","The elders were prohibited from teaching the community language by a commander. Those lessons were no longer received by the children.","the children","resumed community-language lessons","protection for community-language teaching"),
("assault","bodily","An officer beat the worker and broke the worker's leg. The worker had pain for months.","The worker was beaten by an officer and the worker's leg was broken. Pain was experienced by the worker for months.","the worker","medical rehabilitation sessions","protection against renewed assault"),
("mine","bodily","Fighters placed a mine. The mine injured the civilian. The civilian needed assistance to walk.","A mine was placed by fighters. The civilian was injured by the mine. Assistance was needed by the civilian to walk.","the civilian","mobility assistance equipment","clearance of remaining mines")]
CRITERIA={
"completed_typed_response":"Retrieve an account explicitly stating that the named affected party received the specified response as completed. Match beneficiary, response type and completion; do not judge sufficiency.",
"acknowledgment_voice":"Retrieve an account explicitly stating that the named affected party spoke and their account was acknowledged. Completion of material support alone does not meet this criterion."}
candidates=[];queries=[];relevant_sets=[];pairs=[]
for i,(fid,kind,base,para,victim,need,prevention) in enumerate(FAMILIES):
 split="dev" if i%2==0 else "test"
 texts={
 "completed":f"A helpful support program delivered {need} to {victim}. The specified delivery was completed. No speaking session is recorded.",
 "proposed":f"A helpful support program proposed {need} for {victim}. Delivery is planned for next year and has not begun. No speaking session is recorded.",
 "other_beneficiary":f"A helpful support program delivered {need} to another affected party, not {victim}. Delivery was completed. No speaking session is recorded.",
 "voice":f"At a supportive public session, {victim} spoke about the incident and the account was acknowledged. The session did not deliver {need}.",
 "sanction":f"A lawful accountability process imposed a sanction on the responsible actors. The process did not deliver {need} to {victim} or give them a speaking session.",
 "nonrepetition":f"A protective program completed {prevention} for {victim}. No delivery of {need} and no speaking session are recorded.",
 "completion_unknown":f"A helpful support program approved {need} for {victim}. The available record does not establish whether delivery occurred. No speaking session is recorded."}
 pool=[]
 for typ,text in texts.items():
  cid=fid+"_"+typ;pool.append(cid)
  candidates.append(dict(id=cid,family=fid,split=split,text=text,response_class=typ,beneficiary=victim if typ!="other_beneficiary" else "another affected party",
   completion_status={"completed":"asserted_complete","proposed":"asserted_not_started","other_beneficiary":"asserted_complete","voice":"asserted_session_complete","sanction":"asserted_sanction","nonrepetition":"asserted_prevention_complete","completion_unknown":"not_established"}[typ],
   label_source="author_synthetic_attribute_expectation_not_human_gold",
   adequacy="not_evaluated"))
 for variant,context in [("base",base),("retained_agent_passive",para)]:
  qids=[]
  for crit,instruction in CRITERIA.items():
   qid=fid+"_"+variant+"_"+crit;qids.append(qid)
   query=f"{context} Named affected party: {victim}. Specified response: {need}."
   rel=fid+("_completed" if crit=="completed_typed_response" else "_voice")
   queries.append(dict(id=qid,family=fid,split=split,variant=variant,kind=kind,source_incident_status="asserted_in_hypothetical",source_completion_inference="not_inferred_from_incident",context=context,affected_party=victim,specified_response=need,criterion_id=crit,condition=instruction,text=query,candidate_ids=pool))
   relevant_sets.append(dict(query_id=qid,relevant_candidate_ids=[rel],label_source="author_synthetic_attribute_expectation_not_human_gold",rationale="Explicit asserted beneficiary/status/type match only; no moral rightness or adequate reparation claim."))
  pairs.append(dict(id=fid+"_"+variant,query_ids=qids,expected_top_ids=[fid+"_completed",fid+"_voice"],relation="criterion_switch_top_rank_reversal"))
# Contract: independent relevance from explicit statuses, no injury/confinement relabeling.
assert len(FAMILIES)==12 and len(candidates)==84 and len(queries)==48
assert len({r["id"] for r in candidates})==84 and len({r["id"] for r in queries})==48
for p in pairs:
 a,b=[next(q for q in queries if q["id"]==qid) for qid in p["query_ids"]]
 assert a["context"]==b["context"] and a["text"]==b["text"] and a["candidate_ids"]==b["candidate_ids"]
for fid,*_ in FAMILIES:
 qs=[q for q in queries if q["family"]==fid]
 cs=[c for c in candidates if c["family"]==fid]
 assert len({q["split"] for q in qs}|{c["split"] for c in cs})==1
 assert len({q["candidate_ids"][0] for q in qs})==1
 assert all(c["adequacy"]=="not_evaluated" for c in cs)
 assert next(c for c in cs if c["response_class"]=="completed")["completion_status"]=="asserted_complete"
 assert next(c for c in cs if c["response_class"]=="completion_unknown")["completion_status"]=="not_established"
 assert next(c for c in cs if c["response_class"]=="proposed")["completion_status"]=="asserted_not_started"
 assert next(c for c in cs if c["response_class"]=="other_beneficiary")["beneficiary"]=="another affected party"
# Tokenize CPU with exact Qwen tokenizer, never silently truncate.
from transformers import AutoTokenizer
snapshot=TOKENIZER/"models--Qwen--Qwen3-Embedding-8B"/"snapshots"/"c90816d848505624c2434128dfc61132162a0ee9"
tok=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True)
for r in queries+candidates:
 r["qwen_tokens"]=max(len(tok.encode("Instruct: Represent the passage for semantic similarity with respect to this condition: "+condition+"\nQuery: "+r["text"],add_special_tokens=True))+1 for condition in CRITERIA.values())
assert max(r["qwen_tokens"] for r in queries+candidates)<=160
# Fit lexical vocabulary on dev text only; evaluate test with fixed feature mapping.
from sklearn.feature_extraction.text import TfidfVectorizer
dev=[r["text"] for r in queries+candidates if r["split"]=="dev"]
vec=TfidfVectorizer(ngram_range=(1,2)).fit(dev)
Q=vec.transform([q["text"] for q in queries]);C=vec.transform([c["text"] for c in candidates])
byid={c["id"]:j for j,c in enumerate(candidates)};rels={r["query_id"]:r["relevant_candidate_ids"] for r in relevant_sets}
pred=[]
for n,q in enumerate(queries):
 scores=[(cid,float((Q[n]@C[byid[cid]].T).toarray()[0,0])) for cid in q["candidate_ids"]]
 scores.sort(key=lambda x:(-x[1],x[0]))
 rank=next(i+1 for i,(cid,s) in enumerate(scores) if cid in rels[q["id"]])
 pred.append(dict(query_id=q["id"],split=q["split"],top_id=scores[0][0],reciprocal_rank=1/rank,ranking=scores))
dataset=dict(schema_version="2.0",provenance="Wholly authored hypothetical diagnostic; no human labels or real JEP excerpts.",claim_scope="Asserted beneficiary, completion status and typed response retrieval only. No normative adequacy, moral reasoning or ethical theory claim.",language="English",families=[dict(id=f[0],kind=f[1],split="dev" if i%2==0 else "test") for i,f in enumerate(FAMILIES)],criteria=CRITERIA,queries=queries,candidates=candidates,relevant_sets=relevant_sets,criterion_switch_pairs=pairs,
 exclusions=["No claim sanction/voice/nonrepetition has lower moral worth.","No claim listed support is sufficient or culturally appropriate.","Source incident facts remain asserted in every variant; unknown applies only to candidate response completion.","Passive variants are author-reviewed proposals, not independently human-validated."],
 invariants=["Same fixed candidate pool under both criteria.","All descendants in source-family split.","Known injury and confinement remain asserted.","Unknown response completion is separate from known noncompletion.","Only typed response completion vs explicit acknowledged voice determines relevance."])
payload=json.dumps(dataset,indent=2)+"\n";(OUT/"dataset.json").write_text(payload)
(OUT/"lexical_screen.json").write_text(json.dumps(dict(method="dev-fit TF-IDF word unigrams+bigrams",predictions=pred,summary={s:dict(n=len(z:=[p for p in pred if p["split"]==s]),mrr=sum(p["reciprocal_rank"] for p in z)/len(z),top1=sum(p["reciprocal_rank"]==1 for p in z)/len(z)) for s in ["dev","test"]}),indent=2)+"\n")
execution=dict(status="CPU_built_checked_and_lexical_screen_executed",utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),families=12,queries=48,candidates=84,criteria=2,switch_pairs=24,tokenizer_path=str(snapshot),scaffold="Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}",eod_tokens=1,max_query_tokens=max(q["qwen_tokens"] for q in queries),max_candidate_tokens=max(c["qwen_tokens"] for c in candidates),token_limit=160,truncated=False,checks_passed=["unique_ids","same_fixed_pool_under_switch","family_disjoint_split","status_adequacy_provenance","token_length_without_truncation"],dataset_sha256=hashlib.sha256(payload.encode()).hexdigest(),no_gpu=True,no_training=True,independent_human_labels=False,review_status="Root independent audit required before frozen inference",python=sys.version.split()[0])
(OUT/"execution.json").write_text(json.dumps(execution,indent=2)+"\n")
print(json.dumps(execution))
