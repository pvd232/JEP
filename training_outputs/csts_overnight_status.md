# JEP overnight experiments — live status

Published: **2026-10-26 06:03 UTC**.

| Comparator | Validation Spearman | Existing-test Spearman |
|---|---:|---:|
| Saved Qwen + LoRA | 0.782575 | 0.788505 |
| Archived LLM pair judge | — | 0.802917 |

Existing baseline predictions are reused. Scores below identify validation or test explicitly.

## overnight_reviewed_physical

Status: **running**.

Controller: `/home/machina/jep-csts-matched-baselines-20261026/matched_baseline_results/overnight_reviewed_physical/summary.json`

Source: `faa0ae537feea2333b5c245c9b23e0829729441c`.

Current native stage: `{'name': 'train_population', 'experiment_id': 'csts_matched_faa0ae53_c98e7a60_train_population'}`.

| Arm | Validation Spearman | Validation MSE | Epoch | State |
|---|---:|---:|---:|---|
| same_passage | 0.763242 | 0.045916 | 8 | selected checkpoint |

Extraction `validation/bank_820/917`: **16/16** occurrences; 746 seconds elapsed.

Extraction `validation/bank_856/917`: **8/16** occurrences; 761 seconds elapsed.

Extraction `validation/bank_891/917`: **16/16** occurrences; 776 seconds elapsed.

## overnight_reviewed_inputs

Status: **failed**.

Controller: `/home/machina/jep-csts-matched-baselines-20261026/matched_baseline_results/overnight_reviewed_inputs/summary.json`

Source: `faa0ae537feea2333b5c245c9b23e0829729441c`.

Current native stage: `{'name': 'prepare', 'experiment_id': 'csts_matched_faa0ae53_13fd0702_prepare'}`.

Failure: `local store escapes the workspace root`. Attempt preserved.

## overnight_reviewed

Status: **failed**.

Controller: `/home/machina/jep-csts-matched-baselines-20261026/matched_baseline_results/overnight_reviewed/summary.json`

Source: `faa0ae537feea2333b5c245c9b23e0829729441c`.

Current native stage: `{'name': 'prepare', 'experiment_id': 'csts_matched_faa0ae53_5adcf770_prepare'}`.

Failure: `workspace path contains a symlink: csts_data/train.json`. Attempt preserved.

## Experiment records

[Overnight plan](../plans/csts-overnight-20261026.md) · [Four correction heads](../plans/csts-tranche-5-matched-baselines.md) · [IPED source review](../plans/csts-iped-research-20261026.md)

Scores are published independently of asynchronous VIPER cloud promotion. The hourly autonomous checks reconcile failures and continue reviewed, eligible work within the overnight budget.
