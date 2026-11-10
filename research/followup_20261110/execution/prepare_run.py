"""Freeze new user-authorized response-attribute follow-up; retain the completed pilot."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path("/home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110")
OLD=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
RUN=OLD.parent/"moral-followup-20261110"
HERE=Path(__file__).parent
if (RUN/"frozen_v2.json").exists():
 raise SystemExit("Run is frozen. Use controller.py --resume or --plan-only; retained data and runners are preserved.")
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
# Runtime sources are checked in and reviewed independently from frozen data.
for name in ["controller.py", "gpu_worker.py", "capacity_advisor.py"]:
 assert (HERE/name).is_file(), "Missing checked-in runtime source: "+name
print("FOLLOWUP_FROZEN",len(tasks),"contexts",sha(RUN/"frozen_v2.json"))
