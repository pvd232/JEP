# Tranche 5: matched real-text baselines with supervised projection

**Status: proposed experiment with implementation supplied for review.** This delivery contains the specification, [derivations](csts-tranche-5-derivations.md), experiment code, focused tests, and an MOA review record. The experiment has not started. The [completed Tranche 4](../training_outputs/csts_condition_reference_report.md) remains the latest measurement.

## Question and working hypotheses

Which reference construction produces the most useful conditional similarity representation after the scoring head learns that representation?

The four candidates use a generic representation of the same passage, an average conditioning shift across real training passages, removal along that average direction, and a CASE-style condition-target representation. Each candidate trains one small head. The existing sealed Qwen + LoRA predictions supply the baseline: validation Spearman **0.7825746597420997**, test Spearman **0.7885050017660868**. Baseline scoring, numerical reproduction, and native-head fitting are excluded from this experiment.

The working hypothesis is that references estimated from matched real text can isolate useful condition-dependent variation. A learned scalar can adjust correction strength, and a shared head architecture can adapt each representation to similarity ratings. These are project hypotheses. Their tests are predictive accuracy, conditional ordering, the false-positive/recall operating point, and the affected comparison rows.

Tranche 4 found 0.78257 validation Spearman and a 9.69% false-positive rate at 90.11% recall for native Qwen + LoRA. Its full-strength empty-passage condition subtraction produced 0.69657/0.68956 Spearman and 21.86%/20.00% false-positive rates. The global mean pairwise cosine decreased during condition subtraction. This motivates evaluating the retained task information directly.

## Literature-to-design mapping

