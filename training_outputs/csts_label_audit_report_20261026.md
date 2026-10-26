# C-STS label audit and corrected error review

The error review now uses the 2,620 examples from Tu's published human reannotation. Development-set labels were independently reviewed in blinded assistant contexts, and all saved model candidates were rescored on the resulting usable development comparisons. Existing encoder predictions were reused. Encoder inference, generation and training were unnecessary.

## Label provenance

| Data | Source | Role |
|---|---|---|
| Original training: 6,980 | LivNLP released training CSV; mixed human/LLM ratings | Existing model training |
| Original development: 1,830 | Same released training CSV | Historical checkpoint selection and earlier error review |
| Test: 2,620 | Tu human reannotations, excluding 214 invalid rows | Corrected error review; original test ratings preserved |
| Model-audited development: 1,491 | Two blind assistant readers per example, with adjudication of disagreements | New development profile and retrospective candidate comparison |

The published Tu reannotation contains residual contradictions. Five concrete cases are flagged in the review, including two captions explicitly describing kitchens with a reference rating of 1 for room type. These flags are qualitative review judgments. The published test ratings and original test metric remain unchanged.

## Review on Tu's 2,620 examples

Selected encoder: `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`.

| Metric | Value |
|---|---:|
| Spearman | 0.788505 |
| MSE on normalized score scale | 0.0707633 |
| Mean absolute error on rating scale | 0.860749 |
| Absolute rating discrepancy at least 1 point | 936 / 2,620 (35.73%) |
| Absolute rating discrepancy at least 2 points | 136 / 2,620 |
| Reversed condition contrasts | 82 / 1,044 |
| Distinct condition strings | 1,140 |
| Conditions occurring once | 894 |

Large semantic families show different discrepancy patterns: spatial conditions have 160/341 discrepancies of at least one point (46.92%); quantity/count has 167/474 (35.23%); entity type has 186/652 (28.53%). Presence/absence has 44/68 (64.71%). These are descriptive rates against the published references. The browser retains complete captions, conditions and exact reference/prediction values.

The semantic taxonomy has 12 descriptive families. All 1,140 condition strings were covered; classification used condition wording independently of prediction errors. The smallest families have few observations. Rating distributions are shown alongside errors to make differences in label mix visible.

Full statistics and flagged references: [clean-test review data](csts_clean_test_error_review_20261026.json). Source rows and saved predictions: [sealed export](csts_qwen_selected_clean_test_export.json).

## Blind development audit

Every development example received two independent assistant judgments. Four isolated reader contexts each handled one of two source-pair partitions. Original ratings, Qwen predictions and other readers' outputs were withheld. Three adjudication batches covered 327 disputed cases. The readers used the same assistant model in separate contexts. These are model-generated audit labels.

