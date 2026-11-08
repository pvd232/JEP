#!/usr/bin/env python3
"""One-time administrator setup for existing JEP workers. Plan-only by default.

Run in the owner's Google Cloud Shell. Never stops/restarts/creates a VM, changes
its service account or startup script, opens test data, or touches collectors.
Only --apply enables additive IAM grants and an additive SSH-public-key update.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ADMIN = 'pvd2112@columbia.edu'
PROJECT = 'mantra-477901'
PRINCIPAL = 'dev-vm@pvd-dev-232.iam.gserviceaccount.com'
MEMBER = 'serviceAccount:' + PRINCIPAL
WORKER_SA = 'jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com'
BUCKET = 'mantra-mlfg-prod-uscentral1-8e7a'
PREFIX = 'viper/pvd232/jep_full_data_prompt_20261107/'
TASK = 'jep-full-data-20261107'
PUBLIC_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMwOLWY22BY2ZJorKonJMkwWgkl2PrnuxI9raszqaWSJ machina'
KEY_FINGERPRINT = 'SHA256:fS9IqRqbaG8cqCCaL289rbH76apAQXO4ofPp8sqGBhY'
REGIONS = {'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-northeast3'}
ROLES = {
    'jepColumbiaReadV1': [
        'compute.instances.get', 'compute.instances.list', 'compute.projects.get',
        'compute.zones.list', 'compute.regions.list', 'compute.zoneOperations.get',
        'compute.globalOperations.get', 'resourcemanager.projects.get'],
    'jepColumbiaWorkerV1': [
        'compute.instances.get', 'compute.instances.start', 'compute.instances.stop',
        'compute.instances.setMetadata'],
    'jepColumbiaArtifactsV1': [
        'storage.buckets.get', 'storage.objects.create', 'storage.objects.get'],
}
BINDING_NOTE = 'Columbia JEP keyless setup v1'


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def metadata_values(obj: dict) -> dict[str, str]:
    return {x['key']: x['value'] for x in obj.get('items', [])}


def select_workers(rows: list[dict], project_metadata: dict) -> list[dict]:
    """Select only live, task-labelled East Asia workers; reject guest-mode changes."""
    selected = []
    for row in rows:
        if row.get('labels', {}).get('task') != TASK or row.get('status') != 'RUNNING':
            continue
        zone = row['zone'].rsplit('/', 1)[-1]
        if not row['name'].startswith('jep-full-prompt-') or zone.rsplit('-', 1)[0] not in REGIONS:
            raise ValueError('Task label found on an unexpected name/region; inspect manually.')
        if not str(row.get('id', '')).isdigit():
            raise ValueError('Worker has no immutable numeric ID.')
        if [x.get('email') for x in row.get('serviceAccounts', [])] != [WORKER_SA]:
            raise ValueError('Worker service account differs from the recorded JEP identity.')
        effective = dict(project_metadata)
        effective.update(metadata_values(row.get('metadata', {})))
        if effective.get('enable-oslogin', 'false').lower() != 'false':
            raise ValueError('OS Login is enabled/unknown. No guest mode or IAM was changed; do not disable it on a live VM.')
        selected.append(row)
    if not 1 <= len(selected) <= 2:
        raise ValueError(f'Expected 1 or 2 running task workers; observed {len(selected)}. No grants applied.')
    return sorted(selected, key=lambda r: (r['zone'], r['name']))


def additive_policy(policy: dict, role: str, condition: dict | None = None) -> tuple[dict, bool]:
    """Keep existing policy entries/etag and add only this exact binding/member."""
    new = copy.deepcopy(policy)
    if condition or any('condition' in b for b in new.get('bindings', [])):
        new['version'] = 3
    for binding in new.setdefault('bindings', []):
        if binding.get('role') == role and binding.get('condition') == condition:
            if MEMBER in binding.get('members', []):
                return new, False
            binding.setdefault('members', []).append(MEMBER)
            return new, True
    binding = {'role': role, 'members': [MEMBER]}
    if condition:
        binding['condition'] = condition
    new['bindings'].append(binding)
    return new, True


def append_public_key(metadata: dict) -> tuple[dict, bool]:
    """Preserve all prior metadata and SSH keys; append only Columbia's public key."""
    updated = copy.deepcopy(metadata)
    items = updated.setdefault('items', [])
    entry = next((i for i in items if i['key'] == 'ssh-keys'), None)
    line = 'machina:' + PUBLIC_KEY
    if entry:
        if line in entry['value'].splitlines():
            return updated, False
        prior = entry['value']
        entry['value'] = prior + ('' if not prior or prior.endswith('\n') else '\n') + line + '\n'
    else:
        items.append({'key': 'ssh-keys', 'value': line + '\n'})
    # Only these API fields belong in the metadata-write request.
    return {k: updated[k] for k in ('fingerprint', 'items') if k in updated}, True


