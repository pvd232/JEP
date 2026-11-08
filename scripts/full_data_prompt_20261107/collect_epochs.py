#!/usr/bin/env python3
"""One-shot authenticated IAP/cloud exporter for exactly two task-owned GPU workers.

This is not a recurring automation. Interrupted/failed workers are preserved and
stopped rather than relaunched blindly. Auth failure never causes credential
export, IAM alteration, permission bypass, or an unbounded idle GPU allocation.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time

PROJECT='mantra-477901'
ACCOUNT='pvd2112@columbia.edu'
REMOTE_ROOT='/home/machina/jep-full-data-task-20261107/repo'
PREFIX='gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_full_data_prompt_20261107'
WORKERS={
 'worker1':('jep-full-prompt-spot-1-20261107','asia-northeast3-a'),
 'worker2':('jep-full-prompt-spot-2-20261107','asia-northeast1-b'),
}

def run(args: list[str], timeout: int=120) -> subprocess.CompletedProcess:
    """Invoke one bounded provider CLI command, preserving stderr on failure."""
    return subprocess.run(args,capture_output=True,text=True,timeout=timeout)

def require_ok(result: subprocess.CompletedProcess) -> str:
    """Return stdout only after confirmed command success."""
    if result.returncode:
        raise RuntimeError(result.stderr[-1800:] or result.stdout[-1800:])
    return result.stdout

def sha(path: Path) -> str:
    """Hash streamed file bytes independently of provider metadata checksums."""
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def ssh(worker: str, command: str, timeout: int=120) -> subprocess.CompletedProcess:
    """Use private IAP; no external IPs or transferred credentials."""
    instance,zone=WORKERS[worker]
    return run(['gcloud','compute','ssh',f'machina@{instance}',f'--project={PROJECT}',
                f'--zone={zone}',f'--account={ACCOUNT}','--tunnel-through-iap','--quiet',
                '--command='+command],timeout)

def scp(worker: str, source: str, target: str, upload: bool=False) -> None:
    """Copy one task artifact over the established IAP channel."""
    instance,zone=WORKERS[worker]
    src=source if upload else f'machina@{instance}:{source}'
    dst=f'machina@{instance}:{target}' if upload else target
    require_ok(run(['gcloud','compute','scp',src,dst,f'--project={PROJECT}',f'--zone={zone}',
                    f'--account={ACCOUNT}','--tunnel-through-iap','--quiet'],900))

def describe(worker: str) -> dict:
    """Confirm task labels before any stop operation; never act on historical VMs."""
    instance,zone=WORKERS[worker]
    text=require_ok(run(['gcloud','compute','instances','describe',instance,
                         f'--project={PROJECT}',f'--zone={zone}',f'--account={ACCOUNT}',
                         '--format=json(name,status,labels,scheduling.provisioningModel)'],60))
    d=json.loads(text)
    if d['name']!=instance or d.get('labels',{}).get('task')!='jep-full-data-20261107':
        raise ValueError('Instance ownership does not match this task.')
    return d

def stop(worker: str) -> dict:
    """Stop only the two named, label-confirmed task clones; disks remain preserved."""
    d=describe(worker)
    instance,zone=WORKERS[worker]
    if d['status']!='TERMINATED':
        require_ok(run(['gcloud','compute','instances','stop',instance,f'--project={PROJECT}',
                        f'--zone={zone}',f'--account={ACCOUNT}','--quiet'],180))
    final=describe(worker)
    return {'worker':worker,'instance':instance,'status':final['status']}

def read_worker(worker: str) -> dict:
    """Fetch only task state and complete export manifests, never credential paths."""
    base=f'{REMOTE_ROOT}/baseline_results/full_data_prompt_20261107/{worker}'
    program=f'''import json,pathlib
p=pathlib.Path({base!r})
s=json.loads((p/'state.json').read_text()) if (p/'state.json').exists() else None
ready=[]
for m in sorted((p/'transfer').glob('*/ready.json')):
 if not (m.parent/'ack.json').exists():ready.append(json.loads(m.read_text()))
print(json.dumps({{'state':s,'ready':ready}}))
'''
    return json.loads(require_ok(ssh(worker,'python3 -c '+shlex.quote(program),90)))

def collect(worker: str, manifest: dict, local: Path, expected_source: str) -> dict:
    """Require archive SHA and cloud-download SHA before publishing generation ACK."""
    generation=manifest['generation']
    if (manifest['worker']!=worker or manifest['source_commit']!=expected_source
            or not generation or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in generation)):
        raise ValueError('Export identity or generation name differs from assigned work.')
    remote_base=f'{REMOTE_ROOT}/baseline_results/full_data_prompt_20261107/{worker}/transfer/{generation}'
    if manifest['archive']!=remote_base+'/native.tar':
        raise ValueError('Unexpected remote artifact path.')
    folder=local/worker/generation;folder.mkdir(parents=True,exist_ok=True)
    (folder/'ready.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=folder/'native.tar'
    if not archive.exists() or sha(archive)!=manifest['archive_sha256']:
        partial=folder/'native.tar.partial'
        scp(worker,manifest['archive'],str(partial))
        if partial.stat().st_size!=manifest['archive_size'] or sha(partial)!=manifest['archive_sha256']:
            raise ValueError('IAP-delivered native artifact bytes differ from sealed generation.')
        partial.replace(archive)
    destination=f'{PREFIX}/{expected_source}/{worker}/{generation}'
    flags=[f'--project={PROJECT}',f'--account={ACCOUNT}','--quiet']
    require_ok(run(['gcloud','storage','cp',str(archive),destination+'/native.tar',*flags],900))
    roundtrip=folder/'roundtrip.native.tar'
    require_ok(run(['gcloud','storage','cp',destination+'/native.tar',str(roundtrip),*flags],900))
    if sha(roundtrip)!=manifest['archive_sha256']:
        raise ValueError('Cloud native artifact failed independent SHA round trip.')
    roundtrip.unlink()
    # Authoritative manifest is published after all its referenced bytes verify.
    require_ok(run(['gcloud','storage','cp',str(folder/'ready.json'),destination+'/manifest.json',*flags],120))
    ack={'generation':generation,'source_commit':expected_source,
         'archive_sha256':manifest['archive_sha256'],'cloud_roundtrip_verified':True,
         'cloud_prefix':destination,'verified_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    path=folder/'ack.json';path.write_text(json.dumps(ack,indent=2)+'\n')
    scp(worker,str(path),remote_base+'/ack.json.partial',upload=True)
    require_ok(ssh(worker,'mv '+shlex.quote(remote_base+'/ack.json.partial')+' '+shlex.quote(remote_base+'/ack.json'),60))
    return ack

def monitor(worker: str, args: argparse.Namespace) -> dict:
    """Export sequential generations and stop this GPU after completion/failure."""
    deadline=time.monotonic()+args.max_hours*3600
    local=args.local;last=None;observed_start=False
    try:
        while time.monotonic()<deadline:
            d=describe(worker)
            if d['status']=='TERMINATED':
                raise RuntimeError('Task worker stopped or was preempted; persistent checkpoint disk preserved for explicit resume.')
            if d['status']!='RUNNING':
                time.sleep(15);continue
            obj=read_worker(worker)
            if obj['state']:
                observed_start=True;last=obj['state']
                (local/f'{worker}-latest-state.json').write_text(json.dumps(last,indent=2)+'\n')
                if last['source_commit']!=args.source:
                    raise ValueError('Running source differs from approved collector source.')
            for manifest in obj['ready']:
                ack=collect(worker,manifest,local,args.source)
                print(json.dumps({'event':'native_generation_cloud_verified','worker':worker,**ack}),flush=True)
            if last and last['status']=='assigned_training_complete_test_not_opened':
                if not (local/worker/'training-final'/'ack.json').exists():
                    time.sleep(5);continue
                return {'status':'training_collected_test_still_locked','worker':worker,
                        'trials':len(last['trials']),'gpu':stop(worker)}
            if last and last['status']=='failed_preserved':
                raise RuntimeError(json.dumps(last.get('failure',{})))
            if not observed_start and time.monotonic()>deadline-(args.max_hours*3600-300):
                raise RuntimeError('Training never started within the bounded launch window.')
            time.sleep(20)
        raise TimeoutError('Bounded training collection window ended; preserve and stop.')
    finally:
        try:
            result=stop(worker);print(json.dumps({'event':'gpu_shutdown_verified',**result}),flush=True)
        except Exception as exc:
            print(json.dumps({'event':'cloud_stop_unverified_guest_deadline_remains','worker':worker,'error':str(exc)}),flush=True)

def main() -> None:
    """Run one bounded collector per task GPU; no schedules or future triggers."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True)
    p.add_argument('--local',type=Path,required=True)
    p.add_argument('--max-hours',type=float,default=23)
    args=p.parse_args()
    if len(args.source)!=40 or any(c not in '0123456789abcdef' for c in args.source):raise ValueError('Exact source commit required.')
    if not 0<args.max_hours<=23:raise ValueError('Collector time must fit task shutdown envelope.')
    args.local.mkdir(parents=True,exist_ok=True)
    records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pending={pool.submit(monitor,w,args):w for w in WORKERS}
        for future in concurrent.futures.as_completed(pending):
            w=pending[future]
            try:record=future.result()
            except Exception as exc:record={'worker':w,'status':'failed_preserved','reason':str(exc)}
            records.append(record);print(json.dumps(record),flush=True)
    (args.local/'collection-final.json').write_text(json.dumps(records,indent=2)+'\n')
    if any(r['status']!='training_collected_test_still_locked' for r in records):raise SystemExit(2)

if __name__=='__main__':main()
