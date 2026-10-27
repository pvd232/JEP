# Revised JEP experiment: evidence readout and symmetric comparison

Status: implementation for review; scientific execution has not started. This replaces the earlier A/B/C pilot proposal. The configuration, implementation, synthetic cases and verification record in this PR form one experiment.

## Motivation and working hypothesis

The [frozen full-bank report](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md) changes the starting point. The ratings control reached test Spearman 0.855375 and normalized MSE 0.038359; proposition writing followed by ratings reached 0.863398 and 0.035584. The paired Spearman gain was 0.008024 with a source-group interval crossing zero. These are one backbone seed and independently selected final checkpoints, with different final ratings update counts. They support further investigation of the complete procedure; they do not isolate an objective at fixed compute or establish a replicated effect.

The final proposition model's colour score fell, and colour comprised 120 of the 137 appearance rows. These are overlapping regressions. On 877 same-pair condition comparisons, the proposition model and the stronger generative scorer each got 841 strict orderings right, while their graded errors differed substantially. This motivates testing the comparison rule alongside evidence selection; it does not show that selection is solved. Earlier writing fidelity measured on a smaller capture does not establish fidelity after the final ratings phase.

**Working hypothesis:** proposition supervision creates useful condition-specific structure that the current cosine readout uses imperfectly. A separately supervised evidence readout and a fitted symmetric comparison rule can improve graded similarity, including fine attributes. Useful evidence selection, preservation of writing behavior and improved similarity are separate empirical claims.

This is an exploratory mechanism screen on a benchmark already inspected in this project. A later replication needs fresh evaluation material and independent backbone seeds. This document is a prospective specification for this screen, not a preregistration.

## Design and identifying comparisons

Freeze the final proposition encoder throughout. Fit B/C first, select them on validation, and freeze both readouts before fitting D/E.

| Readout training | Cosine comparison | Fitted symmetric comparison |
|---|---|---|
| Ratings only | B (`ratings`) | D (`ratings_comparison`) |
| Ratings + evidence | C (`evidence`) | E (`evidence_comparison`) |

A (`A_parent`) is the final proposition encoder's original end-of-document cosine score. R (`R_ratings_parent`) is the final ratings control, recomputed on the same current test rows. They are reference baselines and receive no new fitting. The generative scorer's published result is historical context; this experiment makes no new paid teacher requests or claims of matched inference cost.

- **C−B:** primary evidence-supervision contrast with exactly the same cosine rule, architecture, initialization, batches and update exposure.
- **D−B and E−C:** planned comparison-rule contrasts. Each pair uses exactly the same frozen selected sentence vectors. D/E add parameters and ratings fitting, so this estimates the whole specified comparison intervention.
- **E−D:** evidence contrast under the same learned comparison architecture and fitting policy. The comparison weights are fitted separately; this includes the downstream refit and is not a fixed-weight direct effect of evidence loss.
- **(E−D)−(C−B):** descriptive interaction on Spearman and MSE, not a causal mediation estimate.

C−B remains the primary contrast for continuity. All five contrasts, all three seeds and all four cells must be reported, including unfavorable outcomes. Secondary intervals are unadjusted and exploratory; selecting whichever interval is positive is not confirmatory evidence. A positive mean C−B with its source-group interval above zero and the predicted edit behavior supports the narrow readout hypothesis. Secondary comparison gains support the revised comparison hypothesis only for the comparator tested here. Neither finding proves the mechanism is exclusive.

## Frozen data and artifacts

Use `jep-csts-v1.1`: 6,051 training comparisons / 2,635 source groups; 1,576 validation / 680 groups; 2,431 test / 1,222 groups. Targets are `(rating − 1) / 4`. The breakthrough report used the earlier 2,430-row test revision. Recompute A and R on version 1.1; do not subtract historical scores on different cohorts.

