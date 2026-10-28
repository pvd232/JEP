# Qwen proposition supervision: early validation diagnostic

This is a fixed short continuation from the selected Qwen adapter. The full matched-budget comparison is queued separately. The reported predictions use the current validation split.

| Cohort | n | Groups | Baseline Spearman | Ratings continuation | Proposition continuation | Proposition − ratings [95% CI] |
|---|---:|---:|---:|---:|---:|---|
| all | 1572 | 678 | 0.818432 | 0.812967 | 0.812447 | -0.000520 [-0.003289, +0.002199] |
| appearance | 93 | 70 | 0.788686 | 0.783993 | 0.787748 | +0.003756 [-0.017268, +0.024610] |
| colour | 74 | 54 | 0.779353 | 0.798910 | 0.803303 | +0.004394 [-0.016043, +0.025972] |

| Cohort | Arm | Raw MAE, 1–5 | Raw RMSE, 1–5 | Calibrated MAE, 1–5 | Calibrated RMSE, 1–5 |
|---|---|---:|---:|---:|---:|
| all | baseline | 0.766282 | 0.947855 | 0.676700 | 0.895647 |
| all | ratings | 0.742419 | 0.942327 | 0.666403 | 0.904577 |
| all | evidence | 0.743453 | 0.943666 | 0.667318 | 0.906887 |
| appearance | baseline | 0.814470 | 0.983302 | 0.731789 | 0.905016 |
| appearance | ratings | 0.785588 | 0.960587 | 0.734693 | 0.914039 |
| appearance | evidence | 0.790513 | 0.964940 | 0.736903 | 0.915372 |
| colour | baseline | 0.815673 | 0.978416 | 0.705458 | 0.878781 |
| colour | ratings | 0.775269 | 0.940713 | 0.704099 | 0.878023 |
| colour | evidence | 0.781473 | 0.944397 | 0.707429 | 0.876937 |

The JSON includes both continuation changes from the unchanged baseline, paired source-group intervals, exact protocol and source identities, and five-fold group-held-out calibration errors. Calibrated scores in the table use coefficients fitted on the same overall validation predictions. Spearman uses raw scores. Sampling intervals are conditional on this one seed and fixed calibration. Appearance and colour results are exploratory.
