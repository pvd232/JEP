# Completed C-STS development audit and saved-candidate update

**Version 3: user adjudication of three displayed cases.** The development set contains **1,513 usable comparisons across 674 source groups**, with **288 invalid cases, 29 ambiguity exclusions and zero pending cases**.

## User adjudication

| Source ID | Condition | Version 2 | Current rating | User decision |
|---|---|---:|---:|---|
| train_72 | type of meal | 5 | 5 | Pie and cake are interpreted as desserts |
| train_7753 | angle of ground | 1 | 1 | Sidewalk is interpreted as level ground, stairs as inclined |
| train_8859 | number of riders | 1 | 5 | Each caption describes one active wave rider |

Exactly one numeric label changed: `train_8859`, from 1 to 5. Every example ID, group, inclusion decision and other numeric rating stays fixed. The three user decisions followed disclosure of the existing ratings and reader votes.

The [user adjudication record](csts_development_user_adjudications_v3_20261026.json) supplies current decision precedence. The [version-3 audit](csts_development_blind_audit_v3_20261026.json) retains historical model-reader votes and the previous rider-count rationale. [Version 2](https://github.com/pvd232/JEP/blob/769114a4967de1cb8fbb26709a13119e01df1cff/training_outputs/csts_label_audit_report_20261026.md) preserves the prior published results.

## Label provenance

| Data | Labels | Role |
|---|---|---|
| Training, 6,980 | LivNLP released training CSV, mixed human/LLM labels | Existing training input |
| Original development, 1,830 | Same released training CSV | Historical reference |
| Current development, 1,513 | Prediction-blind model audit followed by user adjudication of three displayed cases | Future checkpoint selection |
| Test, 2,620 | Tu human reannotations after invalid-case exclusions | Existing test reference |

The initial model audit used isolated contexts of the same assistant model. Its rubric, blind inputs, raw votes, rationales, disagreement review and exclusion policy remain archived in [version-2 audit evidence](csts_development_blind_audit_evidence_v2_20261026.json). User review is separately identified and unblinded.

The initial 1,306 reader agreements and 207 adjudicated usable cases retain their inclusion statuses. The audit now differs from original ratings on **742 of 1,513** usable comparisons. Original source labels remain preserved.

The rubric follows [Tu sections 3.2 and 3.3](https://aclanthology.org/2024.acl-long.64/) and the original [C-STS verification scale, Appendix C.2](https://aclanthology.org/2023.emnlp-main.345/).

## Saved predictions and label correction

The middle and right columns use the same 1,513 comparisons and saved predictions.

| Saved model | Original labels, all 1,830 | Original labels, same 1,513 | Current labels, same 1,513 | Correction-only lift |
|---|---:|---:|---:|---:|
| Selected Qwen ratings | 0.782575 | 0.800542 | 0.832619 | +0.032077 |
| Qwen evidence then ratings | 0.773647 | 0.794755 | 0.835354 | +0.040600 |

Selected Qwen normalized MSE is **0.051485**, with rating-scale MAE **0.728315**. Evidence then ratings has MSE **0.050913** and MAE **0.715706**. Original-label values on those same rows are retained in the full comparison.

## Saved candidate comparison

Twenty-seven full-development saved candidates were rescored.

| Candidate | Current development Spearman |
|---|---:|
| Qwen evidence then ratings | 0.835354 |
| Selected Qwen ratings | 0.832619 |
| Same-passage control | 0.831498 |
| Qwen ratings pretraining checkpoint | 0.827459 |
| Earlier Qwen LoRA | 0.819768 |

Evidence then ratings exceeds selected Qwen by **0.002735**, with a paired source-group bootstrap 95% interval of **[-0.008891, +0.014438]** using 2,000 draws.

The rider comparison occurs outside the retained-answer and answer-input trial cohorts. Their scores stay fixed:

| Matched cohort | Original captions | Frozen answers | Adapted answers |
|---|---:|---:|---:|
| Retained diagnostic, 55 usable | 0.813272 | 0.763026 | Unavailable |
| Answer-input LoRA, 25 usable | 0.820347 | 0.764370 | 0.800243 |

The [full version-3 comparison](csts_audited_candidate_comparison_v3_20261026.json) preserves original-label metrics, coverage, all saved candidate identities, exclusions and paired intervals. The [point summary](csts_audited_candidate_point_summary_v3_20261026.json) decomposes filtering and label correction.

Independent checks reproduced **35 cohort/candidate views** with SciPy Spearman and direct MSE. A separate recomputation matched both leading candidates after the single correction.

## Validation profile and preserved artifacts

The [validation profile](../configs/csts-qwen-audited-development.json) points to [version-3 development rows](csts_development_model_audited_rows_v3_20261026.json).

Development SHA-256: `dfb3a12f25a77ac4c0ff2f472cef6c0d1e22344f6e847bc4da0ae6d6ebc8aa80`.

Training and test paths, hashes and counts stay fixed. The selected encoder's existing Tu-reannotated test score stays **0.788505**. All previous audit versions and raw model-reader decisions remain archived.

This update reuses saved predictions. Training updates and new encoder inference: **0**.
