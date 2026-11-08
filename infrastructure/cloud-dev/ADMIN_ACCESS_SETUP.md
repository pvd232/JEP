# One-time owner action: authorize Columbia's machine identity

Open [Mantra in Google Cloud Shell](https://console.cloud.google.com/?project=mantra-477901&cloudshell=true), signed in as **pvd2112@columbia.edu**. Authorize Cloud Shell inside Google's interface when prompted. Do not send a verification code, token, credential file or private key to chat.

The remaining Google grant must be made by your administrator account. The Columbia VM currently authenticates as `dev-vm@pvd-dev-232.iam.gserviceaccount.com`; that principal still lacks the observed Mantra `compute.instances.get` permission. Your human account's permissions are not automatically inherited by the VM identity.

## Run this exact setup

[Inspect the pinned source](https://github.com/pvd232/JEP/blob/d6d8ee86f63e64f0b10c5a183020d8fa33e824c8/infrastructure/cloud-dev/tools/admin_columbia_mantra_access.py).

```bash
curl --fail --location --proto '=https' --proto-redir '=https' \
  'https://raw.githubusercontent.com/pvd232/JEP/d6d8ee86f63e64f0b10c5a183020d8fa33e824c8/infrastructure/cloud-dev/tools/admin_columbia_mantra_access.py' \
  -o columbia_mantra_access.py &&
printf '%s  %s\n' \
  '6e92d3cbd0fe8567336bb46764037b9f3f232c74e64d8d30774b798ab82eaea6' \
  'columbia_mantra_access.py' | sha256sum --check - &&
python3 columbia_mantra_access.py --apply
```

The `--apply` explicitly authorizes the additive permissions and public-key setup described below. Omit it to run only inspection and print the plan. A standalone shell is also available at [shell.cloud.google.com](https://shell.cloud.google.com/).

## Exactly what it changes

- Creates three narrowly defined custom roles if absent, without overwriting an existing role with different permissions.
- Grants the Columbia service account required read-only project discovery.
- Grants get/start/stop/SSH-metadata permissions only on the currently running, task-labelled JEP workers in approved East Asia regions; the script itself never starts or stops them.
- Grants instance-specific IAP access restricted to port 22.
- Grants Service Account User on the already-attached JEP worker service account, not on all project service accounts.
- Grants bucket-metadata read and object create/get only at the declared JEP artifact namespace. No object delete or bucket-wide object-list permission is included.
- Appends the Columbia host's **public** SSH key while preserving every existing metadata item and SSH key. The private key was generated locally on Columbia and was not exported. Its public fingerprint is `SHA256:fS9IqRqbaG8cqCCaL289rbH76apAQXO4ofPp8sqGBhY`.

The script identifies actual current instance names/IDs rather than assuming the obsolete Tokyo allocation. It refuses unexpected service accounts, OS Login mode, missing/extra live workers, replacement instance IDs, conflicting role definitions or incompatible storage policy. It does not change OS Login, firewall rules, startup scripts, service-account attachments, GPU state, trainer/collector processes, checkpoint data, approval manifests or shutdown deadlines. It preserves IAM etags and metadata fingerprints, and never broadens access automatically after a denial.

## Interpret the result correctly

On successful setup the output contains `ACCESS_SETUP_APPLIED` and `RECEIPT=<local JSON file>`. That means the additive setup calls completed, **not** that runtime SSH, Storage, expiry refresh or collector cutover has been verified. IAM propagation can delay observation of new grants.

If the script prints `SETUP_STOPPED`, retain the exact error and receipt. Do not stop a GPU, change its login mode, grant Owner, or repeatedly rerun a still-pending metadata operation. Some earlier additive grants may already have been applied; the receipt records them. The script does not attempt a destructive rollback.

Return the final status and receipt filename, or the exact error text. Do not return Google login codes, tokens or private keys.

## Remaining execution, without disturbing existing training

After permissions propagate, verify from Columbia using its attached identity: real destination read, IAP/SSH read-only status, and an artifact write/read/hash canary outside training files. Reconcile the actual training/checkpoint state before changing any controller. The old collector's cleanup path may stop/delete its worker, so do not terminate it for migration. Keep its deadlines and current training code intact. Use the replacement collector only at an explicitly safe assignment boundary.

PR #19 and PR #20 remain unmerged/uninstalled at this preparation. This setup script does not merge or install either PR. It resolves the administrator setup portion; operational acceptance and safe deployment remain explicit steps. Future newly provisioned workers require the same per-resource authorization setup; this script does not grant blanket provisioning rights.

## Evidence

At **2026-11-08 21:27 UTC**, the published source SHA matched the tested bytes on Columbia, the attached account's `cloud-platform` scope was observed, and **75 offline tests passed**: the prior 58 plus 17 bootstrap tests. The new checks cover policy/key preservation, idempotency, target scope, wrong-account/OS-Login rejection, plan-only behavior and no VM lifecycle commands. Those tests are not live administrator execution or independent subagent review.

No administrator grant has been applied by this preparation, no GPU operation or collector restart was performed, no Aether tool was used, and installed runner files were not replaced. Only Columbia's missing local SSH key was generated; its private bytes stayed on that host.

References: [attached workload identities](https://docs.cloud.google.com/docs/authentication/set-up-adc-attached-service-account), [IAP's separate permission requirements](https://docs.cloud.google.com/iap/docs/using-tcp-forwarding), [Storage IAM condition limits](https://docs.cloud.google.com/storage/docs/access-control/iam), [IAM propagation](https://docs.cloud.google.com/iam/docs/access-change-propagation).
