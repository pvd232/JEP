# JEP evidence selection and sentence comparison

Source: `f59d2f8c5c64b96940a624a56d385330cf6a11ca`

Hardware: NVIDIA A100-SXM4-80GB

Seeds: 7, 8, 9. Training: 6,051 comparisons. Validation: 1,576. Test: 2,431.

A: saved cosine score. B: token weighting trained with ratings. C: token weighting trained with ratings and evidence. D: fitted comparison of B vectors. E: fitted comparison of C vectors.

## Live progress

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 04:29:56 | stage started | 7 |  | name: publish_proposition_final |
| 2026-10-28 04:30:36 | stage finished | 7 |  | name: publish_proposition_final; status: succeeded |
| 2026-10-28 04:30:36 | stage started | 7 |  | name: publish_proposition_writing_epoch5 |
| 2026-10-28 04:31:15 | stage finished | 7 |  | name: publish_proposition_writing_epoch5; status: succeeded |
| 2026-10-28 04:31:15 | stage started | 7 |  | name: publish_ratings_final |
| 2026-10-28 04:31:55 | stage finished | 7 |  | name: publish_ratings_final; status: succeeded |
| 2026-10-28 04:31:55 | stage started | 7 |  | name: writing_retention |
| 2026-10-28 04:31:55 | study failed |  |  | error_type: PathError |
