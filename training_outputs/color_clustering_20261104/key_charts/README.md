# Fine-tuned Qwen: key charts

[View the 7-page PDF](csts-color-key-charts.pdf) · [Download charts and tables](csts-color-key-charts.zip)

Winning encoder: **fine-tuned Qwen3-Embedding-8B with the original color condition included**. Each point is one sentence plus its condition. Existing vectors and cluster assignments are reused.

| Input group | Inputs | Known color labels | Chosen clusters | Median silhouette |
|---|---:|---:|---:|---:|
| Validation, one clear target color | 65 | 13 | 12 | 0.8012 |
| Test, one clear target color | 119 | 11 | 11 | 0.8561 |
| All splits, one clear target color | 497 | 17 | 12 | 0.8156 |
| All splits, all selected inputs | 1,017 | 17 among clearly labeled inputs | 20 | 0.5675 |

The chosen cluster count has the highest median silhouette across 20 random starts. Higher scores mean inputs are closer to their own group than to the nearest other group. The PDF and [winner table](k-winners.csv) also show the highest individual run across all counts and starts. Cluster plots use the highest-scoring start at the chosen count.

## Cluster-count comparison

![Cluster counts and separation scores](figures/01-cluster-count-winners.png)

## Validation: 12 groups

![Validation winner](figures/02-validation-single-12-clusters.png)

## Test: 11 groups

![Test winner](figures/03-test-single-11-clusters.png)

## All single-color inputs: 12 groups

![All single-color inputs](figures/04-pooled-single-12-clusters.png)

## All selected inputs: 20 groups

![All selected inputs](figures/05-pooled-all-20-clusters.png)

## Off-the-shelf Qwen at the same K

**K = 12** matches the fine-tuned validation plot above: it maximizes that encoder's median silhouette over 20 starts. Both plots use the same 65 single-color validation inputs and target-color palette. The ARI bar comparison below uses K = 13, the number of reference colors.

![Off-the-shelf Qwen at K=12 on PC1 and PC2](matched-k/off-the-shelf-qwen-k12-pca.png)

Dots show reference target colors. Gray spokes connect members of each of the 12 fitted groups to their mean PCA position; numbers identify groups. The off-the-shelf encoder receives the original condition. The figure reuses its saved PC1/PC2 coordinates and the highest-silhouette saved start at K=12 (seed 18), following the fine-tuned chart's plotting policy. PCA is fitted separately for each encoder; clustering uses the original normalized 4,096-dimensional vectors.

Across all 20 starts at K=12, median ARI is **0.3475 off-the-shelf** and **0.9375 fine-tuned**. The illustrated off-the-shelf fit has ARI **0.3478**. Reference labels retain the provisional status described below.

[SVG](matched-k/off-the-shelf-qwen-k12-pca.svg) · [Point coordinates and groups](matched-k/off-the-shelf-qwen-k12-points.csv) · [Fit metadata](matched-k/off-the-shelf-qwen-k12-metadata.json) · [Reproduction script](matched-k/build_pretrained_pca.py)

## Comparison with the controls

![Fine-tuned encoder and controls](figures/06-winning-encoder-controls.png)

The three panels use different metrics:

- **Left: adjusted Rand index (ARI).** Cluster assignments versus the reference color labels for 65 single-color validation inputs, using K=13 for all three encoders. Bars show medians over 20 starts.
- **Middle: Spearman correlation.** Raw embedding cosine similarity versus audited ratings for 74 validation pairs.
- **Right: condition-switch probe counts.** Of 50 source-derived probes, 47 have enough reference examples to score. A probe passes when both condition-specific vectors prefer their intended color reference. References exclude the probe's caption family. These exploratory probes draw from multiple dataset splits.


## Files and interpretation

- [Cluster-count winners](k-winners.csv): both selection policies for every cohort.
- [Silhouette scores by cluster count](silhouette-by-k.csv): medians, quartiles and best scores.
- [Plotted fits](selected-runs.csv): cluster count, initialization seed and scores.
- [Plotted inputs](selected-point-data.csv): sentence, condition, reference color, group, silhouette and PCA coordinates.
- [Encoder configuration](winning-model.json): checkpoint identity and archived settings.
- [PNG and SVG figures](figures/).

All-inputs results include multiple-color, unspecified and unresolved cases. Single-color results require one clearly resolved relevant color. Reference labels are provisional and were frozen before inference. Group numbers in this pack start at 1.

The two-dimensional positions reuse the original PCA coordinates. Clustering and numerical scores use the original normalized 4,096-dimensional vectors. Per-point silhouettes were recomputed from those vectors and checked against each saved fit score within 1e-5. No encoder training, encoding or k-means fitting is repeated for this pack.

[Full measured report](../report.md) · [All 86 diagnostic pages](../csts-color-clustering-diagnostics.pdf)
