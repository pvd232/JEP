#!/usr/bin/env python3
"""Offline review of the published replay, reporting, and CLI failure boundary.

Writes temporary inputs only under this review directory and deletes them
after observation. Retained raw responses never enter publication artifacts.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE.parents[1] / 'base'


def read(path):
    """Read one JSON input without mutating it."""
    return json.loads(path.read_text())


def digest(path):
    """Bind a review observation to its exact input bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(path, name):
    """Import a reviewed module with bytecode writes disabled."""
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def invoke(loaded, argv):
    """Observe the module's actual CLI branch with its stdout held locally."""
    previous = sys.argv
    sys.argv = [str(loaded.__file__), *argv]
    code, error = 0, None
    stream = io.StringIO()
    try:
        with contextlib.redirect_stdout(stream):
            loaded.main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if code:
            error = str(exc)
    except Exception as exc:
        code, error = 1, type(exc).__name__ + ': ' + str(exc)
    finally:
        sys.argv = previous
    return {'exit_code': code, 'error': error}


def failed_report(reporter, output):
    """Change only proof success flags and observe the generated pass claim."""
    target = output / 'failed_report'
    target.mkdir(parents=True, exist_ok=True)
    for name in ['summary.json', 'broad_metadata_scope.json', 'scope_decisions.json', 'crawl_manifest.json', 'crawl_sources.json', 'pagination_reproduction.json', 'standalone_replay_result.json', 'video_inventory.json']:
        shutil.copy2(BASE / name, target / name)
    proof = read(target / 'pagination_reproduction.json')
    proof['checks'][0]['passed'] = False
    proof['all_passed'] = False
    (target / 'pagination_reproduction.json').write_text(json.dumps(proof))
    replay = read(target / 'standalone_replay_result.json')
    replay.update(all_passed=False, exit_code=1)
    (target / 'standalone_replay_result.json').write_text(json.dumps(replay))
    loaded = module(reporter, 'review09_reporter')
    loaded.OUT = target
    result = invoke(loaded, [])
    report = target / 'reverse_audit_report.md'
    body = report.read_text() if report.exists() else ''
    result.update({
        'input_reproduction_all_passed': False,
        'input_replay_all_passed': False,
        'input_replay_exit_code': 1,
        'generated_report': report.exists(),
        'claims_reproduction_passed_all': f"passed {len(proof['checks'])}/{len(proof['checks'])}" in body,
        'claims_replay_passed_all': f"passed {replay['checks']}/{replay['checks']}" in body,
    })
    return result


def failed_crawl(crawler, output):
    """Use the real crawl command with one deterministic transport failure."""
    target = output / 'failed_crawl'
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE / 'live_pagination_proof.json', target / 'live_pagination_proof.json')
    loaded = module(crawler, 'review09_failed_crawler')
    loaded.BASE, loaded.WORK, loaded.ORIGINAL = target, target / 'missing_work', target / 'missing_original'
    attempts = []

    def unavailable_request(url, body=None):
        attempts.append(url)
        raise TimeoutError('Deterministic offline transport failure')

    loaded.request = unavailable_request
    result = invoke(loaded, ['crawl', '--collections', 'case03'])
    state_path = target / 'caches/case03/state.json'
    state = read(state_path) if state_path.exists() else {}
    result.update({'transport_stub_calls': len(attempts), 'status': state.get('status'), 'pagination_exhausted': state.get('pagination_exhausted'), 'error_count': len(state.get('errors', []))})
    return result


def cached_live_probe(crawler, output):
    """Prove whether a cached replay can be labeled a new live success."""
    target = output / 'cached_live_probe'
    cache = target / 'caches/case03'
    cache.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'inventory_work/reverse_audit/caches/case03'
    for name in ['initial.html', 'page_000.json', 'page_000.meta.json', 'page_001.json', 'page_001.meta.json']:
        shutil.copy2(original / name, cache / name)
    shutil.copy2(BASE / 'pagination_reproduction.json', target / 'pagination_reproduction.json')
    loaded = module(crawler, 'review09_cached_crawler')
    loaded.BASE, loaded.WORK, loaded.ORIGINAL = target, target / 'missing_work', target / 'missing_original'
    attempts = []

    def no_network(url, body=None):
        attempts.append(url)
        raise AssertionError('The offline probe must use only the retained cache')

    loaded.request = no_network
    result = invoke(loaded, ['probe-next', '--collection', 'case03'])
    proof_path = target / 'live_pagination_proof.json'
    proof = read(proof_path) if proof_path.exists() else {}
    result.update({
        'network_calls': len(attempts),
        'proof_passed': proof.get('passed'),
        'proof_at': proof.get('at'),
        'actual_page_fetch_times': [read(cache / f'page_{i:03}.meta.json')['fetched_at'] for i in [0, 1]],
        'proof_field_names': sorted(proof),
        'freshness_or_cache_evidence': {k: v for k, v in proof.items() if re.search(r'cache|fetch|request|provenance|fresh|replay|network', k, re.I)},
    })
    return result


