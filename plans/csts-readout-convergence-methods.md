# Training the sentence heads to a validation plateau

This extends the [completed experiment](../training_outputs/csts_evidence_readout_20261028/progress.md) and its [diagnosis](../training_outputs/csts_evidence_readout_20261028/diagnosis.md). The user requested full B/C fitting at a selected learning rate, new D/E comparisons and the same comparison fitted directly on A's final vectors. [Results stream](../training_outputs/csts_readout_convergence_20261028/progress.md).

The follow up is complete. [Final results and interpretation](../training_outputs/csts_readout_convergence_20261028/results.md) include all selected models, training durations, controlled edits and paired bootstrap intervals. The selected rates are 0.0001 for B and 0.00003 for C. All nine candidates reached the declared validation stopping rule.

## Question and hypothesis

**Hypothesis:** smaller steps allow the token weighting models to learn useful sentence vectors for longer. A learned comparison can improve the ordering of sentence pairs, including pairs represented by A's final vectors. Quotation supervision may contribute additional information after each model receives equal resources for learning rate selection.

Use the same frozen Qwen checkpoint and its retained token states. Every sentence vector keeps all 4,096 coordinates. The 128 coordinate query and key projections determine the attention weights. The original attention formula, evidence coefficient and rating targets stay fixed for this test.

## B and C through validation stopping

B learns attention weights from ratings. C has the same architecture and adds the quotation loss with coefficient 0.1. Their full derivations appear in the [original methods](csts-evidence-readout-methods.md).

Fit each candidate learning rate, 0.00001, 0.00003 and 0.0001, with seeds 7, 8 and 9. The middle candidate fills the interval between the two rates examined in the diagnostic probe. Each pair starts from the same weights and uses the same batch order. Use AdamW, weight decay 0.01, batch size 32 and gradient clipping at 1. Each fit starts from initialization and has its own optimizer and permutation generator.

Evaluate validation Spearman after every epoch. Keep each model's first strictly best checkpoint, including initialization. Continue both models until ten epochs have passed since either one improved its best validation score. Both models receive the same number of updates within each candidate and seed. This defines completion as a validation plateau. Record the training losses as well.

The ceiling is 256 epochs for each candidate and seed. A fit reaching the ceiling is marked incomplete and requires further fitting before learning rate selection. The selection function rejects such candidates. Each epoch retains the current weights, selected weights, optimizer state and batch generator state in the native resume artifact. Completed candidate models and terminal optimizer states are retained together.

For each objective, average the three seeds' selected validation Spearman at each rate. Choose the rate with the highest mean. An exact tie chooses the smaller rate. The selected rate applies to all three seeds for that objective. This finds the best rate in the declared grid. B and C can select different rates. Report every candidate, seed, selected epoch, terminal epoch and stopping reason.

## D, E and a learned comparison of A

After learning rate selection, freeze the selected B and C weights and their sentence vectors. Fit D using B's vectors and E using C's vectors. Also fit the same function using A's normalized final end of document vectors.

For any pair of unit sentence vectors $a,b\in\mathbb{R}^{4096}$, use

```math
f(a,b)=a^\top b+w_d^\top|a-b|+w_p^\top(a\odot b)+c.
```

The first term is cosine similarity. The learned vectors $w_d,w_p\in\mathbb{R}^{4096}$ score absolute coordinate differences and matching coordinate products; $\odot$ denotes multiplication of matching coordinates, and $c\in\mathbb{R}$ is a learned constant. The function maps two unit vectors to a scalar. It has 8,193 parameters and gives the same prediction when sentence order is reversed. Initialize all additional parameters at zero. The initial function then equals the original cosine score for that representation. `SymmetricComparison.forward()` in the [implementation](../csts_pilot/evidence_readout.py) realizes this function.

