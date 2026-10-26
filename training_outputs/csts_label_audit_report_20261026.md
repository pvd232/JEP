# C-STS development scope audit and saved-model update

**Version 4: exhaustive scope review completed.** All **1,830** development comparisons were reviewed. The current set has **1,572 usable comparisons across 678 source groups**, **257 invalid cases**, **one excluded case with ambiguous entity scope**, and **zero pending cases**.

## What changed from version 3

| Decision change | Comparisons |
|---|---:|
| Previously excluded, restored with a rating | 62 |
| Accepted numeric rating corrected | 101 |
| Previously accepted, now excluded | 3 |
| Total changed dispositions or ratings | 166 |

All **29** prior ambiguity exclusions now have ratings. Another **33** cases were restored from the invalid set. The one current ambiguity exclusion, `train_1693`, has a child and an adult as competing referents for the singular person-age condition. The other new exclusions are `train_3209` and `train_7271`.

The [166-case change record](csts_development_scope_changes_v4_20261026.json) includes both complete captions, condition, original rating, version-3 rating, current rating, adopted scope, extracted values and rationale. The [full current audit](csts_development_blind_audit_v4_20261026.json) preserves all 1,830 dispositions and historical votes. [Version 3](https://github.com/pvd232/JEP/blob/d1cff0f531e3994be6e21db63ed20b0b8823868e/training_outputs/csts_label_audit_report_20261026.md) remains archived.

## Review method and label provenance

Six isolated assistant contexts independently reviewed every source comparison, recording the relevant entity or role and extracted feature values before rating. Original supplied labels, prior model-audit labels and encoder scores were withheld during this pass. Three user-adjudicated anchors remained fixed: `train_72`=5, `train_7753`=1, `train_8859`=5.

Focused readers resolved **397** disagreements or scope flags using the captions, rubric and shuffled interpretation options. Disagreement alone supplies no ambiguity exclusion. Each ambiguity exclusion requires concrete competing referents or feature interpretations. Missing precision can support 3 when both captions provide recoverable feature values. A wholly absent requested attribute remains invalid under Tu. The validity clarification was applied to all first-pass outputs before final adjudication.

The final checks preserved **161** existing grades where the difference concerned defensible calibration, and recorded **16** explicit scope/context/color decisions. Root checks adopted ordinary contextual inferences consistently, including Tu's snowy-ground weather example. All adopted scopes and extracted values match the final decisions.

The [compressed evidence archive](csts_development_scope_audit_evidence_v4_20261026.json) preserves inputs, rubric, review policy, six first-pass reviews, 397 focused decisions, quality checks and the semantic freeze. The frozen audit hash was set before rescoring. These labels are assistant-model judgments with three user-adjudicated anchors. Independent human validation remains a subsequent quality estimate.

## Current saved-model results

All metrics reuse saved predictions. Training updates and new encoder inference: **0**.

| Saved model | Original labels, all 1,830 | Original labels, same 1,572 | Current labels, same 1,572 | Label-correction lift on same rows |
|---|---:|---:|---:|---:|
| Selected Qwen ratings | 0.782575 | 0.797278 | 0.816461 | +0.019183 |
| Qwen evidence then ratings | 0.773647 | 0.790045 | 0.816995 | +0.026950 |

| Candidate | Current development Spearman |
|---|---:|
| Qwen evidence then ratings | 0.816995 |
| Selected Qwen ratings | 0.816461 |
| Qwen ratings pretraining checkpoint | 0.811842 |
| Same-passage control | 0.811082 |
| Earlier Qwen LoRA | 0.801630 |

Evidence then ratings exceeds selected Qwen by **0.000533**, with paired source-group bootstrap 95% interval **[-0.011027, +0.011612]**, using 2,000 draws.

Selected Qwen normalized MSE is **0.055850**, and rating-scale MAE is **0.762603**. Evidence then ratings has MSE **0.055503** and MAE **0.749076**. Original-label metrics and all candidate views remain available in the full comparison.

## Why correlation decreased from version 3

The review changes reference targets and usable-example membership. The **1,510** comparisons included in both versions isolate the target revisions:

| Model, same 1,510 comparisons | Version-3 labels | Version-4 labels |
|---|---:|---:|
| Selected Qwen ratings | 0.833041 | 0.823071 |
| Evidence then ratings | 0.836027 | 0.824299 |

Adding the 62 restored comparisons then gives the current 1,572-row values above. Model weights and predictions remain fixed throughout these comparisons.

## Answer-input diagnostics

| Current matched cohort | Original captions | Generated or frozen answers | Adapted answers |
|---|---:|---:|---:|
| Retained diagnostic, n=58 | 0.798101 | 0.750420 | Unavailable |
| Answer-input LoRA, n=25 | 0.788134 | 0.731556 | 0.762812 |

These are Spearman values. The full report includes paired source-group intervals for each diagnostic. Independent SciPy and direct-MSE checks reproduced all **35** candidate/cohort views.

## Data and validation profile

The [validation profile](../configs/csts-qwen-audited-development.json) points to [1,572 version-4 development rows](csts_development_model_audited_rows_v4_20261026.json). The existing 6,980-row training split and 2,620-row Tu-reannotated test split retain their prior paths, counts and hashes. The selected model's existing human-reannotated test Spearman remains **0.788505**.

The [ID-and-label release package](../datasets/csts-development-audit-v4/README.md) supplies all 1,830 dispositions, source revision, group IDs and reconstruction instructions. It distributes annotation IDs and labels while leaving source captions with their upstream distributors. Full-caption audit artifacts remain in this private project repository.

Usable development SHA-256: `87af4e9aee2513b2e948ad8669027f7c059c2cba00c64c054893d03bcf370e24`.

Frozen audit SHA-256: `e8ffe2bd973ce96a51a1f72b03e0d680bfdeb6e3932a19127f6d32cf4ef5a5ab`.
