"""CPU-only preparation of a byte-canonical, initially ungated native protocol."""
import argparse
import json
from pathlib import Path
import native_capture as capture


def deployment_path(path):
    """Use the portable /tmp spelling across Mac preparation and Linux replay."""
    value=str(Path(path).absolute())
    return '/tmp/'+value[len('/private/tmp/'):]if value.startswith('/private/tmp/')else value


def runtime_config(model,snapshot,runtime_manifest):
    identity=capture.support_identity()
    if model=='knowcoder':
        model_id,revision='golaxy/KnowCoder-7B-IE','90ba076763dfb2e9efefd84a0e599f15ae533597'
        backend,dtype,context='author_vllm_0.2.2_cu118','float16',4096
    elif model=='gollie':
        model_id,revision='HiTZ/GoLLIE-7B','d3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9'
        backend,dtype,context='pinned_original_flash_model','bfloat16',16384
    else:raise ValueError('Unknown native model')
    receipt=Path(runtime_manifest)
    config={'model_id':model_id,'revision':revision,'tokenizer_id':model_id,'tokenizer_revision':revision,
        'snapshot':deployment_path(snapshot),'backend':backend,'dtype':dtype,
        'runtime_manifest_path':deployment_path(receipt),'runtime_manifest_sha256':capture._digest(receipt.read_bytes()),
        **{key:identity[key] for key in ('support_manifest_sha256','compiler_implementation_sha256','compiler_implementation_files')},
        'support_manifest_path':deployment_path(capture.ROOT/'support-seal.json'),
        'context_limit':context,'max_new_tokens':512,'profile':'positive_anchor',
        'contract_recipe':'native_spatial_clause_food_recipe_v1',
        'prompt_profile':('native_know_palette_clause_refinement_v1'if model=='knowcoder'else'native_spatial_clause_food_recipe_v1'),
        'allowed_profiles':['positive_anchor'],'allow_compiler_stages':True,'stage_overrides':{},
        'allowed_compiler_families':['unary_typed_mentions','binary_properties_locations','actions_events','other'],
        'unsupported_compiler_families':['aggregate_counts_quantities'],
        'allowed_native_tasks':['NER','RE','NER+RE'],'allow_typed_ner':True,'allow_condition_compiled_re':True,
        'diagnostic_authorization':{},
        'generation':{'do_sample':False,'num_beams':1,'num_return_sequences':1}}
    if model=='knowcoder':config['generation'].update(gpu_memory_utilization=0.6,max_num_seqs=4,
        temperature=0.0,n=1,best_of=1,stop='"""')
    else:config['generation']['method']='manual_greedy_cache'
    return config


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',choices=['knowcoder','gollie'],required=True)
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--runtime-manifest',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    cfg=runtime_config(args.model,args.snapshot,args.runtime_manifest)
    protocol={'status':'PREPARED_UNGATED_NATIVE_PROTOCOL','models':{args.model:{
        'handler':{'module':'native_capture','callable':'capture_one','verify_callable':'verify_normalize_record',
                   'sha256':capture.support_identity()['handler_sha256']},
        'max_model_calls_per_source':3,'native_capture':cfg}},'capture_scope':'locked48_diagnostic_only'}
    # Exact canonical bytes/no newline: file SHA equals handler canonical-object SHA.
    with args.output.open('xb') as out:out.write(capture._canonical(protocol))

if __name__=='__main__':main()
