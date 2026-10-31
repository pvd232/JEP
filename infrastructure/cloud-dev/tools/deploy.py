#!/usr/bin/env python3
"""Deploy the reviewed bundle through an explicit GCP/IAP route."""
import argparse
import datetime
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile
import tempfile

from preflight import load_profile, ssh_arguments


def cloud(profile, *arguments):
    target = profile['target']
    return ['gcloud', *arguments, '--account=' + target['gcp_account'], '--project=' + target['gcp_project']]


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, text=True, **kwargs)


def inspect_instance(profile):
    target = profile['target']
    result = run(cloud(profile, 'compute', 'instances', 'describe', target['vm_name'], '--zone=' + target['zone'], '--format=json(name,status,disks)'), capture_output=True)
    instance = json.loads(result.stdout)
    if instance['name'] != target['vm_name'] or instance['status'] != 'RUNNING':
        raise RuntimeError('Configured VM must be running; deployment does not start or reboot it')
    return instance


def snapshots(profile, instance):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')
    receipts = []
    for index, disk in enumerate(instance['disks']):
        if not disk.get('source'):
            continue
        source = disk['source'].split('/')
        if 'zones' not in source:
            raise RuntimeError('This backup helper supports zonal persistent disks')
        disk_zone = source[source.index('zones') + 1]
        name = profile['profile'] + '-dev-backup-' + timestamp + '-' + str(index)
        run(cloud(profile, 'compute', 'snapshots', 'create', name, '--source-disk=' + source[-1], '--source-disk-zone=' + disk_zone, '--quiet'))
        receipts.append({'snapshot': name, 'source_disk': disk['source'], 'boot': disk.get('boot', False)})
    if not receipts:
        raise RuntimeError('No persistent disks were found for recovery')
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('operation', choices=['plan', 'inventory', 'apply', 'backup', 'verify'])
    parser.add_argument('--project-definition', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    host = load_profile(args.profile)
    if args.operation == 'apply':
        if not args.project_definition:
            parser.error('apply requires --project-definition')
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'implementation'))
        from project import project_profile
        project_profile(host, json.loads(args.project_definition.read_text()))
    base = Path(__file__).resolve().parent.parent
    target = host['target']
    if args.operation == 'plan':
        print(json.dumps({'target': target, 'paths': host['paths'], 'sequence': ['verify live metadata and capacity', 'snapshot attached persistent disks', 'copy reviewed source bundle over IAP', 'install pinned host tooling', 'create specified project environment', 'register its own tunnel and runtime key', 'verify, then take a recovery snapshot'], 'deployed': False}, indent=2))
        return
    if args.operation == 'inventory':
        run([sys.executable, str(base / 'tools/preflight.py'), '--profile', str(args.profile), '--remote'] + (['--output', str(args.receipt)] if args.receipt else []))
        return
    instance = inspect_instance(host)
    if args.operation == 'verify':
        command = 'CLOUD_DEV_CONFIG=' + shlex.quote(host['paths']['config_root'] + '/profile.json') + ' /usr/bin/python3 ' + shlex.quote(host['paths']['install_root'] + '/bin/probe_mcp.py')
        run(ssh_arguments(host) + ['--command', command])
        return
    if args.operation == 'apply':
        # Metadata checks happen before snapshots and before guest filesystem writes.
        run([sys.executable, str(base / 'tools/preflight.py'), '--profile', str(args.profile), '--remote'])
    receipt = {'profile': host['profile'], 'target': target, 'snapshots': snapshots(host, instance), 'consistency': 'GCP crash-consistent persistent-disk snapshots; restore test pending'}
    destination = args.receipt or (base / 'receipts' / (host['profile'] + '-backup.json'))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2) + '\n')
    if args.operation == 'backup':
        print(json.dumps(receipt, indent=2))
        return
    # The archive contains source, locks and public configuration only.
    with tempfile.TemporaryDirectory(prefix='cloud-dev-source-') as temporary:
        bundle = Path(temporary) / 'setup.tar.gz'
        with tarfile.open(bundle, 'w:gz') as archive:
            for directory in ['implementation', 'tools']:
                for path in sorted((base / directory).rglob('*')):
                    if path.is_file() and '__pycache__' not in path.parts:
                        archive.add(path, arcname=path.relative_to(base))
            archive.add(args.profile, arcname='profiles/host.json')
            archive.add(args.project_definition, arcname='projects/project.json')
            for filename in ['toolchain.lock.json', 'desktop-commander.package-lock.json']:
                archive.add(base / filename, arcname=filename)
        remote = '/home/' + target['linux_user'] + '/cloud-dev-' + host['profile'] + '-setup.tar.gz'
        scp = cloud(host, 'compute', 'scp', str(bundle), target['linux_user'] + '@' + target['vm_name'] + ':' + remote, '--zone=' + target['zone'])
        if target['ssh_via_iap']:
            scp.append('--tunnel-through-iap')
        run(scp)
    source = '/home/' + target['linux_user'] + '/cloud-dev-setup/' + host['profile']
    q = shlex.quote
    command = '\n'.join([
        'set -eu',
        'mkdir -p ' + q(source),
        'tar -xzf ' + q(remote) + ' -C ' + q(source),
        '/usr/bin/python3 ' + q(source + '/implementation/install.py') + ' --profile ' + q(source + '/profiles/host.json') + ' --lock ' + q(source + '/toolchain.lock.json'),
        '/usr/bin/python3 ' + q(host['paths']['install_root'] + '/bin/project.py') + ' --host-profile ' + q(host['paths']['config_root'] + '/profile.json') + ' setup --definition ' + q(source + '/projects/project.json'),
    ])
    run(ssh_arguments(host) + ['--command', command])
    print('Host and project installed. Tunnel activation and client acceptance remain.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
