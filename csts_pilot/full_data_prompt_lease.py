"""Bind a local GPU execution to one immutable Mantra instance and shutdown deadline."""
from __future__ import annotations
import datetime as dt
import subprocess
import time
import urllib.request
from typing import Any

ASSIGNMENTS={
    'worker1':('jep-full-prompt-spot-1-20261107','asia-northeast3-a'),
    'worker2':('jep-full-prompt-spot-2-20261107','asia-northeast1-b'),
}


def validate_assignment(worker: str, assignment: dict[str, Any], actual: dict[str, str],
                        gpu_uuid: str, scheduled_usec: int | None, now: float) -> dict[str, Any]:
    """Reject wrong hosts, unbound GPUs and missing/expired independent shutdown timers.

    An immutable GCP instance ID plus a host-wide flock is the exclusive lease:
    a different host cannot use it, and two worker labels cannot share one GPU.
    The external collector binds this same execution identity in immutable objects.
    """
    if worker not in ASSIGNMENTS:
        raise PermissionError('Unknown task worker.')
    name,zone=ASSIGNMENTS[worker]
    if assignment.get('instance_name')!=name or assignment.get('zone')!=zone:
        raise PermissionError('Assignment does not identify the fixed task worker.')
    expected={'project':'mantra-477901','name':name,'zone':zone,'id':assignment.get('instance_id')}
    if actual!=expected or not isinstance(actual['id'],str) or not actual['id'].isdigit():
        raise PermissionError('Actual GCP identity differs from the assigned immutable instance.')
    if not gpu_uuid.startswith('GPU-') or gpu_uuid!=assignment.get('gpu_uuid'):
        raise PermissionError('Actual GPU differs from the assigned execution lease.')
    execution=assignment.get('execution_id','')
    if len(execution)!=32 or any(c not in '0123456789abcdef' for c in execution):
        raise PermissionError('A unique immutable execution lease is required.')
    deadline=assignment.get('deadline_epoch')
    if not isinstance(deadline,(int,float)) or not now+60<deadline<=now+86400:
        raise PermissionError('Task allocation deadline is absent, expired or exceeds 24 hours.')
    if scheduled_usec is None or abs(scheduled_usec/1e6-deadline)>60:
        raise PermissionError('Independent guest shutdown deadline is not installed as assigned.')
    return {'worker':worker,'execution_id':execution,'instance_id':actual['id'],
            'gpu_uuid':gpu_uuid,'deadline_epoch':deadline,
            'deadline_utc':dt.datetime.fromtimestamp(deadline,dt.timezone.utc).isoformat(),
            'deadline_verified':True}


def inspect_local_assignment(worker: str, assignment: dict[str, Any]) -> dict[str, Any]:
    """Read nonsecret GCP metadata and installed timer; never request credentials."""
    def metadata(path: str) -> str:
        request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/'+path,
                                       headers={'Metadata-Flavor':'Google'})
        with urllib.request.urlopen(request,timeout=5) as response:
            return response.read().decode().strip()
    actual={'project':metadata('project/project-id'),'name':metadata('instance/name'),
            'zone':metadata('instance/zone').rsplit('/',1)[-1],'id':metadata('instance/id')}
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True,timeout=10).strip().splitlines()
    if len(gpu)!=1:raise PermissionError('Task worker must expose exactly one assigned GPU.')
    result=subprocess.run(['sudo','-n','cat','/run/systemd/shutdown/scheduled'],capture_output=True,text=True,timeout=5)
    fields=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    scheduled=int(fields['USEC']) if result.returncode==0 and fields.get('USEC','').isdigit() else None
    return validate_assignment(worker,assignment,actual,gpu[0],scheduled,time.time())
