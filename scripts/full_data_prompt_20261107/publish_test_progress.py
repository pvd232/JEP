"""Publish frozen-checkpoint scores incrementally on the established GitHub monitor branch."""
from pathlib import Path
import argparse,base64,concurrent.futures,csv,datetime as dt,hashlib,io,json,os,shlex,statistics,subprocess,sys,time

def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".partial");tmp.write_text(value);tmp.replace(path)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--launch-dir",type=Path,required=True)
    p.add_argument("--monitor-checkout",type=Path,required=True)
    p.add_argument("--once",action="store_true")
    a=p.parse_args()
    root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
    from scripts.full_data_prompt_20261107.collect_epochs import controller_environment
    from csts_pilot.diagnostics import summarize
    os.environ.update(controller_environment())
    out=a.launch_dir;mon=a.monitor_checkout
    branch="monitor/full-data-prompt-20261107"
    account="767812446290-compute@developer.gserviceaccount.com"
    matrix=json.loads((out/"payload/matrix.json").read_text())
    selected={s["trial_id"]:s for s in matrix}
    test=json.loads((out/"payload/test.json").read_text())
    test_sha=digest((out/"payload/test.json").read_bytes())
    source=json.loads((out/"evaluation-source.json").read_text())["source_commit"]
    cache_path=out/"incremental-test-metrics.json"
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    destination=mon/"plans/full_data_prompt_20261107"
    errors={}
    def git(*args):
        return subprocess.check_output(["git","-C",str(mon),*args],text=True,stderr=subprocess.STDOUT).strip()
    def collect(worker):
        final=out/("results-eval"+str(worker)+".json")
        if final.exists():
            result=json.loads(final.read_text())
            return {m["trial_id"]:{**m,"cloud_verified":True} for m in result["metrics"]}
        latest=out/("latest-eval"+str(worker)+".json")
        if not latest.exists():return {}
        state=json.loads(latest.read_text())
        if state["source_commit"]!=source:raise ValueError("Unexpected inference source")
        records=[r for r in state["records"] if r["trial_id"] not in cache]
        if not records:return {}
        allocation=json.loads((out/("allocation-eval"+str(worker)+".json")).read_text())["allocation"]
        code="from pathlib import Path;import json,base64;records="+repr(records)+";result=[]\nfor r in records:\n d=Path(r['path']).parent/'artifacts'/'capture';result.append({'record':r,'predictions':base64.b64encode((d/'predictions/predictions.json').read_bytes()).decode(),'timing':json.loads((d/'timing/timing.json').read_text())})\nprint(json.dumps(result))"
        response=subprocess.run(["gcloud","compute","ssh","machina@"+allocation["instance_name"],
            "--project=mantra-477901","--zone="+allocation["zone"],"--account="+account,
            "--quiet","--tunnel-through-iap","--command=python3 -c "+shlex.quote(code)],
            capture_output=True,text=True,timeout=80)
        if response.returncode:raise RuntimeError(response.stderr[-1500:])
        updates={}
        for obj in json.loads(response.stdout):
            record=obj["record"];trial=record["trial_id"];s=selected[trial]
            raw=base64.b64decode(obj["predictions"],validate=True);timing=obj["timing"]
            assert digest(raw)==record["predictions_sha256"]==timing["predictions_sha256"]
            assert timing["model_sha256"]==s["model_sha256"] and timing["test_sha256"]==test_sha
            predictions=json.loads(raw)
            assert len(predictions)==len(test)
            assert all({k:v for k,v in row.items() if k!="prediction"}==original for row,original in zip(predictions,test,strict=True))
            atomic(out/"progress_predictions"/trial/"predictions.json",raw.decode())
            atomic(out/"progress_predictions"/trial/"timing.json",json.dumps(timing,indent=2)+"\n")
            updates[trial]={"trial_id":trial,"arm":s["arm"],"seed":s["seed"],
                "validation":s["validation_metrics"],"test":summarize(predictions),
                "selected_epoch":s["selected_epoch"],"completed_epochs":s["completed_epochs"],
                "scoring_seconds":timing["scoring_including_model_load_seconds"],
                "native_seconds":record["seconds"],"predictions_sha256":digest(raw),"cloud_verified":False}
        return updates
    deadline=time.monotonic()+7000
    while time.monotonic()<deadline:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            pending={pool.submit(collect,w):w for w in (1,2)}
            for future,w in pending.items():
                try:cache.update(future.result());errors.pop(str(w),None)
                except Exception as error:errors[str(w)]=str(error);print(json.dumps({"worker":w,"observation_error":str(error)}),flush=True)
        atomic(cache_path,json.dumps(cache,indent=2)+"\n")
        now=dt.datetime.now(dt.timezone.utc).isoformat()
        states={}
        for w in (1,2):
            path=out/("latest-eval"+str(w)+".json")
            if path.exists():
                s=json.loads(path.read_text())
                states[str(w)]={"phase":s["phase"],"completed":len(s["records"]),"assigned":len(s["assigned"]),
                    "current_trial":s.get("current_trial"),"last_cpu_observation_utc":dt.datetime.fromtimestamp(path.stat().st_mtime,dt.timezone.utc).isoformat(),
                    "validation_replay":s.get("validation_replay")}
        cleanups={}
        for w in (1,2):
            path=out/("cleanup-eval"+str(w)+".json")
            if path.exists():cleanups[str(w)]=json.loads(path.read_text())
        payload={"checked_utc":now,"source_commit":source,"training_fits":15,"test_scores":len(cache),
            "cloud_verified_test_scores":sum(bool(m["cloud_verified"]) for m in cache.values()),
            "workers":states,"scores":cache,"observation_errors":errors,"cleanup":cleanups,
            "test_status":"previously_examined_exploratory","selection_rule":"validation only; frozen before test"}
        lines=["# Live validation and test results","",
            "Updated: "+now+". This durable reporter checks every 30 seconds and pushes each newly observed score to this branch.","",
            "**Training: 15/15 finished. Test scores: "+str(len(cache))+"/15. VIPER cloud bytes independently verified: "+str(payload["cloud_verified_test_scores"])+"/15.**","",
            "Scores are Spearman correlation. Checkpoints were selected using validation only; no retraining occurs here. The test partition was previously examined and these comparisons are exploratory.","",
            "| Arm | Seed | Selected epoch | Validation | Test | Publication |",
            "| --- | ---: | ---: | ---: | ---: | --- |"]
        for s in sorted(matrix,key=lambda x:(x["arm"],x["seed"])):
            m=cache.get(s["trial_id"])
            score=f'{m["test"]["spearman"]:.6f}' if m else "pending"
            publication=("cloud verified" if m["cloud_verified"] else "sealed; cloud verification pending") if m else "pending"
            lines.append(f'| {s["arm"]} | {s["seed"]} | {s["selected_epoch"]} | {s["validation_metrics"]["spearman"]:.6f} | {score} | {publication} |')
        lines+=["","| Arm | Validation mean ± SD (5 seeds) | Test mean ± SD | Completed test seeds |",
            "| --- | ---: | ---: | ---: |"]
        for arm in sorted({s["arm"] for s in matrix}):
            vals=[s["validation_metrics"]["spearman"] for s in matrix if s["arm"]==arm]
            tests=[m["test"]["spearman"] for m in cache.values() if m["arm"]==arm]
            test_text=f"{statistics.mean(tests):.6f} ± {statistics.stdev(tests):.6f}" if len(tests)==5 else "pending full arm"
            lines.append(f'| {arm} | {statistics.mean(vals):.6f} ± {statistics.stdev(vals):.6f} | {test_text} | {len(tests)}/5 |')
        lines+=["","| Worker | Observed phase | Test captures | Current trial |",
            "| --- | --- | ---: | --- |"]
        for w,s in states.items():lines.append(f'| {w} | {s["phase"]} | {s["completed"]}/{s["assigned"]} | {s["current_trial"]} |')
        if errors:lines+=["","An observation failed; retained scores remain valid. See structured status for the exact error."]
        lines+=["","Inference and native VIPER uploads run concurrently. 'Sealed' means the CPU independently checked prediction bytes, row identities, labels and frozen model/test hashes. 'Cloud verified' additionally requires verified publication and download receipts. Compute cleanup follows verified export.","",
            "[Score CSV](test-progress.csv) · [Structured status](test-progress.json) · [Final analysis](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/training_outputs/full_data_prompt_20261108/test-results.md)",""]
        if cleanups:lines+=["Cleanup receipts received for worker(s): "+", ".join(cleanups)+".",""]
        buf=io.StringIO();writer=csv.writer(buf)
        writer.writerow(["trial_id","arm","seed","selected_epoch","validation_spearman","test_spearman","test_mse_0_1","cloud_verified"])
        for s in sorted(matrix,key=lambda x:(x["arm"],x["seed"])):
            m=cache.get(s["trial_id"])
            writer.writerow([s["trial_id"],s["arm"],s["seed"],s["selected_epoch"],s["validation_metrics"]["spearman"],
                m["test"]["spearman"] if m else "",m["test"]["mse_0_1"] if m else "",m["cloud_verified"] if m else ""])
        paths=["plans/full_data_prompt_20261107/"+x for x in ("live-status.md","test-progress.csv","test-progress.json")]
        signature_data={k:v for k,v in payload.items() if k!="checked_utc"}
        signature_data["workers"]={w:{k:v for k,v in state.items() if k!="last_cpu_observation_utc"} for w,state in states.items()}
        signature=digest(json.dumps(signature_data,sort_keys=True).encode())
        previous=out/"test-progress-published-signature.txt"
        publication_ok=previous.exists() and previous.read_text()==signature
        if a.once or not publication_ok:
            publication_ok=False
            atomic(destination/"live-status.md","\n".join(lines))
            atomic(destination/"test-progress.csv",buf.getvalue())
            atomic(destination/"test-progress.json",json.dumps(payload,indent=2)+"\n")
            try:
                assert git("branch","--show-current")==branch
                git("add","--",*paths)
                if git("diff","--cached","--name-only"):
                    git("-c","user.name=pvd232","-c","user.email=50126818+pvd232@users.noreply.github.com",
                        "commit","-m",f"Publish live test scores {len(cache)}/15 [skip ci]")
                git("push","origin","HEAD:refs/heads/"+branch)
                atomic(previous,signature)
                publication_ok=True
                print(json.dumps({"published_test_scores":len(cache),"cloud_verified":payload["cloud_verified_test_scores"],"commit":git("rev-parse","HEAD"),"utc":now}),flush=True)
            except Exception as error:print(json.dumps({"publication_error":str(error)}),flush=True)
        if a.once:
            if not publication_ok:raise RuntimeError("GitHub result publication failed; local results retained")
            return
        if publication_ok and len(cache)==15 and payload["cloud_verified_test_scores"]==15 and len(cleanups)==2:return
        time.sleep(30)
    raise TimeoutError("GitHub test reporter deadline reached")

if __name__=="__main__":main()
