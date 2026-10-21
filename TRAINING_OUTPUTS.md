# See training output

[C-STS progress](CSTS_PROGRESS.md) contains learning curves and a timestamped
development table. Live output is available through the progress command below.
It refreshes every 15 seconds and shows epoch metrics, GPU use, free storage and
the controller's status.

From a terminal authenticated with the Columbia GCP account:

```sh
gcloud compute ssh machina@rico-source-l4-uswest4c \
  --project=mantra-477901 --zone=us-west4-c --tunnel-through-iap \
  --command='/home/machina/jep-joint-pilot-20261020/.venv/bin/python /home/machina/jep-csts-observer-20261021/progress.py --root /home/machina/jep-csts-20261021 --watch'
```

On the VM, the shorter command is:

```sh
/home/machina/jep-joint-pilot-20261020/.venv/bin/python \
  /home/machina/jep-csts-observer-20261021/progress.py \
  --root /home/machina/jep-csts-20261021 --watch
```

The resumed answer and joint study uses
`/mnt/rico-source-data/jep-joint-recovery-20261021` and its separate environment:

```sh
/mnt/rico-source-data/jep-joint-env-20261021/bin/python \
  /home/machina/jep-csts-observer-20261021/progress.py \
  --root /mnt/rico-source-data/jep-joint-recovery-20261021 --watch
```

The controller log gives trial completions and failures:

```sh
tail -f /mnt/rico-source-data/jep-joint-recovery-20261021/csts_results/finalizer.log
```

VIPER saves training and development MSE in each run's
`attempts/1/measurements` directory. Completed `trace.json` artifacts contain the
full epoch history, selected checkpoint, elapsed time and peak GPU memory.
Joint traces also include training and development answer cross-entropy.
The answer stage prints its completed count after each batch. Its artifact
contains every generated answer and its source-span validation result.

The finalizer prints counts and epoch metrics every 30 seconds. It publishes
[live status](training_outputs/csts_live_status.json) and completed training
curves to GitHub every five minutes. The launcher log in the same directory
contains controller errors. Verified storage cleanup writes
`/mnt/rico-source-data/jep-storage-cleanup-20261021.log`.

The VM stops after all five approaches have been evaluated across three seeds,
the approved backup and cleanup have completed, and reports have been published
to GitHub and VIPER. A failed study leaves an error in the finalizer log.

The observation process reads files and queries GPU utilization. Its JSON
snapshot includes metrics and configuration. It leaves evaluation inputs closed.
Model checkpoints, source references and native run records remain available
through VIPER. The joint study publishes to the configured GCS repository.



## Cached annotation format screen

The separate cached-format pilot has completed native CPU preparation; GPU training awaits capacity. Its [protocol](training_outputs/csts_annotation_format_protocol.md) specifies the three matched arms, common budget freeze after throughput profiling, development Spearman checkpoint selection, and all-model freeze before benchmark evaluation. [Preparation evidence](training_outputs/csts_annotation_format_preparation.json), [metadata source review](training_outputs/csts_annotation_format_metadata_audit.json), [native immutable retrieval references](training_outputs/csts_annotation_format_retrieval.json), and [Tokyo allocation errors](training_outputs/csts_annotation_format_capacity.json) are published. The retrieval record identifies the full cache and every prepared artifact by exact native reference, SHA256 and byte count. The earlier VM study and its outputs remain intact.
