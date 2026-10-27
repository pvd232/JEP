# Validation label audit: calibration-policy repair, version 4.1

The preservation bug is repaired. **22 calibration-only rating changes were reverted to their pre-existing version-3 grades**, following the policy specified before the original version-4 scoring. Explicit canonical classes now determine preservation for all 397 focused decisions. The prior implementation matched free-text prefixes and missed some `numeric_calibration` and mixed-tag decisions.

The validation set retains **1,572 usable comparisons across 678 source groups**, **257 invalid cases** and **one excluded case with unresolved entity scope**. Every usable example ID stays identical to version 4. The three user-adjudicated anchors retain their ratings. Adopted scope and extracted values stay identical for the 22 repaired examples.

## Current validation results

| Saved model | Published version 4 | Repaired version 4.1 |
|---|---:|---:|
| Qwen ratings | 0.816461 | 0.818432 |
| Evidence then ratings | 0.816995 | 0.818755 |

These are Spearman correlations on the same 1,572 comparisons and saved predictions. Evidence's current advantage is **0.000324**, with paired source-group 95% interval **[-0.011019, +0.011372]** from 2,000 bootstrap draws.

Qwen normalized MSE is **0.056152**, and rating-scale MAE is **0.766282**. Evidence then ratings has MSE **0.055826** and MAE **0.753175**. The small answer-input cohorts retain their version-4 results.

## Preserved and corrected decisions

Relative to version 3, the current validation reference restores **62 exclusions**, changes **79 accepted numeric ratings** and excludes **three previously accepted cases**. All **29** earlier ambiguity exclusions have ratings. Current defensible calibration-grade preservations total **183**. Four genuine scope, value or category corrections within the repair review remain adopted, alongside the explicit root color-similarity decision.

The [22-case repair record](csts_validation_policy_repair_v4_1_20261027.json) includes complete captions, conditions, both ratings, adopted scopes and values, classifications, the 26-case review and merger implementation. The [current audit](csts_validation_audit_v4_1_20261027.json) preserves every source ID and historical vote. The [full comparison](csts_validation_comparison_v4_1_20261027.json) includes original-label metrics, matched cohorts, saved-model identities and paired intervals. The [point summary](csts_validation_point_summary_v4_1_20261027.json) provides compact results.

## Meaning of these results

This work revises **validation evaluation targets and checkpoint selection**. The 6,980 training examples, 2,620 Tu-reannotated test examples, saved weights and saved predictions retain their original versions. The existing held-out test result remains **0.788505**. New training, encoder inference and test evaluation in this update: **0**.

Confidence is stronger for concrete counting, role-scope and binary-scale corrections. Overall label accuracy has a limited evidence base: readers share one assistant model, three selected user adjudications supply the human anchors, and independent human error rates remain unmeasured. Score decreases can reflect corrected targets exposing model errors, harder restored examples, grading choices and residual annotation mistakes. A score decrease supplies no independent label-accuracy estimate.

The original version-4 performance was known when this implementation repair was reviewed. Per-comparison encoder predictions were withheld from repair classification. The 22 repair choices implement the earlier preservation policy and were fixed before recomputing their scores.

## Data and verification

The [validation profile](../configs/csts-qwen-audited-development.json) points to the [current validation rows](csts_validation_rows_v4_1_20261027.json). All other profile fields and training/test hashes remain fixed. The legacy profile filename is retained for compatibility.

The [ID-and-label package](../datasets/csts-validation-audit-v4-1/README.md) provides the revised labels and reconstruction instructions. Prior [version-4 results](https://github.com/pvd232/JEP/blob/a9c8619fa332d4ed1f4c594135805cec8d5a561c/training_outputs/csts_label_audit_report_20261026.md) and raw evidence remain archived.

Independent checks reproduce all **35** candidate/cohort views with SciPy and direct MSE. The exact package reconstruction example matches every usable row and its SHA-256.

Validation rows SHA-256: `f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9`.

Audit SHA-256: `845ed43db26743496fbd73dd4e6453d7dd18fb54002f3d8b2a07d3fd7655c412`.
