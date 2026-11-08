# Live training status

Updated: Sun 6:00 AM EST. Refresh this page for the latest snapshot.
A background CPU reporter updates this branch every five minutes. Treat snapshots older than ten minutes as stale.

**Training fits finished: 6 / 15.**
The held-out test remains sealed for evaluation.

**Estimated training finish: Sun 1:07 PM EST**
Planning range: Sun 10:23 AM EST to Sun 2:29 PM EST.
Basis: 16.4 minutes per completed epoch; 3–6 total epochs per remaining fit, based on 6 stopped fits.
Validation-based stopping or Spot interruptions can extend this estimate.

| Placement | Current work | Fits finished | GPU use | Cloud-verified epochs | Uploads pending |
| --- | --- | ---: | ---: | ---: | ---: |
| Seoul (asia-northeast3-a) | C_case_inspired_seed9, epoch 6 | 3 / 9 | 100 % | 20 | 0 |
| Taiwan (asia-east1-b) | A_condition_first_seed10, epoch 2 | 3 / 6 | 100 % | 15 | 0 |

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
| C_case_inspired_seed9 | 5 | Running | — |
| A_condition_first_seed9 | 0 | Queued | — |
| B_order_only_seed9 | 0 | Queued | — |
| A_condition_first_seed10 | 1 | Running | — |
| B_order_only_seed10 | 0 | Queued | — |
| C_case_inspired_seed10 | 0 | Queued | — |
| B_order_only_seed11 | 0 | Queued | — |
| C_case_inspired_seed11 | 0 | Queued | — |
| A_condition_first_seed11 | 0 | Queued | — |

[Structured status](live-status.json) · [Deployment records](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/plans/full_data_prompt_20261107/lifecycle-launch-20261108/README.md)

Monitoring reads progress metadata and publication receipts. Models and dataset contents remain in their existing stores.
