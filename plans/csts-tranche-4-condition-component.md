# Tranche 4: condition-reference correction and a conditional LoRA follow-up

**Status: executed; stopped at the validation gate.** See the [completed report](../training_outputs/csts_condition_reference_report.md). All five interventions missed eligibility. Test scoring and conditional training remain unstarted. The original prespecified plan is retained at extraction source `c7f5bf04e18d4a4efced86a2533dcfd9c4a03858`, with SHA-256 `3eaf1b31528f7af61fd30efaefd8c20d5810df46e5d4008c99fc203898a19520`.

The immediate experiment uses the selected checkpoint with zero optimizer updates. A successful subtraction result can advance to a matched LoRA continuation. This document follows the [earlier tranche format](csts-tranche-3.md). The [derivations](csts-tranche-4-derivations.md) define every calculation and gradient used below.

## Question and working hypotheses

Can reference subtraction improve discrimination between similar and dissimilar passages while retaining conditional ranking and similar-pair recall?

A shared prompt or condition component may raise cosine scores between dissimilar passages. Sentence-only pooling may alter the information retained by the passage representation. These are proposed mechanisms. Their measurements are reference alignment, geometry summaries, and predictive comparisons.

The experiment separates condition-containing reference subtraction, generic prompt subtraction, normalization order, and sentence-only pooling. Every inference arm reuses the same extracted passage states.

## Preliminary evidence and provenance

The selected ratings-trained Qwen checkpoint achieved **0.788505 test Spearman** and **0.070763 test MSE**. Reference similarities 0 and 1 have mean predicted cosines 0.316 and 0.797. This is an observed compression toward the middle. A strictly increasing rescaling preserves ranks and the attainable false-positive/recall tradeoff; the derivations explain why operating-point comparisons are needed.

For the prior binary diagnostic, reference ratings 1–2 define negatives and 4–5 define positives; rating 3 is excluded. At cutoff 0.50, false-positive and missed-positive rates were 14.8% and 10.9%. At 0.75, they were 1.7% and 41.8%.

