"""Condition-only contracts for descriptive facets outside the ordinary anchors.

These contracts are proposals. They extend route coverage, not model fidelity.
Each stage is a native Entity, Relation or Event task with an explicit scope;
there is no anonymous answer field or source-dependent schema construction.
"""

from __future__ import annotations

import re


def _schema(name, kind, description, target, predicate=None, value_type=None, answer_role="direct"):
    return {"name": name, "kind": kind, "description": description,
            "target_type": target, "predicate": predicate,
            "value_type": value_type, "polarity": "positive", "answer_role": answer_role}


def extension_route(condition, text):
    """Return a finite reviewed condition contract, never an answer to a source."""
    def route(family, task, schemas, scope, stages=None):
        return {"family": family, "native_task": task, "supported": True,
                "gate_status": "new_scope_contract_requires_development_gates",
                "scope": scope, "schemas": schemas,
                "semantic_gates_required": ["minimal_positive_anchor", "source_absence",
                                             "binding_and_scope_counterexample", "explicit_negation_or_uncertainty"],
                "stage_contract": stages,
                "interpretation_status": "candidate_condition_scope_requires_development_review",
                "coverage_complete": False}

    def ner(name, category, scope):
        return route("unary_typed_mentions", "NER",
                     [_schema(name, "entity", scope, category)], scope)

    def relation(name, target, predicate, value_type, scope):
        return route("binary_properties_locations", "RE",
                     [_schema(name, "relation", scope, target, predicate, value_type)], scope)

    def with_context(value, contexts, stage_name, facet):
        direct_names=[schema['name'] for schema in value['schemas']]
        value['schemas']=contexts+value['schemas']
        value['stage_contract']={}
        for name, schemas in contexts_by_stage(contexts).items():
            value['stage_contract'][name]=schemas
        value['stage_contract'][stage_name]=direct_names
        value['native_task']='+'.join(task for kind,task in (('entity','NER'),('relation','RE'),('event','EE'))
                                      if any(s['kind']==kind for s in value['schemas']))
        value['family']='other'
        value['requested_facet']=facet
        value['context_does_not_establish_requested_facet']=True
        return value

    def contexts_by_stage(contexts):
        return {('observed_mentions' if kind=='entity' else 'observed_activity'):
                [schema['name'] for schema in contexts if schema['kind']==kind]
                for kind in ('entity','event') if any(schema['kind']==kind for schema in contexts)}

    def observed_activity(actor='Person'):
        return _schema('ActivityEvent','event','An explicitly observed activity relevant to the requested condition. Preserve trigger, actor, theme and place. This annotation records the observed action only; it does not establish any unstated goal, attention state or persistent hobby.',actor,'activity',answer_role='context')

    if re.fullmatch(r"(?:means|method|mode) of transportation", text):
        return ner("TransportMode", "TransportMode", "A source-mentioned means of travel, including a named conveyance or an explicitly described mode such as walking, cycling or driving. Copy the travel-mode phrase. Do not infer a vehicle or activity that the sentence does not establish.")
    if text == "type of play":
        scope = "An explicitly mentioned play activity. Preserve its action trigger, participants, play object/theme and stated setting. Mere presence of a toy or child does not establish play. Do not infer a persistent hobby."
        return route("actions_events", "EE", [_schema("PlayEvent", "event", scope, "Entity", "play_activity")], scope)
    scene = {
        "contents of bathroom": ("BathroomItem", "Object", "Source-mentioned fixtures, furnishings or objects explicitly in the bathroom/restroom. Keep item qualifiers and quantities; do not infer standard bathroom fixtures."),
        "background features": ("BackgroundFeature", "SceneFeature", "Features explicitly located in the background or described as the textual setting. Preserve spatial/context qualifiers. A foreground subject is not automatically a background feature."),
        "environment": ("EnvironmentFeature", "SceneFeature", "Explicit textual setting/environment features or descriptions, including stated terrain, weather, vegetation, structures and indoor/outdoor setting. Do not invent scenery or infer location from a typical activity."),
        "nature of place": ("PlaceCharacteristic", "SceneFeature", "Explicitly stated place type and physical setting characteristics. Preserve modifiers. Do not infer a place category solely from a stereotypical object or activity."),
    }
    if text in scene:
        return ner(*scene[text])
    if text == "design of bathroom":
        return relation("HasDesignFeature", "Location", "design_feature", "DesignFeature", "A source-mentioned bathroom/restroom and one of its explicitly described design/layout/material/style features. Quote both room and feature spans; do not infer an architectural style from an ordinary fixture.")
    if text == "substance on ground":
        return relation("GroundSubstance", "Ground", "covered_by", "Substance", "The explicitly mentioned ground/surface and a substance stated to cover, lie on, or form that surface. Keep the surface-to-substance binding. Do not infer a ground covering merely from a place or season.")
    if text == "items used by people":
        scope = "Preserve source-mentioned human-use item categories separately from actual participation/use. A lexical item category is not evidence that an absent person is using it."
        value = route("other", "NER+RE", [
            _schema("HumanUseItem", "entity", "An explicitly named tool, personal item, furnishing, appliance, instrument or other lexical category designed for human use. Copy its source span. This class categorizes the item; it does not assert any actual user, ownership or use event.", "Object"),
            _schema("Uses", "relation", "A person/group and an object explicitly used, operated, carried as a tool, or manipulated by that person in the source. Keep the correct user-item binding. Mere proximity or ownership does not establish use.", "Person", "uses", "Object"),
        ], scope, {"item_categories": ["HumanUseItem"], "explicit_use": ["Uses"]})
        value["alternative_interpretations"] = ["Which human-use item categories occur?", "Who is explicitly using which item?"]
        value['facet_stage_contract']={'item_categories':'item_categories','actual_use':'explicit_use'}
        value['facet_schemas']={'item_categories':['HumanUseItem'],'actual_use':['Uses']}
        return value
    if text in {"object's purpose", "purpose of running"}:
        target = "Object" if text == "object's purpose" else "Activity"
        value=relation("HasPurpose", target, "explicit_purpose", "Goal", "The requested " + target + " and an explicitly stated purpose/goal clause (for example a textual for/to/in-order-to construction establishing purpose). Preserve the goal clause. Typical object functions, causes, observed action alone and speculation do not establish purpose.")
        contexts=[observed_activity('Entity')]
        if target=='Object':
            contexts.insert(0,_schema('Object','entity','An explicitly mentioned object relevant to the purpose question. Preserve noun modifiers; naming an object does not establish its purpose.','Object',answer_role='context'))
        return with_context(value,contexts,'explicit_purpose','purpose')
    if text == "people's immediate attention":
        value=relation("AttendsTo", "Person", "explicit_attention_target", "AttentionTarget", "A person/group and the target explicitly watched, looked at, focused on or attended to in the source. Keep each subject-target binding. Do not infer attention from being near an object or merely facing the same scene.")
        return with_context(value,[observed_activity()],'explicit_attention','attention')
    if text == "sweetness of food":
        value=relation("HasSweetness", "Food", "explicit_sweetness", "SweetnessDescription", "A source-mentioned food and its explicit sweetness/taste description. A cake, fruit or dessert name alone does not establish sweetness. Preserve denial and uncertainty only in a separately gated polarity profile.")
        context=_schema('Food','entity','An explicitly mentioned food relevant to the condition. Preserve its source name/modifiers. Naming a dessert or fruit does not establish sweetness.','Food',answer_role='context')
        return with_context(value,[context],'explicit_sweetness','sweetness')
    if text == "type of hobby":
        value=relation("HasHobby", "Person", "explicit_hobby", "Hobby", "A person/group and an activity explicitly characterized as that person's hobby or habitual pastime. An observed activity or sport alone is insufficient. Copy person and hobby spans from the source.")
        return with_context(value,[observed_activity()],'explicit_hobby','hobby')
    if text == "quantity of food":
        value = relation("FoodAmount", "Food", "explicit_food_amount", "QuantityPhrase", "A food item/group and its explicitly stated amount, count or unit-bearing quantity phrase. Preserve units such as slices, pieces, portions or mass, exactness and uncertainty. Do not sum unlike units, convert portions to mass, or infer an amount from a food name. No automatic numeric total is projected.")
        value["quantity_projection"] = "verbatim_units_only_no_numeric_aggregation"
        context=_schema('Food','entity','Each explicitly mentioned food item/group, preserving the full noun phrase and its quantities/units. Do not invent a mass or combine different units.','Food',answer_role='context')
        return with_context(value,[context],'explicit_amount','food_amount')
    if text == "man with food":
        value = relation("FoodContext", "Person", "food_context", "Food", "A source-mentioned man/person and food explicitly associated by stated spatial presence, looking at, holding, possession or eating. Preserve the person-food binding and original support wording. This broad context relation alone does not assert ownership, holding or eating; food in front of a man establishes only the stated context.")
        value["alternative_interpretations"] = ["Person with food in the explicitly described context", "Ownership/consumption only when separately stated"]
        value["relation_does_not_imply"] = ["owns", "eats", "holds"]
        return value
    if text == "train on track":
        return relation("OnTrack", "Vehicle", "on_rail_track", "RailTrack", "A source-mentioned train and the rail track explicitly supporting or traversed by that train. Preserve qualifiers and binding. A train mention alone does not establish a visible/stated track.")
    if text in {"person", "rider"}:
        schemas = [_schema("Person" if text == "person" else "Rider", "entity", "An explicitly mentioned " + text + " or referential group, with its source noun modifiers and quantities. Keep distinct referents separate; do not infer demographic or activity attributes from stereotypes.", "Person")]
        if text == "rider":
            schemas.append(_schema("Rides", "relation", "A rider and the explicitly ridden animal, conveyance or board. The mount must be stated and bound to this rider; do not invent a bicycle from the word rider.", "Person", "rides", "Mount"))
            stages = {"subjects": ["Rider"], "riding": ["Rides"]}
        else:
            schemas.extend([
                _schema("Wears", "relation", "A source-mentioned person and clothing explicitly worn by that person. Keep the subject-clothing binding and qualifiers.", "Person", "wears", "Clothing"),
                _schema("ActivityEvent", "event", "An explicit action involving the requested person, preserving trigger, actor, object/theme and stated setting. Do not infer a persistent hobby or unstated purpose.", "Person", "activity"),
            ])
            stages = {"subjects": ["Person"], "clothing": ["Wears"], "actions": ["ActivityEvent"]}
        return route("other", "NER+RE" if text == "rider" else "NER+RE+EE", schemas,
                     "Explicit descriptions of the requested subject, extracted through separate native task stages. Every stage has its own fidelity gate; a subject mention does not establish complete attribute/event coverage.", stages)
    return None
