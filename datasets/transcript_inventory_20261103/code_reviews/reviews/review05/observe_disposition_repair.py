#!/usr/bin/env python3
"""Check R05-F2 rework without importing or running the top-level builder.

Execute only its pure definitions and isolated candidate/validation loops. All
inputs come from the frozen review snapshot; only this observer's receipt is
written. No raw captions or source text are needed.
"""
from __future__ import annotations

import argparse
import ast
import collections
import copy
import hashlib
import json
from pathlib import Path
import re
import unicodedata


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'base'
ROOT = HERE.parents[2]
DEFAULT_BUILDER = ROOT / 'reverse_audit/build_mapping_review.py'
DEFAULT_LEDGER = ROOT / 'reverse_audit/accepted_reverse_dispositions.json'
URL_RE = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|live/))([\w-]{11})')


def read(path):
    """Read one explicit JSON fixture."""
    return json.loads(path.read_text())


def compiled_nodes(nodes, source):
    """Compile selected existing code without executing module-level I/O."""
    return compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(source), 'exec')


def prepare(source, ledger_path, inventory):
    """Bind pure builder functions to frozen metadata and the proposed ledger."""
    tree = ast.parse(source.read_text(), filename=str(source))
    names = {'norm', 'url', 'public_date', 'public_participant', 'source_session_index_fingerprint', 'validate_absence_ledger', 'accepted_absence'}
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in definitions} != names:
        raise ValueError('Expected rework functions are missing; inspect the candidate')
    review = read(BASE / 'reverse_mapping_review.json')
    by_video = {row['video_id']: row for row in review['videos']}
    namespace = {'json': json, 'hashlib': hashlib, 're': re, 'unicodedata': unicodedata, 'INV': inventory, 'URL_RE': URL_RE, 'ABSENCE_LEDGER_PATH': ledger_path, 'BY_UID': {row['unique_id']: row for row in inventory}, 'cache': lambda vid: {'title': by_video[vid]['title']} if vid in by_video else {}}
    exec(compiled_nodes(definitions, source), namespace)
    namespace['ABSENCE_LEDGER'] = read(ledger_path)
    namespace['ACCEPTED_ABSENCES'] = namespace['validate_absence_ledger'](namespace['ABSENCE_LEDGER'], inventory)
    grouped = collections.defaultdict(list)
    for row in inventory:
        for vid in URL_RE.findall(row.get('youtube_url', '')):
            grouped[vid].append(row)
    namespace['grouped'] = grouped
    selections = [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'absent' for target in node.targets)]
    candidate_loops = [node for node in tree.body if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == 'absent']
    final_loops = [node for node in tree.body if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == 'rows']
    if len(selections) != 1 or len(candidate_loops) != 1 or len(final_loops) != 1:
        raise ValueError('Builder structure changed; inspect observer boundary')
    return namespace, compiled_nodes(selections + candidate_loops, source), compiled_nodes(final_loops, source)


def candidates(namespace, code, records):
    """Run only the candidate loop against a supplied scope fixture."""
    namespace['scope'] = {'records': records}
    namespace['rows'] = []
    exec(code, namespace)
    return namespace['rows']


