# One-time owner authorization for Columbia → Mantra

**Current state, November 8:** the tested runner/probe update is installed on Columbia. Host authentication and the existing job-runner smoke test pass. Mantra authorization and collector cutover are still incomplete. No GPU worker, trainer, publisher, collector, checkpoint, shutdown timer, attached service account or firewall was changed during that installation.

The human account's administrator permissions have **not** been verified from this chat. The available Columbia credential is `dev-vm@pvd-dev-232.iam.gserviceaccount.com`; it lacks the observed Mantra access. The connected browser session and the Mac admin relay are unavailable. A new permission preflight in the setup script tests the **actual authenticated administrator caller** before any IAM or SSH-metadata change. It does not assume that an email address or an account-owner claim proves those rights.

## Owner-session entrypoint

Open [Mantra in Google Cloud Shell](https://console.cloud.google.com/?project=mantra-477901&cloudshell=true), signed in as **pvd2112@columbia.edu**. Authorize Cloud Shell inside Google's interface when prompted. No authorization code, token, credential file or private key needs to enter chat.

[Inspect the pinned script](https://github.com/pvd232/JEP/blob/746c41475cb99131fa1c1a52bb2e0118da318b71/infrastructure/cloud-dev/tools/admin_columbia_mantra_access.py). This source supersedes the earlier setup command, which did not explicitly preflight administrator permissions.

```bash
curl --fail --location --proto '=https' --proto-redir '=https' \
  'https://raw.githubusercontent.com/pvd232/JEP/746c41475cb99131fa1c1a52bb2e0118da318b71/infrastructure/cloud-dev/tools/admin_columbia_mantra_access.py' \
  -o columbia_mantra_access.py &&
printf '%s  %s\n' \
  '268f2e99ea3d76bc8b434166ad3beb3ca21e35d7916b6b4e515b21ee8498710d' \
  'columbia_mantra_access.py' | sha256sum --check - &&
python3 columbia_mantra_access.py --apply
```

Omit `--apply` for read-only inspection and permission checks. With `--apply`, mutation begins only after all observed preflight checks pass. Actual write APIs still enforce current IAM and organization policy; a preflight is not a guarantee that a later write cannot fail.

## Permission checks before mutation

The script calls Google's permission-test APIs for the logged-in caller on the project, worker service account, artifact bucket, selected Compute instances and their IAP resources. Missing permissions are reported by exact resource and permission name. Permission-test requests do not grant rights.

Custom-role creation is checked only if a role is absent. SSH-metadata write permission is checked only if Columbia's public key needs to be added. Disabled-service errors retain the API service and consumer-project identifier without exposing credentials. The script does not enable APIs automatically, assign Owner, weaken policies, or retry through a different identity after a denial.

The previous `SERVICE_DISABLED` diagnostic seen from the Columbia VM named consumer project **263437697547**, which was independently verified to be **pvd-dev-232**. It was not evidence that the human account lacked Mantra administrator privileges, nor proof that Cloud Resource Manager was disabled in Mantra. The owner-session checks must establish their own outcome.

## Exactly what authorized application changes

The script creates three scoped custom roles if absent, without overwriting a conflicting role. It grants the Columbia account project discovery reads; get/start/stop/SSH-metadata rights on the selected task workers; instance-specific IAP access for port 22; Service Account User on the existing JEP worker account; and bucket-metadata read plus object create/get within the approved JEP namespace. It does not grant object-delete or object-list permission.

It appends Columbia's public SSH key while preserving existing keys and all other instance metadata. The private key remains on Columbia. Public fingerprint: `SHA256:fS9IqRqbaG8cqCCaL289rbH76apAQXO4ofPp8sqGBhY`.

Selection uses current running task-labelled workers, not obsolete fixed Tokyo names. Unexpected identities, guest-login mode, region, role definitions, extra/missing workers or storage policy stop the procedure. The setup does **not** start, stop, reset, delete or recreate VMs; change service-account attachments, OS Login or startup scripts; restart collectors; rewrite approvals; or open training/test data.

IAM etags and metadata fingerprints prevent blindly overwriting concurrent changes. If a later call fails, earlier additive grants can remain and are retained in the receipt. There is no destructive automatic rollback.

## Result interpretation

- `ADMIN_PERMISSION_PREFLIGHT_PASSED`: read-only checks observed the necessary caller permissions. No grant is implied by this message alone.
- `ACCESS_SETUP_APPLIED`: the setup calls completed. Runtime SSH/storage/renewal and safe controller migration still require acceptance checks from Columbia.
- `SETUP_STOPPED`: retain the exact error and receipt. Do not stop a GPU, disable OS Login, broaden to Owner or rerun a still-pending metadata operation to force progress.

The final line names a local `RECEIPT=...json`. Share status/error text and that filename, never login codes, tokens or private keys.

## What is already installed

At **2026-11-08 21:48:55 UTC**, `project.py` and `probe_identity.py` from tested source `ac9a4c6de08ab7fbd7d9ba48b760da4b08c5bfd9` were installed atomically on Columbia after verifying no active/queued CPU durable jobs. Original source files were backed up. The host probe passed and explicitly reported `scope: host_only` and `workload_access_verified: false`; a real `cloud-project --project jep run` smoke test passed. The connector PID, project profile and `cloud_job.py` bytes stayed unchanged. No service restart was performed.

No active workload manifest was rewritten. The companion collector in PR #20 is **not** installed over a running controller. Existing collectors can execute destructive cleanup when terminated, so completing the IAM setup must be followed by read-only state reconciliation and a safe assignment boundary, not a blind service stop.

## Verification still required

After authorization propagates: actual destination reads from Columbia's attached identity, IAP/SSH status reads, an artifact canary write/read/hash check outside training files, denied unrelated operations using nonmutating checks, and calls across token expiry. Verify recovered checkpoints before changing ownership. Preserve the independent shutdown deadlines.

Future replacement workers need their own scoped authorization; this is not blanket VM-provisioning authority. This setup removes routine human Google logins from job execution, not platform action-safety checks, resource capacity constraints or network dependencies.

## Tests and provenance

**81 offline tests passed** against source `746c41475cb99131fa1c1a52bb2e0118da318b71`, whose script and test bytes were compared with the published GitHub objects. The six additional preflight tests check caller permissions, malformed/empty results, all resource boundaries, conditional role/key requirements and rejection before writes. These are offline tests, not actual administrator execution or independent subagent review.

No Aether tools or copied Google credentials were used. No native subagent execution capability is exposed in the current chat; no hosted Codex review is represented as one.

Official API references: [project permission tests](https://docs.cloud.google.com/resource-manager/reference/rest/v1/projects/testIamPermissions), [service-account permission tests](https://docs.cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/testIamPermissions), [Compute permission tests](https://docs.cloud.google.com/compute/docs/reference/rest/v1/instances/testIamPermissions), [Storage permission tests](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets/testIamPermissions), [IAP API](https://docs.cloud.google.com/iap/docs/reference/rest).
