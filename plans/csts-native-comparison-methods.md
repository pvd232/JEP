# Training Qwen and the sentence comparison together

Status: proposed experiment, awaiting user review. [Plan review](csts-native-comparison-review.md).

## Question and working hypothesis

Can we improve similarity by training Qwen's LoRA weights and the learned comparison together?

**Working hypothesis:** joint training will improve held out similarity over matched cosine training because Qwen can adapt its sentence embeddings to the comparison that scores them. A small regularization study will measure how shrinking the comparison weights affects validation performance.

The [completed experiment](../training_outputs/csts_readout_convergence_20261028/results.md) held Qwen fixed. A used the final sentence embedding from our proposition trained, similarity trained Qwen model. Adding a learned comparison raised mean test Spearman from 0.863398 to 0.865230. The paired 95% interval for the gain was [0.001108, 0.002569]. Those three comparison fits shared one saved Qwen adapter.

Every new encoder run starts from the original pretrained Qwen3 Embedding 8B checkpoint with freshly initialized LoRA factors. A remains the existing frozen reference. The proposed change is to train the fresh comparison and LoRA together, using the same rating error. We keep obtaining each sentence embedding from Qwen's final token. Its values can change as LoRA learns.

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

The embeddings depend on $\theta$. Both LoRA and the comparison receive gradients from this same loss. The cosine control trains $\theta$ using $a_i^\top b_i$. The learned comparison trains $\theta$ and $\phi$ using $f_\phi$.

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

Some changes to the coefficients therefore leave every training prediction unchanged. This establishes flexibility in the fitted coefficients. Validation measures how that flexibility affects new predictions. The completed study already used AdamW weight decay 0.01 and validation stopping, as recorded in its [methods](csts-readout-convergence-methods.md). The new decay study will estimate the contribution of this choice.

AdamW applies shrinkage separately from its gradient based update. For optimizer step $t$, let $\eta_t>0$ be the comparison learning rate, $\lambda_\phi\geq0$ its decay coefficient, and $u_t\in\mathbb{R}^{8193}$ Adam's direction computed from its gradient history. Its update has the form

```math
\phi_{t+1}=(1-\eta_t\lambda_\phi)\phi_t-\eta_t u_t.
```

Shrinking $w_d,w_p,c$ toward zero favors the current encoder's cosine score. LoRA has its own decay group: shrinking its factors favors a smaller update to the original pretrained matrices. These are distinct reference points. The rating objective remains MSE; decoupled shrinkage belongs to the optimizer. [Loshchilov and Hutter, Section 2 and Algorithm 2](https://arxiv.org/pdf/1711.05101), and the [PyTorch 2.14 AdamW definition](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html), specify this operation.

Rank 32, adapter dropout 0.05 and validation stopping provide additional controls on fitting. Their settings stay fixed in this experiment.

## Regularization screen using saved embeddings

First fit comparison heads on A's saved training and validation embeddings with comparison decay 0, 0.01 and 0.1. A's encoder stays frozen throughout this CPU reference study. Use seeds 7, 8 and 9, identical batches across decay settings within each seed, zero initialization, AdamW learning rate 0.001, batch size 32 and gradient clipping at 1. Keep initialization eligible. Select the first strictly best validation Spearman; stop after ten further epochs, with a 256 epoch ceiling.

This is nine inexpensive fits using existing features. It requires CPU computation and retains the original Qwen measurements. Select one decay by mean selected validation Spearman across the three seeds. An exact tie chooses stronger decay. Publish every validation curve, selected epoch, MSE and coefficient norm. This selects a comparison decay setting for the first joint experiment; its behavior during joint fitting remains part of the measurement.

Retain the selected frozen comparison for evaluation alongside the native models. This provides a reference using the same comparison decay as joint training. The historical 0.865230 result remains a separate reference at decay 0.01.

## Paired native training runs

Start each seed from the original pretrained Qwen with fresh LoRA adapters. Train its proposition phase once, then fork the resulting fresh checkpoint into two rating runs:

| Rating run | Score | Parameters updated |
| --- | --- | --- |
| Fresh cosine control | Cosine of the final embeddings | Freshly trained LoRA factors |
| Fresh learned comparison | Learned symmetric comparison of the final embeddings | Freshly trained LoRA factors and comparison coefficients |

Use seeds 7, 8 and 9. Each seed independently initializes and trains its own LoRA factors. Within a seed, the two rating runs share the exact proposition checkpoint. These are six rating fits plus three shared writing fits. Initialize each native comparison at $\phi=0$; the CPU screen supplies its decay setting. Record the fresh adapter initialization digest and the writing checkpoint as the rating parent. A supplies reference predictions and saved features for the separate comparison screen.

For the fresh writing phase, use five complete passes over the original training comparisons with at least one accepted proposition answer, filtered to the pinned current training partition. Use the existing answer loss, frozen vocabulary head and complete accepted targets. Tokenize the accepted training answers once, record their maximum length including the terminal token, and bind that value as the training answer ceiling. Each answer contributes its mean causal cross entropy. Use LoRA learning rate 0.00002, decay 0.01, batch size 32, microbatch size 2 and clipping at 1, with the AdamW and adapter settings below. Share the terminal writing checkpoint within the seed, and start fresh rating optimizers. This preserves the proposition then ratings schedule as a declared training choice. Record the eligible rows and update count. The [writing helpers](../csts_pilot/qwen_evidence.py), including `answer_loss_sum()`, define the existing calculations.

For every rating fit, use one AdamW optimizer with separate parameter groups:

