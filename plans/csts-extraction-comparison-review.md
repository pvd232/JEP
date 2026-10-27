# Extraction comparison review

Verdict: **Approve experiment preparation.** Independent design and implementation reviews found no remaining blocking findings after repairs.

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

Final reviewed SHA-256 identities:

| File | SHA-256 |
|---|---|
| `extraction_comparison.py` | `2f2d91afa04395e3a90430c439565261d2f5acfce64e1a117765234513c7dcf7` |
| `extraction_formats.py` | `676a1856ca0f6f3925098664e727483a7f0dcc5a13922340efd3b2229bcef0db` |
| `extraction_native.py` | `4f50273aca3c6a0fb1d2179b6a95bbeffb5247ceed466490eb67eefa53b56517` |
| Configuration | `a10239cc9e79b320fca07cd034285e5a75fbea9e51da212ae8bb73be5396b8fe` |
| Methods | `90a7a15e0cbb0956cba4e306bcc049d306b655d3f48ff292000f36e8fe360c36` |

## Remaining execution evidence

Live signed-in Codex capture and native GPU loading/generation require execution evidence. The optional native requirements are a starting declaration, with package versions recorded after loading; they are not a tested environment lock. GoLLIE requires its pinned custom model code, CUDA and flash-attention.

Reviewer independence and human adjudication require operator oversight. A supplied reviewer identifier does not establish independent human review. GPT model weights cannot be pinned through the available alias. Native output lacks the richer GPT support metadata and therefore requires semantic review.

This PR establishes preparation, capture controls, safe parsing, review and reporting. It reports no new model-performance result and launches no Qwen training.
