# Workload identity across Columbia and Mantra

This implementation extends the existing runner and probe; it does not deploy a credential service or migrate a live job. The installed `/opt/cloud-dev/columbia/bin` files and `/etc/cloud-dev/columbia` profile remain unchanged during development.

## Configuration

The existing host `target` continues to identify Columbia (`dev`, `pvd-dev-232`). Add this object to a **reviewed future project definition**, not to an active collector's files:

```json
{
  "workload": {
    "resource_project": "mantra-477901",
    "instance_manifest": "/absolute/path/to/approved-new-controller-manifest.json",
    "artifact_prefix": "gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_full_data_prompt_20261107/"
  }
}
```

The manifest must be a regular file with a full `source_commit`, `user_execution_approved: true`, `controller_account` matching the attached service account, and one or two explicit `assignments` containing `project`, `zone`, `instance_name` and immutable numeric `instance_id`. Existing GPU/execution/deadline fields are retained; this extension does not invent a second assignment authority. A manifest for a human-account collector is deliberately rejected. Do not rewrite an active worker's approval to pass this check.

`project_profile()` validates the optional workload fields. `project_environment()` sets the resource project independently of the host identity, removes inherited credential/endpoint/metadata overrides and inherited default zone/region for cross-project work, and prohibits browser prompting. Explicit credential overrides, a local ADC file, or persisted SDK auth overrides fail closed. Existing project definitions without `workload` retain host-project defaults.

`workload_context()` reads and SHA-binds the approved manifest once. It checks account consistency, explicit target identity, duplicate workers and bounded manifest size without outputting credentials.

## Read-only entry points

From the checked-out repository:

```bash
python3 infrastructure/cloud-dev/implementation/probe_identity.py \
  --profile /path/to/reviewed-candidate-profile.json

python3 infrastructure/cloud-dev/implementation/probe_identity.py \
  --profile /path/to/reviewed-candidate-profile.json --workload

python3 infrastructure/cloud-dev/tools/identity.py \
  --profile /path/to/reviewed-candidate-profile.json workload-plan
```

These are template paths: use the actual reviewed candidate profile. The first probe is **host-only**. The second also checks exact manifest-selected instance reads, using the attached identity observed in metadata. It fails nonzero on a denial, unavailable metadata, unexpected response, or replacement instance. It reports `execution_ready: false` even if those reads pass: SSH, IAP, Storage, actual token renewal and exclusive collector ownership have not been tested by a Compute GET.

The IAM entry point emits **ADMINISTRATOR_PLAN_ONLY**: exact assigned resources, get/start/stop permissions, IAP role/port intent, create/get object permissions and unresolved guest/CLI prerequisites. It has no apply path, creates no service accounts or keys, and cannot stop/restart a VM. The pre-existing `identity.py apply` provisions VM identity and can restart hosts; **do not use that operation for this workload-access repair**.

An authorized administrator still needs to inspect/apply the scoped Mantra bindings. The runtime service account is not permitted to grant itself rights. No user login, IAM mutation, account impersonation or alternative tool route is attempted when authorization fails.

## Collector dependency

The companion collector change consumes the installed `probe_identity.py --workload` contract and must run through the corresponding `cloud-project --project jep` environment. Roll out this runner/probe code before opting a **new or fully quiescent assignment** into that collector. The candidate collector defaults to read-only inspection, preserves all disks, and requires explicit monitor ownership.

Do not overwrite installed scripts/profile files or stop the existing collector while it owns live training. The old collector can perform destructive cleanup from its `finally` branch. No live handover is implemented or claimed here. Prefer finishing its assignment, verifying publication, and starting the next assignment with the new code. Existing independent shutdown deadlines remain unchanged.

## Tests and evidence

```bash
python3 -m unittest discover -s infrastructure/cloud-dev/tests -q
```

58 tests passed at preparation, including 28 pre-existing tests. Coverage includes host/resource separation, manifest SHA/account/instance identity, inherited-versus-explicit overrides, local ADC refusal, destination 403 after host success, no token in receipts, redirect refusal, and a no-mutation IAM plan. Mocked renewal checks are not a real after-expiry test.

A real candidate host-only probe succeeded on Columbia. A separate read-only Mantra instance request at 2026-11-08T08:19:42Z still reported missing `compute.instances.get` for `dev-vm@pvd-dev-232.iam.gserviceaccount.com`. Thus this code is implemented/tested but **target authorization and operational cutover are not complete**. Live runner SHA-256 values were unchanged before and after preparation. No GPU mutation or collector restart was performed.

## Remaining deployment acceptance

After administrator setup, verify the real destination read, IAP and guest SSH identity, an allowed artifact round-trip, denied unrelated operations using nonmutating permission checks, post-expiry calls without user intervention, and a clean reconstruction without copied credentials. Credentials do not provide network reachability or cloud capacity. A platform tool refusal remains distinct from Google IAM.

No new token broker, key store, private Google key, login-cache replication or refresh daemon is introduced. Google clients own token acquisition/renewal. Host-local SSH/connector credentials remain in their protected existing stores and are not exported in this code change.

Primary references: [attached service accounts](https://docs.cloud.google.com/docs/authentication/set-up-adc-attached-service-account), [instance access](https://docs.cloud.google.com/compute/docs/access/managing-access-to-resources), [IAP](https://docs.cloud.google.com/iap/docs/using-tcp-forwarding), [Storage IAM](https://docs.cloud.google.com/storage/docs/access-control/iam).
