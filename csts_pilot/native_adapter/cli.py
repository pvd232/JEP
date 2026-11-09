"""Offline normalize/export CLI; model execution proof stays in the outer runner.

Input is a source capture record or list of records. Required fields: source_id,
condition, passage, model and raw_output (or stage_outputs). Optional profile,
task_stage/count_stage and runtime_status. No model is called. The raw record,
source, helper identities and external protocol identifier are retained; this
utility does not independently verify the model/checkpoint execution receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .export import canonical_text
from .normalize import normalize_native,normalize_stages
from .schema import compile_condition,encoded,implementation_identity,plan_digest
from .runtime import PINNED_MODELS,descriptor


def normalize_record(record):
    """Keep unsupported/runtime/parse failures in place, with retained raw input."""
    source={key:record[key] for key in ('source_id','condition','passage','model')}
    if any(not isinstance(value,str) or not value.strip() for value in source.values()):
        raise ValueError('Source identity, condition, passage and model must be nonempty strings')
    plan=compile_condition(source['condition'],contract_recipe=record.get('contract_recipe'))
    runtime=record.get('runtime_status','ok')
    if runtime not in {'ok','error','unsupported','truncated'}:
        raise ValueError('Unknown runtime status')
    profile=record.get('profile','positive_anchor')
    raw={**source,'profile':profile,'runtime_status':runtime,
         'task_stage':record.get('task_stage'),'count_stage':record.get('count_stage'),
         'contract_recipe':record.get('contract_recipe'),
         'external_protocol_sha256':record.get('external_protocol_sha256')}
    if 'raw_output' in record:raw['raw_output']=record['raw_output']
    if 'stage_outputs' in record:raw['stage_outputs']=record['stage_outputs']
    result={'source_id':source['source_id'],'condition':source['condition'],
            'route_designed':plan['supported'],'route_production_approved':False,
            'runtime_status':runtime,'parse_valid':False,'coverage_complete':False,
            'normalized_evidence':None,'error':None,'raw_capture':raw,
            'raw_capture_sha256':hashlib.sha256(encoded(raw)).hexdigest(),
            'plan_sha256':plan_digest(plan),'implementation_sha256':implementation_identity(),
            'external_protocol_verified':False}
    if runtime!='ok':
        result['error']='Retained operational failure: '+runtime
        return result
    if not plan['supported']:
        result['runtime_status']='unsupported'
        result['error']='Adapter unsupported: '+plan['unsupported_reason']
        return result
    try:
        if ('raw_output' in raw)==('stage_outputs' in raw):
            raise ValueError('Exactly one raw_output or complete stage_outputs mapping is required')
        if 'stage_outputs' in raw:
            evidence=normalize_stages(raw['stage_outputs'],plan,source['model'],source['passage'],profile=profile)
        else:
            evidence=normalize_native(raw['raw_output'],plan,source['model'],source['passage'],profile=profile,
                                      task_stage=raw['task_stage'],count_stage=raw['count_stage'])
        result.update(parse_valid=True,normalized_evidence=evidence)
    except (ValueError,TypeError,RecursionError) as error:
        result['error']=str(error)
    return result


def export_record(result):
    """Reconstruct normalization; never trust a stored successful parsed object."""
    reconstructed=normalize_record(result['raw_capture'])
    if reconstructed!=result:
        raise ValueError('Stored normalization/helper/source identity changed')
    evidence=result['normalized_evidence']
    return {'source_id':result['source_id'],'condition':result['condition'],
            'status':evidence['status'] if evidence is not None else result['runtime_status'] if result['runtime_status']!='ok' else 'parse_failure',
            'canonical_evidence':canonical_text(evidence) if evidence is not None else None,
            'runtime_status':result['runtime_status'],'parse_valid':result['parse_valid'],
            'coverage_complete':False,'error':result['error'],
            'semantic_support_validated':False,'route_production_approved':False,
            'requested_facet_status_kind':'candidate_prediction',
            'requested_facet_status':evidence.get('requested_facet_status') if evidence else None,
            'facet_statuses':evidence.get('facet_statuses',{}) if evidence else {},
            'context_annotations_present':evidence.get('context_annotations_present',False) if evidence else False,
            'contract_recipe':evidence.get('contract_recipe') if evidence else result['raw_capture'].get('contract_recipe'),
            'resolved_event_role_claims':evidence.get('resolved_event_role_claims') if evidence else None,
            'candidate_grounding_status':evidence.get('candidate_grounding_status','not_applicable') if evidence else 'not_applicable',
            'ambiguity_origins':evidence.get('ambiguity_origins',[]) if evidence else [],
            'external_protocol_sha256':result['raw_capture']['external_protocol_sha256'],
            'external_protocol_verified':False,'raw_capture_sha256':result['raw_capture_sha256']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    compile_parser=sub.add_parser('compile');compile_parser.add_argument('--condition',required=True)
    compile_parser.add_argument('--contract-recipe',default=None)
    runtime_parser=sub.add_parser('descriptor');runtime_parser.add_argument('--model-alias',choices=tuple(PINNED_MODELS),required=True)
    for command in ('normalize','export'):
        child=sub.add_parser(command);child.add_argument('--input',type=Path,required=True);child.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='compile':
        print(json.dumps(compile_condition(args.condition,contract_recipe=args.contract_recipe),ensure_ascii=False,indent=2));return
    if args.command=='descriptor':
        print(json.dumps(descriptor(args.model_alias),ensure_ascii=False,indent=2));return
    value=json.loads(args.input.read_text(),parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON is not allowed')))
    records=value if isinstance(value,list) else [value]
    result=[normalize_record(row) if args.command=='normalize' else export_record(row) for row in records]
    content=(json.dumps(result,ensure_ascii=False,indent=2)+'\n') if args.command=='normalize' else ''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in result)
    with args.output.open('x') as handle:handle.write(content)


if __name__=='__main__':main()
