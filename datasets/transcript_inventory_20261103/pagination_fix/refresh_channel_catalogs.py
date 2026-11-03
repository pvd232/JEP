#!/usr/bin/env python3
"""Refresh the public Videos/Live metadata grids with timestamped page receipts.

Python 3.10+, standard library. This collects listing metadata only. The output
directory is explicit so an earlier snapshot is never silently overwritten.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
import crawl_public_catalog as catalog


def write_json(path, value):
    """Replace a derived checkpoint after its response receipt is durable."""
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temporary.replace(path)


def grid_entries(items):
    """Unwrap only direct grid items, preserving the list's own continuation."""
    unwrapped = []
    for item in items:
        if 'richItemRenderer' in item:
            content = item['richItemRenderer'].get('content')
            if not isinstance(content, dict):
                raise ValueError('Grid item has no content object')
            unwrapped.append(content)
        else:
            unwrapped.append(item)
    return catalog.parse_list(unwrapped)


def validate_selected_surface(tab, surface):
    """Bind the selected tab to the requested official channel surface."""
    endpoint = tab.get('endpoint', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url')
    parsed = urlparse(endpoint or '')
    path = parsed.path.rstrip('/')
    expected_paths = {'/@jepcolombia/' + surface, '/channel/' + catalog.JEP_CHANNEL + '/' + surface}
    if (parsed.scheme not in ('', 'https')
            or (parsed.netloc and parsed.hostname not in ('youtube.com', 'www.youtube.com'))
            or path not in expected_paths):
        raise ValueError('Selected channel surface does not match requested ' + surface + ': ' + str(endpoint))
    return endpoint


def refresh(surface, output, max_pages):
    """Exhaust one public channel grid or preserve its exact incomplete state."""
    directory = output / surface
    directory.mkdir(parents=True, exist_ok=True)
    url = 'https://www.youtube.com/@jepcolombia/' + surface
    result = {
        'collection_key': 'channel_' + surface,
        'collection_id': catalog.JEP_CHANNEL + ':' + surface,
        'collection_type': 'channel_surface', 'source_url': url,
        'title': 'JEP Colombia / ' + surface,
        'source_role': 'fresh_channel_discovery',
        'scope': 'Channel listing metadata only; separate Casanare scope admission required',
        'started_at': catalog.now(), 'pages': [], 'memberships': [], 'errors': [],
        'declared_items': None, 'original_fetch_time': None,
    }
    pending, seen_tokens, error, cycle = [], set(), None, False
    try:
        first = directory / 'page_000.json'
        if first.exists():
            data = catalog.read(first)
            receipt = catalog.read(directory / 'page_000.meta.json')
            raw = (directory / 'initial.html').read_bytes()
            if receipt['requested_url'] != url or catalog.sha(raw) != receipt['sha256']:
                raise ValueError('Initial response URL or checksum mismatch')
            html = raw.decode()
            if data != catalog.assigned(html, 'ytInitialData'):
                raise ValueError('Initial parsed cache does not match retained HTML')
        else:
            raw, receipt = catalog.request(url)
            html = raw.decode()
            data = catalog.assigned(html, 'ytInitialData')
            (directory / 'initial.html').write_bytes(raw)
            write_json(first, data)
            write_json(directory / 'page_000.meta.json', receipt)
        result['original_fetch_time'] = receipt['fetched_at']
        channel_id = data.get('metadata', {}).get('channelMetadataRenderer', {}).get('externalId')
        if channel_id != catalog.JEP_CHANNEL:
            raise ValueError('Unexpected channel identity: ' + str(channel_id))
        tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        selected = [t['tabRenderer'] for t in tabs if t.get('tabRenderer', {}).get('selected')]
        if len(selected) != 1:
            raise ValueError('Expected one selected channel surface')
        result['selected_tab_url'] = validate_selected_surface(selected[0], surface)
        grid = selected[0].get('content', {}).get('richGridRenderer')
        if not grid or not grid.get('targetId'):
            raise ValueError('Selected channel surface has no identifiable primary grid')
        result['selected_tab_title'] = selected[0].get('title')
        result['target_id'] = target = grid['targetId']
        context = catalog.context_from(html)
        items = grid.get('contents', [])
        for page in range(max_pages):
            if page:
                if not pending:
                    break
                token = pending[0]
                if token in seen_tokens:
                    cycle = True
                    break
                seen_tokens.add(token)
                response_path = directory / f'page_{page:03}.json'
                receipt_path = directory / f'page_{page:03}.meta.json'
                if response_path.exists():
                    data, receipt = catalog.read(response_path), catalog.read(receipt_path)
                    if receipt.get('request_token_sha256') != catalog.sha(token):
                        raise ValueError('Continuation cache identity mismatch')
                    if receipt.get('parsed_response_sha256') != catalog.sha(json.dumps(data, sort_keys=True)):
                        raise ValueError('Continuation cache checksum mismatch')
                else:
                    raw, receipt = catalog.request('https://www.youtube.com/youtubei/v1/browse?prettyPrint=false', json.dumps({'context': context, 'continuation': token}).encode())
                    data = json.loads(raw)
                    receipt['request_token_sha256'] = catalog.sha(token)
                    receipt['parsed_response_sha256'] = catalog.sha(json.dumps(data, sort_keys=True))
                    write_json(response_path, data)
                    write_json(receipt_path, receipt)
                items, path, legacy, ignored = catalog.continued_list(data, target)
                if legacy:
                    raise ValueError('Unexpected playlist continuation in channel grid')
            else:
                response_path = first
                path, ignored = ('selected_tab', 'richGridRenderer', 'contents'), []
            entries, next_tokens = grid_entries(items)
            if not entries and next_tokens:
                raise ValueError('Empty primary grid page still has a continuation')
            result['pages'].append({'page_index': page, 'response_path': str(response_path), 'list_json_path': list(path), 'items': len(entries), 'ignored_action_targets': ignored, 'request': receipt})
            for entry in entries:
                result['memberships'].append({**entry, 'collection_id': result['collection_id'], 'collection_key': result['collection_key'], 'source_url': url, 'page_index': page, 'position': len(result['memberships']) + 1})
            pending = next_tokens
            result['pending_token_sha256'] = [catalog.sha(t) for t in pending]
            write_json(directory / 'state.json', {**result, **catalog.completion(result['memberships'], pending, None, None, 0)})
            print(json.dumps({'surface': surface, 'page': page, 'positions': len(result['memberships']), 'pending': bool(pending)}), flush=True)
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'at': catalog.now()}
        result['errors'].append(error)
    result['pending_token_sha256'] = [catalog.sha(t) for t in pending]
    result.update(catalog.completion(result['memberships'], pending, error, None, 0, cycle, bool(pending) and len(result['pages']) >= max_pages))
    result['finished_at'] = catalog.now()
    result['normal_title_memberships'] = sum(bool(x.get('title')) and x.get('visibility') != 'unavailable_placeholder' for x in result['memberships'])
    result['unavailable_placeholder_memberships'] = sum(x.get('visibility') == 'unavailable_placeholder' for x in result['memberships'])
    write_json(directory / 'state.json', result)
    print(json.dumps({k: result.get(k) for k in ['collection_key', 'status', 'returned_memberships', 'unique_video_ids', 'original_fetch_time', 'errors']}), flush=True)
    return result


def main():
    """Refresh selected channel surfaces sequentially and fail on any gap."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--surfaces', nargs='+', choices=['videos', 'streams'], default=['videos', 'streams'])
    parser.add_argument('--max-pages', type=int, default=160)
    args = parser.parse_args()
    if args.max_pages < 1:
        parser.error('--max-pages must be positive')
    results = [refresh(surface, args.output_dir.resolve(), args.max_pages) for surface in args.surfaces]
    write_json(args.output_dir.resolve() / 'refresh_manifest.json', {'generated_at': catalog.now(), 'collections': results})
    return 0 if all(r['pagination_exhausted'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
