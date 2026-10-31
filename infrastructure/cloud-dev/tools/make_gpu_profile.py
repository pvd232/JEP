#!/usr/bin/env python3
"""Generate a GPU-worker profile from observed GCP inventory; make no cloud changes."""
import argparse
import copy
import json
from pathlib import Path
import re


def make_profile(base, instance, linux_user, profile_id, service_account_id):
    patterns = [(linux_user, r'[a-z_][a-z0-9_-]{0,63}'), (profile_id, r'[a-z][a-z0-9-]{0,47}'), (service_account_id, r'[a-z][a-z0-9-]{4,28}[a-z0-9]')]
    if not all(re.fullmatch(pattern, value) for value, pattern in patterns):
        raise ValueError('Supply a valid Linux user, profile id and service account id')
    name = instance.get('name', '')
    zone = instance.get('zone', '').rsplit('/', 1)[-1]
    project = base['target']['gcp_project']
    if not re.fullmatch(r'[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?', name) or not re.fullmatch(r'[a-z]+-[a-z0-9]+[0-9]-[a-z]', zone):
        raise ValueError('Instance inventory requires a valid name and zone')
    if '/projects/' + project + '/zones/' + zone + '/instances/' + name != instance.get('selfLink', '').removeprefix('https://www.googleapis.com/compute/v1'):
        raise ValueError('Instance selfLink must match the configured project, zone and name')
    if not instance.get('guestAccelerators'):
        raise ValueError('Observed instance has no GPU accelerators')
    result = copy.deepcopy(base)
    result['profile'] = profile_id
    result['connection_name'] = 'GPU worker ' + name
    result['role'] = 'gpu-worker'
    result['target'].update(vm_name=name, zone=zone, linux_user=linux_user)
    result['paths'] = {
        'workspace_root': '/home/' + linux_user + '/worktrees',
        'project_root': '/home/' + linux_user + '/cloud-projects',
        'install_root': '/opt/cloud-dev/' + profile_id,
        'state_root': '/var/lib/cloud-dev/' + profile_id,
        'config_root': '/etc/cloud-dev/' + profile_id,
    }
    result['job_identity']['service_account_id'] = service_account_id
    email = service_account_id + '@' + project + '.iam.gserviceaccount.com'
    result['job_identity']['service_account_email'] = email
    result['project']['runtime_service_account'] = email
    result.pop('resolved', None)
    for key in result['transport']:
        if key not in ['preferred', 'fallback']:
            result['transport'][key] = None
    result['project_instructions'] = 'Use the existing project runtime and checkpoints. Preserve active GPU jobs. Keep this worker stopped when it was stopped before identity provisioning.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-profile', required=True, type=Path)
    parser.add_argument('--instance-json', required=True, type=Path)
    parser.add_argument('--linux-user', required=True)
    parser.add_argument('--profile-id', required=True)
    parser.add_argument('--service-account-id', default='jep-gpu-jobs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = make_profile(json.loads(args.base_profile.read_text()), json.loads(args.instance_json.read_text()), args.linux_user, args.profile_id, args.service_account_id)
    content = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
