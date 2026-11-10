"""Own one bounded GPU, retain returned bytes, close out locally, and clean owned resources."""
import argparse,base64,datetime as dt,fcntl,gzip,hashlib,json,os,subprocess,sys,tarfile,time,urllib.error,urllib.parse,urllib.request,uuid
from pathlib import Path
import capacity_advisor
ROOT=Path("/home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110")
RUN=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-followup-20261110")
PROJECT="mantra-477901";BUCKET="mantra-mlfg-prod-uscentral1-8e7a";NAME="jep-moral-followup-20261110-g1";LABEL="jep-moral-followup-20261110"
HERE=Path(__file__).resolve().parent
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def deadline_epoch():return dt.datetime.fromisoformat(json.loads((RUN/"design_v2.json").read_text())["deadline_utc"].replace("Z","+00:00")).timestamp()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(".tmp")
 with t.open("w") as f:json.dump(x,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
 t.replace(p)
def event(kind,**kw):
 with (RUN/"events.jsonl").open("a") as f:f.write(json.dumps(dict(at=now(),event=kind,**kw))+"\n")
def update(**kw):
 s=json.loads((RUN/"state.json").read_text());s.update(kw,updated_at=now());save(RUN/"state.json",s)
def token():
 q=urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",headers={"Metadata-Flavor":"Google"})
 return json.load(urllib.request.urlopen(q,timeout=10))["access_token"]
def request(url,method="GET",body=None,absent=False,timeout=60):
 data=None if body is None else json.dumps(body).encode()
 q=urllib.request.Request(url,data=data,method=method,headers={"Authorization":"Bearer "+token(),"Content-Type":"application/json"})
 try:
  with urllib.request.urlopen(q,timeout=timeout) as f:return json.load(f)
 except urllib.error.HTTPError as e:
  text=e.read().decode()
  if absent and e.code==404:return None
  raise RuntimeError(str(e.code)+" "+url+" "+text[:1800]) from e
def compute(path,**kw):return request("https://compute.googleapis.com/compute/v1/projects/"+PROJECT+("/"+path if path else ""),**kw)
def waitop(op):
 end=time.monotonic()+180
 while op.get("status")!="DONE":
  if time.monotonic()>end:raise RuntimeError("Operation status unknown; no reallocation: "+op["name"])
  time.sleep(3);op=request(op["selfLink"])
 return op
def resourcefile():return RUN/"resources.json"
def ledger():return json.loads(resourcefile().read_text()) if resourcefile().exists() else dict(project=PROJECT,intents=[],allocations=[],gpu_seconds=0)
def owned(instance,record):
 if instance["name"]!=NAME or instance.get("labels",{}).get("task")!=LABEL:raise RuntimeError("Resource ownership mismatch")
 if record.get("id") and str(instance["id"])!=str(record["id"]):raise RuntimeError("Immutable VM identity mismatch")
def cleanup(record):
 # Cleanup never deletes preexisting resources or sole unretained result bytes.
 zone=record["zone"];live=compute("zones/"+zone+"/instances/"+NAME,absent=True)
 if live:
  owned(live,record);op=compute("zones/"+zone+"/instances/"+NAME,method="DELETE")
  terminal=waitop(op)
  if terminal.get("error"):raise RuntimeError("Delete failed "+json.dumps(terminal["error"]))
 disk=compute("zones/"+zone+"/disks/"+NAME,absent=True)
 if disk:
  if disk.get("users"):raise RuntimeError("Owned disk remains attached")
  if record.get("disk_id") and str(disk["id"])!=str(record["disk_id"]):raise RuntimeError("Disk identity changed")
  # Name was verified absent before this task's create and journaled before mutation.
  op=compute("zones/"+zone+"/disks/"+NAME,method="DELETE");terminal=waitop(op)
  if terminal.get("error"):raise RuntimeError("Disk deletion failed")
 assert compute("zones/"+zone+"/instances/"+NAME,absent=True) is None
 assert compute("zones/"+zone+"/disks/"+NAME,absent=True) is None
 record["cleanup_verified_at"]=now();record["deleted"]=True
 j=ledger()
 record["gpu_seconds"]=max(record.get("gpu_seconds",0),int(time.time()-record.get("created_epoch",time.time())))
 for old in j["allocations"]:
  if old.get("id")==record.get("id"):old.update(record)
 j["gpu_seconds"]=sum(r.get("gpu_seconds",0) for r in j["allocations"])
 save(resourcefile(),j)
 save(RUN/"cleanup.json",dict(complete=True,verified_at=now(),resources=j,no_task_static_ips_reservations_snapshots_created=True,existing_dev_preserved=True))
def startup(payload):
 encoded=base64.b64encode(gzip.compress(json.dumps(payload).encode())).decode()
 parts=[encoded[i:i+150000] for i in range(0,len(encoded),150000)]
 worker=base64.b64encode((HERE/"gpu_worker.py").read_bytes()).decode()
 advisor=base64.b64encode((HERE/"capacity_advisor.py").read_bytes()).decode()
 script="""#!/bin/bash
set -euo pipefail
mkdir -p /var/lib/jep-moral-pilot
exec > >(tee -a /var/lib/jep-moral-pilot/startup.log /dev/ttyS0) 2>&1
echo MORAL_BOOT
/usr/bin/python3 - <<'BOOT'
import base64,gzip,urllib.request,hashlib
from pathlib import Path
r=Path('/var/lib/jep-moral-pilot')
base='http://metadata.google.internal/computeMetadata/v1/instance/attributes/'
parts=[]
for i in range("""+str(len(parts))+"""):
 q=urllib.request.Request(base+'moral-payload-'+str(i),headers={'Metadata-Flavor':'Google'})
 parts.append(urllib.request.urlopen(q,timeout=10).read())
raw=gzip.decompress(base64.b64decode(b''.join(parts)))
assert hashlib.sha256(raw).hexdigest()=='"""+hashlib.sha256(json.dumps(payload).encode()).hexdigest()+"""'
(r/'payload.json').write_bytes(raw)
(r/'worker.py').write_bytes(base64.b64decode('"""+worker+"""'))
(r/'capacity_advisor.py').write_bytes(base64.b64decode('"""+advisor+"""'))
BOOT
/usr/bin/python3 -m pip install 'transformers==4.57.1' 'peft==0.17.1' 'jinja2>=3.1.0' accelerate requests > /var/lib/jep-moral-pilot/install.log 2>&1
/usr/bin/python3 -m pip freeze > /var/lib/jep-moral-pilot/environment.txt
nvidia-smi
/usr/bin/python3 -u /var/lib/jep-moral-pilot/worker.py
echo MORAL_WORKER_EXIT
"""
 items=[dict(key="startup-script",value=script),dict(key="install-nvidia-driver",value="True")]+[dict(key="moral-payload-"+str(i),value=p) for i,p in enumerate(parts)]
 assert max(len(x["value"].encode()) for x in items)<262144
 assert sum(len(x["value"].encode())+len(x["key"]) for x in items)<512000
 return items
def capacity_plan(output,machine_type=capacity_advisor.MACHINE_TYPE):
 """Persist fresh advisory inputs and the exact score used for placement."""
 plan=capacity_advisor.build_plan(compute,request,PROJECT,machine_type=machine_type)
 plan["source_sha256"]=dict(controller=sha(__file__),advisor=sha(HERE/"capacity_advisor.py"))
 save(output,plan)
 return plan

def admission_limits(j,search_admitted=False):
 """Keep closed runs, consumed admissions, deadlines and GPU budgets sealed."""
 state=json.loads((RUN/"state.json").read_text());design=json.loads((RUN/"design_v2.json").read_text())
 if state.get("phase","").startswith("closed") or state.get("phase")=="complete":raise RuntimeError("Run is closed; preserve retained outputs")
 if state.get("final_admission_consumed") and not search_admitted:raise RuntimeError("This recovery admission is already consumed")
 if state.get("recovery_launches",0)>min(design["max_recovery_launches"],2):raise RuntimeError("Recovery launch budget exhausted")
 if design["max_gpus"]!=1:raise RuntimeError("Expected a single-GPU design")
 deadline=dt.datetime.fromisoformat(design["deadline_utc"].replace("Z","+00:00")).timestamp()
 seconds=min(2700,design["max_gpu_seconds"])-j.get("gpu_seconds",0)
 seconds=min(seconds,int(deadline-time.time()))
 if seconds<=0:raise RuntimeError("Compute deadline or GPU-time budget reached")
 return seconds

def reconcile_jobs(state):
 """Reconcile durable controller statuses before an allocation mutation."""
 jobs=json.loads(subprocess.check_output(["cloud-project","--project","jep","list"],text=True))
 ids={x["id"] for x in state.get("jobs",[]) if x.get("id")}
 ids.update(x["id"] for x in jobs if x.get("cwd")==str(ROOT) and x.get("checkpoint")==str(RUN))
 for job_id in sorted(ids):
  listed=next((x for x in jobs if x["id"]==job_id),None)
  if listed is not None and (not any(Path(a).name=="controller.py" for a in listed.get("argv",[])) or "--plan-only" in listed.get("argv",[])):continue
  actual=json.loads(subprocess.check_output(["cloud-project","--project","jep","status",job_id],text=True))
  argv=actual.get("argv",[])
  if not any(Path(a).name=="controller.py" for a in argv) or "--plan-only" in argv:continue
  if listed is None or listed.get("status")!=actual.get("status"):raise RuntimeError("Durable job status unresolved: "+job_id)
  if actual.get("status") in {"succeeded","failed","cancelled","canceled","interrupted"}:continue
  if actual.get("status")=="running" and actual.get("child_pid")==os.getpid():continue
  raise RuntimeError("Another controller is active or unresolved: "+job_id)

def allocate(payload,machine_type=capacity_advisor.MACHINE_TYPE):
 """Try eligible L4 Spot placements in descending probability-times-uptime order."""
 j=ledger()
 for record in j.get("allocations",[]):
  if not record.get("deleted"):return record
 admission_limits(j)
 reconcile_jobs(json.loads((RUN/"state.json").read_text()))
 if any(i["status"] not in {"reconciled_absent","terminal_failed","allocated"} for i in j["intents"]):raise RuntimeError("Prior create intent requires reconciliation")
 for zone in {i["zone"] for i in j["intents"]}:
  if compute("zones/"+zone+"/instances/"+NAME,absent=True) or compute("zones/"+zone+"/disks/"+NAME,absent=True):raise RuntimeError("Prior allocation resources require reconciliation")
 attempted=set();plan=None;search_admitted=False
 for attempt in range(capacity_advisor.MAX_ATTEMPTS):
  seconds=admission_limits(j,search_admitted)
  if plan is None or time.time()-plan["started_at_epoch"]>=capacity_advisor.ADVICE_TTL_SECONDS:
   plan=capacity_plan(RUN/"capacity_advice"/("plan_"+str(time.time_ns())+".json"),machine_type)
  choices=[x for x in plan["ranked"] if x["eligible"] and x["zone"] not in attempted]
  if not choices:raise RuntimeError("Ranked eligible placements exhausted; inspect retained capacity plan")
  candidate=choices[0]
  if time.time()-candidate["checked_at_epoch"]>=capacity_advisor.ADVICE_TTL_SECONDS:
   plan=None;continue
  zone=candidate["zone"];attempted.add(zone)
  if compute("zones/"+zone+"/instances/"+NAME,absent=True) or compute("zones/"+zone+"/disks/"+NAME,absent=True):raise RuntimeError("Candidate contains surviving resources")
  seconds=admission_limits(j,search_admitted)
  intent=dict(name=NAME,zone=zone,absent_before_create=True,at=now(),status="requesting",placement=candidate)
  j["intents"].append(intent);save(resourcefile(),j)
  admission=json.loads((RUN/"state.json").read_text());admission["final_admission_consumed"]=True;save(RUN/"state.json",admission)
  search_admitted=True
  worker_payload=dict(payload,allocation_machine_type=machine_type,lease_deadline_utc=dt.datetime.fromtimestamp(time.time()+max(1,seconds-60),dt.timezone.utc).isoformat())
  body=dict(name=NAME,machineType="zones/"+zone+"/machineTypes/"+machine_type,
   labels=dict(task=LABEL,owner="pvd232",experiment="moral-v2"),
   disks=[dict(boot=True,autoDelete=True,initializeParams=dict(diskName=NAME,diskSizeGb="120",diskType="zones/"+zone+"/diskTypes/pd-balanced",sourceImage="projects/deeplearning-platform-release/global/images/pytorch-2-9-cu129-ubuntu-2204-nvidia-580-v20261029"))],
   networkInterfaces=[candidate["network_interface"]],
   serviceAccounts=[dict(email="jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com",scopes=["https://www.googleapis.com/auth/cloud-platform"])],
   scheduling=dict(provisioningModel="SPOT",automaticRestart=False,onHostMaintenance="TERMINATE",instanceTerminationAction="STOP",maxRunDuration=dict(seconds=str(seconds))),
   metadata=dict(items=startup(worker_payload)))
  save(RUN/"allocation_request.json",dict(zone=zone,request={k:v for k,v in body.items() if k!="metadata"},placement=candidate,startup_sha256=hashlib.sha256(body["metadata"]["items"][0]["value"].encode()).hexdigest()))
  try:
   op=compute("zones/"+zone+"/instances?requestId="+str(uuid.uuid4()),method="POST",body=body)
   intent["operation"]=op["selfLink"];save(resourcefile(),j)
   terminal=waitop(op)
  except Exception as error:
   intent.update(status="unknown_or_denied",error=repr(error));save(resourcefile(),j)
   raise
  if terminal.get("error"):
   intent.update(status="terminal_failed",error=terminal["error"]);save(resourcefile(),j)
   live=compute("zones/"+zone+"/instances/"+NAME,absent=True);disk=compute("zones/"+zone+"/disks/"+NAME,absent=True)
   if live or disk:raise RuntimeError("Partial allocation resources retained; reconcile before fallback")
   codes={e.get("code") for e in terminal["error"].get("errors",[])}
   if not any("RESOURCE_POOL_EXHAUSTED" in (code or "") for code in codes):raise RuntimeError(json.dumps(terminal["error"]))
   continue
  live=compute("zones/"+zone+"/instances/"+NAME);owned(live,{})
  disk=compute("zones/"+zone+"/disks/"+NAME)
  record=dict(name=NAME,id=str(live["id"]),zone=zone,disk_id=str(disk["id"]),created_epoch=dt.datetime.fromisoformat(intent["at"]).timestamp(),created_epoch_source="allocation_request_time_conservative",created_at=now(),labels=live["labels"],gpu_count=1,provider_max_seconds=seconds,placement=candidate,capacity_advisor_sha256=sha(HERE/"capacity_advisor.py"))
  j["allocations"].append(record);intent["status"]="allocated";save(resourcefile(),j)
  return record
 raise RuntimeError("Bounded ranked Spot placement attempts exhausted")

def collect(payload):
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

def prepare_host_memory_fallback(record):
 """Authorize one larger-host retry from a verified, cleaned-up preflight failure."""
 result=json.loads((RUN/"gpu_return"/"compute.json").read_text())
 if result.get("status")!="failed" or result.get("failure_code")!="HOST_MEMORY_PREFLIGHT_FAILED":return False
 if record.get("placement",{}).get("machine_type")!=capacity_advisor.MACHINE_TYPE:return False
 memory=json.loads((RUN/"gpu_return"/"host_memory_preflight.json").read_text())
 if memory.get("passed") is not False or memory.get("machine_type")!=capacity_advisor.MACHINE_TYPE or memory.get("source_sha256")!=record.get("capacity_advisor_sha256"):raise RuntimeError("Host-memory failure proof mismatch")
 if (RUN/"gpu_return"/"embeddings.npz").exists() or (RUN/"gpu_return"/"shards").exists():raise RuntimeError("Retained inference stages require checkpoint-aware recovery before host replacement")
 state=json.loads((RUN/"state.json").read_text());design=json.loads((RUN/"design_v2.json").read_text())
 if state.get("recovery_launches",0)>=min(design["max_recovery_launches"],2):return False
 try:admission_limits(ledger(),search_admitted=True)
 except RuntimeError:return False
 resources=ledger()
 if any(not x.get("deleted") for x in resources.get("allocations",[])):raise RuntimeError("Clean the failed worker before host-memory fallback")
 if not record.get("deleted") or not record.get("cleanup_verified_at"):raise RuntimeError("Worker cleanup proof required for fallback")
 proof=json.loads((RUN/"collection.json").read_text())
 if sha(RUN/"gpu_return.tar.gz")!=proof["bundle_sha256"]:raise RuntimeError("Retained failure bundle changed")
 if not str(record["id"]).isdigit():raise RuntimeError("Expected immutable numeric VM identity")
 archive=RUN/"attempts"/str(record["id"])
 archive.mkdir(parents=True,exist_ok=False)
 for name in ["gpu_return","gpu_return.tar.gz","collection.json"]:(RUN/name).rename(archive/name)
 save(archive/"host_memory_fallback.json",dict(from_machine=capacity_advisor.MACHINE_TYPE,to_machine=capacity_advisor.HOST_MEMORY_FALLBACK,previous_vm_id=record["id"],failure=result,collection=proof,created_at=now()))
 update(phase="allocating_gpu",allocation_machine_type=capacity_advisor.HOST_MEMORY_FALLBACK,recovery_launches=state.get("recovery_launches",0)+1,generation=state.get("generation",0)+1,final_admission_consumed=False,host_memory_fallback_from=record["id"],host_memory_fallback_archive=str(archive))
 event("host_memory_fallback",previous_vm_id=record["id"],machine_type=capacity_advisor.HOST_MEMORY_FALLBACK)
 return True

def closeout():
 # CPU-only serialization/analysis may run after the compute deadline.
 script=HERE/"analyze.py"
 if script.exists():
  subprocess.run([sys.executable,str(script),"--resume"],cwd=ROOT,check=True)
 else:
  update(phase="inference_retained_analysis_pending",next_action="Run analyze.py on retained embeddings; never repeat inference.")
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--resume",action="store_true");parser.add_argument("--cleanup-only",action="store_true");parser.add_argument("--plan-only",action="store_true");parser.add_argument("--plan-output",type=Path);parser.add_argument("--plan-machine-type",choices=[capacity_advisor.MACHINE_TYPE,capacity_advisor.HOST_MEMORY_FALLBACK],default=capacity_advisor.MACHINE_TYPE);args=parser.parse_args()
 if args.plan_only:
  output=args.plan_output or RUN/"diagnostics"/("capacity_plan_"+str(time.time_ns())+".json")
  plan=capacity_plan(output,args.plan_machine_type);print(json.dumps(dict(path=str(output),ranked=plan["ranked"],unknown_regions=[x["region"] for x in plan["region_reports"] if x["status"]=="unknown"])));return
 with (RUN/"execution.lock").open("a") as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print("Healthy owner holds execution.lock; no duplicate launch.");return
  state=json.loads((RUN/"state.json").read_text())
  if not args.cleanup_only and (state.get("phase","").startswith("closed") or state.get("phase")=="complete"):
   print(json.dumps(dict(phase=state["phase"],action="retained_outputs_preserved")));return
  frozen=json.loads((RUN/"frozen_v2.json").read_text())
  for n,h in frozen["files"].items():assert sha(RUN/n)==h,"Frozen data/config changed"
  if args.cleanup_only:
   if not (RUN/"collection.json").exists():raise RuntimeError("Retain output bytes before cleanup")
   for r in ledger()["allocations"]:
    if not r.get("deleted"):cleanup(r)
   return
  if (RUN/"collection.json").exists():
   for r in ledger()["allocations"]:
    if not r.get("deleted"):cleanup(r)
   closeout();return
  q=json.loads((RUN/"qwen_selection.json").read_text());encoder=json.loads((RUN/"encoder_identity.json").read_text())
  payload=dict(tasks=json.loads((RUN/"tasks.json").read_text()),encoder=encoder,selection=q["selected"],archive=q["archive"],bucket=BUCKET,result_object="moral_geometry_transfer_20261110/"+sha(RUN/"frozen_v2.json")[:16]+"/"+sha(HERE/"gpu_worker.py")[:16]+"/return.tar.gz",worker_sha256=sha(HERE/"gpu_worker.py"))
  payload["met_reasoner"]=None
  payload["capacity_advisor_sha256"]=sha(HERE/"capacity_advisor.py")
  payload["compute_deadline_utc"]=json.loads((RUN/"design_v2.json").read_text())["deadline_utc"]
  payload["extension_cases"]=json.loads((RUN/"extension_cases.json").read_text())
  save(RUN/"payload_identity.json",dict(met_reasoner=payload["met_reasoner"],extension_sha256=sha(RUN/"extension_cases.json"),worker_sha256=payload["worker_sha256"],capacity_advisor_sha256=payload["capacity_advisor_sha256"],compute_deadline_utc=payload["compute_deadline_utc"],encoder=payload["encoder"]))
  save(RUN/"controller_execution.json",dict(argv=sys.argv,python=sys.executable,source_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),worker_sha256=payload["worker_sha256"],frozen_sha256=sha(RUN/"frozen_v2.json"),started_at=now(),owner_pid=os.getpid(),unknown_hosted_run_id=None))
  update(phase="allocating_gpu",stage="Qwen_v2_inference",owner_pid=os.getpid(),owner_relinquished=False,active_design_sha256=sha(RUN/"design_v2.json"),next_action="Inspect this durable controller and resource ledger; no duplicate allocation.")
  if time.time()>=deadline_epoch():
   if collect(payload):
    for owned_record in ledger()["allocations"]:
     if not owned_record.get("deleted"):cleanup(owned_record)
   else:update(phase="deadline_preservation_pending",next_action="No new compute. Retain existing owned disk and recover terminal outputs before cleanup.")
   if (RUN/"collection.json").exists():closeout()
   return
  save(RUN/"controller_payload.json",payload)
  if time.time()>=deadline_epoch():
   retained=collect(payload)
   if retained:
    for old in ledger()["allocations"]:
     if not old.get("deleted"):cleanup(old)
   update(phase="deadline_closeout" if retained else "deadline_output_preservation_pending",next_action="No new compute; preserve outputs and reconcile owned cleanup")
   if retained:closeout()
   return
  machine_type=json.loads((RUN/"state.json").read_text()).get("allocation_machine_type",capacity_advisor.MACHINE_TYPE)
  record=allocate(payload,machine_type);update(phase="running",resource_ledger=str(resourcefile()),gpu=record)
  while True:
   if collect(payload):
    update(phase="inference_retained",stage="cleanup");cleanup(record)
    if prepare_host_memory_fallback(record):
     record=allocate(payload,capacity_advisor.HOST_MEMORY_FALLBACK);update(phase="running",gpu=record);continue
    break
   live=compute("zones/"+record["zone"]+"/instances/"+NAME,absent=True)
   if live is None:
    update(phase="interrupted_gpu",next_action="GPU no longer exists and return object absent. Inspect disk/result/serial before a bounded recovery.")
    raise RuntimeError("Worker disappeared without a retained terminal result")
   owned(live,record)
   elapsed=time.time()-record["created_epoch"]
   update(heartbeat=now(),gpu_elapsed_seconds=int(elapsed))
   if elapsed>min(2400,record["provider_max_seconds"]-30) or time.time()>=deadline_epoch():
    # Preserve sole disk bytes on timeout rather than assert successful cleanup.
    raise RuntimeError("GPU envelope nearly exhausted; inspect serial/output immediately; no new compute")
   time.sleep(45)
  closeout()
if __name__=="__main__":
 try:main()
 except Exception as e:
  if "--plan-only" in sys.argv:raise
  event("controller_error",error=repr(e));update(phase="controller_attention",error=repr(e),next_action="Reconcile actual job, resource intents, cloud inventory and surviving locks before any recovery. Preserve compatible stages.")
  raise
