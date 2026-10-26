# Tranche 7: answer as the similarity input

Authorized 26 October 2026. The user requested execution of the proposed answer-as-input route. First run a bounded, zero-update diagnostic using existing teacher answers and the selected Qwen+LoRA checkpoint. Reuse saved baseline predictions; do not rerun the baseline or train another control head.

## Representation and cohort

For each single passage and condition, use its accepted copied teacher answer. The cached answer was generated without the companion passage or similarity label and passed literal-source and teacher checks. It is model supervision, not human ground truth. Preserve the original passage for every unavailable or rejected answer. Keep every one of the 1,830 validation comparisons.

Compare two fixed systems: `cached_span_conditioned` encodes accepted answers under the original condition; `cached_span_generic` encodes accepted answers under the fixed condition “overall meaning.” A fallback passage always keeps its original condition. Never represent absent information with a shared missing-value vector. If neither side has an accepted answer, reuse that pair's saved baseline score exactly.

For accepted answer a(x,c), the first system scores

\[
s(x_1,x_2,c)=z(a(x_1,c),c)^\top z(a(x_2,c),c).
\]

Here x is a passage, c its condition, a is its accepted copied answer (or the original passage when unavailable), and z is the frozen Qwen+LoRA encoder with unit output. The generic system changes c to “overall meaning” only for accepted answers. Each passage is represented independently; the final score is the inner product of unit vectors.

Use the original final-token readout and two-pair, left-then-right batching. No optimizer updates or new paid resources. Extraction allowance: 1,200 seconds; native stage allowance: 1,800 seconds. The existing L4 GPU lock prevents overlapping runs. Publish events every 15 seconds and each arm's metrics immediately.

## Decision and interpretation

Report Spearman, rating MSE, condition ordering and FPR at the baseline's validation recall (approximately 90.11%). Also report both-answer, one-answer and neither-answer coverage with matched saved-baseline subset metrics. Eligibility requires a 0.005 Spearman gain with no more than one percentage point worse FPR or condition ordering. Validation alone selects a candidate; no test data is read by this screen.

This first screen is an extractive answer-input hybrid. Tu's method generates concise answers and trains its answer comparator. A negative frozen-checkpoint result does not reject generated propositions or training on answer inputs. Actor, beneficiary, polarity and attribution fields are relevant to later JEP extraction; this English caption diagnostic does not invent those fields or Spanish labels.

Native artifacts retain all comparison scores, extracted vectors, checkpoint/data/cache hashes, timing and the unchanged adapter-state digest. Cloud publication is queued asynchronously. A failed run remains preserved; repairs use a new attempt name.

## One trained answer comparator

Declared while the frozen screen is still loading the model, before any candidate scores: fit one bias-free 4096-to-128 projection on conditioned answer/fallback embeddings. This checks adaptation to the answer-input distribution. Reuse `baseline_stages.fit_projection` and its existing cosine-MSE, AdamW, seed 7, learning rate 0.001, weight decay 0.01, batch/microbatch 32, validation patience 5, ceiling 48 epochs and 600 fitting seconds. Training uses all 6,980 original training comparisons, preserving their original groups; validation retains all 1,830 comparisons. There is no generic-answer training arm or new native control-head fit.

The selected frozen Qwen+LoRA checkpoint supplies features; only this new projection trains. Transform each accepted passage to its answer while preserving its condition, and retain original passages for absent answers. Apply the learned projection to every representation, including fallback passages. Thus neither-answer pairs receive projected-original scores in this trained system; the frozen screen's direct baseline-score reuse does not apply here.

Share one unique-input extraction across train and validation, with a 1,200-second extraction ceiling. The existing native feature-cache schema binds transformed rows, original data/cache/checkpoint identities and the complete audit map. Preserve group separation, exact prediction identities, full-cohort metrics and the same validation gate. This system comparison does not isolate answer replacement from projection learning, and remains distinct from full Tu encoder fine-tuning. No test scores enter fitting or selection.
