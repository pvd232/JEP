# C-STS Conditional Color Clustering

## 1. Status

**Contract status:** Methods accepted by the user; execution uses native VIPER stages. Requirements and three dependent implementation blocks are declared. The cohort, labels and exact encoder checkpoint are frozen. The implementation and sixteen focused fixtures are verified. Native run references, measured results and the diagnostic review pack retain experiment evidence separately from source-review lifecycle records.

| ID | Implementation obligation |
|---|---|
| <nobr><code>COL-REQ-01</code></nobr> | Select every retained color-related comparison from pinned JEP C-STS revision 1.1; preserve original text, splits, connected-caption groups and pair-to-point links. |
| <nobr><code>COL-REQ-02</code></nobr> | Freeze reviewed target-color annotations and spelling aliases before inference; preserve single-color, multiple-color, unspecified and unresolved cases. |
| <nobr><code>COL-REQ-03</code></nobr> | Identify the exact conditional-summary-plus-similarity encoder underlying the recorded approximately 0.865 scorer result and pin every model, tokenizer, adapter and extraction setting. |
| <nobr><code>COL-REQ-04</code></nobr> | Encode the identical point cohort for all three arms using validated caches, final non-padding EOD pooling and finite float32 unit vectors. |
| <nobr><code>COL-REQ-05</code></nobr> | Fit the predeclared K grid and all twenty k-means++ seeds in the original normalized vector space for each arm and analysis cohort. |
| <nobr><code>COL-REQ-06</code></nobr> | Report color agreement, geometric separation, seed stability and original-pair cosine/rating Spearman using fixed selection rules and family-aware paired uncertainty. |
| <nobr><code>COL-REQ-07</code></nobr> | Evaluate a fixed source-derived condition-switch probe with independent target labels and prototypes that exclude the probe's connected-caption family. |
| <nobr><code>COL-REQ-08</code></nobr> | Publish a complete reproducible diagnostic report with source, label, model and configuration identities, all runs, split-specific results and explicit undefined outcomes. |

The [typed contract](csts-color-clustering.toml) owns these requirements and their verifiers. The [checklist workspace](../checklists/csts-color-clustering.toml) places them in three phases. The [experiment settings](../experiments/color-clustering.toml) hold the accepted scientific parameters. Implementation is in `scripts/color_clustering.py`, `scripts/run_color_clustering.py`, `scripts/color_diagnostics.py` and the focused contract fixture module. Source-review lifecycle state remains separate from native experiment run evidence.

## 2. Claim

The analysis will produce a reproducible comparison of conditional color structure in the selected fine-tuned Qwen encoder and two controls, using reviewed target-color labels and a fixed clustering and evaluation policy.

Three research questions remain open until measurement: whether the fine-tuned conditioned vectors align with target colors more strongly than the controls; whether the silhouette-selected K lies near the represented color count; and whether their raw cosine similarities preserve the audited color-pair ratings.

Here, C is the number of distinct reviewed single target-color labels in an analysis cohort; N is the number of unique points in that cohort. K-star is the K with the greatest median cosine silhouette across the twenty seeds. The accepted definition of “near” is an absolute difference from C of at most the larger of one cluster and 25% of C, rounded up. This tolerance is a project choice for review.

Implementation acceptance requires complete, correctly identified evidence. Scientific outcomes may support, weaken or leave these hypotheses unresolved.

## 3. Models

The preparer reads original comparisons, creates unique points and preserves the link from each original sentence side to its vector. Explicit target-binding rules and assistant review of the rules and exception cases assign provisional reference colors before model output is available. The annotation file retains supporting spans for expert review. The encoder and scorer then write the remaining records.

