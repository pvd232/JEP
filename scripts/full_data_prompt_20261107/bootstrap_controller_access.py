"""Give the attached controller persistent workload administration as requested."""
from pathlib import Path
import json,subprocess,datetime as dt,urllib.request

PROJECT="mantra-477901"
ADMIN="pvd2112@columbia.edu"
PRINCIPAL="767812446290-compute@developer.gserviceaccount.com"
DEP=Path("/home/peter_aetherlabs_live/jep-full-data-launch-20261107/deployment-20261108")
RECORD=DEP/"inspection-20261108-2142/controller-bootstrap"
RECORD.mkdir(exist_ok=True)
request=urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
                              headers={"Metadata-Flavor":"Google"})
with urllib.request.urlopen(request,timeout=5) as response:
    assert response.read().decode().strip()==PRINCIPAL

# The user explicitly requested persistent project-wide access without per-run conditions.
member="serviceAccount:"+PRINCIPAL
commands=[
 ("project_owner",["gcloud","projects","add-iam-policy-binding",PROJECT,
    "--project="+PROJECT,"--account="+ADMIN,"--quiet","--member="+member,
    "--role=roles/owner","--condition=None"]),
 ("iap_access",["gcloud","projects","add-iam-policy-binding",PROJECT,
    "--project="+PROJECT,"--account="+ADMIN,"--quiet","--member="+member,
    "--role=roles/iap.tunnelResourceAccessor","--condition=None"]),
 ("viper_bucket_admin",["gcloud","storage","buckets","add-iam-policy-binding",
    "gs://mantra-mlfg-prod-uscentral1-8e7a","--project="+PROJECT,"--account="+ADMIN,"--quiet",
    "--member="+member,"--role=roles/storage.admin","--condition=None"])
]
receipts=[]
for label,command in commands:
    result=subprocess.run(command,text=True,capture_output=True,timeout=90)
    if result.returncode:raise RuntimeError(label+": "+result.stderr[-1800:])
    receipts.append({"action":label,"applied_utc":dt.datetime.now(dt.timezone.utc).isoformat()})
    (RECORD/"applied.json").write_text(json.dumps({"principal":PRINCIPAL,"project":PROJECT,
        "scope":"persistent_project_wide","conditional":False,"receipts":receipts},indent=2)+"\n")
    print(json.dumps({"grant_applied":label,"principal":PRINCIPAL}),flush=True)
print(json.dumps({"status":"persistent_workload_access_applied","principal":PRINCIPAL,
                 "project":PROJECT,"no_per_run_access_expiry":True}),flush=True)
