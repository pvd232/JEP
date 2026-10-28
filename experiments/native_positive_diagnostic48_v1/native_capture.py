"""Public inference-only callback for frozen native jobs; no automatic examples or retries."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import threading

from native_adapter.schema import (compile_condition, bounded_input, verify_bound_input,
                                   selected_schemas, implementation_identity)
from native_adapter.normalize import normalize_native, normalize_stages
from native_capture_backends import Backend

ROOT = Path(__file__).resolve().parent
_SESSIONS = {}
_LOCK = threading.RLock()
BACKEND_FACTORY = Backend


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def support_identity():
    """Expose immutable helper identities without reading a source/job manifest."""
    path = ROOT / "support-seal.json"
    return {"support_manifest_sha256": _digest(path.read_bytes()),
            "compiler_implementation_sha256": _digest(_canonical(implementation_identity())),
            "compiler_implementation_files": implementation_identity(),
            "handler_sha256": _digest(Path(__file__).read_bytes())}


def _verify_support(cfg):
    seal_path = ROOT / "support-seal.json"
    if _digest(seal_path.read_bytes()) != cfg["support_manifest_sha256"]:
        raise ValueError("Frozen native helper manifest differs")
    seal = json.loads(seal_path.read_text())
    for name, expected in seal["files"].items():
        path = (ROOT/name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError("Invalid frozen support path: " + name)
        if _digest(path.read_bytes()) != expected:
            raise ValueError("Frozen native helper changed: " + name)
    if cfg["compiler_implementation_sha256"] != _digest(_canonical(implementation_identity())) or cfg["compiler_implementation_files"] != implementation_identity():
        raise ValueError("Frozen condition-only compiler differs")


def _stage_specs(plan, cfg):
    """Use only the compiler-declared stages and frozen profile/budget choices."""
    if plan["family"] == "aggregate_counts_quantities":
        return None, "Symbolic count dispatch is explicitly unsupported in the positive diagnostic"
    elif plan.get("stage_contract"):
        required = list(plan["stage_contract"])
        kind = "task_stage"
    else:
        required, kind = [None], None
    if len(required)>1 and cfg.get("allow_compiler_stages") is not True:
        return None, "Required native stages are not enabled by frozen protocol"
    specs=[]
    for name in required:
        override=cfg.get("stage_overrides",{}).get(name or "ordinary",{})
        profile=override.get("profile",cfg["profile"])
        limit=override.get("max_new_tokens",cfg["max_new_tokens"])
        if profile not in cfg.get("allowed_profiles",[cfg["profile"]]):
            return None,"Stage profile is outside frozen allowlist"
        if type(limit) is not int or not 1<=limit<=cfg["max_new_tokens"]:
            return None,"Stage output budget is outside frozen maximum"
        specs.append({"profile":profile,"max_new_tokens":limit,
            "count_stage":name if kind=="count_stage" else None,
            "task_stage":name if kind=="task_stage" else None})
    return specs,None


def gate_key(plan, model, spec):
    """Identify one condition-only native schema capability, including its stage."""
    schemas=selected_schemas(plan,model,spec["count_stage"],spec["profile"],spec["task_stage"])
    labels=",".join(sorted(item["name"] for item in schemas))
    stage=spec["count_stage"] or spec["task_stage"] or "ordinary"
    return "/".join((plan["native_task"],spec["profile"],stage,labels))


def authorization_binding(descriptor):
    """Noncircular descriptor identity; outer protocol binds the receipt itself."""
    value=json.loads(json.dumps(descriptor))
    gate=value["native_capture"].setdefault("diagnostic_authorization",{})
    if not isinstance(gate,dict) or set(gate)-{"receipt_path","receipt_sha256"}:
        raise ValueError("Unexpected diagnostic authorization fields")
    gate.pop("receipt_path",None)
    gate.pop("receipt_sha256",None)
    return _digest(_canonical(value))


def _compile(condition,cfg):
    recipe=cfg.get("contract_recipe")
    if not isinstance(recipe,str) or not recipe:
        raise ValueError("A single frozen positive task recipe is required")
    plan=compile_condition(condition,contract_recipe=recipe)
    if plan.get("contract_recipe")!=recipe:
        raise ValueError("Compiler did not retain the frozen task recipe")
    return plan


def _gate_passed(descriptor,source,plan,model,spec):
    """Authorize only the declared48 diagnostic; never imply semantic qualification."""
    cfg=descriptor["native_capture"]
    gate=cfg.get("diagnostic_authorization",{})
    try:
        if set(gate)!={"receipt_path","receipt_sha256"}:return False
        raw=Path(gate["receipt_path"]).read_bytes()
        if _digest(raw)!=gate["receipt_sha256"]:
            return False
        receipt=json.loads(raw)
        expected={"status":"AUTHORIZED_LOCKED48_DIAGNOSTIC","phase":"locked-canaries","model":model,
            "descriptor_binding_sha256":authorization_binding(descriptor),
            "experimental_calls_only":True,"semantic_qualification_passed":False,"fresh_evaluation_authorized":False,
            "cohort":cfg["diagnostic_cohort"]}
        ids=receipt.get("source_ids")
        records=receipt.get("source_record_sha256")
        if (any(receipt.get(k)!=v for k,v in expected.items()) or not isinstance(ids,list)
                or len(ids)!=48 or len(set(ids))!=48 or source["id"]not in ids):
            return False
        if not isinstance(records,dict) or set(records)!=set(ids):return False
        projection={key:source[key]for key in("id","passage","condition")}
        if records[source["id"]]!=_digest(_canonical(projection)):return False
        if plan["family"]=="aggregate_counts_quantities" or plan["family"]in cfg["unsupported_compiler_families"]:
            return False
        if plan["family"]not in cfg["allowed_compiler_families"] or plan["native_task"]not in cfg["allowed_native_tasks"]:
            return False
        if plan["family"]=="other" and not plan.get("stage_contract"):
            return False
        if spec["count_stage"]is not None or spec["profile"]!="positive_anchor":
            return False
        schemas=selected_schemas(plan,model,None,spec["profile"],spec["task_stage"])
        if not schemas:return False
        for schema in schemas:
            if schema["kind"]=="entity" and cfg.get("allow_typed_ner")is True:continue
            if schema["kind"]=="relation" and cfg.get("allow_condition_compiled_re")is True:continue
            return False
        return True
    except (OSError,KeyError,ValueError,TypeError):
        return False


def _session(model,cfg):
    # Profile/gate/source changes do not allocate a second copy of identical weights.
    fields=("model_id","revision","tokenizer_id","tokenizer_revision","snapshot",
            "backend","dtype","runtime_manifest_path","runtime_manifest_sha256",
            "support_manifest_sha256")
    key=_digest(_canonical({name:cfg[name] for name in fields} | {"model":model,
        "runtime_shim":cfg.get("runtime_shim")}))
    if key not in _SESSIONS:
        if _SESSIONS:
            raise RuntimeError("One frozen backend/model configuration is allowed per process")
        _SESSIONS[key]=BACKEND_FACTORY(model,cfg)
    return _SESSIONS[key]


def _base(source,model,protocol):
    return {"id":source.get("id"),"source_id":source.get("id"),"model":model,
        "protocol_canonical_sha256":_digest(_canonical(protocol)),
        "route_supported":False,"runtime_status":"not_run","parse_valid":False,
        "truncated":False,"coverage_complete":False,"raw_output":None,
        "normalized_evidence":None,"error":"","model_calls":0,
        "bound_inputs":[],"bound_input_verified":False,"stage_outputs":[],
        "automatic_companion_cases":False,"automatic_retries":False}


def capture_one(source, model, protocol):
    """Capture exactly the predeclared native stages for one inference-only source.

    Caller must atomically claim each source before invoking this function and run
    one model per process. This callback never opens a job's held-out files; it
    receives only the source supplied by the public driver.
    """
    if not isinstance(source,dict):
        source={}
    result=_base(source,model,protocol)
    session=None
    before=0
    prepared=[]
    try:
        if model not in {"knowcoder","gollie"}:
            raise ValueError("Unknown public native model name")
        if not isinstance(source.get("id"),str) or not source["id"]:
            raise ValueError("Source ID must be nonempty")
        if not isinstance(source.get("passage"),str) or not isinstance(source.get("condition"),str) or not source["condition"].strip():
            raise ValueError("Source passage must be text and condition must be nonempty")
        descriptor=protocol["models"][model]
        cfg=descriptor["native_capture"]
        if descriptor["handler"]["sha256"]!=_digest(Path(__file__).read_bytes()):
            raise ValueError("Handler bytes differ from protocol")
        _verify_support(cfg)
        if cfg["context_limit"]!=(4096 if model=="knowcoder" else 16384):
            raise ValueError("Frozen native context differs from reviewed compiler bound")
        expected_profile=("native_know_palette_clause_refinement_v1"if model=="knowcoder"else"native_spatial_clause_food_recipe_v1")
        if cfg.get("prompt_profile")!=expected_profile or cfg.get("contract_recipe")!="native_spatial_clause_food_recipe_v1":
            raise ValueError("Positive diagnostic requires its single fixed per-model task prompt recipe")
        generation=cfg["generation"]
        allowed={"do_sample","num_beams","num_return_sequences","gpu_memory_utilization","max_num_seqs","temperature","n","best_of","stop","method"}
        if set(generation)-allowed:
            raise ValueError("Undeclared generation option in frozen protocol")
        optional={"temperature":0.0,"n":1,"best_of":1}
        if any(k in generation and generation[k]!=v for k,v in optional.items()):
            raise ValueError("Only frozen greedy generation values are supported")
        if "stop" in generation and (model!="knowcoder" or generation["stop"]!='"""'):
            raise ValueError("Frozen native stop policy differs")
        expected={"do_sample":False,"num_beams":1,"num_return_sequences":1}
        if any(generation.get(k)!=v for k,v in expected.items()):
            raise ValueError("Only frozen single-sequence greedy generation is supported")
        if model=="knowcoder" and (generation.get("gpu_memory_utilization")!=0.6 or generation.get("max_num_seqs")!=4):
            raise ValueError("Know resource protocol must bind0.6 memory and4 maximum sequences")
        plan=_compile(source["condition"],cfg)
        if "plan" in source and source["plan"]!=plan:
            raise ValueError("Supplied frozen plan differs from condition-only compilation")
        result["plan_sha256"]=_digest(_canonical(plan))
        if not plan["supported"]:
            result.update(runtime_status="unsupported",error=plan["unsupported_reason"])
            return result
        specs,error=_stage_specs(plan,cfg)
        if error:
            result.update(runtime_status="unsupported",error=error)
            return result
        maximum=descriptor["max_model_calls_per_source"]
        if type(maximum) is not int or len(specs)>maximum:
            result.update(runtime_status="unsupported",error="Declared stages exceed frozen per-source call cap")
            return result
        if len({item["profile"] for item in specs}) != 1:
            result.update(runtime_status="unsupported",error="Stage merge requires one frozen profile")
            return result
        keys=[gate_key(plan,model,spec) for spec in specs]
        result["capability_gate_keys"]=keys
        if not all(_gate_passed(descriptor,source,plan,model,spec) for spec in specs):
            result.update(runtime_status="unsupported",error="Route/source lacks the frozen experimental locked48 diagnostic authorization")
            return result
        result["route_supported"]=True
        with _LOCK:
            session=_session(model,cfg)
            before=session.calls
            for spec in specs:
                bound=bounded_input(plan,model,source["passage"],session.count_tokens,
                    max_new_tokens=spec["max_new_tokens"],count_stage=spec["count_stage"],
                    profile=spec["profile"],task_stage=spec["task_stage"],prompt_profile=cfg["prompt_profile"])
                verify_bound_input(bound,plan,source["passage"],session.count_tokens)
                prepared.append(bound)
            if "inference_requests" in source and source["inference_requests"]!=prepared:
                raise ValueError("Frozen inference-only request manifest differs from actual compiler/tokenizer binding")
            result["prepared_inputs"]=prepared
            payloads={}
            for spec,bound in zip(specs,prepared):
                calls_before=session.calls
                try:
                    generated=session.generate(bound)
                finally:
                    # Even API/kernel errors are attempts; retain exactly their sent binding.
                    delta=session.calls-calls_before
                    if delta not in (0,1):
                        raise ValueError("Backend made undeclared native request count")
                    if delta:
                        result["bound_inputs"].append(bound)
                result["stage_outputs"].append({"stage":spec["count_stage"] or spec["task_stage"] or "ordinary",
                    "count_stage":spec["count_stage"],"task_stage":spec["task_stage"],
                    "profile":spec["profile"],"generated":generated})
                if generated["truncated"]:
                    result.update(runtime_status="truncated",truncated=True,
                        raw_output=generated["payload"],error="Native output budget exhausted")
                    return result
                normalize_native(generated["payload"],plan,model,source["passage"],
                    coverage_complete=False,count_stage=spec["count_stage"],
                    profile=spec["profile"],task_stage=spec["task_stage"])
                payloads[spec["count_stage"] or spec["task_stage"] or "ordinary"]=generated["payload"]
            profiles={item["profile"] for item in specs}
            if len(profiles)!=1:
                raise ValueError("Literal native stage merge requires one frozen capability profile")
            if len(specs)==1:
                evidence=normalize_native(next(iter(payloads.values())),plan,model,source["passage"],
                    coverage_complete=False,count_stage=specs[0]["count_stage"],
                    profile=specs[0]["profile"],task_stage=specs[0]["task_stage"])
            else:
                evidence=normalize_stages(payloads,plan,model,source["passage"],
                    coverage_complete=False,profile=next(iter(profiles)))
            raws=[item["generated"]["payload"] for item in result["stage_outputs"]]
            result.update(runtime_status="ok",parse_valid=True,normalized_evidence=evidence,
                raw_output=raws[0] if len(raws)==1 else json.dumps(payloads,ensure_ascii=False,sort_keys=True),
                backend_metadata=session.metadata)
    except TimeoutError as error:
        result.update(runtime_status="timeout",error=str(error))
    except Exception as error:
        result.update(runtime_status="error",error=type(error).__name__+": "+str(error))
        if session is not None and getattr(session,"last_raw",None) is not None:
            result["raw_backend_error_response"]=session.last_raw
    finally:
        if session is not None:
            result["model_calls"]=session.calls-before
            if result["model_calls"]:
                result["backend_metadata"]=session.metadata
        try:
            result["bound_input_verified"]=bool(result["bound_inputs"]) and all(
                verify_bound_input(bound,_compile(source["condition"],cfg),source["passage"],session.count_tokens)
                for bound in result["bound_inputs"])
        except Exception as verification_error:
            result.update(bound_input_verified=False,runtime_status="error",
                error="Post-capture binding verification failed: "+str(verification_error))
        if result["raw_output"] is None and result["stage_outputs"]:
            raws={item["stage"]:item["generated"]["payload"] for item in result["stage_outputs"]}
            result["raw_output"]=(next(iter(raws.values())) if len(prepared)==1 else
                json.dumps(raws,ensure_ascii=False,sort_keys=True))
    return result


