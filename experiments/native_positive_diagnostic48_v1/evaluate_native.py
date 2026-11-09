#!/usr/bin/env python3
"""Frozen inference-only jobs, blinded review packets, fixed-denominator metrics.

No gold/ratings are copied into inference jobs. run-capture is an explicit later
native operation; it calls a hash-pinned public handler once per source. This
module never calls Colab or a model judge on import/preparation/summarization.
"""
import argparse
import collections
import datetime
import hashlib
import importlib
import inspect
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import random
import re
import sys
import time

MODELS=('gollie','knowcoder')
PHASE_COUNTS={'locked-canaries':48,'locked-controls':80,'fresh-evaluation':240}
CRITERIA=('faithful','complete','scope_correct','binding_correct','multiplicity_correct','abstention_correct','inference_correct')
QUOTE_REPRESENTATION='uninterpreted_count_relevant_source_assertions'
QUOTE_ACCEPTED_STATUSES=('candidate_assertions','no_candidate_assertions','ambiguous_candidate_grounding')
FREEZE_CHECKS=('condition_only_schema','checkpoint_and_tokenizer_pinned','runtime_and_backend_pinned',
               'token_budget_bound','capability_profile_and_stages_bound','no_heldout_passage_or_gold_tuning')
_VERIFIED_MODULES={}
_VERIFIED_SOURCE_BYTES={}
_DECLARED_MODULE_PATHS={}
_ORIGINAL_GET_CODE=importlib.machinery.SourceFileLoader.get_code
_RUNNING_DRIVER_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def sha(raw):return hashlib.sha256(raw).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def encoded(value):return(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def read(path):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=value
        return result
    def invalid(value):raise ValueError('Nonfinite JSON constant')
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=invalid)
def write(path,value):
    with path.open('xb')as handle:handle.write(encoded(value))
def file_sha(path):return sha(Path(path).read_bytes())
def new_dir(path):
    path=Path(path).resolve()
    if path.exists():raise ValueError('Output exists; no replacement/hidden retry')
    path.mkdir(parents=True);return path


def locate_module_source(name):
    """Find plain Python source without executing package initializers."""
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',name):raise ValueError('Invalid frozen handler module name')
    parts=name.split('.')
    for value in sys.path:
        base=Path(value or Path.cwd())
        package=base.joinpath(*parts)/'__init__.py'
        source=base.joinpath(*parts).with_suffix('.py')
        if package.is_file():return package.resolve()
        if source.is_file():return source.resolve()
    raise ValueError('Frozen handler source is not available as plain Python')


def module_source_path(value):
    filename=getattr(value,'__file__',None)
    if not filename:return None
    source=Path(filename).resolve()
    if source.suffix=='.pyc':
        try:source=Path(importlib.util.source_from_cache(str(source))).resolve()
        except ValueError:source=source.with_suffix('.py')
    return source


def load_verified_handler(protocol,model):
    """Verify all declared bytes before import; execute verified source, not stale pyc."""
    descriptor=protocol['models'][model];spec=descriptor['handler'];name=spec['module']
    path=locate_module_source(name);raw=path.read_bytes()
    if sha(raw)!=spec['sha256']:raise ValueError('Native handler code differs before import')
    cfg=descriptor.get('native_capture',{});manifest_path=Path(cfg.get('support_manifest_path','support-seal.json'))
    if not manifest_path.is_absolute():manifest_path=path.parent/manifest_path
    if manifest_path.resolve()!=(path.parent/'support-seal.json').resolve():raise ValueError('Support manifest must be the handler sibling support-seal.json')
    if file_sha(manifest_path)!=cfg.get('support_manifest_sha256'):raise ValueError('Native support manifest differs before import')
    support=read(manifest_path);files=support.get('files')
    if (not isinstance(files,dict)or not files or support.get('no_heldout_content_read')is not True
            or support.get('automatic_companions')is not False or support.get('automatic_retries')is not False):raise ValueError('Support preparation/companion/retry policy differs')
    verified={};declared_modules={name:path}
    for relative,digest in files.items():
        relative=Path(relative)
        if relative.is_absolute():raise ValueError('Support artifact paths must be relative')
        artifact=(path.parent/relative).resolve()
        if path.parent.resolve()not in artifact.parents:raise ValueError('Support artifact escapes the frozen handler directory')
        data=artifact.read_bytes()
        if sha(data)!=digest:raise ValueError('Native helper/artifact differs before import: '+str(relative))
        if artifact.suffix=='.py':
            verified[artifact]=data
            parts=list(relative.parts)
            if parts[-1]=='__init__.py':parts=parts[:-1]
            else:parts[-1]=Path(parts[-1]).stem
            if parts:declared_modules['.'.join(parts)]=artifact
            if parts and parts[0]=='legacy_support'and len(parts)>1:declared_modules['.'.join(parts[1:])]=artifact
    if path not in verified or sha(verified[path])!=spec['sha256']:raise ValueError('Handler is absent from its frozen support manifest')
    for parent in ['.'.join(name.split('.')[:i])for i in range(1,len(name.split('.')))]:
        parent_path=locate_module_source(parent)
        if parent_path not in verified:raise ValueError('Package initializer is not in frozen support manifest')
    for key,digest_key in(('runtime_manifest_path','runtime_manifest_sha256'),):
        if cfg.get(key):
            artifact=Path(cfg[key]);artifact=artifact if artifact.is_absolute()else path.parent/artifact
            if file_sha(artifact)!=cfg.get(digest_key):raise ValueError('External runtime manifest differs before import')
    shim=cfg.get('runtime_shim')
    if shim:
        artifact=Path(shim['path']);artifact=artifact if artifact.is_absolute()else path.parent/artifact
        if file_sha(artifact)!=shim.get('sha256'):raise ValueError('Runtime shim differs before import')
        if artifact.suffix=='.py':verified[artifact.resolve()]=artifact.read_bytes()
        if shim.get('module_name'):declared_modules[shim['module_name']]=artifact.resolve()
    def is_running_frozen_driver(value,source):
        return (getattr(value,'__dict__',None)is globals()and source==Path(__file__).resolve()
                and source in verified and _RUNNING_DRIVER_SHA256==sha(verified[source])
                and protocol.get('capture_driver_sha256')==_RUNNING_DRIVER_SHA256)
    for module_name,expected_source in declared_modules.items():
        cached=sys.modules.get(module_name)
        if cached is not None:
            source=module_source_path(cached)
            if is_running_frozen_driver(cached,source):_VERIFIED_MODULES[module_name]=(id(cached),str(source),sha(verified[source]))
            fingerprint=_VERIFIED_MODULES.get(module_name)
            if source!=expected_source or fingerprint!=(id(cached),str(expected_source),sha(verified[expected_source])):
                raise ValueError('Conflicting/unverified cached custom module: '+module_name)
    for module_name,value in list(sys.modules.items()):
        source=module_source_path(value)
        if source is None:continue
        if source in verified:
            if is_running_frozen_driver(value,source):_VERIFIED_MODULES[module_name]=(id(value),str(source),sha(verified[source]))
            fingerprint=_VERIFIED_MODULES.get(module_name)
            if fingerprint!=(id(value),str(source),sha(verified[source])):raise ValueError('Unverified/stale cached custom module: '+module_name)
    _VERIFIED_SOURCE_BYTES.update(verified)
    _DECLARED_MODULE_PATHS.update(declared_modules)
    def frozen_get_code(loader,fullname):
        source=Path(loader.path).resolve()
        if fullname in _DECLARED_MODULE_PATHS and source!=_DECLARED_MODULE_PATHS[fullname]:raise ImportError('Frozen custom module resolved to an unverified source: '+fullname)
        if source in _VERIFIED_SOURCE_BYTES:return compile(_VERIFIED_SOURCE_BYTES[source],str(source),'exec')
        return _ORIGINAL_GET_CODE(loader,fullname)
    importlib.machinery.SourceFileLoader.get_code=frozen_get_code
    importlib.invalidate_caches();module=importlib.import_module(name)
    origin=Path(inspect.getsourcefile(module)or'').resolve()
    if origin!=path or file_sha(path)!=spec['sha256']:raise ValueError('Loaded handler origin/source differs from the frozen module')
    for module_name,value in list(sys.modules.items()):
        source=module_source_path(value)
        if source in verified:_VERIFIED_MODULES[module_name]=(id(value),str(source),sha(verified[source]))
    return module,spec


