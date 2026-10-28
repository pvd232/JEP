# Testing evidence selection and sentence comparison in JEP

Status: implemented for review. The scientific experiment has not run.

## Question and hypothesis

The [previous experiment](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md) improved test Spearman from 0.855375 to 0.863398 after training Qwen to write propositions before learning similarity ratings. The uncertainty interval for that difference includes zero. The models used one backbone seed and different numbers of rating updates. This motivates another experiment without establishing why the improvement occurred.

**Hypothesis:** proposition training encodes facts relevant to the condition, but the existing cosine score uses them imperfectly. Evidence quotations could improve which sentence information contributes to the score. A learned comparison function could improve how that information is scored. We test these separately.

All five models use the same final proposition checkpoint: Qwen3 Embedding 8B with its existing LoRA weights. Qwen stays frozen. Its vectors retain all 4,096 coordinates. The new components described below produce scores without generating answers.

## A: the existing similarity score

For each sentence, Qwen reads the condition, then the sentence, then an end of document token. Let $e_1,e_2\in\mathbb{R}^{4096}$ be its final layer vectors at that last token for the two sentences. Divide each vector by its length, then take their dot product:

```math
\widehat y_A
=\frac{e_1^\top e_2}{\|e_1\|_2\|e_2\|_2}.
```

This is cosine similarity. A has no new training. It asks whether the existing scorer already does better than the proposed replacements.

## B: learn which sentence tokens to average, using ratings

Qwen produces a vector at every input token. Let $r_j\in\mathbb{R}^{4096}$ describe condition token $j$, for $j=1,\ldots,n$. Let $h_t\in\mathbb{R}^{4096}$ describe sentence token $t$, for $t=1,\ldots,T$. Each vector includes information from preceding input tokens. The condition comes first, so its vectors cannot read the sentence.

Average the condition vectors to obtain $u$. Two learned matrices $W_q,W_k\in\mathbb{R}^{128\times4096}$ turn it into a vector $q$ containing 128 numbers and each sentence token into a vector $k_t$ containing 128 numbers. Their dot product gives token score $\ell_t$:

```math
\begin{aligned}
u&=\frac1n\sum_{j=1}^{n}r_j,\\
q&=W_q\mathrm{LN}(u),\qquad k_t=W_k\mathrm{LN}(h_t),\\
\ell_t&=\frac{q^\top k_t}{\sqrt{128}}.
\end{aligned}
```

Here LN subtracts each vector's coordinate mean, then divides by the square root of (coordinate variance plus $10^{-5}$) for stability. The 128 coordinates and square root scaling apply only to token scoring. Averaging the condition vectors and choosing 128 are design choices to test.

Convert the token scores into positive weights summing to one. Average the original sentence vectors using those weights, then divide by the result's length:

```math
\alpha_t=\frac{\exp(\ell_t)}{\sum_{a=1}^{T}\exp(\ell_a)},
\qquad v=\sum_{t=1}^{T}\alpha_t h_t,
\qquad z=\frac{v}{\|v\|_2}.
```

The index $a$ runs over sentence tokens. Compute $z$ separately for each sentence. B predicts $\widehat y_B=z_1^\top z_2$. Its sentence vectors still have 4,096 coordinates.

For comparison $i$, convert the human rating to $y_i=(\mathrm{rating}_i-1)/4$. For a batch of $m$ comparisons, minimize mean squared error:

```math
L_r=\frac1m\sum_{i=1}^{m}(\widehat y_i-y_i)^2,
\qquad L_B=L_r.
```

Ratings therefore teach B which token weights make its cosine scores more accurate. B receives no evidence labels. B and C each add 1,048,705 parameters.

## C: the same calculation, also trained on evidence quotations

C has exactly B's architecture. Its additional training labels are existing teacher quotations copied from the input sentence. These identify token positions to emphasize; they are distinct from Qwen's internal vectors.

Both models also contain a learned vector $k_0\in\mathbb{R}^{128}$ and scalar $b_0$ for a “no supporting text” option. Include this option when calculating evidence probabilities:

```math
\begin{aligned}
\ell_0&=\frac{q^\top k_0}{\sqrt{128}}+b_0,\\
Z&=\exp(\ell_0)+\sum_{a=1}^{T}\exp(\ell_a),\\
p_t&=\frac{\exp(\ell_t)}{Z},\qquad t=0,\ldots,T.
\end{aligned}
```

For labeled sentence occurrence $s$, $p_{st}$ and $g_{st}$ are predicted and target probabilities. Valid quotations divide probability equally across the union of their overlapping tokens. An explicit `not_specified` record assigns all probability to option zero. Ambiguous, missing or unsuccessfully aligned quotations contribute no evidence loss. Every comparison still contributes rating loss.

Since target probabilities sum to one, substituting the expression for $p$ gives the evidence loss below. Average it over $S$ labeled occurrences, then add it to rating loss:

```math
\begin{aligned}
E_s&=-\sum_{t=0}^{T_s}g_{st}\log p_{st}
=\log Z_s-\sum_{t=0}^{T_s}g_{st}\ell_{st},\\
\frac{\partial E_s}{\partial\ell_{st}}&=p_{st}-g_{st},\\
L_e&=\frac1S\sum_{s=1}^{S}E_s,\qquad L_C=L_r+0.1L_e.
\end{aligned}
```

