# Training Qwen and the sentence comparison together

Status: execution authorized on October 28, 2026. The plan and implementation received a second review before fitting. [Plan review](csts-native-comparison-review.md).

## Question and working hypothesis

Can we improve similarity by training Qwen's LoRA weights and the learned comparison together?

**Working hypothesis:** training fresh LoRA factors and the learned comparison together will improve held out similarity relative to the existing ratings model. Qwen can adapt its sentence embeddings to the comparison that scores them. This follow up measures the complete training procedure against that historical control.

The [completed experiment](../training_outputs/csts_readout_convergence_20261028/results.md) held Qwen fixed. A used the final sentence embedding from our proposition trained, similarity trained Qwen model. Adding a learned comparison raised mean test Spearman from 0.863398 to 0.865230. The paired 95% interval for the gain was [0.001108, 0.002569]. Those three comparison fits shared one saved Qwen adapter.

The initial run starts from the original pretrained Qwen3 Embedding 8B checkpoint with freshly initialized LoRA factors and trains directly on similarity ratings. A positive validation result releases two further seeds using the same procedure. A remains the existing historical reference. The proposed change is to train the fresh comparison and LoRA together, using the same rating error. We keep obtaining each sentence embedding from Qwen's final token. Its values can change as LoRA learns.

## What LoRA changes inside Qwen

Each adapted attention matrix has pretrained weights $W_0\in\mathbb{R}^{m\times n}$, where $n$ and $m$ are its input and output widths. LoRA learns smaller matrices $U\in\mathbb{R}^{m\times r}$ and $V\in\mathbb{R}^{r\times n}$. At evaluation, the effective matrix is

```math
W_{\mathrm{effective}}=W_0+\frac{\alpha}{r}UV.
```

