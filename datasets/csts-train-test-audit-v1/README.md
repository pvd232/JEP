# C-STS training/test audit V1

[Full report](../../training_outputs/csts_train_test_audit_report_v1_20261027.md) and [decision files](../../training_outputs/csts_train_test_audit_v1_20261027/README.md). This package preserves the original connected-caption project split and supplies audited labels for all 6,980 training and 2,834 raw test rows. The paired validation package is [V4.2](../csts-validation-audit-v4-2/README.md).

## Reconstruction

Use the pinned `LivNLP/C-STS-Reannotated` revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b` with original `csts_train_reannotated.csv` and `csts_validation_reannotated.csv` bytes.

```bash
python datasets/csts-train-test-audit-v1/reconstruct.py --source /path/to/upstream-csvs --output /path/to/audited-data
```

The script checks original hashes, rebuilds the original source partition, applies ID-keyed labels and split restrictions, and verifies every output hash. It writes canonical project files `train.json`, `validation.json`, `test.json` and byte-identical legacy aliases `dev.json`, `evaluation.json`. No model training or evaluation is launched.

## Files

- `training.labels.json`: all project training dispositions.
- `test.labels.json`: all raw test dispositions, including source-invalid rows and split restrictions.
- `manifest.json`: counts, provenance, source hashes, group merges and expected reconstructed hashes.
- `rubric.md`: frozen semantic rules and user continuation decisions.
- `verification.json`: release coverage and reconstruction checks.
- `source_partition.py`: pinned original preparation implementation.

Source and group identifiers remain traceable. A semantically usable test label can still be excluded from export if it shares a caption with original training or validation. Original validation labels outside the four explicit restorations remain fixed.
