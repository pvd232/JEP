"""Readable capture/replay entrypoint for the frozen positive-recipe diagnostic.

The provider archive is the immutable implementation, not a second adapter.
Restore it at its declared path and supply its sealed inference-only job.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read(path):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=value
        return result
    def invalid(value):raise ValueError('Nonfinite JSON constant')
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=invalid)


def verify_provider_files(provider,protocol_path):
    """Check bytes before executing the frozen provider or driver."""
    provider=Path(provider).resolve();protocol=_read(protocol_path)
    driver=provider/'evaluate_native.py'
    if _sha(driver)!=protocol.get('capture_driver_sha256'):raise ValueError('Frozen driver differs from protocol')
    support=provider/'support-seal.json';manifest=_read(support)
    for model in protocol['models'].values():
        if _sha(support)!=model['native_capture']['support_manifest_sha256']:raise ValueError('Support manifest differs')
    for name,digest in manifest['files'].items():
        path=(provider/name).resolve()
        if provider not in path.parents or _sha(path)!=digest:raise ValueError('Frozen helper/artifact differs: '+name)
    if manifest['files'].get('evaluate_native.py')!=_sha(driver):raise ValueError('Driver is missing from support manifest')
    return driver


def _load_driver(provider,protocol_path):
    driver=verify_provider_files(provider,protocol_path)
    name='_frozen_native_positive_driver'
    if name in sys.modules:raise ValueError('Run replay in a fresh process')
    module=types.ModuleType(name);module.__file__=str(driver);sys.modules[name]=module
    sys.path.insert(0,str(Path(provider).resolve()))
    # Execute the verified source directly, avoiding stale bytecode caches.
    exec(compile(driver.read_bytes(),str(driver),'exec'),module.__dict__)
    return module


def replay(args):
    job=Path(args.job);driver=_load_driver(args.provider,job/'protocol.json')
    _,seal,protocol,freeze,sources=driver.job_data(job)
    root=Path(args.captures);manifest=driver.capture_header(root,job,seal,protocol,args.model,sources)
    module,spec=driver.load_verified_handler(protocol,args.model);results=[]
    for source in sources:
        try:
            record=driver.verified_capture(root,source,args.model,seal,protocol,freeze,manifest,module,spec)
            normalized=getattr(module,spec['verify_callable'])(source=source,model=args.model,protocol=protocol,record=record)
            if normalized!=record.get('normalized_evidence'):raise ValueError('CPU normalization differs')
            valid,reason=driver.operational(record)
            results.append({'source_id':source['id'],'replay_verified':True,'operational_valid':valid,'operational_failure':reason})
        except Exception as error:
            results.append({'source_id':source['id'],'replay_verified':False,'operational_valid':False,'error':type(error).__name__+': '+str(error)})
    value={'status':'CPU_REPLAY_COMPLETED','model':args.model,'expected_sources':len(sources),'model_calls':0,
           'semantic_support_validated':False,'semantic_qualification_passed':False,'results':results,
           'verified_records':sum(row['replay_verified']for row in results)}
    with Path(args.output).open('x')as handle:json.dump(value,handle,sort_keys=True,indent=2);handle.write('\n')
    print(json.dumps({key:value[key]for key in('status','model','expected_sources','verified_records','model_calls')}))
    return 0 if value['verified_records']==len(sources)else 1


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',type=Path,required=True,help='Exact restored frozen provider directory')
    commands=parser.add_subparsers(dest='command',required=True)
    command=commands.add_parser('verify');command.add_argument('--protocol',type=Path,required=True);command.add_argument('--model',choices=('gollie','knowcoder'),required=True)
    command=commands.add_parser('capture');command.add_argument('--job',type=Path,required=True);command.add_argument('--model',choices=('gollie','knowcoder'),required=True)
    command.add_argument('--output',type=Path,required=True);command.add_argument('--python',default=sys.executable,help='Frozen native environment Python')
    command=commands.add_parser('replay');command.add_argument('--job',type=Path,required=True);command.add_argument('--model',choices=('gollie','knowcoder'),required=True)
    command.add_argument('--captures',type=Path,required=True);command.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='replay':return replay(args)
    protocol=args.protocol if args.command=='verify'else args.job/'protocol.json'
    driver=verify_provider_files(args.provider,protocol)
    if args.command=='verify':command=[sys.executable,str(driver),'verify-provider','--protocol',str(protocol),'--model',args.model]
    else:command=[args.python,str(driver),'run-capture','--job',str(args.job),'--model',args.model,'--output',str(args.output)]
    return subprocess.run(command,check=False).returncode


if __name__=='__main__':raise SystemExit(main())
