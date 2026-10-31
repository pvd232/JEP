# Established project routes

Confirm these recorded targets against live inventory.

| Role | Target | Routing |
| --- | --- | --- |
| Academic CPU development | VM `dev`, project `pvd-dev-232`, `us-central1-a` | Intended `Columbia Dev VM`; administrator `pvd2112@columbia.edu`; Linux user `pvd2112_columbia_edu` |
| JEP GPU work | Existing JEP workers found through GCP inventory | Preserve observed project, zone, runtime and checkpoints; use attached workload account |
| Company development | `aether-dev-peter-vm`, project `aether-dev-peter`, `us-central1-a` | Existing `Aether Dev VM`; Linux user `peter_aetherlabs_live` |

The prepared Columbia workload account is
`dev-vm@pvd-dev-232.iam.gserviceaccount.com`, initially Compute
Viewer on that project. JEP GPU workers can share a dedicated JEP workload
account scoped to their actual artifact buckets and cloud tasks. Discover
existing identities before choosing an account.

The October 31, 2026 setup is recorded in
[JEP PR 16](https://github.com/pvd232/JEP/pull/16). Columbia deployment and GPU
migration require live verification. Aether's terminal connector and fresh-SDK
metadata authentication were verified. These records are not current health checks.

Use the VM connector or established IAP route for cloud work. Route native
Mac commands through the Mac connector, or the private reverse SSH relay
behind the existing authenticated Aether connection. See
[Mac relay](mac-relay.md) when a local connector is unavailable. Keep VM file
paths and Mac file paths distinct.
