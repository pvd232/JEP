"""Launch the approved extraction pilot after checkpoint verification."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path('/home/machina/jep-instructuie-pilot-20261026')
PYTHON = '/home/machina/jep-format-env/bin/python'
LOCK = Path('/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock')
STATUS = ROOT / 'execution-status.json'
deadline = time.monotonic() + 4 * 60 * 60


def status(phase, **fields):
    record = {'phase': phase, 'updated_at_unix': time.time(), **fields}
    temporary = STATUS.with_suffix('.tmp')
    temporary.write_text(json.dumps(record, indent=2) + '\n')
    temporary.replace(STATUS)
    print(json.dumps(record), flush=True)


status('waiting_model_verification', worker_pid=os.getpid())
while not (ROOT / 'model-ready.json').exists():
    if time.monotonic() > deadline:
        status('failed', reason='model_verification_timeout')
        raise SystemExit(2)
    time.sleep(15)
status('waiting_gpu_lock', worker_pid=os.getpid())
with LOCK.open('r') as lock:
    while True:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() > deadline:
                status('failed', reason='gpu_lock_timeout')
                raise SystemExit(3)
            time.sleep(15)
    command = [PYTHON, '-u', str(ROOT / 'run_instructuie.py'),
               '--inputs', str(ROOT / 'inputs.json'),
               '--output', str(ROOT / 'outputs.jsonl'),
               '--model-path', str(ROOT / 'model'),
               '--device', 'cuda', '--dtype', 'bfloat16', '--execute']
    with (ROOT / 'instructuie-run.log').open('x') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        status('running', worker_pid=os.getpid(), inference_pid=child.pid,
               command=command)
        code = child.wait()
    manifest = ROOT / 'outputs.jsonl.manifest.json'
    if code == 0 and manifest.exists():
        status('complete', exit_code=code, manifest=json.loads(manifest.read_text()))
    else:
        status('failed', exit_code=code, log=str(ROOT / 'instructuie-run.log'))
    raise SystemExit(code)