def _cpu_codec(model,cfg):
    """Load only the pinned tokenizer JSON; no Transformers, torch or GPU imports."""
    from native_cpu_codec import codec
    import native_capture_backends as backend
    identity=(cfg["model_id"],cfg["revision"])
    if model=="knowcoder":
        if identity not in backend.MODEL_IDENTITIES:
            raise ValueError("Unknown pinned Know tokenizer")
        label=backend.MODEL_IDENTITIES[identity]
        folder=ROOT/"legacy_support/pinned-metadata"/label
    else:
        if identity!=backend.GO_ID:
            raise ValueError("Unknown pinned Go tokenizer")
        folder=ROOT/"gollie_pinned"
    if (cfg["tokenizer_id"],cfg["tokenizer_revision"])!=identity:
        raise ValueError("Tokenizer identity differs from frozen model")
    return codec(model,folder/"tokenizer.json"),folder


def _verify_record_backend_metadata(record,model,cfg,pinned):
    metadata=record.get("backend_metadata")
    if not isinstance(metadata,dict):
        raise ValueError("Completed capture lacks backend identity")
    if metadata.get("checkpoint")!={"model_id":cfg["model_id"],"revision":cfg["revision"]}:
        raise ValueError("Recorded checkpoint differs")
    if metadata.get("runtime_manifest_sha256")!=cfg["runtime_manifest_sha256"]:
        raise ValueError("Recorded runtime identity differs")
    required={"vllm":"0.2.2+cu118","torch":"2.1.0+cu118",
              "transformers":"4.34.1","tokenizers":"0.14.1"}
    if any(metadata.get("versions",{}).get(k)!=v for k,v in required.items()):
        raise ValueError("Recorded historical runtime versions differ")
    if model=="knowcoder":
        kwargs=metadata.get("engine_kwargs",{})
        expected={"max_num_seqs":4,"max_model_len":4096,"max_num_batched_tokens":16384,
                  "dtype":"auto","gpu_memory_utilization":0.6,
                  "tokenizer_mode":"auto","trust_remote_code":True}
        if any(kwargs.get(k)!=v for k,v in expected.items()):
            raise ValueError("Recorded Know engine options differ")
    else:
        if metadata.get("original_source_sha256")!="39ed69a0a8f40344981ba6c142074ea315769a770d959ef214aab41d181a6dbd":
            raise ValueError("Recorded Go implementation differs")
    index=json.loads((pinned/"pytorch_model.bin.index.json").read_text())
    selected=set(index["weight_map"].values())
    info=json.loads((pinned/"model-info.json").read_text())
    weights={item["rfilename"]:item["lfs"] for item in info["siblings"] if item["rfilename"] in selected}
    checks=metadata.get("snapshot_audit",{}).get("shard_file_checks",{})
    if set(checks)!=selected or set(weights)!=selected:
        raise ValueError("Recorded actual-byte shard proof is incomplete")
    for name,primary in weights.items():
        check=checks[name]
        if check.get("recomputed_sha256")!=primary["sha256"] or check.get("size")!=primary["size"] or check.get("full_file_hash_recomputed") is not True:
            raise ValueError("Recorded actual shard identity differs: "+name)


