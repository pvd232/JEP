#!/usr/bin/env python3
"""Create project environments and run jobs through the shared VM toolchain."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
from preflight import collect, load_profile


def write(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.exists() or path.read_text() != content:
        path.write_text(content)
    path.chmod(mode)


def project_profile(host, definition):
    name = definition.get('id', '')
    if definition.get('schema_version') != 1 or not re.fullmatch(r'[a-z][a-z0-9-]{0,30}', name):
        raise ValueError('Project requires schema_version=1 and a short lowercase id')
    if not re.fullmatch(r'https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git', definition.get('repository_url', '')):
        raise ValueError('Use a GitHub HTTPS repository URL without credentials')
    if not re.fullmatch(r'[a-f0-9]{40}', definition.get('repository_revision', '')):
        raise ValueError('Pin repository_revision to a full commit SHA')
    python = definition.get('python_executable', '/usr/bin/python3')
    if not Path(python).is_absolute() or '..' in Path(python).parts:
        raise ValueError('python_executable must be an absolute path')
    if not isinstance(definition.get('cpu_quota_percent'), int) or not 1 <= definition['cpu_quota_percent'] <= 10000:
        raise ValueError('cpu_quota_percent must be between 1 and 10000')
    memory = definition.get('memory_max_mib')
    if memory is not None and (not isinstance(memory, int) or memory < 256):
        raise ValueError('memory_max_mib must be null or at least 256')
    profile = copy.deepcopy(host)
    workspace = Path(host['paths']['workspace_root']) / name
    runtime = Path(host['paths']['project_root']) / name
    config = Path(host['paths']['config_root']) / 'projects' / name
    state = Path(host['paths']['state_root']) / 'projects' / name
    profile['profile'] = host['profile'] + '-' + name
    profile['project_id'] = name
    profile['paths'].update(workspace_root=str(workspace), state_root=str(state), config_root=str(config))
    profile['project_definition'] = copy.deepcopy(definition)
    profile.setdefault('resolved', {})['project_environment'] = {
        'VIRTUAL_ENV': str(runtime / 'venv'),
        'CLOUDSDK_CONFIG': str(config / 'gcloud'),
        'GOOGLE_APPLICATION_CREDENTIALS': str(config / 'gcloud' / 'application_default_credentials.json'),
        'XDG_CACHE_HOME': str(runtime / 'cache'),
        'HF_HOME': str(runtime / 'cache' / 'huggingface'),
        'UV_CACHE_DIR': str(runtime / 'cache' / 'uv'),
        'PIP_CACHE_DIR': str(runtime / 'cache' / 'pip'),
        'CLOUD_PROJECT_ID': name,
        'CLOUD_PROJECT_DATA': str(runtime / 'data'),
        'CLOUD_DEV_CONFIG': str(config / 'profile.json'),
    }
    profile['resolved']['project_runtime'] = str(runtime)
    return profile


def project_environment(profile):
    environment = os.environ.copy()
    # Do not inherit common account-level credentials into a project process.
    for key in ['GOOGLE_OAUTH_ACCESS_TOKEN', 'CLOUDSDK_AUTH_ACCESS_TOKEN', 'CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE']:
        environment.pop(key, None)
    environment.update(profile['resolved']['project_environment'])
    environment['PATH'] = ':'.join([
        str(Path(environment['VIRTUAL_ENV']) / 'bin'),
        profile['resolved']['node_bin_dir'], profile['resolved']['bin_dir'],
        environment.get('PATH', '/usr/bin:/bin'),
    ])
    return environment


def memory_limit(definition, meminfo):
    available = meminfo['MemAvailable'] // 1024
    headroom = max(1024, meminfo['MemTotal'] // 1024 // 5)
    budget = available - headroom
    requested = definition.get('memory_max_mib')
    limit = requested if requested is not None else min(4096, budget // 2)
    if limit < 512 or limit > budget:
        raise ValueError('Insufficient available RAM for this project plus host headroom')
    return limit


def setup(host, definition):
    identity = collect(host)
    if not identity['target_verified']:
        raise RuntimeError('VM identity mismatch: ' + json.dumps(identity['identity_mismatches']))
    if not host.get('resolved'):
        raise RuntimeError('Install the host toolchain before project setup')
    profile = project_profile(host, definition)
    root = Path(host['paths']['project_root'])
    ancestor = root
    while not ancestor.exists():
        ancestor = ancestor.parent
    if shutil.disk_usage(ancestor).free < 8 * 1024**3:
        raise RuntimeError('Project setup requires at least 8 GiB free disk')
    meminfo = {line.split(':')[0]: int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if len(line.split()) >= 2}
    profile['project_definition']['memory_max_mib'] = memory_limit(definition, meminfo)
    runtime = Path(profile['resolved']['project_runtime'])
    workspace = Path(profile['paths']['workspace_root'])
    config = Path(profile['paths']['config_root'])
    state = Path(profile['paths']['state_root'])
    existing = config / 'profile.json'
    previous_config = existing.read_text() if existing.exists() else None
    if existing.exists():
        prior = json.loads(existing.read_text())
        # Preserve the recorded cap on idempotent applies, subject to current headroom.
        if definition.get('memory_max_mib') is None:
            profile['project_definition']['memory_max_mib'] = memory_limit(prior['project_definition'], meminfo)
    if workspace.exists():
        origin = subprocess.check_output(['git', '-C', str(workspace), 'remote', 'get-url', 'origin'], text=True).strip()
        if origin != definition['repository_url']:
            raise RuntimeError('Existing workspace has another origin; choose a new project id')
    for directory in [runtime, runtime / 'data', runtime / 'cache', config, config / 'gcloud', state, state / 'jobs', state / 'receipts']:
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    changed = not workspace.exists()
    if not workspace.exists():
        subprocess.run(['git', 'clone', '--no-checkout', definition['repository_url'], str(workspace)], check=True)
        subprocess.run(['git', '-C', str(workspace), 'checkout', '--detach', definition['repository_revision']], check=True)
    if not (runtime / 'venv' / 'bin' / 'python').exists():
        changed = True
        subprocess.run([definition['python_executable'], '-m', 'venv', str(runtime / 'venv')], check=True)
    config_file = config / 'profile.json'
    rendered_config = json.dumps(profile, indent=2) + '\n'
    changed = changed or rendered_config != previous_config
    write(config_file, rendered_config)
    # Explicit ADC path deliberately fails until project credentials are provisioned.
    # gcloud CLI credentials are separately stored under this project's gcloud/.
    job_name = 'cloud-dev-' + profile['profile'] + '-job@.service'
    template = (Path(host['paths']['state_root']) / ('cloud-dev-' + host['profile'] + '-job@.service')).read_text()
    template = template.replace(str(Path(host['paths']['config_root']) / 'profile.json'), str(config_file))
    limits = profile['project_definition']
    slice_name = 'cloud-dev-' + profile['profile'] + '.slice'
    template = template.replace('[Service]\n', '[Service]\nSlice=' + slice_name + '\n')
    unit_source = state / job_name
    write(unit_source, template)
    slice_source = state / slice_name
    write(slice_source, '[Unit]\nDescription=Shared project job limits\n\n[Slice]\nCPUQuota=' + str(limits['cpu_quota_percent']) + '%\nMemoryMax=' + str(limits['memory_max_mib']) + 'M\n')
    units_changed = False
    for source in [unit_source, slice_source]:
        destination = '/etc/systemd/system/' + source.name
        if subprocess.run(['sudo', '-n', 'cmp', '-s', str(source), destination]).returncode:
            changed = units_changed = True
            subprocess.run(['sudo', '-n', 'install', '-m', '0644', str(source), destination], check=True)
    if units_changed:
        subprocess.run(['sudo', '-n', 'systemctl', 'daemon-reload'], check=True)
    print(json.dumps({'project': definition['id'], 'changed': changed, 'workspace': str(workspace), 'state': str(state), 'memory_max_mib': limits['memory_max_mib'], 'credentials': 'project login required; no credentials copied'}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-profile', type=Path, default=os.environ.get('CLOUD_DEV_CONFIG'))
    parser.add_argument('--project')
    operations = parser.add_subparsers(dest='operation', required=True)
    for operation in ['plan', 'setup']:
        operations.add_parser(operation).add_argument('--definition', required=True, type=Path)
    for operation in ['run', 'submit', 'status', 'logs', 'cancel', 'list']:
        operations.add_parser(operation, add_help=False).add_argument('arguments', nargs=argparse.REMAINDER)
    args, unknown = parser.parse_known_args()
    if not args.host_profile:
        parser.error('--host-profile or CLOUD_DEV_CONFIG is required')
    if args.operation in ['plan', 'setup'] and unknown:
        parser.error('Unknown arguments: ' + ' '.join(unknown))
    host = load_profile(args.host_profile)
    if args.operation in ['plan', 'setup']:
        definition = json.loads(args.definition.read_text())
        profile = project_profile(host, definition)
        if args.operation == 'plan':
            print(json.dumps(profile, indent=2))
        else:
            setup(host, definition)
        return 0
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,30}', args.project or ''):
        parser.error('--project ID is required')
    config = Path(host['paths']['config_root']) / 'projects' / args.project / 'profile.json'
    profile = json.loads(config.read_text())
    argv = unknown + args.arguments
    if argv[:1] == ['--']:
        argv = argv[1:]
    if args.operation == 'run':
        if not argv:
            parser.error('run requires a command after --')
        os.chdir(profile['paths']['workspace_root'])
        os.execvpe(argv[0], argv, project_environment(profile))
    controller = Path(host['paths']['install_root']) / 'bin' / 'cloud_job.py'
    os.execvpe('/usr/bin/python3', ['/usr/bin/python3', str(controller), '--config', str(config), args.operation] + argv, project_environment(profile))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
