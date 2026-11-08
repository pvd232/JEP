#!/usr/bin/env python3
"""Read-only host and destination identity checks; never emit bearer credentials."""
import argparse
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward metadata headers or bearer credentials to a redirect target."""

    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def metadata(path):
    """Read Google metadata without environment proxy or redirect overrides."""
    request = urllib.request.Request(
        'http://metadata.google.internal/computeMetadata/v1/' + path,
        headers={'Metadata-Flavor': 'Google'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=5) as response:
        if response.headers.get('Metadata-Flavor') != 'Google':
            raise RuntimeError('Unexpected metadata response')
        return response.read().decode().strip()


def verify_host(profile):
    """Verify the actual host and attached principal without requesting a token."""
    target, identity = profile['target'], profile['job_identity']
    project = metadata('project/project-id')
    instance = metadata('instance/name')
    email = metadata('instance/service-accounts/default/email')
    if (identity.get('mode') != 'attached_service_account'
            or project != target['gcp_project'] or instance != target['vm_name']
            or email != identity['service_account_email']):
        raise RuntimeError('Live VM or attached job identity differs from the configured target')
    return {'service_account': email, 'gcp_project': project, 'vm': instance}


def access_token():
    """Obtain an ephemeral token internally; callers never serialize this mapping."""
    value = json.loads(metadata('instance/service-accounts/default/token'))
    lifetime = value.get('expires_in')
    if (value.get('token_type') != 'Bearer' or not isinstance(lifetime, (int, float))
            or isinstance(lifetime, bool) or not 0 < lifetime <= 3600
            or not isinstance(value.get('access_token'), str) or not value['access_token']):
        raise RuntimeError('Unexpected metadata access-token lifetime or type')
    return value


def compute_get(project, zone, instance):
    """Read one fixed Google API resource; fetch credentials anew for this request."""
    token = access_token()
    url = ('https://compute.googleapis.com/compute/v1/projects/' + project
           + '/zones/' + zone + '/instances/' + instance)
    request = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token['access_token']})
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=15) as response:
        return response.status, json.load(response), token['expires_in']


def probe(profile):
    """Retain the existing host-only receipt, explicitly identifying its scope."""
    host = verify_host(profile)
    status, observed, lifetime = compute_get(host['gcp_project'], profile['target']['zone'], host['vm'])
    if status != 200 or observed.get('name') != host['vm']:
        raise RuntimeError('Unexpected Compute API identity response')
    return {'keyless_identity_verified': True, **host,
            'token_expires_in_seconds': lifetime, 'compute_api_http_status': status,
            'scope': 'host_only', 'workload_access_verified': False}


def probe_workload(profile):
    """Prove host and assigned-instance reads separately; never claim SSH/storage readiness."""
    from project import project_environment, workload_context

    # Enforce the same saved configuration checks as the real child process.
    project_environment(profile)
    context = workload_context(profile)
    result = {
        'scope': 'host_and_assigned_instance_reads',
        'controller_account': context['account'],
        'resource_project': context['resource_project'],
        'manifest_sha256': context['manifest_sha256'],
        'source_commit': context['approval']['source_commit'],
        'artifact_prefix': context['artifact_prefix'],
        'host': None, 'targets': [], 'workload_access_verified': False,
        'execution_ready': False,
        'not_checked': ['IAP', 'guest_SSH', 'storage_write_read', 'long_lived_refresh',
                        'collector_exclusivity', 'shutdown_deadline'],
    }
    try:
        result['host'] = probe(profile)
    except urllib.error.HTTPError as error:
        result['host'] = {'verified': False, 'http_status': error.code, 'error': 'HOST_API_DENIED'}
        return result
    except (OSError, ValueError, RuntimeError):
        result['host'] = {'verified': False, 'error': 'HOST_IDENTITY_OR_METADATA_FAILED'}
        return result
    for worker, assignment in context['approval']['assignments'].items():
        item = {'worker': worker, 'project': assignment['project'], 'zone': assignment['zone'],
                'instance': assignment['instance_name'], 'expected_id': assignment['instance_id'],
                'operation': 'compute.instances.get', 'verified': False}
        try:
            status, observed, _ = compute_get(assignment['project'], assignment['zone'], assignment['instance_name'])
            item['http_status'] = status
            item['verified'] = (status == 200 and observed.get('name') == assignment['instance_name']
                                and str(observed.get('id')) == assignment['instance_id'])
            if not item['verified']:
                item['error'] = 'TARGET_IDENTITY_MISMATCH'
        except urllib.error.HTTPError as error:
            item['http_status'] = error.code
            item['error'] = 'TARGET_API_DENIED' if error.code in (401, 403) else 'TARGET_API_ERROR'
            if error.code == 403:
                item['required_permission'] = 'compute.instances.get'
        except (OSError, ValueError, RuntimeError):
            item['error'] = 'TARGET_READ_FAILED'
        result['targets'].append(item)
    result['workload_access_verified'] = bool(result['targets']) and all(t['verified'] for t in result['targets'])
    return result


def main():
    """Emit secret-free JSON; destination failure remains a nonzero exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('--workload', action='store_true', help='Check manifest-selected destination reads too')
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text())
    try:
        result = probe_workload(profile) if args.workload else probe(profile)
    except (OSError, ValueError, RuntimeError):
        print(json.dumps({'error': 'INVALID_PROFILE_OR_IDENTITY', 'workload_access_verified': False}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get('workload_access_verified' if args.workload else 'keyless_identity_verified') else 1


if __name__ == '__main__':
    sys.exit(main())
