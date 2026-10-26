# Answer-as-input screen — 26 October 2026

**Runner deployed; focused checks and independent review in progress. No new scores yet.**

The saved Qwen validation comparator is **0.7825746597 Spearman**, MSE **0.034574**, FPR **9.69%** at approximately **90.11% recall**. It is reused without a baseline rerun.

Two zero-update arms replace each passage with its previously accepted copied answer: original condition, and fixed “overall meaning” condition. Missing or rejected answers retain that side's original passage and condition. All 1,830 validation comparisons remain. Neither-accepted pairs reuse saved native scores exactly.

This is an extractive answer-input hybrid, a first diagnostic of Tu's answer bottleneck. It does not replicate generated-proposition extraction or answer-encoder fine-tuning. Validation alone determines eligibility; no candidate test scores are used.

Progress and each arm's metrics will be published here. Native artifacts and unchanged adapter identities will be retained.
