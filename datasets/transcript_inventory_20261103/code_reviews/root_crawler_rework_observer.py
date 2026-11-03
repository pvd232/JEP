#!/usr/bin/env python3
"""Validate only the root's R01/R02/R09 crawler repairs, entirely offline.

The prior independent receipts remain unchanged. All generated fixtures and
CLI outputs live in a temporary directory; the retained channel data is read
only. A frozen code snapshot avoids races with later parent integration.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import urllib.error

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
WORK = HERE.parent


def read(path):
    """Read one local JSON file without changing it."""
    return json.loads(Path(path).read_text())


def digest(path):
    """Bind evidence to the exact bytes inspected."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    """Keep all observer writes within the authorized tie-out directory."""
    path = Path(path).resolve()
    path.relative_to(HERE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def module(path, name):
    """Import one exact implementation without bytecode writes."""
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def crawler(path, target):
    """Route the real implementation to private inputs and block all network."""
    loaded = module(path, 'root_rework_crawler')
    loaded.BASE = target / 'crawler'
    loaded.WORK = target
    loaded.ORIGINAL = target / 'raw'
    loaded.BASE.mkdir(parents=True, exist_ok=True)
    loaded.ORIGINAL.mkdir(parents=True, exist_ok=True)

    def blocked(*args, **kwargs):
        raise AssertionError('Root repair validation is strictly offline')

    loaded.request = blocked
    return loaded


def compact(state):
    """Retain the state fields needed to assess success or incompleteness."""
    return {k: state.get(k) for k in ['status', 'pagination_exhausted', 'count_reconciled', 'visible_memberships', 'unique_video_ids', 'pending_token_sha256', 'errors']}


def channel_fixture(loaded, label, numbers=(0, 1, 2), wrong_branch=False):
    """Create a precise channel-chain fixture, including one false About case."""
    pages = []
    for index in numbers:
        ident = f'R{index:010d}'
        items = [] if wrong_branch and index == 1 else [{'id': ident, 'title': 'Fixture', 'kind': 'videoRenderer', 'type': 'LOCKUP_CONTENT_TYPE_VIDEO'}]
        pages.append({'page': index, 'items': items})
        rendered = [{'videoRenderer': {'videoId': ident, 'title': {'simpleText': 'Fixture'}}}]
        if index != numbers[-1]:
            rendered.append({'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'fixture-next-' + str(index)}}}})
        if index == 0:
            raw = {'contents': {'twoColumnBrowseResultsRenderer': {'tabs': [{'tabRenderer': {'selected': True, 'content': {'richGridRenderer': {'targetId': 'fixture-grid', 'contents': rendered}}}}]}}}
        else:
            target = 'unrelated-grid' if wrong_branch and index == 1 else 'fixture-grid'
            raw = {'onResponseReceivedActions': [{'appendContinuationItemsAction': {'targetId': target, 'continuationItems': rendered}}]}
        name = label + ('_' + str(index) if index else '') + '.json'
        write(loaded.ORIGINAL / name, raw)
    snapshot = {'label': label, 'pages': pages, 'continuation_remaining': False}
    write(loaded.WORK / (label + '_full_public_catalog.json'), snapshot)
    return snapshot


def parser_cases(source, output, prior):
    """Recheck the two original R01 counterexamples and their valid control."""
    loaded = crawler(source, output / 'r01')
    loaded.load_initial = lambda *a, **kw: (prior.first_page(target=None), {}, {'fixture': True})
    loaded.load_next = lambda *a, **kw: (prior.next_page(target=None), {'fixture': True})
    with contextlib.redirect_stdout(io.StringIO()):
        state = loaded.crawl_one('case03')
    results = [{'id': 'R01-F01', 'scenario': 'Missing target on both first and continued page', 'observed': compact(state), 'passed': state['pagination_exhausted'] is False and state['status'] == 'error' and 'target' in state['errors'][0]['message']}]
    for name, legacy, expected in [
        ('R01-F02', [{'nextContinuationData': {}}], 'Malformed legacy continuation token'),
        ('R01-F02-valid-control', [{'nextContinuationData': {'continuation': 'fixture-supported'}}], None),
    ]:
        error, entries, pending = None, [], []
        try:
            entries, pending = loaded.parse_list([prior.video('aaaaaaaaaaa')], legacy)
        except ValueError as exc:
            error = str(exc)
        passed = error == expected if expected else error is None and len(entries) == 1 and pending == ['fixture-supported']
        results.append({'id': name, 'observed_error': error, 'entry_count': len(entries), 'pending_count': len(pending), 'passed': passed})
    return results


def completeness_cases(source, output):
    """Check missing pages, branch recognition and missing declared sources."""
    results = []
    for name, numbers, wrong_branch in [
        ('R02-01', (0, 2), False),
        ('R02-01-branch-guard', (0, 1, 2), True),
    ]:
        loaded = crawler(source, output / name)
        channel_fixture(loaded, 'deep_channel_videos', numbers, wrong_branch)
        state = loaded.reused_channel('deep_channel_videos', 'videos')
        results.append({'id': name, 'scenario': 'Missing middle index' if not wrong_branch else 'A wrong-target video page is mislabelled an empty non-video branch in the derived catalog', 'observed': compact(state), 'page_roles': [p.get('role') for p in state.get('pages', [])], 'passed': state['pagination_exhausted'] is False and bool(state['errors'])})
    loaded = crawler(source, output / 'R02-02')
    for label in ['deep_channel_videos', 'deep_channel_streams']:
        channel_fixture(loaded, label, (0,))
    label = 'casanare'
    collection_id = loaded.SEEDS[label][0]
    membership = {'video_id': 'R0000000000', 'url': 'https://www.youtube.com/watch?v=R0000000000', 'title': 'Fixture', 'collection_id': collection_id, 'collection_key': label, 'source_url': 'https://www.youtube.com/playlist?list=' + collection_id, 'visibility': 'listed', 'position': 1, 'page_index': 0}
    state = {'collection_key': label, 'collection_id': collection_id, 'collection_type': 'playlist', 'source_role': 'core_declared_source', 'memberships': [membership], 'errors': [], 'pending_token_sha256': [], **loaded.completion([membership], [], None, 1, 0)}
    write(loaded.BASE / 'caches/casanare/state.json', state)
    manifest = loaded.export_all()
    by_key = {c['collection_key']: c for c in manifest['collections']}
    missing = sorted(set(loaded.SEEDS) - {label})
    passed = all(k in by_key and by_key[k]['status'] == 'required_snapshot_missing' and by_key[k]['pagination_exhausted'] is False and bool(by_key[k]['errors']) for k in missing)
    results.append({'id': 'R02-02', 'retained_required_core_keys': sorted(loaded.CORE_SEED_KEYS), 'missing_core_keys_with_explicit_status': [k for k in missing if k in loaded.CORE_SEED_KEYS], 'missing_regional_keys_with_explicit_status': [k for k in missing if k not in loaded.CORE_SEED_KEYS], 'channel_controls_exhausted': all(by_key[k]['pagination_exhausted'] for k in ['deep_channel_videos', 'deep_channel_streams']), 'passed': passed and all(k in by_key for k in loaded.CORE_SEED_KEYS) and all(by_key[k]['pagination_exhausted'] for k in ['deep_channel_videos', 'deep_channel_streams'])})
    return results


def retained_channels(source, output, prior_receipt):
    """Run the repaired validator against all 120 original retained responses."""
    loaded = crawler(source, output / 'retained')
    loaded.WORK = WORK
    loaded.ORIGINAL = WORK / 'public_catalog_cache'
    old = {r['label']: r for r in prior_receipt['retained_channel_audits']}
    reports = []
    for label, surface, pages, expected_ids in [('deep_channel_videos', 'videos', 90, 2663), ('deep_channel_streams', 'streams', 30, 847)]:
        snapshot_path = WORK / (label + '_full_public_catalog.json')
        snapshot = read(snapshot_path)
        state = loaded.reused_channel(label, surface)
        expected = [item['id'] for page in snapshot['pages'] for item in page.get('items', [])]
        observed = [item['video_id'] for item in state['memberships']]
        before_pages = {p['page_index']: p['raw_response_sha256'] for p in old[label]['page_evidence']}
        receipts = state.get('pages', [])
        roles = {role: sum(p.get('role') == role for p in receipts) for role in ['primary_video_grid', 'verified_about_branch']}
        checks = {
            'complete_with_no_errors': state['pagination_exhausted'] is True and not state['errors'],
            'all_pages_receipted': len(receipts) == pages,
            'same_complete_ordered_ids': observed == expected,
            'same_unique_id_count': len(set(observed)) == expected_ids,
            'one_recognized_nonvideo_branch': roles == {'primary_video_grid': pages - 1, 'verified_about_branch': 1},
            'every_raw_hash_matches_original_review': all(p['sha256'] == before_pages[p['page_index']] for p in receipts) and len(receipts) == len(before_pages),
            'same_derived_catalog_as_original_review': digest(snapshot_path) == old[label]['catalog_sha256'],
            'unknown_retrieval_time_remains_explicit': 'Not stored' in state['provenance']['original_fetch_time'],
        }
        reports.append({'label': label, 'pages': len(receipts), 'unique_video_ids': len(set(observed)), 'roles': roles, 'checks': checks, 'all_passed': all(checks.values()), 'response_sha256': {str(p['page_index']): p['sha256'] for p in receipts}})
    return reports


def cli_cases(source, output, prior01, prior09):
    """Observe actual crawl CLI failure/success and cached probe provenance."""
    results = []
    observed = prior09.failed_crawl(source, output)
    results.append({'id': 'R09-F02-transport-failure', 'observed': observed, 'passed': observed['exit_code'] == 1 and observed['status'] == 'error' and observed['pagination_exhausted'] is False and observed['transport_stub_calls'] == 1})
    for name, capped in [('page-cap', True), ('successful-completion', False)]:
        loaded = crawler(source, output / name)
        write(loaded.BASE / 'live_pagination_proof.json', {'passed': True})
        loaded.load_initial = lambda *a, **kw: (prior01.first_page(token='fixture-next' if capped else None, declared=2 if capped else 1), {}, {'fixture': True})
        argv = ['crawl', '--collections', 'case03'] + (['--max-pages', '1'] if capped else [])
        observed = prior09.invoke(loaded, argv)
        state = read(loaded.BASE / 'caches/case03/state.json')
        passed = observed['exit_code'] == (1 if capped else 0) and state['pagination_exhausted'] is (not capped)
        results.append({'id': 'R09-F02-' + name, 'observed': {**observed, **compact(state)}, 'passed': passed})
    loaded = module(source, 'root_rework_429_crawler')
    loaded.BASE = output / 'http429/crawler'
    loaded.WORK = output / 'http429'
    loaded.ORIGINAL = output / 'http429/raw'
    write(loaded.BASE / 'live_pagination_proof.json', {'passed': True})
    attempts = []
    original_open = loaded.urllib.request.urlopen

    def denied(request, **kwargs):
        attempts.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, 429, 'Synthetic offline rate limit', {}, None)

    loaded.urllib.request.urlopen = denied
    try:
        observed = prior09.invoke(loaded, ['crawl', '--collections', 'case03', 'casanare'])
    finally:
        loaded.urllib.request.urlopen = original_open
    state = read(loaded.BASE / 'caches/case03/state.json')
    manifest = read(loaded.BASE / 'crawl_manifest.json')
    second = next(c for c in manifest['collections'] if c['collection_key'] == 'casanare')
    passed = observed['exit_code'] == 1 and len(attempts) == 1 and loaded.STOP_NETWORK.is_set() and state['status'] == 'error' and second['status'] == 'required_snapshot_missing'
    results.append({'id': 'R09-F02-stop-on-429', 'observed': {**observed, 'intercepted_transport_calls': len(attempts), 'stop_network_set': loaded.STOP_NETWORK.is_set(), 'first_state': compact(state), 'uncrawled_second_source_status': second['status']}, 'passed': passed})
    observed = prior09.cached_live_probe(source, output)
    proof = read(output / 'cached_live_probe/live_pagination_proof.json')
    provenance = proof.get('page_request_provenance', [])
    expected = [read(WORK / 'reverse_audit/caches/case03' / f'page_{i:03}.meta.json') for i in (0, 1)]
    passed = observed['exit_code'] == 0 and observed['network_calls'] == 0 and proof.get('proof_type') == 'cached_response_replay' and len(provenance) == 2 and proof['passed'] is True
    passed = passed and all(p.get('cache_reused') is True and p.get('fetched_at') == e['fetched_at'] and p.get('response_sha256') == e['sha256'] for p, e in zip(provenance, expected))
    results.append({'id': 'R09-F03', 'observed': {'exit_code': observed['exit_code'], 'network_calls': observed['network_calls'], 'passed': proof['passed'], 'proof_execution_time': proof['at'], 'proof_type': proof.get('proof_type'), 'page_request_provenance': provenance}, 'passed': passed})
    return results


def main():
    """Write the bounded root-rework receipt and fail on any unresolved guard."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crawler', type=Path, default=HERE / 'root_crawler_rework_snapshot/crawl_public_catalog.py')
    parser.add_argument('--output', type=Path, default=HERE / 'root_crawler_rework.json')
    args = parser.parse_args()
    prior_paths = [HERE / 'reviews' / folder / name for folder, name in [
        ('review01', 'review.json'), ('review01', 'observations.json'), ('review01', 'observe_pagination.py'),
        ('review02', 'review.json'), ('review02', 'observer_results.json'),
        ('review09', 'review.json'), ('review09', 'observations.json'), ('review09', 'observe_publication.py'),
    ]]
    before = {str(p.relative_to(HERE)): digest(p) for p in prior_paths}
    prior01 = module(HERE / 'reviews/review01/observe_pagination.py', 'root_rework_prior01')
    prior09 = module(HERE / 'reviews/review09/observe_publication.py', 'root_rework_prior09')
    reviewed_sha = digest(args.crawler)
    with tempfile.TemporaryDirectory(prefix='root_rework_', dir=HERE) as temporary:
        output = Path(temporary)
        cases = parser_cases(args.crawler, output, prior01)
        cases += completeness_cases(args.crawler, output)
        channels = retained_channels(args.crawler, output, read(HERE / 'reviews/review02/observer_results.json'))
        cases += cli_cases(args.crawler, output, prior01, prior09)
    unchanged = before == {str(p.relative_to(HERE)): digest(p) for p in prior_paths}
    passed = all(c['passed'] for c in cases) and all(c['all_passed'] for c in channels) and unchanged and digest(args.crawler) == reviewed_sha
    receipt = {
        'validation_type': 'Follow-up verification of existing Reviews 01, 02 and 09; not an additional independent review',
        'base_commit': '620cc5eb85860ff77a837058903321876de82b15',
        'reviewed_source': str(args.crawler.resolve()), 'reviewed_source_sha256': reviewed_sha,
        'working_source_sha256_at_finish': digest(WORK / 'reverse_audit/crawl_public_catalog.py'),
        'observer_sha256': digest(Path(__file__)), 'runtime': sys.executable,
        'prior_evidence_sha256': before, 'prior_evidence_unchanged': unchanged,
        'actual_network_requests': 0, 'cases': cases, 'retained_channel_replays': channels,
        'passed': passed,
        'limitations': ['The original channel request times and submitted-token provenance were not retained; content/queue closure is checked without inventing retrieval times.', 'The separately reviewed fresh 118-page discovery is not substituted for this 120-page historical replay.', 'No scope, transcript-matching, workbook or publication repair is certified here.'],
    }
    write(args.output, receipt)
    print(json.dumps({'reviewed_source_sha256': reviewed_sha, 'passed': passed, 'failed_cases': [c['id'] for c in cases if not c['passed']], 'cases_passed': sum(c['passed'] for c in cases), 'cases_total': len(cases), 'retained_pages_checked': sum(c['pages'] for c in channels), 'retained_replays_passed': all(c['all_passed'] for c in channels), 'prior_evidence_unchanged': unchanged, 'actual_network_requests': 0}, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
