# Three-seed replication: full-bank proposition supervision

Status: **running**. Completed seeds: **2/3**. Preregistered seeds: **7, 8, 9**.

Both the ratings control and proposition model are trained for each new seed, starting from the pinned pretrained backbone with fresh adapters. Only the training seed changes. The dataset, teacher bank, writing references, learning rate, batch sizes and patience policy are frozen. Writing and ratings stages stop under the same validation policy used for seed 7.

| Seed | Control test Spearman | Proposition test Spearman | Difference | Status |
|---:|---:|---:|---:|---|
| 7 | 0.855375 | 0.863398 | +0.008024 | complete |
| 8 | 0.853183 | 0.854933 | +0.001750 | complete |
| 9 | — | — | — | running |

Each score uses the same **2,430 test examples**. Checkpoints are selected on validation and frozen before test scoring. Completed training seeds: 7, 8.

| Metric, overall cohort | Control mean ± SD | Proposition mean ± SD | Paired difference mean ± SD |
|---|---:|---:|---:|
| Validation Spearman | 0.871280 ± 0.000842 | 0.875124 ± 0.002739 | 0.003844 ± 0.001898 |
| Test Spearman | 0.854279 ± 0.001550 | 0.859165 ± 0.005986 | 0.004887 ± 0.004436 |
| Test raw MSE, 0–1 | 0.038867 ± 0.000718 | 0.037397 ± 0.002564 | -0.001470 ± 0.001846 |

SD is calculated across completed training seeds. Appearance and colour results, per-seed paired intervals, selected epochs and checkpoint identities are included in the JSON. All preregistered seeds are reported.

Reports: [Completed seed-7 report](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md), [seed 8 status and report](./seeds/seed_8/comparison_report.md), and [seed 9 status and report](./seeds/seed_9/comparison_report.md). [Frozen replication protocol](https://github.com/pvd232/JEP/blob/2e4a875cd0ac56754bbee58667bc37f4e061ed55/training_outputs/proposition_full_20261026/replication_protocol.json).

The JEP repository is private. GitHub links require sign-in to an account with repository access. Pending report pages are marked until final results are published.

Selected weights and per-seed metadata are preserved with SHA-256 verification on the JEP VM under `/home/machina/jep-full-propositions-20261027-operator/replications-20261027/checkpoints/`.
