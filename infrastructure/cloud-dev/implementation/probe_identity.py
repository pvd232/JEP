#!/usr/bin/env python3
"""Verify keyless metadata credentials and a scoped API request without exposing tokens."""
import argparse
import json
from pathlib import Path
import urllib.request


def metadata(path):
    request = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/' + path, headers={'Metadata-Flavor': 'Google'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=5) as response:
        if response.headers.get('Metadata-Flavor') != 'Google':
            raise RuntimeError('Unexpected metadata response')
        return response.read().decode().strip()


def probe(profile):
    target = profile['target']
    identity = profile['job_identity']
    project = metadata('project/project-id')
    instance = metadata('instance/name')
    email = metadata('instance/service-accounts/default/email')
    if project != target['gcp_project'] or instance != target['vm_name'] or email != identity['service_account_email']:
        raise RuntimeError('Live VM or attached job identity differs from the configured target')
    token = json.loads(metadata('instance/service-accounts/default/token'))
    if token.get('token_type') != 'Bearer' or not 0 < token.get('expires_in', 0) <= 3600:
        raise RuntimeError('Unexpected metadata access-token lifetime or type')
    url = 'https://compute.googleapis.com/compute/v1/projects/' + project + '/zones/' + target['zone'] + '/instances/' + instance
    request = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token['access_token']})
    with urllib.request.urlopen(request, timeout=15) as response:
        api_status = response.status
        observed = json.load(response)
    if observed.get('name') != instance:
        raise RuntimeError('Unexpected Compute API identity response')
    # Never return or persist the access token itself.
    return {'keyless_identity_verified': True, 'service_account': email, 'gcp_project': project, 'vm': instance, 'token_expires_in_seconds': token['expires_in'], 'compute_api_http_status': api_status}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(probe(json.loads(args.profile.read_text())), indent=2))


if __name__ == '__main__':
    main()