The rubric follows [Tu, sections 3.2 and 3.3](https://aclanthology.org/2024.acl-long.64/): binary equality comparisons use 1/3/5; conditions lacking a feature default to entity type; inference requires direct contextual support; invalid conditions are excluded. Nonbinary grading follows the original [C-STS verification scale, Appendix C.2](https://aclanthology.org/2023.emnlp-main.345/).

| Disposition | Examples |
|---|---:|
| Reader agreement on a usable rating | 1,306 |
| Usable rating after adjudication | 185 |
| Invalid condition or unavailable required information | 255 |
| Interpretation remains unresolved | 84 |
| Total reviewed | 1,830 |

The usable set has **1,491 comparisons across 671 source groups**. **728** included ratings changed from their released training-label values. Exact counts use 1/3/5 throughout. The cow/dog example `train_3985` receives 5 for number of animals in the audited labels.

Audit rows, rationales and provenance: [label audit](csts_development_blind_audit_20261026.json). The compressed [audit evidence](csts_development_blind_audit_evidence_20261026.json) preserves blinded inputs, rubric, four reader outputs and all adjudications. The [84-case review queue](csts_development_label_review_queue_20261026.json) withholds original labels and model scores.

## Re-evaluation of saved candidates

Twenty-seven full-development prediction maps were rescored on the same 1,491 usable examples; 26 have defined Spearman values, and the mean-pooling candidate is unranked. These are saved candidate checkpoints, rather than a reselection across every historical epoch. Original-label metrics remain available for the full historical cohort and for the same usable rows. Partial answer-input studies are compared on matched usable subsets.

| Saved encoder | Model-audited development Spearman, n=1,491 |
|---|---:|
| Qwen evidence then ratings | 0.841791 |
| Selected Qwen ratings | 0.837642 |
| Same-passage control | 0.836233 |
| Qwen ratings pretraining checkpoint | 0.832548 |
| Earlier Qwen LoRA | 0.824816 |

Evidence then ratings exceeds selected Qwen by 0.004150; paired source-group bootstrap 95% interval is **[-0.006402, +0.014903]**. This is a narrow point-ranking change. The original 0.788505 result remains the selected Qwen's score on Tu's 2,620 human-reannotated test examples.

| Matched model-audited cohort | Original captions | Frozen answers | Adapted answers |
|---|---:|---:|---:|
| Retained generated-answer diagnostic, n=54 | 0.806604 | 0.754648 | Unavailable |
| Answer-input LoRA trial, n=25 | 0.820347 | 0.764370 | 0.800243 |

These columns report Spearman. Adapted answers have normalized MSE 0.042388 on the 25-example cohort; original captions have 0.044010. Their Spearman difference is -0.020105, with paired 95% interval [-0.115548, +0.057211]. Generated answers on the 54-example cohort trail original captions by 0.051956, with interval [-0.196485, +0.068742]. Both small answer cohorts retain the original-caption preference on point rank correlation.

Full saved-candidate identities, all metric views, matched IDs, exclusions and three 2,000-draw paired source-group intervals: [candidate comparison](csts_audited_candidate_comparison_20261026.json).

## Future development profile

The new [Qwen development profile](../configs/csts-qwen-audited-development.json) points validation at the separately saved [1,491 model-audited development rows](csts_development_model_audited_rows_20261026.json). It retains the existing training and human-reannotated test inputs. Original experiment configurations and published metrics retain their historical input hashes.

New development SHA-256: `076306732aca5a43a0643735a1d9bb17c3e466963b7ff21d5a154fbbab764829`.

Qwen preparation now accepts a hash-pinned teacher cache that covers the current training and validation inputs plus unused entries. This lets the audited subset reuse the existing cache. Missing required entries, changed input hashes and overlapping training/validation passage-condition keys still fail. Only accepted training answers enter supervision; the preparation audit records `unused_teacher_keys`.

Use the audited profile explicitly for the next Qwen evidence run, with a fresh output name:

```bash
python -m csts_pilot.qwen_evidence_run \
  --settings configs/csts-qwen-audited-development.json \
  --name audited-development-20261026 --execute
```

The runner's historical default profile remains unchanged. This command selects checkpoints against the 1,491 model-audited development rows. The audit itself launched no training and replaced no encoder checkpoint.

## Closeout verification

Independent recomputation from the sealed test export reproduces Spearman `0.7885050017660868`, normalized MSE `0.07076334011896077`, rating-scale MAE `0.8607485359861651`, 936 discrepancies of at least one point and 136 of at least two points. All semantic-family and condition totals reconcile. The development file matches its configured SHA-256; its 1,491 unique rows agree with the usable audit labels and span 671 source groups.

Five preparation regression cases pass in dependency-isolated execution of the exact production and test functions: exact cache, unused superset, missing required key, train/development overlap and changed hash. Real cache parsing, row validation, Pydantic configuration and file hash checks were retained. Ruff checks and formatting pass. Full Qwen pytest collection is blocked in the available local environment by the missing `peft` dependency; full import/integration validation was not completed.
