# Native extraction repair: final result

Both pinned native backends run on the Colab A100 through reviewed adapters. The runtime and empty-input defects are repaired. **The current extraction configurations still fail the evidence-quality gate.** These results do not establish a model ranking or reproduce published UIE F1.

## Original frozen diagnostic

Two separate model-assisted review contexts required all seven semantic criteria to pass. The designed suite retains all 48 cases per model.

| Original first-attempt result | GoLLIE-7B | KnowCoder-7B-IE |
| --- | ---: | ---: |
| Joint accepted pipeline cases | 12/48 | 9/48 |
| Joint accepted answerable cases | 11/32 | 8/32 |
| Correct source-absence abstentions | 1/16 | 1/16 |
| Actual generated responses | 31 | 31 |
| Unsupported routes | 10 | 10 |
| Empty-input harness failures before generation | 7 | 7 |

The seven empty-input failures are our contract mismatch, not model misses. The ten unsupported routes also do not measure an attempted model response. All 62 actual generations passed token/text replay and reached EOS without truncation; many nevertheless failed semantic review. See the [family breakdown](csts_native_positive_diagnostic48_family_summary_20261028.md), [raw evidence index](csts_native_positive_diagnostic48_evidence_20261028_index.json) and [capture archive index](csts_native_positive_diagnostic48_archives_20261028.json).

The reference generator and reviewers share the same model alias in separate contexts. Human adjudication remains outstanding. This is a designed diagnostic suite, not a representative sample; resampling intervals describe stability within the suite.

## Mechanical recovery, separate origin

Two type-check corrections allow empty strings through rendering and normalization. The producer also clears cached error context before each source. Existing nonempty prompts remain unchanged.

Each model then made its first neural call on the seven previously blocked empty controls. **All 14 returned literal empty annotation lists, ended at EOS, and passed normalization and token replay.** No completed nonempty prediction was regenerated. All 292 original indexed capture artifacts and the original job remained unchanged. The [recovery receipt](csts_native_empty_input_first_generation_recovery_20261028.json) and [separate report](csts_native_empty_input_first_generation_recovery_20261028.md) preserve this origin; they do not replace the original diagnostic scores.

## What is ready

The reviewed code, capture/replay CLI, frozen protocols and raw evidence are published. The integrated adapter/existing suite passes 185 tests, with four public-entrypoint tests passing separately. Native runtime, protocol and replay checks are documented in the [final code/design review](../plans/csts-native-final-review-20261028.md) and [reproduction instructions](../docs/native_positive_repair.md).

General symbolic counting remains disabled after substantive failures. A separate quote-only comparator also failed evidence sufficiency. Neither native configuration is a validated replacement baseline for this task, and these outputs are not approved for downstream training. Fresh candidate evaluation, downstream readout and full-test scoring were not run. Further model adaptation would require a separately declared experiment rather than more retrospective repair of these scores.
