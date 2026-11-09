"""Finite semantic anchor gates, separate from native Python syntax validity."""

from __future__ import annotations

import json

from .normalize import normalize_native
from .schema import compile_condition, plan_digest


def model_inputs(cases):
    """Expose source/condition plans only; reference annotations never enter prompts."""
    result = []
    for case in cases:
        plan = compile_condition(case["condition"],contract_recipe=case.get('contract_recipe'))
        result.append({"case_id": case["case_id"], "source_id": case["source_id"],
                       "passage": case["passage"], "condition": case["condition"],
                       "profile": case.get("profile", "positive_anchor"),
                       **({'contract_recipe':case['contract_recipe']} if case.get('contract_recipe') else {}),
                       "plan": plan, "plan_sha256": plan_digest(plan)})
    return result


def semantic_view(evidence):
    """Compare typed meanings and argument bindings rather than local node IDs."""
    nodes = {node["id"]: node for node in evidence["entities"]}
    entities = sorted((node["type"], node["span"]["text"], node["polarity"])
                      for node in nodes.values())
    relations = sorted((relation["predicate"], nodes[relation["subject"]]["span"]["text"],
                        nodes[relation["object"]]["span"]["text"], relation["polarity"])
                       for relation in evidence["relations"])
    events = []
    for event in evidence["events"]:
        roles = {name: sorted(nodes[identity]["span"]["text"] for identity in identities)
                 for name, identities in event["roles"].items()}
        events.append((event["predicate"], event["trigger"]["text"], roles, event["polarity"]))
    return {"status": evidence["status"], "entities": entities, "relations": relations,
            "properties": sorted((prop["predicate"], nodes[prop["subject"]]["span"]["text"], prop["value"], prop["polarity"])
                                 for prop in evidence.get("properties", [])),
            "events": sorted(events, key=lambda value: json.dumps(value, sort_keys=True)),
            "quantity": {key: evidence["quantity"][key] for key in ("kind", "lower", "upper")}
                        if "quantity" in evidence else None}


def check_case(case, payload, model):
    """Check minimal anchors without treating correct extra facts as errors.

    Extra annotations and boundary-equivalent spans require semantic review.
    Exact graph equality is reported separately, never a completeness oracle.
    These exposed smoke cases cannot establish family-wide model fidelity.
    """
    plan = compile_condition(case["condition"],contract_recipe=case.get('contract_recipe'))
    if case["plan_sha256"] != plan_digest(plan):
        raise ValueError("Development gate plan changed")
    profile = case.get("profile", "positive_anchor")
    expected = normalize_native(case["expected_native_annotations"][model], plan, model, case["passage"], profile=profile)
    if "independent_expected_entity_types" in case and sorted({node["type"] for node in expected["entities"]}) != sorted(case["independent_expected_entity_types"]):
        raise ValueError("Development reference disagrees with its independently stated typed contract")
    try:
        actual = normalize_native(payload, plan, model, case["passage"], profile=profile)
    except ValueError as error:
        return {"case_id": case["case_id"], "passed": False, "failure": "invalid_native_evidence",
                "reason": str(error)}
    expected_view, actual_view = semantic_view(expected), semantic_view(actual)
    matches = expected_view == actual_view
    anchors = all(set(expected_view[key]).issubset(set(actual_view[key]))
                  for key in ("entities", "relations", "properties"))
    for predicate, trigger, roles, polarity in expected_view["events"]:
        anchors = anchors and any(
            (predicate, trigger, polarity) == (apredicate, atrigger, apolarity)
            and all(set(values).issubset(set(aroles.get(role, []))) for role, values in roles.items())
            for apredicate, atrigger, aroles, apolarity in actual_view["events"])
    return {"case_id": case["case_id"], "passed": anchors,
            "minimal_anchor_recovered": anchors, "strict_graph_match": matches,
            "semantic_review_required": not matches,
            "completeness_established": False,
            "failure": None if anchors else "anchor_not_confirmed_requires_semantic_review",
            "expected": expected_view, "actual": actual_view}
