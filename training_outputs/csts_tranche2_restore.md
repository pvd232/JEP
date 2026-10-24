# Restore and verify Tranche 2 evidence

The measured source is `cd6d14accb1213d797305cd7c581224d4422164d`, using native VIPER `e4ce91fa0a9330e769644aba0fccdfe062d5d821`. The [results](csts_tranche2_results.json), [cloud restoration record](csts_tranche2_cloud_restoration.json) and [file map](csts_tranche2_file_map.json) bind every reported comparison to its original native producer.

The final [publication receipt](csts_tranche2_report_publication.json) records the report ZIP's sealed GCS address, byte count and SHA-256. With the existing authorized account, restore that artifact through VIPER's `GcsProvider.fetch(GcsFileRef.model_validate(address))`. Check both its length and SHA-256 against the receipt before extracting it. The publisher requires this round trip and an exact comparison with the fixed input ZIP.

The ZIP contains `manifest.json`, the report and source files, control scripts, and `evidence/verified-cloud-evidence.tar.gz`. Verify each ZIP entry against its manifest. Verify the evidence archive against the collection receipt, extract it using Python's `tarfile` data filter, and check every extracted file against `archive-files.json`.

The evidence archive contains `phases/frozen/initial` and `phases/lora/initial`. Each phase preserves its summary, frozen selection, native verification receipt, exact prediction exports and training traces. The native receipts cover 19 runs and 89 recorded measurements. Large model, terminal, optimizer and embedding bytes remain sealed in native storage and on the preserved pilot disk; their exact references appear in the cloud restoration record.

To recompute scores and paired intervals in the existing CPU report environment, use the restored phase directories and this repository's saved FLAN/GPT prediction files:

```python
from pathlib import Path
from csts_pilot.baseline_report import build_report

repository = Path.cwd()
evidence = Path("/path/to/extracted/evidence")
build_report(
    repository,
    [evidence / "phases/frozen/initial", evidence / "phases/lora/initial"],
    Path("/tmp/csts-tranche2-recomputed"),
)
```

This analysis checks the manifests, native producer hashes, frozen selection, ordered row identities, labels, passages, conditions and source groups. It uses 2,000 paired draws over the same 1,241 source components, with bootstrap seed 61021. The computation reuses saved predictions and runs entirely on CPU. Rendering scripts and execution controls are retained in the report ZIP.

The report publication and [shutdown evidence](csts_tranche2_shutdown.json) have separate receipts. The shutdown receipt records the exact pilot identity, both stopped VM states, removal of the newly created scoped NAT and preservation of persistent disks.
