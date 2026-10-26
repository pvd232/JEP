# JEP overnight experiments — live status

Published: **2026-10-26 08:09 UTC**.

| Comparator | Validation Spearman | Existing-test Spearman |
|---|---:|---:|
| Saved Qwen + LoRA | 0.782575 | 0.788505 |
| Archived LLM pair judge | — | 0.802917 |

Existing baseline predictions are reused. Scores below identify validation or test explicitly.

## overnight_cached_model_recovery

Status: **failed**.

Controller: `/home/machina/jep-csts-evidence-attention-20261026/evidence_attention_results/overnight_cached_model_recovery/summary.json`

Source: `934e7d87f485fa8a0739e77255984d3b30ff97cf`.

Current native stage: `{'name': 'freeze_selection', 'experiment_id': 'csts_attention_934e7d87_85314012_freeze_selection'}`.

Failure: `attempt 1 failed; evidence written to /home/machina/jep-csts-evidence-attention-20261026/experiments/csts_attention_934e7d87_85314012_freeze_selection/runs/freeze_selection/01M5VJX4PKCFDR83VSSE0NNTAB/resolved.yaml`. Attempt preserved.

| Arm | Validation Spearman | Validation MSE | Epoch | State |
|---|---:|---:|---:|---|
| attention_ratings | 0.710713 | 0.052670 | 4 | selected checkpoint |
| attention_evidence | 0.598905 | 0.070324 | 10 | selected checkpoint |

Extraction `validation/`: **3660/3660** occurrences; 188 seconds elapsed.

## overnight_disk_recovery

Status: **interrupted**.

Controller: `/home/machina/jep-csts-evidence-attention-20261026/evidence_attention_results/overnight_disk_recovery/summary.json`

Source: `934e7d87f485fa8a0739e77255984d3b30ff97cf`.

Current native stage: `{'name': 'extract_training', 'experiment_id': 'csts_attention_934e7d87_b6d1d2f1_extract_training'}`.

Failure: `Operator stopped launch before GPU inference to restore missing HF_HOME; see preserved launch receipt and overnight_cached_model_recovery`. Attempt preserved.

## overnight_reviewed

Status: **failed**.

Controller: `/home/machina/jep-csts-evidence-attention-20261026/evidence_attention_results/overnight_reviewed/summary.json`

Source: `934e7d87f485fa8a0739e77255984d3b30ff97cf`.

Current native stage: `{'name': 'extract_training', 'experiment_id': 'csts_attention_934e7d87_7dd8b9d5_extract_training'}`.

Failure: `attempt 1 failed; evidence written to /home/machina/jep-csts-evidence-attention-20261026/experiments/csts_attention_934e7d87_7dd8b9d5_extract_training/runs/extract_training/01M5VD483MVKVANHCGQMFXPQM0/resolved.yaml`. Attempt preserved.

Extraction `training/`: **13960/13960** occurrences; 460 seconds elapsed.

## overnight_reviewed_physical

Status: **complete**.

Controller: `/home/machina/jep-csts-matched-baselines-20261026/matched_baseline_results/overnight_reviewed_physical/summary.json`

Source: `faa0ae537feea2333b5c245c9b23e0829729441c`.

| Arm | Validation Spearman | Validation MSE | Epoch | State |
|---|---:|---:|---:|---|
| same_passage | 0.763242 | 0.045916 | 8 | selected checkpoint |
| population | 0.769697 | 0.049334 | 0 | selected checkpoint |
| projection | 0.770358 | 0.048931 | 0 | selected checkpoint |
| case | 0.695586 | 0.056846 | 19 | selected checkpoint |

Frozen validation decision:

```json
{
  "event": "validation_selection",
  "selected_arm": null,
  "eligibility": {
    "same_passage": {
      "eligible": false
    },
    "population": {
      "eligible": false
    },
    "projection": {
      "eligible": false
    },
    "case": {
      "eligible": false
    }
  },
  "thresholds": {
    "native_direct": 0.5334962606430054,
    "same_passage": 0.6072174906730652,
    "population": 0.6161432862281799,
    "projection": 0.6177546977996826,
    "case": 0.6212596893310547
  },
  "test_scores_used_for_selection": false
}
```

Extraction `validation/bank_820/917`: **16/16** occurrences; 746 seconds elapsed.

Extraction `validation/bank_856/917`: **8/16** occurrences; 761 seconds elapsed.

Extraction `validation/bank_891/917`: **16/16** occurrences; 776 seconds elapsed.

Stop reason: `no_validation_candidate_eligible`.

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
