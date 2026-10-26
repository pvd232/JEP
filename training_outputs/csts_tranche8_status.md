# Checked proposition answers and LoRA — live status

**Revised policy passed the fresh audit: 58/60 faithful decisions (96.7%), zero observed severe unsupported assertions. Full generation and one answer-input LoRA run are authorized by the predeclared fidelity screen.**

| Development audit | Faithful decisions | Severe unsupported assertions | Gate |
|---|---:|---:|---|
| Original cached spans, same initial sources | 73/120 (60.8%) | 2 | Descriptive comparator |
| Generated propositions, initial policy | 115/120 (95.8%) | 1 | Failed: hobby inferred from one activity |
| Generated propositions, revised frozen policy; fresh disjoint groups | 58/60 (96.7%) | 0 | Passed: at least 57/60 and zero severe |

The single permitted revision prohibits inferring a hobby, habit or intent from one action and retains known counts alongside uncounted groups. The two remaining fresh-sample errors are conservative abstentions: mounted athletes support a broad equestrian category, and an unspecified bicycle trick still supports that broad category. These were retained as failures; no prompt or criterion was adjusted after this audit.

Each audit used source-sampled groups and two independent model reviewers. Each reviewer saw at most one passage from a source group and saved source-only references before reviewing candidates. Reviewers saw no ratings or companion passages. The initial old/new candidates were randomly labeled A/B; fresh candidates used the opaque label P. This is a model-assisted development check, not human expert validation or a guarantee of population fidelity. Exact quotations are checked separately from semantic fidelity.

The generation policy is now frozen to `gpt-6.1-sol`, requested reasoning `high`, prompt SHA-256 `6895d17242704944632757d7c5eb669f3d4d8f959ee23bbdd7ddae00a0f0304e`. Missing or ambiguous answers fall back to the original passage and condition. The complete target is 17,334 unique training/validation passage-condition inputs, retaining all 6,980 training and 1,830 validation comparisons. Full generation is running under a durable supervisor with four concurrent requests. The last inspected count is 640/17,334 inputs (10 closed batches), with no failed attempts. Request latency varies substantially, so there is no reliable finish estimate yet. Closed raw batches are checkpointed natively. The isolated native workspace is deployed; owner Ruff/Pyrefly/focused-test checks are running before the sampled frozen-Qwen comparison and training. Adapter fitting has not started.

One weights-only warm start from the saved Qwen adapter will use fresh optimizer/RNG state. A frozen-cosine improvement is not a prerequisite for training. The original saved Qwen comparator remains validation Spearman **0.782575**. No baseline rerun or additional native control head is planned. Test inputs remain unopened until a validation candidate meets all predeclared rank, false-positive and condition-order guards.

Audit records, source-only references, blinded judgments, failures and the hash-bound gate are preserved in [proposition_audit](proposition_audit/). The native runs preserve checkpoints, input identities, epoch traces and asynchronous publication receipts. Runtime failures are retained separately from statistical results.