Use the complete, existing training capture: **11,909 canonical inputs**, with 11,079 answered, 802 not specified and 28 ambiguous. All 6,051 rating comparisons remain in both readout arms. Alignment failures never delete a rating row. The teacher was `gpt-6.1-sol` with high reasoning effort. Its frozen audit gate and provenance bind the generation policy and bytes. Literal source quotation alignment is not human verification of semantic correctness.

[The configuration](../configs/csts-evidence-readout.json) pins every split, full-bank record/provenance/gate file, writing target file, shared vocabulary head, checkpoint manifest and intervention file. The checkpoint archive is SHA-256 `2e8e8efe52687edb10b85f000f6a2f77637677f59ae95729ee1c254d11c37d9d`; the exact archived manifest is pinned separately because the published manifest contains later storage metadata.

| Checkpoint | SHA-256 |
|---|---|
| Final proposition, fixed encoder | `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f` |
| Selected writing epoch 5, retention reference | `c9fb43635c0797df6d6fe11b675472a269bf03ebfa3264c7791bbd8072d8abc0` |
| Final ratings control, reference R | `667c124a49be72a6fd8e9fa3df6974830e4ab6a46a10243c360dd46bcc75b534` |

The backbone is `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`, with the saved rank-32 attention LoRA adapters. All 4,096 coordinates are retained. There is no new transformer, LoRA, vocabulary-head or sentence-value projection training. Seeds 7/8/9 measure head-fitting variation conditional on this one parent, not independent backbone replications.

Preflight checks input hashes, split counts, training/validation group disjointness, complete canonical teacher identity coverage, duplicate identities, status counts, provenance/gate consistency, manifest/model hashes and the fixed fitting policy. Test bytes are hashed at preflight; test labels are deserialized only after all selected heads are frozen. Stage extraction rejects foreign teacher identities and checks token offsets. Private captions and captured generations are runtime artifacts rather than source additions in this PR.

## Writing-retention diagnostic, before readout fitting

Run the selected writing checkpoint and the final proposition checkpoint with the same frozen vocabulary head and the existing **121 writing-validation targets**. These targets were already used for writing-checkpoint selection and are not a fresh evaluation sample. Verify exact file bytes, canonical passage/condition membership in validation and exclusion from training.

For each checkpoint, compute the mean of per-answer mean causal cross-entropies over all 121 targets, including the terminal EOD token. Report every per-answer loss and the paired mean change after ratings. Use one answer occurrence at a time, avoiding duplicate exposure from a sentence-pair sampler. Freeze all parameters and verify adapter hashes before/after inference.

Also greedily decode the first 32 targets in sorted canonical-ID order, from the identical embedding prefix including EOD, with a fixed 64-token generation ceiling. Stop at EOD, retain raw outputs privately, and report cap hits and whitespace-normalized exact reference agreement. There is no sampling, new teacher generation, semantic grading or threshold tuning. Exact agreement and reference CE are writing-retention proxies, **not factual accuracy**. In particular, a CE increase is not by itself proof that the model lost the fact rather than changed its phrasing.

This audit reports evidence for interpreting the fixed screen. It does not automatically choose a new encoder, stop an unfavorable run or change the fitting objective. If writing appears degraded, preserving an auxiliary writing objective during ratings is a separate follow-up. If writing remains intact while scoring improves through D/E, a readout/comparison limitation becomes more plausible. Neither outcome uniquely identifies a cause.

## Token extraction and evidence readout

Use the unchanged condition/passage embedding prompt, explicit terminal EOD, maximum prefix length 160, and the original two-comparison, left-then-right forward layout (four inputs per encode batch). Inputs that exceed the prefix ceiling fail instead of truncating evidence. Source and condition positions are bound by tokenizer character offsets; special/prompt tokens are excluded from source evidence.

Cache final-layer contextual source states $h_t \in \mathbb{R}^{4096}$, the mean of condition-prefix states $u$, and normalized EOD vectors. Under causal attention the condition prefix precedes the passage. Its query therefore does not read later passage tokens directly. Each occurrence retains its original comparison binding and source offsets. Cache source states in bfloat16 and compute readouts in float32. Adapter bytes are checked before and after extraction.