| Record | Exact fields and producer | Consumer |
|---|---|---|
| `pairs.json` | Preparer: `row_id: str`, `split: str`, `group_id: str`, `pair_id: str`, `condition: str`, `sentence1: str`, `sentence2: str`, `rating: float`, `point1_id: str`, `point2_id: str`. | Pair scoring and source accounting. |
| `points.json` | Preparer: `point_id: str`, `condition: str`, `sentence: str`, `group_id: str`, `occurrences: list[{row_id: str, side: str, split: str}]`. | Label review, inference and clustering. |
| `color-labels.json` | Reviewer: `point_id: str`, `target: str`, `color_terms: list[str]`, `color_labels: list[str]`, `shade: Optional[str]`, `status: str`, `evidence_kind: str`, `evidence: list[str]`, `rationale: str`, `reviewer: str`, `reviewed: bool`. | C counting, primary-cohort selection and label agreement. |
| `model-manifest.json` | Resolver: each arm's `base_revision: str`, `adapter_sha256: Optional[str]`, `tokenizer_revision: str`, `extraction_commit: str`, `prompt: str`, `pooling: str`, `max_length: int`, `dtype: str`, `dimension: int`, `checkpoint_source_run: str`, `artifact_paths: list[str]`. | Encoder loading and cache validation. |
| `embeddings/<arm>.npz` | Encoder: ordered `point_ids: str[N]`, `vectors: float32[N,4096]`; sidecar records input and model-manifest hashes. | Clustering, pair scoring and the condition-switch probe. |
| `clusters/<cohort>/<arm>/<K>/<seed>.npz` | Clusterer: `point_ids`, `assignments: int[N]`, `centroids: float32[K,4096]`; sidecar records `inertia: float`, `iterations: int`, `converged: bool` and configuration hashes. | Metrics and reproducibility checks. |
| `metrics.json` | Evaluator: per-run scores, denominators, undefined reasons, paired comparisons, resampling seed, selected K and switch coverage. | Report generation and independent recomputation. |

