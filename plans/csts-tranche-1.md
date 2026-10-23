# Tranche 1: loss, convergence and checkpoint selection

**Status: execution authorized on October 23, 2026.** The user instructed “yes. run it” after the rating-loss discussion. Both 24-epoch training arms have completed from source `e2545bbc8e509d12b01e12ce43435b897bcb410f`. Checkpoints and validation calibration were frozen before testing. Evaluation is recovering from a VIPER artifact-name handoff error; the collaborative walkthrough remains open separately.

The experiment will determine whether the existing conditional FLAN encoder benefits from a correlation objective and continued rating training. It will establish the comparison loss, checkpoint rule and training budget for subsequent experiments on evidence supervision and stronger encoders.

## Context

The [completed three-seed study](../training_outputs/csts_joint_results.json) selected rating checkpoints by validation MSE. Mean test Spearman was 0.4303 for rating training and 0.4643 for evidence pretraining followed by rating training. Sequential evidence and rating training received an additional optimization stage. Those results motivate a stronger rating-only reference with explicit convergence measurements.

The [cached-format pilot](../training_outputs/csts_annotation_format_report.md) used validation Spearman for rating checkpoint selection. Evidence, prose and JSON scored 0.4866, 0.4865 and 0.4840 respectively, with paired intervals spanning zero. Typed annotation work is retired from the active sequence. Evidence-only remains the auxiliary target for later controlled experiments.

The [prompted GPT-6.1 Sol reference](../training_outputs/csts_sol61_max_report.md) scored 0.8029 Spearman. It judges both passages together. The encoder objective is a reusable vector for each passage under a specified condition.

The 2,620-comparison test set has already been examined and serves as a follow-up benchmark. Final confirmation will use fresh source groups and independently reviewed Spanish JEP testimony.

## Hypotheses and comparisons

| Hypothesis | Planned observation |
| --- | --- |
| Training beyond eight epochs can improve conditional ranking under a schedule designed for longer training. | Compare each arm's validation-selected eight-epoch-prefix checkpoint with its validation-selected full-run checkpoint. |
| Pearson loss can improve conditional ranking relative to MSE under a common optimization budget. | Compare the two full-run checkpoints, with selection based on validation Spearman. |
| Prediction bias and compressed score spread can explain some numerical error independently of rank quality. | Compare raw scores with a separately fitted positive affine calibration. |

Pearson measures linear association; Spearman measures rank association. A gain in Spearman is an empirical hypothesis. Each hypothesis concerns this model, split and seed. Repeated-seed uncertainty belongs to the subsequent confirmation stage.

## Inputs and model

