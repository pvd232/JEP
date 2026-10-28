"""Read-only audit of frozen native development archives; no models."""
from pathlib import Path
import argparse
import ast
import collections
import hashlib
import json
import re
import tarfile
import tempfile

PHASE_MODELS = (
    ('native-task-contract-v2', ('gollie', 'knowcoder_ie')),
    ('native-one-shot-v1', ('gollie', 'knowcoder_ie')),
    ('finite-count-v2', ('gollie', 'knowcoder')),
    ('guided-count-v1', ('gollie', 'knowcoder')),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def literal_empty(raw):
    tree = ast.parse(raw.strip(), mode='exec')
    node = tree.body[0].value
    return not node.elts if isinstance(node, ast.List) else None


def source_from_prompt(prompt):
    rows = re.findall(r'^(?:text|sentence) = (.+)$', prompt, re.M)
    return json.loads(rows[-1])


def audit(path):
    with tarfile.open(path) as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        if len({m.name for m in members}) != len(members):
            raise ValueError('Duplicate archive file path')
        files = {m.name: tar.extractfile(m).read() for m in members}
        if any(len(files[m.name]) != m.size for m in members):
            raise ValueError('Archive member byte size differs')
    indexes = []
    for name, raw in files.items():
        if not (name.endswith('/capture-index.json') or name.endswith('-execution-index.json')
                or name.endswith('-capture-index.json')):
            continue
        index = json.loads(raw)
        checked = 0
        size_checked = 0
        for relative, entry in index.items():
            expected = entry if isinstance(entry, str) else entry['sha256']
            candidates = [relative, str(Path(name).parent / relative)]
            matches = [candidate for candidate in candidates if candidate in files]
            if not matches:
                raise ValueError(f'Missing indexed file: {path.name}:{name}:{relative}')
            content = files[matches[0]]
            if sha(content) != expected:
                raise ValueError(f'Hash mismatch: {matches[0]}')
            checked += 1
            if isinstance(entry, dict) and 'bytes' in entry:
                if entry['bytes'] != len(content):
                    raise ValueError(f'Indexed size mismatch: {matches[0]}')
                size_checked += 1
        indexes.append({'path': name, 'hashes_verified': checked,
                        'explicit_index_sizes_verified': size_checked})
    if not indexes:
        raise ValueError('No capture/execution index found')
    packets = {}
    for name, raw in files.items():
        if Path(name).name in ('task-contract-requests.json', 'one-shot-requests.json'):
            for item in json.loads(raw)['items']:
                packets[item['case_id']] = item
    generations = []
    ordinary = []
    counts = []
    for name, raw in files.items():
        if name.endswith('-generation.json'):
            item = json.loads(raw)
            case = item['case_id']
            packet = packets[case]
            source = source_from_prompt(item['prompt'])
            if source != packet['passage']:
                raise ValueError('Captured prompt target differs from frozen request')
            output = item.get('api_text', item.get('raw_decoded_generation'))
            row = {'case_id': case, 'condition': packet['condition'], 'passage': source,
                   'raw_output': output, 'empty_literal_list': literal_empty(output),
                   'generation_artifact': name}
            ordinary.append(row)
            generations.append((name, item))
        elif name.startswith('results/') and name.endswith('/result.json'):
            item = json.loads(raw)
            attempt = json.loads(files[name.removesuffix('result.json') + 'attempt.json'])
            row = {'source': attempt['source'], 'runtime_status': item['runtime_status'],
                   'parse_valid': item['parse_valid'], 'error': item['error'],
                   'quantity': item['normalized_evidence'].get('quantity')
                       if item['normalized_evidence'] else None, 'stages': []}
            if 'stage_outputs' not in item:
                generated = item['generation']
                row['raw_output'] = item['raw_output']
                row['quote_evidence'] = item['normalized_evidence']
                row['stages'] = []
                generations.append((name, generated))
            for stage in item.get('stage_outputs', []):
                generated = stage.get('generated')
                row['stages'].append({'stage': stage['stage'], 'parse_valid': stage['parse_valid'],
                    'runtime_status': stage['runtime_status'], 'error': stage['error'],
                    'raw_output': generated['payload'] if generated else None,
                    'empty_literal_list': literal_empty(generated['payload']) if generated else None})
                if generated:
                    generations.append((name + '#' + stage['stage'], generated))
            counts.append(row)
    termination = collections.Counter()
    for name, item in generations:
        ids = item['output_token_ids']
        if not ids:
            raise ValueError('Empty generated token vector')
        termination['generations'] += 1
        termination['final_token_id_2'] += ids[-1] == 2
        termination['truncated'] += bool(item['truncated'])
        termination['reported_output_length_matches'] += item['output_tokens'] == len(ids)
        termination['reported_input_length_matches'] += item['input_tokens'] == len(item['input_token_ids'])
        termination['stop_reason_' + str(item['stop_reason'])] += 1
    return {'archive': str(path), 'sha256': sha(path.read_bytes()),
            'archive_bytes': path.stat().st_size, 'regular_files': len(files),
            'tar_member_sizes_verified': len(files), 'indexes': indexes,
            'termination': dict(termination),
            'ordinary_nonempty': sum(not x['empty_literal_list'] for x in ordinary),
            'ordinary_cases': ordinary, 'count_cases': counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path, default=Path('/tmp'))
    parser.add_argument('--archive-index', type=Path,
                        help='Optional published archive index; all listed archive hashes/sizes are verified.')
    parser.add_argument('--output', type=Path,
                        help='New output directory; defaults to a unique directory under /tmp.')
    parser.add_argument('--include-count-evidence', action='store_true',
                        help='Also audit the two already captured quote-only execution archives; never runs models.')
    args = parser.parse_args()
    directory = args.archive_dir.resolve()
    index_path = args.archive_index
    if index_path is None:
        candidate = directory / 'csts_native_development_archives_20261028.json'
        if candidate.is_file():
            index_path = candidate
    index_proof = None
    if index_path is not None:
        index = json.loads(index_path.read_text())
        for item in index['archive_files']:
            if Path(item['file']).name != item['file'] or not item['file'].endswith('.tar.gz'):
                raise ValueError('Archive index must contain archive basenames only')
            path = directory / item['file']
            if path.stat().st_size != item['bytes'] or sha(path.read_bytes()) != item['sha256']:
                raise ValueError('Published archive hash/size differs: ' + item['file'])
        index_proof = {'path': str(index_path), 'sha256': sha(index_path.read_bytes()),
                       'archive_hashes_and_sizes_verified': len(index['archive_files'])}
    phases = list(PHASE_MODELS)
    if args.include_count_evidence:
        phases.append(('count-evidence-v1', ('gollie', 'knowcoder')))
    paths = []
    for phase, models in phases:
        for model in models:
            original = f'jep-{phase}-{model}-execution-20261028.tar.gz'
            published = ('csts_' + original.removeprefix('jep-')).replace('-', '_')
            choices = [directory / original, directory / published]
            found = next((path for path in choices if path.is_file()), None)
            if found is None:
                raise ValueError('Missing archive; expected ' + original + ' or ' + published)
            paths.append(found)
    records = [audit(path) for path in paths]
    totals = collections.Counter()
    for record in records:
        totals.update(record['termination'])
    report = {'scope': 'Independent read-only qualitative development-artifact audit; not human adjudication or a representative score.',
              'model_calls': 0, 'original_captures_modified': False,
              'source_scope': 'Previously exposed development sources only; no locked/fresh case inspection.',
              'numeric_count_success_claimed': False, 'model_ranking_claimed': False,
              'archive_index_verification': index_proof,
              'termination_totals': dict(totals), 'archives': records}
    output = args.output
    if output is None:
        output = Path(tempfile.mkdtemp(prefix='jep-native-artifact-audit-', dir='/tmp'))
    else:
        output.mkdir(parents=True, exist_ok=False)
    (output / 'artifact-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(output / 'artifact-audit.json'), 'archives': len(records),
                      'termination_totals': dict(totals)}))


if __name__ == '__main__':
    main()
