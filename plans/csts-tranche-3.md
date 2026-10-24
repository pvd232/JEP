# Tranche 3: evidence supervision under matched training allowances

## Question

Does learning condition-relevant source evidence improve the conditional FLAN encoder beyond additional rating training or incorrectly aligned evidence? This is the next one-seed follow-up screen on the already examined C-STS benchmark. The stronger Qwen embedding models remain reference systems; this experiment uses the original FLAN encoder-decoder student because its decoder supplies evidence supervision to the shared encoder.

## Frozen design

The three arms are ratings followed by ratings, checked evidence followed by ratings, and shuffled evidence followed by ratings. All restore one exact native initialization: FLAN-T5-small revision `0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab`, seed 7, a bias-free 128-dimensional projection, passage-token mean pooling and unit normalization. Teacher generation is not rerun. Use the existing 17,334-record cache with its source-span and teacher-review decisions, frozen by SHA-256 in the settings. These checks are not expert validation.

Construct the permutation using training inputs only, within the same condition. Keep only accepted keys whose assigned answer changes semantically. The aligned and shuffled arms use the same resulting answer mask. All three arms use the same first-phase comparisons, restricted to rows with at least one such supervised key. Report excluded and retained coverage. The shuffled target distribution is preserved within condition; singleton and unchangeable answers are excluded from every arm's first-phase comparison subset. Validation evidence is never used for gradient updates.

Phase A completes exactly six epochs in every arm. It uses the same initialization, pair permutations, optimizer, schedule and update count. The rating control minimizes rating MSE; the other two arms minimize per-answer token cross-entropy. Each transition uses the terminal sixth-epoch weights. Selecting different first-phase epochs by different objectives would change exposure and is prohibited.

Phase B uses all 6,980 training comparisons, MSE, batch size 32 and a fresh AdamW optimizer. It retains the original 24-epoch schedule: encoder rate 3e-5, projection rate 1e-3, 10% warmup and linear decay. From epoch 25 onward, preserve optimizer moments and use constant rates 3e-6 and 1e-4 with no new warmup. The ceiling is 40 total rating epochs. Patience is five validation checks during the continuation after epoch 24; all arms have the same allowance and stopping rule. Actual terminal epochs may differ and must be reported. This preserves Tranche 1's original schedule prefix and its constant-rate continuation instead of compressing them into a new schedule.

Select the highest validation Spearman, retaining the earlier epoch on ties. Retain separate best and terminal weights, optimizer information, input hashes, initial RNG hashes, epoch permutations, updates, gradient norms, losses, validation predictions and actual elapsed time. The rating-stage initial digest must equal its own phase-A terminal digest. Compare the three phase-A traces for identical initialization, coverage, batch order and update count before testing.

The 1,830 validation comparisons select checkpoints. Freeze all three checkpoint identities before publishing any test inputs in this experiment. Evaluate the same 2,620 comparisons and 1,241 source-caption groups. Similarity inference encodes the original passages and condition; it does not generate or consume teacher evidence. Native GPU BUILD captures immutable predictions; separate CPU EVAL and independent metric workers verify them.

## Outcomes and resource limits

Report Spearman, raw MSE on rescaled ratings, condition ordering and actual cost. The two predeclared contrasts are aligned evidence minus the rating control, and aligned evidence minus shuffled evidence. Use 2,000 paired bootstrap draws over the same source groups, seed 61021. A +0.02 Spearman gain guides subsequent repeated-seed confirmation. This one-seed, previously examined benchmark cannot establish Spanish JEP performance or seed robustness.

Fitting permits 2,400 seconds per phase, and the aggregate native GPU-stage ceiling is four hours. Observed historical FLAN throughput should allow these phases within that allowance; resource stops remain incomplete measurements. Do not shorten training to satisfy an upload deadline.

## Review and execution

Read the preparation and training implementation, runner and focused tests. Required checks are Pyrefly, Ruff, cache-validation and shuffle tests, source/validation separation, evidence gradients, identical phase-A exposure, terminal-weight transitions, exact learning-rate phases, checkpoint selection and frozen test bindings. Complete strict code review before the experimental launch.

Native VIPER first seals local results. Each successful stage queues the existing independent CPU publication worker. Scoring, subsequent stages and result reporting do not wait for cloud publication. Keep the source disk until outstanding publications are durable. This runner does not stop the VM or alter networking.

The default command displays settings. Execution is explicitly authorized by the user's request to stop Tranche 2, evaluate its best checkpoint, and run Tranche 3 after strict review.

```bash
python -m csts_pilot.evidence_run
python -m csts_pilot.evidence_run --execute
```

Resume reuses only verified successful native stages with the same source and settings. An uncertain native invocation requires reconciliation; it must not silently retrain.