def verify_provider(args):
    """Inert CLI preflight: verify/import helper bytes, never create a backend."""
    protocol=read(args.protocol)
    if protocol.get('capture_driver_sha256')!=file_sha(Path(__file__)):raise ValueError('Executing driver differs from the protocol')
    load_verified_handler(protocol,args.model)
    print(json.dumps({'status':'verified_provider_import','model':args.model,'backend_created':False,'model_calls':0}))


def implementation_digest(value):
    if isinstance(value,dict):return sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    return value


def raw_handler_return(folder,value):
    """Preserve the actual return before rejecting an invalid bridge contract."""
    try:
        raw=(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
        with(folder/'handler-return.json').open('xb')as handle:handle.write(raw)
        return file_sha(folder/'handler-return.json')
    except(TypeError,ValueError):
        with(folder/'handler-return-repr.txt').open('x')as handle:handle.write(repr(value))
        if isinstance(value,dict)and isinstance(value.get('raw_output'),str):
            with(folder/'handler-raw-output.txt').open('x')as handle:handle.write(value['raw_output'])
        raise ValueError('Native handler return is not finite JSON; raw diagnostic return retained')


def load_source_gold(source_path,gold_dir,expected):
    sources=read(source_path);seal=read(Path(gold_dir)/'source-support-seal.json')
    if len(sources)!=expected or len({row['id']for row in sources})!=expected:raise ValueError('Frozen source coverage differs')
    if seal.get('source_support_audit_completed')is not True or seal.get('source_sha256')!=file_sha(source_path):raise ValueError('Source support seal differs or audit is pending')
    plain=Path(gold_dir)/'references.json';rich=Path(gold_dir)/'reference-annotations.json'
    hashes=seal.get('artifacts',{})
    if file_sha(plain)!=seal.get('references_sha256',hashes.get('references.json'))or file_sha(rich)!=seal.get('atomic_annotations_sha256',hashes.get('reference-annotations.json')):raise ValueError('Audited reference bytes differ')
    annotations=read(rich);references=read(plain)
    if [row['id']for row in annotations]!=[row['id']for row in sources]or references!=[{'id':row['id'],'expected_answer':row['expected_answer']}for row in annotations]:raise ValueError('Source/reference coverage/order differs')
    return sources,annotations,seal


def load_protocol(protocol_path,freeze_path):
    protocol=read(protocol_path);freeze=read(freeze_path)
    if(freeze.get('status')!='FROZEN_NATIVE_PROTOCOL'or freeze.get('protocol_sha256')!=file_sha(protocol_path)
       or set(freeze.get('models',[]))!=set(MODELS)
       or any(freeze.get('checks',{}).get(key)is not True for key in FREEZE_CHECKS)
       or not re.fullmatch(r'[a-f0-9]{64}',freeze.get('compiler_implementation_sha256',''))):raise ValueError('Compiler/native protocol freeze receipt is incomplete')
    if set(protocol.get('models',{}))!=set(MODELS):raise ValueError('Protocol must declare both native families')
    if freeze.get('compiler_implementation_files')is not None and implementation_digest(freeze['compiler_implementation_files'])!=freeze['compiler_implementation_sha256']:raise ValueError('Full compiler identity mapping/digest pair differs')
    return protocol,freeze


def prepare_job(args):
    sources,_,gold=load_source_gold(args.sources,args.gold_dir,PHASE_COUNTS[args.phase])
    protocol,freeze=load_protocol(args.protocol,args.compiler_freeze)
    if protocol.get('capture_scope')=='locked48_diagnostic_only'and args.phase!='locked-canaries':raise ValueError('Diagnostic-only protocol cannot authorize control/fresh inference')
    if protocol.get('capture_scope')=='locked48_diagnostic_only':
        expected_cohort={'sources':48,'source_sha256':file_sha(args.sources),'source_support_seal_sha256':file_sha(Path(args.gold_dir)/'source-support-seal.json')}
        if (protocol.get('diagnostic_cohort')!=expected_cohort or freeze.get('diagnostic_cohort')!=expected_cohort
                or any(descriptor.get('native_capture',{}).get('diagnostic_cohort')!=expected_cohort for descriptor in protocol['models'].values())):raise ValueError('Diagnostic protocol/cohort/source-support binding differs')
    if gold.get('unresolved_reference_disagreement_ids')and protocol.get('allow_disputed_gold_with_bounds')is not True:raise ValueError('Disputed gold needs explicit frozen bounds policy')
    gate_hash=None
    if args.phase!='locked-canaries':
        if not args.integration_gate:raise ValueError('A complete all-pass locked48 gate is required before later inference')
        gate=read(args.integration_gate)
        if(gate.get('phase')!='locked-canaries'or gate.get('protocol_sha256')!=file_sha(args.protocol)
           or gate.get('all_integration_canaries_pass')is not True or gate.get('complete_evaluation')is not True
           or any(gate.get('models',{}).get(model,{}).get('expected')!=48 or gate['models'][model].get('accepted')!=48 for model in MODELS)):
            raise ValueError('Integration gate is not exact48 all-pass for both frozen native families')
        gate_hash=file_sha(args.integration_gate)
    output=new_dir(args.output)
    projected=[{key:row[key]for key in('id','passage','condition')}for row in sources]
    write(output/'sources.json',projected)
    for name,original in(('protocol.json',args.protocol),('compiler-freeze.json',args.compiler_freeze)):
        with(output/name).open('xb')as handle:handle.write(Path(original).read_bytes())
    authorization={'status':'AUTHORIZED_SINGLE_CAPTURE_AFTER_SOURCE_AUDIT_AND_COMPILER_FREEZE','phase':args.phase,
        'sources':len(sources),'models':list(MODELS),'source_full_sha256':file_sha(args.sources),
        'source_support_seal_sha256':file_sha(Path(args.gold_dir)/'source-support-seal.json'),
        'protocol_sha256':file_sha(args.protocol),'compiler_freeze_sha256':file_sha(args.compiler_freeze),
        'integration_gate_sha256':gate_hash,'created_at_utc':now(),'inference_input_fields':['id','passage','condition'],
        'gold_or_ratings_in_inference_job':False,'single_attempt_per_source':True,
        'data_scope':'Component-disjoint from declared native-screen/repair development; not historically blind C-STS.',
        'artifacts':{name:file_sha(output/name)for name in('sources.json','protocol.json','compiler-freeze.json')}}
    write(output/'job-seal.json',authorization)
    print(json.dumps({'status':authorization['status'],'phase':args.phase,'sources':len(sources),'job_seal_sha256':file_sha(output/'job-seal.json')}))


def job_data(path):
    root=Path(path).resolve();seal=read(root/'job-seal.json')
    for name,digest in seal['artifacts'].items():
        if file_sha(root/name)!=digest:raise ValueError('Inference job artifact changed')
    protocol,freeze=load_protocol(root/'protocol.json',root/'compiler-freeze.json')
    if protocol.get('capture_scope')=='locked48_diagnostic_only'and seal.get('phase')!='locked-canaries':raise ValueError('Diagnostic-only protocol is restricted to locked48')
    sources=read(root/'sources.json')
    if len(sources)!=seal['sources']or len({s['id']for s in sources})!=len(sources):raise ValueError('Inference job source coverage differs')
    if any(set(s)!={'id','passage','condition'}or not re.fullmatch(r'[a-f0-9]{64}',s['id'])for s in sources):raise ValueError('Inference projection contains forbidden fields/invalid identity')
    return root,seal,protocol,freeze,sources


def operational(record):
    normalized=record.get('normalized_evidence')
    normalized=normalized if isinstance(normalized,dict)else{}
    if record.get('runtime_status')=='unsupported'or normalized.get('status')=='adapter_unsupported':return False,'unsupported_route'
    if normalized.get('representation')==QUOTE_REPRESENTATION and(normalized.get('parse_status')!='accepted'or normalized.get('status')not in QUOTE_ACCEPTED_STATUSES):return False,'count_evidence_invalid'
    if record.get('runtime_status')!='ok':return False,'runtime_'+str(record.get('runtime_status','missing'))
    if record.get('route_supported')is not True:return False,'route_not_approved'
    if record.get('truncated')is not False:return False,'truncated_or_unknown'
    if record.get('parse_valid')is not True:return False,'parse_invalid'
    if not isinstance(record.get('raw_output'),str)or not record['raw_output'].strip():return False,'missing_response'
    if not isinstance(record.get('normalized_evidence'),dict):return False,'missing_normalized_evidence'
    if record.get('error'):return False,'capture_error'
    return True,''


def validate_handler_record(value,source,model,protocol,freeze,protocol_sha=None):
    if not isinstance(value,dict):raise ValueError('Native handler must return a JSON record')
    record=dict(value)
    if('id'in record and record['id']!=source['id'])or('model'in record and record['model']!=model):raise ValueError('Native handler source/model identity differs')
    if protocol_sha is not None and'protocol_sha256'in record and record['protocol_sha256']!=protocol_sha:raise ValueError('Native handler protocol identity differs')
    for field in('route_supported','parse_valid','truncated','coverage_complete'):
        if type(record.get(field))is not bool:raise ValueError('Native bridge requires boolean '+field)
    if record.get('runtime_status')not in('ok','unsupported','error','timeout','not_run','truncated'):raise ValueError('Invalid runtime status')
    if not isinstance(record.get('error'),str):raise ValueError('Native bridge requires error string (empty when none)')
    if record.get('raw_output')is not None and not isinstance(record['raw_output'],str):raise ValueError('Raw native output must be string/null')
    if record.get('normalized_evidence')is not None and not isinstance(record['normalized_evidence'],dict):raise ValueError('Normalized evidence must be JSON object/null')
    calls=record.get('model_calls');limit=protocol['models'][model].get('max_model_calls_per_source',1)
    unknown_failed_call_count=(calls is None and record['runtime_status']in('error','timeout','not_run')and bool(record['error']))
    if not unknown_failed_call_count and(type(calls)is not int or type(limit)is not int or not 0<=calls<=limit):raise ValueError('Native stage-call count exceeds frozen protocol')
    if record['runtime_status']=='ok'and record['route_supported']:
        bound=record.get('bound_inputs')
        if bound is None:bound=[record.get('bound_input')]
        if not isinstance(bound,list)or len(bound)!=calls or not bound:raise ValueError('Every native stage needs its bound-input proof')
        for entry in bound:
            if not isinstance(entry,dict)or entry.get('model')!=model or not isinstance(entry.get('prompt'),str):raise ValueError('Bound native request differs')
            implementation=entry.get('implementation_sha256')
            if entry.get('prompt_sha256')!=sha(entry['prompt'].encode())or implementation_digest(implementation)!=freeze['compiler_implementation_sha256']:raise ValueError('Bound prompt/compiler hash differs')
            if freeze.get('compiler_implementation_files')is not None and implementation!=freeze['compiler_implementation_files']:raise ValueError('Bound compiler module inventory differs')
            for field in('input_tokens','max_new_tokens','context_limit'):
                if type(entry.get(field))is not int or entry[field]<0:raise ValueError('Invalid token-budget proof')
            if entry['max_new_tokens']<1 or entry['input_tokens']+entry['max_new_tokens']>entry['context_limit']:raise ValueError('Native prompt plus reserved output exceeds context')
        if record.get('bound_input_verified')is not True:raise ValueError('Handler must call the frozen adapter verify_bound_input')
    json.dumps(record,allow_nan=False)
    record.update(id=source['id'],model=model)
    return record


def run_capture(args):
    job_root,job,protocol,freeze,sources=job_data(args.job)
    if Path(args.output).exists():raise ValueError('Capture output exists; no duplicate attempt')
    claims=job_root/'capture-attempt-claims';claims.mkdir(exist_ok=True)
    claim=claims/args.model;claim.mkdir() # one model attempt even if another output path is supplied
    output=new_dir(args.output);descriptor=protocol['models'][args.model]
    # Public handler is supplied by the native owner and pinned by the outer protocol.
    handler_spec=descriptor['handler']
    start_record={'status':'running','model':args.model,'phase':job['phase'],'expected_sources':len(sources),
        'job_seal_sha256':file_sha(Path(args.job)/'job-seal.json'),'protocol_sha256':job['protocol_sha256'],
        'handler_sha256':handler_spec['sha256'],'started_at_utc':now(),'single_attempt_per_source':True,
        'capture_driver_sha256':file_sha(Path(__file__))}
    write(output/'started.json',start_record)
    write(claim/'claim.json',{'model':args.model,'job_seal_sha256':file_sha(job_root/'job-seal.json'),'output_path_at_capture':str(output),'claimed_at_utc':now(),'automatic_retries':False})
    module,handler_spec=load_verified_handler(protocol,args.model);handler=getattr(module,handler_spec['callable']);records=[]
    for source in sources:
        folder=output/source['id'];folder.mkdir() # atomic claim BEFORE handler/inference
        write(folder/'request.json',{'source':source,'model':args.model,'protocol_sha256':job['protocol_sha256']})
        started=time.monotonic();value=None;returned=False;return_hash=None
        try:
            value=handler(source=source,model=args.model,protocol=protocol);returned=True
            return_hash=raw_handler_return(folder,value)
            record=validate_handler_record(value,source,args.model,protocol,freeze,job['protocol_sha256'])
        except Exception as exc:
            record={'id':source['id'],'model':args.model,'route_supported':False,'runtime_status':'error','parse_valid':False,
                'truncated':False,'coverage_complete':False,
                'raw_output':value.get('raw_output')if isinstance(value,dict)and isinstance(value.get('raw_output'),str)else None,
                'normalized_evidence':value.get('normalized_evidence')if isinstance(value,dict)and isinstance(value.get('normalized_evidence'),dict)else None,
                'model_calls':value.get('model_calls')if isinstance(value,dict)else None,
                'error':type(exc).__name__+': '+str(exc),'error_policy':'Failure retained; no fabricated empty extraction or automatic retry.'}
        record.update(protocol_sha256=job['protocol_sha256'],seconds=round(time.monotonic()-started,3),
            handler_returned=returned,handler_return_sha256=return_hash)
        write(folder/'capture.json',record);records.append(record)
    write(output/'manifest.json',{**start_record,'status':'completed_capture_attempts','finished_at_utc':now(),
        'completed_records':len(records),'operationally_valid':sum(operational(r)[0]for r in records),
        'started_sha256':file_sha(output/'started.json'),
        'capture_artifact_sha256':{r['id']:file_sha(output/r['id']/'capture.json')for r in records},
        'request_artifact_sha256':{r['id']:file_sha(output/r['id']/'request.json')for r in records},
        'handler_return_artifact_sha256':{r['id']:r['handler_return_sha256']for r in records},
        'diagnostic_artifact_sha256':{r['id']:{p.name:file_sha(p)for p in(output/r['id']).iterdir()if p.name in('handler-return-repr.txt','handler-raw-output.txt')}for r in records}})
    print(json.dumps({'status':'completed_capture_attempts','model':args.model,'records':len(records),'operationally_valid':sum(operational(r)[0]for r in records)}))


def capture_header(root,job_path,job,protocol,model,sources):
    started=read(root/'started.json');manifest=read(root/'manifest.json');ids={row['id']for row in sources}
    expected={'model':model,'phase':job['phase'],'expected_sources':len(sources),'job_seal_sha256':file_sha(Path(job_path)/'job-seal.json'),
              'protocol_sha256':job['protocol_sha256'],'handler_sha256':protocol['models'][model]['handler']['sha256'],'single_attempt_per_source':True}
    if started.get('status')!='running'or manifest.get('status')!='completed_capture_attempts':raise ValueError('Native capture did not complete its declared single attempt')
    if any(started.get(key)!=value or manifest.get(key)!=value for key,value in expected.items()):raise ValueError('Native started/manifest/job/model/handler identity differs')
    if manifest.get('started_sha256')!=file_sha(root/'started.json')or manifest.get('completed_records')!=len(sources):raise ValueError('Native manifest/start/count binding differs')
    if manifest.get('capture_driver_sha256')!=started.get('capture_driver_sha256'):raise ValueError('Native driver identity differs')
    if protocol.get('capture_driver_sha256')is not None and started.get('capture_driver_sha256')!=protocol['capture_driver_sha256']:raise ValueError('Capture driver differs from frozen protocol')
    for key in('capture_artifact_sha256','request_artifact_sha256','handler_return_artifact_sha256'):
        if not isinstance(manifest.get(key),dict)or set(manifest[key])!=ids:raise ValueError('Native artifact manifest coverage differs')
    return manifest


def verified_capture(root,source,model,job,protocol,freeze,manifest,module,handler_spec):
    folder=root/source['id'];capture_path=folder/'capture.json';request_path=folder/'request.json'
    if(file_sha(capture_path)!=manifest['capture_artifact_sha256'][source['id']]
            or file_sha(request_path)!=manifest['request_artifact_sha256'][source['id']]):raise ValueError('Native raw capture/request manifest hash differs')
    expected_request={'source':{key:source[key]for key in('id','passage','condition')},'model':model,'protocol_sha256':job['protocol_sha256']}
    if read(request_path)!=expected_request:raise ValueError('Native request source/model/protocol differs')
    record=read(capture_path)
    if record.get('id')!=source['id']or record.get('model')!=model or record.get('protocol_sha256')!=job['protocol_sha256']:raise ValueError('Native capture source/model/protocol differs')
    return_hash=manifest['handler_return_artifact_sha256'][source['id']]
    if return_hash is not None:
        if file_sha(folder/'handler-return.json')!=return_hash or record.get('handler_return_sha256')!=return_hash:raise ValueError('Native handler return binding differs')
        returned=read(folder/'handler-return.json')
        try:validated=validate_handler_record(returned,source,model,protocol,freeze,job['protocol_sha256'])
        except Exception:
            if(record.get('runtime_status')!='error'or record.get('route_supported')is not False
                    or record.get('parse_valid')is not False or record.get('error_policy')!='Failure retained; no fabricated empty extraction or automatic retry.'):
                raise ValueError('Invalid native return was not retained as an explicit bridge failure')
        else:
            ignore={'id','model','protocol_sha256','seconds','handler_returned','handler_return_sha256'}
            if any(record.get(key)!=value for key,value in validated.items()if key not in ignore):raise ValueError('Saved native claims differ from the original handler return')
    elif record.get('handler_return_sha256')is not None:raise ValueError('Unexpected native handler return hash')
    record=validate_handler_record(record,source,model,protocol,freeze,job['protocol_sha256'])
    valid,_=operational(record)
    if valid:
        if record.get('handler_returned')is not True or return_hash is None:raise ValueError('Operational native output requires its retained original handler return')
        verify=getattr(module,handler_spec.get('verify_callable','verify_normalize_record'),None)
        if not callable(verify):raise ValueError('Frozen native owner has no inert CPU normalization verifier')
        recomputed=verify(source=expected_request['source'],model=model,protocol=protocol,record=record)
        if recomputed!=record['normalized_evidence']:raise ValueError('Saved pipeline claims differ from CPU-recomputed native raw outputs')
    return record


def semantic_view(evidence):
    """Only common semantic claims; no model/provenance/capability identity fields."""
    if not isinstance(evidence,dict):return {}
    edge_limits={'representation','predicate_from_constructor','predicate_cue_spans','predicate_cue_scope',
                 'predicate_argument_association_validated','predicate_cue_validation','event_roles_resolved',
                 'clause_semantics_decomposed','polarity_scope'}
    allowed={'entities':{'id','text','span','candidates','grounding','type','polarity','quantity','answer_roles'},
             'relations':{'predicate','subject','object','polarity','support_span','answer_role'}|edge_limits,
             'events':{'type','predicate','trigger','roles','polarity','support_span','answer_role'}|edge_limits}
    result={}
    if evidence.get('representation')==QUOTE_REPRESENTATION:
        quote_fields={'quote_id','quote','span_candidates','grounding_status'}
        result['representation']=QUOTE_REPRESENTATION
        if isinstance(evidence.get('quotes'),list):
            result['quotes']=[{key:value for key,value in row.items()if key in quote_fields}
                              for row in evidence['quotes']if isinstance(row,dict)]
        for key in('parse_status','rejection_reasons','numeric_count_interpreted'):
            if key in evidence:result[key]=evidence[key]
    for key,fields in allowed.items():
        values=evidence.get(key,[])
        if isinstance(values,list):result[key]=[{k:v for k,v in row.items()if k in fields}for row in values if isinstance(row,dict)]
    if isinstance(evidence.get('properties'),list):
        fields={'subject','predicate','value','polarity','answer_role','source_span','support'}|edge_limits
        result['properties']=[{key:value for key,value in row.items()if key in fields}
                              for row in evidence['properties']if isinstance(row,dict)]
    if isinstance(evidence.get('quantity'),dict):
        result['quantity']={key:value for key,value in evidence['quantity'].items()
                            if key in('kind','lower','upper','source_text','unit','scope','polarity','value','issues','assumptions','coverage_complete')}
    for key in('answer_role','requested_facet_status','context_annotations_present','requested_facet_status_kind',
               'candidate_grounding_status','ambiguity_origins','facet_statuses','status','issues',
               'coverage_validated','semantic_support_validated','resolved_event_role_claims'):
        if key in evidence:result[key]=evidence[key]
    return result


def prepare_reviews(args):
    _,job,protocol,freeze,projected=job_data(args.job)
    sources,gold,gold_seal=load_source_gold(args.sources,args.gold_dir,job['sources'])
    if [{k:s[k]for k in('id','passage','condition')}for s in sources]!=projected or file_sha(args.sources)!=job['source_full_sha256']:raise ValueError('Review source/job identity differs')
    if file_sha(Path(args.gold_dir)/'source-support-seal.json')!=job['source_support_seal_sha256']:raise ValueError('Review gold differs from inference authorization')
    paths={}
    for value in args.captures:
        model,path=value.split('=',1)
        if model in paths:raise ValueError('Duplicate native capture family')
        paths[model]=Path(path)
    if set(paths)!=set(MODELS):raise ValueError('Keep both families in the fixed denominator, even if one failed to capture')
    disputed=set(gold_seal.get('unresolved_reference_disagreement_ids',[]));entries=[]
    capture_headers={};capture_modules={};header_errors={}
    for model in MODELS:
        try:
            capture_headers[model]=capture_header(paths[model],args.job,job,protocol,model,projected)
            capture_modules[model]=load_verified_handler(protocol,model)
        except Exception as exc:header_errors[model]=type(exc).__name__+': '+str(exc)
    for model in MODELS:
        for source,reference in zip(sources,gold):
            path=paths[model]/source['id']/'capture.json';artifact_hash=None
            try:
                if model in header_errors:raise ValueError('Native capture/header/code verification failed: '+header_errors[model])
                module,spec=capture_modules[model]
                record=verified_capture(paths[model],source,model,job,protocol,freeze,capture_headers[model],module,spec);artifact_hash=file_sha(path)
                valid,reason=operational(record)
            except Exception as exc:
                record={'id':source['id'],'model':model,'route_supported':False,'runtime_status':'not_run','parse_valid':False,
                    'truncated':False,'coverage_complete':False,'raw_output':None,'normalized_evidence':None,'error':type(exc).__name__+': '+str(exc)}
                valid,reason=False,'missing_or_invalid_capture_artifact'
            entries.append((model,source,reference,record,valid,reason,artifact_hash))
    seed=protocol.get('evaluation_review_seed','jep-native-repair-evaluation-20261028')
    entries.sort(key=lambda entry:sha(encoded([seed,job['phase'],entry[0],entry[1]['id']])))
    packet=[];mapping=[];operational_rows=[]
    for index,(model,source,reference,record,valid,reason,artifact_hash)in enumerate(entries):
        candidate=f'candidate_{index:05d}'
        mapping.append({'candidate_id':candidate,'model':model,'source_id':source['id'],'group_id':source['group_id'],
            'gold_disputed':source['id']in disputed,'answerability':reference['answerability'],'gold_has_facts':bool(reference['facts']),
            'opportunities':reference['opportunities']})
        operational_rows.append({'candidate_id':candidate,'operational_valid':valid,'operational_failure':reason,
            'route_supported':record.get('route_supported')is True,'runtime_status':record.get('runtime_status'),
            'parse_valid':record.get('parse_valid')is True,'truncated':record.get('truncated'),
            'coverage_complete':record.get('coverage_complete')is True,'capture_sha256':artifact_hash,
            'error':record.get('error',''),'normalized_status':record['normalized_evidence'].get('status')if isinstance(record.get('normalized_evidence'),dict)else None})
        if valid:
            packet.append({'candidate_id':candidate,'passage':source['passage'],'condition':source['condition'],
                'reference':reference,'gold_disputed':source['id']in disputed,'raw_output':record['raw_output'],
                'pipeline_claims':semantic_view(record['normalized_evidence']),'coverage_complete':record['coverage_complete']})
    output=new_dir(args.output)
    write(output/'review-packet.json',packet);write(output/'private-map.json',mapping);write(output/'operational-results.json',operational_rows)
    write(output/'review-seal.json',{'status':'BLINDED_PACKET_SEALED','phase':job['phase'],'protocol_sha256':job['protocol_sha256'],
        'capture_scope':protocol.get('capture_scope','general_frozen_protocol'),
        'experimental_calls_only':protocol.get('capture_scope')=='locked48_diagnostic_only',
        'semantic_qualification_passed':False,'fresh_evaluation_authorized':False,
        'job_seal_sha256':file_sha(Path(args.job)/'job-seal.json'),'source_support_seal_sha256':job['source_support_seal_sha256'],
        'expected_candidates':len(entries),'semantic_review_candidates':len(packet),'operational_failures':len(entries)-len(packet),
        'source_count_per_model':len(sources),'models':list(MODELS),'output_formats_visible':True,'model_identities_in_packet':False,
        'artifacts':{name:file_sha(output/name)for name in('review-packet.json','private-map.json','operational-results.json')}})
    print(json.dumps({'candidates':len(entries),'semantic_review_candidates':len(packet),'operational_failures':len(entries)-len(packet),'review_seal_sha256':file_sha(output/'review-seal.json')}))


def interval(values,seed,iterations=2000):
    if not values:return None
    groups=list(values);rng=random.Random(seed);draws=[]
    for _ in range(iterations):
        selected=[rng.choice(groups)for _ in groups];draws.append(sum(sum(values[g])for g in selected)/sum(len(values[g])for g in selected))
    draws.sort();return[draws[int(.025*iterations)],draws[min(iterations-1,int(.975*iterations))]]


def validate_review_proof(path,packet,packet_sha,review_seal_sha):
    """Require the review file to equal retained fresh, tool-free model responses."""
    base=Path(__file__).parent;engine_path=base/'generate_gold.py'
    engine_sha='67a268503ef4d3839794e73d2599c5c4ec77af442ed1f5e8da23003956295ac4'
    if file_sha(engine_path)!=engine_sha:raise ValueError('Strict review capture engine changed')
    spec=importlib.util.spec_from_file_location('evaluation_proof_engine',engine_path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    root=Path(path).resolve().parent;provenance=read(root/'provenance.json');operator_path=base/'review_native_evaluation.py'
    if (provenance.get('status')!='completed'or provenance.get('packet_sha256')!=packet_sha
            or provenance.get('review_seal_sha256')!=review_seal_sha
            or provenance.get('reviews_sha256')!=file_sha(path)or provenance.get('completed_reviews')!=len(packet)
            or provenance.get('expected_reviews')!=len(packet)or provenance.get('capture_engine_sha256')!=engine_sha
            or provenance.get('review_operator_sha256')!=file_sha(operator_path)
            or provenance.get('model_alias')!=engine.MODEL or provenance.get('reasoning_effort')!='max'):
        raise ValueError('Review completion/provenance/hash/alias differs')
    reviewer=provenance.get('reviewer_id')
    if reviewer not in('model:gpt-6.1-sol:max:native-eval-a','model:gpt-6.1-sol:max:native-eval-b'):raise ValueError('Unrecognized independent evaluator identity')
    order_seed=sha((str(provenance['seed'])+':'+reviewer).encode())
    if order_seed!=provenance['derived_order_seed']:raise ValueError('Review independent order differs')
    ordered=list(packet);random.Random(order_seed).shuffle(ordered)
    properties={'candidate_id':{'type':'string'},'reviewer_id':{'type':'string','enum':[reviewer]},**{field:{'type':'boolean'}for field in CRITERIA},'rationale':{'type':'string'}}
    expected_schema={'type':'object','additionalProperties':False,'properties':{'reviews':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}}},'required':['reviews']}
    # Importing the operator is inert; its prompt bytes are part of the pinned code.
    spec=importlib.util.spec_from_file_location('evaluation_review_prompt',operator_path);operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)
    def command(folder):
        value=[engine.CLI,'--no-daemon','--ask-for-approval','never','exec','--ignore-user-config','--ignore-rules','--ephemeral','--skip-git-repo-check','-C',str(root/'closed-book'),'-s','read-only','-m',engine.MODEL,'-c','model_reasoning_effort="max"','-c','web_search="disabled"']
        for feature in('shell_tool','multi_agent','apps','plugins','memories','skill_search','browser_use','computer_use','image_generation','view_image','sleep_tool','hooks'):value+=['--disable',feature]
        return value+['--json','--color','never','--output-schema',str(folder/'schema.json'),'-o',str(folder/'response.json'),'-']
    collected=[];proofs=[]
    for index,offset in enumerate(range(0,len(ordered),8)):
        items=ordered[offset:offset+8];batch=root/f'batch-{index:03d}';result=read(batch/'batch-result.json')
        if result.get('status')!='completed'or result.get('selected_attempt')not in('attempt-0','recovery-1'):raise ValueError('Incomplete semantic-review batch')
        folder=batch/result['selected_attempt'];audit=read(folder/'audit.json')
        if audit.get('status')!='completed'or type(audit.get('exit_code'))is not int or audit['exit_code']!=0:raise ValueError('Review process was not completed/exit0')
        prompt=operator.PROMPT+'\nREVIEWER_ID: '+json.dumps(reviewer)+'\n\nBLINDED EVALUATION INPUTS:\n'+json.dumps(items,ensure_ascii=False)
        if(folder/'prompt.txt').read_text()!=prompt or read(folder/'schema.json')!=expected_schema or read(folder/'command.json')!=command(folder):raise ValueError('Review source/prompt/schema/model/isolation command differs')
        response=read(folder/'response.json');events=[engine.decode(line)for line in(folder/'events.jsonl').read_text().splitlines()if line.strip()]
        proof=engine.completed(events,response)
        if not isinstance(response,dict)or set(response)!={'reviews'}or[row.get('candidate_id')for row in response['reviews']]!=[row['candidate_id']for row in items]:raise ValueError('Raw semantic response coverage differs')
        for row in response['reviews']:
            if(set(row)!=set(properties)or row.get('reviewer_id')!=reviewer
                    or any(type(row.get(key))is not bool for key in CRITERIA)
                    or not isinstance(row.get('rationale'),str)or not row['rationale'].strip()):raise ValueError('Raw semantic review row contract differs')
        if result['selected_attempt']=='recovery-1':
            original=batch/'attempt-0';receipt=read(batch/'operational-recovery-policy.json');original_audit=read(original/'audit.json')
            original_events,bad=engine.read_event_history(original/'events.jsonl')
            if(bad or not engine.eligible_recovery(original_events,original,original_audit)
                    or receipt.get('maximum_recovery_calls')!=1 or receipt.get('capture_engine_sha256')!=engine_sha
                    or receipt.get('candidate_ids')!=[row['candidate_id']for row in items]
                    or receipt.get('same_prompt_sha256')!=sha(prompt.encode())
                    or receipt.get('original_artifact_sha256')!={p.name:file_sha(p)for p in sorted(original.iterdir())if p.is_file()}
                    or(original/'prompt.txt').read_text()!=prompt or read(original/'schema.json')!=expected_schema
                    or read(original/'command.json')!=command(original)):raise ValueError('Review recovery is not the declared one no-response operational attempt')
        collected.extend(response['reviews']);proofs.append({'batch':index,'attempt':result['selected_attempt'],'closed_book_proof':proof,
            'artifact_sha256':{p.name:file_sha(p)for p in sorted(folder.iterdir())if p.is_file()}})
    by_id={row['candidate_id']:row for row in collected}
    final=[by_id[item['candidate_id']]for item in packet]
    if len(by_id)!=len(collected)or read(path)!=final:raise ValueError('Collected review file differs from raw model proof')
    return {'reviewer_id':reviewer,'provenance_sha256':file_sha(root/'provenance.json'),'review_sha256':file_sha(path),'batch_proofs':proofs}


