#!/usr/bin/env python3
"""Observe bilateral edge preservation and conservative unlinked-upload labels.

All writes stay under this review's observer_outputs directory. Network and the
canonical inventory are unused. Exit 1 means a reproduced review finding remains.
"""
from __future__ import annotations

import argparse
import ast
import collections
import contextlib
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import types
import unicodedata


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'base'
WORK = HERE.parents[2].parent / 'reverse_audit'
URL_RE = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|live/))([\w-]{11})')


def load(path):
    """Read one frozen JSON input."""
    return json.loads(path.read_text())


def edges(inventory, reverse):
    """Return source-to-video edges and their independently stored inverse."""
    forward = {(r['unique_id'], vid) for r in inventory for vid in URL_RE.findall(r.get('youtube_url', ''))}
    backward = {(uid, r['video_id']) for r in reverse for uid in r.get('transcript_ids', [])}
    return forward, backward


def assembly_case(source, name, change=None):
    """Run the exact assembler with isolated copies and one optional mutation."""
    case = HERE / 'observer_outputs' / name
    inputs, output = case / 'inputs', case / 'outputs'
    inputs.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    aliases = {'scope_decisions_initial.json': 'scope_decisions.json', 'root_content_checks.json': 'new_content_checks.json'}
    for filename in ['scope_decisions_initial.json', 'reverse_mapping_review.json', 'crawl_manifest.json', 'broad_metadata_scope.json', 'root_content_checks.json', 'pagination_reproduction.json', 'live_pagination_proof.json', 'standalone_replay_result.json']:
        (inputs / filename).write_bytes((BASE / aliases.get(filename, filename)).read_bytes())
    for name in ['catalog', 'memberships']:
        (inputs / (name + '.json')).write_bytes(gzip.decompress((BASE / ('public_' + name + '.json.gz')).read_bytes()))
    for name in ['inventory.json', 'summary.json']:
        (output / name).write_bytes((BASE / name).read_bytes())
    if change:
        value = load(inputs / 'reverse_mapping_review.json')
        change(value)
        (inputs / 'reverse_mapping_review.json').write_text(json.dumps(value))
    module = types.ModuleType('isolated_assembly')
    module.__file__ = str(source)
    exec(compile(source.read_text(), str(source), 'exec'), module.__dict__)
    module.BASE, module.OUT, module.ROOT = inputs, output, case
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module.main()
    except Exception as exc:
        return {'accepted': False, 'error': {'type': type(exc).__name__, 'message': str(exc)}}
    forward, backward = edges(load(output / 'inventory.json'), load(output / 'video_inventory.json'))
    return {'accepted': True, 'forward_edges': len(forward), 'reverse_edges': len(backward), 'dropped_forward_edges': sorted(forward - backward), 'reverse_only_edges': sorted(backward - forward)}


def unlinked_candidate_case(source):
    """Execute the builder's actual unlinked-candidate loop, without its I/O."""
    tree = ast.parse(source.read_text(), filename=str(source))
    function_names = {'norm', 'url', 'public_date', 'public_participant'}
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in function_names]
    assignments = [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'absent' for target in node.targets)]
    loops = [node for node in tree.body if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == 'absent']
    if len(assignments) != 1 or len(loops) != 1:
        raise ValueError('Review the changed builder before adapting the observer')
    inventory = load(BASE / 'inventory.json')
    grouped = collections.defaultdict(list)
    for row in inventory:
        for vid in URL_RE.findall(row.get('youtube_url', '')):
            grouped[vid].append(row)
    candidate = {'video_id': 'SYNTHETIC01', 'scope_decision': 'included', 'exact_video_id_currently_linked': False, 'title': 'Caso 03 | Marco Fabián García Céspedes | Subcaso Casanare | 20190705'}
    namespace = {'re': re, 'unicodedata': unicodedata, 'INV': inventory, 'URL_RE': URL_RE, 'scope': {'records': [candidate]}, 'grouped': grouped, 'rows': [], 'cache': lambda _: {}}
    module = ast.fix_missing_locations(ast.Module(body=definitions + assignments + loops, type_ignores=[]))
    exec(compile(module, str(source), 'exec'), namespace)
    row = namespace['rows'][0]
    return {'fixture': 'Synthetic unlinked upload with the exact principal and date of VV-057; no content evidence', 'coverage_status': row['coverage_status'], 'related_transcript_ids': row.get('related_transcript_ids', []), 'source_anchors': row['source_anchors'], 'transcript_ids': row['transcript_ids'], 'absence_claimed': row['coverage_status'].startswith('No supplied transcript')}


def main():
    """Run the baseline, inverse-edge counterexamples and unlinked-ID observer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly', type=Path, default=BASE / 'workbook_build/assemble_outputs.py')
    parser.add_argument('--mapping', type=Path, default=HERE / 'working_build_mapping_review.py')
    args = parser.parse_args()
    baseline = assembly_case(args.assembly, 'baseline')

    def drop_edge(review):
        row = next(x for x in review['videos'] if x['video_id'] == 'eM8ZrqhZbgQ')
        row['transcript_ids'].remove('VV-029')

    def duplicate_row(review):
        row = copy.deepcopy(next(x for x in review['videos'] if x['video_id'] == 'eM8ZrqhZbgQ'))
        row['transcript_ids'] = ['VV-030']
        review['videos'].append(row)

    missing = assembly_case(args.assembly, 'missing_reverse_edge', drop_edge)
    duplicate = assembly_case(args.assembly, 'duplicate_reverse_id', duplicate_row)
    unlinked = unlinked_candidate_case(args.mapping)
    current_inventory, current_videos = load(BASE / 'inventory.json'), load(BASE / 'video_inventory.json')
    forward, backward = edges(current_inventory, current_videos)
    included = [x for x in current_videos if x['scope_label'] == 'Included']
    result = {
        'reviewed_code_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.assembly, args.mapping]},
        'baseline': baseline,
        'published_counts': {'included': len(included), 'linked_uploads': sum(bool(x['transcript_ids']) for x in included), 'no_source_content_checked': sum(x['coverage_label'] == 'No supplied transcript · content checked' for x in included), 'no_source_metadata_basis': sum(x['coverage_label'] == 'No supplied transcript · metadata basis' for x in included), 'partial_supplied_source': sum(x['coverage_label'] == 'Partial supplied transcript' for x in included), 'forward_edges': len(forward), 'reverse_edges': len(backward), 'edge_sets_equal': forward == backward},
        'missing_reverse_edge': missing,
        'duplicate_reverse_id': duplicate,
        'unlinked_candidate': unlinked,
    }
    defects = []
    if missing.get('accepted') and missing.get('dropped_forward_edges'):
        defects.append('R05-F1: reverse row omits a forward edge without rejection')
    if duplicate.get('accepted') and duplicate.get('dropped_forward_edges'):
        defects.append('R05-F1: duplicate reverse video ID silently overwrites an edge')
    if unlinked['absence_claimed']:
        defects.append('R05-F2: unlinked same-principal/same-date upload is automatically labelled absent')
    result['reproduced_findings'] = defects
    result['all_invariants_preserved'] = not defects
    (HERE / 'observations.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if defects else 0


if __name__ == '__main__':
    raise SystemExit(main())
