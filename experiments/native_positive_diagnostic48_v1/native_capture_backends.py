"""Pinned lazy backend sessions for frozen native inference jobs; no generated code execution."""
from __future__ import annotations
from importlib import metadata
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "legacy_support"))
import run_legacy as know_support
import gollie_backend_support

MODEL_IDENTITIES = {
    ("golaxy/KnowCoder-7B-base", "4a7a076f573fe87fe0a97670c63c64214484742f"): "base",
    ("golaxy/KnowCoder-7B-IE", "90ba076763dfb2e9efefd84a0e599f15ae533597"): "ie",
}
GO_ID = ("HiTZ/GoLLIE-7B", "d3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9")
GO_SOURCE_SHA = "39ed69a0a8f40344981ba6c142074ea315769a770d959ef214aab41d181a6dbd"
_ACTIVE = None


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _check_runtime(cfg):
    path = Path(cfg["runtime_manifest_path"])
    if digest(path.read_bytes()) != cfg["runtime_manifest_sha256"]:
        raise ValueError("Frozen runtime receipt differs")
    record = json.loads(path.read_text())
    if record.get("status") not in {"ready_import_verified", "ready_kernel_verified", "complete"}:
        raise ValueError("Runtime receipt is not ready")
    shim = cfg.get("runtime_shim")
    if shim is not None:
        source = Path(shim["path"])
        if digest(source.read_bytes()) != shim["sha256"]:
            raise ValueError("Frozen task-local runtime shim changed")
        spec = importlib.util.spec_from_file_location("frozen_native_runtime_shim", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        getattr(module, shim["callable"])(**shim.get("kwargs", {}))
    return {"runtime_manifest_sha256": cfg["runtime_manifest_sha256"],
            "runtime_shim_sha256": None if shim is None else shim["sha256"]}


class Backend:
    """Load the tokenizer for binding, then load model weights only on the first call."""
    def __init__(self, model, cfg):
        self.model_name, self.cfg = model, dict(cfg)
        self.calls = 0
        self.failed_load = False
        self.last_raw = None
        self.engine = self.model = self.torch = None
        self.metadata = _check_runtime(cfg)
        self.metadata["versions"] = know_support.versions()
        self.snapshot = Path(cfg["snapshot"]).resolve()
        identity = (cfg["model_id"], cfg["revision"])
        if self.snapshot.name != cfg["revision"]:
            raise ValueError("Snapshot revision path differs")
        if (cfg["tokenizer_id"], cfg["tokenizer_revision"]) != identity:
            raise ValueError("Checkpoint and tokenizer must use the same pinned native snapshot")
        from transformers import AutoTokenizer
        if model == "knowcoder":
            if identity not in MODEL_IDENTITIES or cfg["backend"] != "author_vllm_0.2.2_cu118" or cfg["dtype"] != "float16":
                raise ValueError("Unsupported frozen Know backend/checkpoint")
            label = MODEL_IDENTITIES[identity]
            self.audit = know_support.snapshot_metadata(self.snapshot,
                {"model_id": identity[0], "revision": identity[1]},
                ROOT / "legacy_support/pinned-metadata" / label)
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.snapshot), use_fast=True,
                legacy=False, padding_side="left", trust_remote_code=True, local_files_only=True)
        elif model == "gollie":
            if identity != GO_ID or cfg["backend"] != "pinned_original_flash_model" or cfg["dtype"] != "bfloat16":
                raise ValueError("Unsupported frozen Go backend/checkpoint")
            import flash_attn
            self.metadata["flash_attention"]={"distribution":metadata.version("flash-attn"),"module":flash_attn.__version__}
            if self.metadata["flash_attention"] != {"distribution":"2.3.4","module":"2.3.4"}:
                raise ValueError("Unexpected FlashAttention distribution")
            pinned = ROOT / "gollie_pinned"
            for name in ("config.json", "generation_config.json", "tokenizer_config.json",
                         "tokenizer.json", "special_tokens_map.json", "pytorch_model.bin.index.json",
                         "modeling_flash_llama.py"):
                if digest((self.snapshot/name).read_bytes()) != digest((pinned/name).read_bytes()):
                    raise ValueError("Go pinned artifact differs: " + name)
            if digest((self.snapshot/"modeling_flash_llama.py").read_bytes()) != GO_SOURCE_SHA:
                raise ValueError("Go original source differs")
            index = json.loads((self.snapshot/"pytorch_model.bin.index.json").read_text())
            if len(index["weight_map"]) != 291:
                raise ValueError("Go parameter index differs")
            selected = set(index["weight_map"].values())
            expected = {"pytorch_model-00001-of-00002.bin", "pytorch_model-00002-of-00002.bin"}
            if selected != expected:
                raise ValueError("Go index must select only the two current shards")
            info = json.loads((pinned/"model-info.json").read_text())
            if info["sha"] != GO_ID[1]:
                raise ValueError("Go primary artifact revision differs")
            self.audit = {"selected_shards": {row["rfilename"]: row for row in info["siblings"]
                          if row["rfilename"] in selected},
                          "metadata_sha256": {name: digest((pinned/name).read_bytes()) for name in
                          ("config.json","tokenizer_config.json","tokenizer.json","pytorch_model.bin.index.json")}}
            self.tokenizer = AutoTokenizer.from_pretrained(self.snapshot, add_eos_token=True, local_files_only=True)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token_id = self.tokenizer.unk_token_id if self.tokenizer.unk_token_id is not None else self.tokenizer.eos_token_id
        else:
            raise ValueError("Unknown native model")
        self.metadata["checkpoint"] = {"model_id": identity[0], "revision": identity[1]}
        self.metadata["tokenizer_class"] = type(self.tokenizer).__name__

    def encode(self, prompt):
        ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        if self.model_name == "gollie":
            if not ids or ids[-1] != self.tokenizer.eos_token_id:
                raise ValueError("Go tokenizer must append the author-removed EOS")
            ids = ids[:-1]
        if not ids or ids[0] != 1 or ids.count(1) != 1 or 2 in ids:
            raise ValueError("Unexpected native BOS/EOS input")
        return ids

    def count_tokens(self, prompt):
        return len(self.encode(prompt))

    def _load(self):
        global _ACTIVE
        identity = (self.model_name, self.cfg["model_id"], self.cfg["revision"])
        if _ACTIVE is not None and _ACTIVE is not self:
            raise ValueError("Run one GPU model per process; do not overcommit cached native models")
        self.audit["shard_file_checks"] = know_support.verify_weight_files(self.snapshot, self.audit)
        import torch
        self.torch = torch
        if not torch.cuda.is_available():
            raise ValueError("Native backend requires CUDA")
        _ACTIVE = self
        if self.model_name == "knowcoder":
            from vllm import LLM
            kwargs = {"model": str(self.snapshot), "tokenizer_mode": "auto",
                "trust_remote_code": True, "max_num_seqs": 4, "max_model_len": 4096,
                "max_num_batched_tokens": 16384, "dtype": "auto", "gpu_memory_utilization": 0.6}
            self.engine = LLM(**kwargs)
            if str(self.engine.llm_engine.model_config.dtype) != "torch.float16":
                raise ValueError("Know auto dtype differs from FP16")
            self.metadata["engine_kwargs"] = kwargs
        else:
            from transformers import LlamaConfig
            source = self.snapshot/"modeling_flash_llama.py"
            spec = importlib.util.spec_from_file_location("pinned_general_gollie_model", source)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            config = LlamaConfig.from_pretrained(self.snapshot, local_files_only=True)
            self.model, report = module.LlamaForCausalLM.from_pretrained(self.snapshot, config=config,
                torch_dtype=torch.bfloat16, device_map={"":0}, output_loading_info=True, local_files_only=True)
            gollie_backend_support.strict_load_info(report)
            params = dict(self.model.named_parameters())
            index = json.loads((self.snapshot/"pytorch_model.bin.index.json").read_text())["weight_map"]
            if len(params) != 291 or set(params) != set(index):
                raise ValueError("Go learned parameter names differ")
            for name, value in params.items():
                if value.dtype != torch.bfloat16 or not torch.isfinite(value).all().item():
                    raise ValueError("Invalid learned Go tensor: " + name)
            self.model.eval()
            if self.model.model.layers[0].self_attn.rotary_emb.base != 10000:
                raise ValueError("Go original rotary base differs")
            self.metadata.update(loading_info=report, finite_parameter_tensors=291,
                                 original_source_sha256=GO_SOURCE_SHA)
        _ACTIVE = self
        self.metadata.update(snapshot_audit=self.audit, cuda=torch.version.cuda,
                             gpu=torch.cuda.get_device_name(0), timing_isolated=False)

    def generate(self, bound):
        if self.failed_load:
            raise ValueError("Backend load previously failed; no automatic load retry")
        if self.engine is None and self.model is None:
            try:
                self._load()
            except Exception:
                self.failed_load = True
                raise
        prompt, limit = bound["prompt"], bound["max_new_tokens"]
        ids = self.encode(prompt)
        if len(ids) != bound["input_tokens"] or len(ids)+limit > bound["context_limit"]:
            raise ValueError("Verified native token budget changed")
        start = time.monotonic()
        self.last_raw = None
        if self.model_name == "knowcoder":
            from vllm import SamplingParams
            if self.engine.get_tokenizer().encode(prompt) != ids:
                raise ValueError("Know engine tokenizer differs")
            self.calls += 1
            responses = self.engine.generate(prompt_token_ids=[ids], sampling_params=SamplingParams(
                n=1,best_of=1,temperature=0.0,stop='"""',max_tokens=limit))
            raw = [{"prompt_token_ids":list(r.prompt_token_ids),"request_id":r.request_id,"finished":r.finished,
                    "outputs":[{"text":o.text,"token_ids":list(o.token_ids),"finish_reason":o.finish_reason,
                    "cumulative_logprob":know_support.diagnostic_number(o.cumulative_logprob)} for o in r.outputs]}
                   for r in responses]
            self.last_raw = raw
            if len(responses)!=1 or list(responses[0].prompt_token_ids)!=ids or len(responses[0].outputs)!=1 or not responses[0].finished:
                raise ValueError("Native response identity/incomplete output; raw response retained on backend")
            out=responses[0].outputs[0]
            tokens=list(out.token_ids)
            result={"payload":out.text,"api_text":out.text,"raw_backend_response":raw,
                "author_projection":know_support.author_projection(self.tokenizer,ids,tokens),
                "stop_reason":out.finish_reason,"truncated":out.finish_reason=="length",
                "generation_options":{"n":1,"best_of":1,"temperature":0.0,"stop":'"""',"max_tokens":limit}}
        else:
            tensor=self.torch.tensor([ids],device="cuda")
            self.calls += 1
            response=gollie_backend_support.greedy(self.model,tensor,limit,self.tokenizer.eos_token_id,self.torch)
            tokens=response["token_ids"]
            result={"payload":self.tokenizer.decode(tokens,skip_special_tokens=True),
                "stop_reason":"eos" if response["ended_on_eos"] else "length",
                "truncated":response["length_truncated"],"cache_checks":response["cache_vs_full_prefix"],
                "generation_options":{"method":"manual_greedy_cache","max_new_tokens":limit,"do_sample":False,"num_beams":1}}
        result.update(input_token_ids=ids,output_token_ids=tokens,input_tokens=len(ids),output_tokens=len(tokens),
            raw_decoded_generation=self.tokenizer.decode(tokens,skip_special_tokens=True),
            raw_decode_with_special_tokens=self.tokenizer.decode(tokens,skip_special_tokens=False),
            elapsed_seconds=time.monotonic()-start)
        return result
