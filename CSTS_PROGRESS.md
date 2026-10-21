# C-STS progress

Snapshot: 2026-10-21T07:52:49.103307+00:00.

All training trials have completed. Reserved evaluation is being finished through the corrected input declaration. The next stages generate answer annotations and train the shared encoder.

| Training arm | Seed | Development MSE | Spearman | Question ordering |
| --- | ---: | ---: | ---: | ---: |
| With question | 7 | 0.0811 | 0.486 | 78.1% |
| Without question | 7 | 0.0998 | 0.191 | 50.0% |
| With question | 8 | 0.0790 | 0.501 | 78.9% |
| With question | 9 | 0.0796 | 0.492 | 78.4% |
| Without question | 8 | 0.1007 | 0.181 | 50.0% |
| Without question | 9 | 0.0951 | 0.177 | 50.0% |

The constant training-mean predictor has development MSE 0.0920. Ordering compares different questions for the same caption pair; these comparisons reuse captions.

![Epoch curves](training_outputs/csts_learning_curves.png)

These are development results on the filtered C-STS reannotation split. The [protocol](CSTS_RUN.md) records data construction, label sources and checkpoint selection. The [joint study](CSTS_JOINT_RUN.md) defines the answer supervision experiment.

For live output, see [training visibility](TRAINING_OUTPUTS.md). This page is a timestamped snapshot.
