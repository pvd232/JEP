#!/usr/bin/python3
"""Finish tunnel activation using a real ID and a securely entered runtime key."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--config', type=Path, required=True)
parser.add_argument('--tunnel-id', required=True)
args = parser.parse_args()
if not re.fullmatch(r'tunnel_[A-Za-z0-9_-]+', args.tunnel_id):
    raise SystemExit('Supply the real tunnel ID from OpenAI Platform')
profile = json.loads(args.config.read_text())
config_root = Path(profile['paths']['config_root'])
state_root = Path(profile['paths']['state_root'])
key_file = config_root / 'runtime.key'
if not key_file.exists():
    key = getpass.getpass('Restricted OpenAI runtime key (hidden input): ').strip()
    if not key or '\n' in key:
        raise SystemExit('A single runtime key is required')
    descriptor = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(key)
existing_id = profile['transport'].get('tunnel_id')
if existing_id and existing_id != args.tunnel_id:
    raise SystemExit('A different tunnel is already configured; review the association before changing it')
profile['transport']['tunnel_id'] = args.tunnel_id
profile['transport']['selected'] = 'secure_tunnel'
args.config.write_text(json.dumps(profile, indent=2) + '\n')
os.chmod(args.config, 0o600)
profile_yaml = state_root / 'tunnel' / (profile['profile'] + '.yaml')
if not profile_yaml.exists():
 subprocess.run([
    profile['resolved']['tunnel_client'], 'init', '--profile', profile['profile'],
    '--profile-dir', str(state_root / 'tunnel'), '--tunnel-id', args.tunnel_id,
    '--mcp-command', str(Path(profile['paths']['install_root']) / 'bin/cloud-mcp'),
    '--control-plane-api-key-ref', 'file:' + str(key_file), '--health-listen-addr', '127.0.0.1:0',
 ], check=True)
service = 'cloud-dev-' + profile['profile'] + '-tunnel.service'
subprocess.run(['sudo', '-n', 'systemctl', 'start', service], check=True)
print('Tunnel service started. Verify readiness, workspace association, and an actual ChatGPT tool call before declaring completion.')
