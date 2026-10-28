# How the learned comparison uses saved sentence vectors

This analysis studies the information in the saved embeddings and the contribution of the learned comparison. It replays the color probe, reviews individual sentence pairs and fits one small comparison to the existing ratings control.

## Saved models and inputs

The existing encoder received proposition generation and similarity training. Its checkpoint has SHA256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`. The ratings control has SHA256 `667c124a49be72a6fd8e9fa3df6974830e4ab6a46a10243c360dd46bcc75b534`. These are the seed 7 pair in the [original comparison protocol](https://github.com/pvd232/JEP/blob/8bff661ecc58e8df8ede124808c53a3588e26ca4/training_outputs/proposition_full_20261026/replication_protocol.json).

The [color probe](https://github.com/pvd232/JEP/blob/fc00f4f5c2e100ff8d2ecd2d7309673976b6c6f4/training_outputs/color_diagnostics_20261028/protocol_plan.md) retained 520 vectors for each saved model. Replay uses the vectors from the exact existing encoder on which the three original comparisons were fitted. It checks their saved hash, dimensions, unit lengths and input identities. The cosine replay reproduces the published margins.

The rating inputs retain the [committed split identities](../configs/csts-native-comparison.json): 6,051 training, 1,576 validation and 2,431 test comparisons. One inference pass through the frozen ratings control captures the required vectors. The inference process records zero encoder updates. Each completed cache publishes through the existing VIPER Cloud file API while subsequent encoding continues.

## What the comparison changes

Let $a,b\in\mathbb R^{4096}$ be unit sentence vectors produced under the same condition. The saved comparison has weights $w_d,w_p\in\mathbb R^{4096}$ and bias $\beta\in\mathbb R$. The [implemented score](../csts_pilot/evidence_readout.py) is

```math
f_\phi(a,b)=a^\top b+w_d^\top|a-b|+w_p^\top(a\odot b)+\beta.
```

Here absolute value and $\odot$ act coordinate by coordinate. The learned terms change how the fixed vectors contribute to the rating. The color replay reports score margins and ordering of the expected matching and mismatching colors.

For each implied family, it compares the caption with its matching and mismatching anchors. It repeats the comparison after explicitly naming the expected color. For families with two colored objects, it switches the condition between the two objects and uses the original four anchor orientations. The three reported margin contrasts are the implied margin, the additional benefit of explicitly stating the color, and the condition switch margin.

Paired intervals resample whole families 10,000 times. The three saved comparisons remain together in each draw. Each interval has confidence $1-0.05/3$, approximately 98.33 percent. These intervals describe probe family variation for this one saved encoder and its three comparison fits. The implied labels retain the original pending human review. Ordering counts distinguish a stronger margin from a changed preference.

## Review of individual errors

The [analysis script](../scripts/analyze_csts_comparison.py) joins all predictions in the frozen test order and preserves every human rating. It selects five examples per requested group by the largest squared error difference, keeping one example per source group. Groups cover counting, object types, spatial relations, color, comparison improvements, comparison regressions and improvements from fresh training. The review shows both sentences, the condition, the human rating, cosine, the learned score and the learned correction.

Let $y_i\in[0,1]$ be the normalized rating for example $i$, $e_i=y_i-a_i^\top b_i$, and $\delta_i=f_\phi(a_i,b_i)-a_i^\top b_i$. The exact reduction in squared error is

```math
e_i^2-(e_i-\delta_i)^2=2e_i\delta_i-\delta_i^2.
```

This identity attributes the change to the saved comparison for each fixed sentence pair. The report also gives Spearman, which measures the ordering of ratings.

## One missing comparison

The ratings control receives one new comparison with 8,193 trainable parameters on CPU, using seed 7. Its settings match the original seed 7 comparison: zero initialization, rating MSE, AdamW with learning rate 0.001 and weight decay 0.01, batches of 32, gradient clipping at 1 and permutation seed 10007. Its fixed budget is 21 comparison epochs, matching the original seed 7 fitting budget. Select the first strictly best validation Spearman across initialization and these epochs. Test inference follows selection. The [capture script](../scripts/capture_csts_control_vectors.py) keeps Qwen fixed throughout.

Let $\rho_{P,L}$ and $\rho_{P,C}$ be test Spearman for the existing encoder with learned comparison and cosine. Define $\rho_{R,L}$ and $\rho_{R,C}$ similarly for the ratings control. The interaction is

```math
I=(\rho_{P,L}-\rho_{P,C})-(\rho_{R,L}-\rho_{R,C}).
```

A positive value means a larger comparison gain on the existing encoder. A negative value means a larger comparison gain on the ratings control. The analysis computes all four values on identical test rows and uses 2,000 paired source group bootstrap draws for a 95 percent interval.

This is an exploratory analysis after earlier test reporting. The interaction concerns one saved encoder pair and one comparison fitting seed. The existing three comparison fits also provide the color replay. Models, optimizer state, vector caches, predictions, code and reports receive VIPER Cloud publication receipts before runtime shutdown.
