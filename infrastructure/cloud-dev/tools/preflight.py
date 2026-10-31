#!/usr/bin/env python3
"""Render a target plan, or collect bounded inventory from a GCP Linux VM.

The default mode only renders a plan. --local collects on the current VM;
--remote uses an already-authorized gcloud/IAP SSH route. No installation,
service changes, secret reads, reboot, or deletion is performed by this tool.
Google Cloud CLI may perform its normal SSH key provisioning when connecting.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


def load_profile(path):
    data = json.loads(Path(path).read_text())
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    target = data["target"]
    patterns = {
        "gcp_project": r"[a-z][a-z0-9-]{4,28}[a-z0-9]",
        "zone": r"[a-z]+-[a-z0-9]+[0-9]-[a-z]",
        "vm_name": r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?",
        "linux_user": r"[a-z_][a-z0-9_-]{0,63}",
        "gcp_account": r"[^\s@]+@[^\s@]+",
    }
    for key, pattern in patterns.items():
        if not re.fullmatch(pattern, str(target.get(key, ""))):
            raise ValueError(f"Invalid or unresolved target.{key}")
    if not isinstance(target.get("ssh_via_iap"), bool):
        raise ValueError("target.ssh_via_iap must be a boolean")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", data.get("profile", "")):
        raise ValueError("profile must be a short lowercase identifier")
    for key in ["workspace_root", "project_root", "install_root", "state_root", "config_root"]:
        path_value = data["paths"][key]
        if not isinstance(path_value, str) or not re.fullmatch(r'/[A-Za-z0-9_./-]+', path_value):
            raise ValueError(f"paths.{key} must be absolute and contain only letters, digits, underscores, periods, slashes, or hyphens")
        if path_value == "/" or ".." in Path(path_value).parts or "REPLACE" in path_value:
            raise ValueError(f"Unsafe or unresolved paths.{key}")
    return data


def ssh_arguments(profile):
    target = profile["target"]
    arguments = [
        "gcloud", "compute", "ssh", f"{target['linux_user']}@{target['vm_name']}",
        f"--project={target['gcp_project']}", f"--zone={target['zone']}",
        f"--account={target['gcp_account']}", "--ssh-flag=-oBatchMode=yes",
    ]
    if target["ssh_via_iap"]:
        arguments.append("--tunnel-through-iap")
    return arguments


def collect(profile):
    import platform
    import pwd
    import shutil
    import urllib.request

    def metadata(path):
        request = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/" + path,
            headers={"Metadata-Flavor": "Google"},
        )
        try:
            # Bypass proxy environment settings for the metadata request.
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=2) as response:
                if response.headers.get("Metadata-Flavor") != "Google":
                    return None
                return response.read(4096).decode().strip()
        except Exception:
            return None

    observed = {
        "gcp_project": metadata("project/project-id"),
        "vm_name": metadata("instance/name"),
        "zone": metadata("instance/zone"),
        "linux_user": pwd.getpwuid(os.getuid()).pw_name,
    }
    if observed["zone"]:
        observed["zone"] = observed["zone"].rsplit("/", 1)[-1]
    mismatches = {
        key: {"expected": profile["target"][key], "observed": value}
        for key, value in observed.items() if profile["target"][key] != value
    }
    result = {
        "schema_version": 1,
        "profile": profile["profile"],
        "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_verified": not mismatches,
        "identity": observed,
        "identity_mismatches": mismatches,
    }
    if mismatches:
        result["next_action"] = "Run on the configured VM as the configured Linux user; resolve identity before setup."
        return result

    def command(arguments):
        try:
            done = subprocess.run(arguments, text=True, capture_output=True, timeout=10)
            return {"exit_code": done.returncode, "output": (done.stdout + done.stderr)[:12000]}
        except (OSError, subprocess.TimeoutExpired) as error:
            return {"error": str(error)}

    os_info = Path("/etc/os-release")
    result["os_release"] = os_info.read_text()[:5000] if os_info.exists() else None
    result["architecture"] = platform.machine()
    result["cpu_count"] = os.cpu_count()
    result["memory_kib"] = {
        line.split(':')[0]: int(line.split()[1])
        for line in Path('/proc/meminfo').read_text().splitlines()
        if line.startswith(('MemTotal:', 'MemAvailable:'))
    }
    result["paths"] = {}
    for key, value in profile["paths"].items():
        path_value = Path(value)
        ancestor = path_value
        while not ancestor.exists() and ancestor != ancestor.parent:
            ancestor = ancestor.parent
        usage = shutil.disk_usage(ancestor)
        result["paths"][key] = {
            "path": value, "exists": path_value.exists(),
            "storage_probe_path": str(ancestor), "free_bytes": usage.free,
            "total_bytes": usage.total,
        }
    result["mounts"] = command(["findmnt", "--json", "--output", "TARGET,SOURCE,FSTYPE"])
    result["versions"] = {}
    for tool in ["node", "npm", "python3", "gcloud", "git", "docker", "tunnel-client"]:
        executable = shutil.which(tool)
        result["versions"][tool] = {"path": executable}
        if executable:
            result["versions"][tool].update(command([executable, "--version"]))
    result["service_units"] = {}
    for label, arguments in [
        ("system", ["systemctl", "list-unit-files", "--type=service", "--no-pager", "--no-legend"]),
        ("user", ["systemctl", "--user", "list-unit-files", "--type=service", "--no-pager", "--no-legend"]),
    ]:
        unit_result = command(arguments)
        if "output" in unit_result:
            unit_result["output"] = "\n".join(
                line for line in unit_result["output"].splitlines()
                if re.search(r"desktop|mcp|tunnel|caddy|ngrok|cloudflared|aether|viper", line, re.I)
            )
        result["service_units"][label] = unit_result
    result["note"] = "Inventory only. No credentials, tokens, environment values, or service contents were read."
    return result


def render_plan(profile):
    return {
        "profile": profile["profile"],
        "connection_name": profile["connection_name"],
        "target": profile["target"],
        "paths": profile["paths"],
        "admin_ssh_command": shlex.join(ssh_arguments(profile)),
        "preferred_transport": profile["transport"]["preferred"],
        "fallback_transport": profile["transport"]["fallback"],
        "execution_order": [
            "0: inventory and recovery checkpoint",
            "1: account access and transport proof",
            "2: idempotent host and project automation",
            "3: durable job runner and backup",
            "4: end-to-end acceptance and recovery",
            "5: repeat on a second VM",
        ],
        "deployment_status": "deployment not verified; live inventory, authorization, and acceptance checks required",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="render parameters and steps; default")
    mode.add_argument("--local", action="store_true", help="inventory this VM; require matching GCP metadata")
    mode.add_argument("--remote", action="store_true", help="inventory through the configured gcloud/IAP route")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    try:
        profile = load_profile(arguments.profile)
        if arguments.remote:
            import base64
            source = Path(__file__).read_text()
            data_b64 = base64.b64encode(json.dumps(profile).encode()).decode()
            source += (
                "\n_profile = json.loads(__import__('base64').b64decode(" + repr(data_b64) + "))\n"
                "print(json.dumps(collect(_profile)))\n"
            )
            # Suppress main() in the copied module and call only collect().
            source = source.replace('if __name__ == "__main__":\n    sys.exit(main())', '')
            source_b64 = base64.b64encode(source.encode()).decode()
            remote_python = "import base64;exec(compile(base64.b64decode(" + repr(source_b64) + "),'<cloud-dev-inventory>','exec'))"
            command = ssh_arguments(profile) + ["--command", "python3 -c " + shlex.quote(remote_python)]
            completed = subprocess.run(command, text=True, capture_output=True, timeout=180)
            if completed.returncode:
                raise RuntimeError("SSH inventory failed: " + completed.stderr[-5000:])
            result = json.loads(completed.stdout)
        elif arguments.local:
            result = collect(profile)
        else:
            result = render_plan(profile)
        rendered = json.dumps(result, indent=2) + "\n"
        if arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(rendered)
        print(rendered, end="")
        return 0 if result.get("target_verified", True) else 2
    except (KeyError, ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