The rank $r$ limits the update and the scalar $\alpha$ scales it. Training holds $W_0$ fixed and updates $U,V$. This follows [Hu et al., Section 4.1](https://arxiv.org/pdf/2106.09685). Each attention module has its own factors. Our [encoder implementation](../csts_pilot/baseline_models.py), `load_backbone()`, applies rank 32, scale 32 adapters to the query, key, value and attention output projections in Qwen's transformer blocks. Adapter dropout is 0.05 during training and disabled at evaluation.

Let $\theta\in\mathbb{R}^{P}$ collect all $P$ trainable LoRA factor entries across these modules. LoRA receives its learning signal from the task loss. The sentence embedding retains all $d=4096$ coordinates.

## From the output embedding to the comparison

For each sentence, Qwen reads the condition followed by the sentence and an end of document token. Let $e_1,e_2\in\mathbb{R}^{d}$ be its final token embeddings for the two inputs. Their lengths are finite and positive. Normalize them:

```math
a=\frac{e_1}{\|e_1\|_2},\qquad
b=\frac{e_2}{\|e_2\|_2}.
```

The vectors $a,b\in\mathbb{R}^{d}$ have unit length. The condition influences these vectors through Qwen. `last_token_pool()` in the [encoder](../csts_pilot/baseline_models.py) implements this normalization.

Cosine adds the products of matching coordinates with equal coefficients. With coordinate index $j=1,\ldots,d$,

```math
f_0(a,b)=a^\top b=\sum_{j=1}^{d}a_jb_j.
```

First let the comparison learn an adjustment $w_{p,j}$ to each product coefficient. Writing $w_p\in\mathbb{R}^{d}$ for these adjustments gives

```math
\begin{aligned}
\sum_{j=1}^{d}(1+w_{p,j})a_jb_j
&=\sum_{j=1}^{d}a_jb_j+\sum_{j=1}^{d}w_{p,j}a_jb_j\\
&=a^\top b+w_p^\top(a\odot b).
\end{aligned}
```

Here $\odot$ multiplies matching coordinates. Also allow a learned contribution from their absolute differences, with coefficients $w_d\in\mathbb{R}^{d}$, and a scalar bias $c\in\mathbb{R}$. The complete score is

```math
\begin{aligned}
f_\phi(a,b)
&=a^\top b+w_p^\top(a\odot b)+w_d^\top|a-b|+c,\\
\phi&=[w_d;w_p;c]\in\mathbb{R}^{2d+1}.
\end{aligned}
```

The semicolons concatenate the parameter groups. There are 8,193 comparison parameters. They are shared across sentence pairs, and their signs are learned. A negative difference coefficient makes a larger difference in that coordinate lower the score. This is the function implemented by `SymmetricComparison` in the [comparison code](../csts_pilot/evidence_readout.py).

Swapping the sentences leaves every feature unchanged. Starting the additional weights at zero reproduces cosine:

```math
\begin{aligned}
b^\top a&=a^\top b,& b\odot a&=a\odot b,& |b-a|&=|a-b|,\\
f_\phi(b,a)&=f_\phi(a,b),& f_{\phi=0}(a,b)&=a^\top b.
\end{aligned}
```

The output is a raw scalar. We report its full range alongside the rating error.

## One rating loss trains both components

For training comparison $i=1,\ldots,N$, let $a_i,b_i$ be the normalized embeddings and $y_i\in[0,1]$ the human rating scaled from 1 through 5. The predictions and mean squared error are

```math
\widehat{y}_i=f_\phi(a_i,b_i),\qquad
L_r(\theta,\phi)=\frac{1}{N}\sum_{i=1}^{N}(\widehat{y}_i-y_i)^2.
```

The embeddings depend on $\theta$. Both LoRA and the comparison receive gradients from this same loss: the new runs train $\theta$ and $\phi$ using $f_\phi$.

To see the comparison update, define error $\delta_i=\widehat{y}_i-y_i$ and include the bias in an augmented feature vector $x_i\in\mathbb{R}^{2d+1}$:

```math
x_i=[|a_i-b_i|;a_i\odot b_i;1],\qquad
\nabla_\phi L_r=\frac{2}{N}\sum_{i=1}^{N}\delta_i x_i.
```

Each coefficient learns from the prediction error and the feature that contributed to it. For a single pair, let $\gamma=\mathbf{1}+w_p$, where $\mathbf{1}\in\mathbb{R}^{d}$ contains ones. Differentiating the products and absolute differences gives

```math
\begin{aligned}
g_a=\nabla_a f_\phi
&=\gamma\odot b+w_d\odot\mathrm{sgn}(a-b),\\
g_b=\nabla_b f_\phi
&=\gamma\odot a-w_d\odot\mathrm{sgn}(a-b).
\end{aligned}
```

The sign function acts on each coordinate; at zero difference, use its zero subgradient. Both gradients have $d$ coordinates. For pair loss $\ell=(f_\phi(a,b)-y)^2$ and error $\delta=f_\phi(a,b)-y$, the gradient through normalization is

```math
\begin{aligned}
\nabla_{e_1}\ell
&=\frac{2\delta}{\|e_1\|_2}(I_d-aa^\top)g_a,\\
\nabla_{e_2}\ell
&=\frac{2\delta}{\|e_2\|_2}(I_d-bb^\top)g_b.
\end{aligned}
```

Here $I_d$ is the $d\times d$ identity matrix. Let $J_k=\partial e_k/\partial\theta\in\mathbb{R}^{d\times P}$ for sentence index $k\in\{1,2\}$. The chain rule gives the LoRA update direction:

```math
\nabla_\theta\ell
=J_1^\top\nabla_{e_1}\ell+J_2^\top\nabla_{e_2}\ell.
```

Average these pair gradients over the batch. Joint training therefore lets the comparison teach Qwen how to change its embeddings. Frozen comparison fitting updates the comparison using saved embeddings.

## What regularization means here

The comparison has 8,193 coefficients and 6,051 training pairs. For fixed embeddings, form $X\in\mathbb{R}^{N\times8193}$ with rows $x_i^\top$. Let $s_0,y\in\mathbb{R}^{N}$ contain the cosine scores and ratings. Then

```math
L_r(\phi)=\frac{1}{N}\|X\phi-(y-s_0)\|_2^2,\qquad
\mathrm{rank}(X)\leq6051<8193.
```

Some changes to the coefficients therefore leave every training prediction unchanged. This flexibility motivates standard fitting controls; their benefit for this task remains an empirical question. The completed study already used AdamW weight decay 0.01 and validation stopping, as recorded in its [methods](csts-readout-convergence-methods.md). Reuse these settings for the joint runs. This keeps regularization a fixed implementation choice.

AdamW applies shrinkage separately from its gradient based update. For optimizer step $t$, let $\eta_t>0$ be the comparison learning rate, $\lambda_\phi\geq0$ its decay coefficient, and $u_t\in\mathbb{R}^{8193}$ Adam's direction computed from its gradient history. Its update has the form

```math
\phi_{t+1}=(1-\eta_t\lambda_\phi)\phi_t-\eta_t u_t.
```

Shrinking $w_d,w_p,c$ toward zero favors the current encoder's cosine score. LoRA has its own decay group: shrinking its factors favors a smaller update to the original pretrained matrices. These are distinct reference points. The rating objective remains MSE; decoupled shrinkage belongs to the optimizer. [Loshchilov and Hutter, Section 2 and Algorithm 2](https://arxiv.org/pdf/1711.05101), and the [PyTorch 2.14 AdamW definition](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html), specify this operation.

Rank 32, adapter dropout 0.05 and validation stopping provide additional controls on fitting. Their settings stay fixed in this experiment.

## Initial run and follow on runs

Train one joint model first, using seed 7. It starts from the original pretrained Qwen with freshly initialized LoRA adapters and a zero initialized comparison, $\phi=0$, then trains directly on human similarity ratings. The fit updates both LoRA factors and comparison coefficients. Record the public Qwen revision, fresh adapter initialization digest and empty optimizer state for each parent.

Continue seed 7 using the validation stopping rule below. Define a positive result as a selected checkpoint after a completed training epoch having strictly higher validation Spearman than the saved ratings control on the same frozen validation rows. Compute both values from archived predictions at full precision. The control's published validation Spearman, 0.871875 over 1,576 rows, supplies a reference; the archived predictions determine the exact threshold. Recover any required reference predictions from the saved control checkpoint.

Release seeds 8 and 9 as soon as that positive epoch checkpoint has a sealed Cloud publication. Seed 7 continues to validation patience. Its selected validation score increases on strict improvements, so the positive threshold crossing is preserved through later checkpoint selection. The [release helper](../csts_pilot/native_comparison_release.py) recomputes the full precision validation comparison from immutable checkpoint predictions and publishes the decision before the follow on jobs start. Each independently initializes fresh LoRA and a zero initialized comparison and follows the unchanged configuration. Otherwise, complete the initial trial and publish its result and diagnostics. Record seed 7's validation score, the control score, their difference, input identities and the continuation decision before evaluating test targets.

The training count is one initial native rating fit, plus two conditional fits, for a maximum of three. Reuse the saved ratings control, A and A with comparison for evaluation. Comparison decay stays at 0.01 throughout. Each native run computes its own embeddings during training.

For every rating fit, use one AdamW optimizer with separate parameter groups:

| Parameters | Learning rate | Weight decay |
| --- | --- | --- |
| LoRA factors | 0.00002 | 0.01 |
| Comparison coefficients, including bias | 0.001 | 0.01 |

Use AdamW coefficients 0.9 and 0.999, epsilon $10^{-8}$, logical batch size 32, a physical microbatch selected by the hardware profile below, gradient clipping at 1 over all trained parameters, constant learning rates and rank 32 adapters with scale 32 and dropout 0.05. After constructing every module, set the rating random state to seed plus 2,000. Use a separate rating batch generator at seed plus 10,000. Record both states for reproducible resumption. The encoder uses bfloat16 computation; normalization, comparison and MSE use float32. Joint runs recompute Qwen outputs from token inputs at every update. CUDA uses fused AdamW with the same declared optimizer groups.

Before fitting, profile physical microbatches of 8, 16 and 32 pairs on A100 hardware, or 2, 4 and 8 pairs on L4 hardware. Each profile computes gradients for the same logical batch of the 32 longest training comparisons, then clears gradients. Select the fastest successful candidate and record timing and peak allocation. Verify unchanged parameter bytes and reset random states before the initial validation pass. The logical batch size and pair weighting stay fixed. This profile selects memory use and throughput.

Evaluate validation Spearman after each epoch, with dropout disabled. Initialization is eligible. Keep the first strictly best checkpoint for each model. Each fit continues until ten epochs have passed since its own last improvement, with an initial ceiling of 48 epochs. Record a ceiling case as incomplete and continue from its saved state before final evaluation. Report both selected and terminal epochs and actual updates. These learning rates define this experiment's starting protocol; their optimality is a separate empirical question.

## Inputs, evaluation and diagnostics

Use the frozen rating input identities in the [readout configuration](../configs/csts-evidence-readout.json): 6,051 training, 1,576 validation and 2,431 test comparisons. Restore each required input through its sealed VIPER Cloud artifact and verify its declared hash once on loading. Pin the fresh encoder to public Qwen revision `c90816d848505624c2434128dfc61132162a0ee9`, tokenizer, prompt, maximum input length 160 and all 4,096 output coordinates. The [completed run references](../training_outputs/csts_readout_convergence_20261028/cloud-receipts.json) locate historical reference predictions. Retain A's model identity, SHA256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`, as reference provenance. The native fitting inputs are sentence pairs, conditions and their human similarity ratings.

Use training and validation for fitting, stopping and the decision to release further seeds. Freeze the executed seed list and the training and stopping rules before evaluating test targets. For each completed fit, freeze its selected model and publish its test score. The remaining fits continue under the committed validation rule. Publish the aggregate report after all three fits complete. The primary comparison is each fresh joint model against the saved ratings control from the [completed proposition study](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md), which reported Spearman 0.855375 over 2,430 test comparisons. Preserve that control's checkpoint, selected epoch and original training history. Reuse its archived predictions; evaluation from its saved checkpoint can recover any required predictions.

Join reference and new predictions by frozen input identities. Report paired differences on their verified common rows, with row counts, source group counts and input hashes. Also report each new model on all 2,431 current test comparisons. A and A with comparison supply secondary historical references. Report Spearman and normalized MSE for every executed seed, with 2,000 paired source group bootstrap draws. If the follow on seeds run, report their results alongside seed 7 and the three seed mean. Within each draw, recompute every model difference on the same sampled groups, then average across executed new seeds. Report seed variation when available, and identify the three seed summary as conditional on the initial validation result. The reused control supplies one historical training seed; intervals describe test source uncertainty conditional on these retained models. The result measures the complete new procedure relative to that saved control, with differences in training history retained in its interpretation. The existing test supplies exploratory evidence; confirmation uses fresh reserved source groups.

Record training and validation loss, validation Spearman, coefficient norms, bias, LoRA factor norms, gradient norms for both parameter groups, prediction ranges, residual score ranges and selected checkpoint hashes. Measure embedding changes against each run's initial validation embeddings using the existing validation forwards. Report the six fixed [edit cases](../configs/csts-readout-interventions.json), condition families and ordering across conditions for the same sentence pair.

## Implementation and execution contract

The [completed fit scoring driver](../scripts/score_completed_csts_native.py) publishes each finished model's test result while the other fits continue. This reporting schedule was adopted on October 28 at 17:50 Eastern, following the request for test scores and before the first new test evaluation.

The [native stages](../csts_pilot/native_comparison.py) and [run controller](../csts_pilot/native_comparison_run.py) save and restore LoRA and comparison weights together, with an explicit scorer kind, both optimizer groups, batch order state, random number state, source commit and input hashes. Prediction after restore must use the saved comparison. The existing [cosine training stages](../csts_pilot/baseline_stages.py) and [comparison module](../csts_pilot/evidence_readout.py) supply the components; the [native configuration](../configs/csts-native-comparison.json) binds their joint execution.

The [focused integration tests](../tests/test_native_comparison.py) check cosine initialization, sentence order symmetry, the derived gradients, frozen pretrained weights, active LoRA and comparison group gradients on a controlled example, batch accumulation, and prediction equality after saving and restoring both components. Accumulated rating loss divides the sum of pair errors by the actual logical batch size, including its final partial batch. Source and configuration are committed before fitting. Successful measurement artifacts retain their original identities through later reporting or recovery.

Use the existing VIPER native execution, resume and Cloud publication facilities. Epoch checkpoints, models, optimizer state, traces, validation predictions and final evaluation artifacts publish asynchronously while fitting continues. Verify their publication receipts before releasing a worker. Stream progress and the continuation decision to Markdown and publish completed epoch summaries to GitHub. Use an available authorized L4 or A100 worker for seed 7. A positive validation result releases the two follow on runs to available workers. Preserve other jobs through the shared GPU locks. An epoch snapshot can also transfer a running fit from L4 to A100. The [controller](../csts_pilot/native_comparison_run.py) restores the complete sealed model, optimizer, random state, batch order and selected checkpoint through a snapshot manifest. It profiles the destination microbatch and restores the saved random state again before continuing. The source is released after destination progress is verified. Record the source and destination hardware and the retained epoch boundary.

The A100 high memory allocation is attempted first, with assigned VRAM verified inside the kernel. The 40 GB A100 is the declared fallback. Follow on L4 workers start after the positive validation decision. Confirm native Cloud publication receipts and final report delivery before shutting down each task owned runtime. Preserve unrelated jobs.

## Sources

- JEP: [completed results](../training_outputs/csts_readout_convergence_20261028/results.md), [completed methods](csts-readout-convergence-methods.md) and [Cloud receipts](../training_outputs/csts_readout_convergence_20261028/cloud-receipts.json), October 28, 2026.
- JEP: [encoder](../csts_pilot/baseline_models.py), `load_backbone()` and `last_token_pool()`; [comparison](../csts_pilot/evidence_readout.py), `SymmetricComparison`. Inspected source: `809082f627c98bea466c893c9cc99344e62ba4bd`.
- Hu et al.: [LoRA: Low Rank Adaptation of Large Language Models](https://arxiv.org/pdf/2106.09685), Section 4.1, 2021, for the adapter parameterization.
- Loshchilov and Hutter: [Decoupled Weight Decay Regularization](https://arxiv.org/pdf/1711.05101), Section 2 and Algorithm 2, ICLR 2019, for AdamW.
- PyTorch: [AdamW, version 2.14](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html), optimizer update and parameter group definitions.
