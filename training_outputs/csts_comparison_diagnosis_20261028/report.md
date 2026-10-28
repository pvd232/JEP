# What the learned comparison adds

The analysis reuses the saved existing encoder and its three comparisons, reviews individual rating errors, and fits one comparison to the frozen ratings control. The interaction uses comparison seed 7 for the original saved encoder pair.

## Color replay

| Measurement | Cosine | Learned mean | Change |
| --- | --- | --- | --- |
| Implied color margin | 0.610405 | 0.656670 | +0.046265 |
| Additional benefit from explicitly naming the color | 0.268565 | 0.292573 | +0.024008 |
| Condition switch margin | 0.783123 | 0.848034 | +0.064911 |
| Fraction of implied families with the proposed matching color ranked first | 1.000000 | 1.000000 | +0.000000 |

| Contrast | Change | 98.33 percent family interval |
| --- | --- | --- |
| implicit_margin | +0.046265 | [+0.036059, +0.055462] |
| Q | +0.024008 | [+0.017356, +0.031365] |
| C | +0.064911 | [+0.057077, +0.072708] |

The cosine replay ranks the proposed matching color first in 30 of 30 implied families. The three learned comparisons average 30 of 30. Margins measure preference strength; the ordering column records changes in preference. The labels retain their original pending human review.

## The missing comparison

All four cells use the same 2,431 frozen test examples. The new comparison trains 8,193 parameters on CPU and selects its first best validation epoch within the original seed 7 comparison's 21 epoch budget.

| Encoder and score | Spearman | Normalized MSE |
| --- | --- | --- |
| Existing encoder, cosine | 0.863397667 | 0.035635971 |
| Existing encoder, learned comparison | 0.864671663 | 0.034939583 |
| Ratings control, cosine | 0.855516672 | 0.038370129 |
| Ratings control, learned comparison | 0.856070210 | 0.038449038 |

The interaction in Spearman is **+0.000720**, with a 95 percent paired source group interval **[+0.000122, +0.001281]**. Positive values indicate a larger comparison gain on the existing encoder. Negative values indicate a larger gain on the ratings control.

The new control comparison selects epoch **1**. Its encoder receives zero parameter updates.

## Individual examples

The [sentence pair review](cases.md) shows the original human ratings and the scores for counting, object type, spatial relations, color and the largest changes produced by each scoring choice. The [row errors](row-errors.json) preserve the full 2,431 example analysis.

## Methods and scope

Exploratory analysis after prior test reporting. The interaction uses the original seed 7 encoder pair and comparison fitting seed 7. The new comparison uses the original seed 7 comparison's 21 epoch budget and first best validation selection. Encoder parameters remain fixed.

[Methods](../../plans/csts-comparison-diagnostics-methods.md) · [Numeric results](analysis.json) · [Color details](color-comparison.json) · [Cloud receipts](cloud-receipts.json)

## Matched color replay

This descriptive table applies each encoder's own comparison, using comparison seed 7 in both arms.

| Encoder and score | Implied margin | Explicit cue benefit | Condition switch margin |
| --- | --- | --- | --- |
| A_cosine | 0.610405 | 0.268565 | 0.783123 |
| A_learned_seed7 | 0.643620 | 0.285401 | 0.828691 |
| R_cosine | 0.633666 | 0.198004 | 0.515159 |
| R_learned_seed7 | 0.646117 | 0.205673 | 0.524788 |

[Matched probe values](color-control-replay.json) · [Interpretation of selected examples](case-notes.md) · [Implied label review](implied-label-review.md)

The original ratings reference covers 2,430 rows. This study replays the unchanged control checkpoint on all 2,431 current rows. Its common row replay differs from the original predictions by mean absolute score 0.002789. [Replay check](control-replay-parity.json).

## Score scaling and ordering

An affine approximation summarizes the learned score as a scale and offset of cosine. It is fitted to the saved score outputs for inspection.

| Encoder | Scale | Offset | Score variance explained | Approximation RMSE |
| --- | --- | --- | --- | --- |
| A | 1.046829 | -0.004998 | 99.9368% | 0.009205 |
| R | 1.006686 | 0.038919 | 99.9282% | 0.009473 |

Positive scaling preserves ordering while increasing margins. Small departures from the affine approximation contribute the observed Spearman changes. The color ordering counts therefore accompany its raw margin changes. [Score approximation](affine-score-check.json).
