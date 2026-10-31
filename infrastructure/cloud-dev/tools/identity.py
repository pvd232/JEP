#!/usr/bin/env python3
"""Provision a dedicated keyless VM identity using scoped, declared IAM grants."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

from preflight import load_profile, ssh_arguments
from deploy import cloud, run, snapshots


def plan(profile):
    identity = profile['job_identity']
    account = identity['service_account_email']
    member = 'serviceAccount:' + account
    commands = [cloud(profile, 'iam', 'service-accounts', 'create', identity['service_account_id'], '--display-name=Cloud workload jobs')]
    for binding in identity['iam_bindings']:
        if binding['scope'] == 'project':
            argv = cloud(profile, 'projects', 'add-iam-policy-binding', binding['resource'])
        else:
            argv = cloud(profile, 'storage', 'buckets', 'add-iam-policy-binding', 'gs://' + binding['resource'])
        commands.append(argv + ['--member=' + member, '--role=' + binding['role'], '--condition=None', '--quiet'])
    target = profile['target']
    for operation in ['stop', 'set-service-account', 'start']:
        argv = cloud(profile, 'compute', 'instances', operation, target['vm_name'], '--zone=' + target['zone'], '--quiet')
        if operation == 'set-service-account':
            argv += ['--service-account=' + account, '--scopes=cloud-platform']
        commands.append(argv)
    return {'service_account': account, 'oauth_scopes': identity['oauth_scopes'], 'iam_bindings': identity['iam_bindings'], 'private_key_files': False, 'restart_policy': 'running idle VM only when attachment/scopes differ; snapshot and check durable/GPU jobs first; preserve an already stopped VM', 'commands': [shlex.join(argv) for argv in commands]}


def matches(instance, identity):
    accounts = instance.get('serviceAccounts', [])
    return len(accounts) == 1 and accounts[0].get('email') == identity['service_account_email'] and set(accounts[0].get('scopes', [])) == set(identity['oauth_scopes'])


def active_jobs_command(profile):
    # Read status only. Do not print command arguments or credential values.
    source = "\n".join([
        'import json,shutil,subprocess', 'from pathlib import Path',
        'root=Path(' + repr(profile['paths']['state_root']) + ')',
        'active=[]',
        "for path in root.rglob('job.json'):",
        ' try:',
        '  data=json.loads(path.read_text())',
        "  if data.get('status') in ['queued','running']: active.append({'id':data.get('id'),'status':data['status']})",
        ' except (OSError,ValueError): raise RuntimeError("Unreadable job record; inspect before restarting")',
        "if shutil.which('nvidia-smi'):",
        " result=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],check=True,capture_output=True,text=True,timeout=10)",
        " for line in result.stdout.splitlines():",
        "  if line.strip(): active.append({'gpu_pid':int(line.strip()),'status':'gpu-active'})",
        'print(json.dumps(active))',
    ])
    return 'python3 -c ' + shlex.quote(source)


def apply(profile, allow_restart, receipt_path):
    # Use the administrator identity for initial setup. Job IAM grants cannot
    # create service accounts, assign roles, or alter VM identity.
    target = profile['target']
    identity = profile['job_identity']
    description = cloud(profile, 'compute', 'instances', 'describe', target['vm_name'], '--zone=' + target['zone'], '--format=json(name,status,disks,serviceAccounts)')
    instance = json.loads(run(description, capture_output=True).stdout)
    needs_change = not matches(instance, identity)
    was_running = instance.get('status') == 'RUNNING'
    needs_restart = needs_change and was_running
    if instance.get('status') not in ['RUNNING', 'TERMINATED']:
        raise RuntimeError('Wait for the configured VM to reach RUNNING or TERMINATED before identity setup')
    if needs_restart:
        if not allow_restart:
            raise RuntimeError('Attachment changes require a controlled stop/start. Review plan and run with --allow-restart after inspecting active work')
        active = json.loads(run(ssh_arguments(profile) + ['--command', active_jobs_command(profile)], capture_output=True).stdout)
        if active:
            raise RuntimeError('Active durable jobs must finish or checkpoint before VM restart: ' + json.dumps(active))
    receipt = {'target': target, 'requested': identity, 'previous_status': instance['status'], 'previous_service_accounts': instance.get('serviceAccounts', []), 'snapshots': [], 'changed_attachment': needs_change, 'restarted': needs_restart}
    if needs_change:
        receipt['snapshots'] = snapshots(profile, instance)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    email = identity['service_account_email']
    found = subprocess.run(cloud(profile, 'iam', 'service-accounts', 'describe', email, '--format=json'), text=True, capture_output=True)
    if found.returncode:
        if 'NOT_FOUND' not in found.stderr and 'does not exist' not in found.stderr:
            raise RuntimeError('Could not inspect service account: ' + found.stderr[-2000:])
        run(cloud(profile, 'iam', 'service-accounts', 'create', identity['service_account_id'], '--display-name=Development background jobs'))
    elif json.loads(found.stdout).get('disabled'):
        raise RuntimeError('Configured job service account is disabled')
    member = 'serviceAccount:' + email
    for binding in identity['iam_bindings']:
        if binding['scope'] == 'project':
            prefix = cloud(profile, 'projects')
            resource = binding['resource']
        else:
            prefix = cloud(profile, 'storage', 'buckets')
            resource = 'gs://' + binding['resource']
        policy = json.loads(run(prefix + ['get-iam-policy', resource, '--format=json'], capture_output=True).stdout)
        present = any(item.get('role') == binding['role'] and member in item.get('members', []) and not item.get('condition') for item in policy.get('bindings', []))
        if not present:
            run(prefix + ['add-iam-policy-binding', resource, '--member=' + member, '--role=' + binding['role'], '--condition=None', '--quiet'])
    if needs_restart:
        # Recheck durable jobs immediately before stopping the development host.
        active = json.loads(run(ssh_arguments(profile) + ['--command', active_jobs_command(profile)], capture_output=True).stdout)
        if active:
            raise RuntimeError('A job started during setup; VM restart deferred')
    common = ['--zone=' + target['zone'], '--quiet']
    if needs_change:
        if was_running:
            run(cloud(profile, 'compute', 'instances', 'stop', target['vm_name'], *common))
        try:
            run(cloud(profile, 'compute', 'instances', 'set-service-account', target['vm_name'], *common, '--service-account=' + email, '--scopes=cloud-platform'))
        finally:
            # Restore host availability even if the attachment operation fails.
            if was_running:
                run(cloud(profile, 'compute', 'instances', 'start', target['vm_name'], *common))
    current = json.loads(run(description, capture_output=True).stdout)
    if not matches(current, identity):
        raise RuntimeError('Post-change identity or access scopes do not match the profile')
    receipt['attachment_verified'] = True
    receipt['token_and_api_verification'] = 'pending probe_identity.py on the VM'
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('operation', choices=['plan', 'apply'])
    parser.add_argument('--allow-restart', action='store_true')
    parser.add_argument('--receipt', type=Path, default=Path('receipts/columbia-identity.json'))
    args = parser.parse_args()
    profile = load_profile(args.profile)
    if not profile.get('job_identity'):
        parser.error('The host profile requires job_identity')
    if args.operation == 'plan':
        print(json.dumps(plan(profile), indent=2))
    else:
        apply(profile, args.allow_restart, args.receipt)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
