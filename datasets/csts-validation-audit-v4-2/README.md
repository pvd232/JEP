# C-STS validation audit V4.2

This revision restores exactly four user-approved exclusions from V4.1. The user approved inclusion; the numerical grades below were assigned by the assistant. All other 1,826 disposition records and the previous 1,572 usable rows are preserved.

| Report item | Row | Condition | Rating |
|---|---|---|---|
| 13 | train_624 | number of beverages | 5 |
| 27 | train_1075 | amount of food | 3 |
| 59 | train_1809 | size of cow | 3 |
| 64 | train_2022 | type of room | 3 |

Final membership: **1576 usable**, **253 invalid**, **1 unresolved scope**, from 1,830 validation rows and 680 represented source groups. Original split and group identifiers are preserved.

The source report is [pinned here](https://github.com/pvd232/JEP/blob/a6a2628b4b51c95df119d4fedb227d30feb02c4d/training_outputs/csts_validation_exclusions_full_audit_v4_1_20261027.md). `changes.json` preserves complete before/after decisions. `labels.json` is the ID-and-label package. The [complete V4.2 audit](../../training_outputs/csts_validation_audit_v4_2_20261027.json) retains the historical review trail. Run the [paired reconstruction script](../csts-train-test-audit-v1/README.md) to produce `validation.json`; its bytes match the `usable_rows.json` staging hash in `verification.json`. The verification record maps staging names to their published or reconstructed locations and records coverage, preservation, and hashes. No model predictions were inspected for these decisions.

The user also confirmed the original exclusion rationales for the other 12 review-flagged entries before #64: #6, #7, #11, #14, #15, #16, #26, #28, #31, #50, #58, #63. These retain their V4.1 dispositions, including the unresolved age-scope case #58. The explicit four inclusion decisions take precedence. Exact confirmation records are retained in audit metadata.
