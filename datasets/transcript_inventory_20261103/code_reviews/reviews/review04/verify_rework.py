"""Observe the R04 repair without writing generator outputs or source caches.

Only derived IDs, measurements, and hashes are reported. The actual generator
runs in memory; its Path.write_text calls are intercepted, never persisted.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
from pathlib import Path
import re
import unicodedata
from unittest.mock import patch

ROOT = Path('/workspace/scratch/8a7e64850a04')
WORK = ROOT / 'inventory_work'
OUT = Path(__file__).resolve().parent
BASE = WORK / 'tieout_review_20261103/base'
SCRIPT = WORK / 'build_versiones_rows.py'
REGISTRY = WORK / 'tieout_review_20261103/accepted_record_ids.json'
META = WORK / 'versiones_metadata.json'
PAIRS = WORK / 'versiones_version_pairs.json'
METRICS = ROOT / 'outputs/jep_transcripts_20261103/version_comparisons.json'
EXTRACTED = WORK / 'versiones_text_private.json'
ORIGINAL_READ = Path.read_text


def digest(path):
    """Return exact byte SHA-256 without reporting file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text):
    """Tokenize lowercase, accent-stripped NFD text with Unicode word matches."""
    lowered = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if not unicodedata.combining(c))
    return re.findall(r'\w+', lowered)


def grams(words):
    """Return distinct ordered five-token tuples, retaining word repetitions."""
    return {tuple(words[i:i + 5]) for i in range(len(words) - 4)}


def execute_generator(source, metadata):
    """Execute current production source with metadata and all writes in memory."""
    writes = {}

    def read(path, *args, **kwargs):
        return json.dumps(metadata) if path == META else ORIGINAL_READ(path, *args, **kwargs)

    def write(path, text, *args, **kwargs):
        writes[str(path)] = text
        return len(text)

    with patch.object(Path, 'read_text', read), patch.object(Path, 'write_text', write), patch('builtins.print'):
        exec(compile(source, str(SCRIPT), 'exec'), {'__file__': str(SCRIPT), '__name__': 'review_only'})
    return json.loads(writes[str(WORK / 'versiones_rows_draft.json')])


