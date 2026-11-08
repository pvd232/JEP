# Live validation and test results

Updated: 2026-11-08T23:37:30.954487+00:00. This durable reporter checks every 30 seconds and pushes each newly observed score to this branch.

**Training: 15/15 finished. Test scores: 14/15. VIPER cloud bytes independently verified: 7/15.**

Scores are Spearman correlation. Checkpoints were selected using validation only; no retraining occurs here. The test partition was previously examined and these comparisons are exploratory.

| Arm | Seed | Selected epoch | Validation | Test | Publication |
| --- | ---: | ---: | ---: | ---: | --- |
| A_condition_first | 7 | 4 | 0.876475 | 0.855876 | sealed; cloud verification pending |
| A_condition_first | 8 | 5 | 0.873108 | 0.853193 | cloud verified |
| A_condition_first | 9 | 4 | 0.875194 | 0.852316 | sealed; cloud verification pending |
| A_condition_first | 10 | 3 | 0.872498 | 0.849665 | sealed; cloud verification pending |
| A_condition_first | 11 | 4 | 0.875049 | 0.849990 | cloud verified |
| B_order_only | 7 | 4 | 0.874697 | 0.856239 | cloud verified |
| B_order_only | 8 | 2 | 0.869726 | 0.849378 | sealed; cloud verification pending |
| B_order_only | 9 | 4 | 0.872478 | 0.858619 | cloud verified |
| B_order_only | 10 | 4 | 0.876187 | 0.859654 | cloud verified |
| B_order_only | 11 | 3 | 0.875597 | 0.853037 | sealed; cloud verification pending |
| C_case_inspired | 7 | 4 | 0.875696 | 0.851034 | sealed; cloud verification pending |
| C_case_inspired | 8 | 4 | 0.875750 | 0.855447 | cloud verified |
| C_case_inspired | 9 | 5 | 0.875979 | pending | pending |
| C_case_inspired | 10 | 2 | 0.872364 | 0.849748 | sealed; cloud verification pending |
| C_case_inspired | 11 | 6 | 0.875695 | 0.859601 | cloud verified |

| Arm | Validation mean ± SD (5 seeds) | Test mean ± SD | Completed test seeds |
| --- | ---: | ---: | ---: |
| A_condition_first | 0.874465 ± 0.001630 | 0.852208 ± 0.002541 | 5/5 |
| B_order_only | 0.873737 ± 0.002648 | 0.855385 ± 0.004213 | 5/5 |
| C_case_inspired | 0.875097 ± 0.001532 | pending full arm | 4/5 |

| Worker | Observed phase | Test captures | Current trial |
| --- | --- | ---: | --- |
| 1 | test_inference | 7/8 | C_case_inspired_seed9 |
| 2 | complete | 7/7 | C_case_inspired_seed8 |

Inference and native VIPER uploads run concurrently. 'Sealed' means the CPU independently checked prediction bytes, row identities, labels and frozen model/test hashes. 'Cloud verified' additionally requires verified publication and download receipts. Compute cleanup follows verified export.

[Score CSV](test-progress.csv) · [Structured status](test-progress.json) · [Final analysis](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/training_outputs/full_data_prompt_20261108/test-results.md)
