# Overnight C-STS results — 26 October 2026

**No new system beat the saved Qwen baseline. Stop GPU experiments and retain the existing model.** All six trained alternatives missed the fixed validation Spearman requirement. No new candidate test extraction or evaluation ran.

## Measurements

Full validation cohort: 1,830 comparisons in 688 source groups. Positive ratings are 4–5; negative ratings are 1–2. Every row remains in regression/ranking. Each system's validation cutoff retains 90.11% positive recall.

| System | Validation Spearman | MSE (0–1 scale) | Condition ordering | FPR at matched recall |
|---|---:|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | 90.15% | **9.69%** |
| Same-passage subtraction + head | 0.763242 | 0.045916 | 90.85% | 13.20% |
| Population translation + head | 0.769697 | 0.049334 | 91.12% | 12.58% |
| Population component removal + head | 0.770358 | 0.048931 | 90.43% | 11.55% |
| CASE-style residual + head | 0.695586 | 0.056846 | 88.07% | 24.95% |
| Condition-query attention: ratings | 0.710713 | 0.052670 | 87.66% | 24.12% |
| Same attention: ratings + span CE, weight 0.1 | 0.598905 | 0.070324 | 82.80% | 38.76% |

The validation gate required Spearman at least 0.7875746597420997, condition ordering no more than one percentage point below Qwen, and FPR no more than one point higher. None qualified. The attention numbers above are CPU replays of the saved, validation-selected checkpoints, with the integrity limitation below disclosed.

Archived test comparators remain Qwen **0.7885050017660868** and GPT-6.1 Sol max **0.8029168452132416** on the same 2,620 rows / 1,241 groups. Those are prior results; no new candidate reached sealed test predictions, so a candidate-minus-GPT test bootstrap is inapplicable.

## What the attention experiment establishes

The two heads have identical initial-state and fitting-cohort hashes, seed 7, and the same 6,942 fitting comparisons. They selected epochs 4 and 10, respectively; patience stopped training after epochs 9 and 15. Their stopping points and optimizer-update totals therefore differ.

Adding span supervision reduced validation Spearman by **0.111808**. A retrospective 2,000-draw paired source-group validation bootstrap, seed 61024, gives an evidence-minus-ratings interval of **[−0.143302, −0.081973]**. The FPR change is +14.64 percentage points, interval **[+9.70, +19.57]** points. These are validation diagnostics for selected checkpoints, not fresh-test confirmation or seed uncertainty. Squared prediction error improved on 823 rows and worsened on 1,007.

Training extraction retained 13,960 passage occurrences. Existing accepted teacher answers covered 9,141; 8,984 aligned to a unique literal token span, with 157 accepted answers lacking unambiguous alignment. Actual bank-excluded fitting batches contained 8,940 supervised passage occurrences per epoch. Validation caches contained zero teacher target mass during fitting and selection.

After both heads were fixed and found ineligible, a separate CPU-only development diagnostic joined the existing teacher cache to validation passages. It found 2,312 aligned occurrences, representing 2,269 unique passage-condition pairs, out of 3,660 occurrences.

| Post-selection dev diagnostic | Ratings-only | Ratings + span CE |
|---|---:|---:|
| Mean attention mass on accepted copied span | 9.52% | **75.54%** |
| Top-attended token falls within copied span | 9.52% | **78.55%** |
| Mean normalized attention entropy | 0.000341 | 0.364332 |

Uniform attention would put 38.86% mass on these spans on average. The evidence-trained readout learned agreement with the cached teacher's localization, while its similarity predictions became worse. These spans are model-produced, source-checked targets, not independent human grounding judgments. The 75.54% measurement does not establish that the teacher selected every distinction needed for JEP.

The ratings-only readout was almost one-token attention on this dev subset. A plausible explanation is that copying/localizing relevant words and preserving a sufficient representation of their relational meaning are different objectives. Frozen causal passage-token states also lack the full right context available to the original final-token readout. These are hypotheses to test, not identified causes.

## Integrity and execution closeout

Both attention TRAIN runs and both token-extraction runs succeeded and were sealed. The native CPU selection stage failed its predeclared prediction-replay check: ratings-only exceeded the 1e−5 absolute tolerance on one of 1,830 rows, with maximum difference **3.772974e−5** and mean difference **7.538624e−8**. Evidence-head maximum difference was **1.072884e−6**. Independent CPU replay verified row contents/order, cache/model/bank/config identities, selected checkpoint hashes, and selected-model trace hashes. Spearman matches to six decimals and the failed-eligibility conclusion is unchanged.

**The native selection attempt remains failed. Its tolerance was not widened and its failure was not reclassified as a successful native selection.** The CPU diagnostic records an independently computed negative decision; it authorizes no test stage. No experiment-code change, retraining, baseline rerun, seed sweep, loss-weight sweep, new resource, or Spanish ground-truth creation was used to close out this screen.

The prior disk-full failure and interrupted launch remain preserved. Disk recovery removed 35 reconstructible cache copies only after matching them to preserved immutable-store originals. All eight successful Tranche 5 runs and all four successful Tranche 6 runs were verified cloud-published. The GPU had no active experiment process at closeout.

## JEP research direction

Keep the selected Qwen model for candidate retrieval and initial grouping. The subtraction systems did not improve discrimination; the new attention experiment demonstrates that better teacher-span localization can coexist with worse similarity. Further reference subtraction or span-loss sweeps are not the supported next step from these results.

The next useful comparison is the distinct **answer-as-input** route: express the condition-specific proposition, including actor, requested action, object/beneficiary, polarity and attribution, then compare representations of those answers while retaining original-source citations. A copied span can identify the right words while dropping the relationships that determine whether two demands should merge. This is the Tu-style route; auxiliary span supervision did not test it. It should be compared with the unchanged Qwen system under a new reviewed plan, not launched as a continuation of a failed gate.

For a bounded JEP pilot, have experts adjudicate nearest-neighbor pairs that would merge into one codebook entry. Include related-topic pairs differing in demand, beneficiary, negation, modality or attributed speaker. Use expert-validated condition-preserving paraphrases and condition-changing edits to distinguish retrieval failures from false codebook merges. Measure false merges at a fixed retrieval-recall target and inspect supporting evidence. This directly tests the intended discovery workflow using the existing expert-review budget; it avoids assuming an English C-STS gain will transfer to Colombian hearings.

IPED remains architectural motivation: the inspected official repository supplies no released checkpoint. This experiment is a new adaptation and does not rule out UIE or end-to-end evidence-aware models.

## Records

- [Four-head result and coefficients](csts_tranche5_verified_result.md).
- [Native attention runs, checkpoint hashes, CPU replay and post-selection diagnostics](csts_tranche6_closeout.json).
- [Frozen attention plan](../plans/csts-tranche-6-evidence-attention.md).
- [Execution handoff and recovery history](../plans/csts-overnight-20261026.md).
- Tranche 5 source: `faa0ae537feea2333b5c245c9b23e0829729441c`.
- Tranche 6 source: `934e7d87f485fa8a0739e77255984d3b30ff97cf`; completed training attempt `85314012`, `overnight_cached_model_recovery`.
