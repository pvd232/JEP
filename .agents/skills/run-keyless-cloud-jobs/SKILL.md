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

For native Mac commands, apply [Connect Mac Relay](https://github.com/pvd232/agents/blob/main/skills/connect-mac-relay/SKILL.md).
Keep cloud workloads on their intended VM and Mac commands on the Mac.

## Verify the attached identity

Read [identity preflight](references/gcp-setup.md). Require the VM's existing
attached service account to match the project configuration. Verify its
metadata identity and a permitted API operation before starting the job.

Keep routine job execution scoped to the existing account and its granted
permissions. If the account or resource grant is missing, report the exact
principal, permission and resource requiring an administrator grant. Treat
IAM changes, service-account attachment and VM power changes as separately
requested infrastructure work under the project's reviewed setup workflow.
Preserve active jobs and the existing state of stopped GPU workers.

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
