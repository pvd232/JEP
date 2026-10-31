#!/usr/bin/python3
"""Launch the pinned stdio server and attach target-specific instructions."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading

profile = json.loads(Path(os.environ.get('CLOUD_DEV_CONFIG', '/etc/cloud-dev/profile.json')).read_text())
target = profile['target']
environment = os.environ.copy()
environment['PATH'] = profile['resolved']['node_bin_dir'] + ':' + profile['resolved']['bin_dir'] + ':' + environment.get('PATH', '/usr/bin:/bin')
environment['HOME'] = profile['resolved']['linux_home']
command = [profile['resolved']['node'], profile['resolved']['desktop_commander_entry'], '--no-onboarding']
child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr, cwd=profile['paths']['workspace_root'], env=environment)
instructions = (
    f"You are connected to {profile['connection_name']}: VM {target['vm_name']}, GCP project {target['gcp_project']}, zone {target['zone']}, user {target['linux_user']}. "
    f"Use {profile['paths']['workspace_root']} for development. Use explicit project, zone, and account in cloud commands. Route native Mac tasks to the Mac. "
    f"For work that must survive disconnection use cloud-job submit --cwd PATH -- COMMAND ARGUMENTS, then cloud-job status ID and cloud-job logs ID. Cancel with cloud-job cancel ID. "
    "Check host identity and repository status before changes. Use task worktrees and project lockfiles. Preserve existing work and active jobs."
)
instructions += (
    f" This is a shared development host. Project data and environments live under {profile['paths'].get('project_root', profile['paths']['workspace_root'])}. "
    "For project jobs use cloud-project --project PROJECT_ID submit --cwd PATH -- COMMAND ARGUMENTS; retrieve results with cloud-project --project PROJECT_ID status ID or logs ID. "
    "Project environments share the host's trust boundary. " + profile.get('project_instructions', '')
)


def forward_input():
    try:
        for line in sys.stdin.buffer:
            child.stdin.write(line)
            child.stdin.flush()
    except (BrokenPipeError, ValueError):
        pass
    finally:
        try:
            child.stdin.close()
        except (BrokenPipeError, ValueError):
            pass


def terminate(signum, frame):
    child.terminate()


signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGINT, terminate)
threading.Thread(target=forward_input, daemon=True).start()
for line in child.stdout:
    try:
        message = json.loads(line)
        result = message.get('result', {})
        if isinstance(result, dict) and 'protocolVersion' in result and 'serverInfo' in result:
            result['instructions'] = instructions + '\n' + result.get('instructions', '')
            line = (json.dumps(message) + '\n').encode()
    except (ValueError, AttributeError):
        pass
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()
sys.exit(child.wait())
