#!/usr/bin/env python3
"""Reach the user's Mac through a private reverse SSH port on the existing VM."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess


def key_pair(path):
    public = Path(str(path) + '.pub')
    if not path.exists():
        if public.exists():
            raise RuntimeError('Existing public key has no private counterpart; preserve it and inspect')
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', 'chatgpt-mac-relay', '-f', str(path)], check=True)
    path.chmod(0o600)
    return public.read_text().strip()


def configure(state, user, port, host_key):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]{0,63}', user):
        raise ValueError('Invalid Mac short username')
    if not 1024 <= port <= 65535:
        raise ValueError('Use an unprivileged relay port')
    if not re.fullmatch(r'ssh-ed25519 [A-Za-z0-9+/]+={0,2}', host_key):
        raise ValueError('Supply the Mac SSH server Ed25519 public host key')
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    known_hosts = state / 'known_hosts'
    known_hosts.write_text('[127.0.0.1]:' + str(port) + ' ' + host_key + '\n')
    known_hosts.chmod(0o600)
    config = state / 'config.json'
    config.write_text(json.dumps({'mac_user': user, 'port': port}, indent=2) + '\n')
    config.chmod(0o600)


def ssh_argv(state, key, arguments):
    config = json.loads((state / 'config.json').read_text())
    user, port = config['mac_user'], int(config['port'])
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]{0,63}', user) or not 1024 <= port <= 65535:
        raise ValueError('Invalid saved relay configuration')
    if not arguments:
        raise ValueError('A Mac command is required after --')
    remote = '/bin/zsh -lc ' + shlex.quote(shlex.join(arguments))
    return ['ssh', '-p', str(port), '-i', str(key), '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(state / 'known_hosts'), '--', user + '@127.0.0.1', remote]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', type=Path, default=Path('/var/lib/cloud-dev/aether/mac-relay'))
    parser.add_argument('--key-file', type=Path, default=Path.home() / '.ssh/chatgpt_mac_relay_ed25519')
    subcommands = parser.add_subparsers(dest='operation', required=True)
    subcommands.add_parser('public-key')
    setup = subcommands.add_parser('configure')
    setup.add_argument('--mac-user', required=True)
    setup.add_argument('--port', type=int, default=22022)
    setup.add_argument('--host-key', required=True)
    subcommands.add_parser('run').add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.operation == 'public-key':
        print(key_pair(args.key_file))
    elif args.operation == 'configure':
        configure(args.state_root, args.mac_user, args.port, args.host_key)
        print('Mac relay identity configured; awaiting the outbound Mac tunnel')
    else:
        arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
        command = ssh_argv(args.state_root, args.key_file, arguments)
        os.execvp(command[0], command)


if __name__ == '__main__':
    main()
