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

The [answer and joint study](CSTS_JOINT_RUN.md) is annotating 17,334 unique caption and question inputs. Qwen3-8B generates evidence spans. A second prompt checks their relevance and completeness. In the fresh 128-example pilot, 89 answers passed both checks. Codex judged 82 clearly appropriate, with two errors and five uncertain cases. The [audit](training_outputs/csts_annotation_audit.json) records these findings and limitations.

At 09:48 EDT on 21 October, the observer confirmed that annotation stopped at its four-hour execution limit. It saved 14,272 of 17,334 records, including 9,302 accepted answers. The GPU was idle. Training had not started. Recovery validates and reuses the saved answers and gives each stage a six-hour limit. The remaining generation uses the same Qwen revision, prompts and batch size. Comparison, annotation-only, sequential, joint and shuffled-answer checkpoints will use the same reserved evaluation set. Results from the original source `aa11bd3e5f0b731b484fc2a0d01c74dc1d1f2520` remain intact.

The VIPER precision repair is documented in [PR #21](https://github.com/pvd232/viper/pull/21). All seven CI jobs passed, including 198 integration tests and 28 subtests. Its nine numerical GPU regressions also passed on the L4.

Use the [live-output instructions](TRAINING_OUTPUTS.md) for current controller status, epoch scores, answer loss, GPU use and storage.