Fit all three comparison functions with ratings MSE, AdamW, learning rate 0.001, weight decay 0.01, batch size 32 and clipping at 1. Use the same batches for all three functions, with permutation seed equal to head seed plus 10,000. Initialization is eligible for selection. Select each function's first strictly best validation Spearman. Continue until ten epochs have passed since any function improved, with the same 256 epoch ceiling and explicit incomplete status.

This comparison isolates the scoring function on identical fixed vectors. The selected B/C vectors receive zero comparison gradients. Verify their parameter hashes before and after fitting.

## Inputs, evaluation and diagnostics

Rebuild training and validation caches from the original model and input files restored through sealed VIPER Cloud references. The model, rows and quotation records retain their original hashes. The configuration binds the completed parent study at source `f59d2f8c5c64b96940a624a56d385330cf6a11ca`. Verify the parent summary, input hashes, new cache hashes and frozen encoder identity. There are 6,051 training, 1,576 validation and 2,431 test comparisons. The fitting worker receives training and validation inputs. Seal all selected models and learning rates, then extract test and fixed edit features for evaluation.

Report A, B, C, D, E and A with its learned comparison for every seed. The primary new contrast is A with comparison minus A. Also report D minus A, E minus A, B minus A, C minus A, C minus B, E minus D, D minus B and E minus C. Include normalized MSE and Spearman for every model, plus all 2,000 draw paired source group bootstrap intervals across the 1,222 test groups.

C minus B and E minus D now compare separately tuned objectives with equal search resources. Their interpretation includes the chosen learning rates. Candidate validation trajectories also retain comparisons at each common rate. D minus B and E minus C hold their sentence vectors fixed while fitting the comparison function.

Record rating loss, quotation loss, teacher agreement, query and key weight norms, attention entropy, the fraction of occurrences with over 99% weight on one token, null probability and the first batch gradient diagnostics each epoch. Evaluation includes all six fixed edit cases, condition results, comparisons across conditions for the same sentence pair and condition families. Null probability supplies a separate addressability measurement. The original test has informed this follow up, so this evaluation is exploratory. Fresh reserved examples and additional backbone seeds would support confirmation.

## Execution and review

The recovery divides fitting across two L4 workers and an A100 worker when available. Each worker fits one seed at every declared learning rate. The coordinator collects all nine candidates and applies the original mean validation selection across seeds. D, E and the comparison on A then use the globally selected rates. Every worker uses the same sealed feature files and records its actual hardware.

Each fitting epoch saves an immutable copy of its current and selected weights, optimizer, batch generator and history. A CPU thread publishes these snapshots through VIPER's existing file publication API. The first snapshot completes a Cloud restore with a matching hash before the second epoch. Later uploads proceed during fitting. Completed candidate bundles, comparison checkpoints and publication receipts are retained through the same native API. Fitting completion waits for these receipts.

The [configuration](../configs/csts-readout-convergence.json) declares the grid and stopping rules. The [native stages](../csts_pilot/evidence_readout_convergence.py) fit and evaluate the models. The [controller](../csts_pilot/evidence_readout_convergence_run.py) consumes the rebuilt native artifacts under the shared GPU lock on a Colab A100 with 40 GB memory. Cache extraction, fitting and evaluation use native VIPER runs. The existing publication queue invokes VIPER Cloud promotion in separate processes as each stage completes. Publication receipts record the sealed Cloud references.

Review covers equal seed coverage, rate selection using validation alone, tie handling, rejection of incomplete fits, initialization selection, checkpoint retention, full coordinate values and frozen B/C parameters during comparison fitting. Five focused tests passed in the L4 environment. The earlier implementation passed 72 related tests and three publisher tests. The completed native evaluation exercised stored model transport, sealed test inputs and the separate metric worker. Scientific execution uses the committed source and configuration. The Markdown stream reports extraction, every epoch and the final results.

## Proposed next step: train Qwen and the comparison together

