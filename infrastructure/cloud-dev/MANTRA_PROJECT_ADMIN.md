# Columbia → Mantra: active project-wide access

**Verified November 8, 2026, 23:50 UTC.** The owner granted `roles/admin` on `mantra-477901` to `dev-vm@pvd-dev-232.iam.gserviceaccount.com`, with an unconditional project binding. A live IAM read from Columbia confirmed that binding.

This is the active owner-selected access policy. The earlier custom-role/per-worker grant bootstrap is superseded by this project-wide binding. It remains historical code; routine jobs use the attached service account and the existing job runner.

## Verified operational path

```text
Columbia VM / cloud-project --project jep
    → attached dev-vm service account
    → Mantra project-wide Admin access
    → Compute, IAP/SSH, and Cloud Storage
```

Live acceptance covered Compute inventory, IAM read, Cloud Storage write/read with matching SHA-256, creation of a disposable E2 CPU VM, IAP/SSH guest execution as `machina`, and removal of that test VM plus its disk. Nine pre-existing project SSH keys and all other project metadata were preserved while adding Columbia's public key. The private key remains on Columbia.

A durable job, `0bfa7937bdae41e5951e72d2f2eb00a8`, inherited the attached identity from the existing JEP runner, read Mantra's instance inventory, and read/hash-verified the storage canary. It finished with exit code zero. This exercised the actual systemd job environment.

The current runner deliberately distinguishes host identity (`pvd-dev-232`, VM `dev`) from workload destination. Supply `--project=mantra-477901` and the intended zone in cloud commands. The runner selects the attached account. Existing task manifests still bind source revisions, resource IDs, checkpoints and cleanup ownership to their executions; those are run-integrity checks.

## Routine read-only commands

On Columbia:

```bash
/opt/cloud-dev/columbia/bin/cloud-project --project jep run \
  gcloud compute instances list --project=mantra-477901 \
  --format='table(name,zone.basename(),status)' --quiet

/opt/cloud-dev/columbia/bin/cloud-project --project jep status \
  0bfa7937bdae41e5951e72d2f2eb00a8
```

For durable work, use the existing `cloud-project --project jep submit --cwd ... -- COMMAND ...` entrypoint and a fresh approved assignment. Preserve the current owner of any active worker during transitions.

Google's metadata service and supported clients supply short-lived credentials for the attached identity. This acceptance verified fresh acquisition and separate CLI/durable-process access. A real post-expiry soak observation remains a separate measurement. Identity changes, account disablement, IAM revocation and external service failures remain normal operational dependencies.

## Preserved experiment evidence

Columbia verified the presence and exact recorded sizes of all 77 saved training archives, totalling 35,921,745,920 bytes. The two final-publication archives were streamed independently and matched their recorded SHA-256 hashes. Training/evaluation code, checkpoint contents, and experiment resource lifecycle were left unchanged by this acceptance work.

See [the machine-readable acceptance receipt](MANTRA_ACCESS_VERIFIED_20261108.json) for actual identities, hashes, job ID and test cleanup. The evidence distinguishes full-inventory object/size checks from the two freshly recomputed archive hashes.

## Operational authority

The user's selected policy is broad project administration. The scoped-role helper is unnecessary for this configuration. Columbia handles academic execution. Google Cloud Shell remains an owner-controlled administrative interface for changes to the policy itself. The connector, host-local SSH key, and Google service-account credentials each retain their established authentication mechanism.

Reference: [Google Cloud CLI attached-account authentication](https://docs.cloud.google.com/sdk/docs/authenticate).
