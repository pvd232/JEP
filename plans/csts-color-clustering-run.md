# C-STS COLOR Clustering Execution

Use the accepted contract in `contracts/csts-color-clustering.md` and the frozen settings in `experiments/color-clustering.toml`.

The analysis uses the exact `proposition_final.pt` checkpoint with SHA-256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`. This is the single encoder whose vectors supplied the archived A comparison result. The approximately 0.865230 figure averages three learned-comparator fits; raw cosine on those vectors scored 0.863398 on the recorded test set.

Native VIPER stages:

1. `scripts.run_color_clustering.embed` builds the three arm caches from frozen point, label, checkpoint and configuration inputs.
2. `scripts.run_color_clustering.cluster` consumes those managed artifacts, retains every K/seed fit and computes the fixed diagnostic comparisons.
3. `scripts.run_color_clustering.report` consumes the managed embeddings and clustering artifacts and produces the full visual and example review pack.

Run from the verified GPU project environment:

```bash
python -m scripts.run_color_clustering --root /home/machina/jep-color-clustering-20261104/repo
```

The driver verifies each successful VIPER run and retains its exact reference. A restart reuses verified completed stages with identical input and implementation identities. Intermediate work is retained under an input-and-code-specific directory. Checkpoints and source text stay in the task's private input/artifact store.

The review pack includes every cohort's K curves, seed IQR, convergence iterations, representative silhouette distributions, cluster sizes, color/cluster contingency heatmaps, centroid distances, PCA views with explained variance, seed-stability matrices, original-pair cosine plots, condition-switch diagnostics and paired comparison intervals. Tables retain all run metrics and assignments, source labels, central/peripheral exemplars and cross-family nearest neighbors. PDF, PNG and SVG views share one visualization index.

Validation is bounded to the sixteen success/rejection fixtures named by the accepted contract, source-format/documentation checks and native VIPER run verification. The new analysis has no retained CodeQL impact selection; this limitation remains explicit rather than widening the repository test suite.

Local VIPER persistence is the completion path. A separate durable background uploader exports the terminal run into a local outbox, then publishes that immutable bundle to the configured VIPER cloud repository. Queue state, failures and cloud references are retained independently; cloud transfer never gates scientific completion or review delivery.
