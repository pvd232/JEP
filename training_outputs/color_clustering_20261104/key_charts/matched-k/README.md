# Qwen color structure at K = 12

![Off-the-shelf and fine-tuned Qwen with identical formatting](qwen-k12-pca-comparison.png)

Both panels use the same 65 single-color validation inputs, K = 12, target-color palette, dot sizes, axis limits and equal axis scaling. K = 12 was selected by the fine-tuned encoder's highest median silhouette over 20 starts.

**Gray lines show cluster membership.** Each line connects a sentence to the mean PCA position of its assigned cluster. Numbers identify clusters within each panel. Dot colors show the reference target colors.

Both encoders receive the original condition. The plots reuse the saved PC1/PC2 coordinates and K=12 assignments. Each panel follows the same selection rule: the highest-silhouette saved start at K=12. The off-the-shelf fit uses seed 18 (ARI 0.3478); the fine-tuned fit uses seed 2 (ARI 0.9486).

PCA is fitted separately for each encoder; positions show each encoder's own first two principal components. Clustering and ARI use the original normalized 4,096-dimensional vectors. Across all 20 starts at K=12, median ARI is 0.3475 off-the-shelf and 0.9375 fine-tuned. Reference labels are provisional; see the [measured report](../../report.md).

| Chart | PNG | SVG | Coordinates and groups | Fit metadata |
|---|---|---|---|---|
| Paired comparison | [PNG](qwen-k12-pca-comparison.png) | [SVG](qwen-k12-pca-comparison.svg) | See both encoders below | See both encoders below |
| Off-the-shelf Qwen | [PNG](off-the-shelf-qwen-k12-pca.png) | [SVG](off-the-shelf-qwen-k12-pca.svg) | [CSV](off-the-shelf-qwen-k12-points.csv) | [JSON](off-the-shelf-qwen-k12-metadata.json) |
| Fine-tuned Qwen | [PNG](fine-tuned-qwen-k12-pca.png) | [SVG](fine-tuned-qwen-k12-pca.svg) | [CSV](fine-tuned-qwen-k12-points.csv) | [JSON](fine-tuned-qwen-k12-metadata.json) |

Reproduce all three illustrations from the original native review archive:

```sh
python3 build_pretrained_pca.py /path/to/native-review.zip --out .
```

The generator requires Python, NumPy and Matplotlib. It checks matching point IDs and colors, 12 occupied clusters per encoder, normalized vectors, finite coordinates, saved cosine silhouettes and identical axis limits. Metadata records the archive SHA-256.