Use the existing LivNLP/C-STS-Reannotated release at revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b` and preserve its prepared partitions:

| Partition | Comparisons | Connected caption groups | Input SHA-256 |
| --- | ---: | ---: | --- |
| Training | 6,980 | 2,674 | `4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01` |
| Validation | 1,830 | 688 | `f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273` |
| Test | 2,620 | 1,241 | `2c8b6f2b62740c85c376eacd02ef222c2bfacdfe8df5f772a4dd7d52b6d38f1e` |

Training comparisons supply gradient updates. Validation comparisons select checkpoints and fit calibration. Test comparisons measure the frozen candidates after selection.

Partitioning groups connected canonical source captions and removes 2,532 training-release rows whose groups overlap the test set. Our test set comes from LivNLP's released `validation` split. The [label audit](../training_outputs/csts_sol61_max_label_audit.json) establishes that all 2,834 ratings in that released split match Tu's human reannotation; 214 invalid rows are excluded. Our training and validation sets retain LivNLP's separate human/LLM training ratings.

Use the existing [AnswerEncoder](../csts_pilot/joint.py) in rating-only mode, with `google/flan-t5-small` revision `0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab`. Encode `Condition: <condition>` followed by `Passage: <passage>`, pool passage-token states, apply the existing bias-free 512-to-128 projection and normalize the result. Cosine between the two conditioned passage vectors predicts the rating.

Create one initial model state from the pinned pretrained backbone and seed-7 projection initialization. Both arms restore those exact bytes. Teacher generation and auxiliary decoder losses are outside this tranche. Rating-only training and validation passes execute the encoder and projection; the decoder remains available in the model container for compatibility with later tranches.

Let a reference rating be $r \in [1,5]$. Its training target is $y = (r - 1) / 4$. The predicted score $s$ is raw cosine in $[-1,1]$. Preserve that score definition in both arms and report its observed range.

Reported MSE is the mean of $(s_i-y_i)^2$ on this rescaled rating scale. Converting predictions back through $\hat r_i=1+4s_i$ makes MSE on the original 1–5 scale equal to 16 times this value. The rescaling applies to rating targets; predictions retain their raw cosine definition.

## Arms and optimization

The two arms differ only in their training objective: mean squared score error versus one minus stabilized batch Pearson correlation.

Both arms use these settings:

- The same saved seed-7 model state and per-epoch pair permutations.
- 24 fixed epochs, pair batch size 32 and 5,256 total updates.
- Fresh AdamW with weight decay 0.01, encoder learning rate 3e-5 and projection learning rate 1e-3.
- Linear warmup for 526 updates, followed by linear learning-rate decay over the remaining updates.
- Gradient clipping at global norm 1.0.
- The same tokenizer, passage mask and 160-token cap.
- BF16 for eligible encoder and projection operations; float32 for passage pooling, vector normalization, cosine scores and loss arithmetic.
- Checkpoint selection by highest validation Spearman.

Each epoch contains 219 updates, including the final four-pair batch. Both arms complete the common budget; validation scores determine the retained checkpoints. Reset and record RNG state for each arm. Record initialization digests, batch-order digests, actual updates, processed tokens, peak memory and elapsed fit time.

For a batch of $b$ comparisons, MSE is:

```math
\mathcal{L}_{\mathrm{MSE}}=\frac{1}{b}\sum_{i=1}^{b}(s_i-y_i)^2.
```

For Pearson loss, define centered scores $u_i = s_i - \bar{s}$ and centered targets $v_i = y_i - \bar{y}$, where the bars denote batch means:

```math
\begin{aligned}
\rho_{\epsilon}(s,y)&=
\frac{\sum_i u_i v_i}
{\sqrt{\sum_i u_i^2+\epsilon}\sqrt{\sum_i v_i^2+\epsilon}},\\
\mathcal{L}_{\mathrm{Pearson}}&=1-\rho_{\epsilon}(s,y),\\
\epsilon&=10^{-8}.
\end{aligned}
```

Compute the loss in float32. Record batches with constant targets. In such a batch the centered target vector is zero, the data gradient is zero, and the ordinary optimizer and schedule step still occurs. Preserve the common batch order and final batch. Fail on nonfinite losses or gradients and retain the exact failure record.

The full-budget design gives both objectives equal update allowances and reveals their learning curves. Stop the overall experiment at the resource ceiling or on a numerical failure, retaining completed checkpoints and reporting the affected comparison as incomplete.

## Checkpoint selection and testing

For each arm retain two candidates:

- The checkpoint with the highest validation Spearman among epochs 1 through 8.
- The checkpoint with the highest validation Spearman among epochs 1 through 24.

Resolve equal validation scores in favor of the earlier epoch. Record each selected epoch, validation metrics and model digest. Freeze all candidate identities before any test-set scoring. Evaluate each unique checkpoint once and reuse its immutable predictions when the two selection windows identify the same model.

The eight-epoch-prefix checkpoints use the 24-epoch learning-rate schedule. Their comparison with the full-run checkpoints measures continued training under that schedule. The earlier eight-epoch study used its own schedule and remains a historical reference. This tranche supports a matched loss comparison and a within-schedule convergence comparison.

Predeclare three contrasts:

1. **Primary:** full-run Pearson minus full-run MSE.
2. **Secondary:** full-run MSE minus its eight-epoch-prefix candidate.
3. **Secondary:** full-run Pearson minus its eight-epoch-prefix candidate.

Report raw Spearman, MSE on the rescaled rating scale, condition-ordering accuracy, prediction mean and standard deviation, target mean and standard deviation, score range, selected epoch, optimizer steps and measured GPU time. Condition ordering follows the existing [diagnostic](../csts_pilot/diagnostics.py): compare the same passage pair under different conditions with distinct reference ratings, assigning half credit to tied predictions.

Produce learning curves against epochs, optimizer steps and measured GPU time. Include epoch-level training objectives and validation metrics. Pearson training loss and MSE training loss have different meanings; assess arms through the common validation and test metrics.

Recompute metrics independently from saved row-level predictions. Require identical row IDs, targets and group IDs across candidates. Use 2,000 paired bootstrap draws with seed 61021 over the 1,241 connected caption groups in the test set. Reuse each sampled group set across all candidates. Report percentile 95% intervals for the three Spearman and MSE contrasts. Interpret secondary contrasts as exploratory. These intervals measure uncertainty from sampling test groups; variation across training seeds requires repeated runs.

## Calibration diagnostic

Fit a single positive affine map $s_{\mathrm{cal}} = as + c$, with $a > 0$, using validation predictions and ratings. A fixed positive affine map preserves score order. Primary ranking results use raw cosine; calibrated results provide a separate numerical-error diagnostic.

First estimate calibration MSE with five deterministic validation folds separated by connected caption groups. Fit on four folds and score the fifth, then aggregate held-out squared errors. Fit the final coefficients on all validation predictions and freeze them before testing. If the unconstrained slope is zero or negative, retain the identity map and record that outcome. Preserve raw and calibrated predictions as distinct fields. The final map is applied unchanged to test scores, with clipping disabled so its rank-preserving behavior stays explicit.

## Decision rules

Choose the provisional comparison loss using validation Spearman alone. An exact tie retains MSE. Freeze that choice before opening test outputs. Treat a raw Spearman gain of 0.02 as the predeclared practical target for expanding a training change into repeated-seed confirmation; report smaller effects with their costs and intervals. Test scores describe the frozen candidates and their contrasts; later revisions require a new prospective experiment.

If extended training yields a useful gain, carry its selected duration and exact schedule prefix into the matched evidence-supervision controls. If both curves plateau within eight epochs, retain the shorter update allowance and its recorded schedule prefix, including warmup, for the next screen. A newly compressed learning-rate schedule would be a separate experimental change. If a curve is still rising at epoch 24, report convergence as unresolved and propose a separately budgeted extension. If the loss comparison remains ambiguous, retain MSE provisionally and carry both candidates into the next design review.

Evidence-supervision comparisons, stronger-backbone experiments and Spanish JEP testing remain later tranches. The present screen supplies a rating-training reference and a recorded convergence assessment.

## Execution, checks and deliverables

Plan for one L4, sequential execution and roughly 15-20 minutes of fitting, extrapolated from the saved 2.43-2.68-minute eight-epoch rating stages. Provisioning, scoring, native publication and verification add elapsed time. The proposed ceiling is 30 GPU-active minutes across fitting and scoring. Record each category separately. Capacity and environment checks begin after design approval and implementation checks.

Reuse the prepared inputs, pinned model cache and existing native VIPER execution path. Keep tokenized inputs on the GPU where practical and batch both passages together. Publish each completed measurement stage and its exact artifact references before downstream scoring. A reporting or transfer failure resumes from the successful artifacts. Publish scalar results before bulky transfers, verify durable selected checkpoints, then stop the task's GPU after completion. Preserve prior studies and unrelated worktrees.

The implementation keeps the existing encoder and tokenization. Its code can be reviewed in this order:

1. [Frozen settings](../configs/csts-tranche-1.json): model revision, optimizer settings, checkpoint windows, input hashes and the resource ceiling.
2. [Shared rating losses](../csts_pilot/joint.py): MSE and stabilized Pearson with float32 reductions.
3. [Native VIPER stages](../csts_pilot/convergence.py): one saved initialization, matched training, both checkpoint windows and test scoring. Teacher generation and decoder losses remain outside these stages.
4. [Runner](../csts_pilot/convergence_run.py): verify matching arms, freeze selection and calibration, then invoke VIPER test stages. Identical checkpoints reuse one prediction artifact. Successful native stages are reused on resume; an uncertain invocation requires reconciliation.
5. [CPU analysis](../csts_pilot/convergence_analysis.py) and [reporting](../csts_pilot/convergence_report.py): validation calibration, independent metrics, paired intervals and learning curves.

Running `python -m csts_pilot.convergence_run` displays the settings for review. The experiment requires the explicit `--execute` flag. After the native stages finish, `python -m csts_pilot.convergence_report` produces the report using a CPU environment with NumPy, SciPy and Matplotlib.

The runner counts the wall time of GPU stages, including their native publication, against the 1,800-second ceiling. This is a conservative implementation of the proposed compute allowance. Epoch traces separately record fitting and validation times. VM startup and shutdown remain operator actions, to be reviewed before execution.

Required implementation checks:

- Verify MSE and stabilized Pearson values and gradients against hand-computable cases, including constant targets and predictions.
- Verify that both objectives produce gradients through the encoder and similarity projection.
- Verify identical initial weights, batch orders and update counts across arms.
- Verify validation-Spearman selection, earlier-epoch tie handling and the two checkpoint windows.
- Verify that all candidates are frozen before testing and that repeated checkpoint identities reuse saved predictions.
- Verify positive-affine calibration, group-separated folds and calibration coefficients frozen before testing.
- Run Pyrefly, focused regression tests, Ruff formatting checks and Ruff lint checks in the existing project environment.

The completed experiment will publish its frozen configuration, native run and checkpoint references, full epoch traces, row-level predictions, independent metric verification, paired intervals, calibration coefficients, compute accounting and a concise interpretation linked from this PR.

## Review boundary and references

This proposal is based on repository commit `71df70a33a210a0f1347366d9bc774539e95c4ea`. The PR targets `experiment/csts-joint-20261021`. Existing completed measurements retain their source revisions and native identities. The experiment starts after the user's code review and implementation checks.

- [Overall research plan](https://chatgpt.com/space/page_d766bdd5d80881918721acab2cac1e3d)
- [Earlier study protocol](../CSTS_JOINT_RUN.md)
- [Existing encoder, loss and training loop](../csts_pilot/joint.py)
- [Tokenization and optimizer defaults](../csts_pilot/training.py)
- [Partition construction](../csts_pilot/data.py)
- [Prepared data manifest](../training_outputs/csts_joint_results.json)
- [Completed format results and timing](../training_outputs/csts_annotation_format_results.json)
- [Test-label audit](../training_outputs/csts_sol61_max_label_audit.json)
