"""Frozen source-independent prompt profiles, separate from schema capabilities."""
from pathlib import Path
import hashlib
import json
from .task_recipe import CONTRACT_RECIPE,is_plain_food

ZERO_SHOT='native_zero_shot_v1'
ONE_SHOT='native_fixed_family_one_shot_v1'
DEMONSTRATIONS_SHA256='23a4c1091997f9953990757561494966b8883fc2aa6ec263c0ca678de0ce9a84'
RECIPE_DEMONSTRATIONS_SHA256='cfd6dd191d52a548ac7bc3c4e77bc3dd5ee77c24fd959cc54178c9fe4276e028'
SYSTEM='You are a highly skilled assistant at digesting and extracting information from textual content. Below is an input containing standard type definitions and textual content. Please complete it with the extracted information in the form of structured code.'


def identity(prompt_profile,native_task,schema_profile,count_stage=None,task_stage=None):
    if prompt_profile==ZERO_SHOT:
        return {'prompt_profile':ZERO_SHOT,'demonstrations_sha256':None,'family':None,'demonstrations':0}
    if prompt_profile!=ONE_SHOT:raise ValueError('Unknown frozen native prompt profile')
    if native_task not in {'NER','RE','EE'} or schema_profile!='positive_anchor' or count_stage is not None or task_stage is not None:
        raise ValueError('One-shot profile is qualified only for ordinary positive NER/RE/EE schemas')
    raw=(Path(__file__).parent/'demonstrations.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DEMONSTRATIONS_SHA256:
        raise ValueError('Frozen one-shot demonstration bytes changed')
    return {'prompt_profile':ONE_SHOT,'demonstrations_sha256':DEMONSTRATIONS_SHA256,'family':native_task,'demonstrations':1}


def render(target_prompt,model,native_task,prompt_profile,schema_profile,count_stage=None,task_stage=None):
    """Retain the complete target query; add one fixed completed family example."""
    receipt=identity(prompt_profile,native_task,schema_profile,count_stage,task_stage)
    if receipt['demonstrations']==0:return target_prompt
    raw=(Path(__file__).parent/'demonstrations.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DEMONSTRATIONS_SHA256:
        raise ValueError('Frozen one-shot demonstration bytes changed')
    examples=json.loads(raw)
    example=examples[native_task]
    if model=='knowcoder':
        prefix=SYSTEM+'\nInput:\n'
        if not target_prompt.startswith(prefix) or not target_prompt.endswith('\nOutput:\n'):
            raise ValueError('Target must retain the canonical KnowCoder wrapper')
        query=target_prompt[len(prefix):]
        return prefix+example['know_query']+'\nOutput:\n'+example['know_output']+'\nInput:\n'+query
    if model=='gollie':
        if not target_prompt.endswith('result ='):
            raise ValueError('Target must retain the canonical GoLLIE completion marker')
        return example['go_query']+' '+example['go_output']+'\n\n'+target_prompt
    raise ValueError('Unknown native model')


def recipe_identity(plan,model,schemas,schema_profile,count_stage=None):
    """One model/task/class rule, with no source or output-dependent switches."""
    if plan.get('contract_recipe')!=CONTRACT_RECIPE or schema_profile!='positive_anchor' or count_stage is not None or plan['family']=='aggregate_counts_quantities':
        raise ValueError('New task recipe qualifies positive non-count schemas only')
    kinds={schema['kind'] for schema in schemas};names=sorted(schema['name'] for schema in schemas)
    if kinds=={'entity'}:
        route='gollie_food_same_class' if model=='gollie' and len(schemas)==1 and is_plain_food(schemas[0]) else 'preserved_zero_shot_ner'
        key='Food' if route=='gollie_food_same_class' else None
    elif schemas and all(schema.get('representation')=='spatial_predicate_edge' for schema in schemas):
        route,key='fixed_spatial_inventory','Spatial'
    elif schemas and all(schema.get('representation')=='verbatim_action_description' for schema in schemas):
        route,key='actor_full_clause_relation','ActionDescription'
    elif kinds=={'relation'}:
        route,key='preserved_fixed_re_family_one_shot','RE'
    else:raise ValueError('Recipe needs one explicit native task stage')
    if key in {'Food','Spatial','ActionDescription'}:
        raw=(Path(__file__).parent/'recipe_demonstrations.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=RECIPE_DEMONSTRATIONS_SHA256:raise ValueError('Frozen task-recipe demonstration bytes changed')
        demo_sha=RECIPE_DEMONSTRATIONS_SHA256
    elif key=='RE':
        identity(ONE_SHOT,'RE',schema_profile);demo_sha=DEMONSTRATIONS_SHA256
    else:demo_sha=None
    return {'prompt_profile':CONTRACT_RECIPE,'recipe_route':route,'demonstration_key':key,
            'demonstrations_sha256':demo_sha,'demonstrations':int(key is not None),
            'selected_constructors':names,'development_selected':True}


def render_recipe(target_prompt,plan,model,schemas,schema_profile,count_stage=None):
    receipt=recipe_identity(plan,model,schemas,schema_profile,count_stage)
    key=receipt['demonstration_key']
    if key is None:return target_prompt
    if key=='RE':return render(target_prompt,model,'RE',ONE_SHOT,schema_profile)
    raw=(Path(__file__).parent/'recipe_demonstrations.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RECIPE_DEMONSTRATIONS_SHA256:raise ValueError('Frozen task-recipe demonstration bytes changed')
    example=json.loads(raw)[key]
    if model=='gollie':return example['go_query']+' '+example['go_output']+'\n\n'+target_prompt
    prefix=SYSTEM+'\nInput:\n'
    if model!='knowcoder' or not target_prompt.startswith(prefix) or not target_prompt.endswith('\nOutput:\n'):
        raise ValueError('Target lost canonical native wrapper')
    return prefix+example['know_query']+'\nOutput:\n'+example['know_output']+'\nInput:\n'+target_prompt[len(prefix):]