| Source | Relevant construction | Experiment consequence |
|---|---|---|
| [CASE, Equation 1 and Section 3](https://arxiv.org/html/2503.17279v5#S3) | Condition-target contextual representation, standalone-condition subtraction, supervised projection. | Include a CASE-style residual and train the same head architecture on the four alternatives. |
| [Persona Vectors, Section 2](https://arxiv.org/pdf/2507.21509) and [authors' extraction code](https://github.com/safety-research/persona_vectors/blob/55b6e5914e81afa104fb0ab8b6e1ffb74b611d98/generate_vec.py) | Difference in average activations from trait-expressing and trait-suppressing response sets. | Estimate a shared conditioning shift from matched real passages. Bank-member stability analysis remains a possible diagnostic extension. |
| [Steering Llama 2 via Contrastive Activation Addition, Section 3](https://arxiv.org/html/2312.06681v4#S3) | Average activation differences from closely matched input pairs; validate the effect of intervention. | Keep passage identity fixed within each conditional/generic reference pair and assess conditional selectivity after correction. |
| [Disentangling Steering Vectors, 2026 preprint](https://arxiv.org/pdf/2609.07037) | Mean-difference directions can combine semantic and stylistic components. | Measure conditional ordering and retain per-row predictions for later feature-specific inspection. |

Persona/steering studies evaluate generative behavior. This experiment evaluates passage similarity using the existing C-STS ratings. The shared mathematical device is a difference between matched activation populations. Task usefulness is established by the present measurements.

The CASE-style arm uses the authors' prompt construction with this project's selected LoRA checkpoint, explicit EOD, rating scale, and source-group partition. Its name identifies the representation construction. Exact reproduction of the paper's reported benchmark score is outside this comparison.

## Frozen model, cohort, and reference bank

Use `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`, with selected ratings-only adapters SHA-256 `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`. Keep all backbone and adapter weights fixed in evaluation mode during extraction. Retain BF16 backbone operations, float32 pooling/reductions, width 4,096, the pinned tokenizer, the 160-token ceiling, and explicit attended `<|endoftext|>`.

| Partition | Comparisons | Connected source groups | SHA-256 |
|---|---:|---:|---|
| Training source | 6,980 | 2,674 | `4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01` |
| Validation | 1,830 | 688 | `f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273` |
| Existing test | 2,620 | 1,241 | `2c8b6f2b62740c85c376eacd02ef222c2bfacdfe8df5f772a4dd7d52b6d38f1e` |

Before any fitting, select a bank of **16 distinct training passages from 16 distinct connected source groups**. The hash key is the UTF-8 encoding of `matched-bank-61026:7:<text>`. Rank groups by the hash of their group ID, with lexical group-ID ties. Within each selected group, choose the passage with the smallest hash of its canonical caption, with original-text lexical ties. Canonical captions use the existing preparation function's Unicode normalization, case folding, and collapsed whitespace. Preserve the original passage text in the bank manifest. Exclude all 16 bank source groups from all four head fits. Record the resulting common fitting row count, IDs, and SHA-256. Preserve the original training-source hash separately.

The selected LoRA checkpoint previously used the original training partition. Bank exclusion establishes disjointness between bank estimation and the new head fits. That lineage remains explicit in the report.

Use the same bank for every condition. A validation or test condition receives references computed from these training-bank passages and its own condition string. Benchmark passage states never enter a population baseline. The generic condition is the exact literal `overall meaning`.

## Exact representation arms

All vectors are columns. Let \(s\) denote a passage, \(c\) its condition, and \(c_0\) the fixed generic condition. Let \(h(s,c)\in\mathbb R^{4096}\) be the raw final attended EOD state from the native prompt below. “Raw” retains model-internal normalization and precedes external unit normalization.

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: <condition>
Query: <passage>
```

Let \(x_j\) be bank passage \(j\), for \(j=1,\ldots,M\), with \(M=16\). Define the shared conditioning shift \(b_c\in\mathbb R^{4096}\) by:

\[
b_c=\frac1M\sum_{j=1}^{M}\left[h(x_j,c)-h(x_j,c_0)\right].
\]

Let \(k(s,c)\in\mathbb R^{4096}\) be the EOD state under the authors' condition-target prompt, and let \(k_0(c)\in\mathbb R^{4096}\) be its standalone-condition reference. Copy the pinned [authors' prompt rules](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/llm_encoders.py#L71), retaining this project's tokenization and EOD contract:

```text
Instruct : Retrieve semantically similar texts to a given Query, under the given Condition Query : <condition>
Condition : <passage>
```

```text
Instruct : Retrieve semantically similar texts Query : <condition>
```

Each head receives a residual \(r(s,c)\in\mathbb R^{4096}\):

| Arm | Residual presented to its learned head |
|---|---|
| M: same-passage baseline | \(h(s,c)-\alpha h(s,c_0)\) |
| B: population translation | \(h(s,c)-\alpha b_c\) |
| P: population component removal | \(h(s,c)-\alpha\frac{b_c^\top h(s,c)}{b_c^\top b_c}b_c\) |
| C: CASE-style residual | \(k(s,c)-k_0(c)\) |

Arms M, B, and P each learn one scalar correction strength, shared across their conditions and passages. Parameterize \(\alpha=\sigma(a)\), where \(a\in\mathbb R\) is its trainable logit and \(\sigma(a)=1/(1+e^{-a})\) is the logistic sigmoid. Initialize \(a=0\), giving \(\alpha=0.5\). In exact real arithmetic, finite logits give \(0<\alpha<1\). Floating-point sigmoid may round to an endpoint. Arm C uses fixed full subtraction.

Keep the existing direct native comparator D0 through its sealed per-row validation/test predictions and producer identities. D0 originally unit-normalized \(h(s,c)\) and scored cosine. This experiment consumes those predictions and performs zero new baseline forward passes or head updates. Native contextual states are extracted only where the four alternative representations require them. The comparison measures each complete corrected-head system against the existing baseline; it includes the candidate head's contribution.

Preserve raw vectors throughout reference construction. Apply external unit normalization after the head. All comparisons use identical cohort rows. Required feature tensors must be finite and have the declared shapes and nonzero norms. The extractor appends attended EOD and rejects a token-ceiling overflow; arm P requires bank-direction norm above \(10^{-8}\). Invalid features or residuals raise an error and preserve a failed native attempt. No comparison rows are dropped. Dedicated ID-level coverage reports are outside the supplied implementation; the cohort, cache keys, and native exception remain available for diagnosis.

## Tranche A: provenance, extraction, and preflight

Validate the declared split and model hashes; check source-group separation; select and seal the bank and common fitting cohort; then freeze the complete extraction manifest.

Preserve the original two-pair forward batch layout for contextual states needed by the alternatives and their generic passage references. Store passage keys, raw states, and per-comparison left/right state indices. Tranche 4 already established native numerical reproduction with this layout. The present plan reuses that evidence and the sealed baseline predictions. No repeated baseline numerical-scoring stage is included.

Bank extraction uses a fixed member order and fixed deterministic batches. Compute generic bank states once per extraction, bank-conditioned states once per condition, and standalone CASE references once per condition. Store the resulting average conditioning shifts and CASE references with native, generic, and CASE passage states. The cache records row/model/bank hashes, condition keys, bank passages, backbone revision, generic-condition literal, embedding width, batching label, and initial/terminal adapter tensor digests. The source and frozen extraction configuration bind exact prompt templates, EOD handling, precision, and token ceiling. Exact token IDs, attention-mask arrays, and per-member bank states are outside the supplied cache format.

The runner resolves stored outputs as preceding native stages succeed and assigns distinct materialization paths to every binding. The final test CPU EVAL consumes the canonical stored model, test cohort, and row-index inputs. Validation selection runs as a CPU BUILD stage; it reloads each alternative head and independently reproduces its captured validation predictions. It validates the existing baseline prediction identities and metrics through their sealed artifacts.

The `--preflight` command checks settings, configuration schemas, data hashes/cohorts, parent checkpoint identity, and available sealed baseline bindings. It starts zero GPU inference and zero fitting updates. It does not materialize or execute the complete native stage graph. Token coverage, finite-vector checks, bank/head-fit separation, throughput, and peak memory are checked or measured by the corresponding alternative-extraction stages. The supplied review receipt must distinguish offline checks from an actual native end-to-end run.

## Tranche B: matched head training

Each representation receives a bias-free 4,096-to-512 linear map, LeakyReLU with negative slope 0.01, dropout 0.15 during training, and unit normalization. Evaluation disables dropout. Head computation uses float32 on the single declared CPU or GPU device for every arm. The learned output is 512-dimensional. Head parameters remain trainable; the cached Qwen states and reference bank remain fixed.

For each passage pair, cosine similarity predicts the target \(y=(q-1)/4\), where \(q\in[1,5]\) is the released rating and \(y\in[0,1]\) is its rescaled target. Minimize mean squared error. The [derivations](csts-tranche-5-derivations.md) define every forward operation and gradient.

All four head fits use seed 7, byte-identical initial projection weights, the same training row permutations, and the same dropout random stream policy. Reset the head-fitting RNG state before every arm and use the same row-permutation generator seed 107. Record the initial projection digest and common fitting-row digest. Successful terminal state includes the generator and main-process RNG states. Initial RNG hashes and per-epoch permutation hashes are outside the supplied trace. The three learned correction logits start identically at zero.

Use AdamW with learning rate 0.001, moment coefficients 0.9 and 0.999, numerical stabilizer \(10^{-8}\), comparison batch size 32, mean MSE over each actual batch including the final short batch, gradient clipping 1, a constant learning rate, and zero warmup. This head fit processes each batch in one forward/backward pass. Projection weights receive weight decay 0.01. A learned correction logit receives weight decay zero through its own optimizer parameter group. Use the common bank-excluded fitting cohort. Permit at most 48 epochs and five successive validation checks without a strict Spearman improvement. Include epoch zero as a checkpoint candidate; retain the earlier checkpoint on exact ties.

Every candidate reaches this training stage after its feature/input checks. Epoch-zero validation scores are checkpoint candidates. Select each arm's head checkpoint by validation Spearman. Preserve selected weights/logits and validation predictions. Successful terminal state includes the final head, optimizer, RNG, generator, fitting row IDs, epoch, and update count. Traces include epoch losses, validation metrics, correction strengths, elapsed time, selected epoch, actual updates, and stopping cause. Gradient clipping checks finite gradients; per-update gradient-norm logging is outside the supplied trace.

## Tranche C: validation selection

Report D0 and every fitted arm on the full 1,830 comparisons: Spearman, MSE, conditional ordering, confusion counts, false-positive rate, recall, and false-negative rate. Conditional ordering uses comparisons of differing conditions and differing targets for the same source passage pair; ties receive half credit. The common metric artifact also retains the existing diagnostic function's prediction summaries.

Negatives are ratings 1–2; positives are ratings 4–5. All middle ratings between 2 and 4 contribute to regression and ranking metrics. Each system receives its own largest validation cutoff attaining at least 90% positive recall, with inclusive ties. Freeze these cutoffs before test. Include the 0.50 and 0.75 descriptive operating points.

Eligibility requires at least **0.005 Spearman improvement against D0**, condition-ordering accuracy falling by at most **0.01 against D0**, and false-positive rate increasing by at most **0.01 against D0** at the validation recall target. Differences in rates/accuracies are absolute fractions; 0.01 equals one percentage point. The existing validation Spearman therefore requires candidate Spearman at least 0.7875746597420997.

Choose the eligible candidate with the highest validation Spearman. Ties favor lower false-positive rate, higher conditional-ordering accuracy, then fixed order M, B, P, C. If every candidate misses eligibility, retain the existing native model, publish all validation measurements, and stop. Freeze the winner, existing baseline prediction identity, thresholds, checkpoint/cache/bank hashes, and analysis settings in one selection artifact.

Per-row validation predictions are retained for later inspection of ranking repairs and regressions. Detailed condition/rating/length error strata, covariance geometry, reference-alignment plots, and leave-one-bank-member-out stability are possible future diagnostics outside this minimal runnable comparison. They do not affect the present selection rule.

## Tranche D: frozen existing-test comparison

After validation selects an eligible candidate, score that candidate on the existing 2,620 test comparisons and load D0's sealed test predictions. Use their frozen validation-derived thresholds. The benchmark has already been examined in earlier experiments; the report states that history. The baseline's previously reported test Spearman is 0.7885050017660868.

Practical transfer requires a Spearman gain of at least 0.005 against D0, condition-ordering accuracy declining by at most one percentage point, false-positive rate increasing by at most one percentage point, and recall declining by at most one percentage point against D0. Report point differences for Spearman, MSE, false-positive rate, recall, and condition ordering. Report paired confidence intervals for Spearman, MSE, false-positive rate, and recall. Conditional ordering is reported as a point comparison in this implementation.

Use 2,000 paired bootstrap draws over connected source groups, seed 61024. Reuse each sampled group multiset across all systems, recompute rank statistics with average ties, and keep every cutoff fixed. Report valid-draw counts. This stage supplies existing-benchmark test-sample uncertainty for the fixed fitted models.

Retain the existing native deployment model when the candidate misses the transfer rule. Publish complete results for the tested candidate and existing baseline. Spanish JEP measurement remains a separate task; this experiment creates no independently reviewed Spanish passages.

## Implementation plan and execution contract

The supplied implementation is organized as:

| File | Responsibility |
|---|---|
| [matched_baselines.py](../csts_pilot/matched_baselines.py) | Prompt/readout contracts, deterministic bank and fitting cohort, reference construction, four residuals, learned correction strengths, matched projection heads, and native extraction/training stages. |
| [matched_baselines_run.py](../csts_pilot/matched_baselines_run.py) | Settings validation, sealed baseline binding, native stage sequencing, resources, progress, CPU alternative-head verification/selection, conditional test EVAL, fail-closed attempt handling, and asynchronous publication. |
| [csts-tranche-5.json](../configs/csts-tranche-5.json) | Frozen model/data identities, bank rule, fitting schedule, eligibility rules, and compute ceilings. |
| [test_csts_matched_baselines.py](../tests/test_csts_matched_baselines.py) | Independent algebra/gradient checks, token/row alignment, bank isolation, shared initialization/exposure, selection/threshold behavior, and native artifact contracts. |

Implementation sequence: validate settings and identities; bind the existing sealed baseline predictions; seal the bank/common fit rows; extract and seal the contextual states and reference corrections required by the four alternatives; initialize matching alternative heads; fit those four heads through native TRAIN; reproduce selected alternative head predictions and freeze validation metrics/cutoffs in CPU BUILD; conditionally publish existing test inputs, capture the candidate predictions, load the sealed baseline test predictions, and independently evaluate the candidate/baseline comparison through CPU EVAL and a stateless metric worker; assemble the receipt and report.

Run native VIPER BUILD for extraction, validation checks, and cohort publication; TRAIN for head fits; and separate CPU EVAL/stateless metric workers for final test verification. Stateless metrics declare artifact dependencies and numerical comparators. Stored evaluation inputs use distinct materialization paths. An existing attempt directory raises an error; automatic resume and cached-stage recovery are outside the supplied runner. A failed or uncertain attempt is preserved for manual source/settings/artifact-identity reconciliation. Any later implementation of artifact reuse must verify saved stage references and exact payloads before execution.

Flush extraction progress at least every 15 seconds. Flush each completed epoch's training loss, validation metrics, elapsed time, and correction strength. Traces retain the selected epoch. Broadcast completed validation scores when the CPU selection stage verifies all head predictions. The controller summary and event sidecar report native stages, resource counters, failures, and the frozen selection. Native local sealing and metric reporting precede asynchronous cloud promotion. Preserve local source/artifacts until promotion is durable.

Default invocation displays the frozen settings. `--preflight` performs the limited identity/schema checks described above. `--execute` starts native extraction and fitting. Obtain the reviewed `experiment/csts-matched-baselines-20261026` branch before execution so the native source snapshot contains these modules. Commands run from that checkout’s repository root under its declared environment:

```bash
python -m csts_pilot.matched_baselines_run --root .
python -m csts_pilot.matched_baselines_run --root . --preflight
python -m csts_pilot.matched_baselines_run --root . --name initial --execute
```

The delivery of this plan/code does not launch extraction, fitting, or test scoring.

## Resources, review, and follow-up

Allow at most **90 GPU minutes for training/validation extraction**, **10 GPU minutes per alternative head fit** (40 aggregate), **30 GPU minutes for frozen candidate test extraction/scoring**, and **30 CPU minutes for analysis**. Existing baseline predictions require zero new GPU scoring or fitting. These ceilings are proposed execution settings. Resource stops preserve the failed attempt's native diagnostics and last-written artifacts. A head allowance ending within an epoch raises an error; successful terminal optimizer/RNG state is written after completed training. Report extraction token counts, bank/condition counts, passage occurrences, elapsed time, peak CUDA allocation, head fitting rows, completed epochs, and actual updates from their corresponding receipts.

MOA review covers experimental validity, mathematics, data isolation, native VIPER contracts, attempt preservation/publication behavior, and the code/tests. Resolve blocking findings before any launch. Offline checks cover Ruff, Pyrefly, focused tests, numerical gradients, bank/fitting isolation, shared initialization, batch weighting, sealed baseline identity, cutoff/selection behavior, and declared stage-input contracts. Frozen-encoder digests, real tokenizer/EOD/token-ceiling coverage for alternative features, runtime binding materialization, and measured resource use are execution checks. Complete native end-to-end execution remains unperformed in this delivery. Record reviewer findings, fixes, rerun evidence, source hash, and this distinction in the review receipt.

After an eligible construction transfers, a separate matched LoRA continuation can test learning the same representation inside the encoder update. That follow-up must define gradients through current passage/reference branches, current bank/reference recomputation, deterministic reference dropout behavior, equal optimizer/exposure controls, and a measured memory/throughput budget. The present implementation trains frozen-feature heads. Its resource allowance contains zero LoRA optimizer steps.
