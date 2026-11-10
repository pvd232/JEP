"""Pinned Qwen adapter inference. Local shards first; one terminal transfer."""
import contextlib,datetime as dt,hashlib,json,os,subprocess,sys,tarfile,time,traceback,urllib.request,urllib.parse
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModel,AutoTokenizer,AutoModelForCausalLM
from peft import LoraConfig,TaskType,get_peft_model
R=Path("/var/lib/jep-moral-pilot");R.mkdir(parents=True,exist_ok=True)
C=json.loads((R/"payload.json").read_text())
START=time.monotonic();END=min(START+6000,dt.datetime(2026,11,10,13,tzinfo=dt.timezone.utc).timestamp()-time.time()+START)
torch.set_num_threads(4)
def digest(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def save(p,x):
 p=Path(p);t=p.with_suffix(".tmp");t.write_text(json.dumps(x,indent=2)+"\n");t.replace(p)
def check():
 if time.monotonic()>=END:raise TimeoutError("bounded GPU compute deadline")
def credential():
 q=urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",headers={"Metadata-Flavor":"Google"})
 return json.load(urllib.request.urlopen(q,timeout=10))["access_token"]
def get(uri):
 b,n=uri[5:].split("/",1);url="https://storage.googleapis.com/storage/v1/b/"+b+"/o/"+urllib.parse.quote(n,safe="")+"?alt=media"
 return urllib.request.urlopen(urllib.request.Request(url,headers={"Authorization":"Bearer "+credential()}),timeout=60)
def put(path,name):
 # Internal return transport; provenance publication is a separate CPU VIPER job.
 token=credential();url="https://storage.googleapis.com/upload/storage/v1/b/"+C["bucket"]+"/o?uploadType=media&name="+urllib.parse.quote(name,safe="")
 import requests
 with Path(path).open("rb") as body:
  res=requests.post(url,data=body,headers={"Authorization":"Bearer "+token,"Content-Type":"application/octet-stream"},timeout=(20,120))
 res.raise_for_status();return res.json()
def load_cached(path,key,rows):
 if not path.exists():return None
 data=np.load(path)
 assert str(data["cache_key"])==key
 vectors=data["vectors"]
 assert vectors.shape==(rows,4096) and np.isfinite(vectors).all() and np.allclose(np.linalg.norm(vectors,axis=1),1,atol=2e-5)
 return data
def save_cached(path,key,vectors,extra):
 temp=path.with_suffix(".tmp.npz")
 np.savez(temp,vectors=vectors,cache_key=key,**extra)
 temp.replace(path)

def reasoning_views():
 """Use released MET-D weights with forced grounds; this is not full MET selection/distillation."""
 identity=C.get("met_reasoner")
 if not identity:return []
 path=R/"reasoning_views.json"
 views=[]
 if path.exists():
  prior=json.loads(path.read_text());views=prior["views"]
  if prior.get("status")=="complete":return views
 completed={(x["family"],x["theory"]) for x in views}
 started=time.monotonic()
 try:
  tokenizer=AutoTokenizer.from_pretrained(identity["model"],revision=identity["revision"])
  reasoner=AutoModelForCausalLM.from_pretrained(identity["model"],revision=identity["revision"],dtype=torch.bfloat16,device_map={"":"cuda"},attn_implementation="sdpa",trust_remote_code=False).eval()
  for row in C.get("extension_cases",[]):
   if row["type"]!="harm" or row["theory"]=="restorative_aspect":continue
   if (row["family"],row["theory"]) in completed:continue
   check()
   message="Situation: "+row["text"]+"\nGrounds: reason-based authority; care/harm value; "+row["condition"]+" Use the assigned theory consistently. Explain the mechanism and ethically relevant features of the harm in at most sixty words. Do not give a final verdict, score, action recommendation, or theory label."
   prompt=tokenizer.apply_chat_template([{"role":"user","content":message}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
   inputs=tokenizer(prompt,return_tensors="pt").to("cuda")
   with torch.inference_mode():
    output=reasoner.generate(**inputs,max_new_tokens=96,do_sample=False,pad_token_id=tokenizer.eos_token_id)
   text=tokenizer.decode(output[0,inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()
   views.append(dict(family=row["family"],theory=row["theory"],condition=row["condition"],source_key=row["key"],view=text,new_tokens=int(output.shape[1]-inputs["input_ids"].shape[1]),truncated=int(output.shape[1]-inputs["input_ids"].shape[1])>=96))
   save(path,dict(status="running",model=identity,views=views,seconds=time.monotonic()-started))
  del reasoner
  import gc;gc.collect();torch.cuda.empty_cache()
  save(path,dict(status="complete",model=identity,views=views,seconds=time.monotonic()-started))
 except Exception as error:
  save(path,dict(status="partial_or_unavailable",model=identity,views=views,error=repr(error),seconds=time.monotonic()-started))
  if "reasoner" in locals():del reasoner
  import gc;gc.collect();torch.cuda.empty_cache()
 return views

def run():
 check()
 subprocess.run([sys.executable,__file__,"--reasoning-only"],check=True,timeout=600)
 views=json.loads((R/"reasoning_views.json").read_text())["views"]
 import gc;gc.collect();torch.cuda.empty_cache()
 print("CUDA_AFTER_REASONER",torch.cuda.memory_allocated(),flush=True)
 selection=C["selection"];target=R/"adapter.pt"
 if not target.exists():
  with get(C["archive"]["uri"]) as response,tarfile.open(fileobj=response,mode="r|") as archive:
   for item in archive:
    check()
    if not item.isfile() or not item.name.endswith("/model.pt"):continue
    temp=R/"adapter.partial";h=hashlib.sha256()
    with archive.extractfile(item) as src,temp.open("wb") as dst:
     for block in iter(lambda:src.read(4*1024*1024),b""):
      check();h.update(block);dst.write(block)
    if h.hexdigest()==selection["model_sha256"]:temp.replace(target);break
    temp.unlink()
 assert digest(target)==selection["model_sha256"]
 checkpoint=torch.load(target,map_location="cpu",weights_only=False)
 cfg=checkpoint["config"]
 assert cfg["model_id"]==C["encoder"]["model"] and cfg["revision"]==C["encoder"]["revision"] and cfg["trial_id"]==selection["trial_id"]
 weights=checkpoint["state_dict"] if "state_dict" in checkpoint else checkpoint.get("parameters",checkpoint.get("state"))
 if weights is None:
  raise ValueError("Unknown checkpoint weights schema: "+str(list(checkpoint)))
 tokenizer=AutoTokenizer.from_pretrained(C["encoder"]["model"],revision=C["encoder"]["revision"],padding_side="left")
 model=AutoModel.from_pretrained(C["encoder"]["model"],revision=C["encoder"]["revision"],dtype=torch.bfloat16,attn_implementation="sdpa",device_map={"":"cuda"},trust_remote_code=False)
 model.config.use_cache=False
 model=get_peft_model(model,LoraConfig(task_type=TaskType.FEATURE_EXTRACTION,r=32,lora_alpha=32,lora_dropout=.05,target_modules=["q_proj","k_proj","v_proj","o_proj"],bias="none"))
 trainable={n:p for n,p in model.named_parameters() if p.requires_grad}
 if set(trainable)!=set(weights):raise ValueError("Adapter parameter names differ: "+str((len(trainable),len(weights),list(weights)[:2])))
 with torch.no_grad():
  for n,p in trainable.items():
   value=weights[n]
   if value.shape!=p.shape or not torch.isfinite(value).all():raise ValueError("Bad saved adapter tensor "+n)
   p.copy_(value.to(device=p.device,dtype=p.dtype))
 model.eval()
 eod=tokenizer.convert_tokens_to_ids("<|endoftext|>");tasks=list(C["tasks"]);vectors=[];keys=[]
 generated=[]
 for row in views:
  if not row["view"]:continue
  text=row["view"]
  prompt=cfg["prompt_template"].format(passage=text,condition=row["condition"])
  # This bound applies only to a generated auxiliary view; original inputs never truncate.
  ids=tokenizer(text,add_special_tokens=False)["input_ids"]
  while len(tokenizer(prompt,add_special_tokens=False)["input_ids"])+1>160 and ids:
   ids=ids[:-1];text=tokenizer.decode(ids);prompt=cfg["prompt_template"].format(passage=text,condition=row["condition"])
  key=hashlib.sha256(prompt.encode()).hexdigest()
  tasks.append(dict(key=key,prompt=prompt,layers=True))
  generated.append(dict(row,key=key,used_view=text,view_was_shortened=text!=row["view"]))
 save(R/"generated_tasks.json",generated)
 captured={};layer_keys=[];layer_vectors={k:[] for k in [0,9,18,27,36]};active=[False]
 def hook(label):
  def record(module,args,out):
   if not active[0]:return
   tensor=out[0] if isinstance(out,tuple) else out
   captured[label]=torch.nn.functional.normalize(tensor[:,-1,:].detach().float(),dim=-1).cpu().numpy()
  return record
 base=model.base_model.model
 handles=[base.embed_tokens.register_forward_hook(hook(0))]
 for layer in [9,18,27]:handles.append(base.layers[layer-1].register_forward_hook(hook(layer)))
 shardroot=R/"shards";shardroot.mkdir(exist_ok=True)
 identity=hashlib.sha256(json.dumps(C["encoder"],sort_keys=True).encode()).hexdigest()
 for start in range(0,len(tasks),4):
  check();chunk=tasks[start:start+4];p=shardroot/(str(start)+".npz")
  key=hashlib.sha256((identity+json.dumps(chunk,sort_keys=True)).encode()).hexdigest()
  data=load_cached(p,key,len(chunk))
  if data is not None:
   v=data["vectors"]
   if any(x.get("layers") for x in chunk):
    for label in [0,9,18,27,36]:captured[label]=data["layer_"+str(label)]
  else:
   seqs=[tokenizer(x["prompt"],add_special_tokens=False,truncation=False)["input_ids"]+[eod] for x in chunk]
   assert max(map(len,seqs))<=160
   batch=tokenizer.pad({"input_ids":seqs,"attention_mask":[[1]*len(s) for s in seqs]},padding=True,return_tensors="pt").to("cuda")
   active[0]=any(x.get("layers") for x in chunk)
   captured.clear()
   with torch.inference_mode(),torch.autocast("cuda",dtype=torch.bfloat16):
    hidden=model(**batch).last_hidden_state
   positions=torch.arange(hidden.shape[1],device="cuda").expand(len(hidden),-1)
   last=positions.masked_fill(~batch["attention_mask"].bool(),-1).max(1).values
   pooled=hidden[torch.arange(len(hidden),device="cuda"),last].float()
   v=torch.nn.functional.normalize(pooled,dim=-1).cpu().numpy()
   assert v.shape==(len(chunk),4096) and np.isfinite(v).all() and np.allclose(np.linalg.norm(v,axis=1),1,atol=2e-5)
   captured[36]=v
   extra={("layer_"+str(label)):captured[label] for label in [0,9,18,27,36]} if active[0] else {}
   save_cached(p,key,v,extra)
   if start==0:save(R/"tiny_e2e.json",dict(self_score=float(np.dot(v[0],v[0])),pair_score=float(np.dot(v[0],v[-1])),finite=bool(np.isfinite(v).all()),encoder=C["encoder"]))
  if any(x.get("layers") for x in chunk):
   ix=[i for i,x in enumerate(chunk) if x.get("layers")]
   layer_keys.extend(chunk[i]["key"] for i in ix)
   for label in [0,9,18,27,36]:layer_vectors[label].append(captured[label][ix])
  vectors.append(v);keys.extend(x["key"] for x in chunk)
  if start%100==0:
   save(R/"progress.json",dict(completed=start+len(chunk),total=len(tasks),elapsed=time.monotonic()-START,encoder=C["encoder"]))
   print("INFERENCE",start+len(chunk),len(tasks),flush=True)
 np.savez(R/"embeddings.npz",keys=np.array(keys),vectors=np.concatenate(vectors))
 if layer_keys:np.savez(R/"layers.npz",keys=np.array(layer_keys),**{("layer_"+str(k)):np.concatenate(v) for k,v in layer_vectors.items()})
 save(R/"compute.json",dict(status="complete",source_sha256=digest(__file__),tasks=len(tasks),seconds=time.monotonic()-START,encoder=C["encoder"],gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name,uuid","--format=csv,noheader"],text=True).strip(),torch=torch.__version__))
if __name__=="__main__":
 if "--reasoning-only" in sys.argv:
  reasoning_views();sys.exit(0)
 try:run()
 except BaseException as e:
  save(R/"compute.json",dict(status="failed",source_sha256=digest(__file__),encoder=C["encoder"],error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-START))
  traceback.print_exc()
 finally:
  # Always preserve completed shards and failures, even if full inference failed.
  names=["compute.json","progress.json","embeddings.npz","layers.npz","reasoning_views.json","generated_tasks.json","environment.txt","tiny_e2e.json","startup.log","install.log"]
  manifest={}
  for n in names:
   p=R/n
   if p.exists():manifest[n]=dict(sha256=digest(p),bytes=p.stat().st_size)
  save(R/"result_manifest.json",manifest)
  bundle=R/"return.tar.gz"
  with tarfile.open(bundle,"w:gz") as tar:
   for n in names+["result_manifest.json"]:
    if (R/n).exists():tar.add(R/n,arcname=n)
   if not (R/"embeddings.npz").exists() and (R/"shards").exists():tar.add(R/"shards",arcname="shards")
  print("LOCAL_RETURN_READY",str(bundle),digest(bundle),flush=True)
  # GPU service account denied this new GCS namespace. Stop that operation;
  # the existing authenticated IAP controller retrieves the local bundle.