For each readout:

```math
\begin{aligned}
q &= W_q\mathrm{LN}(u), & k_t &= W_k\mathrm{LN}(h_t), \\
\ell_t &= q^\top k_t/\sqrt{128}, &
\ell_\emptyset &= q^\top k_\emptyset/\sqrt{128}+b_\emptyset.
\end{aligned}
```

$W_q,W_k$ map 4,096 to 128 for attention scores only. The value and output sentence vectors retain all 4,096 coordinates. There are 1,048,705 readout parameters. Padding logits are $-\infty$. A joint softmax over null plus source positions gives evidence probabilities $p$. Unknown irrelevant words are not forbidden at inference.

Compute source-conditional content independently of null mass:

```math
\begin{aligned}
\alpha_t &= \mathrm{softmax}_{t\in\mathrm{source}}(\ell_t), &
v &= \sum_t\alpha_t h_t, \\
z &= v/\|v\|_2, &
\widehat{y}_{B,C} &= z_1^\top z_2.
\end{aligned}
```

The separate source softmax remains stable even when joint null probability approaches one. Reject nonfinite and near-zero directions. Null probability is an uncalibrated addressability proxy; it never gates a score, changes a target or removes a row. Ratings alone do not identify null-only parameters.

Answered records supervise the union of uniquely occurring literal **evidence quotations**, using a uniform target on overlapping source tokens. They do not align the possibly paraphrased answer string. `not_specified` targets null. Ambiguous, uncaptured, absent/repeated-quotation and unaligned records contribute zero evidence loss, with explicit coverage reasons. Missing capture never means missing information.

For a rating batch of size $m$ and supervised sentence occurrences $S$:

```math
\begin{aligned}
L_r &= \frac1m\sum_i(\widehat{y}_i-y_i)^2, \\
L_e &= -\frac1{|S|}\sum_{s\in S}\sum_{t\in\{\emptyset,\mathrm{source}\}}g_{st}\log p_{st}, \\
L_B &= L_r, \qquad L_C=L_r+0.1L_e.
\end{aligned}
```

With no supervised occurrences, $L_e$ is a differentiable zero. Exclude padding from the log-probability reduction before multiplying targets, avoiding $0 \times (-\infty)$. Sentence occurrences inherit rating-pair sampling frequency; evidence is not rebalanced by unique record.

## Symmetric comparison intervention

After selecting B and C, freeze their parameters and materialize detached, full-width training/validation vectors separately. D uses B's vectors and E uses C's. Verify readout hashes before/after comparator fitting and reject any new readout gradient.

Fit an 8,193-parameter residual scorer:

```math
\widehat{y}_{D,E}=z_1^\top z_2+
w_\Delta^\top|z_1-z_2|+w_\times^\top(z_1\odot z_2)+b.
```

All residual weights and the bias start at zero, so epoch zero reproduces the corresponding cosine score exactly. Both feature blocks include every coordinate. The score is invariant to swapping the two sentences. No null features, condition-specific biases, hidden sentence projection, dropout or test calibration are introduced. Scores are not clipped to [0,1]; report their range and fraction outside the target range.

This is a limited, interpretable comparison intervention: it tests fitted coordinate weighting and absolute differences, not arbitrary cross-coordinate or token-to-token reasoning. A null result cannot rule out richer comparison functions. D/E receive only rating MSE, and their epoch-zero cosine candidates remain eligible for validation selection.

## Optimization, checkpoint selection and native records

For each seed, initialize one readout with default PyTorch linear initialization and zero null key/bias, then deep-copy it to B/C. Process identical seeded permutations and batch boundaries in lockstep. Use AdamW, learning rate 0.001, weight decay 0.01, batch size 32 and global gradient clipping at 1. Select each arm's **first strictly best complete-validation Spearman** checkpoint independently. Stop both after five completed epochs improve neither arm, with a ceiling of 48. Equal terminal update exposure does not imply equal selected epochs.

