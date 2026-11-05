# JEP C-STS revision 1.1

This revision includes `evaluation_2450` following user adjudication and confirms the other twelve reviewed determinations.

| Split | Reviewed | Retained | Excluded |
|---|---:|---:|---:|
| Training | 6,980 | 6,051 | 929 |
| Validation | 1,830 | 1,576 | 254 |
| Test | 2,834 | 2,431 | 403 |
| **Total** | **11,644** | **10,058** | **1,586** |

The 2,532 earlier overlap removals remain separate. The current data therefore excludes 4,118 of the 14,176 source rows.

For `evaluation_2450`, the **supplied score is 1/5** and the **restored audited score is 3/5**. The user approved inclusion. The assistant assigned 3 after independent review: three unnamed coat colors supply partial information for comparison with beige. The [adjudication report](ADJUDICATION.md) shows supplied, previous and current scores for every reviewed case. All thirteen questions are resolved.

## Reconstruct

Obtain the pinned upstream CSVs described in the [source attribution](NOTICE.md). Run:

```bash
python datasets/csts-jep-revision-v1-1/reconstruct.py --source /path/to/upstream-csvs --output /path/to/jep-csts-v1.1
```

The script checks source and package hashes, applies the 26 overrides to the frozen baseline labels, verifies split separation, and writes `train.json`, `validation.json`, `test.json` and a receipt. Use `jep-csts-v1.1` when reporting results.

The [version-1 exclusion audit](../csts-jep-revision-v1/EXCLUSIONS.md) preserves the source evidence and peer reviews. Its `evaluation_2450` exclusion is superseded by this revision. [User decisions](user_adjudications.json) record all thirteen resolutions and the wording correction for `evaluation_855`. [Verification](verification.json) checks the single added row, unchanged training and validation, final export hashes and zero caption overlap. The inherited initial model-review judgments remain in `independent_grades.json`.