The main arm is the encoder after conditional summarization pretraining and similarity training that supplied vectors to the recorded approximately 0.865 comparison system. Its learned pairwise comparator is a separate artifact. The resolved checkpoint is `proposition_final.pt`, SHA-256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`. The 0.865230 result averages three learned-comparator fits on this single frozen encoder; its archived raw-cosine test Spearman is 0.863398.

## 4. Execution

1. **Freeze the source and color filter.** Reconstruct revision 1.1 from the pinned upstream CSVs and verify its export hashes. Use JEP commit `5dde4314e90f92eb4ac84b122e3b312402b18931`. Review every unique condition for color-related meaning; color/colour, hue and shade terms identify initial candidates. Save every inclusion decision and reason. Include all retained matching rows in training, validation and test.
2. **Create points and annotations.** Embed each original condition/sentence separately. Deduplicate exact text tuples, using SHA-256 of their compact UTF-8 JSON array; retain all source occurrences. Preserve original text bytes in prompts. Annotate the color of the named target and its evidence. Merge spelling variants such as grey/gray. Store light/dark modifiers separately from a base term such as blue. Keep named shades such as navy, tan and beige distinct. An implied label requires an explicit rationale; ambiguous inferences remain unresolved. Freeze the reviewed annotations and the alias table before inference.
3. **Resolve and encode the three arms.** Use the archived main encoder; its pretrained backbone with the same conditioned prompt; and the main encoder with a generic similarity instruction omitting the condition. Reuse the existing `passage_keys`, `encoder_settings`, `encode` and cache-validation behavior where the verified checkpoint implementation permits it. Pool the last non-padding EOD token and normalize in float32. Load the archived maximum-length policy; record and reject overlength inputs before inference. Run inference with evaluation mode, gradients disabled and fixed weights. Reuse a cache only after its complete identity matches.
4. **Run the K sweep.** Primary analysis uses validation points with one reviewed target color. Repeat for training, test and pooled points as descriptive analyses. Run a second full-cohort diagnostic that retains multiple-color, unspecified and unresolved points and scores ARI only on the resolved single-color subset. For each cohort, sweep every integer K from 2 through `min(2*C,N-1)`, retaining K=C when supported. Use twenty explicit seeds 0–19, `n_init=1`, `max_iter=500`, `tol=1e-4`, Lloyd updates and k-means++ initialization. Fit in the normalized 4096-dimensional space. Unsupported K values and cohorts with fewer than two represented colors receive an explicit reason. Use the same comparable K values across arms.
5. **Score geometry and pair similarity.** Primary label agreement is ARI at K=C. Report all per-seed scores and their median and interquartile range; use the lowest-inertia seed for a representative cluster table. Select K-star using median cosine silhouette and the declared tie rule. Report inertia, cluster sizes, color contingency tables and pairwise ARI between seed assignments. Reconnect the original color pairs and compute raw-cosine Spearman against all their audited ratings. Include explicit and implied slices and target/color frequencies with denominators.
6. **Compare arms with paired resampling.** Resample the existing `group_id` components 1,000 times with seed 20261104, using identical sampled groups across arms. Components link captions reused by any pair or condition. Repeated sampled components contribute repeated observations. Recompute median-over-seed ARI differences at K=C and cosine/rating Spearman differences; retain a 95% percentile interval. These intervals rescore the fitted clusterings. Report initialization variability separately. Record undefined resamples and return no interval when fewer than 950 resamples are valid. Comparisons use identical point and pair cohorts.
7. **Evaluate condition switching.** Before inference, freeze up to fifty hash-ordered source sentences with two differently colored, explicitly identified objects. Keep the sentence unchanged and supply one color condition for each object; record any added alternative condition. Construct a unit prototype for each color from the normalized mean of other single-color vectors, excluding the entire probe family and requiring at least five other families per color. For each direction, measure cosine to the requested-color prototype minus cosine to the other-color prototype. Report the mean of the two directional margins and the fraction with both margins positive. The unconditioned arm supplies the same vector in both directions, giving a bidirectional mean margin of zero. Coverage shortfalls remain visible.
8. **Retain and explain the result.** Publish every run and failure, the fixed-K comparisons, the full K curves, color/cluster contingency tables and representative nearest neighbors. Plot one point per K with seed variability. A 2-D projection may be added for inspection; numerical scores use the retained full-dimensional vectors. A favorable interpretation considers label agreement, direct pair similarity and condition-switch behavior together; K proximity receives its own finding.

All split-wise and pooled analyses in this first run are exploratory. Validation is the primary reporting cohort. Training results describe fitted-data behavior; test results provide a separate descriptive check. Protocol completion never depends on a favorable research result.

### Native VIPER and visual review

The embedding, clustering and reporting operations run as native VIPER stages with frozen inputs and managed artifact references. The driver verifies the resulting runs. The review pack retains K curves, seed dispersion and stability, convergence, silhouette distributions, cluster sizes, color-agreement heatmaps, centroid distances, PCA projections with explained variance, nearest-neighbor and exemplar tables, original-pair plots, condition-switch results and paired intervals. PNG, SVG and a multipage PDF share one visualization index. The HTML index filters plots for review; tables retain the underlying values and every seeded assignment.

## 5. Persisted evidence

Native VIPER stores the stage artifacts under its managed experiment directories. The driver collects the user review artifacts and run references under `color_results/run-20261104/`. A lightweight source report may be published under `training_outputs/color_clustering/`. Writers hash each input and output and retain the exact software revision and command. Existing model and dataset artifacts remain inputs.

| Artifact | Evidence retained |
|---|---|
| `cohort-manifest.json`, `condition-filter.json`, `pairs.json`, `points.json` | Source/export hashes, every filter decision, split and component counts, exact input IDs and original pair links. |
| `color-labels.json`, `color-aliases.json`, `label-review.md` | Frozen labels, source evidence, rationale, reviewer identity and unresolved cases. |
| `experiment.toml`, `model-manifest.json`, `environment.json` | Accepted settings, actual checkpoint and tokenizer identities, pooling and token policy, dependency versions, hardware, device/dtype and thread settings. |
| `embeddings/`, `clusters/`, `metrics.json`, `switch-probe.json` | Reusable vectors, every clustering, full score tables, paired intervals and condition-switch definitions and coverage. |
| `report.md`, `figures/`, `run-receipt.json` | Interpretations linked to measured values; command, job ID, exit state and complete artifact hashes. |

Local artifact persistence and verified local runs satisfy experiment completion. Cloud replication runs as a separate durable asynchronous job with a retained queue and upload receipt; upload progress and retries do not gate completion or user review.

The report generator consumes these records directly. A report repair reuses successful embeddings and cluster fits.

## 6. Verification

The typed [verifier declarations](csts-color-clustering.toml) retain the exact conditions, success tests and targeted rejections. One focused, table-driven test module will exercise these boundaries; real-data preflight will verify input and model identities.

| Rule | Executable condition |
|---|---|
| <nobr><code>COL-VR-01</code></nobr> | Planned `scripts/color_clustering.py:prepare_cohort`; `tests/test_color_clustering.py:test_cohort_preserves_rows_points_and_splits` and `test_cohort_rejects_source_or_membership_mismatch`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-02</code></nobr> | Planned `scripts/color_clustering.py:validate_labels`; `tests/test_color_clustering.py:test_labels_resolve_the_named_target` and `test_labels_reject_missing_or_conflicting_evidence`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-03</code></nobr> | Planned `scripts/color_clustering.py:resolve_encoder`; `tests/test_color_clustering.py:test_encoder_matches_the_archived_run` and `test_encoder_rejects_checkpoint_substitution`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-04</code></nobr> | Planned `scripts/color_clustering.py:encode_inputs`; `tests/test_color_clustering.py:test_embeddings_preserve_arm_and_input_identity` and `test_embeddings_reject_stale_or_invalid_vectors`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-05</code></nobr> | Planned `scripts/color_clustering.py:fit_sweep`; `tests/test_color_clustering.py:test_sweep_covers_each_supported_k_and_seed` and `test_sweep_rejects_missing_or_changed_settings`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-06</code></nobr> | Planned `scripts/color_clustering.py:score_sweep`; `tests/test_color_clustering.py:test_scores_follow_fixed_selection_and_pair_links` and `test_scores_reject_label_selected_k_or_broken_pairs`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-07</code></nobr> | Planned `scripts/color_clustering.py:score_condition_switch`; `tests/test_color_clustering.py:test_switch_scores_follow_target_changes` and `test_switch_rejects_overlapping_prototypes`; reject with `ValueError` and the declared message predicate. |
| <nobr><code>COL-VR-08</code></nobr> | Planned `scripts/color_clustering.py:write_report`; `tests/test_color_clustering.py:test_report_accounts_for_all_inputs_and_results` and `test_report_rejects_omissions_or_outcome_gates`; reject with `ValueError` and the declared message predicate. |

The methods document is accepted through review. Scientific labels must be frozen before model inspection. Source-plan gates must pass before execution. A missing model identity or unresolved source hash blocks inference at its named preflight boundary.

## 7. Propagation

| Surface | Required change |
|---|---|
| Dataset revision 1.1 | Read the pinned reconstruction outputs and retain their hashes. |
| Existing encoder extraction and caches | Reuse the verified representation and matching cache records. |
| `scripts/color_clustering.py` | Proposed analysis command owning cohort preparation, annotation checks, cached inference, clustering, scoring and reporting. |
| `tests/test_color_clustering.py` | Proposed focused fixtures for identity, target binding, vector validity, sweep coverage and score joins. |
| Contract and checklist declarations | Register the accepted requirements and dependent blocks; bind plans to the chosen implementation checkout and its actual runtime. |
| Existing shared worktrees | Preserve all pre-existing changes; the draft validation uses temporary new declaration files and removes them afterwards. |

The current workspace binding records the inspected local checkout and a compatible Python runtime used for declaration validation. The execution workspace will bind the selected JEP checkout and its own verified runtime. That operational binding is finalized with the first source plan.

## 8. Acceptance case

### Success

An illustrative comparison contains “A person wears a red shirt and blue trousers” under “color of shirt.” The preparer creates a point with the original sentence and condition, plus a pair/side link. The reviewer records target “shirt,” color “red,” the supporting “red shirt” span and an explicit evidence kind. The encoder produces one validated unit vector per arm. The clusterer writes all supported K/seed results. The scorer joins that point to the red reference label and its original pair rating. Repeated appearances of the exact input reuse the vector while retaining each original pair link.

The alternate “color of trousers” condition labels the same sentence blue in the frozen switch probe. Its prototypes exclude the sentence's connected-caption component.

### Rejection

A cache produced from another LoRA checkpoint has the right dimensions but a different adapter digest. Proposed `encode_inputs` raises `ValueError` containing `embedding cache: identity mismatch` under `COL-VR-04` before clustering. A target-color label based only on an unrelated object's color is sent back to label review under `COL-VR-02`. A report omitting an unfavorable supported seed fails `COL-VR-08`.

## 9. Implementation order

1. Apply the accepted color policy: distinct named colors, with modifiers stored separately.
2. Complete `COL-PB-01`: prepare the data/label review and resolve the archived encoder artifacts. Review the frozen input inventories before inference.
3. Create the current source-backed `PairBlockPlan` over the inspected implementation baseline; reuse the owning project's environment and focused checks.
4. Complete `COL-PB-02`: implement and verify the analysis on small fixtures and validated cache slices.
5. Complete `COL-PB-03`: run GPU inference and CPU analysis on the existing suitable JEP worker, using durable job records. Verify live worker state and preserve existing jobs.
6. Review the full result and its condition-specific failure examples before choosing a follow-up experiment.

## 10. Master checklist

The [checklist](../checklists/csts-color-clustering.md) is generated from the registered typed package and workspace. Its phases cover data/model freeze, implementation, and execution/reporting. Declaration-validation evidence is retained in `declaration-validation.json`; it establishes schema and dependency consistency. Experiment gates and scientific measurements remain future evidence.

## 11. Contract-owned PairBlocks

The generated region owns the current block states and requirement links. The operational plan is [the native execution plan](../plans/csts-color-clustering-run.md). Native stage references and observed results are retained separately from source-review lifecycle receipts.

<!-- contract-protocol:generated:start -->
**In progress.** [Jump to current PairBlock](#col-pb-01)

**Checklist:** [C-STS Color Clustering](../checklists/csts-color-clustering.md)

### PairBlocks

<a id="col-pb-01"></a>

#### <nobr><code>COL-PB-01</code></nobr>

**Status:** drafting

**Requirement contribution:** Prepare the audited cohort, review target colors and resolve the archived encoder identity.

**Plan:** None

**Current receipt:** None

**Dependencies:** None

**Next action:** Run the current PairBlock plan.

<a id="col-pb-02"></a>

#### <nobr><code>COL-PB-02</code></nobr>

**Status:** waiting

**Requirement contribution:** Reuse the encoder extraction path and implement the cached clustering and scoring analysis.

**Plan:** None

**Current receipt:** None

**Dependencies:** <nobr><code>COL-PB-01</code></nobr>

**Next action:** Wait for the declared dependencies.

<a id="col-pb-03"></a>

#### <nobr><code>COL-PB-03</code></nobr>

**Status:** waiting

**Requirement contribution:** Run the frozen analysis and publish its complete evidence and interpretation.

**Plan:** None

**Current receipt:** None

**Dependencies:** <nobr><code>COL-PB-02</code></nobr>

**Next action:** Wait for the declared dependencies.


### Requirements

| Requirement | Claim | Progress | Verifiers | PairBlocks |
|---|---|---|---|---|
| <nobr><code>COL-REQ-01</code></nobr> | Select every retained color-related comparison from pinned JEP C-STS revision 1.1; preserve original text, splits, connected-caption groups and pair-to-point links. | in_progress | <nobr><code>COL-VR-01</code></nobr> | <nobr><code>COL-PB-01</code></nobr> |
| <nobr><code>COL-REQ-02</code></nobr> | Freeze reviewed target-color annotations and spelling aliases before inference; preserve single-color, multiple-color, unspecified and unresolved cases. | in_progress | <nobr><code>COL-VR-02</code></nobr> | <nobr><code>COL-PB-01</code></nobr> |
| <nobr><code>COL-REQ-03</code></nobr> | Identify the exact conditional-summary-plus-similarity encoder underlying the recorded approximately 0.865 scorer result and pin every model, tokenizer, adapter and extraction setting. | in_progress | <nobr><code>COL-VR-03</code></nobr> | <nobr><code>COL-PB-01</code></nobr> |
| <nobr><code>COL-REQ-04</code></nobr> | Encode the identical point cohort for all three arms using validated caches, final non-padding EOD pooling and finite float32 unit vectors. | planned | <nobr><code>COL-VR-04</code></nobr> | <nobr><code>COL-PB-02</code></nobr> |
| <nobr><code>COL-REQ-05</code></nobr> | Fit the predeclared K grid and all twenty k-means++ seeds in the original normalized vector space for each arm and analysis cohort. | planned | <nobr><code>COL-VR-05</code></nobr> | <nobr><code>COL-PB-02</code></nobr> |
| <nobr><code>COL-REQ-06</code></nobr> | Report color agreement, geometric separation, seed stability and original-pair cosine/rating Spearman using fixed selection rules and family-aware paired uncertainty. | planned | <nobr><code>COL-VR-06</code></nobr> | <nobr><code>COL-PB-02</code></nobr> |
| <nobr><code>COL-REQ-07</code></nobr> | Evaluate a fixed source-derived condition-switch probe with independent target labels and prototypes that exclude the probe's connected-caption family. | planned | <nobr><code>COL-VR-07</code></nobr> | <nobr><code>COL-PB-02</code></nobr> |
| <nobr><code>COL-REQ-08</code></nobr> | Execute embedding, clustering and reporting as native VIPER stages and publish a complete reproducible visual diagnostic report with source, label, model and configuration identities, all runs, split-specific results and explicit undefined outcomes. | planned | <nobr><code>COL-VR-08</code></nobr> | <nobr><code>COL-PB-03</code></nobr> |

### Verification rules

| Rule | Requirements | Acceptance conditions | Success case | Rejection cases |
|---|---|---|---|---|
| <nobr><code>COL-VR-01</code></nobr> | <nobr><code>COL-REQ-01</code></nobr> | All unique conditions receive an inclusion decision before embeddings are inspected.<br>Exact duplicate condition/sentence inputs share one point and retain every source occurrence.<br>Changed source hashes or a selected excluded row raise ValueError containing 'color cohort: source mismatch'. | [test_cohort_preserves_rows_points_and_splits](../tests/test_color_clustering.py) | [test_cohort_rejects_source_or_membership_mismatch](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-02</code></nobr> | <nobr><code>COL-REQ-02</code></nobr> | Each reviewed label records the condition target, supporting text, evidence kind, color set and reviewer.<br>Primary color-label agreement uses resolved points with exactly one target color; other points remain in the full-cohort diagnostic.<br>A resolved label lacking supporting text or containing an unresolved target raises ValueError containing 'color label: missing target evidence'. | [test_labels_resolve_the_named_target](../tests/test_color_clustering.py) | [test_labels_reject_missing_or_conflicting_evidence](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-03</code></nobr> | <nobr><code>COL-REQ-03</code></nobr> | The checkpoint digest and extraction configuration resolve to the archived main-encoder run; the pairwise comparator is identified separately.<br>The two controls use the same base revision and tokenizer as the main encoder.<br>A different adapter or unpinned representation raises ValueError containing 'encoder identity: checkpoint mismatch'. | [test_encoder_matches_the_archived_run](../tests/test_color_clustering.py) | [test_encoder_rejects_checkpoint_substitution](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-04</code></nobr> | <nobr><code>COL-REQ-04</code></nobr> | Cache identity includes exact input bytes, arm, base and adapter digests, tokenizer, prompt, pooling and token policy.<br>Each arm produces a 4096-dimensional vector per point; norms differ from one by at most 2e-5.<br>Stale cache identity, invalid vectors or an omitted point raise ValueError containing 'embedding cache: identity mismatch'. | [test_embeddings_preserve_arm_and_input_identity](../tests/test_color_clustering.py) | [test_embeddings_reject_stale_or_invalid_vectors](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-05</code></nobr> | <nobr><code>COL-REQ-05</code></nobr> | Each supported K and seed is retained with assignments, centroids, inertia, iterations and convergence status.<br>K-means uses Lloyd updates, n_init=1, max_iter=500, tol=1e-4 and seeds 0 through 19.<br>A missing supported run or changed setting raises ValueError containing 'kmeans sweep: incomplete grid'. | [test_sweep_covers_each_supported_k_and_seed](../tests/test_color_clustering.py) | [test_sweep_rejects_missing_or_changed_settings](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-06</code></nobr> | <nobr><code>COL-REQ-06</code></nobr> | Primary ARI is evaluated at K=C; K-star maximizes median cosine silhouette across seeds, with ties within 1e-6 resolved toward smaller K.<br>Original color-pair Spearman uses all retained selected pairs, including multiple-color and unspecified cases.<br>Ground-truth ARI used to select K-star or a missing original pair raises ValueError containing 'metric policy: unsupported selection'. | [test_scores_follow_fixed_selection_and_pair_links](../tests/test_color_clustering.py) | [test_scores_reject_label_selected_k_or_broken_pairs](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-07</code></nobr> | <nobr><code>COL-REQ-07</code></nobr> | At most fifty hash-ordered sentences with two explicitly named, differently colored objects enter the frozen probe.<br>Both condition directions use the same text and prototypes estimated from at least five other caption families per color.<br>A prototype containing the probe family raises ValueError containing 'condition switch: prototype overlap'; insufficient coverage yields an explicit undefined result. | [test_switch_scores_follow_target_changes](../tests/test_color_clustering.py) | [test_switch_rejects_overlapping_prototypes](../tests/test_color_clustering.py) |
| <nobr><code>COL-VR-08</code></nobr> | <nobr><code>COL-REQ-08</code></nobr> | The report contains every arm, cohort, K and seed, including failures and undefined metrics with reasons.<br>Artifact hashes and runtime versions permit metrics to be recomputed from retained vectors and annotations.<br>Verified local evidence satisfies completion; cloud replication uses an independent durable outbox and upload receipt and never gates review delivery.<br>Missing evidence or a requirement that clustering favor the hypothesis raises ValueError containing 'report: incomplete evidence'. | [test_report_accounts_for_all_inputs_and_results](../tests/test_color_clustering.py) | [test_report_rejects_omissions_or_outcome_gates](../tests/test_color_clustering.py) |
<!-- contract-protocol:generated:end -->

## 12. ContractTarget

The future source plan will use the shared `add`, `replace`, `patch` and `remove` file actions. Each implementation target must map to its owning requirement and a focused observing verifier. Candidate materialization and gates use the shared protocol runner; this contract adds no lifecycle runner or local contract schema.

## Sources

- [JEP C-STS revision 1.1](https://github.com/pvd232/JEP/tree/5dde4314e90f92eb4ac84b122e3b312402b18931/datasets/csts-jep-revision-v1-1): retained rows, reconstruction and provenance.
- [Caption-component partition implementation](https://github.com/pvd232/JEP/blob/5dde4314e90f92eb4ac84b122e3b312402b18931/datasets/csts-jep-revision-v1-1/source_partition.py): canonical-caption groups and split separation.
- [Inspected encoder extraction](https://github.com/pvd232/JEP/blob/3a840ac90ee52db525b53b8f876abf042e319e0a/csts_pilot/baseline_models.py): conditioned prompt, EOD pooling, input deduplication and unit-vector cache checks. This inspected implementation informs reuse; the archived winning checkpoint remains to be resolved.
- [KMeans documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html): initialization and solver settings.
- [Clustering evaluation documentation](https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation): ARI and silhouette.
- [Contract-package protocol](https://github.com/pvd232/agents/blob/b963085bdb098cc13443d29ee47ced50de3378b3/contracts/contract-package.md): declaration, workspace, compilation and rendering ownership.
