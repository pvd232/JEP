# Full-data prompt training results

All 15 LoRA fits finished. Their 77 checkpoint archives (35,921,745,920 bytes)
and all three input files passed independent cloud byte verification.
Both Spot VMs and both boot disks were then deleted using the controller's
attached service account. The held-out test remains unopened. Patience is 1.

| Prompt arm | Seeds | Mean validation Spearman | SD across seeds |
| --- | ---: | ---: | ---: |
| A_condition_first | 5 | 0.874465 | 0.001630 |
| B_order_only | 5 | 0.873737 | 0.002648 |
| C_case_inspired | 5 | 0.875097 | 0.001532 |

Scores use validation-selected checkpoints. These are validation results; the
standard deviation describes five initializations on the same validation set.
[Per-fit scores](validation_scores.csv) retain selected and completed epochs.
[Frozen selections](frozen-selections.json) retain model hashes and native references.

Taiwan's final VIPER publication was verified at 12:38 p.m. Eastern; Seoul's at
1:10 p.m. The CPU controllers had lost their personal Google login at 10:34 a.m.
and failed to collect the completed work. Training continued independently under
the workers' attached service accounts. Both idle VMs were stopped after access
was restored; independent archive verification finished at 4:53 p.m., followed by
VM and disk deletion at 4:57 p.m. No training was restarted during this recovery.

The controller now has permanent project-wide Owner and IAP access on Mantra,
and Storage Admin on the VIPER bucket, as explicitly requested. It uses metadata
credentials with automatic refresh. There are no per-run IAM conditions or expiry.

- [Archive hashes and cloud references](cloud-archive-inventory.json)
- [Verified input references](input-cloud-proofs.json)
- [Cleanup receipts](cleanup.json)
- [Controller access receipts](controller-access.json)
- [Metadata authentication preflight](controller-metadata-preflight.json)
- [Failure diagnosis and repair](../../plans/full_data_prompt_20261107/controller-repair-20261108/README.md)

Execution source: `83467f756d1d10e9c1f3183d9242cea4424e1ce4`.
Scientific training source: `9b163a100362580f99722eecc63895420ecec3b1`.
Protocol SHA-256: `0aee2f8aece3e89ff12223fe40a54fb632305339f240475362212c432fd68a11`.

[Live status](https://github.com/pvd232/JEP/blob/monitor/full-data-prompt-20261107/plans/full_data_prompt_20261107/live-status.md)
