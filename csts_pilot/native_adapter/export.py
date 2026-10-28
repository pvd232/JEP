"""Deterministic common evidence text for downstream scoring/training exports."""

from __future__ import annotations


def canonical_text(evidence):
    """Retain source spans, local identity, binding, polarity and facet absence.

    No backend class names, prompt format, source-support quotes or capture
    provenance enter the text. This is a fixed rendering of common semantics;
    it does not certify that an extracted annotation is faithful to its source.
    """
    if evidence['status']=='adapter_unsupported':
        raise ValueError('An unsupported adapter cannot be exported as source absence')
    lines=[]
    facet=evidence.get('requested_facet_status',evidence['status'])
    if facet=='not_specified':
        lines.append('Requested facet: not specified.')
    elif facet=='ambiguous':
        origins=evidence.get('ambiguity_origins',[])
        if any('binding_unresolved' in origin for origin in origins):
            lines.append('Candidate evidence: unresolved source-span binding.')
        if 'condition_interpretations_or_unevaluated_facets' in origins:
            lines.append('Condition interpretation: unresolved.')
        if not origins:lines.append('Candidate facet prediction: ambiguous.')
    for name,status in sorted(evidence.get('facet_statuses',{}).items()):
        lines.append('Facet '+name+': '+status.replace('_',' ')+'.')
    ids={node['id'] for node in evidence['entities']}
    def prefix(item):
        context='Context: ' if item.get('answer_role')=='context' or item.get('answer_roles')==['context'] else ''
        return context+{'positive':'','negative':'Not ','uncertain':'Possibly '}[item['polarity']]
    for node in evidence['entities']:
        lines.append(prefix(node)+'['+node['id']+'] '+node['type']+': '+node['span']['text']+'.')
    for edge in evidence['relations']:
        if edge['subject'] not in ids or edge['object'] not in ids:
            raise ValueError('Evidence export contains an unbound relation')
        lines.append(prefix(edge)+'['+edge['subject']+'] '+edge['predicate']+' ['+edge['object']+'].')
    for prop in evidence.get('properties',[]):
        if prop['subject'] not in ids:raise ValueError('Evidence export contains an unbound property')
        lines.append(prefix(prop)+'['+prop['subject']+'] '+prop['predicate']+': '+prop['value']+'.')
    for event in evidence['events']:
        roles=[]
        for name,values in event['roles'].items():
            if any(identity not in ids for identity in values):
                raise ValueError('Evidence export contains an unbound event role')
            if values:roles.append(name+'='+', '.join('['+identity+']' for identity in values))
        lines.append(prefix(event)+event['predicate']+': '+event['trigger']['text']+(' ('+'; '.join(roles)+')' if roles else '')+'.')
    if 'quantity' in evidence:
        quantity=evidence['quantity'];kind=quantity['kind']
        value=('exactly '+str(quantity['lower']) if kind=='exact' else 'at least '+str(quantity['lower']) if kind=='lower_bound' else str(quantity['lower'])+' to '+str(quantity['upper']) if kind=='range' else 'unknown')
        lines.append('Count: '+value+'.')
    return '\n'.join(lines)
