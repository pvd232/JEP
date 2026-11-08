# Full-data prompt experiment: validation and test

All 15 LoRA fits and all 15 frozen-checkpoint test evaluations are complete. Values are mean ± sample SD across the same five seeds. Patience remained 1. Checkpoints were selected using validation before test inference.

| Prompt arm | Validation Spearman | Test Spearman |
| --- | ---: | ---: |
| A_condition_first | 0.874465 ± 0.001630 | 0.852208 ± 0.002541 |
| B_order_only | 0.873737 ± 0.002648 | 0.855385 ± 0.004213 |
| C_case_inspired | 0.875097 ± 0.001532 | 0.853567 ± 0.003981 |

B has the highest mean test score, +0.003177 above A. Its conditional 95% source-group bootstrap interval is [-0.005175, +0.011577]. All three paired intervals include zero, so this study does not establish a clear prompt winner. C has the highest mean validation score.

A places the condition first. B moves the same instruction after the passage. C uses the CASE-inspired condition-target formulation. Validation has 1,576 comparisons; test has 2,430 comparisons in 1,222 source groups.

[Paired comparisons and bootstrap intervals](test-results.md) · [Per-fit validation/test scores](test_and_validation.csv) · [Full statistics](test_and_validation.json)

The test partition was examined in earlier work. These are exploratory comparisons; test scores did not choose checkpoints or extend training. The 10,000-draw shared source-group bootstrap conditions on the trained checkpoints. Seed variation is reported separately.

## Publication and resource cleanup

Training produced 77 checkpoint archives (35,921,745,920 bytes). All archives and three input files passed independent cloud byte verification before the original training VMs and disks were deleted.

The inference-only evaluation restored the 15 exact selected model hashes. Each worker replayed one validation score exactly before scoring test. Predictions, timing and native run references were uploaded asynchronously through VIPER Cloud. All 45 test artifacts were independently downloaded and SHA-256 verified, including ordered row identities, targets and frozen model/test hashes. Both evaluation VMs, their disks and the temporary evaluation snapshot were deleted after verification. Historical source resources were preserved.

- [Frozen checkpoint selections](frozen-selections.json)
- [Training archive hashes and cloud references](cloud-archive-inventory.json)
- [Training cleanup receipts](cleanup.json)
- [Test publication and verification receipts](test-publication-receipts.json)
- [Test input publication references](test-input-publication.json)
- [Test allocations](test-allocations.json)
- [Test cleanup receipts](test-cleanup.json)
- [Measured evaluation timing](test-timing-profile.json)
- [Controller access receipts](controller-access.json)
- [Controller metadata authentication preflight](controller-metadata-preflight.json)
- [Controller failure diagnosis and repair](../../plans/full_data_prompt_20261107/controller-repair-20261108/README.md)

## Publishing progress

The durable CPU reporter checks every 30 seconds and publishes newly measured scores to the established [GitHub tracker](https://github.com/pvd232/JEP/blob/monitor/full-data-prompt-20261107/plans/full_data_prompt_20261107/live-status.md). It distinguishes sealed predictions from independently verified cloud bytes. The [execution procedure](../../scripts/full_data_prompt_20261107/README.md) and reporter are committed with this experiment.

Across all 15 test captures, mean elapsed time was 212.49 seconds per checkpoint: 146.84 seconds for scoring including model loading, and 65.65 seconds outside scoring (30.9%). This is measurable orchestration and artifact overhead.

Two evaluation-launch API errors were repaired before any test scoring. The final inference source is `9fb983cc71a3745c1684a67f74d60a7c19855917`. Validation replay matched both saved scores exactly. The current evaluator reloads the backbone and starts a native run for each checkpoint; the timing profile measures this overhead rather than treating total elapsed time as GPU forward time.

The controller uses its attached service account with automatic credential refresh and permanent project-wide Owner and IAP access on Mantra, plus Storage Admin on the VIPER bucket, as explicitly requested.

Training execution source: `83467f756d1d10e9c1f3183d9242cea4424e1ce4`. Scientific training source: `9b163a100362580f99722eecc63895420ecec3b1`. Protocol SHA-256: `0aee2f8aece3e89ff12223fe40a54fb632305339f240475362212c432fd68a11`.

The original frozen-selection release records retain their pre-evaluation timestamps and unopened-test flags. The completed test release is recorded separately in the test receipts above.
