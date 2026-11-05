"""CPU-only operational proof for two already frozen native48 capture archives."""
from pathlib import Path
import argparse
import collections
import hashlib
import importlib.util
import json
import sys
import tarfile
import tempfile

EXPECTED = {
    'knowcoder': 'f01cc8aba5da050e0902afd2bed9028100dfcf4aa7675b30ad7cdb42df6c7189',
    'gollie': '92efafb0154ec7271325801cceb2113f125c756b6b10a311ab6ae3a85904d7d5',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def archived_codec(model, files, provider):
    """Load only the verified regular codec/tokenizer bytes, without tar extraction."""
    tokenizer_relative = ('gollie_pinned/tokenizer.json' if model == 'gollie'
                          else 'legacy_support/pinned-metadata/ie/tokenizer.json')
    # Both names are fixed here. No archive member name is used as an output path.
    # codec() loads its encoder/decoder fully before this private directory closes.
    with tempfile.TemporaryDirectory(prefix='jep-native48-cpu-codec-') as temporary:
        root = Path(temporary)
        cpu_path = root / 'native_cpu_codec.py'
        tokenizer_path = root / 'tokenizer.json'
        cpu_path.write_bytes(files[provider + 'native_cpu_codec.py'])
        tokenizer_path.write_bytes(files[provider + tokenizer_relative])
        spec = importlib.util.spec_from_file_location('frozen_cpu_codec_' + model, cpu_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.codec(model, tokenizer_path)


def audit(model, directory):
    archive = directory / f'jep-final-native-48-v1-{model}-execution-20261028.tar.gz'
    if sha(archive.read_bytes()) != EXPECTED[model]:
        raise ValueError('Frozen execution archive differs')
    with tarfile.open(archive) as tar:
        members = [member for member in tar.getmembers() if member.isfile()]
        files = {member.name: tar.extractfile(member).read() for member in members}
        if len(files) != len(members) or any(len(files[m.name]) != m.size for m in members):
            raise ValueError('Duplicate member or TAR byte-size mismatch')
    checks = 0
    for name, raw in files.items():
        if name.endswith('-execution-index.json'):
            for target, digest in json.loads(raw).items():
                if target not in files or sha(files[target]) != digest:
                    raise ValueError('Execution-index hash differs')
                checks += 1
    job = 'inputs/jep-native-positive-diagnostic-job-v1-20261028/'
    seal = json.loads(files[job + 'job-seal.json'])
    for name, digest in seal['artifacts'].items():
        if sha(files[job + name]) != digest:
            raise ValueError('Frozen job artifact differs')
    sources = json.loads(files[job + 'sources.json'])
    if len(sources) != 48 or len({row['id'] for row in sources}) != 48:
        raise ValueError('Source denominator differs')
    if any(set(row) != {'id', 'passage', 'condition'} for row in sources):
        raise ValueError('Inference source contains forbidden fields')
    protocol = json.loads(files[job + 'protocol.json'])
    root = f'final-native-48-bridge-v1-execution/{model}/'
    manifest = json.loads(files[root + 'manifest.json'])
    started = json.loads(files[root + 'started.json'])
    ids = {row['id'] for row in sources}
    if manifest['completed_records'] != 48 or started['expected_sources'] != 48:
        raise ValueError('Capture denominator differs')
    if manifest['job_seal_sha256'] != sha(files[job + 'job-seal.json']):
        raise ValueError('Capture job identity differs')
    if manifest['started_sha256'] != sha(files[root + 'started.json']):
        raise ValueError('Started receipt differs')
    for field, suffix in (('capture_artifact_sha256', 'capture.json'),
                          ('request_artifact_sha256', 'request.json'),
                          ('handler_return_artifact_sha256', 'handler-return.json')):
        if set(manifest[field]) != ids:
            raise ValueError('Capture manifest source coverage differs')
        for identity, digest in manifest[field].items():
            if sha(files[root + identity + '/' + suffix]) != digest:
                raise ValueError('Manifest raw/request/capture hash differs')
    provider = 'inputs/jep-native-positive-diagnostic-capture-20261028/'
    support = json.loads(files[provider + 'support-seal.json'])
    for name, digest in support['files'].items():
        if sha(files[provider + name]) != digest:
            raise ValueError('Frozen provider file differs: ' + name)
    codec = archived_codec(model, files, provider)
    status = collections.Counter()
    termination = collections.Counter()
    errors = []
    call_rows = []
    for source in sources:
        identity = source['id']
        folder = root + identity + '/'
        record = json.loads(files[folder + 'capture.json'])
        request = json.loads(files[folder + 'request.json'])
        original = json.loads(files[folder + 'handler-return.json'])
        if request != {'source': source, 'model': model, 'protocol_sha256': seal['protocol_sha256']}:
            raise ValueError('Request source/model/protocol differs')
        if record['id'] != identity or record['model'] != model or record['protocol_sha256'] != seal['protocol_sha256']:
            raise ValueError('Capture source/model/protocol differs')
        if any(record[key] != original[key] for key in ('raw_output', 'stage_outputs', 'normalized_evidence', 'model_calls', 'runtime_status', 'error')):
            raise ValueError('Bridge altered raw handler evidence')
        if record['automatic_retries'] is not False or record['automatic_companion_cases'] is not False:
            raise ValueError('Unexpected retry/companion policy')
        status[record['runtime_status']] += 1
        calls = record['model_calls']
        if calls != len(record['bound_inputs']) or calls != len(record['stage_outputs']):
            raise ValueError('Actual calls, bindings and retained stages differ')
        if record['runtime_status'] == 'error':
            if calls or record['raw_output'] is not None or source['passage'] != '':
                raise ValueError('Expected zero-call empty-input failure differs')
            errors.append({'source_id': identity, 'error': record['error'], 'passage_length': 0, 'model_calls': calls})
        for binding, stage in zip(record['bound_inputs'], record['stage_outputs']):
            generated = stage['generated']
            inputs, outputs = generated['input_token_ids'], generated['output_token_ids']
            if inputs != codec.encode(binding['prompt']) or sha(binding['prompt'].encode()) != binding['prompt_sha256']:
                raise ValueError('Actual input IDs or prompt hash differs')
            if binding['input_tokens'] != len(inputs) or generated['input_tokens'] != len(inputs) or generated['output_tokens'] != len(outputs):
                raise ValueError('Recorded token lengths differ')
            if len(inputs) + binding['max_new_tokens'] > binding['context_limit'] or len(outputs) > binding['max_new_tokens']:
                raise ValueError('Token budget exceeded')
            raw = codec.decode(outputs, skip_special_tokens=True)
            if generated['raw_decoded_generation'] != raw or generated['raw_decode_with_special_tokens'] != codec.decode(outputs):
                raise ValueError('Actual output IDs/raw decodings differ')
            if model == 'gollie':
                if generated['payload'] != raw:
                    raise ValueError('Go payload differs from output IDs')
            elif generated['payload'] != generated['api_text'] or generated['api_text'].strip() != raw.split('"""', 1)[0].strip():
                raise ValueError('Know API envelope differs beyond declared stop/whitespace')
            termination['responses'] += 1
            termination['last_token_id_2'] += bool(outputs and outputs[-1] == 2)
            termination['truncated'] += bool(generated['truncated'])
            termination['stop_' + generated['stop_reason']] += 1
            call_rows.append({'source_id': identity, 'stage': stage['stage'], 'input_tokens': len(inputs),
                'output_tokens': len(outputs), 'prompt_sha256': binding['prompt_sha256'],
                'output_ids_sha256': sha(canonical(outputs)), 'last_token_id': outputs[-1] if outputs else None,
                'truncated': generated['truncated'], 'raw_decode_verified': True})
    if status != {'ok': 31, 'unsupported': 10, 'error': 7} or termination['responses'] != 31:
        raise ValueError('Frozen operational totals differ')
    return {'model': model, 'archive': str(archive), 'sha256': EXPECTED[model],
        'tar_member_lengths_verified': len(files), 'execution_index_hashes_verified': checks,
        'manifest_raw_request_capture_hashes_verified': 144, 'fixed_denominator': 48,
        'inference_source_fields_only': ['id', 'passage', 'condition'], 'runtime_status_counts': dict(status),
        'termination': dict(termination), 'empty_input_precondition_failures': errors, 'actual_calls': call_rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path, default=Path('/tmp'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--tokenizers-path', type=Path, default=Path('/tmp/jep-native-tokenizer-20261028'))
    args = parser.parse_args()
    if args.tokenizers_path.is_dir():
        sys.path.insert(0, str(args.tokenizers_path))
    rows = [audit(model, args.archive_dir)
            for model in ('knowcoder', 'gollie')]
    report = {'scope': 'Frozen original96 operational audit only; no semantic-quality judgment.',
        'model_calls_during_audit': 0, 'captures_modified': False, 'semantic_accuracy_score_produced': False,
        'fixed_total_denominator': 96, 'actual_model_responses': 62, 'unsupported_records': 20,
        'zero_call_empty_input_failures': 14, 'empty_failures_are_model_abstentions': False,
        'model_capability_inferred_from_zero_call_errors': False, 'models': rows}
    output = args.output
    if output is None:
        output = Path(tempfile.mkdtemp(prefix='jep-final48-operational-audit-', dir='/tmp'))
    else:
        output.mkdir(parents=True, exist_ok=False)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(output / 'report.json'), 'models': [
        {key: row[key] for key in ('model', 'fixed_denominator', 'runtime_status_counts', 'termination')}
        for row in rows]}))


if __name__ == '__main__':
    main()
