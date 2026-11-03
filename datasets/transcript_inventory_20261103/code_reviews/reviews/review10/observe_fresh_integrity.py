#!/usr/bin/env python3
"""Replay fresh public-list receipts and test two cache boundaries offline.

No network request or shared-cache mutation is permitted. Synthetic states are
created only in temporary directories beneath this review directory.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlparse

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TIEOUT = HERE.parents[1]
WORK = TIEOUT.parent


def digest(path):
    """Hash exact retained bytes without exposing raw response content."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    """Read one local JSON evidence file."""
    return json.loads(Path(path).read_text())


def load_modules(refresh_path, catalog_path):
    """Load exact code paths and replace the request boundary with a hard stop."""
    spec = importlib.util.spec_from_file_location('crawl_public_catalog', catalog_path)
    catalog = importlib.util.module_from_spec(spec)
    sys.modules['crawl_public_catalog'] = catalog
    spec.loader.exec_module(catalog)
    spec = importlib.util.spec_from_file_location('review10_refresh', refresh_path)
    refresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(refresh)
    attempts = []

    def no_network(url, body=None):
        attempts.append({'url': url, 'method': 'POST' if body else 'GET'})
        raise RuntimeError('Offline review: network request deliberately unavailable')

    catalog.request = no_network
    return catalog, refresh, attempts


def check(checks, label, condition):
    """Append one named observed invariant without silently swallowing failure."""
    checks.append({'check': label, 'passed': bool(condition)})


def retained_audit(catalog, refresh, surface):
    """Replay every primary-list page and compare the complete membership order."""
    directory = TIEOUT / 'fresh_discovery' / surface
    state = read(directory / 'state.json')
    checks, evidence, membership, pending, times = [], [], [], [], []
    expected_url = 'https://www.youtube.com/@jepcolombia/' + surface
    pages = state['pages']
    check(checks, 'Consecutive response page indexes', [p['page_index'] for p in pages] == list(range(len(pages))))
    first = read(directory / 'page_000.json')
    html = (directory / 'initial.html').read_text()
    first_receipt = read(directory / 'page_000.meta.json')
    check(checks, 'Initial HTML raw checksum', digest(directory / 'initial.html') == first_receipt['sha256'])
    check(checks, 'Parsed first page equals the retained HTML assignment', first == catalog.assigned(html, 'ytInitialData'))
    check(checks, 'Official channel identity', first.get('metadata', {}).get('channelMetadataRenderer', {}).get('externalId') == catalog.JEP_CHANNEL)
    tabs = first['contents']['twoColumnBrowseResultsRenderer']['tabs']
    selected = [t['tabRenderer'] for t in tabs if t.get('tabRenderer', {}).get('selected')]
    check(checks, 'Exactly one selected tab', len(selected) == 1)
    tab = selected[0]
    endpoint_url = tab.get('endpoint', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url')
    check(checks, 'Selected endpoint belongs to the requested surface', urlparse(endpoint_url or '').path.rstrip('/').endswith('/' + surface))
    target = tab['content']['richGridRenderer']['targetId']
    check(checks, 'Recorded grid target agrees', state.get('target_id') == target and bool(target))
    context = catalog.context_from(html)
    check(checks, 'Anonymous initial context was retained', isinstance(context, dict) and isinstance(context.get('client'), dict))
    for index, page in enumerate(pages):
        path = directory / f'page_{index:03}.json'
        meta_path = directory / f'page_{index:03}.meta.json'
        data, receipt = read(path), read(meta_path)
        page_checks = []
        check(page_checks, 'Successful request status', receipt.get('http_status') == 200)
        check(page_checks, 'State receipt equals its retained sidecar', page.get('request') == receipt)
        check(page_checks, 'State response path points to this page', Path(page['response_path']) == path)
        times.append(dt.datetime.fromisoformat(receipt['fetched_at']))
        if index:
            check(page_checks, 'Exactly one predecessor continuation', len(pending) == 1)
            check(page_checks, 'Predecessor token fingerprint matches the request', receipt.get('request_token_sha256') == catalog.sha(pending[0]))
            check(page_checks, 'Parsed response checksum matches', receipt.get('parsed_response_sha256') == catalog.sha(json.dumps(data, sort_keys=True)))
            expected_endpoint = 'https://www.youtube.com/youtubei/v1/browse?prettyPrint=false'
            check(page_checks, 'Continuation used the normal public browse endpoint', receipt.get('requested_url') == expected_endpoint and receipt.get('response_url') == expected_endpoint and receipt.get('method') == 'POST')
            items, json_path, legacy, ignored = catalog.continued_list(data, target)
            check(page_checks, 'No legacy playlist branch used for channel traversal', not legacy)
            check(page_checks, 'Ignored response targets accounted for', ignored == page.get('ignored_action_targets'))
            check(page_checks, 'List path is the retained primary response path', list(json_path) == page.get('list_json_path'))
        else:
            check(page_checks, 'First request targets the declared surface', receipt.get('requested_url') == expected_url and receipt.get('response_url') == expected_url and receipt.get('method') == 'GET')
            items = tab['content']['richGridRenderer']['contents']
        entries, pending = refresh.grid_entries(items)
        check(page_checks, 'Page item count agrees', len(entries) == page['items'])
        for entry in entries:
            membership.append({**entry, 'collection_id': state['collection_id'], 'collection_key': state['collection_key'], 'source_url': expected_url, 'page_index': index, 'position': len(membership) + 1})
        evidence.append({'page_index': index, 'response_sha256': digest(path), 'receipt_sha256': digest(meta_path), 'items': len(entries), 'fetched_at': receipt['fetched_at'], 'checks': page_checks, 'all_passed': all(x['passed'] for x in page_checks)})
    check(checks, 'All reconstructed membership fields and order agree', membership == state['memberships'])
    check(checks, 'Every page receipt passes', all(p['all_passed'] for p in evidence))
    check(checks, 'Final primary continuation exhausted', not pending)
    check(checks, 'No recorded errors or pending requests', not state.get('errors') and not state.get('pending_token_sha256'))
    check(checks, 'Terminal state is honest about absent declared count', state.get('status') == 'exhausted_count_unknown' and state.get('pagination_exhausted') is True and state.get('count_reconciled') is None and state.get('declared_items') is None)
    check(checks, 'Returned and distinct-ID counts agree', len(membership) == state['returned_memberships'] and len({r['video_id'] for r in membership}) == state['unique_video_ids'])
    check(checks, 'Original fetch time is the initial receipt time', state.get('original_fetch_time') == first_receipt['fetched_at'])
    check(checks, 'Request times are ordered and no later than completion', times == sorted(times) and times[-1] <= dt.datetime.fromisoformat(state['finished_at']))
    old = read(WORK / ('deep_channel_' + surface + '_full_public_catalog.json'))
    old_ids = {r['id'] for p in old['pages'] for r in p.get('items', [])}
    new_ids = {r['video_id'] for r in membership}
    expected_removed = {'Pg8DvszQMME'} if surface == 'streams' else set()
    check(checks, 'No newly added IDs in this refresh', not (new_ids - old_ids))
    check(checks, 'Historical difference is exactly the recorded difference', old_ids - new_ids == expected_removed)
    comparison = next(r for r in read(TIEOUT / 'fresh_channel_comparison.json') if r['surface'] == surface)
    check(checks, 'Comparison receipt counts and ID differences agree', comparison['old_ids'] == len(old_ids) and comparison['fresh_ids'] == len(new_ids) and {r['id'] for r in comparison['removed']} == expected_removed and not comparison['added'])
    return {'surface': surface, 'state_sha256': digest(directory / 'state.json'), 'initial_html_sha256': digest(directory / 'initial.html'), 'selected_tab': tab.get('title'), 'selected_tab_url': endpoint_url, 'pages_checked': len(pages), 'membership_count': len(membership), 'unique_ids': len(new_ids), 'added_ids': sorted(new_ids - old_ids), 'absent_from_fresh_listing_ids': sorted(old_ids - new_ids), 'checks': checks, 'page_evidence': evidence, 'all_passed': all(c['passed'] for c in checks)}


def video(ident):
    """Build one ordinary public grid card with an exact synthetic ID."""
    return {'richItemRenderer': {'content': {'lockupViewModel': {'contentId': ident, 'contentType': 'LOCKUP_CONTENT_TYPE_VIDEO', 'metadata': {'lockupMetadataViewModel': {'title': {'content': 'Fixture ' + ident}}}}}}}


def continuation(token):
    """Build a supported primary-list continuation control."""
    return {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': token}}}}


def initial_data(catalog, surface, with_next=False):
    """Build a channel-owned first-page fixture for a named surface."""
    items = [video('R0000000001')]
    if with_next:
        items.append(continuation('fixture-next'))
    tab = {'selected': True, 'title': 'Videos' if surface == 'videos' else 'Live', 'endpoint': {'commandMetadata': {'webCommandMetadata': {'url': '/@jepcolombia/' + surface}}}, 'content': {'richGridRenderer': {'targetId': 'fixture-grid', 'contents': items}}}
    return {'metadata': {'channelMetadataRenderer': {'externalId': catalog.JEP_CHANNEL}}, 'contents': {'twoColumnBrowseResultsRenderer': {'tabs': [{'tabRenderer': tab}]}}}


def cache_first(catalog, root, requested_surface, original, parsed=None):
    """Store a fixture HTML/receipt pair and optionally a different parsed JSON."""
    directory = root / requested_surface
    directory.mkdir(parents=True)
    html = '<html><script>var ytInitialData = ' + json.dumps(original) + '; var config = {"INNERTUBE_CONTEXT":{"client": {"clientName": "WEB", "clientVersion": "fixture"}}};</script></html>'
    receipt = {'requested_url': 'https://www.youtube.com/@jepcolombia/' + requested_surface, 'response_url': 'https://www.youtube.com/@jepcolombia/' + requested_surface, 'method': 'GET', 'http_status': 200, 'content_type': 'text/html', 'fetched_at': '2026-11-03T00:00:00+00:00', 'sha256': catalog.sha(html.encode()), 'bytes': len(html.encode())}
    (directory / 'initial.html').write_text(html)
    (directory / 'page_000.json').write_text(json.dumps(original if parsed is None else parsed))
    (directory / 'page_000.meta.json').write_text(json.dumps(receipt))
    return directory


def cache_next(catalog, directory, data, token='fixture-next', parsed_checksum=None):
    """Store a second fixture page with inspectable continuity fingerprints."""
    receipt = {'requested_url': 'https://www.youtube.com/youtubei/v1/browse?prettyPrint=false', 'response_url': 'https://www.youtube.com/youtubei/v1/browse?prettyPrint=false', 'method': 'POST', 'http_status': 200, 'content_type': 'application/json', 'fetched_at': '2026-11-03T00:00:01+00:00', 'request_token_sha256': catalog.sha(token), 'parsed_response_sha256': parsed_checksum or catalog.sha(json.dumps(data, sort_keys=True)), 'sha256': catalog.sha(json.dumps(data)), 'bytes': len(json.dumps(data).encode())}
    (directory / 'page_001.json').write_text(json.dumps(data))
    (directory / 'page_001.meta.json').write_text(json.dumps(receipt))


def run_case(catalog, refresh, attempts, name, setup, surface='videos', max_pages=5):
    """Run the actual refresh function against one isolated synthetic cache."""
    start = len(attempts)
    with tempfile.TemporaryDirectory(prefix='fixture_', dir=HERE) as tmp:
        root = Path(tmp)
        setup(root)
        with contextlib.redirect_stdout(io.StringIO()):
            result = refresh.refresh(surface, root, max_pages)
    return {'case': name, 'observed': {k: result.get(k) for k in ['collection_key', 'selected_tab_title', 'status', 'pagination_exhausted', 'returned_memberships', 'unique_video_ids', 'duplicate_memberships', 'pending_token_sha256', 'errors']}, 'network_attempts_intercepted': len(attempts) - start}


def counterexamples(catalog, refresh, attempts):
    """Exercise real false-completeness cases plus focused failure controls."""
    findings, controls = [], []
    original = initial_data(catalog, 'videos', with_next=True)
    parsed = copy.deepcopy(original)
    parsed['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['richGridRenderer']['contents'].pop()
    case = run_case(catalog, refresh, attempts, 'Parsed first-page JSON drops the continuation retained in HTML', lambda root: cache_first(catalog, root, 'videos', original, parsed))
    case.update({'id': 'R10-01', 'expected': 'Reject or rederive the inconsistent parsed cache; do not claim exhaustion', 'defect_reproduced': case['observed']['pagination_exhausted'] is True})
    findings.append(case)
    wrong_surface = initial_data(catalog, 'videos')
    case = run_case(catalog, refresh, attempts, 'Requested streams page contains the Videos selected endpoint', lambda root: cache_first(catalog, root, 'streams', wrong_surface), surface='streams')
    case.update({'id': 'R10-02', 'expected': 'Reject the mismatched selected surface before recording a Live catalog', 'defect_reproduced': case['observed']['pagination_exhausted'] is True})
    findings.append(case)

    case = run_case(catalog, refresh, attempts, 'Valid complete first-page control', lambda root: cache_first(catalog, root, 'videos', initial_data(catalog, 'videos')))
    case['passed'] = case['observed']['pagination_exhausted'] is True and case['observed']['returned_memberships'] == 1
    controls.append(case)
    case = run_case(catalog, refresh, attempts, 'Request failure preserves the pending primary continuation', lambda root: cache_first(catalog, root, 'videos', original))
    case['passed'] = case['observed']['status'] == 'error' and case['observed']['pagination_exhausted'] is False and len(case['observed']['pending_token_sha256']) == 1 and 'Offline review' in case['observed']['errors'][0]['message']
    controls.append(case)
    case = run_case(catalog, refresh, attempts, 'Page limit preserves the pending primary continuation', lambda root: cache_first(catalog, root, 'videos', original), max_pages=1)
    case['passed'] = case['observed']['status'] == 'limit_reached' and case['observed']['pagination_exhausted'] is False
    controls.append(case)
    for name, target, token, checksum, repeat in [
        ('Wrong continuation receipt token is rejected', 'fixture-grid', 'wrong-token', None, False),
        ('Changed continuation cache checksum is rejected', 'fixture-grid', 'fixture-next', 'wrong-checksum', False),
        ('Other-target continuation is rejected', 'other-grid', 'fixture-next', None, False),
        ('Repeated primary continuation is a cycle', 'fixture-grid', 'fixture-next', None, True),
    ]:
        data = {'onResponseReceivedActions': [{'appendContinuationItemsAction': {'targetId': target, 'continuationItems': [video('R0000000002')] + ([continuation('fixture-next')] if repeat else [])}}]}
        def setup(root, data=data, token=token, checksum=checksum):
            directory = cache_first(catalog, root, 'videos', original)
            cache_next(catalog, directory, data, token, checksum)
        case = run_case(catalog, refresh, attempts, name, setup)
        expected = 'cycle_detected' if repeat else 'error'
        expected_message = {'Wrong continuation receipt token is rejected': 'Continuation cache identity mismatch', 'Changed continuation cache checksum is rejected': 'Continuation cache checksum mismatch', 'Other-target continuation is rejected': 'Expected one continuation'}
        correct_reason = repeat or expected_message[name] in case['observed']['errors'][0]['message']
        case['passed'] = case['observed']['status'] == expected and case['observed']['pagination_exhausted'] is False and correct_reason
        controls.append(case)
    return findings, controls


def main():
    """Write a bounded review receipt and optionally require both defects fixed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', type=Path, default=HERE / 'snapshot/refresh_channel_catalogs.py')
    parser.add_argument('--catalog', type=Path, default=HERE / 'snapshot/crawl_public_catalog.py')
    parser.add_argument('--output', type=Path, default=HERE / 'observations.json')
    parser.add_argument('--require-fixed', action='store_true')
    args = parser.parse_args()
    args.output.resolve().relative_to(HERE)
    catalog, refresh, attempts = load_modules(args.refresh.resolve(), args.catalog.resolve())
    channels = [retained_audit(catalog, refresh, surface) for surface in ['videos', 'streams']]
    findings, controls = counterexamples(catalog, refresh, attempts)
    report = {'base_commit': '620cc5eb85860ff77a837058903321876de82b15', 'runtime': sys.executable, 'reviewed_code_sha256': {'refresh': digest(args.refresh), 'catalog': digest(args.catalog)}, 'actual_network_requests': 0, 'retained_source_audits': channels, 'counterexamples': findings, 'failure_controls': controls, 'removed_live_metadata_receipt_sha256': digest(HERE.parent / 'review07/removed_live_watch_metadata.json'), 'fresh_comparison_sha256': digest(TIEOUT / 'fresh_channel_comparison.json'), 'limitations': ['Raw first-page HTML bytes and normalized continuation JSON are retained and checked; original continuation HTTP bytes are not retained verbatim.', 'Request bodies are inferred from the reviewed caller and recorded token fingerprints; this is not a packet capture.', 'Absence from a channel listing does not establish deletion, unlisted privacy or video unavailability.']}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    summary = {'pages_checked': sum(x['pages_checked'] for x in channels), 'all_saved_page_checks_passed': all(x['all_passed'] for x in channels), 'counts': {x['surface']: x['unique_ids'] for x in channels}, 'defects_reproduced': [x['id'] for x in findings if x['defect_reproduced']], 'failure_controls_passed': all(x['passed'] for x in controls), 'actual_network_requests': 0}
    print(json.dumps(summary, indent=2))
    return 0 if summary['all_saved_page_checks_passed'] and summary['failure_controls_passed'] and (not args.require_fixed or not summary['defects_reproduced']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
