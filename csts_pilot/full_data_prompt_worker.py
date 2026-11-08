"""Bounded, one-GPU executor for an approved full-data prompt study.

Training phases are scientific continuous fits; native epoch boundaries retain
optimizer/RNG state. A separate authenticated IAP collector must checksum-verify
each generation in persistent cloud storage before acknowledging advancement.
No cloud credentials, provisioning or broad shutdown authority live in this module.
"""
from __future__ import annotations
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import tarfile
import time
import uuid
from typing import Any

from csts_pilot.full_data_prompt_protocol import (
    digest_file, digest_object, load_fit_cohorts, require_complete_selections,
    require_launch_approval, trial_matrix,
)


def utc() -> str:
    """UTC timestamp for execution receipts, not a completion estimate."""
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: Path, obj: Any) -> None:
    """Publish one durable JSON record after syncing its temporary bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.partial')
    with temp.open('w') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def emit(event: str, **data: Any) -> None:
    """Expose phase transitions without claiming buffered optimizer counts."""
    print(json.dumps({'utc': utc(), 'event': event, **data}, allow_nan=False), flush=True)


def publish_generation(root: Path, output: Path, generation: str,
                       record: dict[str, Any], state: dict[str, Any],
                       files: list[Path], *, wait_for_cloud: bool = True) -> None:
    """Seal native state locally, then wait for a matching verified cloud ACK.

    Never use unverified uploads or a pointer from another generation. If transfer
    fails, leave the complete local generation intact and exit at the bounded wait.
    """
    queue = output / 'transfer' / generation
    queue.mkdir(parents=True, exist_ok=True)
    archive = queue / 'native.tar'
    manifest_path = queue / 'ready.json'
    if not manifest_path.exists():
        snapshot = queue / 'worker-state.json'
        atomic_json(snapshot, state)
        items = [*files, snapshot]
        included: set[str] = set()
        temp = queue / 'native.tar.partial'
        with tarfile.open(temp, 'w') as tar:
            for path in items:
                if path.is_symlink():
                    raise ValueError("Native recovery bundle must not contain symlinks.")
                path = path.resolve()
                rel = str(path.relative_to(root.resolve()))
                if rel in included:
                    continue
                included.add(rel)
                if path.is_dir():
                    for candidate in path.rglob('*'):
                        if candidate.is_symlink():
                            raise ValueError('Native recovery bundle must not contain symlinks.')
                elif not path.is_file():
                    raise ValueError(f'Recovery artifact missing: {rel}')
                tar.add(path, arcname=rel, recursive=True)
        with temp.open('rb') as f: os.fsync(f.fileno())
        os.replace(temp, archive)
        manifest = {'generation': generation, 'worker': state['worker'],
                    'source_commit': state['source_commit'],
                    'protocol_sha256': state['protocol_sha256'],
                    'execution_id': state['lease']['execution_id'],
                    'instance_id': state['lease']['instance_id'],
                    'archive': str(archive), 'archive_sha256': digest_file(archive),
                    'archive_size': archive.stat().st_size,
                    'native_record': record, 'status': 'ready_for_verified_export'}
        atomic_json(manifest_path, manifest)
    manifest = json.loads(manifest_path.read_text())
    if digest_file(archive) != manifest['archive_sha256']:
        raise ValueError('Existing sealed transfer archive changed.')
    emit('checkpoint_export_ready', generation=generation,
         sha256=manifest['archive_sha256'], bytes=manifest['archive_size'])
    if not wait_for_cloud:
        pending = [p for p in (output / 'transfer').glob('*/ready.json')
                   if not (p.parent / 'ack.json').exists()]
        if len(pending) <= 2:
            return
        # Bound recoverable work and disk usage when publication falls behind.
        oldest = min(pending, key=lambda p: p.stat().st_mtime)
        old = json.loads(oldest.read_text())
        wait_for_generation(oldest.parent, old, output)
        return
    wait_for_generation(queue, manifest, output)


def wait_for_generation(queue: Path, manifest: dict[str, Any], output: Path) -> None:
    """Wait for an ACK bound to immutable generation bytes, including an older lease."""
    deadline = time.monotonic() + 1200
    while time.monotonic() < deadline:
        ackpath = queue / 'ack.json'
        if ackpath.exists():
            ack = json.loads(ackpath.read_text())
            if (ack.get('generation'), ack.get('source_commit'), ack.get('archive_sha256'),
                ack.get('cloud_roundtrip_verified'), ack.get('execution_id'), ack.get('instance_id')) != (
                    manifest['generation'], manifest['source_commit'], manifest['archive_sha256'], True,
                    manifest['execution_id'], manifest['instance_id']):
                raise ValueError('Collector acknowledgment is not bound to this exact generation.')
            atomic_json(output / 'verified-cloud-generation.json', ack)
            emit('checkpoint_cloud_verified', generation=manifest['generation'])
            return
        time.sleep(5)
    raise TimeoutError('Checkpoint export was not verified; local state preserved, no advancement.')


def run_training(root: Path, output: Path, protocol: dict[str, Any], state: dict[str, Any],
                 seeds: list[int], gpu_model: str) -> None:
    """Execute assigned seed blocks, respecting prior sealed generations and stopping."""
    from viper import execution
    from viper.repository import read_source
    from csts_pilot.convergence_run import artifact_path
    from csts_pilot.full_data_prompt_native import epoch_plan
    from csts_pilot.full_data_prompt_integrity import seal_native_selection

    source = read_source(root)
    rows = [r for r in trial_matrix(protocol) if r['seed'] in seeds]
    for trial in rows:
        key, arm, seed = trial['trial_id'], trial['arm'], trial['seed']
        prior = state['trials'].setdefault(key, {'arm': arm, 'seed': seed, 'records': []})
        if prior.get('selection'):
            continue
        for _ in range(protocol['training']['max_epochs']):
            parent = prior['records'][-1] if prior['records'] else None
            trace = None
            if parent:
                trace_path = artifact_path(parent, 'train', 'trace', 'trace.json')
                trace = json.loads(trace_path.read_text())
                generation = f'{key}_epoch{len(trace["epochs"]):02}'
                # A crash after local-state commit but before export must finish
                # that exact publication before selecting or continuing.
                publish_generation(root, output, generation, parent, state,
                                   [Path(parent['path']).parent], wait_for_cloud=False)
                stale_pending = output / 'pending-native.json'
                if stale_pending.exists():
                    pending_info = json.loads(stale_pending.read_text())
                    if (pending_info.get('trial'), pending_info.get('epoch')) == (key, len(trace['epochs'])):
                        stale_pending.unlink()
                    else:
                        raise RuntimeError('Unreconciled native attempt differs from sealed parent.')
                if trace['stop_reason'] == 'validation_patience':
                    selected = seal_native_selection(root, protocol, parent['source_commit'], arm, seed, parent,
                                                     state['training_source_commit'])
                    prior['selection'] = selected
                    atomic_json(output / 'state.json', state)
                    emit('trial_validation_selected', trial=key, epoch=selected['selected_epoch'],
                         validation_spearman=selected['validation_metrics']['spearman'])
                    break
                if len(trace['epochs']) >= protocol['training']['max_epochs']:
                    raise RuntimeError(f'{key}: epoch cap reached without patience convergence.')
            epoch = 1 if trace is None else len(trace['epochs']) + 1
            pending = output / 'pending-native.json'
            if pending.exists():
                raise RuntimeError('An interrupted native attempt requires explicit reconciliation; no duplicate launch.')
            planned = epoch_plan(root, protocol, arm, seed, gpu_model, parent, trace)
            atomic_json(pending, {'trial': key, 'epoch': epoch, 'source_commit': source.commit,
                                 'started_utc': utc(), 'attempt': uuid.uuid4().hex})
            emit('native_epoch_start', trial=key, epoch=epoch)
            started = time.monotonic()
            result = execution.run(planned, timeout_seconds=14400,
                                   trusted_source_repositories=frozenset({str(source.repository)}))
            record = {'status': result.status, 'path': str(result.path),
                      'reference': result.reference.model_dump(mode='json'),
                      'source_commit': source.commit, 'trial_id': key,
                      'seconds': time.monotonic() - started}
            if result.status != 'succeeded':
                atomic_json(output / 'failed-native.json', record)
                raise RuntimeError(f'{key} epoch {epoch}: native execution {result.status}')
            actual_trace = json.loads(artifact_path(record, 'train', 'trace', 'trace.json').read_text())
            if (actual_trace.get('status') != 'complete'
                    or actual_trace.get('actual_updates') != 190 * epoch
                    or len(actual_trace.get('epochs', [])) != epoch):
                raise ValueError('Native run completed with inconsistent full-data counters.')
            prior['records'].append(record)
            atomic_json(output / 'state.json', state)
            pending.unlink()
            generation = f'{key}_epoch{epoch:02}'
            # Preserve all native bytes for that execution, including model/optimizer/RNG.
            native_run = Path(record['path']).parent
            publish_generation(root, output, generation, record, state, [native_run], wait_for_cloud=False)
            emit('native_epoch_sealed', trial=key, epoch=epoch,
                 stop_reason=actual_trace['stop_reason'])
        if not prior.get('selection'):
            # The final permitted iteration might have just sealed a patience stop.
            last = prior['records'][-1]
            prior['selection'] = seal_native_selection(root, protocol, last['source_commit'], arm, seed, last,
                                                       state['training_source_commit'])
            atomic_json(output / 'state.json', state)
    selected = [state['trials'][r['trial_id']]['selection'] for r in rows]
    initial = {}
    for s in selected:
        initial.setdefault(s['seed'], set()).add(s['initial_trainable_sha256'])
    if any(len(v) != 1 for v in initial.values()):
        raise ValueError('Within-seed initial adapter weights differed across prompt arms.')
    atomic_json(output / 'selections.json', selected)
    state['status'] = 'assigned_training_complete_test_not_opened'
    state['final_generation'] = 'training-final-' + state['lease']['execution_id']
    atomic_json(output / 'state.json', state)
    publish_generation(root, output, state['final_generation'], {}, state,
                       [output / 'selections.json', output / 'state.json'])
    for manifest_path in sorted((output / 'transfer').glob('*/ready.json')):
        wait_for_generation(manifest_path.parent, json.loads(manifest_path.read_text()), output)
    emit('assigned_training_complete', trials=len(selected), test_opened=False)


def require_training_compatibility(root: Path, source: str, training_source: str) -> None:
    """Allow controller repairs while requiring unchanged model, loss, data and protocol code."""
    import re
    import subprocess
    if any(re.fullmatch(r"[0-9a-f]{40}", value) is None for value in (training_source, source)):
        raise ValueError("Training compatibility must name an immutable source commit.")
    scoped = ["csts_pilot", "jep_pilot", "configs", "pilot_requirements.txt", "tranche2_requirements.txt"]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", training_source, source, "--", *scoped],
        cwd=root, text=True, timeout=30,
    ).splitlines()
    controllers = {
        "csts_pilot/full_data_prompt_integrity.py", "csts_pilot/full_data_prompt_lease.py",
        "csts_pilot/full_data_prompt_worker.py", "csts_pilot/full_data_prompt_uploads.py",
    }
    if set(changed) - controllers:
        raise ValueError("Training revision changes scientific code or inputs: " + ", ".join(changed))


def observed_runtime(gpu_model: str) -> dict[str, Any]:
    """Capture actual GPU type and the pinned Python distribution fingerprint."""
    import subprocess
    from viper.runtime import observe_python_env
    actual = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True, timeout=10,
    ).strip().splitlines()
    if actual != [gpu_model]:
        raise ValueError('Actual GPU type differs from the approved training block.')
    return {'gpu_model': gpu_model, 'python_env': observe_python_env().model_dump(mode='json')}


def require_preserved_runtime(state: dict[str, Any], runtime: dict[str, Any]) -> None:
    """Require resumed seed blocks to retain their recorded GPU type and Python environment."""
    import yaml
    if state.get('runtime_block') is not None and state['runtime_block'] != runtime:
        raise ValueError('Resume changes the seed block GPU type or runtime.')
    for trial in state['trials'].values():
        for record in trial['records']:
            folder = Path(record['path']).parent
            resolved = yaml.safe_load((folder / 'resolved.yaml').read_text())
            spec = folder / 'spec.yaml'
            if digest_file(spec) != resolved['spec']['sha256']:
                raise ValueError('Preserved native runtime specification changed.')
            environment = yaml.safe_load(spec.read_text())['env']
            expected = {'gpu_model': environment['compute']['model'],
                        'python_env': environment['python_env']}
            if expected != runtime or environment['compute']['count'] != 1:
                raise ValueError('Preserved native fit used a different GPU type or runtime.')


def rebind_resume_state(state: dict[str, Any], approval: dict[str, Any], worker: str,
                        source: str, protocol_sha: str, lease: dict[str, Any],
                        state_sha: str) -> dict[str, Any]:
    """Rebind preserved completed work only under an explicit hash-bound resume record."""
    if (state['protocol_sha256'], state['worker']) != (protocol_sha, worker):
        raise ValueError('Existing worker state has different protocol or ownership.')
    preserved_source = state.get('training_source_commit', state['source_commit'])
    if approval.get('training_source_commit') != preserved_source:
        raise ValueError('Resume cannot replace the original scientific source.')
    for trial in state['trials'].values():
        selected = trial.get('selection')
        if selected and selected.get('training_source_commit') != preserved_source:
            raise ValueError('Preserved selections have conflicting scientific provenance.')
    if state['source_commit'] == source and state.get('lease') == lease:
        state['status'] = 'running'
        state.pop('failure', None)
        return state
    resume = approval.get('resumes', {}).get(worker, {})
    if (resume.get('state_sha256'), resume.get('previous_source_commit'),
            resume.get('previous_execution_id')) != (
                state_sha, state['source_commit'], state.get('lease', {}).get('execution_id')):
        raise ValueError('Explicit resume is not bound to the preserved state and prior lease.')
    history = state.setdefault('resume_history', [])
    history.append({'previous_source_commit': state['source_commit'],
                    'previous_lease': state['lease'], 'state_sha256': state_sha, 'resumed_utc': utc()})
    state.update(source_commit=source, lease=lease, status='running',
                 training_source_commit=preserved_source)
    state.pop('failure', None)
    return state


def main() -> None:
    """Run only an approved exact revision under an exclusive local worker lock."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=['worker1', 'worker2'], required=True)
    parser.add_argument('--approval', type=Path, required=True)
    parser.add_argument('--reviews', type=Path, required=True)
    parser.add_argument('--gpu-model', default='NVIDIA L4')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    from viper.repository import resolve_root, read_source
    root = resolve_root()
    source = read_source(root)
    protocol = json.loads((root / 'configs/csts-full-data-prompt-20261107.json').read_text())
    approval = json.loads(args.approval.read_text())
    require_launch_approval(protocol, source.commit, approval, json.loads(args.reviews.read_text()))
    training_source = approval.get('training_source_commit', source.commit)
    require_training_compatibility(root, source.commit, training_source)
    load_fit_cohorts(root, protocol)
    seeds = [7, 9, 11] if args.worker == 'worker1' else [8, 10]
    output = root / 'baseline_results/full_data_prompt_20261107' / args.worker
    output.mkdir(parents=True, exist_ok=True)
    with (root.parent / 'gpu-exclusive.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        from csts_pilot.full_data_prompt_lease import inspect_local_assignment
        lease = inspect_local_assignment(args.worker, approval['assignments'][args.worker])
        runtime = observed_runtime(args.gpu_model)
        state_path = output / 'state.json'
        if state_path.exists():
            if not args.resume:
                raise ValueError('Existing work requires explicit --resume.')
            state = json.loads(state_path.read_text())
            require_preserved_runtime(state, runtime)
            preserved_training_source = state.get('training_source_commit', state['source_commit'])
            require_training_compatibility(root, state['source_commit'], preserved_training_source)
            for trial in state['trials'].values():
                for record in trial['records']:
                    require_training_compatibility(root, record['source_commit'], preserved_training_source)
            previous_bytes = state_path.read_bytes()
            previous_sha = digest_file(state_path)
            archive = state_path.with_name('state.' + state['lease']['execution_id'] + '.before-resume.json')
            if not archive.exists():
                archive.write_bytes(previous_bytes)
            state = rebind_resume_state(state, approval, args.worker, source.commit,
                                        digest_object(protocol), lease, previous_sha)
            state['runtime_block'] = runtime
            atomic_json(state_path, state)
        else:
            state = {'source_commit': source.commit, 'protocol_sha256': digest_object(protocol),
                     'worker': args.worker, 'seeds': seeds, 'status': 'running', 'trials': {},
                     'started_utc': utc(), 'test_opened': False, 'lease': lease,
                     'training_source_commit': training_source, 'runtime_block': runtime}
            atomic_json(state_path, state)
        try:
            run_training(root, output, protocol, state, seeds, args.gpu_model)
        except BaseException as exc:
            state['status'] = 'failed_preserved'
            state['failure'] = {'type': type(exc).__name__, 'message': str(exc), 'utc': utc()}
            atomic_json(state_path, state)
            publish_generation(root, output, 'worker-failed-' + state['lease']['execution_id'], {}, state,
                               [state_path], wait_for_cloud=False)
            raise


if __name__ == '__main__':
    main()
