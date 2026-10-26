# Tranche 5 — MOA code review

**Final verdict: Approve for delivery of the experiment plan and code.** No unresolved P0–P2 finding remains in the reviewed scope. The final source manifest matches the passed implementation-validation receipt. The complete native experiment has not executed; this verdict does not assert measured model performance, GPU extraction coverage, or successful native end-to-end execution.

## Review method and scope

This review used the user's Multi-Agent Orchestration workflow from `/Users/machina/Developer/ChatGPT/moa/introduction-to-multi-agent-orchestration.md`, together with `/Users/machina/.agents/skills/code-review/SKILL.md` and its literature reference. The local MOA directory supplies an orchestration workflow; it supplies no `moa` executable. Two actual independent review agents performed bounded work with separate outputs:

| Agent | Responsibility | Output |
|---|---|---|
| `/root/moa_review` | Mathematics, optimization, statistical selection, test observers, source-review synthesis | This report; `csts-tranche-5-moa-math-checks.json` |
| `/root/moa_review/runtime_review` | Native VIPER stage contracts, artifact bindings, recovery behavior, execution/publication boundaries | `csts-tranche-5-runtime-review.md` |

Both agents inherited the session's model configuration. The tool interface did not expose a separately verifiable model identifier, so this receipt makes no claim of a multi-model panel. The experiment authors repaired findings; reviewers inspected the repairs. Mechanical checks supplement the source reviews.

The review covers all seven files in the manifest below. Relevant existing helpers were inspected for EOD readout/batching, rating diagnostics, recall thresholds, paired bootstrap, early stopping, and native stage/artifact integration. The separate runtime report records its exact operational boundary.

## Reviewed snapshot

| File | SHA-256 |
|---|---|
| `csts_pilot/matched_baselines.py` | `9a89e28bea4f9dff98b8b760931c12babb94c794b27d80cab7175db425f0669a` |
| `csts_pilot/matched_baselines_run.py` | `1e71195a4cc0c034a7bc592112534f5483be02b1af8590ac5ce1dfc47607c65c` |
| `configs/csts-tranche-5.json` | `c492c508e7fb63a199b3e927461d954d4d939fecb2d578dbaa6e245f4153f07c` |
| `tests/test_csts_matched_baselines.py` | `2f9f52eeb5af224ebe75ea28269a3aa29985cea7e19cab9b87c4554976e0ede9` |
| `plans/csts-tranche-5-matched-baselines.md` | `5582db5136accc41002cfd772f8405e4a3b935efd44eb05419981d5b744ba387` |
| `plans/csts-tranche-5-derivations.md` | `a7b58e0e3417ce09a20bce7d613acd66f335037c1c73396b04bfcdbd9584c492` |
| `scripts/check_tranche5_math.py` | `07447aed9c4421214be64008c71a84a7b40a1f9194cdf5f7e0795cbc39de343e` |

The manifest excludes this report and the other review receipts to avoid a self-referential hash. A later content change requires a hash refresh and review of the changed lines.

## User-directed execution scope

The final runner fits **four alternative heads**: same-passage subtraction, population translation, population projection removal, and CASE-style residual. Its configuration lists only those four arms. Its training function explicitly rejects a native-head fit. Existing sealed native validation/test predictions supply the sole comparator. The runner performs no baseline scoring or baseline reproduction stage.

Cheap checks bind archived predictions to the complete original comparison identities and preserve their SHA-256. Candidate contextual states are extracted where the four alternatives require them. The default command prints configuration; `--preflight` performs identity/schema checks; `--execute` explicitly starts native execution. This delivery ran no experiment, new Qwen inference, or LoRA continuation.

The comparison measures candidate-pipeline improvement against the existing native pipeline. Candidate head capacity contributes to that intervention. A score gain would not isolate reference subtraction as its cause. The plan and derivations state this scope. Earlier review requirements for a newly trained native head and repeated native-score reproduction were withdrawn following the user's explicit scope change.

## Findings and verified repairs

| Priority | Concrete failure in the earlier candidate | Repair and observer |
|---|---|---|
| P1 | Selection consumed fitting-row count/hash fields that the head trace did not emit; a completed fit could fail during selection. | The terminal trace now emits both fields. The four-head CPU integration test fits, restores selected weights, and runs `freeze_selection`. |
| P1 | A cache could retain valid shapes, counts, and hashes while an in-range occurrence-index permutation attached states to the wrong sentence/condition. | `validate_cache_rows` checks both semantic keys for every comparison. A test permutes valid indices and requires rejection. |
| P1 | Progress emission used the previous tranche's sidecar variable, so expected live events could miss the Tranche 5 event file. | The local emitter flushes stdout and `CSTS_TRANCHE5_EVENTS`; the test observes both and verifies that NaN input changes neither artifact. |
| P2 | Precomputing the projection component outside the residual operator left its documented raw/reference differentiation outside that operator's derivative observer. Frozen-feature head/logit fitting itself had the same forward formula. | The cache supplies the bank direction and the residual operator computes the component internally. Autograd tests check both raw and reference Jacobians. An orthogonal input retains its raw vector. |
| P1 | Stored artifacts sharing a materialization path could collide in a native stage. | Every binding receives its own `inputs/<binding>` path; runtime review checked the final producer/consumer graph. |
| P1 | A bare runner invocation could launch extraction/fitting despite the delivery's review-first execution contract. | A bare invocation displays settings; execution requires `--execute`. The main training loop contains only the four alternatives. |
| P2 | The documentation promised token arrays, individual bank shifts, stability/geometry diagnostics, automatic recovery, and broader preflight/uncertainty coverage than the code supplied. | The plan/derivations distinguish implemented caches/traces/checks from future diagnostics and manual recovery. Conditional ordering remains a point guard; intervals cover Spearman, MSE, FPR, and recall. |
| P2 | An enclosing native-worker autocast context could lower head precision despite the specified float32 head contract. | `CorrectedHead.forward` disables enclosing autocast while preserving its declared tensor dtype. Four arm-specific CPU BF16 outer-autocast observers require exact float32 output agreement and finite float32 gradients; float64 gradient observers remain supported. |
| P2 | Optimization derivation omitted the implemented global clipping and could imply decay on the correction logit. | The derivation includes the joint norm, bound 1, stabilizer 1e-6, and clipped-gradient AdamW moments. The implementation gives projection weights decay 0.01 and the logit decay zero. |
| P2 | Archived validation prediction identity was checked after fitting, wasting work if the stored cohort was wrong. | The runner checks the full archived cohort before any inference and before the preflight return. No baseline forward pass is used. |
| P2 | The test report omitted the promised MSE point difference and explicit archived prediction checksum. | It now reports the MSE difference and archived native-test SHA; validation selection and test-capture timing retain archive checksums. |

