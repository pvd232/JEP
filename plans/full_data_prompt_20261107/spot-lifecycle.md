# East Asia Spot training lifecycle

The controller resumes the existing full-data prompt study. Its model, loss,
training data, validation data, batch size, optimizer and patience rule remain
bound to the scientific source revision. Controller-only revisions record their
actual execution source separately. Completed native epochs remain reusable.

## Components

- `scripts/full_data_prompt_20261107/deploy_spot.py` discovers L4 zones, queries
  capacity and attempts bounded Spot allocation from a prepared snapshot.
- `csts_pilot/full_data_prompt_lease.py` validates the manifest's current placement,
  immutable instance ID, GPU UUID, execution ID and independent poweroff deadline.
- `csts_pilot/full_data_prompt_worker.py` runs assigned seeds under a GPU lock,
  seals local generations and resumes only through an exact prior-state digest.
- `csts_pilot/full_data_prompt_uploads.py` publishes sealed archives through VIPER
  under the attached workload account, independently of optimizer execution.
- `scripts/full_data_prompt_20261107/collect_epochs.py` observes the manifest's
  workers and deletes exact task resources after verified export. Failure retains
  the recovery disk. The job's held-out test remains locked.

## Allocation

Use the existing administrator connection with explicit project and account.
Provide `deploy_spot.py` with `--snapshot`, `--name`, `--service-account`,
`--project`, `--account`, `--journal`, and preferred `--regions`. `--plan-only`
records discovered candidates without creating a VM. Actual allocation remains
Spot and stays within the requested concurrency, attempts and 23-hour envelope.

Use the returned placement rather than changing code for another zone. Bind its
actual GPU UUID and guest deadline before launch. Record the task-owned boot disk
ID and keep boot auto-delete disabled until publication verifies recovery bytes.
A ten-minute provider bootstrap deadline deletes an idle new VM if launch does
not complete. Extend that deadline to the approved run envelope only after
observing the training service and actual GPU work.

## Launch and recovery

Freeze and review the execution source, verify the scientific compatibility
boundary, and validate the protocol and exact ten-review receipts. Save an
approval record containing placements, controller account, VIPER owner/workspace
and original scientific source. A resumed worker additionally binds its prior
state digest, source and execution ID. Preserve that original state file.

Run the worker and uploader in separate bounded systemd services using the
existing pinned project environment. Start the lifecycle monitor on the durable
CPU controller. Before claiming deployment, observe actual optimizer activity and
a real VIPER publication and hash-verification receipt.

Each epoch seals model, optimizer, scheduler, RNG, predictions and trace into a
local archive. Training continues during VIPER publication, with backpressure at
two unverified generations. Completion flushes every generation before cleanup.
A failed transfer keeps the native archive. An interrupted native attempt requires
reconciliation before another attempt can start. Never repeat completed training
to fix a downstream verifier or report.

## Cleanup

The CPU controller deletes only task-labelled, immutable-ID-matched instances.
It preserves disks on failure. With `--delete-verified-disks`, successful final
VIPER publication also permits deleting the recorded, detached task boot disk.
Delete temporary bootstrap snapshots after the new worker is verified. Preserve
historical source VMs, snapshots and artifact-retention settings.

Independent seed workers remain the current study's execution mode. A synchronized
multi-GPU fit of one adapter requires its own verified distributed entrypoint and
unchanged scientific configuration; the reusable Spot training skill covers that
separate topology.
