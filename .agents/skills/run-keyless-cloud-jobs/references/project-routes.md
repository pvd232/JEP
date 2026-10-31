# Established project routes

Confirm these recorded targets against live inventory.

| Role | Target | Routing |
| --- | --- | --- |
| Academic CPU development | VM `dev`, project `pvd-dev-232`, `us-central1-a` | Installed `columbia-vm` plugin (Columbia Dev VM); administrator `pvd2112@columbia.edu`; Linux user `pvd2112_columbia_edu` |
| JEP GPU work | Existing JEP workers found through GCP inventory | Preserve observed project, zone, runtime and checkpoints; use attached workload account |
| Company development | `aether-dev-peter-vm`, project `aether-dev-peter`, `us-central1-a` | Existing `Aether Dev VM`; Linux user `peter_aetherlabs_live` |

The attached Columbia workload account is
`dev-vm@pvd-dev-232.iam.gserviceaccount.com`, initially Compute
Viewer on that project. JEP GPU workers can share a dedicated JEP workload
account scoped to their actual artifact buckets and cloud tasks. Discover
existing identities before choosing an account.

The October 31, 2026 setup is recorded in
[JEP PR 16](https://github.com/pvd232/JEP/pull/16). Columbia's direct plugin passed hostname/user, file write/read and tunnel
automatic-recovery checks. Its ten-minute durable project job succeeded. The
JEP L4 worker has its dedicated account attached and remains stopped; verify
guest credentials at its next intentional start. Check current health before work.

Use the VM connector or established IAP route for cloud work. Route native
Mac commands through the Mac connector, or the private reverse SSH relay
behind the existing authenticated Aether connection. See
[Mac relay](mac-relay.md) when a local connector is unavailable. Keep VM file
paths and Mac file paths distinct.
