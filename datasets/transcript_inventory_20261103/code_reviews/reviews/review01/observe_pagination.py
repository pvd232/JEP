#!/usr/bin/env python3
"""Review the frozen parser without network calls or writes to shared inputs."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path('/workspace/scratch/8a7e64850a04')
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'inventory_work/tieout_review_20261103/base'
SOURCE = BASE / 'pagination_fix/crawl_public_catalog.py'
CACHES = ROOT / 'inventory_work/reverse_audit/caches'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module():
    spec = importlib.util.spec_from_file_location('review01_frozen_crawler', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def video(identifier):
    return {'videoRenderer': {'videoId': identifier, 'title': {'simpleText': 'Synthetic review item'}}}


def first_page(target='fixture-primary-list', token='fixture-next', declared=2):
    entries = [video('aaaaaaaaaaa')]
    if token is not None:
        entries.append({'continuationItemViewModel': {'continuationCommand': {'innertubeCommand': {'continuationCommand': {'token': token}}}}})
    container = {'contents': entries}
    if target is not None:
        container['targetId'] = target
    return {
        'contents': {'twoColumnBrowseResultsRenderer': {'tabs': [{'tabRenderer': {'selected': True, 'content': {'sectionListRenderer': {'contents': [{'itemSectionRenderer': container}]}}}}]}},
        'header': {'test': {'simpleText': str(declared) + ' videos'}},
    }


def next_page(target='fixture-primary-list', token=None):
    entries = [video('bbbbbbbbbbb')]
    if token is not None:
        entries.append({'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': token}}}})
    action = {'continuationItems': entries}
    if target is not None:
        action['targetId'] = target
    return {'onResponseReceivedActions': [{'appendContinuationItemsAction': action}]}


def synthetic_run(name, first, second, *, max_pages=30):
    module = load_module()
    module.BASE = HERE / 'counterexamples' / name
    module.load_initial = lambda *args, **kwargs: (copy.deepcopy(first), {}, {'fixture': True})

    def load_next(*args):
        if isinstance(second, Exception):
            raise second
        return copy.deepcopy(second), {'fixture': True}

    module.load_next = load_next
    with contextlib.redirect_stdout(io.StringIO()):
        result = module.crawl_one('case03', max_pages=max_pages)
    return {key: result.get(key) for key in ['status', 'target_id', 'pagination_exhausted', 'count_reconciled', 'returned_memberships', 'pending_token_sha256', 'errors']}


def retained_replay():
    reports = []
    for collection in read(BASE / 'crawl_manifest.json')['collections']:
        if collection['collection_type'] != 'playlist':
            continue
        module = load_module()
        label = collection['collection_key']
        key = collection['cache_key']
        selected_cache = CACHES / key
        module.BASE = HERE / 'retained_replay' / key
        original_state = read(selected_cache / 'state.json')
        if collection['snapshot_view'] == 'include_unavailable':
            visible_state = read(CACHES / label / 'state.json')
            minimal = {'pagination_exhausted': visible_state['pagination_exhausted'], 'memberships': [{'video_id': x['video_id']} for x in visible_state['memberships']]}
            module.write(module.BASE / 'caches' / label / 'state.json', minimal)

        def load_initial(*args, **kwargs):
            return read(selected_cache / 'page_000.json'), {}, {'fixture': True}

        def load_next(actual_key, index, token, context):
            assert actual_key == key
            metadata = read(selected_cache / f'page_{index:03}.meta.json')
            assert metadata['request_token_sha256'] == module.sha(token)
            return read(selected_cache / f'page_{index:03}.json'), {'fixture': True}

        module.load_initial, module.load_next = load_initial, load_next
        with contextlib.redirect_stdout(io.StringIO()):
            replay = module.crawl_one(label, show_unavailable=collection['snapshot_view'] == 'include_unavailable')
        fields = ['video_id', 'position', 'page_index', 'source_position', 'visibility']
        expected = [[row.get(field) for field in fields] for row in original_state['memberships']]
        actual = [[row.get(field) for field in fields] for row in replay['memberships']]
        reports.append({
            'collection_key': label,
            'cache_key': key,
            'pages': len(replay['pages']),
            'memberships': len(actual),
            'same_ordered_memberships': actual == expected,
            'status': replay['status'],
            'same_status': replay['status'] == collection['status'],
            'count_reconciled': replay['count_reconciled'],
            'target_present': bool(replay.get('target_id')),
            'errors': replay['errors'],
            'response_hashes': [digest(selected_cache / f'page_{p["page_index"]:03}.json') for p in replay['pages']],
        })
    return reports


def main():
    standalone = HERE / 'standalone'
    shutil.copytree(BASE / 'pagination_fix', standalone, dirs_exist_ok=True)
    replay = subprocess.run([sys.executable, str(standalone / 'crawl_public_catalog.py'), 'reproduce'], cwd=standalone, capture_output=True, text=True)
    (HERE / 'standalone_stdout.txt').write_text(replay.stdout)
    (HERE / 'standalone_stderr.txt').write_text(replay.stderr)
    standalone_result = read(standalone / 'pagination_reproduction.json')
    counterexamples = {
        'missing_primary_target': synthetic_run('missing_primary_target', first_page(target=None), next_page(target=None)),
        'mismatched_primary_target': synthetic_run('mismatched_primary_target', first_page(), next_page(target='fixture-unrelated-list')),
        'request_failure': synthetic_run('request_failure', first_page(), TimeoutError('Synthetic timeout')),
        'repeated_token': synthetic_run('repeated_token', first_page(declared=3), next_page(token='fixture-next')),
        'page_limit': synthetic_run('page_limit', first_page(), next_page(), max_pages=1),
    }
    module = load_module()
    malformed_legacy = [{'nextContinuationData': {}}]
    entries, pending = module.parse_list([video('aaaaaaaaaaa')], malformed_legacy)
    counterexamples['malformed_legacy_continuation'] = module.completion(entries, pending, None, 1, 0)
    retained = retained_replay()
    report = {
        'commit': '620cc5eb85860ff77a837058903321876de82b15',
        'python': sys.executable,
        'source_sha256': digest(SOURCE),
        'fixture_sha256': {p.name: digest(p) for p in sorted((BASE / 'pagination_fix/fixtures').glob('*.json'))},
        'standalone': {'exit_code': replay.returncode, 'all_passed': standalone_result['all_passed'], 'checks': len(standalone_result['checks'])},
        'retained_playlist_replay': retained,
        'counterexamples': counterexamples,
        'network_requests': 0,
        'baseline_hashes_unchanged': digest(SOURCE) == '8e7ba646de4edc9ee86045201eb7405077a8d670598f245969778b2e5d8936f6',
    }
    (HERE / 'observations.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'standalone': report['standalone'], 'retained_playlists': len(retained), 'retained_response_pages': sum(x['pages'] for x in retained), 'retained_replay_exact': all(x['same_ordered_memberships'] and x['same_status'] and x['count_reconciled'] for x in retained), 'counterexamples': counterexamples}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
