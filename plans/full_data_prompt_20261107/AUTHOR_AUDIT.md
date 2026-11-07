# Author audit — not an independent review

**Verdict: DRAFT / not approved for GPU execution.** Ten independent reviews: 0/10.

Scope: new protocol manifest, exact prompt registry, native VIPER graph builders, optional prompt-template extension, CPU tests, and their original `fit_lora`/`fit_neural`/resume/scoring callees. No training was started. No model, production dataset or credential was copied into this review packet.

## Changes made during this author audit

| Finding | Severity | Repair or disposition |
|---|---|---|
| Old five-epoch subset and optimizer reset do not belong in a standalone full-data experiment. | P1 design | Removed. Every new fit starts from fresh base+LoRA on all 6,051 examples, with one continuous optimizer. |
| CASE-style C changes instruction wording and target/context role, not just input order. | P1 interpretation | Arm names and contrast descriptions distinguish order-only B from CASE-inspired C; no claim of exact CASE replication or pure role effect. |
| A process-global prompt string can contaminate concurrent arms and fail to bind prompt identity into model caches. | P1 provenance | Added per-run `prompt_template` to config, tokenization, encoder metadata and saved model config; legacy default preserved. |
| Original trainer saves full resume state only when the native stage ends. | P1 Spot safety | Draft uses sealed one-epoch segments with native optimizer/RNG restoration, not silent five-epoch resets. Cross-host restoration, publication, and interruption tests remain a release blocker. |
| Prior evaluation failed by passing `data_role` twice on a source-bound VIPER input. | P1 runtime | New source-bound inputs omit path/data_role redeclaration. CPU AST regression included; actual VIPER compiler verification still pending. |
| Incomplete or censored training matrices could leak into test reporting. | P1 analysis | Global guard requires all 15 unique trial IDs, validation-only selections, patience completion, valid model hashes, one training source and matching protocol hashes. |
| Five seeds cannot guarantee a stable training-population confidence interval or conventional exact-test significance. | P2 inference | Plan reports paired seed values/SD separately from conditional source-group bootstrap, notes low power, and prohibits best-seed comparisons. |
| GPU hardware could become confounded with the prompt arm. | P1 design | Whole seed blocks use a common GPU type/runtime; Colab A100 is not reserved for one arm only. |
| Baseline historical test was already inspected. | P2 reporting | Marked exploratory; historical scores are not the newly retrained controls. |
| Draft graph builders are not a complete production dispatcher or verified Spot recovery system. | P1 readiness | Stated explicitly; execution remains disabled. No runtime validation or independent reviews were fabricated. |

## Mechanical evidence

`python3 -m unittest tests.test_full_data_prompt_protocol -v`: **39 passed**.

`python3 -m py_compile csts_pilot/full_data_prompt_protocol.py csts_pilot/full_data_prompt_native.py csts_pilot/baseline_models.py`: passed.

`git diff --check`: passed. `python3 -m csts_pilot.full_data_prompt_protocol`: emitted exactly 15 distinct full-data trials without importing a model or allocating compute.

Tests are dependency-free structural/contract checks. They do not exercise CUDA, PEFT, tokenizer assets, actual native VIPER graph compilation, dropout/RNG recovery equivalence or cloud checkpoint transport.

## Release blockers

1. Ten attributable independent reviews of the same exact revision; currently none completed.
2. Pinned-environment native stage compilation, checkpoint save/load and evaluation-binding integration tests.
3. Token-length preflight across all three arms on training/validation; complete source-split separation and hash verification.
4. Real cold-start initial adapter hashes, frozen-base/gradient checks and uninterrupted-vs-resumed equivalence with dropout enabled.
5. Durable epoch upload/restore with manifest-last publication and interruption fault injection; independent worker lease, deadline and shutdown verification.
6. Refreshed Mantra authorization and current quota/pricing/capacity checks; optional Colab A100 access and hardware confirmation.
7. User has seen the plan/review findings and approves execution.

## Access evidence, current preparation

- Columbia CPU dev VM: reachable; new isolated JEP worktree created there.
- Available Claude reviewer CLI: authenticated status false; real print-mode probe returned `Not logged in`, zero input/output model tokens. A local CLI result/session UUID is **not** an independent review.
- Mac direct relay: connection failed; alternate device listing reports Mac offline. Therefore the known Colab CLI route is not presently verified.
- Existing Mantra cloud-user inventory read: token reauthentication required. No new quota request, instance start, allocation or training call made.
