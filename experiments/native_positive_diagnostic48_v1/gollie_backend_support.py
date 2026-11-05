"""Compare pinned original GoLLIE FlashAttention code with stock Llama eager attention in the historical runtime."""
from pathlib import Path
import argparse
import gc
import hashlib
import importlib.util
import json
import sys
import time

REVISION = 'd3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9'
SOURCE_SHA = '39ed69a0a8f40344981ba6c142074ea315769a770d959ef214aab41d181a6dbd'

def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(jsonable(v) for v in value)
    if isinstance(value, (tuple, list)):
        return [jsonable(v) for v in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError('Unsupported metadata type: ' + type(value).__name__)

def write(path, value):
    data = (json.dumps(jsonable(value), indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as out:
        out.write(data)

def greedy(model, inputs, limit, eos, torch):
    current, past, tokens, cache_checks = inputs, None, [], []
    with torch.inference_mode():
        for _ in range(limit):
            result = model(input_ids=current, past_key_values=past, use_cache=True, return_dict=True)
            logits = result.logits[0, -1].float()
            if not torch.isfinite(logits).all():
                raise ValueError('Nonfinite cached generation logits')
            if 0 < len(tokens) <= 3:
                full = torch.cat([inputs, torch.tensor([tokens], device=inputs.device)], dim=1)
                full_logits = model(input_ids=full, use_cache=False, return_dict=True).logits[0, -1].float()
                if not torch.isfinite(full_logits).all():
                    raise ValueError('Nonfinite full-prefix comparison logits')
                cache_checks.append({'generated_prefix_tokens': len(tokens),
                    'max_abs_logit_difference': float((logits-full_logits).abs().max()),
                    'mean_abs_logit_difference': float((logits-full_logits).abs().mean()),
                    'top1_equal': int(logits.argmax()) == int(full_logits.argmax())})
            token = int(logits.argmax())
            tokens.append(token)
            if token == eos:
                break
            current = torch.tensor([[token]], device=inputs.device)
            past = result.past_key_values
    return {'token_ids': tokens, 'ended_on_eos': bool(tokens and tokens[-1] == eos),
            'length_truncated': len(tokens) == limit and tokens[-1] != eos,
            'cache_vs_full_prefix': cache_checks}

def strict_load_info(info):
    for key in ('missing_keys', 'unexpected_keys', 'mismatched_keys', 'error_msgs'):
        if key not in info or info[key]:
            raise ValueError('Checkpoint loading is not complete: ' + key)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).parent
    seal = json.loads((root/'probe-seal.json').read_text())
    for name, expected in seal['files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected, name
    assert args.snapshot.name == REVISION
    source = args.snapshot/'modeling_flash_llama.py'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA
    args.output.mkdir(parents=True, exist_ok=False)
    import torch
    import transformers
    import flash_attn
    from transformers import AutoTokenizer, LlamaConfig, LlamaForCausalLM
    assert transformers.__version__ == '4.34.1'
    assert str(torch.__version__) == '2.1.0+cu118'
    assert flash_attn.__version__ == '2.3.4'
    assert torch.cuda.is_available()
    spec = importlib.util.spec_from_file_location('pinned_gollie_author_model', source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot, add_eos_token=True, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.unk_token_id if tokenizer.unk_token_id is not None else tokenizer.eos_token_id
    config = LlamaConfig.from_pretrained(args.snapshot, local_files_only=True)
    assert config.rope_scaling is None
    original, original_info = module.LlamaForCausalLM.from_pretrained(
        args.snapshot, config=config, torch_dtype=torch.bfloat16,
        device_map={'': 0},
        output_loading_info=True, local_files_only=True)
    strict_load_info(original_info)
    original.eval()
    assert original.model.layers[0].self_attn.rotary_emb.base == 10000
    reference_config = LlamaConfig.from_pretrained(args.snapshot, local_files_only=True)
    reference_config.rope_theta = 10000
    reference, reference_info = LlamaForCausalLM.from_pretrained(
        args.snapshot, config=reference_config, torch_dtype=torch.bfloat16,
        device_map={'': 0},
        output_loading_info=True, local_files_only=True)
    strict_load_info(reference_info)
    reference.eval()
    left, right = dict(original.named_parameters()), dict(reference.named_parameters())
    assert len(left) == 291 and set(left) == set(right)
    for name in left:
        assert left[name].dtype == right[name].dtype == torch.bfloat16
        assert torch.equal(left[name], right[name]), name
        assert torch.isfinite(left[name]).all().item(), name
    write(args.output/'runtime.json', {
        'purpose': 'backend reproduction on exposed controls, not fresh quality evaluation',
        'torch': torch.__version__, 'transformers': transformers.__version__,
        'flash_attn': flash_attn.__version__, 'snapshot': str(args.snapshot),
        'source_sha256': SOURCE_SHA, 'equal_parameter_tensors': 291,
        'author_rope_base': 10000, 'stock_reference_rope_base': reference_config.rope_theta,
        'author_loading': original_info, 'stock_loading': reference_info,
        'stock_reference_backend': 'transformers4.34.1_eager',
        'old_transformers5.20_sdpa_parity_claimed': False,
        'generation': 'manual greedy loop using each implementation own forward and KV cache',
        'max_new_tokens': 128, 'official_generation_mixin_parity_claimed': False,
    })
    fixtures = json.loads((root/'fixtures.json').read_text())
    for fixture in fixtures:
        started = time.monotonic()
        encoded = tokenizer(fixture['prompt'], add_special_tokens=True, return_tensors='pt')
        ids = encoded['input_ids']
        assert int(ids[0, -1]) == tokenizer.eos_token_id
        ids = ids[:, :-1].to('cuda')
        input_ids = ids[0].tolist()
        prior = fixture['prior_input_ids']
        input_match = None if prior is None else input_ids == prior
        with torch.inference_mode():
            a = original(input_ids=ids, use_cache=False, return_dict=True).logits[0, -1].float()
            b = reference(input_ids=ids, use_cache=False, return_dict=True).logits[0, -1].float()
        assert torch.isfinite(a).all() and torch.isfinite(b).all()
        p, q = a.log_softmax(-1), b.log_softmax(-1)
        canonical_generation = greedy(original, ids, 128, tokenizer.eos_token_id, torch)
        stock_generation = greedy(reference, ids, 128, tokenizer.eos_token_id, torch)
        canonical_tokens = canonical_generation['token_ids']
        stock_tokens = stock_generation['token_ids']
        result = {
            'fixture_id': fixture['id'], 'prompt': fixture['prompt'], 'input_token_ids': input_ids,
            'prior_input_ids_match': input_match, 'canonical_output_ids': canonical_tokens,
            'stock_reference_output_ids': stock_tokens,
            'canonical_generation_status': canonical_generation,
            'stock_reference_generation_status': stock_generation,
            'canonical_output': tokenizer.decode(canonical_tokens, skip_special_tokens=True),
            'stock_reference_output': tokenizer.decode(stock_tokens, skip_special_tokens=True),
            'same_generated_ids': canonical_tokens == stock_tokens,
            'prefill_logit_max_abs_difference': float((a-b).abs().max()),
            'prefill_logit_mean_abs_difference': float((a-b).abs().mean()),
            'prefill_kl_author_to_stock': float((p.exp()*(p-q)).sum()),
            'prefill_top1_equal': int(a.argmax()) == int(b.argmax()),
            'seconds': time.monotonic()-started,
        }
        write(args.output/(fixture['id']+'.json'), result)
        print(json.dumps({k: result[k] for k in ('fixture_id','prior_input_ids_match','same_generated_ids','prefill_top1_equal')}), flush=True)
    write(args.output/'completed.json', {'fixtures': len(fixtures), 'completed': True})
    del original, reference
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == '__main__':
    main()
