# Extraction comparison review

Current status: **native task-adapter calibration is unresolved.** The capture, parsing and reproducibility controls were reviewed, but subsequent adversarial review found that no in-task positive/negative control had validated the generic condition-to-relation mapping. The model-comparison conclusion is suspended. The earlier approvals below document implementation and evidence integrity, not native adapter calibration.

Base: `61a48b2fa580c7457155535bcfafde10426dab83`. Scope: the three extraction modules, package initializer, configuration, optional native requirements, three test modules and [methods](csts-extraction-comparison-methods.md). Python cache exclusions and the preflight receipt complete the publication.

## Design review

The direct GPT scorer and proposition extractor are separate refreshed baselines, both using `gpt-6.1-sol` with `max` reasoning. JSON versus Python holds the entity/fact contract fixed. Proposition versus structured output also changes decomposition. KnowCoder and GoLLIE compare complete extraction systems.

The 120-pair validation sample is independent of ratings and model errors. The current adjudicated exports are pinned. Full-test preparation checks the identical validation protocol lock and retains all 2,431 pairs, including restored `evaluation_2450`. Previous test exposure remains disclosed.

The primary prompt excludes typical-color assumptions, while the earlier pilot references accepted them. Direct similarity uses the existing audited ratings. Keep inference-policy failures visible and interpret new-versus-historical score differences as protocol differences. This is a refreshed baseline with per-item requests, revised guidance and a common envelope.

## Resolved implementation findings

| Finding | Repair and observer |
|---|---|
| Extraction could precede reference sealing | Extraction requires a valid source-only reference seal; regression verifies no capture starts before it. Direct scoring remains independent. |
| Edited parsed predictions could change reported scores | Result loading verifies raw artifact hashes and reconstructs successful payloads from original Codex events/response or native generation. Tampering tests reject disagreement. |
| Review identity maps could change the arm or source join | A final review seal binds packet, map, template and references; coverage and component joins are rechecked. |
| Unknown counts were forced into exact integers | Structured counts support unknown cardinality; boolean, zero and noninteger counts fail. |
| Export discarded abstention status | Exports retain status, reason and raw-capture path/hash beside evidence. |
| Operational reports blocked later reviewed reports | Reports use deterministic content-addressed names; repeated identical reporting is idempotent. |
| Native prompts requested an incompatible output envelope | Native semantic guidance uses each checkpoint's own constructors and omits GPT transport instructions. |
| Legal native constructor forms were rejected | Literal positional, named and nonconflicting mixed arguments are accepted; duplicates, extra fields and executable code fail. |
| Codex output-token control was unsupported | Removed the unverified setting. Record provider token-cap unavailability; apply a common timeout and retained-payload byte bound. |
| CLI preparation passed the wrong argument name | Actual command dispatch is exercised through preparation, dry runs, capture fixtures, sealed review, reporting and export. |
| Result loading repeatedly reparsed the full input set | Precompute identity lookup once per arm. |
| Invalid numeric targets could pass scale checks | Explicit numeric type, finite-value and normalized-scale validation. |

## Verification

- Independent implementation review: 50 tests passed; `compileall` passed.
- Root verification: the same 50 tests passed; `compileall` passed.
- Real dataset reconstruction matched published hashes for training, validation and test.
- Validation preflight: 120 pairs, 239 extraction inputs, 110 source components.
- Full-test preflight: 2,431 pairs, 4,824 extraction inputs.
- All six configured arms completed dry-run planning.
- No inference requests or checkpoint loads occurred.

The [machine-readable preflight](../training_outputs/csts_extraction_comparison_preflight_20261027.json) records input identities, source hashes and exact request counts.

Initial prepared implementation SHA-256 identities (before the execution amendments below):

