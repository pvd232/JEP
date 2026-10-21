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

For the answer and joint study, replace the root with
`/mnt/rico-source-data/jep-joint-csts-20261021` and use its separate environment:

```sh
/mnt/rico-source-data/jep-joint-env-20261021/bin/python \
  /home/machina/jep-csts-observer-20261021/progress.py \
  --root /mnt/rico-source-data/jep-joint-csts-20261021 --watch
```

The controller log gives trial completions and failures:

```sh
tail -f /mnt/rico-source-data/jep-joint-csts-20261021/csts_results/launcher.log
```

VIPER saves training and development MSE in each run's
`attempts/1/measurements` directory. Completed `trace.json` artifacts contain the
full epoch history, selected checkpoint, elapsed time and peak GPU memory.
Joint traces also include training and development answer cross-entropy.
The answer stage prints its completed count after each batch. Its artifact
contains every generated answer and its source-span validation result.

The observation process reads files and queries GPU utilization. Its JSON
snapshot includes metrics and configuration. It leaves evaluation inputs closed.
Model checkpoints, source references and native run records remain available
through VIPER. The joint study publishes to the configured GCS repository.
