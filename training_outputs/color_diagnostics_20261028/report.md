# Color diagnostic results

The diagnostic is complete. The proposition arm had a lower implied-color embedding margin in all three seeds (mean difference -0.0420; corrected interval [-0.0835, -0.0038]). Explicitly naming the color increased its relative margin by +0.0730. These findings support weaker use of implied colors as a candidate explanation for the original C-STS color regression.

Exact color readout improved by 20 percentage points, and wrong-object answers fell by 3.89 percentage points. Readout scores depend on the frozen vocabulary head and English parser. Some control answers repeated text or used non-English color words, which can affect those scores.

One model authored the probe and expected color labels. The run omitted the two-person label check specified in the plan. This is a completed exploratory result; the unvalidated labels limit interpretation, especially for implied colors.

All 13 model states were evaluated on the same 100 families. Each family contains four caption variants.
The 520 caption-condition inputs are reused across states.

Each contrast is the proposition arm minus the ratings control, averaged over seeds 7, 8 and 9.
Paired intervals resample whole families within strata. Their 99.1667% level corrects six contrasts by Bonferroni.
Intervals describe fresh-family variation conditional on these three trained seeds.

| Contrast | Mean difference | 99.1667% interval | Seed 7 | Seed 8 | Seed 9 |
|---|---:|---|---:|---:|---:|
| Exact color readout E | +0.2000 | [+0.1132, +0.2833] | +0.1500 | +0.3042 | +0.1458 |
| Margin among correct readouts M_G | +0.0874 | [-0.0181, +0.1959] | +0.0643 | +0.0990 | +0.0988 |
| Wrong-object answer rate F | -0.0389 | [-0.0819, -0.0056] | -0.0375 | -0.0208 | -0.0583 |
| Condition-switch margin C | +0.2495 | [+0.1733, +0.3299] | +0.2680 | +0.1556 | +0.3249 |
| Explicit-cue benefit Q | +0.0730 | [+0.0284, +0.1185] | +0.0706 | +0.0642 | +0.0842 |
| Implicit color margin | -0.0420 | [-0.0835, -0.0038] | -0.0233 | -0.0774 | -0.0253 |

The descriptive all-family margin difference is +0.0743; seed 7: +0.1028, seed 8: -0.0009, seed 9: +0.1209.

The following decisions apply the predeclared interval signs to the proposed labels:

| Pattern | Interval signs |
|---|---|
| Readout loss | Unresolved |
| Distance loss among correct readouts | Unresolved |
| Confusion between objects | Unresolved |
| Loss on implied colors | Required signs met |

Geometry requires at least 20 represented families in each seed's shared correct-readout set.

| Seed | Eligible triplets | Represented families | Threshold |
|---|---:|---:|---|
| 7 | 56 | 17 | Unresolved |
| 8 | 26 | 11 | Unresolved |
| 9 | 46 | 16 | Unresolved |

Stage accounting describes the saved training trajectories:

| Seed | First phase D_A | Ratings phase D_B | Final gap |
|---|---:|---:|---:|
| 7 | -0.6684 | +0.7712 | +0.1028 |
| 8 | -0.6829 | +0.6820 | -0.0009 |
| 9 | -0.6690 | +0.7900 | +0.1209 |

The primary readout score weights each explicit and multiple-object family equally.
M_G weights eligible triplets within each seed, then weights the three seed ratios equally.
The margin identity is m = s(anchor, matching) − s(anchor, mismatching) = (d_mismatch² − d_match²)/2.
C averages the target-condition and distractor-condition margins; condition-independent scores give C = 0.
Q = m_explicit − m_implicit. Stage contrasts satisfy final gap = D_A + D_B.
The JSON files retain per-state readouts, implied-label scores, control color-invention rates, family margins and source hashes.
The shared-correct geometry comparison remains unresolved: each seed fell below the required 20 represented families. A confirmatory study would require independently reviewed labels fixed before model evaluation.
