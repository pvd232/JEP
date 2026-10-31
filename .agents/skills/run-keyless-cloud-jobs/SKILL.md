---
name: run-keyless-cloud-jobs
description: Run Google Cloud CPU and GPU workloads with attached service accounts, automatically refreshed credentials, and durable jobs. Use by default for GCP development, GPU training or inference, unattended experiments, cloud execution, and repeated gcloud logins. Exclude conceptual ML advice and native Mac work.
---

# Run Keyless Cloud Jobs

Default Google Cloud workloads to the service account attached to their VM.
Use short-lived metadata credentials with automatic SDK refresh. Keep initial
administrator provisioning and the ChatGPT connection as separate authentication.

## Authorization

Work within the projects, instances and resources authorized by the user.
Follow platform and connector approval requirements for every action. Keep
IAM changes, service-account attachment, restarts and SSH access changes
within that authorization. Use the narrowest resource permissions required.
When an operation is denied for security or access reasons, stop that
operation and report the required grant; continue independent preparation.

## Resolve the host and workload

1. Inspect project instructions and current VM inventory. Read
   [project routes](references/project-routes.md) for established connections.
2. Reuse the persistent CPU development host for coding and orchestration.
   Run GPU work on an existing suitable worker. Preserve its project, zone,
   disks, runtime, checkpoints and active work.
3. Verify project ID, instance name, zone, Linux user, attached service account,
   memory/disk and GPU processes before changes. Supply explicit account,
   project and zone arguments to cloud commands.
4. Resolve the existing project environment and dependency lock. Reuse
   completed measurements and checkpoints.

For a failed Mac connector, use [the existing-VM Mac relay](references/mac-relay.md).
Keep cloud workloads on their intended VM and Mac commands on the Mac.

## Provision identity once

Follow [GCP setup](references/gcp-setup.md). Create or reuse a dedicated
workload service account and declare IAM roles for observed resources. Apply
IAM once, attach the account with the `cloud-platform` scope, and let IAM
determine access. Generate no service-account private-key file.

For a running VM, inspect durable jobs and GPU process PIDs before a
stop/start required for an attachment change. Let active jobs finish or use
their documented checkpoint procedure. Keep an already stopped GPU worker
stopped after updating its identity. Save a recovery snapshot and the prior
account/scopes before a running-host change.

When access is denied, name the exact principal, permission and resource
requiring an administrator grant. Prepare the proposed resource and role
changes for the authorized administrator and follow the applicable approval
requirements before applying them.

## Run with metadata credentials

- Select the attached account for Google Cloud CLI commands. Keep SDK state
  in a separate host/project configuration directory.
- Clear inherited `GOOGLE_APPLICATION_CREDENTIALS`, access-token overrides,
  credential-file overrides and unintended impersonation. Preserve existing
  credential files; reject a job configuration containing a local user ADC file.
- Use the project's existing runtime. Verify attached identity and a permitted
  API operation, reporting only principal, token lifetime and status. Keep
  token values out of output, arguments and persistent records.
- Submit long work through a persistent job runner. Record job ID, exact
  command/configuration references, revision, output, exit status and
  checkpoint path. Require an explicit resume command for reboot recovery.
- Retrieve existing jobs across chats. Reuse successful artifacts when a
  downstream serializer, evaluator or report needs repair.

For the installed cloud-development runner:

```bash
cloud-project --project PROJECT submit --cwd WORKTREE \
  --checkpoint CHECKPOINT -- COMMAND ARGUMENTS
cloud-project --project PROJECT status JOB_ID
cloud-project --project PROJECT logs JOB_ID
```

Use a separate project environment and job namespace on shared hosts. All
processes on a VM can access its attached account. Keep company and academic
hosts separate when their credentials or data require that boundary.

## Verify and report

Confirm identity selection, short-lived token acquisition, a permitted API
call and durable job retrieval on the actual target. Distinguish tested code,
prepared configuration and applied cloud changes. State one concrete next
action when access blocks rollout. Keep responses brief when speed is requested.
