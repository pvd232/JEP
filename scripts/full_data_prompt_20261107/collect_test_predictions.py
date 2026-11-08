"""Collect verified native test predictions and clean up each finished GPU."""
from pathlib import Path
import concurrent.futures,datetime as dt,hashlib,json,os,shlex,subprocess,sys,time
from google.cloud import storage
from google.auth.compute_engine import Credentials
ROOT=Path(__file__).resolve().parents[2]
OUT=Path("/home/peter_aetherlabs_live/jep-full-data-test-launch-20261108")
sys.path.insert(0,str(ROOT))
from scripts.full_data_prompt_20261107.collect_epochs import controller_environment,describe,cleanup
from csts_pilot.diagnostics import summarize
os.environ.update(controller_environment())
ACCOUNT="767812446290-compute@developer.gserviceaccount.com"
client=storage.Client(project="mantra-477901",credentials=Credentials())
matrix=json.loads((OUT/"payload/matrix.json").read_text())
test=json.loads((OUT/"payload/test.json").read_text())
expected_rows=[r["row_id"] for r in test]
protocol=json.loads((OUT/"payload/protocol.json").read_text())

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def download(reference,path):
 loc=reference["stored_at"]
 assert loc["kind"]=="gcs" and loc["owner"]=="pvd232" and loc["workspace"]=="jep_full_data_prompt_20261107"
 path.parent.mkdir(parents=True,exist_ok=True)
 name=loc["prefix"]+"/"+loc["owner"]+"/"+loc["workspace"]+"/"+loc["revision"]+"/"+loc["path"]
 client.bucket(loc["bucket"]).blob(name).download_to_filename(path)
 assert path.stat().st_size==reference["bytes"] and digest(path)==reference["sha256"]

def monitor(worker):
 a=json.loads((OUT/("allocation-eval"+str(worker)+".json")).read_text())["allocation"]
 assigned={s["trial_id"]:s for i,s in enumerate(matrix) if i%2==worker-1}
 deadline=time.monotonic()+6600
 while time.monotonic()<deadline:
  vm=describe(a,ACCOUNT)
  if vm is None or vm["status"]=="TERMINATED":raise RuntimeError("Inference allocation lost; recovery disk retained")
  code="from pathlib import Path;import json;p=Path('/home/machina/jep-full-data-test-20261108/repo/baseline_results/full_data_prompt_test_20261108/worker"+str(worker)+"');s=p/'status.json';c=p/'completion.json';print(json.dumps({'state':json.loads(s.read_text()) if s.exists() else None,'completion':json.loads(c.read_text()) if c.exists() else None}))"
  response=subprocess.run(["gcloud","compute","ssh","machina@"+a["instance_name"],
     "--project=mantra-477901","--zone="+a["zone"],"--account="+ACCOUNT,"--quiet","--tunnel-through-iap",
     "--command=python3 -c "+shlex.quote(code)],text=True,capture_output=True,timeout=90)
  if response.returncode:
   print(json.dumps({"worker":worker,"observation_unavailable":True}),flush=True);time.sleep(20);continue
  obj=json.loads(response.stdout);state=obj["state"]
  if state:
   (OUT/("latest-eval"+str(worker)+".json")).write_text(json.dumps(state,indent=2)+"\n")
   expected_source=json.loads((OUT/"evaluation-source.json").read_text())["source_commit"]
   if state["source_commit"]!=expected_source:time.sleep(10);continue
   print(json.dumps({"worker":worker,"phase":state["phase"],"completed":len(state["records"]),"total":len(assigned)}),flush=True)
   if state["phase"]=="failed_preserved":raise RuntimeError(json.dumps(state["error"]))
  if not obj["completion"]:time.sleep(20);continue
  final=obj["completion"]
  if final["source_commit"]!=expected_source:time.sleep(10);continue
  assert {r["trial_id"] for r in final["records"]}==set(assigned)
  metrics=[];proofs=[]
  for references in final["cloud"]:
   test_keys=[k for k in references if k.endswith("/test/predictions.json")]
   if not test_keys:continue
   key=test_keys[0];trial=key.split("/")[-3];assert trial in assigned
   dest=OUT/"test_predictions"/trial
   for suffix in ["predictions.json","timing.json","resolved.yaml"]:
    ref=references[key.rsplit("/",1)[0]+"/"+suffix];path=dest/suffix
    download(ref,path);proofs.append({"trial":trial,"file":suffix,"reference":ref,"sha256":digest(path),"verified":True})
   predictions=json.loads((dest/"predictions.json").read_text());timing=json.loads((dest/"timing.json").read_text())
   assert [r["row_id"] for r in predictions]==expected_rows
   assert all(float(r["target"])==float(t["target"]) for r,t in zip(predictions,test,strict=True))
   assert timing["model_sha256"]==assigned[trial]["model_sha256"] and timing["test_sha256"]==protocol["splits"]["test"]["sha256"]
   metrics.append({"trial_id":trial,"arm":assigned[trial]["arm"],"seed":assigned[trial]["seed"],
                   "validation":assigned[trial]["validation_metrics"],"test":summarize(predictions),
                   "selected_epoch":assigned[trial]["selected_epoch"],"completed_epochs":assigned[trial]["completed_epochs"],
                   "scoring_seconds":timing["scoring_including_model_load_seconds"]})
  assert len(metrics)==len(assigned)
  result={"worker":worker,"metrics":metrics,"cloud_proofs":proofs,"native_completion":final}
  (OUT/("results-eval"+str(worker)+".json")).write_text(json.dumps(result,indent=2)+"\n")
  receipt=cleanup(a,ACCOUNT,True,True);(OUT/("cleanup-eval"+str(worker)+".json")).write_text(json.dumps(receipt,indent=2)+"\n")
  print(json.dumps({"worker":worker,"test_scores":{m["trial_id"]:m["test"]["spearman"] for m in metrics},"cleanup":receipt}),flush=True)
  return result
 raise TimeoutError("Inference collection deadline; keep recovery disk")

while not (OUT/"evaluation-source.json").exists() or not all((OUT/("started-eval"+str(w)+".json")).exists() for w in [1,2]):time.sleep(10)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 results=list(pool.map(monitor,[1,2]))
(OUT/"test-evaluation-complete.json").write_text(json.dumps({"completed_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"workers":results},indent=2)+"\n")
print(json.dumps({"all_15_test_scores_verified":True}),flush=True)
