# GCP CPU and GPU setup

Use the reviewed [JEP implementation](https://github.com/pvd232/JEP/tree/infra/columbia-shared-devbox-20261031/infrastructure/cloud-dev).
Inspect and pin its revision for a rollout.

1. Collect live instance `name`, `selfLink`, `zone`, `status`, `disks`,
   `serviceAccounts` and `guestAccelerators`, using explicit administrator
   account, project and zone. Inspect active work.
2. Use `profiles/columbia.json` for the recorded academic development host.
   For a GPU worker, run `scripts/make_gpu_profile.py --help` from this skill
   and generate a profile from observed inventory and the verified Linux user.
   The generator makes no cloud changes.
3. Review `tools/identity.py --profile PROFILE plan`. Declare IAM grants for
   observed resources. Grant a specific artifact bucket its required object
   role when checkpoint writes need it. Apply only grants authorized for the
   named resource, following platform approval requirements. Job accounts need
   no IAM-admin grant.
4. Apply with `tools/identity.py --profile PROFILE apply`. For a running idle
   host whose identity must change, use `--allow-restart` after inspecting
   active work. The helper snapshots disks, checks durable/GPU jobs and records
   prior account/scopes. Preserve a stopped worker's state.
5. Use `tools/deploy.py ... apply` on the development host to install pinned
   terminal/job tooling and register its own MCP tunnel. On GPU workers,
   retain the existing project runtime and compatible job runner. Install the
   full terminal stack only when requested and supported: its current baseline
   is Ubuntu 24.04 x86_64 with Python 3.12+.
6. Run `implementation/probe_identity.py --profile PROFILE` on the target.
   Verify SDK selection in a clean configuration and persistent job retrieval.

Use an already authorized administrator for initial setup. Required access
depends on existing IAM: service-account creation/inspection, assignment of
declared resource roles, `iam.serviceAccounts.actAs`, VM identity/start/stop
operations and snapshot operations when used. Report missing grants from a
concrete denial or verified IAM inventory. Jobs then use the attached account.

Official references:

- [ADC](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
- [VM accounts and scopes](https://docs.cloud.google.com/compute/docs/access/service-accounts)
- [Change the attached account](https://docs.cloud.google.com/compute/docs/instances/change-service-account)
