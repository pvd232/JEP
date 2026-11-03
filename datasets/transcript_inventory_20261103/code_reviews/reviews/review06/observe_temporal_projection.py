#!/usr/bin/env python3
"""Read-only timestamp/duration review; write receipts only beside this script.

Use the managed primary Python runtime (openpyxl is used for reading only).
Pass --assembler PATH to replay the duration boundary against a repaired file.
Pass --require-fixed to return a failing exit status while malformed clocks
are accepted. No source text or public caption text is written to the receipt.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import openpyxl


def load_assembler(path):
    """Import the actual duration converter without calling its writer."""
    spec = importlib.util.spec_from_file_location('review06_assembler', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def date_text(value):
    """Compare Excel dates with the published ISO day without local timezone conversion."""
    return value.strftime('%Y-%m-%d') if isinstance(value, dt.datetime) else value


def main():
    """Observe the frozen workbook and the malformed-duration counterexample."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=Path(__file__).resolve().parents[2] / 'base')
    parser.add_argument('--assembler', type=Path)
    parser.add_argument('--require-fixed', action='store_true')
    args = parser.parse_args()
    base = args.base.resolve()
    assembler_path = args.assembler or base / 'workbook_build/assemble_outputs.py'
    assembler = load_assembler(assembler_path)
    videos = json.loads((base / 'video_inventory.json').read_text())
    inventory = json.loads((base / 'inventory.json').read_text())
    reverse = json.loads((base / 'reverse_mapping_review.json').read_text())
    checks = []

    def check(name, actual, expected):
        checks.append({'check': name, 'actual': actual, 'expected': expected, 'passed': actual == expected})

    partial = sorted(i for r in reverse['videos'] if r['coverage_status'].startswith('Partial supplied transcript') for i in r['transcript_ids'])
    check('Known partial supplied transcripts', partial, ['VV-012', 'VV-015', 'VV-016', 'VV-025', 'VV-047', 'VV-053'])
    check('Video projection preserves the same partial set', sorted(i for r in videos if r['coverage_label'] == 'Partial supplied transcript' for i in r['transcript_ids']), partial)
    by_id = {r['unique_id']: r for r in inventory}
    forward_gaps = sorted(r['unique_id'] for r in inventory if str(r.get('coverage_status', '')).startswith('Partial public recording'))
    check('Forward missing-recording gaps remain distinct', forward_gaps, ['VV-015', 'VV-038'])
    shared = next(r for r in reverse['videos'] if r['video_id'] == 'eM8ZrqhZbgQ')
    check('Shared upload retains both transcript segments', sorted(shared['transcript_ids']), ['VV-029', 'VV-030'])
    check('Composite declaration retains both dates', by_id['VV-071']['date'], '2021-08-12; 2021-08-20')
    check('Composite clock labels remain explicit', 'not YouTube offsets' in by_id['VV-071']['timestamps'], True)
    check('Metadata-only records have no verified source offsets', all(not by_id[i]['content_verified'] and 'unverified' in by_id[i]['timestamps'].lower() or not by_id[i]['content_verified'] and 'no verified' in by_id[i]['timestamps'].lower() for i in ['SDSJ-20241203', 'SDSJ-20241204']), True)

    book = openpyxl.load_workbook(base / 'JEP_transcript_inventory.xlsx', read_only=True, data_only=True)
    duration_discrepancies, timestamp_discrepancies, date_discrepancies = [], [], []
    duration_count = 0
    for row, record in enumerate(videos, 2):
        value = book['Videos'].cell(row, 12).value
        expected = record['duration_seconds']
        if expected is None:
            if value not in (None, ''):
                duration_discrepancies.append(record['video_id'])
        else:
            duration_count += 1
            actual = value.total_seconds() if isinstance(value, dt.timedelta) else value * 86400 if isinstance(value, (int, float)) else None
            if actual is None or abs(actual - expected) > 0.001 or book['Videos'].cell(row, 12).number_format != '[h]:mm:ss':
                duration_discrepancies.append(record['video_id'])
        if (book['Videos'].cell(row, 10).value or '') != record['timestamps']:
            timestamp_discrepancies.append(record['video_id'])
        if record.get('date') and date_text(book['Videos'].cell(row, 5).value) != record['date']:
            date_discrepancies.append(record['video_id'])
    for row, record in enumerate(inventory, 2):
        if date_text(book['Transcripts'].cell(row, 4).value) != record['date']:
            date_discrepancies.append(record['unique_id'])
        if (book['Transcripts'].cell(row, 11).value or '') != record['timestamps']:
            timestamp_discrepancies.append(record['unique_id'])
    check('All Excel durations preserve seconds and elapsed-hour formatting', duration_discrepancies, [])
    check('All Excel timestamp text preserves the source distinctions', timestamp_discrepancies, [])
    check('All Excel source and video dates preserve ISO days/composites', date_discrepancies, [])
    check('Summary partial-source formula', book['Summary']['B43'].value, 6)
    book.close()

    valid = {'0:00': 0, '02:03': 123, '4:59:59': 17999, '25740': 25740}
    check('Valid duration examples', {k: assembler.seconds(k) for k in valid}, valid)
    malformed = {x: assembler.seconds(x) for x in ['1:99', '04:60:00', '01:00:60']}
    boundary_fixed = all(v is None for v in malformed.values())
    receipt = {
        'review_id': 'review06', 'base_commit': '620cc5eb85860ff77a837058903321876de82b15',
        'assembler_sha256': hashlib.sha256(assembler_path.read_bytes()).hexdigest(),
        'workbook_sha256': hashlib.sha256((base / 'JEP_transcript_inventory.xlsx').read_bytes()).hexdigest(),
        'published_data_checks': checks,
        'published_data_all_passed': all(c['passed'] for c in checks),
        'cell_counts': {'durations': duration_count, 'source_dates': len(inventory), 'video_dates': sum(bool(r.get('date')) for r in videos), 'populated_video_timestamp_cells': sum(bool(r['timestamps']) for r in videos)},
        'malformed_duration_counterexample': {'actual': malformed, 'expected': dict.fromkeys(malformed), 'fixed': boundary_fixed},
    }
    (Path(__file__).resolve().parent / 'observations.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'published_data_all_passed': receipt['published_data_all_passed'], 'cell_counts': receipt['cell_counts'], 'malformed_duration_counterexample': receipt['malformed_duration_counterexample']}))
    return int(not receipt['published_data_all_passed'] or args.require_fixed and not boundary_fixed)


if __name__ == '__main__':
    raise SystemExit(main())