This section proposes a new experiment. The completed measurements above used frozen Qwen features. The [results](../training_outputs/csts_readout_convergence_20261028/results.md#what-this-changes) motivate adapting Qwen's LoRA weights together with the comparison function. The working hypothesis is that joint fitting can improve similarity by adapting the final sentence vector to the learned coordinate weights.

For training comparison $i=1,\ldots,N$, let $x_{i1},x_{i2}$ be the two input texts, each containing the condition and one sentence, and let $y_i\in[0,1]$ be the normalized human rating. The vector $\theta\in\mathbb{R}^{p}$ contains Qwen's $p$ trainable LoRA parameters. The underlying pretrained model weights stay fixed. Let $e_\theta(x)\in\mathbb{R}^{4096}$ be Qwen's final token vector with a finite positive length. The vector $\phi\in\mathbb{R}^{8193}$ contains the comparison parameters $w_d,w_p,c$ defined above.

Normalize the final vector and use the learned comparison in the rating objective:

```math
\begin{aligned}
z_\theta(x)
&=\frac{e_\theta(x)}{\|e_\theta(x)\|_2},\\
\widehat{y}_i
&=f_\phi\bigl(z_\theta(x_{i1}),z_\theta(x_{i2})\bigr),\\
L_r(\theta,\phi)
&=\frac{1}{N}\sum_{i=1}^{N}(\widehat{y}_i-y_i)^2.
\end{aligned}
```

Here $z_\theta(x)\in\mathbb{R}^{4096}$ has unit length and $f_\phi$ is the symmetric function above. Both $\theta$ and $\phi$ receive rating gradients. Initialize $\phi$ at zero to begin at the encoder's cosine score. The existing `last_token_pool()` in the [encoder](../csts_pilot/baseline_models.py) supplies the normalized final vector, and `SymmetricComparison` in the [head implementation](../csts_pilot/evidence_readout.py) supplies the comparison. Joint fitting is proposed work.

The chain rule explains the change in learning. Write $z_{ij}=z_\theta(x_{ij})$ and $J_{ij}=\partial z_{ij}/\partial\theta\in\mathbb{R}^{4096\times p}$, where $j\in\{1,2\}$ identifies the sentence. Differentiating each squared rating error gives

```math
\nabla_\theta L_r
=\frac{2}{N}\sum_{i=1}^{N}(\widehat{y}_i-y_i)
\sum_{j=1}^{2}J_{ij}^{\top}\nabla_{z_{ij}}f_\phi(z_{i1},z_{i2}).
```

The gradient of the score with respect to each sentence vector has 4,096 coordinates. At equal coordinates, the absolute difference term uses a subgradient. Multiplication by $J_{ij}^{\top}$ gives a gradient with $p$ coordinates for the LoRA parameters. The comparison can therefore teach Qwen how to change its representation. The completed study optimized the comparison on cached vectors; the proposed study keeps the encoder forward pass in the training graph.

Use paired cosine and learned comparison runs for each of two starting points: the current A adapter and fresh LoRA adapters on the original pretrained Qwen3 Embedding 8B checkpoint. Within each pair, match the encoder initialization, training rows, batches, tuning resources and stopping policy. The fresh pair shares the same proposition training phase, then uses its assigned score from the first rating update. The continuation pair measures the value of further fitting from A. Compare both joint models with the existing frozen A plus comparison reference. Additional adapter seeds and fresh reserved evaluation examples provide the next confirmation setting.

A simultaneous proposition objective is a separate proposed factor. Define $L_p(\theta)$ as the existing scalar mean causal cross entropy for writing the accepted proposition answers, implemented by `answer_loss_sum()` in the [writing stage](../csts_pilot/qwen_evidence.py). With a validation selected scalar weight $\lambda_p\geq0$, the joint objective would be

```math
L(\theta,\phi)=L_r(\theta,\phi)+\lambda_p L_p(\theta).
```

The writing targets and the quotation positions used by C define different losses. Treat $\lambda_p$ as its own experimental choice. The first native comparison test can preserve the original proposition then ratings schedule; a subsequent matched test can measure simultaneous writing supervision.
