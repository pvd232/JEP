#!/usr/bin/python3
"""Persistent systemd job controller. Commands and output are private to the dev user."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import uuid

CONFIG = Path(os.environ.get('CLOUD_DEV_CONFIG', '/etc/cloud-dev/profile.json'))


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def job_dir(profile, job_id):
    if not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise ValueError('Invalid job ID')
    path = Path(profile['paths']['state_root']) / 'jobs' / job_id
    if not (path / 'job.json').is_file():
        raise ValueError('Unknown job ID')
    return path


def unit(profile, job_id):
    return 'cloud-dev-' + profile['profile'] + '-job@' + job_id + '.service'


def run_job(profile, job_id):
    directory = job_dir(profile, job_id)
    with (directory / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = directory / 'job.json'
        data = json.loads(path.read_text())
        if data['status'] in ['succeeded', 'failed', 'cancelled']:
            return 0
        if data['status'] in ['running', 'interrupted']:
            data.update(status='interrupted', interrupted_at=now())
            if not data.get('resume_argv'):
                save(path, data)
                return 0
            command = data['resume_argv']
        else:
            command = data['argv']
        data.update(status='running', started_at=now(), worker_pid=os.getpid())
        save(path, data)
        cancelled = [False]

        def stop(signum, frame):
            cancelled[0] = True

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        environment = os.environ.copy()
        environment['PATH'] = profile['resolved']['node_bin_dir'] + ':' + profile['resolved']['bin_dir'] + ':' + environment.get('PATH', '/usr/bin:/bin')
        if profile.get('project_id'):
            from project import project_environment
            environment = project_environment(profile)
        with (directory / 'output.log').open('ab', buffering=0) as output:
            try:
                child = subprocess.Popen(command, cwd=data['cwd'], env=environment, stdout=output, stderr=subprocess.STDOUT)
                data['child_pid'] = child.pid
                save(path, data)
                code = child.wait()
                status = ('cancelled' if (directory / 'cancel_requested').exists() else 'interrupted') if cancelled[0] else ('succeeded' if code == 0 else 'failed')
                data.update(status=status, exit_code=code, finished_at=now())
            except BaseException as error:
                data.update(status='failed', error=str(error), exit_code=1, finished_at=now())
            save(path, data)
        return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=CONFIG)
    commands = parser.add_subparsers(dest='operation', required=True)
    submit = commands.add_parser('submit')
    submit.add_argument('--cwd', required=True)
    submit.add_argument('--checkpoint')
    submit.add_argument('--resume-json', help='Explicit JSON argv used to resume an interrupted job at boot')
    submit.add_argument('argv', nargs=argparse.REMAINDER)
    for name in ['status', 'cancel', '_run', '_finalize']:
        commands.add_parser(name).add_argument('job_id')
    logs = commands.add_parser('logs')
    logs.add_argument('job_id')
    logs.add_argument('--offset', type=int, default=0)
    logs.add_argument('--limit', type=int, default=16384)
    commands.add_parser('list')
    args = parser.parse_args()
    profile = json.loads(args.config.read_text())
    jobs = Path(profile['paths']['state_root']) / 'jobs'
    if args.operation == 'submit':
        argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
        if not argv or not Path(args.cwd).is_dir():
            raise ValueError('An existing cwd and command argv are required')
        job_id = uuid.uuid4().hex
        directory = jobs / job_id
        directory.mkdir(mode=0o700)
        data = {'id': job_id, 'status': 'queued', 'created_at': now(), 'cwd': str(Path(args.cwd).resolve()), 'argv': argv, 'checkpoint': args.checkpoint, 'resume_argv': json.loads(args.resume_json) if args.resume_json else None, 'git_revision': None}
        data['project_id'] = profile.get('project_id')
        data['environment_keys'] = sorted(profile['resolved'].get('project_environment', {}))
        if data['resume_argv'] is not None and (not isinstance(data['resume_argv'], list) or not all(isinstance(x, str) for x in data['resume_argv']) or not data['resume_argv']):
            raise ValueError('resume-json must be a nonempty argv array')
        revision = subprocess.run(['git', '-C', data['cwd'], 'rev-parse', 'HEAD'], capture_output=True, text=True)
        if revision.returncode == 0:
            data['git_revision'] = revision.stdout.strip()
        save(directory / 'job.json', data)
        service = unit(profile, job_id)
        try:
            subprocess.run(['sudo', '-n', 'systemctl', 'enable', service], check=True, capture_output=True)
            subprocess.run(['sudo', '-n', 'systemctl', 'start', '--no-block', service], check=True, capture_output=True)
        except subprocess.CalledProcessError as error:
            data.update(status='failed', error='systemd submission failed', finished_at=now())
            save(directory / 'job.json', data)
            raise RuntimeError('systemd submission failed') from error
        print(json.dumps({'id': job_id, 'status': 'submitted', 'unit': service, 'directory': str(directory)}))
    elif args.operation == 'list':
        print(json.dumps([json.loads(p.read_text()) for p in sorted(jobs.glob('*/job.json'))], indent=2))
    elif args.operation == '_run':
        return run_job(profile, args.job_id)
    else:
        directory = job_dir(profile, args.job_id)
        path = directory / 'job.json'
        if args.operation == '_finalize':
            data = json.loads(path.read_text())
            if data['status'] == 'running':
                data.update(status='interrupted', finished_at=now(), service_result=os.environ.get('SERVICE_RESULT'))
                save(path, data)
        elif args.operation == 'cancel':
            data = json.loads(path.read_text())
            if data['status'] in ['queued', 'running', 'interrupted']:
                (directory / 'cancel_requested').touch(mode=0o600)
                subprocess.run(['sudo', '-n', 'systemctl', 'stop', unit(profile, args.job_id)], check=True)
                data = json.loads(path.read_text())
                data.update(status='cancelled', finished_at=now())
                save(path, data)
            subprocess.run(['sudo', '-n', 'systemctl', 'disable', unit(profile, args.job_id)], check=True, capture_output=True)
            print(json.dumps(data))
        elif args.operation == 'status':
            print(path.read_text(), end='')
        elif args.operation == 'logs':
            log = directory / 'output.log'
            offset = max(args.offset, 0)
            with log.open('rb') if log.exists() else open(os.devnull, 'rb') as stream:
                stream.seek(offset)
                chunk = stream.read(max(1, min(args.limit, 65536)))
            print(json.dumps({'id': args.job_id, 'offset': offset, 'next_offset': offset + len(chunk), 'text': chunk.decode(errors='replace')}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(1)
