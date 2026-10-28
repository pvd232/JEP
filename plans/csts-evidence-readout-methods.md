# Testing evidence selection and sentence comparison in JEP

Completed on the Colab A100. [Results](../training_outputs/csts_evidence_readout_20261028/progress.md). [Diagnosis and proposed follow up](../training_outputs/csts_evidence_readout_20261028/diagnosis.md).

The [next fitting run](csts-readout-convergence-methods.md) selects learning rates, trains B/C to a validation plateau and fits comparisons for A, D and E.

## Question and hypothesis

The [previous experiment](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md) improved test Spearman from 0.855375 to 0.863398 after training Qwen to write propositions before learning similarity ratings. The paired difference was 0.008024, with a 95% interval of [−0.000163, 0.015949]. The models used one backbone seed and different numbers of rating updates. This experiment examines how evidence selection and sentence comparison contribute to that result.

**Hypothesis:** proposition training encodes facts relevant to the condition. Evidence quotations could improve which sentence information contributes to the score. A learned comparison function could improve how that information is scored. We test these separately.

All five models use the same final proposition checkpoint: Qwen3 Embedding 8B with its existing LoRA weights. Qwen stays frozen. Its vectors retain all 4,096 coordinates. The new components convert Qwen's token vectors directly into similarity scores.

## A: the existing similarity score

For each sentence, Qwen reads the condition, then the sentence, then an end of document token. Let $e_1,e_2\in\mathbb{R}^{4096}$ be its final layer vectors at that last token for the two sentences. Divide each vector by its length, then take their dot product:

```math
\widehat y_A
=\frac{e_1^\top e_2}{\|e_1\|_2\|e_2\|_2}.
```

This is cosine similarity. A uses the saved model parameters and supplies the reference score for evaluating B through E.

## B: learn which sentence tokens to average, using ratings

Qwen produces a vector at every input token. Let $r_j\in\mathbb{R}^{4096}$ describe condition token $j$, for $j=1,\ldots,n$. Let $h_t\in\mathbb{R}^{4096}$ describe sentence token $t$, for $t=1,\ldots,T$. Each vector includes information from preceding input tokens. The condition comes first; its vectors incorporate the condition and preceding prompt text.

Average the condition vectors to obtain $u$. Two learned matrices $W_q,W_k\in\mathbb{R}^{128\times4096}$ turn it into a vector $q$ containing 128 numbers and each sentence token into a vector $k_t$ containing 128 numbers. Their dot product gives token score $\ell_t$:

```math
\begin{aligned}
u&=\frac1n\sum_{j=1}^{n}r_j,\\
q&=W_q\mathrm{LN}(u),\qquad k_t=W_k\mathrm{LN}(h_t),\\
\ell_t&=\frac{q^\top k_t}{\sqrt{128}}.
\end{aligned}
```

Here LN subtracts each vector's coordinate mean, then divides by the square root of (coordinate variance plus $10^{-5}$) for stability. Token scoring uses 128 coordinates and square root scaling. Averaging the condition vectors and choosing 128 are design choices to test.

Convert the token scores into positive weights summing to one. Average the original sentence vectors using those weights, then divide by the result's length:

```math
\alpha_t=\frac{\exp(\ell_t)}{\sum_{a=1}^{T}\exp(\ell_a)},
\qquad v=\sum_{t=1}^{T}\alpha_t h_t,
\qquad z=\frac{v}{\|v\|_2}.
```

The index $a$ runs over sentence tokens. Compute $z$ separately for each sentence. B predicts $\widehat y_B=z_1^\top z_2$. The resulting sentence vectors have 4,096 coordinates.

For comparison $i$, convert the human rating to $y_i=(\mathrm{rating}_i-1)/4$. For a batch of $m$ comparisons, minimize mean squared error:

```math
L_r=\frac1m\sum_{i=1}^{m}(\widehat y_i-y_i)^2,
\qquad L_B=L_r.
```

The rating loss trains B's token weights. B and C each add 1,048,705 parameters.

## C: the same calculation, also trained on evidence quotations

C has exactly B's architecture. Its additional training labels are existing teacher quotations copied from the input sentence. Quotation positions provide the targets for token weighting.

Both models also contain a vector $k_0\in\mathbb{R}^{128}$ and scalar $b_0$ for an “unspecified property” option. Include this option when calculating evidence probabilities:

```math
\begin{aligned}
\ell_0&=\frac{q^\top k_0}{\sqrt{128}}+b_0,\\
Z&=\exp(\ell_0)+\sum_{a=1}^{T}\exp(\ell_a),\\
p_t&=\frac{\exp(\ell_t)}{Z},\qquad t=0,\ldots,T.
\end{aligned}
```

For labeled sentence occurrence $s$, $p_{st}$ and $g_{st}$ are predicted and target probabilities. Valid quotations divide probability equally across the union of their overlapping tokens. A teacher record marking the property as unspecified assigns all probability to option zero. Evidence supervision covers complete quotations with unique matches and explicit unspecified records. Rating supervision covers every comparison.

Since target probabilities sum to one, substituting the expression for $p$ gives the evidence loss below. Average it over $S$ labeled occurrences, then add it to rating loss:

```math
\begin{aligned}
E_s&=-\sum_{t=0}^{T_s}g_{st}\log p_{st}
=\log Z_s-\sum_{t=0}^{T_s}g_{st}\ell_{st},\\
\frac{\partial E_s}{\partial\ell_{st}}&=p_{st}-g_{st},\\
L_e&=\frac1S\sum_{s=1}^{S}E_s,\qquad L_C=L_r+0.1L_e.
\end{aligned}
```

