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
| 2026-10-28 04:41:03 | readout extraction |  |  | split: training; 1204/12102 |
| 2026-10-28 04:41:08 | readout extraction |  |  | split: training; 1404/12102 |
| 2026-10-28 04:41:13 | readout extraction |  |  | split: training; 1604/12102 |
| 2026-10-28 04:41:18 | readout extraction |  |  | split: training; 1804/12102 |
| 2026-10-28 04:41:23 | readout extraction |  |  | split: training; 2004/12102 |
| 2026-10-28 04:41:28 | readout extraction |  |  | split: training; 2204/12102 |
| 2026-10-28 04:41:33 | readout extraction |  |  | split: training; 2404/12102 |
| 2026-10-28 04:41:38 | readout extraction |  |  | split: training; 2604/12102 |
| 2026-10-28 04:41:42 | readout extraction |  |  | split: training; 2804/12102 |
| 2026-10-28 04:41:48 | readout extraction |  |  | split: training; 3004/12102 |
| 2026-10-28 04:41:53 | readout extraction |  |  | split: training; 3204/12102 |
| 2026-10-28 04:41:58 | readout extraction |  |  | split: training; 3404/12102 |
| 2026-10-28 04:42:02 | readout extraction |  |  | split: training; 3604/12102 |
| 2026-10-28 04:42:07 | readout extraction |  |  | split: training; 3804/12102 |
| 2026-10-28 04:42:12 | readout extraction |  |  | split: training; 4004/12102 |
| 2026-10-28 04:42:17 | readout extraction |  |  | split: training; 4204/12102 |
| 2026-10-28 04:42:22 | readout extraction |  |  | split: training; 4404/12102 |
| 2026-10-28 04:42:27 | readout extraction |  |  | split: training; 4604/12102 |
| 2026-10-28 04:42:32 | readout extraction |  |  | split: training; 4804/12102 |
| 2026-10-28 04:42:37 | readout extraction |  |  | split: training; 5004/12102 |
| 2026-10-28 04:42:42 | readout extraction |  |  | split: training; 5204/12102 |
| 2026-10-28 04:42:47 | readout extraction |  |  | split: training; 5404/12102 |
| 2026-10-28 04:42:52 | readout extraction |  |  | split: training; 5604/12102 |
| 2026-10-28 04:42:57 | readout extraction |  |  | split: training; 5804/12102 |
| 2026-10-28 04:43:02 | readout extraction |  |  | split: training; 6004/12102 |
| 2026-10-28 04:43:07 | readout extraction |  |  | split: training; 6204/12102 |
| 2026-10-28 04:43:12 | readout extraction |  |  | split: training; 6404/12102 |
| 2026-10-28 04:43:17 | readout extraction |  |  | split: training; 6604/12102 |
| 2026-10-28 04:43:22 | readout extraction |  |  | split: training; 6804/12102 |
| 2026-10-28 04:43:27 | readout extraction |  |  | split: training; 7004/12102 |
| 2026-10-28 04:43:32 | readout extraction |  |  | split: training; 7204/12102 |
| 2026-10-28 04:43:37 | readout extraction |  |  | split: training; 7404/12102 |
| 2026-10-28 04:43:42 | readout extraction |  |  | split: training; 7604/12102 |
| 2026-10-28 04:43:47 | readout extraction |  |  | split: training; 7804/12102 |
| 2026-10-28 04:43:52 | readout extraction |  |  | split: training; 8004/12102 |
| 2026-10-28 04:43:57 | readout extraction |  |  | split: training; 8204/12102 |
| 2026-10-28 04:44:02 | readout extraction |  |  | split: training; 8404/12102 |
| 2026-10-28 04:44:07 | readout extraction |  |  | split: training; 8604/12102 |
| 2026-10-28 04:44:12 | readout extraction |  |  | split: training; 8804/12102 |
| 2026-10-28 04:44:17 | readout extraction |  |  | split: training; 9004/12102 |
| 2026-10-28 04:44:22 | readout extraction |  |  | split: training; 9204/12102 |
| 2026-10-28 04:44:27 | readout extraction |  |  | split: training; 9404/12102 |
| 2026-10-28 04:44:32 | readout extraction |  |  | split: training; 9604/12102 |
| 2026-10-28 04:44:37 | readout extraction |  |  | split: training; 9804/12102 |
| 2026-10-28 04:44:42 | readout extraction |  |  | split: training; 10004/12102 |
| 2026-10-28 04:44:48 | readout extraction |  |  | split: training; 10204/12102 |
| 2026-10-28 04:44:53 | readout extraction |  |  | split: training; 10404/12102 |
| 2026-10-28 04:44:58 | readout extraction |  |  | split: training; 10604/12102 |
| 2026-10-28 04:45:03 | readout extraction |  |  | split: training; 10804/12102 |
| 2026-10-28 04:45:08 | readout extraction |  |  | split: training; 11004/12102 |
| 2026-10-28 04:45:13 | readout extraction |  |  | split: training; 11204/12102 |
| 2026-10-28 04:45:18 | readout extraction |  |  | split: training; 11404/12102 |
| 2026-10-28 04:45:23 | readout extraction |  |  | split: training; 11604/12102 |
| 2026-10-28 04:45:28 | readout extraction |  |  | split: training; 11804/12102 |
| 2026-10-28 04:45:33 | readout extraction |  |  | split: training; 12004/12102 |
| 2026-10-28 04:45:35 | readout extraction |  |  | split: training; 12102/12102 |
| 2026-10-28 04:46:29 | stage finished | 7 |  | name: extract_training_proposition_final; status: succeeded |
| 2026-10-28 04:46:29 | stage started | 7 |  | name: extract_validation_proposition_final |
