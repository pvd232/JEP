"""Create immutable inference requests and reject overlength prompts before allocation."""
import hashlib,json
from pathlib import Path
from prepare import RUN,PLAN,save,digest
from transformers import AutoTokenizer
def build_tasks():
 design=json.loads((RUN/"design_v2.json").read_text())
 tasks={}
 def add(passage,condition=None):
  prompt=passage if condition is None else design["prompt"].format(passage=passage,condition=condition)
  key=hashlib.sha256(prompt.encode()).hexdigest()
  tasks[key]=dict(key=key,prompt=prompt)
  return key
 for split in ["train","dev","test"]:
  for r in json.loads((RUN/("cleaned_"+split+".json")).read_text()):
   for side in ["sentence1","sentence2"]:add(r[side],r["condition"])
 for case in json.loads((RUN/"cases_v2.json").read_text()):
  add(case["text"]);add(case["text"],"overall semantic content")
  for i,p in enumerate(design["principles"]):
   for kind in ["short","definition","paraphrase"]:add(case["text"],p[kind])
   add(case["evidence"][i],p["definition"])
 out=[tasks[k] for k in sorted(tasks)]
 tok=AutoTokenizer.from_pretrained(design["model"],revision=design["revision"],padding_side="left",cache_dir=str(RUN/"qwen-tokenizer"))
 eod=tok.convert_tokens_to_ids("<|endoftext|>")
 assert eod is not None and eod!=tok.unk_token_id
 too_long=[]
 for task in out:
  ids=tok(task["prompt"],add_special_tokens=False,truncation=False)["input_ids"]+[eod]
  task["tokens"]=len(ids)
  if len(ids)>160:too_long.append(dict(key=task["key"],tokens=len(ids),prompt=task["prompt"]))
 save(RUN/"token_preflight.json",dict(tasks=len(out),max_tokens=max(x["tokens"] for x in out),overlength=too_long,revision=design["revision"]))
 if too_long:raise ValueError("Overlength prompts; no GPU allocated: "+str([(x["tokens"],x["prompt"][:60]) for x in too_long[:5]]))
 save(RUN/"tasks.json",out)
 save(RUN/"encoder_identity.json",dict(model=design["model"],revision=design["revision"],adapter_sha256=design["adapter_sha256"],prompt_sha256=hashlib.sha256(design["prompt"].encode()).hexdigest(),pooling="last non-padding explicit EOD, float32 L2",max_length=160,dimension=4096,tasks_sha256=digest(RUN/"tasks.json")))
 return len(out)
if __name__=="__main__":print("tasks",build_tasks())
