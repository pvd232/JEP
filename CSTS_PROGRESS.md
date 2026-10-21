# C-STS results

The rating study is complete. All selected checkpoints and evaluation artifacts are stored in VIPER. These scores use 2,620 reserved comparisons from 1,241 caption groups.

| Model | MSE | Spearman | Question ordering |
| --- | ---: | ---: | ---: |
| With question | 0.1443 | 0.432 | 76.1% |
| Without question | 0.1723 | 0.125 | 50.0% |
| Constant training mean | 0.1681 | Undefined | 50.0% |

Model scores average seeds 7, 8 and 9. MSE uses the normalized 0–1 rating scale. Ordering compares different conditions for the same caption pair. Those comparisons reuse captions.

The condition produces a consistent gain across the three seeds. Absolute rating accuracy remains modest. Reserved ratings contain more extreme scores than development ratings. Constant-predictor MSE is 0.1681 on reserved evaluation and 0.0920 on development.

![Training and development curves](training_outputs/csts_learning_curves.png)

The [result record](training_outputs/csts_baseline_results.json) contains every seed, selected learning rate, native run references and the data manifest. The [rating protocol](CSTS_RUN.md) records the filtered split and the original label sources.

The [answer and joint study](CSTS_JOINT_RUN.md) follows this baseline. Its first annotation pilot exposed question echoes and incorrect value types. A revised prompt is being checked on 128 fresh examples. Joint training follows the answer audit.

Use the [live-output instructions](TRAINING_OUTPUTS.md) for current controller status, epoch scores, answer loss, GPU use and storage.