No remaining source-review defect is being waived on the strength of passing tests.

## Numerical and statistical review

The residual formulas preserve raw readout lengths before correction. Population projection computes the rank-one component without a dense 4096-by-4096 projector. The sigmoid chain, reference-side projection derivative, normalization Jacobian, shared two-passage head gradient, inverted dropout, actual-batch mean MSE, and clipped AdamW update agree with the derivations.

All four fits reserve the same bank source groups, reset identical head/RNG initialization, and share the comparison permutation policy. The bank uses training passages and no rating-driven selection. The selected LoRA checkpoint previously trained on the original training partition; new bank exclusion applies to the new head fits. Epoch zero is eligible, strict validation Spearman improvements replace selected weights, and ties retain the earlier checkpoint. Saved selected weights are reloaded before frozen selection.

Eligibility uses the sealed native comparator, a 0.005 Spearman gain, at most a 0.01 loss in conditional ordering, and at most a 0.01 increase in false-positive rate at each system's validation-derived recall cutoff. Cutoffs include ties and remain fixed for existing-test evaluation. Source-group bootstrap draws reuse the same group multiset across compared systems, report valid counts, and require at least 95% valid draws for each implemented metric. Existing-test history and the single fixed training seed are explicit. Bootstrap intervals describe benchmark sampling uncertainty for these fitted pipelines.

## Executed mathematical checks

The coordinator independently evaluated 14 NumPy float64 observers: projector symmetry/idempotence/scale invariance, orthogonality, raw/reference projection Jacobians, corrected residual Jacobians, unit-normalization Jacobian and radial nullspace, cosine-MSE gradient, sigmoid derivative, paired covariance, and paired mean identities. All passed; maximum absolute error was **2.487232642067738e-10**, against tolerance **2e-8**. Results are in `csts-tranche-5-moa-math-checks.json`.

The coordinator also read and reran the supplied `scripts/check_tranche5_math.py`. Its **24 checks**, including **19 finite-difference gradient checks**, passed. Maximum gradient error was **2.63425571429192e-10**, against tolerance **1e-7**. The script includes a small identity-head algebra case; that auxiliary calculation launches no native-head experiment. The author-owned math receipt separately binds the derivation/script hashes and rendering checks.

The production test file independently checks all residual operators, head/logit finite differences, raw/reference Jacobians, normalization, bank disjointness, semantic cache joins, deterministic selection/ties, correct event sidecar behavior, and four small CPU head fits through selected-state restoration and selection. The integration fixture supplies archived baseline predictions deliberately unrelated to cache-derived native cosine and verifies that those exact saved values survive selection.

## Mechanical validation and execution limits

The final [implementation-validation receipt](csts-tranche-5-verification.json) was inspected and its seven file hashes were checked against the current files. In the owner's declared runtime, `/home/machina/jep-format-env/bin/python`, the final gate passed:

- `python -m pytest -q tests/test_csts_matched_baselines.py`: **43 passed in 8.56 seconds**.
- Ruff checks and formatting: **passed for all four Python files**.
- Pyrefly basic checks: **zero errors in the two production modules**.
- Supplied independent mathematics: **24 checks passed**, including 19 gradient checks.
- Preflight: archived validation identity and configured inputs passed; **zero benchmark inference and zero benchmark fitting**. Archived validation predictions SHA-256: `f82e66b853940ac44b316fb1325e12c6d4d09b1ac7f86c67b76a7177611d6bd0`.
- Owner browser-rendering receipt: **273 math expressions, zero KaTeX parse errors**, with browser-rendered MathML preview and focused visual inspection. No single-dollar delimiters are used.

The coordinator reviewed the final autocast change and its four additional regression cases. AST comparison confirmed that the remaining runner/script formatter changes preserved their semantics. Source-review judgment and the independent runtime review remain separate from these mechanical gates.

The following remain execution-time checks: real pinned-tokenizer/EOD/token-ceiling coverage, frozen-adapter digests over real Qwen extraction, GPU numerical behavior and memory/throughput, native stored-input materialization, full native TRAIN/EVAL/metric-worker execution, and durable asynchronous cloud promotion. No new model score or experimental outcome is claimed in this review. Automatic resume, per-member bank stability, detailed norm/geometry reports, and a future in-training LoRA intervention remain outside the supplied runner.
