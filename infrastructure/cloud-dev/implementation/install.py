#!/usr/bin/python3
"""Install isolated runtime and pinned terminal binaries on the configured GCP VM."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import pwd
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
import shlex


def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'cloud-dev-setup'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, **kwargs)


def write(path, data, mode=0o600):
    content = data if isinstance(data, bytes) else data.encode()
    if path.exists() and path.read_bytes() == content:
        path.chmod(mode)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(mode)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('--lock', type=Path, help='Shared tested toolchain lock for a new VM')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    sys.path.insert(0, str(source.parent / 'tools'))
    from preflight import load_profile
    profile = load_profile(args.profile)
    target = profile['target']
    if platform.machine() != 'x86_64':
        raise RuntimeError('This tested toolchain targets x86_64; select and verify artifacts for the target architecture first')
    for key, route in [('gcp_project', 'project/project-id'), ('vm_name', 'instance/name'), ('zone', 'instance/zone')]:
        request = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/' + route, headers={'Metadata-Flavor': 'Google'})
        observed = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=3).read().decode().rsplit('/', 1)[-1]
        if observed != target[key]:
            raise RuntimeError('Target identity mismatch: ' + key)
    identity = profile.get('job_identity', {})
    if identity.get('mode') == 'attached_service_account':
        for route, expected in [('email', identity['service_account_email']), ('scopes', identity['oauth_scopes'])]:
            request = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/' + route, headers={'Metadata-Flavor': 'Google'})
            observed = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=3).read().decode().strip()
            if (observed != expected if route == 'email' else set(observed.splitlines()) != set(expected)):
                raise RuntimeError('Provision the configured keyless VM job identity before installing host tooling')
    user = pwd.getpwnam(target['linux_user'])
    if os.getuid() != user.pw_uid:
        raise RuntimeError('Run as configured development user')
    os_release = Path('/etc/os-release').read_text()
    if 'ID=ubuntu' not in os_release or 'VERSION_ID="24.04"' not in os_release or sys.version_info < (3, 12):
        raise RuntimeError('This toolchain requires Ubuntu 24.04 and Python 3.12 or later')
    for value in profile['paths'].values():
        ancestor = Path(value)
        while not ancestor.exists():
            ancestor = ancestor.parent
        if shutil.disk_usage(ancestor).free < 8 * 1024**3:
            raise RuntimeError('At least 8 GiB free disk is required before setup')
    install = Path(profile['paths']['install_root'])
    state = Path(profile['paths']['state_root'])
    config = Path(profile['paths']['config_root'])
    managed = [config / 'profile.json', install / 'toolchain.lock.json'] + [install / 'bin' / name for name in ['cloud_job.py', 'mcp_stdio.py', 'activate.py', 'project.py', 'preflight.py', 'probe_mcp.py', 'probe_identity.py', 'mac_relay.py', 'cloud-job', 'cloud-mcp', 'cloud-project', 'mac-command']]
    before = {str(p): p.read_bytes() if p.exists() else None for p in managed}
    for directory in [install, state, config]:
        run(['sudo', '-n', 'install', '-d', '-m', '0700', '-o', user.pw_name, '-g', str(user.pw_gid), str(directory)])
    for key in ['workspace_root', 'project_root']:
        Path(profile['paths'][key]).mkdir(mode=0o700, parents=True, exist_ok=True)
    for directory in [state / 'jobs', state / 'receipts', state / 'tunnel', install / 'bin', install / 'releases']:
        directory.mkdir(mode=0o700, exist_ok=True)
    lock_path = install / 'toolchain.lock.json'
    shared_lock = args.lock or source.parent / 'toolchain.lock.json'
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else (json.loads(shared_lock.read_text()) if shared_lock.exists() else {})
    if not lock:
        raise RuntimeError('A tested toolchain lock is required')
    node_dir = install / 'releases' / ('node-' + lock['node_version'] + '-linux-x64')
    if not node_dir.exists():
        filename = node_dir.name + '.tar.xz'
        base = 'https://nodejs.org/dist/' + lock['node_version'] + '/'
        checksums = download(base + 'SHASUMS256.txt').decode()
        expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1] == filename)
        if expected != lock.get('node_archive_sha256'):
            raise RuntimeError('Node archive differs from the tested toolchain lock')
        content = download(base + filename)
        if hashlib.sha256(content).hexdigest() != expected:
            raise RuntimeError('Node archive checksum mismatch')
        with tarfile.open(fileobj=io.BytesIO(content), mode='r:xz') as archive:
            archive.extractall(install / 'releases', filter='data')
        lock['node_archive_sha256'] = expected
    node = node_dir / 'bin/node'
    node_digest = hashlib.sha256(node.read_bytes()).hexdigest()
    if lock.get('node_binary_sha256') and lock['node_binary_sha256'] != node_digest:
        raise RuntimeError('Pinned Node binary checksum mismatch')
    lock['node_binary_sha256'] = node_digest
    npm = node_dir / 'bin/npm'
    environment = os.environ.copy()
    environment['PATH'] = str(node_dir / 'bin') + ':' + environment.get('PATH', '/usr/bin:/bin')
    package_dir = install / 'releases' / ('desktop-commander-' + lock['desktop_commander_version'])
    if not (package_dir / 'node_modules/@wonderwhy-er/desktop-commander/dist/index.js').exists():
        package_dir.mkdir(exist_ok=True)
        write(package_dir / 'package.json', json.dumps({'private': True, 'dependencies': {'@wonderwhy-er/desktop-commander': lock['desktop_commander_version']}}, indent=2))
        shared_npm_lock = source.parent / 'desktop-commander.package-lock.json'
        if shared_npm_lock.exists():
            write(package_dir / 'package-lock.json', shared_npm_lock.read_bytes())
            run([str(npm), 'ci', '--omit=dev', '--no-audit', '--no-fund'], cwd=package_dir, env=environment)
        else:
            raise RuntimeError('The tested complete npm lockfile is required')
    package_lock = json.loads((package_dir / 'package-lock.json').read_text())
    lock['desktop_commander_integrity'] = package_lock['packages']['node_modules/@wonderwhy-er/desktop-commander']['integrity']
    package_digest = hashlib.sha256((package_dir / 'package-lock.json').read_bytes()).hexdigest()
    if lock.get('package_lock_sha256') and lock['package_lock_sha256'] != package_digest:
        raise RuntimeError('Pinned npm lockfile checksum mismatch')
    lock['package_lock_sha256'] = package_digest
    tunnel_dir = install / 'releases' / ('tunnel-client-' + lock['tunnel_client_version'])
    tunnel = tunnel_dir / 'tunnel-client'
    if not tunnel.exists():
        tunnel_dir.mkdir(exist_ok=True)
        base = 'https://github.com/openai/tunnel-client/releases/download/' + lock['tunnel_client_version'] + '/'
        checksums = download(base + 'SHA256SUMS.txt').decode()
        filename = 'tunnel-client-' + lock['tunnel_client_version'] + '-linux-amd64.zip'
        expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1].lstrip('*') == filename)
        if expected != lock.get('tunnel_archive_sha256'):
            raise RuntimeError('Tunnel archive differs from the tested toolchain lock')
        content = download(base + filename)
        if hashlib.sha256(content).hexdigest() != expected:
            raise RuntimeError('Tunnel archive checksum mismatch')
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for name in archive.namelist():
                if Path(name).name == 'tunnel-client':
                    write(tunnel, archive.read(name), 0o700)
        if not tunnel.exists():
            raise RuntimeError('Tunnel client executable missing from official archive')
        lock['tunnel_archive_sha256'] = expected
    tunnel_digest = hashlib.sha256(tunnel.read_bytes()).hexdigest()
    if lock.get('tunnel_binary_sha256') and lock['tunnel_binary_sha256'] != tunnel_digest:
        raise RuntimeError('Pinned tunnel binary checksum mismatch')
    lock['tunnel_binary_sha256'] = tunnel_digest
    profile['resolved'] = {'node': str(node), 'node_bin_dir': str(node_dir / 'bin'), 'desktop_commander_entry': str(package_dir / 'node_modules/@wonderwhy-er/desktop-commander/dist/index.js'), 'tunnel_client': str(tunnel), 'linux_home': user.pw_dir, 'bin_dir': str(install / 'bin')}
    existing_profile_path = config / 'profile.json'
    if existing_profile_path.exists():
        existing = json.loads(existing_profile_path.read_text())
        for key, value in existing.get('transport', {}).items():
            if profile['transport'].get(key) is None and value is not None:
                profile['transport'][key] = value
    write(config / 'profile.json', json.dumps(profile, indent=2) + '\n')
    write(lock_path, json.dumps(lock, indent=2) + '\n')
    for filename in ['cloud_job.py', 'mcp_stdio.py', 'activate.py', 'project.py', 'probe_mcp.py', 'probe_identity.py']:
        write(install / 'bin' / filename, (source / filename).read_bytes(), 0o700)
    write(install / 'bin/preflight.py', (source.parent / 'tools/preflight.py').read_bytes(), 0o700)
    write(install / 'bin/mac_relay.py', (source.parent / 'tools/mac_relay.py').read_bytes(), 0o700)
    write(install / 'bin/mac-command', '#!/bin/sh\nexec /usr/bin/python3 ' + shlex.quote(str(install / 'bin/mac_relay.py')) + ' --state-root ' + shlex.quote(str(state / 'mac-relay')) + ' run -- "$@"\n', 0o700)
    for name, script in [('cloud-job', 'cloud_job.py'), ('cloud-mcp', 'mcp_stdio.py'), ('cloud-project', 'project.py')]:
        write(install / 'bin' / name, '#!/bin/sh\nexport CLOUD_DEV_CONFIG=' + shlex.quote(str(config / 'profile.json')) + '\nexec /usr/bin/python3 ' + shlex.quote(str(install / 'bin' / script)) + ' "$@"\n', 0o700)
    template = ('[Unit]\nDescription=Cloud development durable job %i\nAfter=network-online.target\nWants=network-online.target\n\n[Service]\nType=oneshot\nUser=' + user.pw_name + '\nGroup=' + str(user.pw_gid) + '\nEnvironment=CLOUD_DEV_CONFIG=' + str(config / 'profile.json') + '\nUMask=0077\nExecStart=/usr/bin/python3 ' + str(install / 'bin/cloud_job.py') + ' _run %i\nExecStopPost=/usr/bin/python3 ' + str(install / 'bin/cloud_job.py') + ' _finalize %i\nTimeoutStartSec=infinity\nTimeoutStopSec=15\nKillMode=control-group\nRemainAfterExit=yes\n\n[Install]\nWantedBy=multi-user.target\n')
    unit_path = state / ('cloud-dev-' + profile['profile'] + '-job@.service')
    changed = write(unit_path, template)
    destination = '/etc/systemd/system/' + unit_path.name
    current = subprocess.run(['sudo', '-n', 'cmp', '-s', str(unit_path), destination])
    if current.returncode:
        run(['sudo', '-n', 'install', '-m', '0644', str(unit_path), destination])
        changed = True
    tunnel_unit = ('[Unit]\nDescription=' + profile['connection_name'] + ' Secure MCP Tunnel\nAfter=network-online.target\nWants=network-online.target\nConditionPathExists=' + str(state / 'tunnel' / (profile['profile'] + '.yaml')) + '\nConditionPathExists=' + str(config / 'runtime.key') + '\nStartLimitIntervalSec=0\n\n[Service]\nType=simple\nUser=' + user.pw_name + '\nGroup=' + str(user.pw_gid) + '\nWorkingDirectory=' + user.pw_dir + '\nEnvironment=CLOUD_DEV_CONFIG=' + str(config / 'profile.json') + '\nUMask=0077\nExecStart=' + str(tunnel) + ' run --profile ' + profile['profile'] + ' --profile-dir ' + str(state / 'tunnel') + ' --health.url-file ' + str(state / 'tunnel/health-url') + ' --mcp.stdio-send-initialized-notification\nRestart=always\nRestartSec=15s\nTimeoutStopSec=20\nKillMode=control-group\nStandardOutput=journal\nStandardError=journal\n\n[Install]\nWantedBy=multi-user.target\n')
    tunnel_unit_path = state / ('cloud-dev-' + profile['profile'] + '-tunnel.service')
    write(tunnel_unit_path, tunnel_unit)
    tunnel_destination = '/etc/systemd/system/' + tunnel_unit_path.name
    if subprocess.run(['sudo', '-n', 'cmp', '-s', str(tunnel_unit_path), tunnel_destination]).returncode:
        run(['sudo', '-n', 'install', '-m', '0644', str(tunnel_unit_path), tunnel_destination])
        changed = True
    if changed:
        run(['sudo', '-n', 'systemctl', 'daemon-reload'])
    run(['sudo', '-n', 'systemctl', 'enable', tunnel_unit_path.name], capture_output=True)
    status = 'configured; client verification required' if profile['transport'].get('tunnel_id') else 'awaiting_tunnel_registration_and_runtime_key'
    write(state / 'receipts/install.json', json.dumps({'target': target, 'lock': lock, 'paths': profile['paths'], 'connection_status': status}, indent=2))
    print(json.dumps({'installed': True, 'profile': str(config / 'profile.json'), 'lock': lock, 'tunnel_binary': str(tunnel)}, indent=2))
    changed = changed or any((p.read_bytes() if p.exists() else None) != before[str(p)] for p in managed)
    print('CLOUD_DEV_CHANGED=' + ('1' if changed else '0'))


if __name__ == '__main__':
    main()
