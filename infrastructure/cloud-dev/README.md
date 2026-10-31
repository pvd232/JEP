# Shared Columbia development VM

Use one persistent Devbox for trusted academic projects. The host profile
installs the terminal connection, pinned tooling and durable job runner once.
Each project definition creates its own checkout, Python environment, cloud
configuration directory, caches, data and job records. Adding a project requires a new
JSON definition and the same setup command.

JEP uses the existing VM `dev`, GCP project `pvd-dev-232`, zone
`us-central1-a`, Google account `pvd2112@columbia.edu`. The intended ChatGPT
connection is **Columbia Dev VM**. This implementation reuses the toolchain
tested on Aether, with a separate Columbia installation and authorization.

## Deployment status: October 31, 2026

The shared host and JEP environment are installed on `dev` in `pvd-dev-232`.
Live inventory verified Ubuntu 24.04.5, 2 CPUs, about 8 GiB RAM and 89 GiB
free root storage before installation. The existing attached account
`dev-vm@pvd-dev-232.iam.gserviceaccount.com` and its `cloud-platform` scope
already matched the profile, so the host required no restart. Its Compute
Viewer grant was applied and a metadata-issued token passed a real Compute
API request with HTTP 200; no token value was recorded.

The real stdio terminal server passed initialization, command execution and
file write/read checks. Reapplying the host installer reported
`CLOUD_DEV_CHANGED=0`; project setup reported `changed: false`. JEP job
`70c04ace84e746c98714b0aa1b0e8ae7` ran for ten minutes after the SSH session
closed, wrote twenty checkpoint heartbeats and exited successfully. Source
validation passed 28 local tests; earlier Linux validation and Ansible syntax
validation passed on Aether.

The existing JEP L4 worker `jep-csts-format-20261021` in `mantra-477901`,
`asia-northeast3-a`, now has
`jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com` attached with the
`cloud-platform` scope and an initial Compute Viewer grant. Its 200 GiB boot
disk was snapshotted first. The worker remained `TERMINATED` throughout;
guest token/API verification must run when it is next intentionally started.
Existing experiment files and runtimes were preserved.

The Mac relay is live and independently verified as
`Peters-MacBook-Air-9.local`, user `machina`. It reuses Aether's connection;
no ngrok subscription or extra VM is required. NumPy 2.5.4 was installed in
the Python interpreter actually used by the Mac's Google Cloud CLI. The
shell and LaunchAgent retain site-package access, and a fresh IAP SSH call
succeeded without the NumPy warning. The bootstrap now handles this dependency.
The older direct Mac connector still points at its exhausted ngrok endpoint;
agents can use the working `mac-command` route now.

Columbia's separate direct ChatGPT connector is the remaining access step.
Its tunnel client and service are installed, but registration and its own
restricted runtime key are pending OpenAI organization/workspace authorization.
The cloud-browser Google sign-in stopped at passkey verification. The
supported terminal registration route also requires a provisioned tunnel
management credential; no admin profile is present. This does not block the
working Mac relay or the installed project environment. Phone access,
tunnel recovery, reboot recovery and snapshot restore have not been accepted.

Recovery snapshots: `columbia-dev-backup-20261031-142059-0` in `pvd-dev-232`
and `jep-gpu-format-dev-backup-20261031-142054-0` in `mantra-477901`.
The project skill is published and referenced by JEP and the agents collection.
Personal Skills registration is tracked separately; its service returned HTTP
422 despite local package validation.

## What is shared and what belongs to JEP

| Component | Location or behavior |
| --- | --- |
| Host tooling and tunnel | `/opt/cloud-dev/columbia`; one host connection |
| JEP checkout | `/home/pvd2112_columbia_edu/columbia-worktrees/jep` |
| JEP environment, caches and data | `/home/pvd2112_columbia_edu/columbia-projects/jep` |
| JEP cloud configuration | `/etc/cloud-dev/columbia/projects/jep` |
| Shared keyless job identity | `dev-vm@pvd-dev-232.iam.gserviceaccount.com` |
| JEP job IDs, logs and checkpoints | `/var/lib/cloud-dev/columbia/projects/jep` |
| Project job resource caps | Shared limit of 1 CPU; memory cap chosen from live available RAM with host headroom |
| GPU training | Existing dedicated worker and IAP route |