$T_s$ is its sentence token count and $Z_s$ its probability denominator. The derivative explains the supervision: less probability than the target favors increasing that token's score; too much favors decreasing it. Without labeled occurrences, evidence loss is zero.

C's prediction is also $\widehat y_C=z_1^\top z_2$, using its own learned token weights.

**The “no supporting text” probability does not adjust similarity.** Both models construct $z$ using weights over sentence tokens alone. For example, joint probabilities 0.90 for no support and 0.06/0.04 for two tokens produce sentence weights 0.60/0.40. No support is reported separately. Computing token weights separately remains stable even when almost all joint probability goes to no support. C tests evidence selection; directly weighting similarity by addressability remains another experiment. B's ratings cannot train parameters used only by option zero.

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

Here $j$ indexes coordinates, $\odot$ multiplies matching coordinates, $w_d,w_p\in\mathbb{R}^{4096}$ are learned weights, and $b$ is a scalar. Swapping the sentences leaves every term unchanged. Starting all 8,193 new parameters at zero reproduces cosine exactly.

**D** applies this function to B's selected, frozen vectors. **E** applies it to C's selected, frozen vectors. Writing $f_D,f_E$ for the separately fitted functions and superscripts B/C for the vectors they receive:

```math
\begin{aligned}
\widehat y_D&=f_D(z_1^B,z_2^B),\\
\widehat y_E&=f_E(z_1^C,z_2^C),\qquad L_D=L_E=L_r.
\end{aligned}
```

Fit both functions using rating MSE. Neither fit changes token selection. These functions cannot compare arbitrary combinations of coordinates, so failure would not rule out richer comparison methods. Predictions remain unclipped.

## Data and fitting

Use 6,051 training, 1,576 validation and 2,431 test comparisons from `jep-csts-v1.1`. Recompute A and the previous ratings control on these rows because the historical test had 2,430. Existing teacher data contains 11,909 inputs: 11,079 answered, 802 not specified and 28 ambiguous. Literal quotation matching requires a unique occurrence and does not verify semantic correctness.

For seeds 7, 8 and 9, train B/C together from identical initial weights and identical batches. Then select their weights, freeze them and fit D/E. Each phase uses AdamW, learning rate 0.001, weight decay 0.01, batch size 32 and gradient clipping at 1. Comparison fitting uses permutation seed plus 10,000.

Select each model's first strictly best validation Spearman. Stop a phase after five epochs improve neither model, or after 48 epochs. D/E also allow the initial cosine solution. Selected epochs can differ. Validation is reused across phases; test labels become available only after all selections freeze. Three head seeds do not replicate backbone training.

The [configuration](../configs/csts-evidence-readout.json) fixes input and model hashes. Preserve token offsets, reject inputs exceeding 160 tokens, exclude padding and verify unchanged Qwen weights. Store token vectors in bfloat16 and calculate heads in float32. The [implementation](../csts_pilot/evidence_readout.py) and [training stages](../csts_pilot/evidence_readout_stages.py) define the executable calculations.

## Diagnostics and interpretation

Report every model and seed, Spearman, MSE, selected epochs, prediction ranges and all five differences: C−B, D−B, E−C, E−D and (E−D)−(C−B). C−B is primary. For 95% intervals, make 2,000 paired bootstrap draws of the 1,222 test source groups, retaining related rows together and averaging seed differences within each draw. Secondary intervals are exploratory.

Check the following:

1. Compare writing before and after ratings using all 121 existing writing validation answers and 32 deterministic generations, capped at 64 tokens. Reference loss and exact agreement measure retained writing behavior, not factual accuracy.
2. Report quotation coverage, separate rating/evidence losses, training quotation agreement, gradient sizes and whether the two losses push shared parameters in similar directions.
3. Report condition results, including overlapping colour/appearance subsets, and score differences when the same sentence pair receives different conditions.
4. Run all six fixed [text edit cases](../configs/csts-readout-interventions.json). Predict smaller changes after irrelevant edits, sensitivity to relevant edits, greater weight on supporting words and increased no support probability when a property disappears. Recompute vectors for each edited sentence. Report every case, token weights and no support probabilities. These probabilities are uncalibrated and affected by sentence length; quotation agreement alone cannot establish which information caused a prediction.

A positive mean C−B Spearman difference, with its interval above zero and the predicted edit behavior, supports evidence supervision. D beating B or E beating C supports this comparison function. E beating D includes fitting new comparison weights. C beating A while matching B supports the new averaging procedure without demonstrating an evidence benefit. Better selection with unchanged similarity leaves the scoring problem unresolved.

This benchmark has already informed project decisions. Results require replication with fresh material and independent backbone seeds. The [review](csts-evidence-readout-review.md) records completed code checks, execution details and their limits; CPU fixtures establish implementation behavior, not scientific success. The controller waits for the shared L4 without preempting work. Progress streams to native logs, and `summary.json` identifies final reports. This PR has not launched the study.
