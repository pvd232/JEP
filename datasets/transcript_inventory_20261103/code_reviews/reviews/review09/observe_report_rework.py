#!/usr/bin/env python3
"""Focused offline recheck of R09-F01; preserves the frozen review receipt."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('review09_original_observer', HERE / 'observe_publication.py')
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
BASE = observer.BASE
TARGET = observer.ROOT / 'inventory_work/reverse_audit/finish_report.py'
INPUTS = ['summary.json', 'broad_metadata_scope.json', 'scope_decisions.json',
          'crawl_manifest.json', 'crawl_sources.json', 'pagination_reproduction.json',
          'standalone_replay_result.json', 'standalone_replay.json',
          'video_inventory.json', 'reverse_audit_report.md']


def change(path, update):
    value = observer.read(path)
    update(value)
    path.write_text(json.dumps(value))


def run_case(name, update=None):
    """Reuse the original observer's module/CLI boundary on an isolated copy."""
    with tempfile.TemporaryDirectory(prefix='report_rework_', dir=HERE) as temporary:
        output = Path(temporary)
        for filename in INPUTS:
            shutil.copy2(BASE / filename, output / filename)
        if update:
            update(output)
        before = {filename: observer.digest(output / filename)
                  for filename in ['summary.json', 'reverse_audit_report.md']}
        reporter = observer.module(TARGET, 'reworked_report_' + name)
        reporter.OUT = output
        result = observer.invoke(reporter, [])
        after = {filename: observer.digest(output / filename) for filename in before}
        result.update({'name': name, 'summary_unchanged': after['summary.json'] == before['summary.json'],
                       'report_unchanged': after['reverse_audit_report.md'] == before['reverse_audit_report.md']})
        if update:
            result['passed'] = (result['exit_code'] != 0 and result['summary_unchanged']
                                and result['report_unchanged']
                                and 'FileNotFoundError' not in (result['error'] or ''))
        else:
            result['passed'] = result['exit_code'] == 0 and result['report_unchanged'] and result['summary_unchanged']
        return result


def original_failed_proof(output):
    def fail_proof(value):
        value['checks'][0]['passed'] = False
        value['all_passed'] = False
    change(output / 'pagination_reproduction.json', fail_proof)
    change(output / 'standalone_replay_result.json', lambda value: value.update(all_passed=False, exit_code=1))


def main():
    cases = [
        run_case('valid_frozen_inputs'),
        run_case('original_failed_proof', original_failed_proof),
        run_case('failed_check_despite_true_aggregate', lambda output: change(
            output / 'pagination_reproduction.json', lambda value: value['checks'][0].update(passed=False))),
        run_case('false_replay_aggregate', lambda output: change(
            output / 'standalone_replay_result.json', lambda value: value.update(all_passed=False))),
        run_case('nonzero_replay_exit', lambda output: change(
            output / 'standalone_replay_result.json', lambda value: value.update(exit_code=1))),
        run_case('missing_replay_exit', lambda output: change(
            output / 'standalone_replay_result.json', lambda value: value.pop('exit_code'))),
        run_case('failed_full_replay_check', lambda output: change(
            output / 'standalone_replay.json', lambda value: value['checks'][0].update(passed=False))),
        run_case('inconsistent_replay_count', lambda output: change(
            output / 'standalone_replay_result.json', lambda value: value.update(checks=value['checks'] + 1))),
        run_case('nonboolean_check_result', lambda output: change(
            output / 'pagination_reproduction.json', lambda value: value['checks'][0].update(passed=1))),
    ]
    manifest = observer.read(HERE.parents[1] / 'baseline_hashes.json')
    changed = [name for name, expected in manifest['files'].items() if observer.digest(BASE / name) != expected]
    result = {
        'finding': 'R09-F01',
        'base_commit': manifest['commit'],
        'fixed_file': str(TARGET.relative_to(observer.ROOT)),
        'base_file_sha256': manifest['files']['workbook_build/finish_report.py'],
        'fixed_file_sha256': observer.digest(TARGET),
        'command': '"$CODEX_PRIMARY_RUNTIME_PYTHON" inventory_work/tieout_review_20261103/reviews/review09/observe_report_rework.py',
        'python': sys.executable,
        'observer_sha256': observer.digest(Path(__file__)),
        'frozen_review_sha256': {name: observer.digest(HERE / name)
                                 for name in ['review.md', 'review.json', 'observations.json', 'observe_publication.py']},
        'cases': cases,
        'checks': len(cases),
        'all_passed': all(case['passed'] for case in cases) and not changed,
        'network_requests': 0,
        'changed_frozen_files': changed,
        'shared_output_writes': 0,
        'verdict': 'R09-F01 repaired' if all(case['passed'] for case in cases) and not changed else 'Rework incomplete',
    }
    (HERE / 'rework.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