$T_s$ is its sentence token count and $Z_s$ its probability denominator. The derivative sets each token's training signal to predicted probability minus target probability. Set $L_e=0$ for a batch containing zero labeled occurrences.

C's prediction is also $\widehat y_C=z_1^\top z_2$, using its own learned token weights.

Both models construct $z$ using weights over sentence tokens. The unspecified property probability supplies an addressability diagnostic. For example, joint probabilities 0.90 for the unspecified option and 0.06/0.04 for two tokens produce sentence weights 0.60/0.40. Independent normalization keeps token weights stable across the full range of unspecified property probabilities. Initialize $k_0$ and $b_0$ at zero. C's evidence loss supplies their training gradients.

## D and E: learn how to compare fixed sentence vectors

Cosine adds coordinate products with equal weight. Allow different weights for these products, plus a learned contribution from absolute coordinate differences and a constant:

```math
\begin{aligned}
f(z_1,z_2)
&=z_1^\top z_2+w_d^\top|z_1-z_2|
+w_p^\top(z_1\odot z_2)+b\\
&=\sum_{j=1}^{4096}\left[(1+w_{p,j})z_{1j}z_{2j}
+w_{d,j}|z_{1j}-z_{2j}|\right]+b.
\end{aligned}
```

Here $j$ indexes coordinates, $\odot$ multiplies matching coordinates, $w_d,w_p\in\mathbb{R}^{4096}$ are learned weights, and $b$ is a scalar. The formula gives the same score in either sentence order. Starting all 8,193 new parameters at zero reproduces cosine exactly.

**D** applies this function to B's selected, frozen vectors. **E** applies it to C's selected, frozen vectors. Writing $f_D,f_E$ for the separately fitted functions and superscripts B/C for the vectors they receive:

```math
\begin{aligned}
\widehat y_D&=f_D(z_1^B,z_2^B),\\
\widehat y_E&=f_E(z_1^C,z_2^C),\qquad L_D=L_E=L_r.
\end{aligned}
```

Fit both functions using rating MSE. Training updates $w_d,w_p,b$. The selected sentence vectors stay fixed. Each function learns weights for matching coordinate products and absolute differences. Report the raw predictions.

## Data and fitting

Use 6,051 training, 1,576 validation and 2,431 test comparisons from `jep-csts-v1.1`. Recompute A and the previous ratings control on these rows because the historical test had 2,430. Existing teacher data contains 11,909 inputs: 11,079 answered, 802 unspecified and 28 ambiguous. Literal quotation matching establishes exact text locations through unique matches. The teacher supplies the semantic labels.

For seeds 7, 8 and 9, train B/C together from identical initial weights and identical batches. Then select their weights, freeze them and fit D/E. Each phase uses AdamW, learning rate 0.001, weight decay 0.01, batch size 32 and gradient clipping at 1. Comparison fitting uses permutation seed plus 10,000.

Select each model's first strictly best validation Spearman. Count epochs since the latest validation improvement by either model; stop at five or at the 48 epoch ceiling. D/E also allow the initial cosine solution. Selected epochs can differ. Both phases use validation. After all selections freeze, load test labels. The three seeds measure variation in training the new components with one fixed Qwen checkpoint.

The [configuration](../configs/csts-evidence-readout.json) fixes input and model hashes. Preserve token offsets, use inputs of at most 160 tokens, select positions belonging to the condition and sentence, and verify Qwen's parameter hashes before and after extraction. Store token vectors in bfloat16 and calculate heads in float32. The [implementation](../csts_pilot/evidence_readout.py) and [training stages](../csts_pilot/evidence_readout_stages.py) define the executable calculations.

## Diagnostics and interpretation

Report every model and seed, Spearman, MSE, selected epochs, prediction ranges and all five differences: C−B, D−B, E−C, E−D and (E−D)−(C−B). C−B is primary. For 95% intervals, make 2,000 paired bootstrap draws of the 1,222 test source groups, retaining related rows together and averaging seed differences within each draw. Secondary intervals are exploratory.

Check the following:

1. Compare writing before and after ratings using all 121 existing writing validation answers and 32 deterministic generations, capped at 64 tokens. Reference loss and exact agreement quantify retention of these writing targets.
2. Report quotation coverage, separate rating/evidence losses, training quotation agreement, gradient sizes and whether the two losses push shared parameters in similar directions.
3. Report condition results, including overlapping colour/appearance subsets, and score differences when the same sentence pair receives different conditions.
4. Run all six fixed [text edit cases](../configs/csts-readout-interventions.json). Predict smaller score changes after edits to other facts, sensitivity to edits of the condition's fact, greater weight on supporting words and increased unspecified property probability for sentences that leave the property unspecified. Recompute vectors for each edited sentence. Report every case, token weights, raw unspecified property probabilities and sentence lengths. Text edits test prediction sensitivity; quotation agreement measures alignment with teacher selected words.

A positive mean C−B Spearman difference, with its interval above zero and the predicted edit behavior, supports evidence supervision. D beating B or E beating C supports this comparison function. E beating D includes fitting new comparison weights. C beating A and matching B supports fitting the averaging procedure using ratings. Improved quotation agreement with stable similarity scores motivates further work on sentence comparison.

This benchmark has already informed project decisions. Plan replication using fresh material and independent backbone seeds. The [review](csts-evidence-readout-review.md) records completed code checks and execution details. CPU fixtures verify calculations and workflow execution. The controller waits for the shared A100 to become idle. Progress streams to native logs and `progress.md`; `summary.json` identifies final reports.
