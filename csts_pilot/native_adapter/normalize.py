"""Normalize native typed annotations without executing generated code.

Grounding, semantic support and completeness are separate checks. Exact quoted
text is required; repeated identical substrings retain all possible offsets.
The normalizer never selects the first occurrence to invent a binding.
"""

from __future__ import annotations

import ast
import hashlib
import re

from .counts import aggregate_count, quantity_from_text
from .schema import selected_schemas, plan_digest


def _constructors(payload, plan, model, count_stage=None, profile="scoped_experimental", task_stage=None):
    """Read only a literal native annotation list and its declared constructors."""
    if model not in {"gollie", "knowcoder"}:
        raise ValueError("Unknown native model")
    if not isinstance(payload, str) or len(payload) > 65536:
        raise ValueError("Native payload must be a bounded string")
    try:
        tree = ast.parse(payload.strip(), mode="exec")
    except (SyntaxError, RecursionError) as error:
        raise ValueError("Malformed native annotation list") from error
    if len(tree.body) != 1 or sum(1 for _ in ast.walk(tree)) > 10000:
        raise ValueError("Expected one bounded native expression")
    statement = tree.body[0]
    if isinstance(statement, ast.Assign) and model == "knowcoder":
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name) or statement.targets[0].id != "results":
            raise ValueError("KnowCoder may assign only its native results list")
        node = statement.value
    elif isinstance(statement, ast.Expr):
        node = statement.value
    else:
        raise ValueError("Only a native annotation list is allowed")
    if not isinstance(node, ast.List):
        raise ValueError("Expected a literal annotation list")
    definitions = {schema["name"]: schema for schema in selected_schemas(plan, model, count_stage, profile, task_stage)}

    def decode(value, depth=0):
        if depth > 12:
            raise ValueError("Native annotation nesting is too deep")
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
        if isinstance(value, ast.List):
            return [decode(item, depth+1) for item in value.elts]
        if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
            raise ValueError("Only declared constructors, strings and role lists are allowed")
        name = value.func.id
        schema = definitions.get(name)
        if name == "Entity" and model == "knowcoder":
            kind = "entity"
        elif schema is not None:
            kind = schema["kind"]
        else:
            raise ValueError("Undeclared native constructor: " + name)
        fields = ["name"] if name == "Entity" else schema["fields"]
        if len(value.args) > len(fields):
            raise ValueError("Too many positional native arguments")
        result = {key: decode(item, depth+1) for key, item in zip(fields, value.args)}
        for item in value.keywords:
            if item.arg not in fields or item.arg in result:
                raise ValueError("Unexpected, repeated or expanded native argument")
            result[item.arg] = decode(item.value, depth+1)
        if set(result) != set(fields):
            raise ValueError("Missing native annotation fields")
        if kind == "relation":
            for role in fields:
                value = result[role]
                if model == "knowcoder" and (not isinstance(value, dict) or value["kind"] != "entity"):
                    raise ValueError("KnowCoder relation arguments require native Entity constructors")
                if model == "gollie" and not isinstance(value, str):
                    raise ValueError("GoLLIE relation fields require string spans")
        elif kind == "event":
            if not isinstance(result[fields[0]], str):
                raise ValueError("Native event triggers require string spans")
            for role in fields[1:]:
                if not isinstance(result[role], list):
                    raise ValueError("Event roles require native lists")
                for value in result[role]:
                    if model == "knowcoder" and (not isinstance(value, dict) or value["kind"] != "entity"):
                        raise ValueError("KnowCoder event roles require native Entity constructors")
                    if model == "gollie" and not isinstance(value, str):
                        raise ValueError("GoLLIE event roles require string spans")
        return {"constructor": name, "kind": kind, "fields": result}

    annotations = [decode(item) for item in node.elts]
    if any(not isinstance(item, dict) or item["constructor"] == "Entity" for item in annotations):
        raise ValueError("Top-level annotations require declared semantic types")
    return annotations


