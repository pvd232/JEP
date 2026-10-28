# Three-seed replication: full-bank proposition supervision

Status: **complete**. Completed seeds: **3/3**. Preregistered seeds: **7, 8, 9**.

Both the ratings control and proposition model are trained for each new seed, starting from the pinned pretrained backbone with fresh adapters. Only the training seed changes. The dataset, teacher bank, writing references, learning rate, batch sizes and patience policy are frozen. Writing and ratings stages stop under the same validation policy used for seed 7.

| Seed | Control test Spearman | Proposition test Spearman | Difference | Status |
|---:|---:|---:|---:|---|
| 7 | 0.855375 | 0.863398 | +0.008024 | complete |
| 8 | 0.853183 | 0.854933 | +0.001750 | complete |
| 9 | 0.853866 | 0.860513 | +0.006646 | complete |

Each score uses the same **2,430 test examples**. Checkpoints are selected on validation and frozen before test scoring. Completed training seeds: 7, 8, 9.

| Metric, overall cohort | Control mean ± SD | Proposition mean ± SD | Paired difference mean ± SD |
|---|---:|---:|---:|
| Validation Spearman | 0.872194 ± 0.001690 | 0.875457 ± 0.002021 | 0.003264 ± 0.001676 |
| Test Spearman | 0.854141 ± 0.001122 | 0.859615 ± 0.004304 | 0.005473 ± 0.003297 |
| Test raw MSE, 0–1 | 0.038994 ± 0.000553 | 0.037270 ± 0.001826 | -0.001724 ± 0.001377 |

SD is calculated across completed training seeds. Appearance and colour results, per-seed paired intervals, selected epochs and checkpoint identities are included in the JSON. All preregistered seeds are reported.

Reports: [Completed seed-7 report](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md), [seed 8 status and report](./seeds/seed_8/comparison_report.md), and [seed 9 status and report](./seeds/seed_9/comparison_report.md). [Frozen replication protocol](https://github.com/pvd232/JEP/blob/2e4a875cd0ac56754bbee58667bc37f4e061ed55/training_outputs/proposition_full_20261026/replication_protocol.json).

The JEP repository is private. GitHub links require sign-in to an account with repository access. Pending report pages are marked until final results are published.

Selected weights and per-seed metadata are preserved with SHA-256 verification on the JEP VM under `/home/machina/jep-full-propositions-20261027-operator/replications-20261027/checkpoints/`.