| File | SHA-256 |
|---|---|
| `extraction_comparison.py` | `2f2d91afa04395e3a90430c439565261d2f5acfce64e1a117765234513c7dcf7` |
| `extraction_formats.py` | `676a1856ca0f6f3925098664e727483a7f0dcc5a13922340efd3b2229bcef0db` |
| `extraction_native.py` | `4f50273aca3c6a0fb1d2179b6a95bbeffb5247ceed466490eb67eefa53b56517` |
| Configuration | `a10239cc9e79b320fca07cd034285e5a75fbea9e51da212ae8bb73be5396b8fe` |
| Methods | `90a7a15e0cbb0956cba4e306bcc049d306b655d3f48ff292000f36e8fe360c36` |

## Remaining execution evidence

Live Codex captures and native A100 generation have now been exercised. Runtime package versions are retained with native captures. GoLLIE uses the reviewed stock-SDPA compatibility backend and unchanged checkpoint tensors; numerical parity with the authors' FlashAttention implementation remains unverified.

Reviewer independence and human adjudication require operator oversight. A supplied reviewer identifier does not establish independent human review. GPT model weights cannot be pinned through the available alias. Native output lacks the richer GPT support metadata and therefore requires semantic review.

## Execution amendments and further review

The preparation review did not catch the missing KnowCoder inference wrapper. The first live run produced 239 empty lists; an audit of the pinned author training template and inference code found the mismatch. Preserve that run as a diagnostic. The corrected author wrapper, tokenizer settings and stop delimiter are frozen in a separate run, with the original raw generations retained and no semantic repair.

The GoLLIE loader initially rejected Transformers 5.20's default `rope_scaling` alias. Independent review approved accepting only the validated unscaled alias while continuing to reject scaled configurations. A regression reproduces the actual modern property alias.

Both amendments received independent code review. All 61 extraction tests, eight transport-amendment tests and compile checks pass. A separate inference-free assembly integration check exercises multiple origin protocols, absent-response transport, fixed denominators, paired component intervals, duplicate review rejection and tamper detection. The assembly operator keeps original request protocol hashes unchanged and declares every origin and amendment.

The blinded screen uses two separate model-assisted review passes. Their agreement is not proof of human validity; disagreements remain available for adjudication. No Qwen training has launched.

A further review found that transient Codex reconnect notices had invalidated five otherwise complete captures. A narrow parser amendment revalidated the original responses offline, checked final-message agreement and preserved every original byte. It recovered all 120 direct scores without new model calls; proposition recovery remains a separate sensitivity audit, preserving the primary panel.

The review collector received independent review and 21 synthetic checks. Repairs require a completed audit with exit code zero and account for the Mac's `/tmp` path alias. One capacity-only failure with no response received one separately recorded operational recovery; scored answers were never retried. Atomic batch claims prevent duplicate inference during scheduling acceleration. Final counts and paired intervals were recomputed independently from the raw judgments.

The published archive contains all raw proof and origin implementations. Independent extraction verified all 6,095 indexed members and reproduced the exact review packet, counts, intervals and disagreements offline. The [results report](../training_outputs/csts_extraction_screen_20261028.md) records the limited model-assisted interpretation.

## Subsequent design finding: missing in-task adapter calibration

The initial design review accepted a generic binary `ConditionRelation(subject, value)` for every condition without checking whether that mapping is usable on literal positives from the actual task. Unary type recognition, binary attributes and aggregate counts were not separately validated. The control examples subsequently copied from the authors establish functional generation under those schemas; they do not validate this mapping. This is a design gap missed by the earlier review.

The raw outputs and model-assisted arithmetic remain valid descriptions of the attempted configuration. They justify withholding these captured outputs from training. They do not justify ruling out KnowCoder or GoLLIE, or describing the attempted adapter as a validated native baseline.

The separately sealed [48-cell A/B/C diagnostic](../training_outputs/csts_native_adapter_diagnostic_20261028.md) is complete. Original and formatting-only GoLLIE prompts recovered none of six literal positives; the descriptive native schema recovered four. Both negatives remained empty. KnowCoder remained empty throughout. Independent review verified the raw outputs and original prompt identities. This demonstrates a selected-case adapter effect and confirms that the earlier native model-choice conclusion was premature. C changes multiple schema factors together; the diagnostic neither isolates one cause nor supplies a representative model score. Any repaired adapter still needs fresh representative evaluation.
