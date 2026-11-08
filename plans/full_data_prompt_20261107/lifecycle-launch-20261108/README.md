# East Asia Spot deployment — 8 November 2026

[Live training status](https://github.com/pvd232/JEP/blob/monitor/full-data-prompt-20261107/plans/full_data_prompt_20261107/live-status.md) updates every five minutes. The observations below are historical launch evidence.

Both L4 workers were observed running native training with active VIPER publishers.
The independent CPU controllers are running with verified-publication cleanup.

| Worker | Observed placement | Fit in the deployment record |
| --- | --- | --- |
| worker1 | Seoul, asia-northeast3-a | B_order_only, seed 7, epoch 2 |
| worker2 | Taiwan, asia-east1-b | B_order_only, seed 8, epoch 1 |

See [runtime evidence](runtime-evidence.json) for observation times, immutable VM
and GPU identities, utilization, active services and controller job IDs.
The running execution source is 83467f756d1d10e9c1f3183d9242cea4424e1ce4.
Its ten genuine, independent source reviews are retained in [reviews](reviews/)
and normalized in [verified-reviews.json](verified-reviews.json).

Worker1 reused the five completed Arm A epochs and 950 updates, selecting epoch 4.
The selected native checkpoint and runtime were verified during preflight.
The held-out test remains sealed for evaluation.

Each [worker1 approval](approval-worker1.json) and
[worker2 approval](approval-worker2.json) binds actual placement, source, protocol,
execution identity, provider runtime envelope and cloud namespace. VIPER uploaded
and streamed hash verification over the canary and opaque input files during
preflight. Each worker has a separate durable publisher with bounded queues.

The CPU controllers verify every cloud generation before deleting an exact owned
VM and boot disk. A failed or unverified run retains its recovery disk.
The provider independently deletes compute at its 23-hour limit.
The [bootstrap cleanup receipt](bootstrap-cleanup.json) records deletion of the
obsolete Tokyo clone, its disk, the temporary snapshot and unused namespace grants.

The allocator follow-up handles GCP returning RUNNING from its server-side wait:
it keeps admission locked and polls the recorded operation within a bounded budget.
Its 24 focused [checks](allocator-checks.json) passed. The running training workers
retain their reviewed execution source; the follow-up changes allocation only.

The reusable skill is published and installed:
[Run East Asia Spot Training](https://github.com/pvd232/agents/tree/9d313eddd45ab8c8aaaeff90479e8bada08c8c04/skills/run-east-asia-spot-training).
It covers independent fits and one synchronized LoRA adapter across GPUs.
Structure, prose and native offline forward checks passed. The user explicitly
approved publication with the full automated release check unavailable during sandbox bootstrap.

The first new native checkpoint, B_order_only seed 7 epoch 1, was asynchronously
published and streamed hash-verified through VIPER at 06:58:46 UTC. Epoch 2 had
already started at 06:57:44 UTC. The [native receipt](first-native-viper-ack.json)
and [training events](worker1-first-epoch-events.json) retain that observed overlap.