Then fit D/E in lockstep with the same optimizer settings, matched zero initialization and a shared permutation generator seeded with `seed + 10000`. Use a fresh joint patience of five and ceiling of 48. Independently select the first strictly best checkpoint, including epoch zero. Only comparator parameters receive gradients. Readout selection and comparator selection reuse validation; this two-stage procedure and its selection opportunities are part of the method.

Preserve selected CPU-cloned weights separately from terminal weights for both phases, optimizer states, loader-generator/RNG state, epoch/update counts, common order hashes, selected validation predictions and weight digests. Report each phase's stopping reason. Reaching an epoch ceiling is budget censoring, not convergence. A native timeout is a failed attempt, not a publishable partial result.

Native validation metrics stream phase-specific epoch records with monotonic steps. An explicit final reporting step recomputes the selected four-cell validation metrics; it is not a training epoch. Hyperparameters are fixed, with no test-guided tuning or reruns based on unfavorable scores.

## Outcomes and diagnostics

The primary outcome is mean test Spearman C−B across three seeds on all 2,431 comparisons. Report each cell, each seed, A/R, all five contrasts, normalized MSE, sample standard deviation of seed differences, selected epochs and prediction ranges. MSE on the original rating scale is 16 times normalized MSE. No cosine clipping, rescaling or fitted test calibration is used.

Use 2,000 paired source-group bootstrap draws, sampling all 1,222 source groups with replacement and retaining their member rows together. Use the same sampled groups for every seed and cell. Within each draw, compute each per-seed contrast then average across seeds. Export percentile 95% intervals for Spearman and MSE and undefined-draw counts. These intervals concern test-source sampling conditional on the retained head/backbone seeds; they omit checkpoint-selection, teacher-policy and project-wide search uncertainty.

Required diagnostics are:

- Writing-retention results and raw generated probes, with reference agreement kept separate from semantic fidelity.
- Full-bank status, canonical identity and token-alignment coverage; report unique records and sentence occurrences distinctly.
- Separate rating MSE, teacher CE and training-only top-1 teacher agreement; query/key gradient norms, weighted evidence-to-rating ratio and cosine on the first batch of each readout epoch. Diagnostic gradients do not accumulate into optimizer updates; null-only parameters are excluded.
- Per-condition metrics and frozen descriptive condition-family metrics, including colour and appearance membership IDs. These subsets overlap and are not independent confirmations; unmapped conditions remain visible.
- Same-unordered-sentence-pair comparisons across distinct conditions with unequal targets: strict correct count, exact ties, half-credit tie accuracy and squared error of predicted score differences. Keep all eligible combinations; do not equate source groups with identical sentence pairs.
- Source-attention entropy and null quantiles on the complete test set, without fabricated held-out evidence labels. D/B and E/C must have identical selection behavior because their readouts are fixed.
- All synthetic cases individually, source-token counts, source/input/cache/model hashes, native references, stopping state and failure state.

[The fixed intervention suite](../configs/csts-readout-interventions.json) has six cases: car/dog/shirt colour, cat posture, exact cup count and ball position relative to a chair. Each has base, irrelevant-edit, relevant-edit and missing-property variants paired with a fixed reference. Numeric ratings are illustrative bookkeeping, not benchmark labels. Re-encode the actual edited text independently after all checkpoints freeze; do not delete states from an old cache as a substitute for textual intervention.

Report irrelevant absolute score change, base-minus-relevant score, quoted-evidence conditional attention mass, and missing-minus-base null probability for every case/arm. The evidence hypothesis predicts smaller irrelevant change, preserved sensitivity to relevant changes, more mass on the designated source phrase and increased null mass for unavailable facts. Do not claim these directions are guaranteed in every ambiguous semantic case. Joint null softmax has a source-length effect; inspect token counts before interpreting answerability.

