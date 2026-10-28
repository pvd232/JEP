"""Audit one already captured KnowCoder refinement against its prior task recipe."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import tarfile
import tempfile

UNCHANGED = ('animal', 'food', 'helmet', 'vehicle', 'animal_color', 'board_color')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def locate(directory, names):
    for name in names:
        path = directory / name
        if path.is_file():
            return path
    raise ValueError('Missing archive: ' + ' or '.join(names))


def load(path):
    with tarfile.open(path) as tar:
        members = [member for member in tar.getmembers() if member.isfile()]
        if len({member.name for member in members}) != len(members):
            raise ValueError('Duplicate archive member')
        files = {member.name: tar.extractfile(member).read() for member in members}
        if any(member.size != len(files[member.name]) for member in members):
            raise ValueError('TAR member byte size differs')
    proofs = []
    indexed = set()
    for name, raw in files.items():
        if not (name.endswith('/capture-index.json') or name.endswith('-execution-index.json')):
            continue
        index = json.loads(raw)
        sizes = 0
        for relative, entry in index.items():
            target = next((value for value in (relative, str(Path(name).parent / relative)) if value in files), None)
            if target is None:
                raise ValueError('Missing indexed file: ' + relative)
            expected = entry if isinstance(entry, str) else entry['sha256']
            if sha(files[target]) != expected:
                raise ValueError('Indexed hash differs: ' + target)
            if isinstance(entry, dict) and 'bytes' in entry:
                if entry['bytes'] != len(files[target]):
                    raise ValueError('Indexed size differs: ' + target)
                sizes += 1
            indexed.add(target)
        proofs.append({'index': name, 'hash_declarations_verified': len(index), 'byte_size_declarations_verified': sizes})
    generations = {json.loads(raw)['case_id']: (name, json.loads(raw))
                   for name, raw in files.items() if name.endswith('-generation.json')}
    if len(generations) != 9:
        raise ValueError('Expected exactly nine generated responses')
    return files, generations, {'archive': str(path), 'sha256': sha(path.read_bytes()),
        'bytes': path.stat().st_size, 'regular_member_sizes_verified': len(files),
        'unique_indexed_files_verified': len(indexed), 'indexes': proofs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path, default=Path('/tmp'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    current = locate(args.archive_dir, ('jep-know-refinement-v1-knowcoder_ie-execution-20261028.tar.gz',
        'csts_know_refinement_v1_knowcoder_ie_execution_20261028.tar.gz'))
    previous = locate(args.archive_dir, ('jep-native-task-contract-v2-knowcoder_ie-execution-20261028.tar.gz',
        'csts_native_task_contract_v2_knowcoder_ie_execution_20261028.tar.gz'))
    if sha(current.read_bytes()) != 'fce040366eb495629ddd320cb8c27e4ba857c8237e8f74f2ec83feaaf1cc3ee4':
        raise ValueError('Current execution archive differs from the reviewed frozen capture')
    if sha(previous.read_bytes()) != 'c796a45644f260350f6717c038348138d3bf4bef5d079c045529b525a92b9eca':
        raise ValueError('Prior execution archive differs from the reviewed frozen capture')
    files, newer, proof = load(current)
    _, older, previous_proof = load(previous)
    packets = [json.loads(raw) for name, raw in files.items() if name.endswith('/know-refinement-requests.json')]
    if len(packets) != 1:
        raise ValueError('Expected one frozen refinement packet')
    cases = {row['case_id']: row for row in packets[0]['items']}
    rows = []
    for case, (name, generation) in sorted(newer.items()):
        prior = older[case][1]
        row = cases[case]
        targets = re.findall(r'^(?:text|sentence) = (.+)$', generation['prompt'], re.M)
        if json.loads(targets[-1]) != row['passage'] or generation['prompt'] != row['requests']['knowcoder']['prompt']:
            raise ValueError('Frozen request/source differs')
        output_ids = generation['output_token_ids']
        if generation['output_tokens'] != len(output_ids) or generation['input_tokens'] != len(generation['input_token_ids']):
            raise ValueError('Reported token lengths differ')
        same_prompt = generation['prompt'] == prior['prompt']
        same_inputs = generation['input_token_ids'] == prior['input_token_ids']
        same_outputs = output_ids == prior['output_token_ids']
        if case in UNCHANGED and not (same_prompt and same_inputs and same_outputs):
            raise ValueError('Claimed unchanged NER/color cell differs: ' + case)
        rows.append({'case_id': case, 'condition': row['condition'], 'passage': row['passage'],
            'raw_output': generation['api_text'], 'previous_raw_output': prior['api_text'],
            'prompt_identical': same_prompt, 'input_ids_identical': same_inputs,
            'output_ids_identical': same_outputs, 'final_output_token_id': output_ids[-1],
            'truncated': generation['truncated'], 'artifact': name})
    report = {'scope': 'Final exposed Know-only candidate delta; qualitative review, no human adjudication or representative score.',
        'model_calls': 0, 'captures_modified': False, 'rollback_or_selection_performed': False,
        'current_archive': proof, 'previous_archive': previous_proof,
        'generated_responses': len(rows), 'final_token_id_2': sum(row['final_output_token_id'] == 2 for row in rows),
        'truncated_responses': sum(row['truncated'] for row in rows),
        'unchanged_ner_color_cells': list(UNCHANGED), 'all_six_prompt_input_output_id_comparisons_pass': True,
        'cases': rows,
        'qualitative_findings': [
            'Near(boy,water) now preserves the source spatial qualifier that was previously omitted.',
            'Dog remains only fetches: action category retained, but stick object and from-the-leaves phrase absent under full-clause contract.',
            'Girl changes from throws-leaves-over-head evidence to an empty list despite explicit source motion. This is a regression, not source absence.',
            'Six NER/color prompts and both input/output token vectors are identical to the prior task-contract captures.',
            'These observations do not establish a complete semantic gate, transfer or a model ranking. No tuning, rollback or count-success claim follows.'
        ]}
    output = args.output
    if output is None:
        output = Path(tempfile.mkdtemp(prefix='jep-know-refinement-delta-', dir='/tmp'))
    else:
        output.mkdir(parents=True, exist_ok=False)
    (output / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(output / 'review.json'), 'current_sha256': proof['sha256'],
        'generated_responses': len(rows), 'final_token_id_2': report['final_token_id_2'],
        'truncated': report['truncated_responses'], 'six_unchanged_comparisons_pass': True}))


if __name__ == '__main__':
    main()
