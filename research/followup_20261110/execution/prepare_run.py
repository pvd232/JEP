"""Freeze new user-authorized response-attribute follow-up; retain the completed pilot."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path("/home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110")
OLD=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
RUN=OLD.parent/"moral-followup-20261110"
HERE=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+"\n")
data_path=HERE.parent/"benchmark_v2/dataset.json";data=json.loads(data_path.read_text())
assert sha(data_path)=="b292fb89e11473a3a48563fbc52cfb80cddb0fc046c73427a852cc8d99086dc3"
RUN.mkdir(exist_ok=True);shutil.copy2(data_path,RUN/"dataset.json")
prompt="Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
tasks={}
conditions=list(data["criteria"].values())
if not all(isinstance(c,str) for c in conditions):conditions=sorted({q["condition"] for q in data["queries"]})
conditions=list(conditions)+["overall semantic content"]
for row in data["queries"]+data["candidates"]:
 for condition in conditions:
  text=prompt.format(passage=row["text"],condition=condition);key=hashlib.sha256(text.encode()).hexdigest();tasks[key]=dict(key=key,prompt=text)
save(RUN/"tasks.json",sorted(tasks.values(),key=lambda x:x["key"]))
encoder=json.loads((OLD/"encoder_identity.json").read_text());encoder.pop("layer_probe",None);encoder["tasks_sha256"]=sha(RUN/"tasks.json");save(RUN/"encoder_identity.json",encoder)
shutil.copy2(OLD/"qwen_selection.json",RUN/"qwen_selection.json");save(RUN/"extension_cases.json",[])
protocol=dict(version=1,authorization="New follow-up explicitly requested after overnight pilot completed. Not a recovery of the expired pilot.",dataset_sha256=sha(data_path),scope="Directed response-linking/attribute diagnostic; not symmetric moral analogy or normative adequacy.",methods=["fixed-condition Qwen cosine","neutral-condition Qwen cosine","lexical baseline","explicit attribute oracle upper bound"],splits="Original family dev/test; no fitting or selection on test labels.",labels="Author-designed asserted beneficiary/status/type expectations, no human labels.",limitations=["English only","Small structured hypothetical pool","No full theory-sensitive moral validation","Benchmark pilot, not claimed novel method"],deadline_utc="2026-11-10T15:30:00Z",max_gpus=1,max_gpu_seconds=2700,max_recovery_launches=2,original_pilot_gpu_seconds=1440,combined_gpu_seconds_upper_bound=4140,model_runtime="Pinned same new runtime as previous pilot; historical numerical replay limitation retained.")
save(RUN/"design_v2.json",protocol);save(HERE.parent/"FOLLOWUP_PROTOCOL.json",protocol)
save(RUN/"frozen_v2.json",dict(files={n:sha(RUN/n) for n in ["dataset.json","tasks.json","encoder_identity.json","design_v2.json"]}))
if not (RUN/"state.json").exists():save(RUN/"state.json",dict(phase="ready",jobs=[],recovery_launches=0,generation=0,owner_run_id=None))
# Reuse the reviewed runner, adapting only new ownership, deadline and transport.
controller=(ROOT/"scripts/moral_geometry_20261110/controller.py").read_text()
controller=controller.replace(str(OLD),str(RUN)).replace('ROOT=Path(__file__).resolve().parents[2]','ROOT=Path("'+str(ROOT)+'")')
controller=controller.replace('NAME="jep-moral-20261110-g1"','NAME="jep-moral-followup-20261110-g1"').replace('LABEL="jep-moral-geometry-20261110"','LABEL="jep-moral-followup-20261110"')
controller=controller.replace('seconds="7200"','seconds="2700"').replace('provider_max_seconds=7200','provider_max_seconds=2700').replace('elapsed>6900','elapsed>2400').replace('2026-11-10T13:00:00','2026-11-10T15:30:00')
controller=controller.replace('payload["met_reasoner"]=dict(model="launch/MET-D-Qwen3-4B",revision="b463bb8ceed1df7f1550a9c5327cb6d7674e6c68")','payload["met_reasoner"]=None')
a=controller.index('def collect(payload):');b=controller.index('def closeout():')
transport='''def collect(payload):
 if (RUN/"collection.json").exists():return True
 j=ledger()
 if not j["allocations"]:return False
 zone=j["allocations"][-1]["zone"]
 common=["--project="+PROJECT,"--zone="+zone,"--account=dev-vm@pvd-dev-232.iam.gserviceaccount.com","--tunnel-through-iap","--ssh-key-file=/home/pvd2112_columbia_edu/.ssh/google_compute_engine","--quiet"]
 cmd=["gcloud","compute","ssh","machina@"+NAME,*common,"--ssh-flag=-oBatchMode=yes","--ssh-flag=-oConnectTimeout=10","--command=test -f /var/lib/jep-moral-pilot/transfer_ready.json && cat /var/lib/jep-moral-pilot/transfer_ready.json"]
 status=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
 if status.returncode:
  if any(x in status.stderr for x in ["PERMISSION_DENIED","HTTP 403"]):raise RuntimeError(status.stderr[-1000:])
  return False
 if not status.stdout.strip():return False
 ready=json.loads(status.stdout)
 dest=RUN/"gpu_return.tar.gz"
 result=subprocess.run(["gcloud","compute","scp","machina@"+NAME+":/var/lib/jep-moral-pilot/return.tar.gz",str(dest),*common],capture_output=True,text=True,timeout=90)
 if result.returncode:raise RuntimeError(result.stderr[-1000:])
 assert sha(dest)==ready["sha256"]
 folder=RUN/"gpu_return";folder.mkdir(exist_ok=True)
 with tarfile.open(dest) as archive:
  for member in archive.getmembers():assert member.isfile() and (folder/member.name).resolve().is_relative_to(folder.resolve())
  archive.extractall(folder,filter="data")
 manifest=json.loads((folder/"result_manifest.json").read_text())
 for name,proof in manifest.items():assert sha(folder/name)==proof["sha256"]
 assert json.loads((folder/"compute.json").read_text())["encoder"]==payload["encoder"]
 save(RUN/"collection.json",dict(files=manifest,bundle_sha256=sha(dest),transport="existing authenticated IAP",verified_at=now()))
 return True

'''
controller=controller[:a]+transport+controller[b:];(HERE/"controller.py").write_text(controller)
worker=(ROOT/"scripts/moral_geometry_20261110/gpu_worker.py").read_text().replace('if not identity:return []','if not identity:\n  save(R/"reasoning_views.json",dict(status="not_requested",views=[]));return []')
worker=worker.replace('START+6000','START+2100').replace('dt.datetime(2026,11,10,13,tzinfo','dt.datetime(2026,11,10,15,30,tzinfo')
worker=worker.replace('print("LOCAL_RETURN_READY",str(bundle),digest(bundle),flush=True)','save(R/"transfer_ready.json",dict(sha256=digest(bundle),bytes=bundle.stat().st_size))\n  print("LOCAL_RETURN_READY",str(bundle),digest(bundle),flush=True)')
(HERE/"gpu_worker.py").write_text(worker)
print("FOLLOWUP_FROZEN",len(tasks),"contexts",sha(RUN/"frozen_v2.json"))
