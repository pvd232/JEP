# Tranche 5 verified result — 26 October 2026

All four correction-head systems missed the frozen validation gate. Retain the archived Qwen model. No candidate test extraction or candidate test evaluation ran.

| System | Validation Spearman | MSE (0–1 scale) | Condition ordering | FPR at 90.11% recall | Selected epoch | Selected alpha |
|---|---:|---:|---:|---:|---:|---:|
| Archived Qwen | 0.782575 | 0.034574 | 90.15% | 9.69% | archived | — |
| Same-passage subtraction | 0.763242 | 0.045916 | 90.85% | 13.20% | 8 | 0.444809 |
| Population translation | 0.769697 | 0.049334 | 91.12% | 12.58% | 0 | 0.5 |
| Population component removal | 0.770358 | 0.048931 | 90.43% | 11.55% | 0 | 0.5 |
| CASE-style residual | 0.695586 | 0.056846 | 88.07% | 24.95% | 19 | 1 (fixed) |

Every system uses the full 1,830-row validation cohort. Positive ratings are 4–5 and negative ratings 1–2; middle ratings remain in regression/ranking. Each operating threshold was chosen separately on validation. Condition ordering uses 721 dependent within-pair condition comparisons.

The gate required Spearman at least 0.7875746597420997, no more than a one-percentage-point condition-ordering decline, and no more than a one-percentage-point FPR increase. Every alternative missed the Spearman gate and exceeded the FPR allowance. The CASE-style arm also missed the ordering guard.

## Interpretation

The best corrected system scored 0.770358, 0.012217 below archived Qwen validation. Population translation improved condition ordering by approximately 0.97 percentage points while worsening FPR by approximately 2.89 points. Thus better relative ordering across conditions did not deliver better absolute discrimination between matching and nonmatching passages.

Population and component-removal heads selected epoch zero: their trained checkpoints did not improve validation Spearman over their initialized heads. Same-passage subtraction learned alpha 0.444809 but still lost ranking accuracy and increased false positives. These results support stopping the tested correction-plus-head systems. They do not isolate subtraction from the added head, establish an optimization minimum, or reproduce the published CASE architecture/results.

The rating-1 mean predictions were 0.251735 for archived Qwen, 0.252440 for same-passage, 0.452901 for population translation, 0.448906 for component removal, and 0.314471 for CASE-style. Population methods substantially overestimated unrelated pairs; condition-ordering gains alone would conceal that failure.

## JEP direction

Keep the selected Qwen representation as the retrieval/clustering starting point. The reviewed next screen tests whether copied evidence helps when it supervises the actual condition-dependent attention readout, comparing identical ratings-only and ratings-plus-span heads. That isolates the added span objective within this fixed architecture.

For codebook discovery, distinguish conditional retrieval from expert decisions that two passages express the same actionable demand or harm. A useful next JEP measurement is the rate of false cluster merges at high retrieval recall, with experts reviewing conflicting evidence, entity/beneficiary mismatches, and distinctions between related demands. This experiment favors that error-focused direction over further post-hoc reference-subtraction sweeps. It supplies no Colombian Spanish ground truth or measured JEP improvement.

## Provenance

- Reviewed source: `faa0ae537feea2333b5c245c9b23e0829729441c`; attempt `c98e7a60`, `overnight_reviewed_physical`.
- Settings SHA-256: `c492c508e7fb63a199b3e927461d954d4d939fecb2d578dbaa6e245f4153f07c`.
- Model SHA-256: `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`.
- Bank SHA-256: `e822d73227636f98498c15b873b1dd79ba27b3d87f754b32f4e85c8b204bcf7b`.
- Selection and per-row predictions are retained under the native `freeze_selection` run `01M5VD1ZA46727B94AEKENZ40G`; summary, selection and event sidecars remain in `/home/machina/jep-csts-matched-baselines-20261026/matched_baseline_results/overnight_reviewed_physical`.
- Archived test comparators remain Qwen 0.7885050017660868 and GPT 0.8029168452132416. Neither is a new result from this tranche.
- [Frozen plan](../plans/csts-tranche-5-matched-baselines.md) · [Live overnight status](csts_overnight_status.md).
