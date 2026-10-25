# Qwen evidence pretraining followed by rating training

| Sequence | Test Spearman | MSE, 0–1 |
|---|---:|---:|
| Ratings → ratings | 0.788505 | 0.070763 |
| Evidence → ratings | 0.783645 | 0.071206 |

Both arms use two fixed first-phase epochs, then the same constant-rate rating training with patience five and a 24-epoch ceiling. Updates and comparison exposure are matched in phase A; evidence training processes additional answer tokens. Both selected checkpoints were frozen before test scoring.

The JSON contains the paired source-group bootstrap interval. It does not measure training-seed variation. Cloud publication runs separately.

## Outcome

Evidence minus ratings-only test Spearman: **−0.004860**, paired 95% interval **[−0.013408, +0.003454]**. The interval uses 2,000 paired bootstrap draws over 1,241 connected source-caption groups, conditional on training seed 7.

This run did not demonstrate a benefit from evidence pretraining. The interval includes zero, so the lower point estimate also does not establish a detrimental effect. It does not establish equivalence.

| Arm | Total epochs trained | Selected total epoch | Selected validation Spearman |
|---|---:|---:|---:|
| Ratings → ratings | 9 | 4 | 0.782575 |
| Evidence → ratings | 12 | 7 | 0.773647 |

Both stopped after five rating epochs without validation improvement. Total epoch counts include the two fixed initial epochs.

## Verification and scope

All ten native stages reported success. The existing report builder checked frozen checkpoint-selection identities and the full 2,620-comparison / 1,241-group test cohort. Metrics recomputed from saved predictions matched native Spearman scores within 1e-12.

This is one seed on the existing, previously examined English C-STS split. Evidence targets were teacher-checked; no Spanish JEP transfer result is claimed. VIPER cloud publication remains separate and asynchronous.

[Full results and provenance](csts_qwen_evidence_results.json) · [Status and direct log access](csts_qwen_evidence_status.md)
