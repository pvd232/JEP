# C-STS revision 1: exclusion audit

**User adjudication is complete.** [Revision 1.1](../csts-jep-revision-v1-1/README.md) restores `evaluation_2450` and confirms the other twelve reviewed determinations. This report preserves the revision-1 audit snapshot.

Every excluded row has a recorded reason and a peer check. The case reports follow the earlier validation format. Dataset labels remain at `jep-csts-v1`.

| Split | Reviewed | Excluded | Retained |
|---|---:|---:|---:|
| Training | 6,980 | 929 | 6,051 |
| Validation | 1,830 | 254 | 1,576 |
| Test | 2,834 | 404 | 2,430 |
| **Total** | **11,644** | **1,587** | **10,057** |

The current exclusions comprise **1,568 invalid cases, 14 unresolved scopes and 5 split restrictions**. A separate ledger documents the **2,532 earlier training removals for caption overlap**.

## Case reports

[Review the 13 outstanding questions](ADJUDICATION.md).

- [Training: all 929 exclusions](../../training_outputs/csts_jep_v1_exclusion_audit/training.md)
- [Validation: all 254 exclusions](../../training_outputs/csts_jep_v1_exclusion_audit/validation.md)
- [Test: all 404 exclusions](../../training_outputs/csts_jep_v1_exclusion_audit/test.md)
- [Earlier overlap removals: all 2,532 rows](../../training_outputs/csts_jep_v1_exclusion_audit/overlap.md)

Peer review flagged **12 policy questions and one issue with a recorded value**. Each report states the evidence conflict and the decision needed. Validation retains the original case numbers and the twelve user-confirmed exclusions.

## Policy

| Code | Rule |
|---|---|
| S1 | Use the requested entity, role and feature. |
| S2 | Entity-only conditions default to type. |
| S3 | A wholly missing feature or required entity yields an invalid comparison. |
| S4 | Partial values support graded comparison. |
| S5 | Ordinary direct context can supply a value. |
| S6 | Speculative identities and fine details exceed the inference threshold. |
| S7 | Competing ordinary readings with different outcomes can leave scope unresolved. |
| S8 | Reader disagreement alone supplies insufficient grounds for exclusion. |
| X1 | Caption-group overlap requires separation of the original partitions. |

Authors reread every semantic exclusion. A different assistant reviewed each explanation. Separate source-graph checkers verified every earlier overlap removal and the five test restrictions. [Structured records](../../training_outputs/csts_jep_v1_exclusion_audit/records.json) preserve the per-row decisions and evidence. [Checks](../../training_outputs/csts_jep_v1_exclusion_audit/checks.json) record coverage, source preservation and prose results.
