"""Run the sealed KnowCoder repair matrix; preserve every raw result, never execute it."""
from __future__ import annotations
import argparse
import ast
import collections
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
import shutil
import sys
import time
import traceback


def sha(data):
    return hashlib.sha256(data).hexdigest()


def metadata_json(value):
    """Normalize diagnostic metadata containers; reject unknown non-JSON values."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Nonfinite metadata float is not JSON")
        return value
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if isinstance(key, str):
                json_key = key
            elif isinstance(key, int) and not isinstance(key, bool):
                # HF PretrainedConfig.id2label uses integer IDs; JSON uses strings.
                json_key = str(key)
            else:
                raise TypeError("Metadata keys must be strings or integer label IDs")
            if json_key in normalized:
                raise ValueError("Metadata key collision after JSON normalization: " + json_key)
            normalized[json_key] = metadata_json(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [metadata_json(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [metadata_json(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False))
    raise TypeError("Unknown non-JSON metadata type: " + type(value).__name__)


def write(path, data):
    """Publish complete diagnostic JSON atomically without overwriting records."""
    encoded = (json.dumps(metadata_json(data), ensure_ascii=False, indent=2,
                          sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent,
                                         prefix=".record-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        # A hard link publishes fully written bytes and fails if the final path exists.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def bind(node, names):
    if len(node.args) > len(names):
        raise ValueError("Too many arguments")
    values = dict(zip(names, node.args))
    for kw in node.keywords:
        if kw.arg not in names or kw.arg in values:
            raise ValueError("Unknown or duplicate argument")
        values[kw.arg] = kw.value
    if set(values) != set(names):
        raise ValueError("Missing argument")
    return [values[name] for name in names]


def literal(node):
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str) or not node.value.strip():
        raise ValueError("Expected nonempty literal string")
    return node.value


def list_node(payload):
    if not isinstance(payload, str) or not payload.strip() or len(payload) > 100000:
        raise ValueError("Empty or oversized output")
    statements = ast.parse(payload.strip(), mode="exec").body
    if len(statements) != 1:
        raise ValueError("Expected single result")
    statement = statements[0]
    if isinstance(statement, ast.Expr):
        result = statement.value
    elif isinstance(statement, ast.Assign):
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name) or statement.targets[0].id not in {"results", "result"}:
            raise ValueError("Unexpected result assignment")
        result = statement.value
    else:
        raise ValueError("Unexpected result statement")
    if not isinstance(result, ast.List) or len(result.elts) > 256:
        raise ValueError("Expected bounded list")
    return result


def parse(payload, fixture, variant):
    result = list_node(payload)
    records = []
    for node in result.elts:
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id not in variant["allowed_classes"]:
            raise ValueError("Unexpected schema constructor")
        if fixture["task"] == "NER":
            values = [literal(bind(node, ["name"])[0])]
        else:
            values = []
            for arg in bind(node, ["head_entity", "tail_entity"]):
                if not isinstance(arg, ast.Call) or not isinstance(arg.func, ast.Name) or arg.func.id != "Entity":
                    raise ValueError("Expected generic Entity(name)")
                values.append(literal(bind(arg, ["name"])[0]))
        records.append([node.func.id, *values])
    return records


def expected_shapes(config):
    h, m, v, n = config.hidden_size, config.intermediate_size, config.vocab_size, config.num_hidden_layers
    if (h, m, v, n, config.num_attention_heads, config.num_key_value_heads) != (4096, 11008, 32000, 32, 32, 32):
        raise ValueError("Unexpected pinned KnowCoder architecture")
    shapes = {"model.embed_tokens.weight": (v, h), "model.norm.weight": (h,), "lm_head.weight": (v, h)}
    for i in range(n):
        p = "model.layers." + str(i) + "."
        for name in ("input_layernorm.weight", "post_attention_layernorm.weight"):
            shapes[p + name] = (h,)
        for name in ("q_proj", "k_proj", "v_proj", "o_proj"):
            shapes[p + "self_attn." + name + ".weight"] = (h, h)
        for name in ("gate_proj", "up_proj"):
            shapes[p + "mlp." + name + ".weight"] = (m, h)
        shapes[p + "mlp.down_proj.weight"] = (h, m)
    return shapes


def load(condition, identity, cache_dir=None):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StopStringCriteria
    from csts_pilot.extraction_native import runtime_metadata
    model_id, revision = identity["model_id"], identity["revision"]
    cache_options = {"cache_dir": str(cache_dir)} if cache_dir is not None else {}
    config = AutoConfig.from_pretrained(model_id, revision=revision, trust_remote_code=False, **cache_options)
    shapes = expected_shapes(config)
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision, use_fast=True,
        legacy=False, padding_side="left", trust_remote_code=False, **cache_options)
    dtype = getattr(torch, condition["dtype"])
    model, report = AutoModelForCausalLM.from_pretrained(model_id, revision=revision,
        config=config, torch_dtype=dtype, device_map="cuda", trust_remote_code=False,
        output_loading_info=True, **cache_options)
    for key in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"):
        if key not in report or report[key]:
            raise ValueError("Nonexact checkpoint load: " + key + "=" + str(report.get(key)))
    params = dict(model.named_parameters())
    if set(params) != set(shapes) or len(params) != 291:
        raise ValueError("Expected all 291 exact KnowCoder parameter names")
    dtypes = collections.Counter()
    for name, parameter in params.items():
        if tuple(parameter.shape) != shapes[name]:
            raise ValueError("Unexpected learned tensor shape: " + name)
        if not bool(torch.isfinite(parameter).all().item()):
            raise ValueError("Nonfinite learned tensor: " + name)
        if parameter.dtype != dtype:
            raise ValueError("Actual parameter dtype differs from declared fresh-load precision")
        dtypes[str(parameter.dtype)] += parameter.numel()
    model.eval()
    meta = runtime_metadata(torch)
    meta.update(condition=condition, checkpoint=identity,
        resolved_model_revision=getattr(model.config, "_commit_hash", None),
        parameter_elements_by_dtype=dict(dtypes), verified_parameter_tensors=291,
        finite_all_parameters=True, strict_loading_report=report,
        full_config=config.to_dict(), model_generation_config=model.generation_config.to_dict(),
        tokenizer_class=type(tokenizer).__name__, tokenizer_special_tokens_map=tokenizer.special_tokens_map,
        tokenizer_settings={"use_fast":True,"legacy":False,"padding_side":"left","add_special_tokens":True},
        tokenizer_init_kwargs={key:tokenizer.init_kwargs.get(key) for key in ("model_max_length","legacy","add_bos_token","add_eos_token","padding_side","clean_up_tokenization_spaces")},
        runtime_reproduction_status="Transformers canary, not author vLLM reproduction")
    if meta["resolved_model_revision"] not in (None, revision):
        raise ValueError("Loaded checkpoint revision changed")
    return model, tokenizer, torch, StoppingCriteriaList([StopStringCriteria(tokenizer, stop_strings=['"""'])]), meta


