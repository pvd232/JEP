# Attached identity preflight

Resolve the VM's actual attached service account and compare it with the
project's declared workload account. Use the established connector to inspect
instance metadata and the installed identity probe. Report the principal,
token lifetime and permitted API status; keep token values out of output.

Run the job with the attached account and automatically refreshed SDK
credentials. Keep user logins, service-account private-key files and global
credential changes outside the job configuration. Preserve existing
credential files and scope environment changes to the submitted job.

When a required account or grant is missing, return its exact principal,
resource and permission. For a separately requested infrastructure setup,
use the project's reviewed
[cloud development implementation](https://github.com/pvd232/JEP/tree/infra/columbia-shared-devbox-20261031/infrastructure/cloud-dev).
That workflow owns provisioning, IAM review, service-account attachment,
recovery snapshots and VM lifecycle decisions.
