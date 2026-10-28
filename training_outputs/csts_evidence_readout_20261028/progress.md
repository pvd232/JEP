# JEP evidence selection and sentence comparison

Source: `f59d2f8c5c64b96940a624a56d385330cf6a11ca`

Hardware: NVIDIA A100-SXM4-80GB

Seeds: 7, 8, 9. Training: 6,051 comparisons. Validation: 1,576. Test: 2,431.

A: saved cosine score. B: token weighting trained with ratings. C: token weighting trained with ratings and evidence. D: fitted comparison of B vectors. E: fitted comparison of C vectors.

## Live progress

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 04:35:25 | stage started | 7 |  | name: publish_proposition_final |
| 2026-10-28 04:36:05 | stage finished | 7 |  | name: publish_proposition_final; status: succeeded |
| 2026-10-28 04:36:05 | stage started | 7 |  | name: publish_proposition_writing_epoch5 |
| 2026-10-28 04:36:45 | stage finished | 7 |  | name: publish_proposition_writing_epoch5; status: succeeded |
| 2026-10-28 04:36:45 | stage started | 7 |  | name: publish_ratings_final |
| 2026-10-28 04:37:24 | stage finished | 7 |  | name: publish_ratings_final; status: succeeded |
| 2026-10-28 04:37:24 | stage started | 7 |  | name: writing_retention |
| 2026-10-28 04:38:39 | writing retention |  |  | checkpoint: writing; 16/121 |
| 2026-10-28 04:38:50 | writing retention |  |  | checkpoint: writing; 32/121 |
| 2026-10-28 04:38:52 | writing retention |  |  | checkpoint: writing; 48/121 |
| 2026-10-28 04:38:53 | writing retention |  |  | checkpoint: writing; 64/121 |
| 2026-10-28 04:38:55 | writing retention |  |  | checkpoint: writing; 80/121 |
| 2026-10-28 04:38:56 | writing retention |  |  | checkpoint: writing; 96/121 |
| 2026-10-28 04:38:58 | writing retention |  |  | checkpoint: writing; 112/121 |
| 2026-10-28 04:38:59 | writing retention |  |  | checkpoint: writing; 121/121 |
| 2026-10-28 04:39:07 | writing retention |  |  | checkpoint: after_ratings; 16/121 |
| 2026-10-28 04:39:14 | writing retention |  |  | checkpoint: after_ratings; 32/121 |
| 2026-10-28 04:39:16 | writing retention |  |  | checkpoint: after_ratings; 48/121 |
| 2026-10-28 04:39:17 | writing retention |  |  | checkpoint: after_ratings; 64/121 |
| 2026-10-28 04:39:19 | writing retention |  |  | checkpoint: after_ratings; 80/121 |
| 2026-10-28 04:39:20 | writing retention |  |  | checkpoint: after_ratings; 96/121 |
| 2026-10-28 04:39:22 | writing retention |  |  | checkpoint: after_ratings; 112/121 |
| 2026-10-28 04:39:22 | writing retention |  |  | checkpoint: after_ratings; 121/121 |
| 2026-10-28 04:39:23 | writing retention scores |  |  | writing answer CE 0.277840, exact agreement 0.375000; after_ratings answer CE 4.954078, exact agreement 0.000000; paired CE change 4.676239 |
| 2026-10-28 04:39:49 | stage finished | 7 |  | name: writing_retention; status: succeeded |
| 2026-10-28 04:39:49 | stage started | 7 |  | name: extract_training_proposition_final |
| 2026-10-28 04:40:33 | readout extraction |  |  | split: training; 4/12102 |
| 2026-10-28 04:40:38 | readout extraction |  |  | split: training; 204/12102 |
| 2026-10-28 04:40:43 | readout extraction |  |  | split: training; 404/12102 |
| 2026-10-28 04:40:48 | readout extraction |  |  | split: training; 604/12102 |
| 2026-10-28 04:40:53 | readout extraction |  |  | split: training; 804/12102 |
| 2026-10-28 04:40:58 | readout extraction |  |  | split: training; 1004/12102 |