class Setup:
    def __init__(self, apply: bool, output: Path):
        self.apply = apply
        self.output = output
        self.records: list[dict] = []
        self.token = ''
        self.token_at = 0.0

    def event(self, operation: str, **fields) -> None:
        record = {'utc': utc(), 'operation': operation, **fields}
        self.records.append(record)
        self.output.write_text(json.dumps(self.records, indent=2) + '\n')
        print(json.dumps(record), flush=True)

    def cli(self, args: list[str]) -> object:
        cmd = ['gcloud', *args, '--account=' + ADMIN, '--project=' + PROJECT, '--quiet', '--format=json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError('gcloud ' + ' '.join(args[:4]) + ': ' + result.stderr[-1800:])
        return json.loads(result.stdout) if result.stdout.strip() else None

    def api(self, url: str, method: str = 'GET', body: dict | None = None) -> dict:
        allowed = {'compute.googleapis.com', 'iap.googleapis.com', 'storage.googleapis.com'}
        if urllib.parse.urlsplit(url).hostname not in allowed or not url.startswith('https://'):
            raise ValueError('Unexpected API destination.')
        if time.monotonic() - self.token_at > 2400 or not self.token:
            # The owner's own Cloud Shell client supplies this token. It remains
            # in process memory, never in argv, output, a receipt, Git or a file.
            r = subprocess.run(['gcloud', 'auth', 'print-access-token', '--account=' + ADMIN],
                               capture_output=True, text=True, timeout=60)
            if r.returncode:
                raise RuntimeError('Cloud Shell authorization is required; authorize inside Google, not by sending codes to chat.')
            self.token, self.token_at = r.stdout.strip(), time.monotonic()
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                     method=method, headers={'Authorization': 'Bearer ' + self.token,
                                                            'Content-Type': 'application/json'})
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        opener = urllib.request.build_opener(NoRedirect())
        try:
            with opener.open(req, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # Do not dump HTTP headers or full resource bodies to the receipt.
            raise RuntimeError(f'{method} {urllib.parse.urlsplit(url).path}: HTTP {error.code}; no automatic permission broadening.') from None

    def ensure_role(self, role_id: str, permissions: list[str], existing: dict) -> None:
        role = existing.get(role_id)
        if role:
            if role.get('deleted') or role.get('stage') in ('DISABLED', 'DEPRECATED') or set(role.get('includedPermissions', [])) != set(permissions):
                raise ValueError('Existing role differs: ' + role_id + '; refusing to overwrite it.')
            return
        self.cli(['iam', 'roles', 'create', role_id, '--title=' + role_id,
                  '--description=' + BINDING_NOTE, '--stage=GA', '--permissions=' + ','.join(permissions)])
        self.event('custom_role_created', role=role_id, permissions=permissions)

    def worker(self, original: dict) -> dict:
        zone = original['zone'].rsplit('/', 1)[-1]
        url = f'https://compute.googleapis.com/compute/v1/projects/{PROJECT}/zones/{zone}/instances/{original["name"]}'
        fresh = self.api(url)
        if (str(fresh.get('id')) != str(original['id'])
                or fresh.get('labels', {}).get('task') != TASK):
            raise ValueError('Worker identity changed during setup. No replacement is authorized.')
        return fresh

    def iap_binding(self, number: str, row: dict) -> None:
        zone = row['zone'].rsplit('/', 1)[-1]
        base = f'https://iap.googleapis.com/v1/projects/{number}/iap_tunnel/zones/{zone}/instances/{row["id"]}'
        self.worker(row)
        policy = self.api(base + ':getIamPolicy', 'POST', {'options': {'requestedPolicyVersion': 3}})
        condition = {'title': 'columbia_jep_ssh_only', 'expression': 'destination.port == 22'}
        new, changed = additive_policy(policy, 'roles/iap.tunnelResourceAccessor', condition)
        if changed:
            self.api(base + ':setIamPolicy', 'POST', {'policy': new})
        self.event('instance_iap_grant', instance=row['name'], instance_id=str(row['id']), changed=changed, port=22)

    def storage_binding(self) -> None:
        url = f'https://storage.googleapis.com/storage/v1/b/{BUCKET}/iam'
        policy = self.api(url + '?optionsRequestedPolicyVersion=3')
        base = 'projects/_/buckets/' + BUCKET
        condition = {'title': 'columbia_jep_artifacts', 'expression':
                     f"resource.name == '{base}' || resource.name.startsWith('{base}/objects/{PREFIX}')"}
        role = f'projects/{PROJECT}/roles/jepColumbiaArtifactsV1'
        new, changed = additive_policy(policy, role, condition)
        if changed:
            self.api(url, 'PUT', new)
        self.event('artifact_grant', bucket=BUCKET, prefix=PREFIX, changed=changed,
                   permissions=ROLES['jepColumbiaArtifactsV1'], list_or_delete_granted=False)

    def run(self) -> None:
        active = subprocess.run(['gcloud', 'config', 'get-value', 'account'],
                                capture_output=True, text=True, timeout=30)
        if active.returncode or active.stdout.strip() != ADMIN:
            raise ValueError('Open Cloud Shell signed in as ' + ADMIN + '. Do not send a login code to chat.')
        rows = self.cli(['compute', 'instances', 'list', '--filter=labels.task=' + TASK])
        info = self.cli(['compute', 'project-info', 'describe'])
        selected = select_workers(rows, metadata_values(info.get('commonInstanceMetadata', {})))
        project = self.cli(['projects', 'describe', PROJECT])
        bucket = self.api(f'https://storage.googleapis.com/storage/v1/b/{BUCKET}?fields=name,iamConfiguration')
        if not bucket.get('iamConfiguration', {}).get('uniformBucketLevelAccess', {}).get('enabled'):
            raise ValueError('Bucket lacks uniform bucket-level access; refusing to change live storage settings.')
        roles = self.cli(['iam', 'roles', 'list', '--view=FULL'])
        existing = {r['name'].rsplit('/', 1)[-1]: r for r in roles}
        for role_id, permissions in ROLES.items():
            role = existing.get(role_id)
            if role and (role.get('deleted') or role.get('stage') in ('DISABLED', 'DEPRECATED')
                         or set(role.get('includedPermissions', [])) != set(permissions)):
                raise ValueError('Role name collision; no changes applied: ' + role_id)
        self.event('plan', mode='APPLY' if self.apply else 'PLAN_ONLY', principal=PRINCIPAL,
                   workers=[{'name':r['name'],'id':str(r['id']),'zone':r['zone'].rsplit('/',1)[-1]} for r in selected],
                   roles=ROLES, public_key_fingerprint=KEY_FINGERPRINT,
                   no_vm_restart=True, no_collector_changes=True, no_service_account_reattachment=True)
        if not self.apply:
            self.event('PLAN_OK', next_action='Run this same script with --apply after reviewing the plan.')
            return
        for role_id, permissions in ROLES.items():
            self.ensure_role(role_id, permissions, existing)
        self.cli(['projects','add-iam-policy-binding',PROJECT,'--member='+MEMBER,
                  f'--role=projects/{PROJECT}/roles/jepColumbiaReadV1','--condition=None'])
        self.event('project_read_grant', project=PROJECT, principal=PRINCIPAL)
        self.cli(['iam','service-accounts','add-iam-policy-binding',WORKER_SA,
                  '--member='+MEMBER,'--role=roles/iam.serviceAccountUser','--condition=None'])
        self.event('worker_service_account_user_grant', worker_service_account=WORKER_SA)
        self.storage_binding()
        for row in selected:
            self.worker(row)
            zone = row['zone'].rsplit('/', 1)[-1]
            self.cli(['compute','instances','add-iam-policy-binding',row['name'],'--zone='+zone,
                      '--member='+MEMBER,f'--role=projects/{PROJECT}/roles/jepColumbiaWorkerV1','--condition=None'])
            self.event('worker_permission_grant', instance=row['name'], zone=zone, instance_id=str(row['id']))
            self.iap_binding(str(project['projectNumber']), row)
            fresh = self.worker(row)
            metadata, changed = append_public_key(fresh.get('metadata', {}))
            if changed:
                url = f'https://compute.googleapis.com/compute/v1/projects/{PROJECT}/zones/{zone}/instances/{row["name"]}/setMetadata'
                op = self.api(url,'POST',metadata)
                name = op['name']
                for _ in range(60):
                    state = self.api(f'https://compute.googleapis.com/compute/v1/projects/{PROJECT}/zones/{zone}/operations/{name}')
                    if state['status']=='DONE':
                        if state.get('error'):
                            raise RuntimeError('Metadata operation failed; retain the receipt and existing training.')
                        break
                    time.sleep(2)
                else:
                    raise RuntimeError('Metadata operation still pending; do not repeat or restart a VM.')
                current = self.worker(row)
                expected = 'machina:' + PUBLIC_KEY
                if expected not in metadata_values(current.get('metadata',{})).get('ssh-keys','').splitlines():
                    raise RuntimeError('Public-key verification did not match.')
                old_items = metadata_values(fresh.get('metadata',{}))
                new_items = metadata_values(current.get('metadata',{}))
                if any(new_items.get(k)!=v for k,v in old_items.items() if k!='ssh-keys'):
                    raise RuntimeError('Other metadata changed concurrently; do not overwrite or auto-rollback.')
            self.event('ssh_public_key_registered', instance=row['name'], changed=changed,
                       public_key_fingerprint=KEY_FINGERPRINT, private_key_transferred=False)
        self.event('ACCESS_SETUP_APPLIED', runtime_ready=False,
                   next_action='Return this status and receipt filename; verify from Columbia before any collector cutover.',
                   limitations='No runtime SSH/storage/expiry test or collector deployment performed; IAM may need to propagate.')


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    os.umask(0o077)
    output=Path.cwd()/('columbia-mantra-setup-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'.json')
    setup=Setup(args.apply, output)
    try:
        setup.run()
        print('RECEIPT='+str(output))
        return 0
    except (OSError,ValueError,RuntimeError,KeyError,subprocess.TimeoutExpired) as error:
        setup.event('SETUP_STOPPED', error=str(error), runtime_ready=False,
                    warning='Any earlier additive grants remain; no rollback or GPU lifecycle action was attempted.')
        print('RECEIPT='+str(output),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
