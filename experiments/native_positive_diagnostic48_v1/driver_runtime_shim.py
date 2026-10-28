"""Activate the already reviewed real-driver discovery wrapper in this worker only."""
from pathlib import Path
import hashlib
import json
import os


def activate(receipt_path,receipt_sha256):
    receipt=Path(receipt_path)
    raw=receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt_sha256:
        raise ValueError('Frozen driver-discovery receipt changed')
    record=json.loads(raw)
    if record.get('status')!='ready_cpu_discovery_verified' or record.get('global_cache_or_symlinks_modified') is not False:
        raise ValueError('Driver discovery receipt is not the reviewed local-only method')
    prefix=Path(record['path_prefix'])
    wrapper=prefix/'ldconfig'
    if hashlib.sha256(wrapper.read_bytes()).hexdigest()!=record['wrapper_sha256']:
        raise ValueError('Frozen driver discovery wrapper changed')
    driver=Path(record['driver'])
    if str(driver.resolve())!=record['driver_resolved'] or hashlib.sha256(driver.read_bytes()).hexdigest()!=record['driver_sha256']:
        raise ValueError('Actual driver bytes changed')
    os.environ['PATH']=str(prefix)+os.pathsep+os.environ.get('PATH','')
