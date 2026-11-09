"""One fixed condition-only spatial/action/Food contract alternative.

Recipe selection depends on model, condition-compiled task and requested class,
never a source passage or a model output. Original EE/NER recipes remain callable
without this explicit contract selection and remain archived separately.
"""
from __future__ import annotations
import copy
import re

CONTRACT_RECIPE='native_spatial_clause_food_recipe_v1'
FOOD_DEFINITION='An explicitly mentioned food, dish, edible ingredient, fruit or vegetable. Include prepared foods and individual ingredients named in the sentence. Copy the noun phrase naming the food; exclude containers, utensils and unstated foods.'

# This complete palette is offered for every compiled location relation. Never
# narrow it by inspecting a caption's preposition or selecting a target answer.
SPATIAL_PALETTE=(
 ('At','at','At a stated physical place or location. Not a fallback for a more specific qualifier.',['at']),
 ('Near','near','Near or close to the reference. Do not substitute for beside/on/in.',['near','nearby','close to']),
 ('On','on','On or on top of the reference.',['on','on top of','upon']),
 ('Inside','inside','Inside/in/within a physical reference; not clothing or participation.',['in','inside','within']),
 ('Outside','outside','Outside a physical reference.',['outside']),
 ('Under','under','Under/below/beneath the reference.',['under','below','beneath']),
 ('Above','above','Above the reference. Do not replace the word over.',['above']),
 ('Over','over','Over the reference; do not infer whether it is static or a path.',['over']),
 ('Beside','beside','Beside/next to/alongside the reference.',['beside','next to','alongside']),
 ('InFrontOf','in_front_of','In front of the reference.',['in front of']),
 ('Behind','behind','Behind the reference.',['behind']),
 ('Between','between','Between stated reference entities; keep their group phrase.',['between']),
 ('Around','around','Around/surrounding the reference.',['around','surrounding']),
 ('Across','across','Across the reference.',['across']),
 ('Along','along','Along the reference.',['along']),
 ('Through','through','Through the reference.',['through']),
 ('From','from','From the stated reference/origin.',['from']),
 ('Toward','toward','Toward the reference; do not assert arrival.',['toward','towards']),
 ('To','to','To the stated reference/destination; distinct from toward.',['to']),
 ('Into','into','Moving into the reference; distinct from static Inside.',['into']),
 ('OutOf','out_of','Moving out of the reference; distinct from static Outside.',['out of']),
)
SPATIAL_GUIDELINE=('Physical locations and spatial paths only. Exclude attire such as in a swimsuit, ownership, participation and figurative uses. '
 'The emitted relation class carries the qualifier. Copy subject/reference entity noun phrases, not leading spatial preposition phrases. '
 'Do not replace an unrepresented/unstated relation with At or infer a place from a typical activity.')
ACTION_DEFINITION=('The source-mentioned actor and its contiguous verbal description. Copy the full verb phrase including its stated objects, '
 'prepositions, negation and modal qualifiers. Keep the correct actor; do not assign another actor\'s separate action to this actor. '
 'This records a verbatim clause description, not resolved event actor/theme/place roles or an inferred goal, state or persistent hobby.')


def transform_plan(original):
    plan=copy.deepcopy(original)
    plan['contract_recipe']=CONTRACT_RECIPE
    plan['development_selected']=True
    plan['production_approved']=False
    plan['recipe_polarity_scope']='positive spatial claims; verbatim clauses retain their own negation without decomposition'
    positives=[schema for schema in plan['schemas'] if schema['polarity']=='positive']
    spatial=next((schema for schema in positives if schema['name']=='Location' and schema['kind']=='relation' and schema['predicate'] in {'located_at','contained_in'}),None)
    if spatial:
        plan['legacy_schemas']=copy.deepcopy(plan['schemas'])
        plan['schemas']=[{'name':name,'kind':'relation','description':description,'predicate':predicate,
                          'target_type':spatial['target_type'],'value_type':'SpatialReference',
                          'polarity':'positive','answer_role':spatial.get('answer_role','direct'),
                          'representation':'spatial_predicate_edge','lexical_cues':cues,
                          'constructor_style':'inherited_relation'}
                         for name,predicate,description,cues in SPATIAL_PALETTE]
        plan['spatial_task_guideline']=SPATIAL_GUIDELINE+' Condition scope: '+plan['condition']
        plan['spatial_palette']=[name for name,*_ in SPATIAL_PALETTE]
        plan['gate_status']='new_spatial_palette_requires_transfer_gate'
    event_bases={schema['name'] for schema in positives if schema['kind']=='event'}
    if event_bases:
        plan['legacy_event_schemas']=[copy.deepcopy(schema) for schema in plan['schemas'] if schema['kind']=='event']
        new=[];seen=set()
        for schema in plan['schemas']:
            if schema['kind']!='event':new.append(schema);continue
            if schema['polarity']!='positive':continue
            role=schema.get('answer_role','direct')
            key=(schema['target_type'],role)
            if key in seen:continue
            seen.add(key)
            new.append({'name':'ActionDescription','kind':'relation','description':ACTION_DEFINITION+' Condition scope: '+plan['condition'],
                        'predicate':'has_action_description','target_type':schema['target_type'],'value_type':'VerbalClause',
                        'polarity':'positive','answer_role':role,'representation':'verbatim_action_description'})
        plan['schemas']=new
        if plan.get('stage_contract'):
            plan['stage_contract']={stage:list(dict.fromkeys('ActionDescription' if name in event_bases else name for name in names))
                                    for stage,names in plan['stage_contract'].items()}
        plan['native_task']='+'.join(task for kind,task in (('entity','NER'),('relation','RE'),('event','EE')) if any(s['kind']==kind for s in new))
        plan['event_roles_resolved']=False
        plan['gate_status']='new_action_clause_contract_requires_transfer_gate'
    return plan


def is_plain_food(schema):
    return schema['kind']=='entity' and schema['name']=='Food' and schema['polarity']=='positive'


def spatial_argument_is_preposition_phrase(text):
    cues={cue for _,_,_,values in SPATIAL_PALETTE for cue in values}
    alternatives='|'.join(re.escape(cue).replace(r'\ ',r'\s+') for cue in sorted(cues,key=lambda value:(-len(value),value)))
    return bool(re.match(r'^(?:'+alternatives+r')\s+\S',text.strip(),re.I))
