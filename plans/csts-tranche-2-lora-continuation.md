# Tranche 2: LoRA continuation

Resume the completed one-epoch LoRA parent at `baseline_results/lora/initial/summary.json` after the user requested five-epoch validation patience and an updated learning rate. The initial test score was 0.7021695526490561; this continuation is exploratory on an already examined benchmark.

Use `configs/csts-tranche-2-lora-continuation.json`. Restore terminal adapter weights, AdamW moments, random state and the training permutation generator. Retain the parent's validation-selected incumbent. Start at completed epoch 1 and optimizer update 219. Use a constant learning rate of 2e-5 with zero new warmup; the parent stopped during warmup at 8.3269962e-6. Keep MSE, rank/alpha 32, dropout 0.05, effective pair batch 32, two-pair microbatches, seed 7, gradient clipping 1.0, weight decay 0.01 and all representation/data identities.

Validate after every completed epoch. A strict validation Spearman improvement resets patience; retain the earlier checkpoint on ties. Stop after five consecutive checks without improvement or at total epoch 24. Validation patience is an empirical stopping rule and does not establish training stationarity.

The observed initial epoch took approximately 1,950 seconds including validation. The remaining 23 epochs would take about 12.5 hours at that rate. Allow 57,600 seconds (16 hours) for fitting/validation and 61,200 seconds (17 hours) for native GPU stages. These safety ceilings include sufficient room for the declared remaining epochs at the observed speed and the 125% next-epoch reserve. If actual throughput changes enough to trigger a resource stop, report the stop explicitly; do not claim validation convergence.

Use a separate run name, `patience5_lr2e5_20261024`, and preserve the parent. Model selection uses validation only. Capture test predictions after fitting and selection, and compute metrics independently through the existing native EVAL. Publish through the existing asynchronous queue without delaying local scores. Keep large artifacts in sealed native storage and retain exact evidence for continuation. When reporting, preserve initial-run results and distinguish the continuation.

```bash
python -m csts_pilot.baseline_run --check-inputs --phase lora --settings configs/csts-tranche-2-lora-continuation.json
python -m csts_pilot.baseline_run --execute --phase lora --name patience5_lr2e5_20261024 --settings configs/csts-tranche-2-lora-continuation.json --continue-from baseline_results/lora/initial/summary.json
```

The executor must verify parent native references, source/runtime identities and the absence of another trainer before launch. Keep publication and reporting on CPU, then stop the pilot only after measurements and required publication receipts are retained. Preserve persistent disks and the original run evidence.
