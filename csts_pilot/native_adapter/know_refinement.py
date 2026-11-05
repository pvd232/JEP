"""One fixed Know-only refinement; Go and earlier recipes are unchanged."""
from pathlib import Path
import hashlib
import json

from .prompt_profiles import SYSTEM,recipe_identity,render_recipe

KNOW_REFINEMENT='native_know_palette_clause_refinement_v1'
DATA_SHA256='8840993e4b080ac783adfda99ec304c881b65b2d9e0957257cc3126bd198a97a'


def _data():
    raw=(Path(__file__).parent/'know_refinement_demonstrations.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DATA_SHA256:
        raise ValueError('Frozen Know refinement demonstrations changed')
    return json.loads(raw)


def identity(plan,model,schemas,schema_profile,count_stage=None):
    if model!='knowcoder':raise ValueError('Refinement is authorized only for KnowCoder grammar')
    base=recipe_identity(plan,model,schemas,schema_profile,count_stage)
    result={**base,'base_prompt_profile':base['prompt_profile'],'prompt_profile':KNOW_REFINEMENT,
            'active_refinement':None,'context_limit':2048}
    if base['recipe_route']=='fixed_spatial_inventory':
        data=_data()['spatial_palette']
        if sorted(data['illustrated_constructors'])!=sorted(schema['name'] for schema in schemas):
            raise ValueError('Spatial illustrations must cover the entire fixed palette')
        result.update(active_refinement='every_palette_constructor_illustrated',
            base_demonstrations_sha256=base['demonstrations_sha256'],demonstrations_sha256=DATA_SHA256,
            demonstration_key='spatial_palette',demonstrations=1,same_class_illustrations=len(schemas),
            context_limit=4096,context_bound_basis='pinned_Know_IE_max_position_embeddings4096_author_vllm_max_model_len4096')
    elif base['recipe_route']=='actor_full_clause_relation':
        _data()
        result.update(active_refinement='full_predicate_retrieval_origin_contrast',
            base_demonstrations_sha256=base['demonstrations_sha256'],demonstrations_sha256=DATA_SHA256,
            demonstration_key='action_completeness',demonstrations=2,same_class_illustrations=2)
    return result


def render(target_prompt,plan,model,schemas,schema_profile,count_stage=None):
    receipt=identity(plan,model,schemas,schema_profile,count_stage)
    if receipt['active_refinement'] is None:
        return render_recipe(target_prompt,plan,model,schemas,schema_profile,count_stage)
    prefix=SYSTEM+'\nInput:\n'
    if not target_prompt.startswith(prefix) or not target_prompt.endswith('\nOutput:\n'):
        raise ValueError('Know target lost canonical wrapper')
    query=target_prompt[len(prefix):]
    data=_data()
    if receipt['active_refinement']=='every_palette_constructor_illustrated':
        example=data['spatial_palette']
        return prefix+example['know_query']+'\nOutput:\n'+example['know_output']+'\nInput:\n'+query
    # Preserve the original gardener demonstration, then add exactly one fixed
    # independent retrieval/origin example with a bare-verb completeness contrast.
    original=json.loads((Path(__file__).parent/'recipe_demonstrations.json').read_text())['ActionDescription']
    example=data['action_completeness']
    return (prefix+original['know_query']+'\nOutput:\n'+original['know_output']+
            '\nInput:\n'+example['know_query']+'\nOutput:\n'+example['know_output']+'\nInput:\n'+query)
