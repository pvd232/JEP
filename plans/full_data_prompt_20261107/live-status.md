# Live training status

Updated: Sun 7:07 AM EST. Refresh this page for the latest snapshot.
A background CPU reporter updates this branch every five minutes. Treat snapshots older than ten minutes as stale.

**Training fits finished: 7 / 15.**
The held-out test remains sealed for evaluation.

ETA is unconfirmed while a worker observation is unavailable.

| Placement | Current work | Fits finished | GPU use | Cloud-verified epochs | Uploads pending |
| --- | --- | ---: | ---: | ---: | ---: |
| Seoul (asia-northeast3-a) | A_condition_first_seed9, epoch 4 | 4 / 9 | 100 % | 24 | 0 |
| Taiwan (asia-east1-b) | Stopped; recovery work preserved | 3 / 6 | — | — | — |

Cloud-verified epochs include the five preserved Seoul epochs. New publications use native VIPER Cloud.
The existing controllers delete owned compute and disks after verified publication; unverified recovery disks are retained.

| Fit | Epochs completed | Status | Selected epoch |
| --- | ---: | --- | ---: |
| A_condition_first_seed7 | 5 | Finished | 4 |
| B_order_only_seed7 | 5 | Finished | 4 |
| C_case_inspired_seed7 | 5 | Finished | 4 |
| B_order_only_seed8 | 3 | Finished | 2 |
| C_case_inspired_seed8 | 5 | Finished | 4 |
| A_condition_first_seed8 | 6 | Finished | 5 |
| C_case_inspired_seed9 | 6 | Finished | 5 |
| A_condition_first_seed9 | 3 | Running | — |
| B_order_only_seed9 | 0 | Queued | — |
| A_condition_first_seed10 | 1 | Checkpointed | — |
| B_order_only_seed10 | 0 | Queued | — |
| C_case_inspired_seed10 | 0 | Queued | — |
| B_order_only_seed11 | 0 | Queued | — |
| C_case_inspired_seed11 | 0 | Queued | — |
| A_condition_first_seed11 | 0 | Queued | — |

[Structured status](live-status.json) · [Deployment records](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/plans/full_data_prompt_20261107/lifecycle-launch-20261108/README.md)

Monitoring reads progress metadata and publication receipts. Models and dataset contents remain in their existing stores.
