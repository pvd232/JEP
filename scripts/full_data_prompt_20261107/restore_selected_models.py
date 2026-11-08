"""Restore only the frozen adapter bytes from already verified VIPER archives."""
from pathlib import Path
import concurrent.futures,hashlib,json,tarfile,datetime as dt
from google.cloud import storage
from google.auth.compute_engine import Credentials

ROOT=Path("/home/peter_aetherlabs_live/jep-worktrees/full-data-test-20261108")
OUT=Path("/home/peter_aetherlabs_live/jep-full-data-test-launch-20261108")
DATA=OUT/"payload";(DATA/"models").mkdir(parents=True,exist_ok=True)
frozen=json.loads((ROOT/"training_outputs/full_data_prompt_20261108/frozen-selections.json").read_text())
selections=frozen["selections"]
import sys
sys.path.insert(0,str(ROOT))
from csts_pilot.full_data_prompt_protocol import require_complete_selections,digest_object
protocol=json.loads((ROOT/"configs/csts-full-data-prompt-20261107.json").read_text())
require_complete_selections(protocol,selections)
matrix=DATA/"matrix.json";matrix.write_text(json.dumps(selections,indent=2)+"\n")
(DATA/"holdout.json").write_text(json.dumps(list(range(protocol["splits"]["test"]["rows"])))+"\n")
(DATA/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
client=storage.Client(project="mantra-477901",credentials=Credentials())
inventory=json.loads((ROOT/"training_outputs/full_data_prompt_20261108/cloud-archive-inventory.json").read_text())

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as stream:
  for block in iter(lambda:stream.read(4*1024*1024),b""):h.update(block)
 return h.hexdigest()

def restore(selected):
 trial=selected["trial_id"];target=DATA/"models"/(trial+".pt")
 if target.exists():assert digest(target)==selected["model_sha256"];return trial
 generation=trial+"_epoch"+str(selected["completed_epochs"]).zfill(2)
 candidates=[p for p in inventory if p["generation"]==generation]
 assert len(candidates)==1 and candidates[0]["controller_verified"]
 proof=candidates[0];uri=proof["uri"];bucket,name=uri[5:].split("/",1)
 found=False
 with client.bucket(bucket).blob(name).open("rb") as raw,tarfile.open(fileobj=raw,mode="r|") as archive:
  for member in archive:
   if not member.isfile() or not member.name.endswith("/model.pt"):continue
   temp=target.with_suffix(".partial");h=hashlib.sha256()
   with archive.extractfile(member) as stream,temp.open("wb") as output:
    for block in iter(lambda:stream.read(4*1024*1024),b""):h.update(block);output.write(block)
   if h.hexdigest()==selected["model_sha256"]:
    temp.replace(target);found=True;break
   temp.unlink()
 assert found,"No frozen model bytes found for "+trial
 selection={"status":"checkpoints_frozen","test_scores_used_for_selection":False,
            "candidates":{"lora":{"sha256":selected["model_sha256"],"trial_id":trial}},
            "frozen_matrix_sha256":digest(matrix)}
 (DATA/(trial+"-selection.json")).write_text(json.dumps(selection,indent=2)+"\n")
 print(json.dumps({"restored":trial,"model_sha256":selected["model_sha256"]}),flush=True)
 return trial

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(restore,selections))
inputs=json.loads((ROOT/"training_outputs/full_data_prompt_20261108/input-cloud-proofs.json").read_text())
for spec in inputs:
 bucket,name=spec["uri"][5:].split("/",1);target=DATA/Path(spec["path"]).name
 client.bucket(bucket).blob(name).download_to_filename(target)
 assert digest(target)==spec["sha256"]
release={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),"source_matrix_commit":"7143baea2cd9193111bdfcb4c7b50000dffdf77a",
         "protocol_sha256":digest_object(protocol),"matrix_sha256":digest(matrix),
         "models":{s["trial_id"]:s["model_sha256"] for s in selections},"test_scoring_started":False,
         "authorization":"User explicitly requested test and validation results on November 8."}
(DATA/"release.json").write_text(json.dumps(release,indent=2)+"\n")
print(json.dumps({"status":"all_15_frozen_models_restored","payload":str(DATA),"test_scoring_started":False}),flush=True)