def verify_normalize_record(source,model,protocol,record):
    """Inert CPU replay from raw stage IDs; return recomputed claims, never saved flags.

    The outer driver must first verify request/handler-return/capture file hashes
    against its retained manifest and exact source/model/raw protocol identity.
    This function verifies the owner-specific invocation, tokenizer and claims.
    It never calls a backend, model, GPU or job/source-file loader.
    """
    if not isinstance(record,dict) or model not in {"knowcoder","gollie"}:
        raise ValueError("Invalid native replay record")
    if record.get("id")!=source["id"] or record.get("source_id")!=source["id"] or record.get("model")!=model:
        raise ValueError("Raw capture source/model identity differs")
    if record.get("protocol_canonical_sha256")!=_digest(_canonical(protocol)):
        raise ValueError("Raw capture protocol identity differs")
    descriptor=protocol["models"][model]
    cfg=descriptor["native_capture"]
    if descriptor["handler"]["sha256"]!=_digest(Path(__file__).read_bytes()):
        raise ValueError("Frozen handler source differs")
    _verify_support(cfg)
    plan=_compile(source["condition"],cfg)
    specs,error=_stage_specs(plan,cfg) if plan["supported"] else (None,plan.get("unsupported_reason"))
    permitted=bool(specs) and not error and len(specs)<=descriptor["max_model_calls_per_source"]
    if permitted:
        permitted=all(_gate_passed(descriptor,source,plan,model,s) for s in specs)
    if record.get("route_supported") is not permitted:
        raise ValueError("Saved route capability claim differs from frozen protocol")
    calls=record.get("model_calls")
    bindings=record.get("bound_inputs")
    stages=record.get("stage_outputs")
    if type(calls) is not int or not isinstance(bindings,list) or not isinstance(stages,list) or calls!=len(bindings):
        raise ValueError("Actual request/binding count differs")
    if record.get("coverage_complete") is not False or record.get("automatic_retries") is not False or record.get("automatic_companion_cases") is not False:
        raise ValueError("Native capture claims undeclared completeness/retries/companions")
    if not permitted:
        if record.get("runtime_status")!="unsupported" or record.get("parse_valid") is not False or record.get("bound_input_verified") is not False:
            raise ValueError("Unsupported record claims operational success")
        if calls or stages or record.get("raw_output") is not None or record.get("normalized_evidence") is not None:
            raise ValueError("Unsupported capture was replaced with fabricated model evidence")
        return None
    if calls>len(specs) or len(stages)>calls:
        raise ValueError("Undeclared native calls/stages")
    codec,pinned=_cpu_codec(model,cfg)
    expected=[bounded_input(plan,model,source["passage"],codec.count_tokens,
        max_new_tokens=s["max_new_tokens"],count_stage=s["count_stage"],
        profile=s["profile"],task_stage=s["task_stage"],prompt_profile=cfg["prompt_profile"]) for s in specs]
    if bindings!=expected[:calls]:
        raise ValueError("Stored native prompts/options/compiler bindings differ")
    for bound in bindings:
        verify_bound_input(bound,plan,source["passage"],codec.count_tokens)
    payloads={}
    truncated=False
    for position,stage in enumerate(stages):
        spec,bound=specs[position],expected[position]
        if stage.get("profile")!=spec["profile"] or stage.get("count_stage")!=spec["count_stage"] or stage.get("task_stage")!=spec["task_stage"]:
            raise ValueError("Stored native stage identity differs")
        generated=stage["generated"]
        inputs=generated.get("input_token_ids")
        outputs=generated.get("output_token_ids")
        if inputs!=codec.encode(bound["prompt"]) or not isinstance(outputs,list):
            raise ValueError("Stored native token IDs do not match frozen input")
        vocab=32000 if model=="knowcoder" else 32016
        if not all(type(x) is int and 0<=x<vocab for x in outputs):
            raise ValueError("Invalid output token IDs")
        raw=codec.decode(outputs,skip_special_tokens=True)
        if generated.get("raw_decoded_generation")!=raw or generated.get("raw_decode_with_special_tokens")!=codec.decode(outputs,skip_special_tokens=False):
            raise ValueError("Stored raw decoding differs from exact output IDs")
        if generated.get("input_tokens")!=len(inputs) or generated.get("output_tokens")!=len(outputs):
            raise ValueError("Stored native token counts differ")
        limit=bound["max_new_tokens"]
        expected_options=({"n":1,"best_of":1,"temperature":0.0,"stop":'"""',"max_tokens":limit}
                          if model=="knowcoder" else {"method":"manual_greedy_cache","max_new_tokens":limit,"do_sample":False,"num_beams":1})
        if generated.get("generation_options")!=expected_options:
            raise ValueError("Stored actual generation options differ")
        reason=generated.get("stop_reason")
        exhausted=len(outputs)==limit and (not outputs or outputs[-1]!=2)
        if model=="knowcoder":
            payload=generated.get("api_text")
            if not isinstance(payload,str) or payload.strip()!=raw.split('"""',1)[0].strip() or generated.get("payload")!=payload:
                raise ValueError("vLLM API payload differs beyond its declared stop/whitespace envelope")
            if generated.get("author_projection")!=__import__("native_capture_backends").know_support.author_projection(codec,inputs,outputs):
                raise ValueError("Stored author token projection differs")
            if reason not in {"stop","length"}:
                raise ValueError("Unexpected vLLM termination reason")
            actual_truncated=reason=="length"
            if not actual_truncated and (not outputs or (outputs[-1]!=2 and '"""' not in raw)):
                raise ValueError("vLLM stop lacks EOS or declared stop marker")
        else:
            payload=raw
            if generated.get("payload")!=payload:
                raise ValueError("Go payload differs from raw model decoding")
            actual_truncated=exhausted
            if reason!=("length" if exhausted else "eos") or (not exhausted and (not outputs or outputs[-1]!=2)):
                raise ValueError("Go termination metadata differs from IDs")
        if len(outputs)>limit or generated.get("truncated") is not actual_truncated:
            raise ValueError("Stored truncation/budget claim differs")
        truncated|=actual_truncated
        label=spec["count_stage"] or spec["task_stage"] or "ordinary"
        if stage.get("stage")!=label:
            raise ValueError("Stored stage label differs")
        payloads[label]=payload
    if calls==0:
        if record.get("runtime_status") not in {"error","timeout"} or record.get("parse_valid") is not False or record.get("bound_input_verified") is not False:
            raise ValueError("Zero-call record claims model success")
        if stages or record.get("raw_output") is not None or record.get("normalized_evidence") is not None:
            raise ValueError("Zero-call record contains invented prediction")
        return None
    if record.get("bound_input_verified") is not True:
        raise ValueError("Actual calls lack binding verification")
    if calls!=len(specs) or len(stages)!=len(specs) or truncated:
        if record.get("normalized_evidence") is not None or record.get("parse_valid") is not False:
            raise ValueError("Incomplete/truncated request claims normalized evidence")
        expected_status={"truncated"} if truncated else {"error","timeout"}
        if record.get("runtime_status") not in expected_status or record.get("truncated") is not truncated:
            raise ValueError("Failed/incomplete capture has inconsistent runtime status")
        _verify_record_backend_metadata(record,model,cfg,pinned)
        return None
    expected_raw=(next(iter(payloads.values())) if len(specs)==1 else
        json.dumps(payloads,ensure_ascii=False,sort_keys=True))
    if record.get("raw_output")!=expected_raw:
        raise ValueError("Saved raw output presentation differs from retained stages")
    if record.get("truncated") is not False:
        raise ValueError("Completed output claims truncation")
    _verify_record_backend_metadata(record,model,cfg,pinned)
    try:
        if len(specs)==1:
            s=specs[0]
            evidence=normalize_native(next(iter(payloads.values())),plan,model,source["passage"],
                coverage_complete=False,count_stage=s["count_stage"],profile=s["profile"],task_stage=s["task_stage"])
        else:
            evidence=normalize_stages(payloads,plan,model,source["passage"],coverage_complete=False,profile=specs[0]["profile"])
    except (ValueError,SyntaxError,RecursionError):
        if record.get("normalized_evidence") is not None or record.get("parse_valid") is not False or record.get("runtime_status")!="error":
            raise ValueError("Malformed/ungrounded raw output was promoted into valid claims")
        return None
    if record.get("normalized_evidence")!=evidence:
        raise ValueError("Saved normalized claims differ from frozen raw replay")
    if record.get("runtime_status")!="ok" or record.get("parse_valid") is not True or record.get("coverage_complete") is not False:
        raise ValueError("Saved capture status differs from raw replay")
    return evidence
