"""Capture the frozen three-format batch study, with one attempt per batch."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time
from typing import Any
from schema_contract import parse_payload, canonical_text

ARMS={'gpt_propositions':'propositions','gpt_json':'json','gpt_python':'python'}
WARNING=re.compile(r'Reconnecting\.\.\. [1-5]/5 \((?:request timed out|stream disconnected before completion: invalid peer certificate: UnknownIssuer|exceeded retry limit, last status: 429 Too Many Requests(?:, request id: [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})?|workspace routing discovery timed out)\)')

def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def json_bytes(value):
 return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def decode(text):
 def pairs(items):
  out={}
  for key,value in items:
   if key in out:raise ValueError('Duplicate JSON key')
   out[key]=value
  return out
 def invalid(value):raise ValueError('Nonfinite JSON constant: '+value)
 return json.loads(text,object_pairs_hook=pairs,parse_constant=invalid)
def read(path):return decode(Path(path).read_text())
def write_new(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as out:out.write(json_bytes(value))
def atomic_write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp');tmp.write_bytes(json_bytes(value));tmp.replace(path)
def safe_path(root,name):
 path=(root/name).resolve()
 if not path.is_relative_to(root.resolve()):raise ValueError('Input path escapes the frozen study')
 return path

def envelope_schema(ids):
 if not ids or len(ids)!=len(set(ids)):raise ValueError('Unique source IDs required')
 item={'type':'object','properties':{'payload':{'type':'string'}},'required':['payload'],'additionalProperties':False}
 return {'type':'object','properties':{'records':{'type':'object','properties':{i:item for i in ids},'required':list(ids),'additionalProperties':False}},'required':['records'],'additionalProperties':False}
def validate_envelope(response,ids):
 if not isinstance(response,dict) or set(response)!={'records'} or not isinstance(response['records'],dict) or set(response['records'])!=set(ids):raise ValueError('Batch response must cover exactly its source IDs')
 for value in response['records'].values():
  if not isinstance(value,dict) or set(value)!={'payload'} or not isinstance(value['payload'],str):raise ValueError('Each source requires exactly one string payload')
 return response['records']
def completed_batch(events,response,ids):
 validate_envelope(response,ids)
 if sum(isinstance(e,dict) and e.get('type')=='thread.started' for e in events)!=1 or sum(isinstance(e,dict) and e.get('type')=='turn.started' for e in events)!=1:raise ValueError('Expected exactly one thread and turn')
 answers=[];completed=0
 for index,event in enumerate(events):
  if not isinstance(event,dict):raise ValueError('Malformed event')
  kind=event.get('type')
  if kind not in {'thread.started','turn.started','item.started','item.updated','item.completed','error','turn.failed','turn.completed'}:raise ValueError('Unknown event type')
  if kind=='turn.failed':raise ValueError('Failed model turn')
  if kind=='error' and (set(event)!={'type','message'} or not isinstance(event['message'],str) or not WARNING.fullmatch(event['message'])):raise ValueError('Unrecognized inference error')
  if kind=='turn.completed':
   completed+=1
   if index!=len(events)-1:raise ValueError('Completion must be final event')
  item=event.get('item',{})
  if not isinstance(item,dict) or item.get('type') not in {None,'reasoning','agent_message'}:raise ValueError('Closed-book tool violation')
  if kind=='item.completed' and item.get('type')=='agent_message':
   if not isinstance(item.get('text'),str):raise ValueError('Missing final answer')
   answers.append(decode(item['text']))
 if completed!=1 or len(answers)!=1 or answers[0]!=response:raise ValueError('Final completion/response agreement failed')
 return response['records']
def source_rows(job,items,records=None,error=None):
 rows=[]
 for item in items:
  row={'arm':job['arm'],'id':item['id'],'job_id':job['id'],'batch_id':job['batch_id'],'valid':False,'original_valid':False,'amended_valid':False,'parsed':None,'status':'invalid','canonical_text':'','payload_sha256':None}
  try:
   if error:raise ValueError(error)
   payload=records[item['id']]['payload']
   if len(payload.encode())>65536:raise ValueError('Per-source payload exceeds 65536 bytes')
   if ARMS[job['arm']]!='python':decode(payload)
   parsed=parse_payload(payload,ARMS[job['arm']],item['passage'])
   row.update(valid=True,original_valid=True,amended_valid=True,parsed=parsed,status=parsed['status'],canonical_text=canonical_text(parsed),payload_sha256=hashlib.sha256(payload.encode()).hexdigest())
  except (ValueError,TypeError,KeyError,RecursionError) as exc:row['error']=str(exc)
  rows.append(row)
 return rows

def load_plan(root,seal_path,ca_file,ca_proof,workers=4):
 root=Path(root).resolve();seal=read(seal_path);files=seal.get('files',seal.get('artifacts',{}))
 for name,expected in files.items():
  if digest(safe_path(root,name))!=expected:raise ValueError('Frozen file changed: '+name)
 for name in ['sources.json','jobs.json','protocol.json']:
  if name not in files:raise ValueError('Seal omits '+name)
 if digest(Path(__file__))!=seal['code_sha256'] or digest(Path(__file__).with_name('schema_contract.py'))!=seal['schema_contract_sha256']:raise ValueError('Runtime code changed after sealing')
 if digest(ca_file)!=seal['ca_sha256'] or digest(ca_proof)!=seal['ca_proof_sha256']:raise ValueError('CA proof identity differs')
 proof=read(ca_proof)
 if proof.get('valid') is not True or proof.get('warnings') or proof.get('ca_sha256')!=seal['ca_sha256']:raise ValueError('Verified zero-warning CA proof required')
 sources=read(root/'sources.json');by_id={s['id']:s for s in sources}
 if len(by_id)!=len(sources):raise ValueError('Duplicate source ID')
 for item in sources:
  if set(item)!={'id','passage','condition'} or any(not isinstance(v,str) or not v.strip() for v in item.values()):raise ValueError('Only source ID, passage and condition are allowed')
 jobs=read(root/'jobs.json');protocol=read(root/'protocol.json');cfg=protocol.get('generator',protocol.get('config',protocol))
 if cfg.get('model')!='gpt-6.1-sol' or cfg.get('reasoning_effort')!='max':raise ValueError('The matched study requires GPT-6.1-sol/max')
 if type(workers) is not int or not 1<=workers<=8:raise ValueError('Invalid total worker count')
 cfg=dict(cfg);cfg['workers']=workers
 ids=set();coverage={a:[] for a in ARMS}
 for job in jobs:
  if job['id'] in ids or job['arm'] not in ARMS:raise ValueError('Duplicate job or unknown arm')
  ids.add(job['id']);expected=job['source_ids']
  if not expected or len(expected)>16 or len(expected)!=len(set(expected)) or not set(expected)<=set(by_id):raise ValueError('Invalid source coverage')
  coverage[job['arm']].extend(expected)
  for key in ['prompt_file','schema_file']:
   if job[key] not in files:raise ValueError('Unsealed job input')
  if read(safe_path(root,job['schema_file']))!=envelope_schema(expected):raise ValueError('Schema differs from exact source envelope')
 for arm,values in coverage.items():
  if len(values)!=len(set(values)) or set(values)!=set(by_id):raise ValueError('Each arm must cover every source exactly once')
 return root,seal,by_id,jobs,cfg

def build_request(root,job,by_id):
 return {'job_id':job['id'],'batch_id':job['batch_id'],'arm':job['arm'],'source_ids':job['source_ids'],'items':[by_id[i] for i in job['source_ids']],'protocol_sha256':digest(root/'protocol.json'),'prompt_sha256':digest(safe_path(root,job['prompt_file'])),'schema_sha256':digest(safe_path(root,job['schema_file']))}
def capture_one(root,job,by_id,cfg,cli,ca_file,seal):
 folder=root/'captures'/job['id'];folder.mkdir(parents=True,exist_ok=False)
 request=build_request(root,job,by_id);write_new(folder/'request.json',request)
 (folder/'prompt.txt').write_bytes(safe_path(root,job['prompt_file']).read_bytes());(folder/'schema.json').write_bytes(safe_path(root,job['schema_file']).read_bytes())
 closed=folder/'closed_book';closed.mkdir()
 command=[str(cli),'--ask-for-approval','never','exec','--ephemeral','--skip-git-repo-check','--ignore-user-config','--sandbox','read-only','--cd',str(closed),'--model',cfg['model'],'-c','model_reasoning_effort="max"','--json','--color','never','--output-schema',str(folder/'schema.json'),'--output-last-message',str(folder/'response.json'),'-']
 write_new(folder/'command.json',command)
 env=os.environ.copy();env.update(CODEX_CA_CERTIFICATE=str(ca_file),SSL_CERT_FILE=str(ca_file))
 started=time.time();error=None;records=None;events=[]
 runtime={'requested_model':cfg['model'],'reasoning_effort':'max','transport':'default_shared_daemon','no_daemon_flag':False,'ca_sha256':seal['ca_sha256'],'code_sha256':digest(Path(__file__)),'schema_contract_sha256':seal['schema_contract_sha256'],'provider_output_token_cap':None,'started_unix':started}
 try:
  version=subprocess.run([str(cli),'--version'],capture_output=True,text=True,check=True,timeout=20)
  runtime['cli_version']=version.stdout.strip();write_new(folder/'runtime.json',runtime)
  with (folder/'events.jsonl').open('x') as out,(folder/'stderr.log').open('x') as err:
   process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,env=env,start_new_session=True)
   try:process.communicate((folder/'prompt.txt').read_text(),timeout=cfg.get('timeout_seconds',1200))
   except subprocess.TimeoutExpired:
    os.killpg(process.pid,signal.SIGTERM)
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    raise ValueError('Batch timeout; retained without retry')
  if process.returncode:raise ValueError('Codex returned nonzero: '+str(process.returncode))
  events=[decode(line) for line in (folder/'events.jsonl').read_text().splitlines() if line.strip()]
  if (folder/'response.json').stat().st_size>cfg.get('max_batch_bytes',1048576):raise ValueError('Batch response exceeds retained byte ceiling')
  records=completed_batch(events,read(folder/'response.json'),job['source_ids'])
 except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as exc:error=str(exc)
 if not events and (folder/'events.jsonl').exists():
  for line in (folder/'events.jsonl').read_text().splitlines():
   if not line.strip():continue
   try:
    event=decode(line)
    if isinstance(event,dict):events.append(event)
   except ValueError:pass  # Original malformed bytes remain in immutable raw log.
 rows=source_rows(job,request['items'],records,error)
 raw={p.name:digest(p) for p in folder.iterdir() if p.is_file() and p.name!='result.json'}
 result={'job_id':job['id'],'arm':job['arm'],'batch_id':job['batch_id'],'started_unix':started,'finished_unix':time.time(),'elapsed_seconds':time.time()-started,'batch_transport_valid':error is None,'error':error,'records':rows,'raw_artifacts':raw,'warnings':[e.get('message') for e in events if e.get('type')=='error'],'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed']}
 write_new(folder/'result.json',result)
 return result

def aggregate(root,jobs,finished=False):
 rows=[];counts={a:{'sources':0,'valid':0,'failed':0,'batches':0} for a in ARMS}
 for job in jobs:
  folder=root/'captures'/job['id'];path=folder/'result.json'
  if not path.exists():continue
  try:result=read(path)
  except (OSError,ValueError):continue
  counts[job['arm']]['batches']+=1
  for row in result['records']:
   value=dict(row);value.update(result_sha256=digest(path),capture_path=str(folder),request_sha256=digest(folder/'request.json'),response_sha256=digest(folder/'response.json') if (folder/'response.json').exists() else None,raw_artifacts=result['raw_artifacts'],warnings=result['warnings'])
   rows.append(value);counts[job['arm']]['sources']+=1;counts[job['arm']]['valid']+=int(row['valid']);counts[job['arm']]['failed']+=int(not row['valid'])
 summary={'status':'complete' if finished else 'running','checked_unix':time.time(),'arms':counts,'completed_jobs':sum(v['batches'] for v in counts.values()),'expected_jobs':len(jobs),'additional_attempts':0}
 atomic_write(root/'progress.json',summary)
 if finished:
  if len(rows)!=sum(len(j['source_ids']) for j in jobs):raise ValueError('Final source coverage incomplete')
  atomic_write(root/'derived/records.json',rows);atomic_write(root/'derived/summary.json',summary)
 return summary

def run(root,seal_path,ca_file,ca_proof,cli,execute=False,workers=4,publication_hook=None):
 root,seal,by_id,jobs,cfg=load_plan(root,seal_path,ca_file,ca_proof,workers)
 if not execute:return {'execute':False,'jobs':len(jobs),'sources_per_arm':len(by_id),'workers_total':cfg['workers'],'transport':'default_shared_daemon'}
 (root/'controller.claim').mkdir(exist_ok=False)
 pending=[]
 for job in jobs:
  folder=root/'captures'/job['id']
  if folder.exists():
   if not (folder/'result.json').exists() or read(folder/'request.json')!=build_request(root,job,by_id):raise ValueError('Incomplete or changed prior capture; no hidden retry')
  else:pending.append(job)
 write_new(root/'execution.json',{'started_unix':time.time(),'pid':os.getpid(),'pending_jobs':len(pending),'jobs':len(jobs),'workers_total':cfg['workers'],'seal_sha256':digest(seal_path),'ca_sha256':seal['ca_sha256'],'protocol_sha256':digest(root/'protocol.json'),'retry_policy':'none'})
 lock=threading.Lock()
 def worker(job):
  capture_one(root,job,by_id,cfg,cli,ca_file,seal)
  if publication_hook is not None:
   try:
    queued=subprocess.run([sys.executable,str(publication_hook),'enqueue-batch','--root',str(root),'--capture-dir',str(root/'captures'/job['id'])],capture_output=True,text=True,timeout=5)
    if queued.returncode:raise RuntimeError('Publication enqueue exit '+str(queued.returncode))
   except (OSError,RuntimeError,subprocess.SubprocessError) as exc:
    atomic_write(root/'publication_errors'/(job['id']+'.json'),{'job_id':job['id'],'error_type':type(exc).__name__,'error':str(exc),'generation_continues':True,'checked_unix':time.time()})
  with lock:aggregate(root,jobs)
 with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
  for _ in pool.map(worker,pending):pass
 return aggregate(root,jobs,finished=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--seal',type=Path);p.add_argument('--cli',type=Path,required=True);p.add_argument('--ca-file',type=Path,required=True);p.add_argument('--ca-proof',type=Path,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--publication-hook',type=Path);p.add_argument('--execute',action='store_true');a=p.parse_args()
 print(json.dumps(run(a.root,a.seal or a.root/'runtime_seal.json',a.ca_file,a.ca_proof,a.cli,a.execute,a.workers,a.publication_hook),indent=2),flush=True)
if __name__=='__main__':main()