The environments support dependency and operational separation. All projects
share the host's Linux user, attached VM service account and outage risk.
Use another VM when credentials/data need a separate trust boundary or a
workload needs independent resources or availability. Keep Aether company
work on its current VM. Google documents that processes on a VM can request
the attached service account's credentials through its metadata server [1].

## Review without connecting

From this directory:

```bash
python3 tools/deploy.py --profile profiles/columbia.json plan
python3 tools/identity.py --profile profiles/columbia.json plan
python3 implementation/project.py --host-profile profiles/columbia.json \
  plan --definition projects/jep.json
python3 -m unittest discover -s tests -v
```

The tested baseline is Ubuntu 24.04, Python 3.12+, x86_64 and systemd. The
installer verifies live GCP metadata and free disk before installation.
The project setup also checks available memory. Existing workspaces keep
their current branch and working tree; a new checkout starts at the explicit
commit in `projects/jep.json`. Install research dependencies from the chosen
experiment's own lockfile when starting that experiment.

## Deploy through the authorized IAP route

Run from a machine with Google Cloud CLI and a current Columbia login:

```bash
python3 tools/deploy.py --profile profiles/columbia.json inventory \
  --receipt receipts/columbia-inventory.json
```

Inspect existing work on dev before changing its attached identity. Google
requires the VM to stop for an account/scope change [2]. The identity helper
snapshots its disks and refuses to restart while recorded durable jobs are
active. It also requires the explicit restart flag:

```bash
python3 tools/identity.py --profile profiles/columbia.json apply \
  --allow-restart --receipt receipts/columbia-identity.json
python3 tools/deploy.py --profile profiles/columbia.json apply \
  --project-definition projects/jep.json \
  --receipt receipts/columbia-before-install.json
```

Apply verifies the target, snapshots attached persistent disks, copies only
the reviewed source/configuration/locks, installs the pinned runtime, and
sets up the JEP environment. It preserves existing application runtimes and
does not reboot or change the GPU worker. Snapshots incur normal GCP storage
charges. The standalone `backup` operation takes another set after saved
authorization and project work exist. Snapshots are crash consistent; record
and test recovery before treating them as a proven restore procedure.

The Ansible entrypoint remains `implementation/playbook.yml`. Supply
`cloud_dev_profile_file` and optional `cloud_dev_project_files` using absolute
paths and the configured Linux user. The direct deployment helper needs only
Python's standard library and Google Cloud CLI on its controller.

## Activate Columbia's own connection

Register a new Secure MCP Tunnel in the intended OpenAI organization and
ChatGPT workspace, then provide its restricted runtime key with Tunnels Read
and Use permissions. Keep that key in protected VM configuration. Run on dev:

```bash
python3 /opt/cloud-dev/columbia/bin/activate.py \
  --config /etc/cloud-dev/columbia/profile.json \
  --tunnel-id REAL_COLUMBIA_TUNNEL_ID
```

The helper prompts for the key through hidden input. Create the custom
connection named **Columbia Dev VM** against that tunnel. The existing Aether
tunnel keeps its own registration and credentials. This follows the outbound
Secure MCP Tunnel design already working on Aether; the HTTP/OAuth fallback
remains an undeployed alternative. DNS ownership and an inbound VM IP are
unnecessary for the selected tunnel route.

## Keyless Google Cloud jobs

Apply the `run-keyless-cloud-jobs` skill for CPU and GPU execution. To prepare
an existing GPU worker, collect its live instance JSON and use
`tools/make_gpu_profile.py` with its verified Linux user. The identity helper
checks GPU process PIDs as well as durable job records, and preserves an
already stopped worker's state. Keep the GPU's existing runtime; identity
provisioning does not require installing the full development-host stack.

