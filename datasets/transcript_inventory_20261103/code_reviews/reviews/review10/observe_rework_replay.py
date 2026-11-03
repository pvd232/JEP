#!/usr/bin/env python3
"""Replay the repaired function on private copies of every retained page.

Network access is blocked. Raw responses and saved source checkpoints are
hashed before and after; only temporary copies are passed to refresh().
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile

import observe_fresh_integrity as review

HERE = Path(__file__).resolve().parent
TIEOUT = HERE.parents[1]
WORK = TIEOUT.parent


def manifest(directory):
    """Return exact byte hashes for every file in the retained fresh directory."""
    return {str(p.relative_to(directory)): review.digest(p) for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    """Require exact membership and page-receipt preservation for both surfaces."""
    fresh = TIEOUT / 'fresh_discovery'
    refresh_path = WORK / 'reverse_audit/refresh_channel_catalogs.py'
    catalog_path = WORK / 'reverse_audit/crawl_public_catalog.py'
    code_before = {'refresh': review.digest(refresh_path), 'catalog': review.digest(catalog_path)}
    before = manifest(fresh)
    catalog, refresh, attempts = review.load_modules(refresh_path, catalog_path)
    results = []
    with tempfile.TemporaryDirectory(prefix='replay_', dir=HERE) as temporary:
        output = Path(temporary)
        for surface in ['videos', 'streams']:
            shutil.copytree(fresh / surface, output / surface)
            retained = review.read(fresh / surface / 'state.json')
            with contextlib.redirect_stdout(io.StringIO()):
                replay = refresh.refresh(surface, output, max_pages=160)
            old_pages = [{k: v for k, v in p.items() if k != 'response_path'} for p in retained['pages']]
            new_pages = [{k: v for k, v in p.items() if k != 'response_path'} for p in replay['pages']]
            checks = {
                'memberships_identical': replay['memberships'] == retained['memberships'],
                'page_receipts_identical': old_pages == new_pages,
                'same_terminal_state': replay['status'] == retained['status'] == 'exhausted_count_unknown' and replay['pagination_exhausted'] is True,
                'no_pending_or_errors': not replay['pending_token_sha256'] and not replay['errors'],
                'original_fetch_time_preserved': replay['original_fetch_time'] == retained['original_fetch_time'],
                'selected_endpoint_recorded': replay['selected_tab_url'] == '/@jepcolombia/' + surface,
                'reported_counts_identical': replay['returned_memberships'] == retained['returned_memberships'] and replay['unique_video_ids'] == retained['unique_video_ids'],
            }
            results.append({'surface': surface, 'pages': len(replay['pages']), 'unique_ids': replay['unique_video_ids'], 'checks': checks, 'all_passed': all(checks.values())})
    after = manifest(fresh)
    code_after = {'refresh': review.digest(refresh_path), 'catalog': review.digest(catalog_path)}
    receipt = {
        'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'code_sha256': code_before,
        'code_unchanged_during_replay': code_before == code_after,
        'replays': results,
        'actual_network_requests': 0,
        'intercepted_request_attempts': len(attempts),
        'retained_files_checked': len(before),
        'retained_files_unchanged': before == after,
        'retained_sha256': before,
    }
    receipt['passed'] = all(x['all_passed'] for x in results) and before == after and not attempts and code_before == code_after
    (HERE / 'rework_replay.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'retained_sha256'}, indent=2))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
