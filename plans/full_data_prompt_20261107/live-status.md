# Live training status

Page checked: Sun 5:03 PM EST. Worker observation times appear below.
The background reporter checks every five minutes. A page update does not establish a fresh GPU observation.

**Training fits finished: 15 / 15.**
The held-out test remains sealed for evaluation.

**Both workers have verified publication and successful compute cleanup receipts.**

| Placement | Current work | Fits confirmed finished | GPU use | Cloud-verified epochs | Uploads pending |
| --- | --- | ---: | ---: | ---: | ---: |
| Seoul (asia-northeast3-a) | Publication verified; compute cleanup confirmed | 9 / 9 | — | 47 | 0 |
| Taiwan (asia-east1-b) | Publication verified; compute cleanup confirmed | 6 / 6 | — | 26 | 0 |

New checkpoint publications use native VIPER Cloud.
Controllers delete exact owned resources after verified publication and retain unverified recovery disks.

worker1 last successful worker observation: 2026-11-08T21:45:34.398386+00:00.
worker2 last successful worker observation: 2026-11-08T21:45:33.703780+00:00.

| Fit | Epochs completed at last observation | Status | Selected epoch |
| --- | ---: | --- | ---: |
| A_condition_first_seed7 | 5 | Finished | 4 |
| B_order_only_seed7 | 5 | Finished | 4 |
| C_case_inspired_seed7 | 5 | Finished | 4 |
| B_order_only_seed8 | 3 | Finished | 2 |
| C_case_inspired_seed8 | 5 | Finished | 4 |
| A_condition_first_seed8 | 6 | Finished | 5 |
| C_case_inspired_seed9 | 6 | Finished | 5 |
| A_condition_first_seed9 | 5 | Finished | 4 |
| B_order_only_seed9 | 5 | Finished | 4 |
| A_condition_first_seed10 | 4 | Finished | 3 |
| B_order_only_seed10 | 5 | Finished | 4 |
| C_case_inspired_seed10 | 3 | Finished | 2 |
| B_order_only_seed11 | 4 | Finished | 3 |
| C_case_inspired_seed11 | 7 | Finished | 6 |
| A_condition_first_seed11 | 5 | Finished | 4 |

[Structured status](live-status.json) · [Deployment records](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/plans/full_data_prompt_20261107/lifecycle-launch-20261108/README.md)

Monitoring reads progress metadata and publication receipts.
