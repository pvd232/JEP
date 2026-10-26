# Full-dimensional codebook test

Authorized 26 October 2026. Reuse the sealed 6,980 training / 1,830 development
pairs and Qwen features from the original codebook screen. Keep all 4,096 output
coordinates. Learn a rank-32 additive correction, with its output weights zero
at initialization, so epoch zero reproduces the existing 0.782575 Spearman
baseline within 0.000001. The original feature vector has an identity path.

Compare rating-only training with the original joint prototype objective,
unchanged: rating MSE + 0.1 * (quantized rating MSE + dictionary regression +
0.25 * commitment). Both arms share residual capacity, initial weights, training
examples, ordering, optimizer settings and updates. The group centres begin at
training-only spherical k-means centres. For the rating-only control, fit centres
to its selected training representations after selection, as in the original
screen. The prototype arm retains its selected learned dictionary.

Use seeds 7/8/9, AdamW rate 0.001, weight decay 0.01 on correction weights,
batch 32, 128 centres, ten k-means iterations, a 12-epoch ceiling and 1,200
seconds per pair. Shared patience five ends both arms together; improvement in
either arm resets patience. Epoch zero remains eligible and all epochs are
reported. Preserve selected and terminal weights and optimizer/RNG states.

On each epoch's first training batch, record the rating and weighted auxiliary
gradient norms on the shared correction weights and their cosine. Record zero
norms explicitly. These measurements do not change the optimizer or loss weight.

Independent native development EVAL replays selected checkpoints and exports
all continuous and code-centre prediction arrays. Its metric worker recomputes
per-seed candidate-minus-control Spearman and the mean. It also recomputes
candidate-minus-unchanged-Qwen gains and code-centre false-positive rates at
exact 90% positive coverage. Boundary ties receive fractional acceptance,
reported explicitly. Ratings 4/5 are positive; 1/2 negative; rating 3 remains
in ranking/regression. This is a pairwise group-score diagnostic.

Proceed only if mean Spearman gains over both the unchanged parent and trained
control are at least 0.005, and mean group-score FPR is lower than the control.
This remains development-selected evidence. The benchmark test stays unopened.

Reuse the existing controller, native TRAIN/EVAL, source guards, cache identities
and asynchronous publication. No generated text, backbone inference or Qwen
weight updates are required. No existing experiment state is changed.

Run `python -m csts_pilot.iterative_codebook_run --residual --prepared-summary
/path/to/csts_codebook_execution.json --name unique-name`; add `--preflight`
for a read-only input check.