These hand-authored probes are mechanism diagnostics without inferential confidence claims. Contextual token states retain surrounding information, so quotation agreement alone does not prove exclusive evidence use. Text edits alter hidden states and sometimes naturalness. This is not a claim of causal rationale faithfulness or a complete sufficiency/comprehensiveness evaluation.

## Decision table

| Observed pattern | Interpretation | Follow-up |
|---|---|---|
| C improves selection/edit behavior but C−B is flat; D−B or E−C improves scores | Supports testing this comparison rule as a limitation on fixed selected vectors | Replicate before a richer comparator or joint fine-tune |
| C−B and E−D improve, with predicted edit behavior | Evidence supervision helps under both specified comparison policies | Replicate across backbone seeds and fresh reviewed data |
| E−D improves while C−B is flat | Evidence benefit depends on the learned comparison pipeline; includes its refit | Inspect interaction and compare richer rules prospectively |
| D−B/E−C improve while both evidence contrasts are flat | The comparison intervention helps; added evidence supervision has no demonstrated benefit here | Review teacher quality, alignment, gradients and redundancy |
| C beats A but matches B | Readout fitting helps; no demonstrated evidence-objective gain | Keep capacity/pooling explanations open |
| Writing retention declines after ratings | Consistent with forgetting or output/wording drift; not a definitive factual-loss diagnosis | Independently review generated probes; test preserving writing in a later ratings phase |
| All fitted heads remain below A | No practical improvement over the existing proposition scorer | Inspect representation and optimization losses before expanding complexity |

## Execution and review handoff

`csts_pilot.evidence_readout_run` publishes the three verified frozen checkpoints as native artifacts, runs retention, extracts training/validation states, fits all three four-cell seed bundles, and writes a frozen selection receipt. Only then does it extract test/intervention states and the final ratings reference. It publishes canonical test/holdout inputs to stored artifacts before the native EVAL stage. Cross-stage cache/model bindings have distinct materialization paths. Final native metrics recompute the report's fixed C−B contrast in a separate metric worker; it is never a test selection rule.

The controller requires a clean pinned source commit and unchanged settings/input hashes, rejects duplicate workers, waits for shared GPU leases, verifies an idle single NVIDIA L4 and holds the leases through the study. It does not preempt workloads. Queue state persists through SSH disconnection; reboot recovery and uncertain attempts require explicit reconciliation of sealed runs. Stage timeout is four hours. Local artifact sealing and asynchronous VIPER cloud publication are recorded separately.

```bash
python -m csts_pilot.evidence_readout_run \
  --root /home/machina/jep-csts-evidence-readout-20261027 \
  --expected-source REVIEWED_COMMIT \
  --name evidence_readout_revised_20261027
```

The private run directory contains `queue.json`, `summary.json`, `selection.json` and worker logs. Native stdout streams per-epoch progress; `summary.json` points to retention and final reports. This PR does not itself launch the scientific study.

The CPU native check seals random 5D fixtures, fits three complete B/C/D/E bundles, freezes them, binds stored held-out inputs, executes EVAL and its separate metric worker, and checks all five contrasts. Its values are transport checks, not scientific findings. It does not validate real Qwen GPU kernels or factual writing retention. See [the implementation review](csts-evidence-readout-review.md) for actual completed checks and remaining limits.

## Relation to prior literature

[SEAVER](https://aclanthology.org/2024.findings-emnlp.5/) motivates distraction-sensitive readouts for C-STS. [Bastings, Aziz and Titov](https://aclanthology.org/P19-1284/) motivate separating selection and prediction. [ERASER](https://aclanthology.org/2020.acl-main.408/) motivates separating rationale agreement from influence on predictions. These papers motivate the tests; they do not establish this frozen-Qwen, teacher-supervised architecture's efficacy. The revised working hypothesis is an inference from the JEP results and related designs.
