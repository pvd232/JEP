"""Validate root assembler repairs with isolated R03/R05/R06 counterexamples.

This is a focused rework observer, not an additional independent review. It
executes the current assembler source with copied, frozen inputs. JSON output
is captured in memory; CSV/gzip writes go to an automatically deleted temporary
directory. No symlinks or canonical output paths are used.
"""
from __future__ import annotations

import collections
import contextlib
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import types


HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=HERE/'base'
SOURCE=ROOT/'inventory_work/reverse_audit/assemble_outputs.py'
SOURCE_BYTES=SOURCE.read_bytes()
SOURCE_HASH=hashlib.sha256(SOURCE_BYTES).hexdigest()
URL_RE=re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|live/))([A-Za-z0-9_-]{11})')


def load_inputs():
    aliases={'scope_decisions_initial.json':'scope_decisions.json','root_content_checks.json':'new_content_checks.json'}
    names=['scope_decisions_initial.json','reverse_mapping_review.json','crawl_manifest.json','broad_metadata_scope.json','root_content_checks.json','inventory.json','summary.json','pagination_reproduction.json','live_pagination_proof.json','standalone_replay_result.json']
    result={name:json.loads((BASE/aliases.get(name,name)).read_text()) for name in names}
    for name in ['catalog','memberships']:
        result[name+'.json']=json.loads(gzip.decompress((BASE/('public_'+name+'.json.gz')).read_bytes()))
    return result


def load_module():
    module=types.ModuleType('root_assembler_rework_observer')
    module.__file__=str(SOURCE)
    exec(compile(SOURCE_BYTES,str(SOURCE),'exec'),module.__dict__)
    return module


def edges(inventory,reverse_rows):
    forward={(r['unique_id'],vid) for r in inventory for vid in URL_RE.findall(r.get('youtube_url',''))}
    backward={(uid,r['video_id']) for r in reverse_rows for uid in r.get('transcript_ids',[])}
    return forward,backward


def fixture_inputs(inputs,mutation):
    data=dict(inputs)
    for name in ['inventory.json','scope_decisions_initial.json','reverse_mapping_review.json','broad_metadata_scope.json']:
        data[name]=copy.deepcopy(inputs[name])
    if mutation: mutation(data)
    return data


def assembly_case(inputs,name,mutation=None,error_prefix=None):
    data=fixture_inputs(inputs,mutation)
    module=load_module()
    captured={}
    with tempfile.TemporaryDirectory(prefix='jep-root-assembler-observer-') as temporary:
        module.OUT=Path(temporary)
        module.BASE=Path(temporary)/'memory_inputs'
        module.ROOT=ROOT
        module.read=lambda path:copy.deepcopy(data[Path(path).name])
        module.write=lambda filename,value:captured.__setitem__(filename,copy.deepcopy(value))
        error=None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                module.main()
            except Exception as exc:
                error={'type':type(exc).__name__,'message':str(exc)}
        output_names=sorted(p.name for p in module.OUT.iterdir())
        if error_prefix is None:
            result={'case':name,'expected':'accept valid frozen input','accepted':error is None,'error':error}
            if error is None:
                inventory=captured['inventory.json']
                videos=captured['video_inventory.json']
                forward,backward=edges(inventory,videos)
                frozen_videos=json.loads((BASE/'video_inventory.json').read_text())
                checks={
                    'source_count_93':len(inventory)==93,
                    'source_ids_unchanged':[r['unique_id'] for r in inventory]==[r['unique_id'] for r in inputs['inventory.json']],
                    'video_count_207':len(videos)==207,
                    'included_count_128':sum(r['scope_label']=='Included' for r in videos)==128,
                    'all_84_forward_reverse_edges_equal':len(forward)==84 and forward==backward,
                    'video_projection_unchanged':videos==frozen_videos,
                    'all_duration_values_unchanged':{r['video_id']:r['duration_seconds'] for r in videos}=={r['video_id']:r['duration_seconds'] for r in frozen_videos},
                    'source_inventory_unchanged':inventory==inputs['inventory.json'],
                }
                result.update(checks=checks,forward_edges=len(forward),reverse_edges=len(backward),passed=all(checks.values()))
            else:
                result['passed']=False
        else:
            no_outputs=not captured and not output_names
            result={'case':name,'expected_error_prefix':error_prefix,'accepted':error is None,'error':error,'rejected_before_any_output':no_outputs,'passed':bool(error and error['type']=='ValueError' and error['message'].startswith(error_prefix) and no_outputs)}
    return result