def _locations(text, passage):
    """Retain every exact substring location, without guessing occurrence identity."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("A native mention must be a nonempty string")
    starts, offset = [], 0
    while True:
        found = passage.find(text, offset)
        if found < 0:
            break
        starts.append({"start": found, "end": found + len(text)})
        offset = found + 1
    if not starts:
        raise ValueError("Native mention is not an exact source span: " + repr(text))
    return {"text": text, "candidates": starts,
            "grounding": "unique" if len(starts) == 1 else "ambiguous"}


def normalize_stages(payloads, plan, model, passage, coverage_complete=False, profile="positive_anchor"):
    """Validate separate native task captures, then project their literal union.

    This never fills a missing stage, repairs an annotation or adds a relation.
    Raw stage bytes remain separately identifiable. Support and completeness
    still require external semantic validation; a schema-valid union is not a
    proof that the group identity/coverage claims follow from the source.
    """
    count = plan["family"] == "aggregate_counts_quantities"
    stages = plan.get("aggregation", {}).get("stages") if count else list(plan.get("stage_contract") or [])
    if not stages or not isinstance(payloads, dict) or set(payloads) != set(stages):
        raise ValueError("Exactly every declared native extraction stage is required")
    elements = []
    for stage in stages:
        kwargs = {"count_stage" if count else "task_stage": stage}
        _constructors(payloads[stage],plan,model,profile=profile,**kwargs)
        statement = ast.parse(payloads[stage].strip(),mode="exec").body[0]
        elements.extend(statement.value.elts)
    literal = "[" + ",".join(ast.unparse(element) for element in elements) + "]"
    evidence = normalize_native(literal,plan,model,passage,coverage_complete=coverage_complete,profile=profile)
    evidence["stage_merge"] = "literal_union_after_each_stage_schema_validation"
    evidence["stage_inputs_sha256"] = {stage:hashlib.sha256(payloads[stage].encode()).hexdigest() for stage in stages}
    if plan.get('facet_stage_contract'):
        _facet_statuses(evidence,plan,_constructors(literal,plan,model,profile=profile),set(stages))
    return evidence


def _facet_statuses(evidence,plan,annotations,evaluated_stages):
    """Keep alternative condition readings distinct rather than merging answers."""
    if not plan.get('facet_stage_contract'):return
    names={item['constructor'] for item in annotations}
    facets={}
    for facet,stage in plan['facet_stage_contract'].items():
        allowed=set(plan['facet_schemas'][facet])
        present=any(name.removeprefix('Negated').removeprefix('Uncertain') in allowed for name in names)
        facets[facet]='answered' if present else 'not_specified' if stage in evaluated_stages else 'not_evaluated'
    evidence['facet_statuses']=facets
    values=set(facets.values())
    overall='answered' if values=={'answered'} else 'not_specified' if values=={'not_specified'} else 'ambiguous'
    evidence['ambiguity_origins']=[item for item in evidence.get('ambiguity_origins',[]) if item!='condition_interpretations_or_unevaluated_facets']
    evidence['issues']=[item for item in evidence['issues'] if item!='condition_readings_have_distinct_or_unevaluated_facet_statuses']
    if overall=='ambiguous':evidence['ambiguity_origins'].append('condition_interpretations_or_unevaluated_facets')
    if evidence.get('candidate_grounding_status')=='ambiguous':overall='ambiguous'
    evidence['requested_facet_status']=overall
    evidence['status']=overall
    if overall=='ambiguous':
        evidence['issues']=sorted(set(evidence['issues']+['condition_readings_have_distinct_or_unevaluated_facet_statuses']))


def normalize_native(payload, plan, model, passage, coverage_complete=False, count_stage=None, profile="scoped_experimental", task_stage=None):
    """Preserve typed mentions, bindings and counts as a common evidence graph.

    coverage_complete is a caller assertion after semantic coverage validation;
    it defaults false. Model output syntax and span occurrence alone cannot
    establish that every target entity or group has been extracted.
    """
    if type(coverage_complete) is not bool:
        raise ValueError("Coverage validation must be explicitly boolean")
    evidence = {"condition": plan["condition"], "family": plan["family"],
                "plan_sha256": plan_digest(plan), "status": "adapter_unsupported",
                "entities": [], "relations": [], "events": [], "issues": [],
                "properties": [],
                "coverage_validated": coverage_complete,
                "semantic_support_validated": False}
    evidence['requested_facet_status_kind']='candidate_prediction'
    evidence['ambiguity_origins']=[]
    if not plan["supported"]:
        evidence["unsupported_reason"] = plan["unsupported_reason"]
        return evidence
    if not isinstance(passage, str) or not passage.strip():
        raise ValueError("A nonempty source passage is required")
    definitions = {schema["name"]: schema for schema in selected_schemas(plan, model, count_stage, profile, task_stage)}
    annotations = _constructors(payload, plan, model, count_stage, profile, task_stage)
    evidence["capability_profile"] = profile
    evidence["schema_stage"] = count_stage or ("merged_projection_unverified" if plan["family"] == "aggregate_counts_quantities" else "ordinary")
    evidence["task_stage"] = task_stage or ("merged_projection_unverified" if plan.get("stage_contract") else None)
    direct = any(definitions[item['constructor']].get('answer_role','direct')=='direct' for item in annotations)
    evidence["status"] = "answered" if direct else "not_specified"
    evidence["requested_facet_status"] = evidence['status']
    evidence["context_annotations_present"] = any(definitions[item['constructor']].get('answer_role')=='context' for item in annotations)
    grounded, by_id = {}, {}

    def entity(value, expected_type, polarity, origin, properties=None, property_polarity=None, answer_role='direct'):
        if isinstance(value, dict):
            if value["kind"] != "entity":
                raise ValueError("A native entity role cannot contain a relation/event")
            name = value["constructor"]
            if name != "Entity" and definitions[name]["target_type"] != expected_type:
                raise ValueError("Entity type disagrees with its declared argument role")
            value = value["fields"]["name" if model == "knowcoder" else "span"]
        mention = _locations(value, passage)
        if properties:
            candidates=[span for span in mention['candidates']
                        if not (value[0].isalnum() and span['start']>0 and passage[span['start']-1].isalnum())
                        and not (value[-1].isalnum() and span['end']<len(passage) and passage[span['end']].isalnum())]
            if not candidates:
                raise ValueError('Lexical property cue is not a complete source token/span')
            mention.update(candidates=candidates,grounding='unique' if len(candidates)==1 else 'ambiguous')
        if plan["family"] == "aggregate_counts_quantities" and ":" in origin.removeprefix("annotation:"):
            # A relation argument must not manufacture a positive duplicate of
            # an uncertain/negative group mentioned by the NER stage. Process
            # all standalone entities first so annotation order cannot alter
            # the polarity join.
            candidates = [node for node in evidence["entities"]
                          if node["type"] == expected_type and node["span"] == mention]
            if len(candidates) == 1:
                candidates[0]["annotation_origins"].append(origin)
                candidates[0]['answer_roles']=sorted(set(candidates[0]['answer_roles']+[answer_role]))
                return candidates[0]["id"]
            if len(candidates) > 1:
                raise ValueError("Count relation has an unresolved scoped-mention join")
            if expected_type != "Quantity":
                polarity = "uncertain"
                evidence["issues"].append("count_relation_without_scoped_group_annotation")
        for prop in properties or []:
            if prop["predicate"] == "sex_or_gender":
                tokens = set(re.findall(r"[a-z]+", value.casefold()))
                allowed = {"male": {"man", "men", "boy", "boys", "male"},
                           "female": {"woman", "women", "girl", "girls", "female"}}[prop["value"]]
                if not tokens & allowed:
                    raise ValueError("Gender type lacks a declared lexical source cue")
                if property_polarity == "negative" and prop["value"] not in tokens:
                    raise ValueError("Negated noun typing cannot imply denial of the broader gender category")
        if mention["grounding"] == "unique":
            span = mention["candidates"][0]
            key = (expected_type, span["start"], span["end"], polarity)
            if key in grounded:
                node = by_id[grounded[key]]
                node["annotation_origins"].append(origin)
                node['answer_roles']=sorted(set(node['answer_roles']+[answer_role]))
                return node["id"]
        else:
            key = None
            evidence["issues"].append("ambiguous_repeated_source_span")
        identity = "e" + str(len(evidence["entities"]))
        node = {"id": identity, "type": expected_type, "span": mention,
                "polarity": polarity, "quantity": quantity_from_text(value),
                "annotation_origins": [origin], 'answer_roles':[answer_role]}
        evidence["entities"].append(node)
        by_id[identity] = node
        if key is not None:
            grounded[key] = identity
        return identity

    def hull(*identities):
        spans = [by_id[identity]["span"] for identity in identities]
        if any(span["grounding"] != "unique" for span in spans):
            return {"text": None, "grounding": "ambiguous", "candidates": []}
        start = min(span["candidates"][0]["start"] for span in spans)
        end = max(span["candidates"][0]["end"] for span in spans)
        return {"text": passage[start:end], "grounding": "unique",
                "candidates": [{"start": start, "end": end}]}

    ordered = sorted(enumerate(annotations), key=lambda item: item[1]["kind"] != "entity")
    for index, annotation in ordered:
        schema, fields = definitions[annotation["constructor"]], annotation["fields"]
        polarity = schema["polarity"]
        answer_role=schema.get('answer_role','direct')
        if schema["kind"] == "entity":
            # Gender is a lexical property of a source mention. Denying a
            # category does not deny the person's existence.
            node_polarity = "positive" if schema.get("canonical_properties") else polarity
            identity = entity(annotation, schema["target_type"], node_polarity, f"annotation:{index}", schema.get("canonical_properties"), polarity,answer_role)
            for prop in schema.get("canonical_properties", []):
                evidence["properties"].append({**prop, "subject": identity, "polarity": polarity,
                                               "source_span": by_id[identity]["span"],
                                               'answer_role':answer_role,
                                               "support": "declared_lexical_typing"})
        elif schema["kind"] == "relation":
            head, tail = (fields[key] for key in schema["fields"])
            # The edge carries attribute negation/uncertainty. "The dog is not
            # brown" still mentions a present dog. Count joins remain a
            # separately gated scope-composition problem.
            subject = entity(head, schema["target_type"], "positive", f"annotation:{index}:subject",answer_role=answer_role)
            obj = entity(tail, schema["value_type"], "positive", f"annotation:{index}:object",answer_role=answer_role)
            evidence["relations"].append({"predicate": schema["predicate"], "subject": subject,
                                          "object": obj, "polarity": polarity,
                                          'answer_role':answer_role,
                                          "support_span": hull(subject, obj)})
        else:
            trigger = _locations(fields["mention" if model == "gollie" else "trigger"], passage)
            roles = {}
            for role, expected in (("actor", schema["target_type"]), ("theme", "Entity"), ("place", "Location")):
                if not isinstance(fields[role], list):
                    raise ValueError("Event roles require native lists")
                roles[role] = [entity(item, expected, "positive", f"annotation:{index}:{role}",answer_role=answer_role) for item in fields[role]]
            evidence["events"].append({"type": schema["name"], "predicate": schema["predicate"],
                                       "trigger": trigger, "roles": roles, "polarity": polarity,'answer_role':answer_role})

    if plan["family"] == "aggregate_counts_quantities":
        target = plan["schemas"][0]["target_type"]
        groups = [node for node in evidence["entities"] if node["type"] == target]
        graph_relations, quantity_conflicts = [], []
        for relation in evidence["relations"]:
            predicate = relation["predicate"]
            if predicate in {"same_referent", "distinct_from", "part_of"}:
                graph_relations.append({key: relation[key] for key in ("predicate", "subject", "object")})
            elif predicate == "has_quantity":
                group, quantity_node = by_id[relation["subject"]], by_id[relation["object"]]
                quantity = quantity_from_text(quantity_node["span"]["text"])
                old = group["quantity"]
                if quantity["kind"] == "unknown":
                    quantity_conflicts.append("uninterpretable_quantity_span")
                elif old["kind"] == "exact" and quantity["kind"] == "exact" and old["lower"] != quantity["lower"]:
                    quantity_conflicts.append("quantity_binding_conflict")
                elif quantity["kind"] == "exact" and old["lower"] is not None and quantity["lower"] < old["lower"]:
                    quantity_conflicts.append("quantity_binding_conflict")
                else:
                    group["quantity"] = quantity
        count = aggregate_count(groups, graph_relations, coverage_complete=coverage_complete)
        if quantity_conflicts or "ambiguous_repeated_source_span" in evidence["issues"]:
            count.update(kind="unknown", lower=None, upper=None)
            count["issues"] = sorted(set(count["issues"] + quantity_conflicts + evidence["issues"]))
        evidence["quantity"] = count
    if "ambiguous_repeated_source_span" in evidence["issues"] or any(event["trigger"]["grounding"] == "ambiguous" for event in evidence["events"]):
        evidence["status"] = "ambiguous"
        if direct:evidence["requested_facet_status"] = 'ambiguous'
    if 'ambiguous_repeated_source_span' in evidence['issues']:
        evidence['ambiguity_origins'].append('candidate_entity_binding_unresolved')
    if any(event['trigger']['grounding']=='ambiguous' for event in evidence['events']):
        evidence['ambiguity_origins'].append('candidate_event_trigger_binding_unresolved')
    evidence['candidate_grounding_status']='ambiguous' if evidence['ambiguity_origins'] else 'unique' if annotations else 'not_applicable'
    evidence["issues"] = sorted(set(evidence["issues"]))
    _facet_statuses(evidence,plan,annotations,{task_stage} if task_stage is not None else set())
    return evidence
