"""Seal only imported provider/helper/data bytes; never test logs or source cases."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
BASE=Path('/tmp/jep-native-general-capture-20261028/support-seal.json')


def main():
    original=json.loads(BASE.read_text())['files']
    names={name for name in original if not name.startswith('native_adapter/')}
    names.update(str(path.relative_to(ROOT))for path in(ROOT/'native_adapter').iterdir()
                 if path.is_file()and path.suffix in('.py','.json'))
    names.update({'build_protocol.py','seal_support.py','evaluate_native.py','native_cpu_codec.py','runtime-manifest.json',
                  'driver_runtime_shim.py','driver-discovery-receipt.json'})
    files={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()for name in sorted(names)}
    record={'status':'FROZEN_POSITIVE_DIAGNOSTIC_PROVIDER_PENDING_INDEPENDENT_REVIEW','files':files,
            'no_heldout_content_read':True,'automatic_companions':False,'automatic_retries':False,
            'symbolic_count_dispatch':False,'count_evidence_dispatch':False,
            'semantic_qualification_passed':False,'fresh_evaluation_authorized':False}
    (ROOT/'support-seal.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':main()
