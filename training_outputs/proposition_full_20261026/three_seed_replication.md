# Three-seed replication: full-bank proposition supervision

Status: **running**. Completed seeds: **1/3**. Preregistered seeds: **7, 8, 9**.

Both the ratings control and proposition model are trained for each new seed, starting from the pinned pretrained backbone with fresh adapters. Only the training seed changes. The dataset, teacher bank, writing references, learning rate, batch sizes and patience policy are frozen. Writing and ratings stages stop under the same validation policy used for seed 7.

| Seed | Control test Spearman | Proposition test Spearman | Difference | Status |
|---:|---:|---:|---:|---|
| 7 | 0.855375 | 0.863398 | +0.008024 | complete |
| 8 | — | — | — | running |
| 9 | — | — | — | queued |

Each score uses the same **2,430 test examples**. Checkpoints are selected on validation and frozen before test scoring. Completed training seeds: 7.

| Metric, overall cohort | Control mean ± SD | Proposition mean ± SD | Paired difference mean ± SD |
|---|---:|---:|---:|
| Validation Spearman | 0.871875 (one seed) | 0.877061 (one seed) | 0.005185 (one seed) |
| Test Spearman | 0.855375 (one seed) | 0.863398 (one seed) | 0.008024 (one seed) |
| Test raw MSE, 0–1 | 0.038359 (one seed) | 0.035584 (one seed) | -0.002775 (one seed) |

SD is calculated across completed training seeds. Appearance and colour results, per-seed paired intervals, selected epochs and checkpoint identities are included in the JSON. All preregistered seeds are reported.

The original seed-7 report is [here](comparison_report.md). New reports will appear at [seed 8](seeds/seed_8/comparison_report.md) and [seed 9](seeds/seed_9/comparison_report.md). The fixed protocol is [here](replication_protocol.json).

Selected weights and per-seed metadata are preserved with SHA-256 verification on the JEP VM under `/home/machina/jep-full-propositions-20261027-operator/replications-20261027/checkpoints/`.