def main():
    source = SCRIPT.read_text()
    parsed = ast.parse(source, str(SCRIPT))
    definitions = [node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name in {'read_record_id_registry', 'resolve_record_ids'}]
    namespace = {'json': json, 're': re}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(SCRIPT), 'exec'), namespace)
    load_registry, resolve = namespace['read_record_id_registry'], namespace['resolve_record_ids']
    by_source, reserved = load_registry(REGISTRY)
    accepted = json.loads((BASE / 'inventory.json').read_text())
    current = json.loads((ROOT / 'outputs/jep_transcripts_20261103/inventory.json').read_text())
    accepted_map = {r['unique_id']: r['source_file_ids'] for r in accepted}
    current_map = {r['unique_id']: r['source_file_ids'] for r in current}
    accepted_vv = {r['source_file_ids'][0]: r['unique_id'] for r in accepted if r['unique_id'].startswith('VV-')}
    metadata = json.loads(META.read_text())
    pairs = json.loads(PAIRS.read_text())
    checks = []

    def check(label, actual, expected):
        checks.append({'check': label, 'passed': actual == expected, 'actual': actual, 'expected': expected})

    def rejected(label, function, message):
        try:
            function()
        except ValueError as error:
            check(label, message in str(error), True)
        else:
            check(label, 'no rejection', 'ValueError')

    before_guard = {str(path.relative_to(ROOT)): digest(path) for path in [META, PAIRS, EXTRACTED, WORK / 'versiones_rows_draft.json', WORK / 'versiones_public_catalog_merged.json', BASE / 'inventory.json']}
    rows = execute_generator(source, metadata)
    before = {r['source_id']: r['unique_id'] for r in rows}
    check('actual generator preserves all 75 accepted VV IDs', before, accepted_vv)
    check('actual generator preserves all 87 VV source assignments', {r['unique_id']: r['source_file_ids'] for r in rows}, {uid: ids for uid, ids in accepted_map.items() if uid.startswith('VV-')})
    check('all 93 current canonical IDs and 105 assignments remain accepted', current_map, accepted_map)
    check('registry preserves all 93 accepted records and 105 source assignments', (len(reserved), len(by_source)), (93, 105))
    renamed = copy.deepcopy(metadata)
    target = '1PN1Snb8AnIUiJtuykAqEc3KMGBbhvcrc'
    for item in renamed['files']:
        if item['id'] == target:
            item['title'] = 'AAA_' + item['title']
    changed_rows = execute_generator(source, renamed)
    after = {r['source_id']: r['unique_id'] for r in changed_rows}
    check('title-only rename preserves all accepted IDs', after, before)
    check('renamed VV-057 retains its accepted ID', after[target], 'VV-057')
    _, reversed_map = resolve(list(reversed(metadata['files'])), pairs, by_source, reserved)
    check('metadata order does not affect IDs', reversed_map, before)
    first = pairs[0]
    canonical_id, variant_id = first['canonical_id'], first['variant_id']
    another_id = target
    merged_pairs = copy.deepcopy(pairs) + [{'canonical_id': canonical_id, 'variant_id': another_id}]
    rejected('merging two established records is rejected', lambda: resolve(metadata['files'], merged_pairs, by_source, reserved), 'mixes established record IDs')
    split_pairs = [pair for pair in pairs if pair['variant_id'] != variant_id]
    rejected('splitting an established source group is rejected', lambda: resolve(metadata['files'], split_pairs, by_source, reserved), 'more than one source group')
    swapped_pairs = copy.deepcopy(pairs)
    swapped_pairs[0]['canonical_id'], swapped_pairs[0]['variant_id'] = variant_id, canonical_id
    _, swapped = resolve(metadata['files'], swapped_pairs, by_source, reserved)
    check('changing preferred source preserves record identity', swapped[variant_id], by_source[canonical_id])
    new_variant = 'review_only_new_alternate'
    files_plus_variant = metadata['files'] + [{'id': new_variant}]
    _, with_variant = resolve(files_plus_variant, pairs + [{'canonical_id': canonical_id, 'variant_id': new_variant}], by_source, reserved)
    check('new alternate preserves its existing group ID', with_variant, before)
    new_file = 'review_only_new_source'
    _, with_new = resolve(metadata['files'] + [{'id': new_file}], pairs, by_source, reserved)
    check('only a truly new source group receives a new ID', with_new, {**before, new_file: 'VV-076'})
    _, new_only = resolve([{'id': new_file}], [], by_source, reserved)
    check('absent accepted records still reserve their IDs', new_only, {new_file: 'VV-076'})

    extracted = json.loads(EXTRACTED.read_text())
    comparisons = json.loads(METRICS.read_text())
    pair_results = []
    for pair in comparisons:
        a, b = pair['canonical_id'], pair['variant_id']
        ta, tb = tokens(extracted[a]['text']), tokens(extracted[b]['text'])
        ga, gb = grams(ta), grams(tb)
        shared = len(ga & gb)
        computed = {'words': [len(ta), len(tb)], 'shared_fivegrams': shared, 'containment': round(shared / min(len(ga), len(gb)), 3)}
        check('recomputed duplicate metrics ' + by_source[a], computed, {key: pair[key] for key in computed})
        pair_results.append({'record_id': by_source[a], 'canonical_id': a, 'variant_id': b, **computed, 'extracted_text_sha256': {a: hashlib.sha256(extracted[a]['text'].encode()).hexdigest(), b: hashlib.sha256(extracted[b]['text'].encode()).hexdigest()}, 'normalized_token_sha256': {a: hashlib.sha256(' '.join(ta).encode()).hexdigest(), b: hashlib.sha256(' '.join(tb).encode()).hexdigest()}})
    check('private caches and prior draft outputs are untouched', {path: digest(ROOT / path) for path in before_guard}, before_guard)
    compact_checks = []
    for result in checks:
        if result['passed'] and isinstance(result['actual'], dict):
            compact_checks.append({'check': result['check'], 'passed': True, 'compared_items': len(result['actual'])})
        else:
            compact_checks.append(result)
    normalizer_source = inspect.getsource(tokens) + '\n' + inspect.getsource(grams)
    result = {
        'all_checks_passed': all(item['passed'] for item in checks),
        'checks': compact_checks,
        'rename_observer': {'target_source_file_id': target, 'before': before[target], 'after': after[target], 'changed_record_ids': sum(before[fid] != after[fid] for fid in before), 'canonical_source_count': len(before), 'actual_generator_executions': 2, 'filesystem_writes': 'All generator Path.write_text calls intercepted in memory'},
        'pair_recomputations': pair_results,
        'normalizer': {'description': 'lowercase; Unicode NFD; discard combining characters; Unicode re.findall(r"\\w+"); distinct five-token tuple sets; containment rounded to 3 decimals', 'source_file': str(Path(__file__).relative_to(ROOT)), 'functions': ['tokens', 'grams'], 'source_sha256': hashlib.sha256(normalizer_source.encode()).hexdigest(), 'unicode_version': unicodedata.unidata_version},
        'extraction': {'retained_cache': str(EXTRACTED.relative_to(ROOT)), 'retained_cache_sha256': digest(EXTRACTED), 'source': 'Existing retained source-text extractions, not re-fetched or modified'},
        'file_sha256': {str(path.relative_to(ROOT)): digest(path) for path in [SCRIPT, REGISTRY, METRICS, Path(__file__)]},
    }
    (OUT / 'rework_observations.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'all_checks_passed': result['all_checks_passed'], 'checks': len(checks), 'failed_checks': [item for item in compact_checks if not item['passed']], 'rename_observer': result['rename_observer']}, indent=2))
    if not result['all_checks_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
