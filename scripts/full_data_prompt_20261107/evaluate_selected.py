"""Capture test predictions from all validation-frozen models without fitting."""
from pathlib import Path
import argparse,concurrent.futures,datetime as dt,hashlib,json,subprocess,time
from viper import execution
from viper.authoring import experiment,input,plan,replicate,stage,variant
from viper.outputs import StageOutputs,output
from viper.references import GitFileRef
from viper.repository import read_source,resolve_root
from viper.runtime import CUDAComputeSpec,LocalEnvSpec,observe_python_env
from viper.storage import ViperCloudDestination
from csts_pilot.baseline_models import ScoreConfig
from csts_pilot.baseline_stages import capture_predictions
from csts_pilot.convergence_run import artifact_path
from csts_pilot.diagnostics import summarize
from csts_pilot.full_data_prompt_protocol import PROMPTS,digest_file,digest_object,require_complete_selections
from csts_pilot.full_data_prompt_uploads import cloud_service
from jep_pilot.loaders import load_json

def atomic(path,value):
    """Keep one complete inference progress record at every update."""
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".partial");tmp.write_text(json.dumps(value,indent=2)+"\n");tmp.replace(path)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--worker",type=int,choices=[1,2],required=True)
    args=parser.parse_args()
    root=resolve_root();source=read_source(root)
    data=root/"eval_inputs";protocol=load_json(data/"protocol.json");matrix=load_json(data/"matrix.json")
    require_complete_selections(protocol,matrix)
    release=load_json(data/"release.json")
    assert release["matrix_sha256"]==digest_file(data/"matrix.json")
    assert release["protocol_sha256"]==digest_object(protocol)
    assigned=[s for i,s in enumerate(matrix) if i%2==args.worker-1]
    for selected in assigned:
        assert digest_file(data/"models"/(selected["trial_id"]+".pt"))==selected["model_sha256"]
    gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name","--format=csv,noheader"],text=True).strip()
    assert gpu=="NVIDIA L4"
    destination=root/"baseline_results/full_data_prompt_test_20261108"/("worker"+str(args.worker))
    destination.mkdir(parents=True,exist_ok=True)
    status=destination/"status.json"
    state={"worker":args.worker,"source_commit":source.commit,"started_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
           "phase":"validation_replay","assigned":[s["trial_id"] for s in assigned],"records":[],"cloud":[]}
    atomic(status,state)
    environment=LocalEnvSpec(compute=CUDAComputeSpec(model="NVIDIA L4",count=1),
        lockfile=GitFileRef(repository=source.repository,commit=source.commit,path="tranche2_requirements.txt"),
        python_env=observe_python_env())
    cloud=cloud_service(root,"mantra-477901")
    uploads=concurrent.futures.ThreadPoolExecutor(max_workers=1)
    futures=[]

    def publish(paths):
        refs=cloud.resolved_files(ViperCloudDestination(owner="pvd232",workspace="jep_full_data_prompt_20261107"),paths)
        for ref in refs.values():cloud.verify_file(ref)
        return {key:ref.model_dump(mode="json") for key,ref in refs.items()}

    def capture(selected,split):
        trial=selected["trial_id"]
        config=ScoreConfig.model_validate({"kind":"lora",**{
            "model_id":protocol["model"]["id"],"revision":protocol["model"]["revision"],
            "max_length":protocol["model"]["max_length"],"embedding_dimension":protocol["model"]["width"],
            "encode_batch_size":4,"device":"cuda","prompt_template":PROMPTS[selected["arm"]],
            "expected_seed":selected["seed"],"expected_trial_id":trial,
            "matrix_sha256":digest_file(data/"matrix.json"),"protocol_sha256":digest_object(protocol),
            "model_sha256":selected["model_sha256"],"selection_sha256":digest_file(data/(trial+"-selection.json")),
            "test_sha256":protocol["splits"][split]["sha256"]}})
        split_name="test.json" if split=="test" else "validation.json"
        holdout_name="holdout.json" if split=="test" else "validation-holdout.json"
        configured=stage(capture_predictions,stage_id="capture",config=config,inputs=(
            input("test",path="eval_inputs/"+split_name,data_role="eval"),
            input("holdout",path="eval_inputs/"+holdout_name,data_role="eval"),
            input("selection",path="eval_inputs/"+trial+"-selection.json",data_role="training"),
            input("matrix",path="eval_inputs/matrix.json",data_role="training"),
            input("protocol",path="eval_inputs/protocol.json",data_role="training"),
            input("model",path="eval_inputs/models/"+trial+".pt",data_role="training")),
            outputs=StageOutputs(predictions=output(path="predictions.json",loader=load_json,data_role="eval"),
                                 timing=output(path="timing.json",loader=load_json,data_role="eval")),reuse="never")
        trial_plan=plan(experiment=experiment(experiment_id="full_prompt_test_"+source.commit[:8]+"_"+trial.lower()+"_"+split,
            variants=(variant("selected",stages=(configured,),estimator=None),),replicates=(replicate(seed=selected["seed"]),)),
            source=source,env=environment)
        started=time.monotonic()
        result=execution.run(trial_plan,timeout_seconds=1200,
                            trusted_source_repositories=frozenset({str(source.repository)}))
        if result.status!="succeeded":raise RuntimeError("Native prediction failed for "+trial+": "+result.status)
        record={"path":str(result.path),"reference":result.reference.model_dump(mode="json"),
                "trial_id":trial,"split":split,"source_commit":source.commit,"seconds":time.monotonic()-started}
        predictions=artifact_path(record,"capture","predictions","predictions.json")
        timing=artifact_path(record,"capture","timing","timing.json")
        assert len(load_json(predictions))==protocol["splits"][split]["rows"]
        record["predictions_sha256"]=digest_file(predictions)
        prefix="baseline_results/full_data_prompt_test_20261108/worker"+str(args.worker)+"/"+trial+"/"+split+"/"
        futures.append(uploads.submit(publish,{prefix+"predictions.json":predictions,prefix+"timing.json":timing,
                                              prefix+"resolved.yaml":Path(result.path)}))
        return record,predictions

    try:
        record,path=capture(assigned[0],"validation")
        observed=summarize(load_json(path))["spearman"]
        expected=assigned[0]["validation_metrics"]["spearman"]
        if abs(observed-expected)>1e-4:raise ValueError("Frozen-checkpoint validation replay differs: "+str((observed,expected)))
        state["validation_replay"]={"trial":assigned[0]["trial_id"],"expected":expected,"observed":observed,"record":record}
        state["phase"]="test_inference";atomic(status,state)
        for selected in assigned:
            state["current_trial"]=selected["trial_id"];atomic(status,state)
            record,path=capture(selected,"test");state["records"].append(record)
            atomic(status,state)
            print(json.dumps({"event":"test_predictions_sealed","worker":args.worker,
                              "trial":selected["trial_id"],"completed":len(state["records"]),"total":len(assigned)}),flush=True)
        state["phase"]="verifying_publication";atomic(status,state)
        for future in futures:state["cloud"].append(future.result())
        state["phase"]="complete";state["completed_utc"]=dt.datetime.now(dt.timezone.utc).isoformat();atomic(status,state)
        state["status_cloud"]=publish({str(status.relative_to(root)):status})
        atomic(destination/"completion.json",state)
        print(json.dumps({"event":"inference_complete","worker":args.worker,"trials":len(assigned)}),flush=True)
    except BaseException as error:
        state["phase"]="failed_preserved";state["error"]={"type":type(error).__name__,"message":str(error)}
        atomic(status,state)
        raise
    finally:
        uploads.shutdown(wait=True)

if __name__=="__main__":main()
