"""Separate bounded VIPER publication. Failure never repeats scientific compute."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from viper.cloud import GcsRepository,ViperCloud,ViperCloudDestination
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
ROOT=Path(__file__).resolve().parents[2]
def atomic(value):
 p=R/"publication.json";t=p.with_suffix(".tmp");t.write_text(json.dumps(value,indent=2)+"\n");t.replace(p)
def attempt():
 outbox=R/"outbox";outbox.mkdir(exist_ok=True)
 sources={p.relative_to(outbox).as_posix():p for p in outbox.rglob("*") if p.is_file()}
 if not sources:raise RuntimeError("No sealed local outbox")
 cloud=ViperCloud(outbox,GcsRepository(bucket="mantra-mlfg-prod-uscentral1-8e7a",prefix="viper"))
 files=cloud.resolved_files(ViperCloudDestination(owner="pvd232",workspace="jep_moral_geometry_20261110"),sources)
 for ref in files.values():cloud.verify_file(ref)
 return dict(status="verified",references={str(k):v.model_dump(mode="json") for k,v in files.items()},files=len(files),outbox=str(outbox))
if __name__=="__main__":
 if "--attempt" in __import__("sys").argv:
  print(json.dumps(attempt()));raise SystemExit(0)
 for number in range(1,4):
  try:
   # Enforce a per-attempt wall limit even if a provider call stalls.
   proc=subprocess.run([__import__("sys").executable,__file__,"--attempt"],capture_output=True,text=True,timeout=90)
   if proc.returncode:raise RuntimeError(proc.stderr[-2000:] or proc.stdout[-2000:])
   receipt=json.loads(proc.stdout.strip().splitlines()[-1]);receipt["attempt"]=number;atomic(receipt);break
  except Exception as error:
   atomic(dict(status="publication_pending",attempt=number,error=repr(error),local_outbox_retained=True))
   # Permission denial is terminal for this operation; do not retry another namespace.
   if any(s in repr(error).lower() for s in ["403","forbidden","permission"]):break
   if number<3:time.sleep(10)