The [retained results](https://github.com/pvd232/JEP/blob/beffa1f4c62141081419787b62a525a74ce9a5e3/training_outputs/csts_qwen_evidence_results.json) identify the native producers. The diagnostic used the sealed ratings prediction file with SHA-256 `9ececbf76ac63b420196b4b4ef1285b5f632601a81043915d9236d9190cd1f24`.

The test benchmark has already been examined. A frozen validation decision followed by another test measurement provides a controlled comparison on that existing benchmark.

## Relationship to CASE

| System | Representation and subtraction | Learned parameters | Objective |
|---|---|---|---|
| Main CASE method | Encode the condition given the sentence; subtract the standalone condition representation; project the residual. | Projection network; encoder fixed. | Cosine-MSE. |
| Authors' Qwen LoRA comparison | Condition-containing text; normalized final-token representation. | Attention adapters. | One minus batch Pearson correlation. |
| Our completed LoRA model | Our instruction-plus-passage prompt; normalized EOD state. | Attention adapters. | Cosine-MSE. |
| Proposed diagnostic | Subtract references in two normalization orders. | Zero updates. | Predictive evaluation. |
| Conditional follow-up | Put the selected subtraction inside the LoRA scoring path. | Attention adapters. | Cosine-MSE. |

The authors' Qwen wrapper returns pooled states directly before the main CASE subtraction and projection. Our unit-first arm subtracts native unit vectors. The raw-first arm retains relative vector norms during subtraction. Both variants are explicit local adaptations of reference subtraction.

Sources: the [authors' wrapper](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/llm_encoders.py#L71), [subtraction](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/generate_embeddings.py#L61), [projection](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/CASE_performance.py#L126), and [LoRA loss](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/lora_finetune.py#L161).

## Frozen model and data

Use `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`, with selected ratings-only adapters SHA-256 `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`. Retain the tokenizer, explicit attended `<|endoftext|>`, 160-token ceiling, BF16 backbone operations, float32 reductions, and 4,096-dimensional output.

Keep the partition hashes in the [existing settings](../configs/csts-qwen-evidence.json): 6,980 training, 1,830 validation, and 2,620 test comparisons. The validation/test partitions contain 688/1,241 connected source groups.

The prompt is:

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: <condition>
Query: <passage>
```

Append EOD after the passage. A condition reference uses the same prompt with an empty passage. A generic prompt reference uses both fields empty. Empty passages are reference inputs with their own metadata; benchmark rows retain their original contents.

## Exact inference arms

`last(passage, condition)` is the final attended contextual state before external L2 normalization. Backbone normalization remains part of the model. `unit(v)` divides a nonzero vector by its Euclidean length. Each reference uses the selected adapters.

| Arm | Vector scored by cosine | Comparison isolated |
|---|---|---|
| A | `unit(last(passage, condition))` | Current native representation. |
| B_u | `unit(unit(last(passage, condition)) - unit(last("", condition)))` | Condition reference, unit-first subtraction. |
| B_r | `unit(last(passage, condition) - last("", condition))` | Condition reference, raw-first subtraction. |
| C_u | `unit(unit(last(passage, condition)) - unit(last("", "")))` | Generic prompt reference, unit-first subtraction. |
| C_r | `unit(last(passage, condition) - last("", ""))` | Generic prompt reference, raw-first subtraction. |
| D | Unit-normalized mean of final contextual passage-token states. | Sentence-only pooling. |

The reference coefficient is fixed at 1 in every subtraction. The coefficient and normalization orders are fixed before evaluation.

Cache raw final states and raw passage means from the same model forward pass, together with their norms. Cache each condition reference once and the generic prompt reference once. The additional normalization-order comparisons require CPU vector operations.

Build D's mask from positive character overlap with the passage span, intersected with the attention mask, and exclude special/EOD/padding positions. A token carrying the first passage word and its leading whitespace is included. Record token counts and reference similarities.

All input vectors, means, and residuals must be finite. An empty mask or vector norm at or below 1e-8 fails the affected arm and produces an ID-level coverage report. Arm metrics require the full original cohort.

## Tranche A: validation diagnostics

All weights remain fixed in evaluation mode. Optimizer updates: **zero**.

Recompute metrics from sealed baseline predictions and check model/input identities. Re-encode the baseline using the same precision and batching conventions; require score agreement within 1e-3 per comparison. Reconcile larger differences before interpreting interventions.

For each arm, report:

- Spearman, MSE, condition ordering, prediction means by rating, and signed errors.
- Binary confusion counts, false-positive rate, recall, and missed-positive rate.
- Global and within-condition mean-vector norms, mean pairwise cosine, covariance spectra, leading-component variance share, and variance participation rank.
- Passage/reference norm ratios, passage-to-reference cosine, and residual norms.
- Wall time, processed tokens, and peak GPU memory.

Use unique passage–condition inputs for geometry and identical keys across arms. Report per-condition geometry for groups with at least 16 unique passages; record source-group counts and the sample-imposed covariance-rank ceiling. Smaller groups retain predictive measurements.

For binary metrics, negatives are reference ratings 1–2 and positives are 4–5. All ratings remain included in regression and ranking metrics.

For each arm, choose the largest validation cutoff attaining at least **90% recall** on validation positives. Predict positive when cosine is greater than or equal to that cutoff, including ties. Freeze the cutoff. Report achieved recall and false-positive rate, plus descriptive measurements at 0.50 and 0.75. The derivations give the exact order statistic.

## Tranche B: validation selection

Retain B_u minus A as the primary planned diagnostic comparison. Prespecified additional comparisons are:

| Comparison | Interpretation |
|---|---|
| B_r minus A | Raw condition-reference subtraction. |
| B_u minus B_r | Normalization order for the condition reference. |
| C_u minus A; C_r minus A | Generic prompt subtraction in each order. |
| B_u minus C_u; B_r minus C_r | Additional effect of the condition-containing reference at a fixed normalization order. |
| D minus A | Pooling change. |

Candidate eligibility requires an absolute false-positive-rate reduction of at least **2 percentage points** at the validation recall target and a Spearman decrease of at most **0.005**. These are proposed project decision tolerances.

Choose the eligible candidate with lowest false-positive rate; ties favor higher Spearman, native final-token pooling, fewer reference encodings, then fixed arm order B_u, B_r, C_u, C_r, D. When every candidate misses eligibility, retain A, publish validation findings, and complete the immediate experiment.

Freeze the selected arm, references, masks, normalization order, cutoff, hashes, and analysis settings before Tranche C.

## Tranche C: frozen test comparison

Evaluate A and the selected candidate on the existing 2,620 test comparisons. Carry each arm's validation cutoff into test unchanged. Report realized test recall alongside false-positive rate; the operating points share a validation recall target.

Report all regression/ranking metrics and error strata. Use 2,000 paired source-group bootstrap draws over the same 1,241 groups, seed 61024. Thresholds remain frozen in every test bootstrap draw.

The practical transfer rule requires at least a 2-percentage-point false-positive-rate reduction, test recall declining by at most **1 percentage point**, and Spearman declining by at most **0.005**. Report point differences and paired intervals. Retain A when the candidate misses this rule.

These observations concern the existing English benchmark. Spanish JEP transfer remains a separate evaluation task.

## Tranche D: conditional LoRA continuation

This follow-up applies to a reference-subtraction winner from B_u, B_r, C_u, or C_r that passes Tranche C. A winning sentence-mean arm motivates a separate pooling-training comparison.

Use two actual training arms from the same selected parent:

| Training arm | Forward representation used in MSE |
|---|---|
| T_A | Native normalized final-token embeddings. |
| T_R | Selected reference-subtracted representation. |

Retain two frozen comparators: parent A and the selected zero-update corrected parent. They separate post-processing from subsequent training. Report both trained endpoints and each continuation's improvement over its own frozen parent.

Both training arms restore the same adapter weights and start fresh AdamW states. Retain seed 7, rank/alpha 32, attention targets q/k/v/o, passage-branch LoRA dropout 0.05, learning rate 2e-5, weight decay 0.01, effective batch 32, two-pair microbatches, gradient clipping 1, constant rate, and zero new warmup.

Both use all 6,980 training comparisons, the same pair-order seed, a ceiling of 24 continuation epochs, validation Spearman selection, and patience five. Include each arm's epoch-zero parent as a checkpoint candidate; ties retain the earlier checkpoint. Report continuation epochs and lineage: the selected parent is total epoch 4 of a run that completed 9 epochs.

For T_R, compute passage and reference representations using current adapters at every optimizer step. Autograd reaches both branches. Recompute references per microbatch; any within-microbatch deduplication must preserve their summed gradient.

Proposed reference-branch policy: evaluation-mode dropout with autograd enabled. Passage branches retain training dropout. This makes the reference deterministic for current weights and preserves the passage random stream across arms. Inference uses evaluation mode throughout. Validate the mode policy in the preflight.

References can be cached across inputs after weights are frozen. Every cache key binds model/adapter hashes, prompt bytes, condition string, pooling rule, and normalization order.

Select both trained checkpoints using validation, derive their validation recall cutoffs, freeze all identities, then evaluate the existing test cohort. Apply the same predictive metrics and paired source-group analysis. Keep the MSE objective fixed.

## Resources and execution contract

Immediate diagnostic allowance: **30 GPU minutes for validation and references, 30 GPU minutes for test, and 30 CPU minutes for analysis**. Collect all six inference arms through shared extracted states.

Conditional continuation allowance: **16 GPU hours per training arm**, plus **one aggregate GPU hour for prediction capture**. The proposed follow-up ceiling is 33 GPU hours. Preflight must measure passage/reference throughput and memory against that allowance. Record comparison exposure, reference-token overhead, updates, and actual stopping causes.

Use native VIPER BUILD for fixed-checkpoint extraction, references, predictions, and selection; use TRAIN for any later continuation. Separate CPU EVAL independently recomputes metrics. Existing workers publish sealed local artifacts asynchronously as scoring and reporting proceed.

Record source/model/input hashes, native attempts, normalization order, masks, reference keys, thresholds, per-row scores, and timing receipts. Preserve source storage until publication is durable.

## Implementation review and mathematical verification

The [measurement runner](../csts_pilot/condition_reference_run.py) and [extraction/evaluation implementation](../csts_pilot/condition_reference.py) are implemented. Execution retained the original two-pair forward batch layout to pass native-score reproduction. All passage occurrences are captured; geometry selects the first occurrence per unique input. The completed report records the batching correction and evaluator recovery. The implementation follows the existing [representation](../csts_pilot/baseline_models.py) and [training](../csts_pilot/baseline_stages.py) contracts.

Implementation checks cover offsets, padding/EOD handling, shared extraction, both subtraction orders, residual coverage, zero diagnostic parameter updates, full reference gradients, reference dropout policy, exact microbatch weighting, checkpoint restoration/selection, and frozen validation thresholds. Apply Pyrefly, Ruff, and focused checks before measurement.

The [derivations](csts-tranche-4-derivations.md) cover the readout, six arms, normalization Jacobian, reference gradients, LoRA updates, MSE/Pearson distinction, geometry, operating points, and source-group uncertainty. A validation receipt records numerical gradient and algebra checks.

## Sources

- [Tranche 2](csts-tranche-2.md), [Tranche 3](csts-tranche-3.md), and [Qwen evidence design](csts-qwen-evidence.md).
- [Selected Qwen results](https://github.com/pvd232/JEP/blob/beffa1f4c62141081419787b62a525a74ce9a5e3/training_outputs/csts_qwen_evidence_results.json) and [fixed settings](../configs/csts-qwen-evidence.json).
- [CASE paper, v5](https://arxiv.org/html/2503.17279v5#S3) and the authors' pinned source files linked above.
- [Qwen embedding configuration](https://huggingface.co/Qwen/Qwen3-Embedding-8B/blob/c90816d848505624c2434128dfc61132162a0ee9/config.json).
- [Mathematical derivations and source map](csts-tranche-4-derivations.md).