| Parameters | Learning rate | Weight decay |
| --- | --- | --- |
| LoRA factors | 0.00002 | 0.01 |
| Comparison coefficients, including bias | 0.001 | Selected screen value |

Use AdamW coefficients 0.9 and 0.999, epsilon $10^{-8}$, batch size 32, microbatch size 2, gradient clipping at 1 over all trained parameters, constant learning rates and rank 32 adapters with scale 32 and dropout 0.05. Preserve matching batch orders within each seed for overlapping epochs. After constructing and restoring every module, reset the writing random state to seed plus 1,000 and the rating random state to seed plus 2,000. Use a separate rating batch generator at seed plus 10,000. This aligns adapter dropout within each pair, including the first batch. The encoder uses bfloat16 computation; normalization, comparison and MSE use float32. Joint runs recompute Qwen outputs from token inputs at every update.

Evaluate validation Spearman after each epoch, with dropout disabled. Initialization is eligible. Keep the first strictly best checkpoint for each model. Each fit continues until ten epochs have passed since its own last improvement, with an initial ceiling of 48 epochs. Record a ceiling case as incomplete and continue from its saved state before final evaluation. Report both selected and terminal epochs and actual updates. These learning rates define this experiment's starting protocol; their optimality is a separate empirical question.

## Inputs, evaluation and diagnostics

Use the original frozen input identities in the [readout configuration](../configs/csts-evidence-readout.json): 6,051 training, 1,576 validation and 2,431 test comparisons. Restore each required input through its sealed VIPER Cloud artifact and verify its declared hash once on loading. The [completed run references](../training_outputs/csts_readout_convergence_20261028/cloud-receipts.json) locate the retained reference models and features; the original writing provenance supplies the vocabulary head and writing targets. Bind those writing inputs to the head and target hashes in the readout configuration before the fresh phase. Pin the fresh encoder to public Qwen revision `c90816d848505624c2434128dfc61132162a0ee9`, tokenizer, prompt, maximum embedding input length 160 and all 4,096 output coordinates. Writing sequences append their complete targets to that prefix. Bind A as a reference artifact by SHA256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`.

Use training and validation for fitting, decay selection and stopping. Freeze all selected states and the regularization decision before loading test targets. The primary comparison is fresh joint training minus fresh cosine training. Secondary comparisons measure fresh joint training against the selected frozen comparison and both fresh models against historical A and A with comparison. Report each seed, mean Spearman and normalized MSE, with 2,000 paired source group bootstrap draws over the 1,222 test groups. All model differences are recomputed within each draw and averaged across seeds. Report seed variation separately. The existing test supplies exploratory evidence; confirmation uses fresh reserved source groups.

Record training and validation loss, validation Spearman, coefficient norms, bias, LoRA factor norms, gradient norms for both parameter groups, prediction ranges, residual score ranges and selected checkpoint hashes. Measure embedding changes against each run's initial validation embeddings using the existing validation forwards. Report the six fixed [edit cases](../configs/csts-readout-interventions.json), condition families and ordering across conditions for the same sentence pair. Reuse the 121 writing validation targets and 32 deterministic generations, with a 64 token generation limit, to measure writing retention after rating training.

## Implementation and execution contract

The new native training and evaluation stages will save and restore LoRA and comparison weights together, with an explicit scorer kind, both optimizer groups, batch order state, random number state, source commit and input hashes. Prediction after restore must use the saved comparison. The existing [cosine training stages](../csts_pilot/baseline_stages.py) and [comparison module](../csts_pilot/evidence_readout.py) supply the components; native joint execution is the implementation work that follows plan review.

Before scientific fitting, perform focused checks of cosine initialization, sentence order symmetry, the derived gradients, frozen pretrained weights, active LoRA and comparison group gradients on a controlled example, batch accumulation, and prediction equality after saving and restoring both components. Accumulated rating loss divides the sum of pair errors by the actual logical batch size, including its final partial batch. Writing loss divides by the actual number of accepted answers in that logical batch. Source and configuration are committed before fitting. Successful measurement artifacts retain their original identities through later reporting or recovery.

Use the existing VIPER native execution, resume and Cloud publication facilities. Epoch checkpoints, models, optimizer state, traces, validation predictions and final evaluation artifacts publish asynchronously while fitting continues. Verify their publication receipts before releasing a worker. Stream progress to Markdown. Use available authorized L4 or A100 workers for independent runs and preserve other jobs through the shared GPU locks. Execution follows user review of this plan.

## Sources

- JEP: [completed results](../training_outputs/csts_readout_convergence_20261028/results.md), [completed methods](csts-readout-convergence-methods.md) and [Cloud receipts](../training_outputs/csts_readout_convergence_20261028/cloud-receipts.json), October 28, 2026.
- JEP: [encoder](../csts_pilot/baseline_models.py), `load_backbone()` and `last_token_pool()`; [comparison](../csts_pilot/evidence_readout.py), `SymmetricComparison`; [writing loss](../csts_pilot/qwen_evidence.py), `answer_loss_sum()`. Inspected source: `809082f627c98bea466c893c9cc99344e62ba4bd`.
- Hu et al.: [LoRA: Low Rank Adaptation of Large Language Models](https://arxiv.org/pdf/2106.09685), Section 4.1, 2021, for the adapter parameterization.
- Loshchilov and Hutter: [Decoupled Weight Decay Regularization](https://arxiv.org/pdf/1711.05101), Section 2 and Algorithm 2, ICLR 2019, for AdamW.
- PyTorch: [AdamW, version 2.14](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html), optimizer update and parameter group definitions.