def main():
    baseline_manifest=json.loads((HERE/'baseline_hashes.json').read_text())['files']
    baseline_before={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in baseline_manifest}
    inputs=load_inputs()

    def promote_broad(data):
        row=next(r for r in data['broad_metadata_scope.json']['records'] if r['video_id']=='j7YryvmCbBw')
        row['scope_decision']='included'
        data['broad_metadata_scope.json']['counts']=dict(collections.Counter(r['scope_decision'] for r in data['broad_metadata_scope.json']['records']))
        data['reverse_mapping_review.json']['videos'].append({'video_id':'j7YryvmCbBw','transcript_ids':[],'coverage_status':'No supplied transcript · metadata basis','evidence':[]})

    def conflict_broad(data):
        next(r for r in data['broad_metadata_scope.json']['records'] if r['video_id']=='O25PKSrxRuA')['scope_decision']='excluded'

    def drop_edge(data):
        next(r for r in data['reverse_mapping_review.json']['videos'] if r['video_id']=='eM8ZrqhZbgQ')['transcript_ids'].remove('VV-029')

    def extra_edge(data):
        next(r for r in data['reverse_mapping_review.json']['videos'] if r['video_id']=='eM8ZrqhZbgQ')['transcript_ids'].append('VV-028')

    def duplicate_reverse(data):
        row=copy.deepcopy(next(r for r in data['reverse_mapping_review.json']['videos'] if r['video_id']=='eM8ZrqhZbgQ'))
        row['transcript_ids']=['VV-030']
        data['reverse_mapping_review.json']['videos'].append(row)

    def duplicate_other(data,name,key):
        rows=data[name][key] if key else data[name]
        rows.append(copy.deepcopy(rows[0]))

    def outside_included(data):
        for name in ['scope_decisions_initial.json','broad_metadata_scope.json']:
            next(r for r in data[name]['records'] if r['video_id']=='O25PKSrxRuA')['scope_decision']='excluded'

    results=[
        assembly_case(inputs,'baseline_valid'),
        assembly_case(inputs,'R03_broad_only_promotion',promote_broad,'Broad inclusion absent from main included map: j7YryvmCbBw'),
        assembly_case(inputs,'R03_conflicting_shared_scope',conflict_broad,'Conflicting main/broad scope decisions: O25PKSrxRuA'),
        assembly_case(inputs,'R05_missing_reverse_edge_VV029',drop_edge,'Forward/reverse edge mismatch:'),
        assembly_case(inputs,'R05_duplicate_reverse_video_id',duplicate_reverse,'Missing or duplicate reverse identifiers'),
        assembly_case(inputs,'duplicate_source_id',lambda d:duplicate_other(d,'inventory.json',None),'Missing or duplicate source identifiers'),
        assembly_case(inputs,'duplicate_main_scope_id',lambda d:duplicate_other(d,'scope_decisions_initial.json','records'),'Missing or duplicate main scope identifiers'),
        assembly_case(inputs,'duplicate_broad_scope_id',lambda d:duplicate_other(d,'broad_metadata_scope.json','records'),'Missing or duplicate broad scope identifiers'),
        assembly_case(inputs,'unexplained_extra_reverse_edge',extra_edge,'Forward/reverse edge mismatch:'),
        assembly_case(inputs,'linked_video_outside_included_scope',outside_included,'A supplied transcript video link is outside the included scope map'),
    ]
    module=load_module()
    malformed={x:module.seconds(x) for x in ['1:99','04:60:00','01:00:60']}
    valid_expectations={'0:00':0,'02:03':123,'4:59:59':17999,'25740':25740,'60:00':3600,'120:59:59':435599}
    valid_actual={x:module.seconds(x) for x in valid_expectations}
    duration={'finding':'R06-01','malformed_actual':malformed,'malformed_expected':dict.fromkeys(malformed),'valid_actual':valid_actual,'valid_expected':valid_expectations,'passed':all(v is None for v in malformed.values()) and valid_actual==valid_expectations}
    baseline_after={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in baseline_manifest}
    source_after=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    integrity={'source_hash_unchanged_during_observation':source_after==SOURCE_HASH,'frozen_input_hashes_unchanged':baseline_before==baseline_after,'all_frozen_hashes_match_manifest':baseline_after==baseline_manifest,'canonical_output_directory_used':False,'prior_review_files_written':False}
    report={
        'validation_type':'Focused post-review root assembler repair validation; not an additional review',
        'source':str(SOURCE),'source_sha256':SOURCE_HASH,'source_sha256_after':source_after,
        'baseline_commit':'620cc5eb85860ff77a837058903321876de82b15',
        'findings_validated':['R03-F2','R05-F1','R06-01'],
        'scope':'Duplicate row identifiers; main/broad conflict and promotion; exact bilateral source-video edges; included scope; malformed duration components',
        'not_reassessed':['R03-F1 territorial/format research dispositions','R05-F2 unlinked-upload classification in build_mapping_review.py'],
        'method':'Execute the exact current assembler main with deep-copied frozen JSON, in-memory JSON writes, and automatically deleted temporary CSV/gzip output; no source, canonical, frozen, or prior-review mutation',
        'assembly_cases':results,'duration_cases':duration,'integrity':integrity,
        'all_passed':all(r['passed'] for r in results) and duration['passed'] and integrity['source_hash_unchanged_during_observation'] and integrity['frozen_input_hashes_unchanged'] and integrity['all_frozen_hashes_match_manifest'],
        'observer':str(Path(__file__).resolve()),
    }
    (HERE/'root_assembler_rework.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['all_passed'] else 1


if __name__=='__main__': raise SystemExit(main())
