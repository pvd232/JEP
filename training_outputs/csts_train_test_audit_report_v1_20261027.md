# C-STS training and test label audit, V1

The full review covers **6,980 project training comparisons and all 2,834 raw project test comparisons**, including all 214 test rows originally marked invalid. Validation is retained at V4.1 except the four explicit user restorations in V4.2. The other 12 review-flagged exclusions before #64 retain the original user-confirmed rationales.

## Final dispositions

| Project split | Reviewed | Usable | Invalid | Unresolved scope | Split conflict |
|---|---:|---:|---:|---:|---:|
| Training | 6,980 | 6,067 | 909 | 4 | 0 |
| Test | 2,834 | 2,431 | 395 | 3 | 5 |
| Validation V4.2 | 1,830 | 1,576 | 253 | 1 | 0 |

## Changes from the supplied training/test labels

| Split | Corrected usable ratings | Previously valid now excluded | Previously invalid restored semantically | Restorations admitted to split |
|---|---:|---:|---:|---:|
| Training | 3,197 | 913 | 0 | 0 |
| Test | 794 | 242 | 58 | 53 |

Source labels are provenance, not a target that this audit tries to match. The metric denominators and labels have changed; scores from the prior dataset version should not be presented as directly comparable evidence of model improvement. No model predictions were inspected and no new training or scoring run was performed for this release.

## Review method and provenance

One manual source-only review was recorded for every one of the 9,814 comparisons. Four assistant contexts divided that first pass; this is **not four votes per row**. A different assistant context then adjudicated all **5,410** proposed exclusions, changed source ratings and low-confidence decisions. The root reviewer additionally reread **389** previously unflagged agreements to enforce the later user-confirmed boundaries and completed **15** final scope/consistency adjudications. These are assistant annotations with a recorded review trail, not independently measured human ground truth.

Each decision records entity/feature scope, a value from each caption, grade or exclusion, confidence and a concrete reason. Disagreement alone never creates an ambiguity exclusion. Remaining scope exclusions preserve competing readings with different outcomes. Historical first and focused judgments, retrospective corrections, source-only inputs, rubric and manually authored batches are retained in the compressed evidence archive.

## User adjudications preserved

| Report item | Row | Decision | Assistant-assigned rating |
|---|---|---|---:|
| #13 | train_624 | Include beverage count from meal-context sippy cup | 5 |
| #27 | train_1075 | Include coarse food serving amount | 3 |
| #59 | train_1809 | Include partial cow size/build information | 3 |
| #64 | train_2022 | Include partial room function from computer/TV context | 3 |

The user approved inclusion, not these four numerical grades. The user also confirmed the original exclusion rationales for **#6, #7, #11, #14, #15, #16, #26, #28, #31, #50, #58 and #63**. These retain their prior validation dispositions. #58 retains the specific child-versus-adult scope exclusion. All other 1,826 validation label records and the prior 1,572 usable validation rows are unchanged.

The confirmations distinguish missing precision from missing information. Generic food is insufficient for food type; unnamed wines do not supply wine varieties; generic furnishings or a messy room do not establish room function. Functional context can still supply a partial value. Concrete entity-only conditions retain the frozen type convention without inventing an unrequested finer subtype. The full rubric records this boundary and the earlier rider, dessert-meal and ground-angle anchors.

## Split integrity

The original 2,532 training rows removed for connected-caption overlap remain excluded. Training/validation membership is not reassigned. All 214 originally invalid test rows were reviewed semantically. Eight have a canonical caption in the original project training or validation split; any usable labels among them are retained in the audit but withheld from the test export. The guard uses the original split captions, including rows newly excluded by the label audit. Test components are merged when a safe restoration connects earlier test groups, while unchanged components retain their identifiers.

The reconstructed usable training, validation and test sets have **zero canonical caption overlap**. The test set also has zero overlap with the entire original project training and validation caption sets.

## Reconstruct and inspect

The ID-and-label package is [`datasets/csts-train-test-audit-v1`](../datasets/csts-train-test-audit-v1/README.md). Run its `reconstruct.py` against the exact pinned upstream CSVs; it verifies source hashes, coverage, split restrictions and output hashes. It writes `train.json`, `validation.json` and `test.json`, with legacy `dev.json`/`evaluation.json` aliases for existing loaders. Validation labels are in [`datasets/csts-validation-audit-v4-2`](../datasets/csts-validation-audit-v4-2/README.md).

- [Training exclusions](csts_training_exclusions_v1_20261027.md)
- [Test exclusions and split restrictions](csts_test_exclusions_v1_20261027.md)
- [Complete decision files](csts_train_test_audit_v1_20261027/README.md)
- [Review evidence archive](csts_train_test_review_evidence_v1_20261027.json.gz)
- [Validation user decisions](csts_validation_user_decisions_v4_2_20261027.json)

## Validation

Coverage, ordering, unique IDs, source reconstruction, duplicate consistency, user-decision preservation, rating normalization, split-caption disjointness and a full reconstruction round trip all passed. An independently authored checker verified the release against the source rows and frozen review records. The [verification record](../datasets/csts-train-test-audit-v1/verification.json), [independent check](../datasets/csts-train-test-audit-v1/independent_verification.json) and [reconstruction receipt](../datasets/csts-train-test-audit-v1/reconstruction_receipt.json) contain the results. The [artifact inventory](../datasets/csts-train-test-audit-v1/artifact_inventory.json) records file hashes. Labels are frozen before any future model evaluation.
