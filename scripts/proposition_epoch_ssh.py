"""Use the existing Mac SSH identity with a task-local writable gcloud cache."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


def main():
    source = Path('/Users/machina/.config/gcloud')
    temporary = Path(tempfile.mkdtemp(prefix='jep-epoch-gcloud-', dir='/tmp'))
    os.chmod(temporary, 0o700)
    try:
        for name in ('credentials.db', 'access_tokens.db', 'active_config'):
            item = source / name
            if item.exists():
                shutil.copy2(item, temporary / name)
                os.chmod(temporary / name, 0o600)
        shutil.copytree(source / 'configurations', temporary / 'configurations')
        environment = os.environ.copy()
        environment['CLOUDSDK_CONFIG'] = str(temporary)
        environment['CLOUDSDK_CORE_DISABLE_FILE_LOGGING'] = 'true'
        proxy = '/Users/machina/google-cloud-sdk/bin/gcloud compute start-iap-tunnel jep-csts-format-20261021 22 --account=pvd2112@columbia.edu --project=mantra-477901 --zone=asia-northeast3-a --listen-on-stdin --verbosity=error'
        command = ['ssh', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', '-o', 'IdentitiesOnly=yes', '-i', '/Users/machina/.ssh/google_compute_engine', '-o', 'HostKeyAlias=compute.8646910299736412654', '-o', 'UserKnownHostsFile=/Users/machina/.ssh/google_compute_known_hosts', '-o', 'StrictHostKeyChecking=yes', '-o', 'ProxyCommand=' + proxy, 'machina@compute.8646910299736412654', shlex.join(sys.argv[1:])]
        result = subprocess.run(command, env=environment, input=sys.stdin.buffer.read(), capture_output=True, timeout=70)
        sys.stdout.buffer.write(result.stdout)
        sys.stderr.buffer.write(result.stderr)
        return result.returncode
    finally:
        shutil.rmtree(temporary)


if __name__ == '__main__':
    sys.exit(main())