The reusable skill is included under `.agents/skills/run-keyless-cloud-jobs`
at the repository root and is loaded by the project instructions.

## Mac connection through the existing VM

The private reverse SSH relay reuses Aether's authenticated terminal connector.
It creates no additional VM, public MCP listener or ngrok subscription. The VM
helper is `tools/mac_relay.py`; run `tools/start_mac_relay.sh` once on the Mac
after enabling Remote Login for the intended local user. It installs a user
LaunchAgent that reconnects automatically. The VM side listens on loopback
port 22022, and its dedicated SSH key is restricted and its Mac host key pinned.
Use `/opt/cloud-dev/aether/bin/mac-command hostname` to verify the Mac route.

Google Cloud workload credentials remain separate from this SSH transport.

## Attached workload account

The host uses the dedicated service account
`dev-vm@pvd-dev-232.iam.gserviceaccount.com`, attached to dev with
the `cloud-platform` access scope. Its initial IAM grant is
`roles/compute.viewer` on `pvd-dev-232`, which supports inspecting VM state.
Further access belongs in explicit resource-scoped `job_identity.iam_bindings`;
for example, a specific artifact bucket can receive its required object role
after inventory identifies it. The job identity has no provisioning grant.

Google supplies short-lived metadata tokens, and SDKs refresh them through
Application Default Credentials [3]. All terminal, host-job and project-job
environments select the attached account. They remove inherited Google
credential overrides, keep Google Cloud SDK state in a separate directory,
and reject a local user ADC file. No service-account private key is created.
Project environments share this VM account's IAM permissions.

The administrator identity still performs initial IAM/VM provisioning. The
Secure MCP Tunnel uses its own protected runtime credential. Those are
separate from Google Cloud job authentication.

The installed `probe_identity.py` verifies the metadata email, a short-lived
token and a permitted Compute API request. It returns identity, token lifetime
and HTTP status; it never prints or persists the token. The deployment
`verify` command runs this probe before testing the terminal server.

## Use a project environment

The installed wrappers live in `/opt/cloud-dev/columbia/bin`; use that absolute
prefix if the directory is outside the current PATH.

```bash
cloud-project --project jep run -- python --version
cloud-project --project jep submit \
  --cwd /home/pvd2112_columbia_edu/columbia-worktrees/jep \
  --checkpoint /home/pvd2112_columbia_edu/columbia-projects/jep/data/checkpoint \
  -- /absolute/path/to/the/experiment-command
cloud-project --project jep status JOB_ID
cloud-project --project jep logs JOB_ID --offset 0 --limit 16384
cloud-project --project jep cancel JOB_ID
```

Use `submit --resume-json '["/absolute/command","--resume",...]'` only for
checkpoint-aware commands. Jobs without that explicit policy remain
interrupted after a reboot. systemd owns execution and process-group
cancellation. CPU and memory caps apply to the project's submitted jobs together. Foreground `run`
selects the environment and working directory.

Project Google Cloud SDK configuration lives under the project's `gcloud/`
directory. SDKs obtain credentials from VM metadata. Use the attached service
account in explicit job `--account` arguments. The job record stores environment
variable names and configuration references. Keep user logins on the
administrator route.

For another project, copy `projects/jep.json`, change its id, repository and
pinned commit, then run installed `project.py setup --definition FILE` with
the same `--host-profile /etc/cloud-dev/columbia/profile.json`. For another
VM, copy the host profile and change the target, persistent paths and tunnel
registration. Shared implementation files remain the same.

## Acceptance still required on Columbia

The real stdio probe and ten-minute detached project job passed. After
activation, make command and file calls from a phone through Columbia Dev VM.
Test tunnel process recovery, a safe
reboot with a checkpoint-aware job, credential replacement, a post-activation
snapshot, and recovery onto a separate test VM. Check active work before any
reboot. Record evidence under `receipts/`; keep private recovery material out
of Git.

[1]: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts
[2]: https://docs.cloud.google.com/compute/docs/instances/change-service-account
[3]: https://docs.cloud.google.com/docs/authentication/application-default-credentials
