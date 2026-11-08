# Full-data prompt experiment execution

The frozen protocol and selected checkpoint hashes own the scientific inputs.
`evaluate_selected.py` captures validation and test predictions through native
VIPER stages. It performs no fitting. The evaluator checks one saved validation
score per worker before opening test inference and uploads artifacts through
VIPER while the next checkpoint runs.

Start the CPU results reporter alongside inference, rather than after the last
worker finishes. Reuse the existing monitor checkout and branch:

```bash
cloud-job submit --cwd "$JEP_CHECKOUT" -- "$JEP_PYTHON" -u \
  scripts/full_data_prompt_20261107/publish_test_progress.py \
  --launch-dir "$JEP_LAUNCH_DIR" --monitor-checkout "$JEP_MONITOR_CHECKOUT"
```

Set these paths to the owning project checkout, pinned Python environment,
launch directory and existing `monitor/full-data-prompt-20261107` checkout.
The launch directory contains the pinned source, matrix, ordered test bytes,
allocation manifests and each worker's latest observation. It must also receive
the collector's `results-evalN.json` and `cleanup-evalN.json` receipts.

The durable reporter checks every 30 seconds. For each new sealed prediction it
checks SHA-256, frozen model/test hashes, every row identity and label, then
computes Spearman and normalized MSE on the CPU. It pushes the existing GitHub
tracker, CSV and structured status when scores or execution state change.
It preserves missing observations as errors and never replaces a measured
score with a failure placeholder. Only the verified collector receipt promotes
a score from sealed to cloud verified. Failed GitHub publication retains the
local files and retries; it does not block inference or artifact export.

Run `analyze_test.py` after the complete collector receipt is available. It
independently recomputes all 15 scores and runs the predeclared 10,000 shared
source-group bootstrap draws. Publish its CSV, JSON and report to the experiment
branch. Preserve the original validation selection matrix. Delete owned GPUs,
disks and temporary snapshots only after verified export; the analysis uses CPU.

Live tracker: https://github.com/pvd232/JEP/blob/monitor/full-data-prompt-20261107/plans/full_data_prompt_20261107/live-status.md

The current evaluator reloads the backbone and prepares a native run for every
checkpoint. One observed test capture took 153.99 seconds for scoring including
model loading, and 217.41 seconds end to end. A future evaluator may amortize
loading and stage startup, after an equivalence check. Keep the current frozen
execution unchanged while it finishes.
