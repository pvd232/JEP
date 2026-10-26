# Completed C-STS development audit and saved-candidate update

**Version 2: every development example has a final disposition.** The final selection set contains **1,513 usable comparisons across 674 source groups**. There are **288 invalid cases and 29 cases excluded for ambiguous conditions**, with **zero pending cases**. The future validation profile points to this finalized set.

Correcting labels improves rank agreement for the same saved predictions on the same examples. For selected Qwen, Spearman rises from **0.800542 to 0.835069**, a correction-only lift of **0.034528**. Evidence then ratings rises from **0.794755 to 0.837784**, a lift of **0.043029**.

## Final labels and provenance

| Data | Label source | Role |
|---|---|---|
| Original training: 6,980 | LivNLP released training CSV, mixed human/LLM ratings | Existing training input |
| Original development: 1,830 | Same released training CSV | Historical development reference |
| Finalized development: 1,513 | Prediction-blind assistant-model audit consensus | Future checkpoint selection |
| Test: 2,620 | Tu human reannotations, excluding 214 invalid examples | Existing held-out test and error review |

These development labels are model-audited. The audit used isolated contexts of the same assistant model. Original dataset ratings remain preserved in the source inputs and archived metric views.

| Final development disposition | Examples |
|---|---:|
| Usable rating from initial reader agreement | 1,306 |
| Usable rating after review | 207 |
| Invalid condition or unavailable required information | 288 |
| Excluded because the comparison remains ambiguous | 29 |
| Total reviewed | 1,830 |
| Pending review | 0 |

**741** ratings changed among the **1,513** included examples. The cow/dog example `train_3985` remains rated 5 for number of animals.

The [full label audit](csts_development_blind_audit_v2_20261026.json) records all dispositions, rationales and final review votes. The [final 84-case decisions](csts_development_final84_decisions_20261026.json) retain complete captions, conditions, votes, dissent and explanations. The [review queue](csts_development_label_review_queue_20261026.json) is closed.

## How the final 84 cases were closed

The initial audit provided two independent blind judgments per example and review of disagreements. Version 2 preserves every one of its **1,491 usable ratings and 255 invalid decisions** exactly.

Three fresh blind contexts each reviewed the remaining 84 cases. They received captions, the condition, source identifiers and the frozen rubric. Original benchmark ratings, candidate predictions and prior reviewer judgments were withheld.

The closure rule was specified before candidate rescoring:

- A numeric rating requires at least two readers independently returning status `rated` with exactly the same value.
- An invalid disposition requires at least two readers returning status `invalid`.
- Every other configuration receives `excluded_ambiguous`, with a null rating and all dissent preserved.

The final 84 yielded **22 usable ratings, 33 invalid cases and 29 ambiguity exclusions**. Excluded cases contribute no numeric target to model selection.

The rubric follows [Tu, sections 3.2 and 3.3](https://aclanthology.org/2024.acl-long.64/): binary comparisons use 1/3/5, featureless conditions default to entity type, contextual inference needs direct support, and invalid conditions are excluded. Nonbinary grading follows the original [C-STS verification scale, Appendix C.2](https://aclanthology.org/2023.emnlp-main.345/).

The compressed [version-2 evidence](csts_development_blind_audit_evidence_v2_20261026.json) preserves blinded inputs, rubric, closure policy, three reader outputs and final decisions. It links initial audit evidence at its immutable source commit.

## Rank lift: correction and cohort filtering

All values below reuse the same saved encoder outputs. The middle and right columns use identical 1,513 example IDs.

| Saved model | Original labels, all 1,830 | Original labels, final 1,513 | Audited labels, final 1,513 | Correction-only lift |
|---|---:|---:|---:|---:|
| Selected Qwen ratings | 0.782575 | 0.800542 | 0.835069 | +0.034528 |
| Qwen evidence then ratings | 0.773647 | 0.794755 | 0.837784 | +0.043029 |

Selecting the usable cohort separately contributes 0.017967 to selected Qwen's correlation and 0.021108 to evidence then ratings. Label correction accounts for the additional lift in the final column.

Numerical calibration metrics also change. On the same 1,513 examples, selected Qwen's normalized MSE increases from **0.034177 to 0.050982**, and rating-scale MAE increases from **0.580031 to 0.726299**. Evidence then ratings has audited MSE **0.050394** and MAE **0.713628**. Rank lift and absolute score errors are reported separately.

## Re-evaluation of saved candidates

Twenty-seven full-development score maps were evaluated on the same finalized development set.

| Saved encoder | Audited development Spearman, n=1,513 |
|---|---:|
| Qwen evidence then ratings | 0.837784 |
| Selected Qwen ratings | 0.835069 |
| Same-passage control | 0.833857 |
| Qwen ratings pretraining checkpoint | 0.829774 |
| Earlier Qwen LoRA | 0.822322 |

Evidence then ratings exceeds selected Qwen by **0.002714**. Its paired source-group bootstrap 95% interval is **[-0.008891, +0.014437]**.

| Matched audited answer cohort | Original captions | Frozen answers | Adapted answers |
|---|---:|---:|---:|
| Retained generated-answer diagnostic, n=55 | 0.813272 | 0.763026 | Unavailable |
| Answer-input LoRA trial, n=25 | 0.820347 | 0.764370 | 0.800243 |

These values are Spearman correlations. Generated answers differ from original captions by -0.050246, with 95% interval [-0.185206, +0.069022]. Adapted answers differ by -0.020105, with interval [-0.115548, +0.057211]. Adapted-answer normalized MSE is 0.042388 on the 25-example cohort, compared with original-caption MSE 0.044010.

The [full comparison](csts_audited_candidate_comparison_v2_20261026.json) preserves original-label views, matched IDs, exclusions, saved-model identities and three 2,000-draw source-group intervals. The [point summary](csts_audited_candidate_point_summary_v2_20261026.json) includes an exact filtering-versus-correction decomposition for each candidate.

Independent checks recomputed the closure policy for all 84 cases, verified all 1,746 frozen initial decisions, and reproduced 35 cohort/candidate metric views using SciPy and direct MSE calculations.

## Tu-reannotated test review

The selected encoder's existing score on the **2,620 Tu-reannotated test examples remains 0.788505**. Those source ratings and saved predictions remain fixed.

The error review covers all 2,620 comparisons, 1,140 distinct condition strings and 12 descriptive semantic families. There are 936 discrepancies of at least one rating point and 136 of at least two points. Spatial conditions have 160/341 one-point discrepancies (46.92%); quantity/count has 167/474 (35.23%); entity type has 186/652 (28.53%). Presence/absence has 44/68 (64.71%).

Five residual reference-label contradictions are flagged for inspection, including two captions explicitly describing kitchens with a published rating of 1 for room type. Published test labels remain intact. Detailed statistics and flags: [test-review data](csts_clean_test_error_review_20261026.json). Full source rows and saved predictions: [sealed export](csts_qwen_selected_clean_test_export.json).

## Future checkpoint selection

The [Qwen development profile](../configs/csts-qwen-audited-development.json) now points validation at the separately saved [1,513 finalized model-audited rows](csts_development_model_audited_rows_v2_20261026.json). Training and human-reannotated test inputs retain their existing hashes. Original experiment configurations preserve their historical data versions.

Final development SHA-256: `8a5b68f165ec8d914bd2b3accbb6f059f573ca5fe3bd122e75acab33aa68ce35`.

Saved weights and predictions were reused throughout this update. No training or encoder inference was launched.
