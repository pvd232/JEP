"""Compare cached readout and prefix embeddings with full-sequence GPU inference."""

import argparse
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path

import numpy as np

SPEC = importlib.util.spec_from_file_location("run_inference", Path(__file__).with_name("run_inference.py"))
run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run)


def full_sequence(model,head,tokenizer,sequences,stop_ids,torch,steps):
    batch=tokenizer.pad(dict(input_ids=sequences,attention_mask=[[1]*len(s) for s in sequences]),
                        padding=True,return_tensors="pt")
    ids=batch["input_ids"].to("cuda")
    mask=batch["attention_mask"].to("cuda")
    tracker=run.GenerationTracker(len(sequences),stop_ids)
    z=None
    with torch.inference_mode(),torch.autocast("cuda",dtype=torch.bfloat16,cache_enabled=False):
        for step in range(steps):
            out=model(input_ids=ids,attention_mask=mask,use_cache=False,return_dict=True)
            raw=out.last_hidden_state[:,-1,:]
            if step==0:
                pooled=raw.float()
                z=(pooled/pooled.norm(dim=-1,keepdim=True)).cpu().numpy()
            chosen=head(raw).argmax(dim=-1)
            if tracker.append(chosen.tolist()):
                break
            ids=torch.cat([ids,chosen[:,None]],dim=1)
            mask=torch.cat([mask,torch.ones((len(sequences),1),dtype=mask.dtype,device="cuda")],dim=1)
    return tracker.ids,z


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--probe",type=Path,required=True)
    parser.add_argument("--models",type=Path,required=True)
    parser.add_argument("--head",type=Path,required=True)
    parser.add_argument("--model-dir",type=Path)
    parser.add_argument("--offline",action="store_true")
    parser.add_argument("--cpu-threads",type=int,default=2)
    parser.add_argument("--minimum-free-gib",type=float,default=18)
    args=parser.parse_args()
    if run.sha256(args.head)!=run.HEAD_SHA256:
        raise ValueError("Shared head SHA-256 differs.")
    probe=run.validated_probe(args.probe,True)
    states=run.validated_models(args.models)
    torch,model,parameters,head,tokenizer,stop_ids,environment,load_seconds=run.load_runtime(args)
    # Unequal prefix lengths exercise the original left-padding behavior.
    rows=[probe["inputs"][0],max(probe["inputs"],key=lambda x:len(x["caption"]+x["condition"]))]
    sequences=run.token_sequences(tokenizer,rows)
    checks=[]
    for state in [s for s in states if s["name"] in ["base","seed7_P_B"]]:
        run.restore_checkpoint(state,parameters,torch)
        context=model.disable_adapter() if state["name"]=="base" else nullcontext()
        with context:
            pred,cached_z=run.generate_batch(model,head,tokenizer,sequences,stop_ids,torch,max_tokens=4)
            uncached_tokens,full_z=full_sequence(model,head,tokenizer,sequences,stop_ids,torch,steps=4)
        np.testing.assert_allclose(cached_z,full_z,atol=2e-5,rtol=2e-5)
        cached_tokens=[x["generated_token_ids"] for x in pred]
        if cached_tokens!=uncached_tokens:
            raise AssertionError(f"Cached and full-sequence greedy tokens differ: {state['name']}: {cached_tokens} / {uncached_tokens}")
        checks.append(dict(state=state["name"],cached_tokens_equal=True,
                           prefix_embedding_max_absolute_difference=float(np.abs(cached_z-full_z).max())))
    print(json.dumps(dict(status="passed",checks=checks,model_load_seconds=load_seconds,
                          environment=environment),indent=2))


if __name__=="__main__":
    main()
