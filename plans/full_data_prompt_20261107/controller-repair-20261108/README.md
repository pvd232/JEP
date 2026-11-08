# Controller failure and repair

All 15 training fits finished successfully. The 77 checkpoint archives and all
three input files passed independent cloud byte verification. Both task VMs and
both boot disks were deleted at 4:57 p.m. Eastern using the controller service
account. [Results and receipts](../../../training_outputs/full_data_prompt_20261108/README.md)
retain the validation-selected models' hashes and cloud references.

## What failed

At 10:34 a.m. Eastern both CPU controllers lost their personal Google login.
The GPU workers continued training and publishing under their own attached
service accounts. Taiwan's final publication was verified at 12:38 p.m.;
Seoul's at 1:10 p.m. The failed controllers left completed VMs running idle.

The reporter incorrectly treated controller exceptions as fresh evidence that
workers had stopped. It then exited successfully at 10:38 a.m. because both
controllers had returned error records. [Failure evidence](failure-evidence.json)
retains exact job IDs, timestamps, errors and prior-state hashes.

The original Taiwan Spot preemption at 6:03 a.m. was a separate provider event.
Its preserved disk was resumed at 9:35 a.m. Completed fits and the sealed
epoch-1 checkpoint were reused.

## What changed

- Failed observation no longer authorizes resource deletion or reports a
  training failure. Transport errors have bounded retries; authentication,
  authorization and ownership failures stop the relevant operation.
- Cleanup failures retain the original worker exception and their own receipt.
- The reporter requires successful collection and cleanup receipts before closing.
  Stale progress remains explicitly marked and does not produce an ETA.
- Unattended lifecycle commands require the CPU host's attached service account,
  use isolated SDK configuration and clear credential overrides. The reporter
  uses the same environment.

Scientific source, model, data and patience remained unchanged. Current controller
repair validation passed 33 lifecycle and regression checks; the nine authentication
and reporter cases passed again after the environment update. See
[full checks](focused-checks.log) and [latest authentication checks](latest-auth-checks.log).
Production metadata authentication, archive reads, VM deletion and disk deletion
also succeeded.

## Persistent controller access

The user explicitly requested project-wide persistent access. Applied grants to
`767812446290-compute@developer.gserviceaccount.com` are:

| Resource | Unconditional grant |
| --- | --- |
| Mantra project `mantra-477901` | `roles/owner` |
| Mantra project `mantra-477901` | `roles/iap.tunnelResourceAccessor` |
| VIPER bucket `mantra-mlfg-prod-uscentral1-8e7a` | `roles/storage.admin` |

These grants have no per-run access expiry. Use the attached identity and metadata
refresh for future workload provisioning, observation, publication and cleanup.
[Grant receipts](controller-access-plan.json) retain the applied state.

[bootstrap_controller_access.py](../../../scripts/full_data_prompt_20261107/bootstrap_controller_access.py)
is the one-time administrator setup. Future jobs reuse the existing grants.
Pass the attached account to the allocator's `--account` option and record it as
`controller_account` in the launch manifest. GPU workers continue using
`jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com`.

[collect_epochs.py](../../../scripts/full_data_prompt_20261107/collect_epochs.py)
keeps the original allocation deadline when collection restarts. The allocator
selects available East Asia zones under the approved manifest. Fully automatic
replacement after Spot preemption remains future work.

[Live status](https://github.com/pvd232/JEP/blob/monitor/full-data-prompt-20261107/plans/full_data_prompt_20261107/live-status.md)
