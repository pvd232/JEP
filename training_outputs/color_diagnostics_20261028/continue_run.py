"""Continue the frozen diagnostic after its timed sample and retain final outputs."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root=Path('/home/machina/jep-color-diagnostic-20261028')
python='/home/machina/jep-format-env/bin/python'
lock=(root/'supervisor.lock').open('w')
fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
def update(**fields):
    value=dict(pid=os.getpid(),updated_unix=time.time(),**fields)
    temporary=root/'supervisor_status.tmp';temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(root/'supervisor_status.json')
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for x in iter(lambda:f.read(8*1024*1024),b''):h.update(x)
    return h.hexdigest()
update(status='waiting_for_timed_sample')
until=time.monotonic()+1800
while not (root/'benchmark_exit.json').exists():
    failed=root/'gpu_check_exit.json'
    if failed.exists() and json.loads(failed.read_text())['returncode']:
        update(status='gpu_validation_failed');raise SystemExit(1)
    if time.monotonic()>until:
        update(status='timed_sample_timeout');raise SystemExit(1)
    time.sleep(5)
if json.loads((root/'benchmark_exit.json').read_text())['returncode']:
    update(status='timed_sample_failed');raise SystemExit(1)
frozen=json.loads((root/'diagnostic_protocol.json').read_text())
for name,sha in frozen['hashes'].items():
    if digest(root/name)!=sha:
        update(status='frozen_input_changed',file=name);raise SystemExit(1)
commands=json.loads((root/'benchmark_launch.json').read_text())['commands']
inference=commands[1]
i=inference.index('--benchmark-batches');inference=inference[:i]+inference[i+2:]
update(status='inference_running',command=inference)
env=os.environ.copy();env.update(PYTHONUNBUFFERED='1',HF_HOME='/home/machina/jep-model-cache',TOKENIZERS_PARALLELISM='false')
with (root/'inference.log').open('ab',buffering=0) as log:
    result=subprocess.run(inference,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
if result.returncode:
    update(status='inference_failed',returncode=result.returncode);raise SystemExit(result.returncode)
contract=json.loads((root/'results/run_contract.json').read_text())
if contract['parser_sha256']!=digest(root/'probe.py') or contract['probe_sha256']!=digest(root/'data/probe.json'):
    update(status='analysis_input_changed');raise SystemExit(1)
update(status='analysis_running')
analysis=[python,str(root/'analyze_diagnostics.py'),'--probe',str(root/'data/probe.json'),
          '--results',str(root/'results'),'--output',str(root/'analysis'),'--preliminary']
with (root/'analysis.log').open('ab',buffering=0) as log:
    result=subprocess.run(analysis,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
if result.returncode:
    update(status='analysis_failed',returncode=result.returncode);raise SystemExit(result.returncode)
update(status='complete',report=str(root/'analysis/report.md'),
       metrics_sha256=digest(root/'analysis/metrics.json'),report_sha256=digest(root/'analysis/report.md'))
