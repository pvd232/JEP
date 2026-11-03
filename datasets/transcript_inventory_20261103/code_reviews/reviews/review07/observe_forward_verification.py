#!/usr/bin/env python3
"""Observe forward-match verification semantics without changing research data."""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'base'


def read(path):
    return json.loads(path.read_text())


def run_case(module, name, unique_id, original, proposed, review_fields=None):
    """Supply a synthetic report to the actual merger in an isolated directory."""
    directory = HERE / 'synthetic_fixtures' / name
    directory.mkdir(parents=True, exist_ok=True)
    row = {'unique_id': unique_id, 'confidence': 'Unmatched', 'content_verified': False,
           'notes': '', 'evidence': '', 'youtube_url': '', **original}
    review = {'unique_id': unique_id, 'status': 'Synthetic verification observer',
              'proposed_update': proposed, **(review_fields or {})}
    (directory / 'deep_unmatched.json').write_text(json.dumps({'records': [review]}, indent=2))
    module.ROOT = directory
    rows = [copy.deepcopy(row)]
    module.apply_deep_results(rows)
    actual = rows[0]
    return {k: actual.get(k) for k in ['unique_id', 'confidence', 'content_verified', 'verification_level', 'playability']}


def main():
    """Report the three regression cases and independently reconcile gap ownership."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', type=Path, default=HERE / 'source_snapshot/merge_deep_results.py')
    parser.add_argument('--output', type=Path, default=HERE / 'observer_results.json')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('reviewed_forward_merger', args.module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = []
    actual = run_case(module, 'metadata_only_high', 'SYNTHETIC-METADATA', {},
                      {'confidence': 'High', 'content_verified': False,
                       'match_basis': 'Title and date metadata only',
                       'evidence': 'Synthetic metadata identity; no caption check.'},
                      {'content_verified': False})
    results.append({'case': 'High identity confidence with explicit metadata-only evidence',
                    'expected_content_verified': False, 'actual': actual,
                    'invariant_passed': actual['content_verified'] is False})
    actual = run_case(module, 'downgrade_clears_verification', 'SYNTHETIC-DOWNGRADE',
                      {'confidence': 'High', 'content_verified': True},
                      {'confidence': 'Unmatched', 'content_verified': False, 'youtube_url': '',
                       'evidence': 'Synthetic rejection of the earlier candidate.'},
                      {'content_verified': False})
    results.append({'case': 'Rejected earlier candidate clears content verification',
                    'expected_content_verified': False, 'actual': actual,
                    'invariant_passed': actual['content_verified'] is False})
    actual = run_case(module, 'former_metadata_id_can_be_verified', 'SDSJ-20241203', {},
                      {'confidence': 'High', 'content_verified': True,
                       'evidence': 'Synthetic new caption check with source and video anchor.'},
                      {'content_verified': True,
                       'verified_anchors': [{'source_pointer': 'Synthetic Order 1',
                                             'video_offset': '00:10',
                                             'finding': 'Synthetic matching date and participant anchor.'}]})
    results.append({'case': 'A formerly metadata-only record can acquire affirmative evidence',
                    'expected_content_verified': True, 'actual': actual,
                    'invariant_passed': actual['content_verified'] is True})
    inventory = read(BASE / 'inventory.json')
    gaps = read(BASE / 'recording_gaps.json')
    actual_gaps = {r['unique_id']: r['gap_type'] for r in gaps}
    expected_gaps = {}
    for row in inventory:
        if row['confidence'] == 'Unmatched':
            expected_gaps[row['unique_id']] = 'Unmatched recording'
        elif row.get('coverage_status', '').startswith('Partial public recording'):
            expected_gaps[row['unique_id']] = 'Missing continuation'
        elif row['confidence'] == 'High' and not row.get('content_verified'):
            expected_gaps[row['unique_id']] = 'Content / coverage verification'
    inventory_by_id = {r['unique_id']: r for r in inventory}
    ownership = {
        'gap_count': len(gaps),
        'gap_counts_by_type': dict(collections.Counter(r['gap_type'] for r in gaps)),
        'exact_expected_gap_set_and_types': actual_gaps == expected_gaps,
        'source_links_agree': all(r['original_transcript_url'] == inventory_by_id[r['unique_id']]['direct_file_link'] for r in gaps),
        'recording_links_agree': all(r['existing_video_url'] == inventory_by_id[r['unique_id']]['youtube_url'] for r in gaps),
        'source_dates_agree': all(r['date'] == inventory_by_id[r['unique_id']]['date'] for r in gaps),
        'unmatched_records_have_no_claimed_link_or_verification': all(not r.get('youtube_url') and not r.get('content_verified') for r in inventory if r['confidence'] == 'Unmatched'),
        'no_candidate_records_silently_omitted': not any(r['confidence'].startswith(('Medium', 'Low')) for r in inventory),
        'private_source_ids': [uid for uid, r in inventory_by_id.items() if r.get('access_classification', '').startswith('Source expressly private')],
        'protected_alias_retained': inventory_by_id['VV-065']['participants'] == 'Protected declarant NRAS / XYZ (identity protected)',
    }
    result = {'reviewed_commit': '620cc5eb85860ff77a837058903321876de82b15',
              'module_path': str(args.module),
              'module_sha256': hashlib.sha256(args.module.read_bytes()).hexdigest(),
              'synthetic_observers': results, 'frozen_gap_ownership': ownership,
              'synthetic_scope_note': 'Synthetic cases are not new hearing matches or research data.'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
