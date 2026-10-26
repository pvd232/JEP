# Full-dimensional residual codebook results

Completed native TRAIN and independent development EVAL from source
`4a611560fe7992145798b09dcbcf15bf426c80f8`. TRAIN took 270.00 seconds;
EVAL took 59.88 seconds. All six fits completed five epochs through shared
patience and selected epoch zero. Mean paired selected Spearman gain: **0**.
All selected scores reproduce unchanged Qwen: **0.7825753746534037**. The
predeclared eligibility gate failed. Publication is queued separately; cloud
completion is unverified.

## Completed fitting

| Seed | Selected epoch, control / groups | Terminal control Spearman | Terminal group Spearman |
| --- | --- | ---: | ---: |
| 7 | 0 / 0 | 0.758106 | 0.755677 |
| 8 | 0 / 0 | 0.764843 | 0.759825 |
| 9 | 0 / 0 | 0.766326 | 0.767140 |

## Cluster statistics

Descriptive means over seeds 7/8/9, each on 3,591 distinct development
caption-condition inputs. Starting groups are TRAIN-only k-means on original
Qwen; terminal groups belong to the unselected epoch-five prototype models.

| Measurement | Starting | Terminal group training |
| --- | ---: | ---: |
| Occupied groups, maximum 128 | 125.33 | 123.33 |
| Effective groups, exp(entropy) | 89.13 | 88.21 |
| Largest group share | 5.96% | 6.34% |
| Rating-1/2 pairs sharing a group | 19.24% | 11.68% |
| Rating-4/5 pairs sharing a group | 84.91% | 77.48% |
| Group-score FPR at exact 90% positive coverage | 30.19% | 38.63% |

Boundary ties receive fractional acceptance. This is an expected pairwise rate
using centre similarities; numerical groups have no adjudicated legal meanings.
Fewer same-group negative pairs accompany lower positive coassignment and worse
FPR at fixed coverage. The continuous terminal group-model Spearman is 0.760881.

## Questions with high reference disagreement

Rank exact condition strings by unchanged Qwen development MSE among the 31
conditions with at least eight pairs. The full cohort contains 917 conditions;
730 have one pair. These are exploratory rankings on a development cohort.

| Condition | Pairs | Source groups | MSE, 0–1 target scale |
| --- | ---: | ---: | ---: |
| number of objects | 12 | 12 | 0.078645 |
| name of place | 10 | 10 | 0.073568 |
| number of players | 10 | 10 | 0.068067 |
| number of animals | 32 | 31 | 0.066812 |
| activity of people | 10 | 9 | 0.064395 |
| number of dogs | 15 | 14 | 0.061533 |

The seed-seven `number of dogs` view contains 29 distinct captions. The original
groups separate seven one-dog captions, seventeen two-dog captions, and five
three-dog captions split into groups of four and one. These descriptions apply
to the displayed captions. Their grouping survives training, with the two
three-dog subgroup IDs exchanging.

Two large reference disagreements merit source/annotation review: one cow
compared with one dog under `number of animals` has supplied rating 1 and Qwen
score 4.455; a clear two-dogs versus two-dogs pair under `number of dogs` has
supplied rating 1 and Qwen score 3.918. Ratings remain unchanged in this analysis.

## Visualization and provenance

Assignments and statistics use all 4,096 coordinates. Each question has one
shared two-dimensional PCA basis fitted for display to both states' caption
vectors. The two axes capture 23–71% of combined variance across the six views.
Global group centres are projected onto those same axes. Projected proximity
is a display quantity; assignments use the full-dimensional cosine.

The accompanying JSON retains native producer references, original/model cache
hashes, resume/trace/summary hashes, every per-seed statistic, all supported
question rankings, plotted coordinates and source captions/pair ratings.

The method is pairwise-supervised representation learning with unsupervised
vector-quantization assignments. Conceptual antecedents are Xing et al. (2002),
[clustering with side information](https://papers.nips.cc/paper_files/paper/2002/hash/c3e4035af2a1cde9f21e1ae1951ac80b-Abstract.html),
and van den Oord et al. (2017),
[learned vector quantization](https://arxiv.org/html/1711.00937v2).
The specific residual/cosine-MSE combination is this experiment's adaptation.
