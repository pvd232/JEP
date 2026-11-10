"""Restore one validation-frozen Qwen adapter and cleaned data without retraining."""
import fcntl,hashlib,json,subprocess,tarfile,time,urllib.request,urllib.parse
from pathlib import Path
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
W=Path("/home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110")
REF="925d26ea2040161d3b5847984f705281761de9cd"
def atomic(p,x):
 t=p.with_suffix(".tmp");t.write_text(json.dumps(x,indent=2)+"\n");t.replace(p)
def git(p):return json.loads(subprocess.check_output(["git","show",REF+":"+p],cwd=W))
def open_gcs(uri):
 bucket,name=uri[5:].split("/",1)
 token=json.load(urllib.request.urlopen(urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",headers={"Metadata-Flavor":"Google"}),timeout=10))["access_token"]
 url="https://storage.googleapis.com/storage/v1/b/"+bucket+"/o/"+urllib.parse.quote(name,safe="")+"?alt=media"
 return urllib.request.urlopen(urllib.request.Request(url,headers={"Authorization":"Bearer "+token}),timeout=60)
with (R/"execution.lock").open("a") as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 start=time.monotonic()
 frozen=git("training_outputs/full_data_prompt_20261108/frozen-selections.json")
 selected=next(s for s in frozen["selections"] if s["trial_id"]=="A_condition_first_seed10")
 inventory=git("training_outputs/full_data_prompt_20261108/cloud-archive-inventory.json")
 gen=selected["trial_id"]+"_epoch"+str(selected["completed_epochs"]).zfill(2)
 proof=next(x for x in inventory if x["generation"]==gen and x["controller_verified"])
 atomic(R/"qwen_selection.json",dict(source_revision=REF,selected=selected,archive=proof,selection_rule="First predeclared condition-first seed10; selection frozen before this pilot, no moral evaluation used."))
 out=R/"restored";out.mkdir(exist_ok=True)
 target=out/"A_condition_first_seed10.pt"
 if not target.exists():
  with open_gcs(proof["uri"]) as response,tarfile.open(fileobj=response,mode="r|") as tar:
   for member in tar:
    if not member.isfile() or not member.name.endswith("/model.pt"):continue
    h=hashlib.sha256();temp=target.with_suffix(".partial")
    with tar.extractfile(member) as src,temp.open("wb") as dest:
     for block in iter(lambda:src.read(4*1024*1024),b""):h.update(block);dest.write(block)
    if h.hexdigest()==selected["model_sha256"]:temp.replace(target);break
    temp.unlink()
  assert target.exists(),"Selected adapter not found"
 else:assert hashlib.sha256(target.read_bytes()).hexdigest()==selected["model_sha256"]
 for spec in git("training_outputs/full_data_prompt_20261108/input-cloud-proofs.json"):
  name=Path(spec["path"]).name
  if name=="test.json":continue
  target=out/name
  if target.exists():
   assert hashlib.sha256(target.read_bytes()).hexdigest()==spec["sha256"];continue
  with open_gcs(spec["uri"]) as src,target.with_suffix(".partial").open("wb") as dest:
   for block in iter(lambda:src.read(1024*1024),b""):dest.write(block)
  temp=target.with_suffix(".partial");assert hashlib.sha256(temp.read_bytes()).hexdigest()==spec["sha256"];temp.replace(target)
 atomic(R/"restore_receipt.json",dict(status="complete",seconds=time.monotonic()-start,adapter_sha256=selected["model_sha256"],source_revision=REF,training_data="cleaned JEP C-STS, existing frozen train/validation splits",no_training=True))
 print("RESTORED_QWEN_AND_CLEANED_DATA",flush=True)
