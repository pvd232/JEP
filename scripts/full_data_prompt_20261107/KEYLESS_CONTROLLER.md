# Columbia-only candidate collector

`collect_epochs.py` now requires an installed keyless runtime profile and defaults to **read-only inspection**. This candidate is not a migration of the currently running collector. No training code, model state, worker approval, active service or shutdown deadline is changed by this patch.

## Dependency and invocation

The companion Columbia runner/probe implementation supplies `project.workload_context()` and `probe_identity.py --workload`. The project profile must bind the approved assignment file, the attached service account and Mantra resource project. The collector rejects human-account manifests, altered assignment bytes, unexpected identities, local credential overrides and direct invocation outside the matching project environment.

After the runtime is separately installed and scoped Mantra access is granted, invoke from the candidate checkout using the existing runner:

```bash
cloud-project --project jep run -- python3 \
  /absolute/path/to/candidate/scripts/full_data_prompt_20261107/collect_epochs.py \
  --profile /etc/cloud-dev/columbia/projects/jep/profile.json \
  --approval /absolute/path/to/approved-new-controller-manifest.json \
  --source APPROVED_WORKER_SOURCE_COMMIT \
  --local /absolute/path/to/collector-receipts
```

These are explicit template paths and source revision. Without `--monitor`, this checks identity and instance status; it never assumes lifecycle ownership. `--monitor` is an explicit operation for an approved **new/quiescent** assignment after its prior collector has finished. There is no default auto-takeover and no fallback to a human account or another host.

The new code has no `--delete-verified-disks` option. Cleanup can stop a matching terminal assignment, but cannot delete its VM record or disks. Completed publication, a matching native terminal failure, or the owned deadline can authorize cleanup. Unexpected IAM, SSH, state-verification errors or interruption retain the worker and its independent deadline rather than stopping potentially active training.

The collector reads only artifact URIs beneath the configured prefix. Existing manifest/ACK/source/execution and SHA verification remains in force. A per-instance flock in the existing project state directory excludes duplicate local collectors even when their output directories differ. **This is not cross-host fencing:** it cannot neutralize the old collector's cleanup branch or prove a live handover is safe.

## Preserve current work

Do not install this candidate over an active collector, edit its approval, terminate its service or restart its worker. The current administrator collector may delete instances from its `finally` branch. Prefer waiting for its existing assignment to complete and independently verifying publication before selecting this candidate for a subsequent assignment. A future live handover would require its own reviewed coordination change; this patch does not add one.

## Tests

From the repository root, the focused offline command is:

```bash
python3 -m unittest tests.test_keyless_collector \
  tests.test_spot_lifecycle.CleanupTests \
  tests.test_spot_lifecycle.CompletionAndStorageRegressionTests.test_invalid_inherited_ack_never_permits_disk_cleanup \
  tests.test_full_data_prompt_lease tests.test_full_data_prompt_protocol -q
```

90 checks passed, including 24 new keyless collector tests. They cover inspect-by-default, account/profile/manifest binding, no lifecycle calls on unexpected failures, no disk deletion, exact stopped-state verification and local ownership exclusion. The larger legacy publication suite was not validated in this CPU environment because its pinned VIPER dependency is absent; no GPU/native-training integration result is claimed. Scientific source and optimizer configuration are unchanged.

The patch is prepared for later deployment. Real IAM, IAP/SSH, storage, renewal and safe-cutover acceptance remain required. The existing active collector and worker code have not been replaced.