def generate(model, tokenizer, torch, stopping, prompt):
    from csts_pilot.extraction_native import native_payload, check_token_budget
    batch = tokenizer(prompt, add_special_tokens=True, return_tensors="pt")
    ids = batch["input_ids"][0].tolist()
    if tokenizer.encode(prompt) != ids:
        raise ValueError("Author tokenizer.encode and actual input IDs differ")
    bos, eos = tokenizer.bos_token_id, tokenizer.eos_token_id
    if ids.count(bos) != 1 or ids[0] != bos or eos in ids:
        raise ValueError("Unexpected BOS/EOS prompt serialization")
    if not bool(batch["attention_mask"].all().item()):
        raise ValueError("Single unpadded input must have all-one attention mask")
    context = min(4096, int(model.config.max_position_embeddings))
    check_token_budget(len(ids), 1024, context)
    batch = {key:value.to(model.device) for key,value in batch.items()}
    start = time.monotonic()
    with torch.inference_mode():
        output = model.generate(**batch, max_new_tokens=1024, min_new_tokens=0,
            do_sample=False, num_beams=1, num_return_sequences=1,
            pad_token_id=eos, stopping_criteria=stopping)
    suffix = output[0, len(ids):]
    output_ids = suffix.tolist()
    raw = tokenizer.decode(suffix, skip_special_tokens=True)
    payload, reason = native_payload(raw, "knowcoder")
    finished = bool(output_ids and output_ids[-1] == eos)
    return {"prompt":prompt,"input_token_ids":ids,"output_token_ids":output_ids,
        "input_tokens":len(ids),"output_tokens":len(output_ids),"context_limit":context,
        "raw_decoded_generation":raw,"payload":payload,"stop_reason":"eos" if finished else reason,
        "truncated":len(output_ids)>=1024 and not finished and reason!="author_stop_string",
        "elapsed_generation_seconds":time.monotonic()-start,
        "encode_equals_actual_input":True,"input_bos_count":ids.count(bos),"input_eos_count":ids.count(eos),
        "decoding":{"do_sample":False,"num_beams":1,"max_new_tokens":1024,"min_new_tokens":0,"pad_token_id":eos}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    seal = json.loads((root/"seal.json").read_text())
    for name, digest in seal["files"].items():
        if sha((root/name).read_bytes()) != digest:
            raise ValueError("Sealed repair artifact changed: "+name)
    design=json.loads((root/"design.json").read_text())
    fixtures=json.loads((root/"fixtures.json").read_text())
    sources=json.loads((root/"sources.json").read_text())
    for fixture in fixtures:
        if fixture["source"] is not None and sources[fixture["source_index"]] != fixture["source"]:
            raise ValueError("Actual-source fixture changed")
    sys.path.insert(0,str(root/"code"))
    args.output.mkdir(parents=True,exist_ok=False)
    write(args.output/"start.json",{"started_at":datetime.now(timezone.utc).isoformat(),
        "seal_sha256":sha((root/"seal.json").read_bytes()),"design":design,
        "primary_screen_unchanged":True,"expected_annotations_in_model_input":False})
    completed=failed=0
    for condition in design["conditions"]:
        cid=condition["id"]
        identity=design["checkpoints"][condition["model"]]
        try:
            model,tokenizer,torch,stopping,meta=load(condition,identity,args.cache_dir)
            write(args.output/(cid+"-load.json"),meta)
        except Exception as exc:
            write(args.output/(cid+"-load-error.json"),{"error":str(exc),"traceback":traceback.format_exc()})
            failed+=15
            continue
        for fixture in fixtures:
            for vid,variant in fixture["variants"].items():
                stem=cid+"-"+fixture["fixture_id"]+"-"+vid
                result={"condition":condition,"checkpoint":identity,"fixture_id":fixture["fixture_id"],
                    "variant":vid,"status":"failed","semantic_status":"unreviewed",
                    "expected_nonempty":fixture["expected_nonempty"],
                    "expected_anchor_relations":variant["minimal_expected_anchors"],
                    "parse_status":"not_attempted","empty_list_emitted":None}
                try:
                    generated=generate(model,tokenizer,torch,stopping,variant["prompt"])
                    write(args.output/(stem+"-generation.json"),generated)
                    if generated["truncated"]:
                        raise ValueError("Output budget exhausted")
                    result["parse_status"]="schema_or_literal_validation_failed"
                    try:result["empty_list_emitted"]=len(list_node(generated["payload"]).elts)==0
                    except (ValueError,SyntaxError,RecursionError):pass
                    rows=parse(generated["payload"],fixture,variant)
                    anchors=variant["minimal_expected_anchors"]
                    target_rows=[row for row in rows if fixture["target_class"] is None or row[0]==fixture["target_class"]]
                    result.update(status="completed",parse_status="valid",nonempty=bool(rows),
                        parsed_relations=rows,target_class_records=target_rows,target_class_nonempty=bool(target_rows),
                        anchors_present=all(row in rows for row in anchors) if anchors else None,
                        exact_anchor_match=sorted(rows)==sorted(anchors),
                        exact_target_anchor_match=sorted(target_rows)==sorted(anchors),
                        anchor_matches_are_descriptive_only=True)
                    completed+=1
                except Exception as exc:
                    failed+=1
                    result.update(error=str(exc),traceback=traceback.format_exc())
                write(args.output/(stem+"-result.json"),result)
                print(json.dumps({key:result[key] for key in ("condition","fixture_id","variant","status","nonempty") if key in result}),flush=True)
        del model,tokenizer,stopping
        gc.collect()
        torch.cuda.empty_cache()
    write(args.output/"complete.json",{"completed":completed,"failed":failed,"representative_quality_score":False})
    raise SystemExit(0 if failed==0 else 1)


if __name__=="__main__":
    main()