def main():
    """Verify preserved accepted decisions and the previously failing boundary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--builder', type=Path, default=DEFAULT_BUILDER)
    parser.add_argument('--ledger', type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()
    inventory = read(BASE / 'inventory.json')
    scope = read(BASE / 'scope_decisions.json')
    namespace, candidate_code, final_code = prepare(args.builder, args.ledger, inventory)
    ledger = namespace['ABSENCE_LEDGER']
    checks = []

    def check(name, passed, detail):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})

    baseline = candidates(namespace, candidate_code, scope['records'])
    accepted = set(namespace['ACCEPTED_ABSENCES'])
    baseline_ids = {row['video_id'] for row in baseline if row['coverage_status'].startswith('No supplied transcript')}
    exec(final_code, namespace)
    check('All 45 accepted baseline dispositions survive both admission and final validation', len(accepted) == 45 and baseline_ids == accepted, {'accepted': len(accepted), 'produced': len(baseline_ids)})

    example = copy.deepcopy(next(row for row in scope['records'] if row['video_id'] == 'KpZNfys5EgQ'))
    example.update(video_id='UNREVIEWED1', exact_video_id_currently_linked=False)
    unreviewed = candidates(namespace, candidate_code, [example])[0]
    check('A new unreviewed upload remains unresolved', unreviewed['coverage_status'].startswith('Coverage unconfirmed') and not unreviewed.get('absence_review'), {'status': unreviewed['coverage_status']})

    collision = copy.deepcopy(example)
    collision.update(video_id='SYNTHETIC01', title='Caso 03 | Marco Fabián García Céspedes | Subcaso Casanare | 20190705')
    synthetic_ledger = copy.deepcopy(ledger)
    synthetic_entry = copy.deepcopy(synthetic_ledger['dispositions'][0])
    synthetic_entry.update(video_id=collision['video_id'], public_title_sha256=hashlib.sha256(collision['title'].encode()).hexdigest(), public_participant=namespace['public_participant'](collision['title']), public_session_date=namespace['public_date'](collision['title']), review_basis='metadata_session_index')
    synthetic_ledger['dispositions'].append(synthetic_entry)
    namespace['ACCEPTED_ABSENCES'] = namespace['validate_absence_ledger'](synthetic_ledger, inventory)
    collided = candidates(namespace, candidate_code, [collision])[0]
    check('An exact principal/date collision remains unresolved even with a metadata ledger entry', collided['coverage_status'].startswith('Coverage unconfirmed') and not collided.get('absence_review'), {'status': collided['coverage_status'], 'existing_source': 'VV-057'})
    namespace['ACCEPTED_ABSENCES'] = namespace['validate_absence_ledger'](ledger, inventory)

    changed = copy.deepcopy(inventory)
    changed[0]['date'] = '2099-01-01'
    try:
        namespace['validate_absence_ledger'](ledger, changed)
        rejected = False
    except ValueError as exc:
        rejected = True
        reason = str(exc)
    check('A changed source-session index fails closed', rejected, {'error': reason if rejected else None})

    same_sessions = copy.deepcopy(list(reversed(inventory)))
    for row in same_sessions:
        row['source_file_ids'].reverse()
        row['youtube_url'] = ''
        row['notes'] = 'Synthetic changed video-mapping note; source identity unchanged.'
    stable = namespace['source_session_index_fingerprint'](same_sessions)
    check('Ordering, video URLs and coverage-note changes do not redefine the source-session index', stable == ledger['source_session_index_sha256'], {'source_session_index_sha256': stable})

    malformed = copy.deepcopy(ledger)
    malformed['dispositions'].append(copy.deepcopy(malformed['dispositions'][0]))
    try:
        namespace['validate_absence_ledger'](malformed, inventory)
        rejected = False
    except ValueError:
        rejected = True
    check('Duplicate accepted video IDs cannot overwrite a disposition', rejected, {})

    unreviewed['coverage_status'] = 'No supplied transcript located for public-metadata session'
    namespace['rows'] = [unreviewed]
    try:
        exec(final_code, namespace)
        rejected = False
    except ValueError as exc:
        rejected = True
        reason = str(exc)
    check('A later override cannot bypass accepted-disposition admission', rejected, {'error': reason if rejected else None})

    result = {'review_id': 'review05', 'kind': 'R05-F2 repair follow-up, not an additional independent review', 'builder_sha256': hashlib.sha256(args.builder.read_bytes()).hexdigest(), 'ledger_sha256': hashlib.sha256(args.ledger.read_bytes()).hexdigest(), 'source_session_index_sha256': ledger['source_session_index_sha256'], 'all_passed': all(check['passed'] for check in checks), 'checks': checks, 'execution_boundary': 'Pure definitions and isolated candidate/final-validation loops only. The top-level builder was neither imported nor executed; canonical outputs were not written.'}
    (HERE / 'disposition_repair_observations.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
