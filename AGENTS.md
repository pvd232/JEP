# JEP execution

The intended persistent development host is `dev` in GCP project `pvd-dev-232`,
zone `us-central1-a`, account `pvd2112@columbia.edu`, Linux user
`pvd2112_columbia_edu`. Its connection name is **Columbia Dev VM**. Read
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
Keep existing GPU experiments, checkpoints, checkouts and their IAP route in
place during development-host setup. Route Mac applications to the Mac and
company work to the existing Aether VM. The Aether connection can administer
the Columbia rollout through its established IAP route.

Until Columbia deployment is accepted, preserve and use the established
authorized execution routes. Report each acceptance check from observed
evidence. This setup adds project environments to a shared host; all projects
on that host share its Linux-user and VM security boundary.
