# JEP execution

Read [.agents/skills/run-keyless-cloud-jobs/SKILL.md](.agents/skills/run-keyless-cloud-jobs/SKILL.md)
by default before GCP CPU or GPU execution. Use attached workload identities and durable job records for
both development hosts and GPU workers. Keep the worker's existing project
runtime and checkpoints; preserve active GPU jobs and stopped-worker state.

The persistent development host is `dev` in GCP project `pvd-dev-232`,
zone `us-central1-a`, account `pvd2112@columbia.edu`, Linux user
`pvd2112_columbia_edu`. Its installed ChatGPT plugin is **columbia-vm**, serving Columbia Dev VM. Read
`infrastructure/cloud-dev/README.md` for deployment status before using it.

Verify live host identity and repository status before changes. Use
`/home/pvd2112_columbia_edu/columbia-worktrees/jep` and task worktrees. JEP's
environment, caches and data belong under `columbia-projects/jep`; its jobs
belong under `/var/lib/cloud-dev/columbia/projects/jep`.

Use `cloud-project --project jep submit --cwd PATH -- COMMAND ARGUMENTS` for
work that must survive chat disconnection. Use the same project selector for
`status`, `logs` and `cancel`. Keep credentials in the protected project
configuration and secret values out of Git, command arguments and reports.

Use explicit account, GCP project and zone arguments for cloud operations.
Administrator provisioning uses `pvd2112@columbia.edu`. Google Cloud jobs use
`dev-vm@pvd-dev-232.iam.gserviceaccount.com`, the existing dedicated account
attached to dev. SDKs and the Google Cloud CLI obtain short-lived credentials
from VM metadata. Keep job environments free of user ADC files and downloaded
service-account private keys. Initial grants are Compute Viewer on the
Columbia project; declare further resource-specific grants in the host profile.
Keep existing GPU experiments, checkpoints, checkouts and their IAP route in
place during development-host setup. Route Mac applications to the Mac and
company work to the existing Aether VM. The Aether connection can administer
the Columbia rollout through its established IAP route.

For native Mac CLI work, apply
[Connect Mac Relay](.agents/skills/connect-mac-relay/SKILL.md). Prefer
Columbia's `/opt/cloud-dev/columbia/bin/mac-command` for academic and personal
work; use Aether's relay for company work. Both routes are configured. Verify
the actual Mac hostname and user before using Mac paths. Connector file tools
refer to the VM. Maintain shared skills through the canonical
[agents collection](https://github.com/pvd232/agents/tree/main/skills) and its
[deployment workflow](https://github.com/pvd232/agents/blob/main/deploy/skill-sync/README.md).

Use the verified columbia-vm connection for development-host commands and
files. Preserve active work and report further acceptance checks from observed
evidence. This setup adds project environments to a shared host; all projects
on that host share its Linux-user and VM security boundary.