def publication_integrity():
    """Check exact published checksums and scan data for excluded raw fields."""
    frozen = read(HERE.parents[1] / 'baseline_hashes.json')['files']
    changed = [name for name, expected in frozen.items() if digest(BASE / name) != expected]
    manifest = read(BASE / 'pagination_fix/fixtures/fixture_manifest.json')
    fixture_checks = []
    for group in ['sources', 'channel_terminals']:
        for label, item in manifest[group].items():
            fixture_checks.append({'label': label, 'reduced_sha_matches': digest(BASE / 'pagination_fix/fixtures' / item['sanitized_fixture']) == item['sanitized_sha256'], 'original_sha_matches': digest(Path(item['original_path'])) == item['original_sha256']})
    script_sha = digest(BASE / 'pagination_fix/crawl_public_catalog.py')
    validation = read(BASE / 'workbook_validation.json')
    forbidden = {'access_token', 'refresh_token', 'streamingData', 'captionTracks', 'baseUrl', 'getTranscriptEndpoint', 'INNERTUBE_CONTEXT', 'ytInitialPlayerResponse', 'transcript_text', 'source_text', 'full_transcript'}
    hazards, token_values, inspected = [], [], []

    def walk(value, name, path=()):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in forbidden:
                    hazards.append({'file': name, 'path': '.'.join(map(str, (*path, key))), 'kind': 'raw_field'})
                if key == 'token':
                    token_values.append({'file': name, 'synthetic': isinstance(item, str) and item.startswith('fixture-')})
                walk(item, name, (*path, key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, name, (*path, i))
        elif isinstance(value, str) and re.search(r'https?://[^\s"<>]*(?:googlevideo\.com|[?&](?:signature|sig|expire|access_token)=)', value, re.I):
            hazards.append({'file': name, 'path': '.'.join(map(str, path)), 'kind': 'signed_media_or_credential_url'})

    for name in frozen:
        path = BASE / name
        if name.endswith('.json'):
            walk(read(path), name)
            inspected.append(name)
        elif name.endswith('.json.gz'):
            walk(json.loads(gzip.decompress(path.read_bytes())), name)
            inspected.append(name)
    with zipfile.ZipFile(BASE / 'JEP_transcript_inventory.xlsx') as archive:
        workbook_members = archive.namelist()
        executable_parts = [name for name in workbook_members if re.search(r'vbaProject|embeddings/|externalLink\d+\.xml$', name)]
    return {
        'frozen_file_count': len(frozen), 'changed_frozen_files': changed,
        'fixture_hash_checks': fixture_checks,
        'script_sha256': script_sha,
        'replay_script_sha_matches': read(BASE / 'standalone_replay_result.json')['script_sha256'] == script_sha,
        'catalog_validation_script_sha_matches': read(BASE / 'catalog_validation.json')['script_sha256'] == script_sha,
        'workbook_sha_matches_receipt': digest(BASE / 'JEP_transcript_inventory.xlsx') == validation['workbook_sha256'],
        'workbook_bytes_match_receipt': (BASE / 'JEP_transcript_inventory.xlsx').stat().st_size == validation['workbook_bytes'],
        'data_files_scanned': inspected, 'excluded_payload_findings': hazards,
        'fixture_tokens_are_synthetic': all(t['synthetic'] for t in token_values),
        'fixture_token_count': len(token_values), 'embedded_workbook_executable_parts': executable_parts,
    }


def main():
    """Run only the three review counterexamples and publication integrity scan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crawler', type=Path, default=BASE / 'pagination_fix/crawl_public_catalog.py')
    parser.add_argument('--reporter', type=Path, default=BASE / 'workbook_build/finish_report.py')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='observer_', dir=HERE) as temporary:
        output = Path(temporary)
        results = {
            'reviewed_commit': '620cc5eb85860ff77a837058903321876de82b15',
            'python': sys.executable,
            'tested_code_sha256': {'crawler': digest(args.crawler), 'reporter': digest(args.reporter)},
            'failed_proof_report': failed_report(args.reporter, output),
            'failed_crawl_cli': failed_crawl(args.crawler, output),
            'cached_live_probe': cached_live_probe(args.crawler, output),
            'publication_integrity': publication_integrity(),
            'network_requests': 0,
        }
    (HERE / 'observations.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in results.items() if k != 'publication_integrity'}, indent=2))
    print(json.dumps({'publication_integrity': {k: v for k, v in results['publication_integrity'].items() if k != 'data_files_scanned'}}, indent=2))


if __name__ == '__main__':
    main()