def summarize(args):
    root=Path(args.review);seal=read(root/'review-seal.json')
    for name,digest in seal['artifacts'].items():
        if file_sha(root/name)!=digest:raise ValueError('Sealed evaluation packet/map/operational result changed')
    packet=read(root/'review-packet.json');mapping=read(root/'private-map.json');ops=read(root/'operational-results.json')
    expected={row['candidate_id']for row in packet};reviews=[];reviewer_ids=[]
    if expected and len(args.reviews)!=2:raise ValueError('Nonempty semantic packet requires two independent review files')
    proof_records=[]
    for path in args.reviews:
        rows=read(path)
        if not isinstance(rows,list)or len(rows)!=len(expected)or{r.get('candidate_id')for r in rows}!=expected:raise ValueError('Review needs exact semantic-packet coverage/no duplicates')
        if not expected:
            reviews.append({});continue
        proof_records.append(validate_review_proof(path,packet,seal['artifacts']['review-packet.json'],file_sha(root/'review-seal.json')))
        ids={r.get('reviewer_id')for r in rows}
        if len(ids)!=1 or not all(ids):raise ValueError('One explicit reviewer identity per independent run')
        reviewer_ids.append(next(iter(ids)));index={}
        for row in rows:
            if any(type(row.get(key))is not bool for key in CRITERIA)or not isinstance(row.get('rationale'),str):raise ValueError('Review criteria/rationale contract differs')
            index[row['candidate_id']]=row
        reviews.append(index)
    if expected and(len(reviews)!=2 or len(set(reviewer_ids))!=2):raise ValueError('Require two independent reviewer identities (same-model limitations remain)')
    by_op={row['candidate_id']:row for row in ops}
    if len(mapping)!=seal['expected_candidates']or len(by_op)!=len(mapping)or{r['candidate_id']for r in mapping}!=set(by_op):raise ValueError('Fixed-denominator coverage differs')
    if (seal['source_count_per_model']!=PHASE_COUNTS[seal['phase']]
            or seal['expected_candidates']!=len(MODELS)*PHASE_COUNTS[seal['phase']]
            or {row['model']for row in mapping}!=set(MODELS)):raise ValueError('Frozen phase/model denominator differs')
    if expected!={identity for identity,row in by_op.items()if row['operational_valid']}:raise ValueError('Semantic packet must include every operationally valid candidate and no failures')
    final=[];models={};agreements=collections.Counter();comparison=collections.defaultdict(list)
    for link in mapping:
        identity=link['candidate_id'];op=by_op[identity];valid=op['operational_valid'];judged=valid and identity in expected
        flags={key:bool(judged and all(review[identity][key]for review in reviews))for key in CRITERIA}
        for key in CRITERIA:
            if judged:agreements[key]+=reviews[0][identity][key]==reviews[1][identity][key]
        accepted=bool(valid and all(flags.values()));disputed=link['gold_disputed']
        lower=int(accepted and not disputed);upper=int(accepted or(valid and disputed))
        correct_empty=bool(valid and not disputed and link['answerability']=='not_specified'and all(flags.values()))
        final.append({**link,**op,'semantic_judgment_performed':judged,'criteria_conjunction':flags,
            'accepted_conjunction':accepted,'accepted_lower':lower,'accepted_upper':upper,'correct_abstention_on_source_absence':correct_empty})
    for model in MODELS:
        rows=[row for row in final if row['model']==model];n=len(rows)
        if n!=seal['source_count_per_model']:raise ValueError('A native family disappeared from the denominator')
        answered=[r for r in rows if r['answerability']!='not_specified'and r['gold_has_facts']]
        negatives=[r for r in rows if r['answerability']=='not_specified']
        binding=[r for r in rows if r['opportunities']['binding']];counts=[r for r in rows if r['opportunities']['multiplicity']]
        criterion_success={key:sum(r['criteria_conjunction'][key]and not r['gold_disputed']for r in rows)for key in CRITERIA}
        groups=collections.defaultdict(list)
        paired_baseline_lower=collections.defaultdict(list);paired_baseline_upper=collections.defaultdict(list)
        for row in rows:
            groups[row['group_id']].append(row['accepted_lower'])
            baseline_lower=int(row['answerability']=='not_specified'and not row['gold_disputed'])
            baseline_upper=int(bool(baseline_lower)or row['gold_disputed'])
            paired_baseline_lower[row['group_id']].append(row['accepted_lower']-baseline_upper)
            paired_baseline_upper[row['group_id']].append(row['accepted_upper']-baseline_lower)
        models[model]={'expected':n,'operationally_valid':sum(r['operational_valid']for r in rows),
            'route_supported':sum(r['route_supported']for r in rows),'structurally_valid':sum(r['parse_valid']for r in rows),
            'operational_failure_counts':dict(collections.Counter(r['operational_failure']for r in rows if not r['operational_valid'])),
            'accepted':sum(r['accepted_lower']for r in rows),'accepted_upper':sum(r['accepted_upper']for r in rows),
            'acceptance_fraction_lower':sum(r['accepted_lower']for r in rows)/n,'acceptance_fraction_upper':sum(r['accepted_upper']for r in rows)/n,
            'criterion_success_fixed_denominator':criterion_success,'criterion_success_fraction_fixed_denominator':{k:v/n for k,v in criterion_success.items()},
            'answerable_cases':len(answered),'answerable_complete_successes':sum(r['criteria_conjunction']['complete']and not r['gold_disputed']for r in answered),
            'answerable_complete_fraction':sum(r['criteria_conjunction']['complete']and not r['gold_disputed']for r in answered)/len(answered)if answered else None,
            'answerable_completeness_metric_scope':'Completeness diagnostic alone; unsupported claims or binding failures can coexist. Use joint all-criteria acceptance for supported-evidence quality.',
            'answerable_accepted_lower':sum(r['accepted_lower']for r in answered),
            'answerable_accepted_upper':sum(r['accepted_upper']for r in answered),
            'answerable_acceptance_fraction_lower':sum(r['accepted_lower']for r in answered)/len(answered)if answered else None,
            'answerable_acceptance_fraction_upper':sum(r['accepted_upper']for r in answered)/len(answered)if answered else None,
            'source_absence_cases':len(negatives),'correct_negative_abstentions':sum(r['correct_abstention_on_source_absence']for r in negatives),
            'correct_negative_abstention_fraction':sum(r['correct_abstention_on_source_absence']for r in negatives)/len(negatives)if negatives else None,
            'binding_opportunities':len(binding),
            'binding_judged_violations':sum(r['semantic_judgment_performed']and not r['gold_disputed']and not r['criteria_conjunction']['binding_correct']for r in binding),
            'binding_operationally_unverified':sum(not r['operational_valid']for r in binding),
            'binding_gold_disputed':sum(r['operational_valid']and r['gold_disputed']for r in binding),
            'binding_confirmed_success':sum(r['operational_valid']and not r['gold_disputed']and r['criteria_conjunction']['binding_correct']for r in binding),
            'multiplicity_opportunities':len(counts),
            'multiplicity_judged_violations':sum(r['semantic_judgment_performed']and not r['gold_disputed']and not r['criteria_conjunction']['multiplicity_correct']for r in counts),
            'multiplicity_operationally_unverified':sum(not r['operational_valid']for r in counts),
            'multiplicity_gold_disputed':sum(r['operational_valid']and r['gold_disputed']for r in counts),
            'multiplicity_confirmed_success':sum(r['operational_valid']and not r['gold_disputed']and r['criteria_conjunction']['multiplicity_correct']for r in counts),
            'disputed_gold_cases':sum(r['gold_disputed']for r in rows),'component_bootstrap_95ci_lower_acceptance':interval(groups,20261028),
            'always_abstain_supported_coverage':0.0,'always_abstain_acceptance_proxy':sum(r['answerability']=='not_specified'and not r['gold_disputed']for r in rows)/n,
            'paired_mean_vs_always_abstain_lower':sum(sum(values)for values in paired_baseline_lower.values())/n,
            'paired_mean_vs_always_abstain_upper':sum(sum(values)for values in paired_baseline_upper.values())/n,
            'paired_component_95ci_vs_always_abstain_lower_endpoint':interval(paired_baseline_lower,20261028),
            'paired_component_95ci_vs_always_abstain_upper_endpoint':interval(paired_baseline_upper,20261028)}
    judged_n=len(packet)
    observed_all_pass=all(models[model]['accepted']==PHASE_COUNTS['locked-canaries']for model in MODELS)if seal['phase']=='locked-canaries'else False
    diagnostic=seal.get('capture_scope')=='locked48_diagnostic_only'
    all_pass=observed_all_pass and not diagnostic
    output=new_dir(args.output);write(output/'candidate-results.json',final)
    write(output/'semantic-review-proof-index.json',proof_records)
    report={'phase':seal['phase'],'protocol_sha256':seal['protocol_sha256'],'source_support_seal_sha256':seal['source_support_seal_sha256'],
        'capture_scope':seal.get('capture_scope','general_frozen_protocol'),'experimental_calls_only':diagnostic,
        'complete_evaluation':True,'observed_all_criteria_canaries_pass':observed_all_pass,
        'all_integration_canaries_pass':all_pass,'semantic_qualification_passed':all_pass,
        'fresh_evaluation_authorized':all_pass,'models':models,
        'method':'Model-assisted, two independent contexts/reviewer identities; same model alias/reference anchoring remain. No human accuracy claim.'if judged_n else'No semantic judging was performed: every frozen candidate failed an operational gate; all remain denominator failures.',
        'semantic_review_candidates':judged_n,'prior_adapter_on_same_fresh_cohort':'Not measured by this report; do not treat old exposed-cohort scores as a paired comparison.',
        'reviewer_ids':reviewer_ids,'review_sha256':[file_sha(path)for path in args.reviews],
        'per_criterion_reviewer_agreement':{key:agreements[key]/judged_n if judged_n else None for key in CRITERIA},
        'gold_disagreement_policy':'Keep fixed-denominator lower/upper bounds; no silent gold replacement.',
        'metric_scope':'Operational failures stay denominator failures; semantic-error details are evaluated only for operationally valid outputs. Negative abstention never includes unsupported routes or capture/parser errors.',
        'validity_is_not_fidelity':True,'engineering_targets':{'support_coverage':0.90,'negative_abstention':0.90,'paper_standard':False},
        'statistical_scope':('Fixed diagnostic suite/component resampling stability only; no representative population accuracy interval or model ranking.'if diagnostic else'Component bootstrap on the declared cohort; generalization depends on its stated sampling design.'),
        'created_at_utc':now(),'review_seal_sha256':file_sha(root/'review-seal.json'),'evaluator_sha256':file_sha(Path(__file__))}
    write(output/'summary.json',report)
    if seal['phase']=='locked-canaries'and not diagnostic:write(output/'integration-gate-seal.json',report)
    print(json.dumps({'phase':seal['phase'],'models':{model:{key:models[model][key]for key in('expected','operationally_valid','accepted','accepted_upper')}for model in MODELS},'all_integration_canaries_pass':all_pass}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    command=commands.add_parser('verify-provider');command.add_argument('--protocol',type=Path,required=True);command.add_argument('--model',choices=MODELS,required=True)
    command=commands.add_parser('prepare-job');command.add_argument('--phase',choices=PHASE_COUNTS,required=True)
    for key in('sources','gold-dir','protocol','compiler-freeze','output'):command.add_argument('--'+key,type=Path,required=True)
    command.add_argument('--integration-gate',type=Path)
    command=commands.add_parser('run-capture');command.add_argument('--job',type=Path,required=True);command.add_argument('--model',choices=MODELS,required=True);command.add_argument('--output',type=Path,required=True)
    command=commands.add_parser('prepare-reviews')
    for key in('job','sources','gold-dir','output'):command.add_argument('--'+key,type=Path,required=True)
    command.add_argument('--captures',nargs=2,required=True,help='gollie=DIR knowcoder=DIR; missing artifacts remain failures')
    command=commands.add_parser('summarize');command.add_argument('--review',type=Path,required=True);command.add_argument('--reviews',type=Path,nargs='*',default=[]);command.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();{'verify-provider':verify_provider,'prepare-job':prepare_job,'run-capture':run_capture,'prepare-reviews':prepare_reviews,'summarize':summarize}[args.command](args)


if __name__=='__main__':
    try:main()
    except Exception as exc:print(type(exc).__name__+': '+str(exc),file=sys.stderr);sys.exit(1)
