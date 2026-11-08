# Columbia → Mantra without recurring human logins

**Status: proposed design and contract draft; not deployed, not independently reviewed.**

Prepared November 8, 2026. This change is limited to credential use and the existing academic execution route. No IAM policies, service-account attachments, GPU states, running jobs, SSH settings or connector permissions were changed while preparing this document. All host inspection used `columbia-vm`; no Aether execution was used.

## Decision

Reuse Columbia's already-attached service account and Google's metadata-token mechanism. Give that identity narrowly scoped access to the approved Mantra workers and JEP artifacts, and make the existing runner and collector consistently use it. **Do not build a token broker, copy a human login to another VM, or create a service-account private key.**

This is mostly a missing authorization setup plus a small integration repair, not a new credential-management product. The minimum delivery is one administrator-reviewed permission change set, small changes to existing profile/probe/callers, focused acceptance tests and a short maintenance procedure. New GPU provisioning, quota requests, account migration, Colab authentication and model-provider authentication are outside this first change.

## 1. How the current system works

There are three separate forms of access. First, the ChatGPT connection authorizes calls to the Columbia terminal service. Second, a Google identity authorizes Compute, IAP and Storage API requests made by that terminal process. Third, SSH authenticates the guest operating-system login on a GPU worker. Passing one does not establish the others. The project's `approval.json` records experimental authorization and assignments; it is not a Google credential or a ChatGPT permission override.

The intended academic host is VM `dev`, project `pvd-dev-232`, zone `us-central1-a`, Linux user `pvd2112_columbia_edu`. The GPU resources belong to **`mantra-477901`**, not the CPU host's project. Its existing attached workload identity is **`dev-vm@pvd-dev-232.iam.gserviceaccount.com`**. The recorded GPU identity is `jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com`; its current attachment and exact grants must be inspected before any worker-side change.

The existing `cloud-project --project jep` runner creates a project-specific environment and uses systemd for durable jobs. `project_profile()` and `project_environment()` in `infrastructure/cloud-dev/implementation/project.py` select the attached account, isolate `CLOUDSDK_CONFIG`, remove common inherited credential overrides, and reject a local ADC file in the job configuration directory. `cloud_job.py:run_job()` constructs that environment again for the child process. These primitives should be retained, not wrapped in a new credential daemon. [P1]

There are two integration gaps. The general profile defaults the resource project/zone to the **host** project/zone. Separately, the experiment collector at `scripts/full_data_prompt_20261107/collect_epochs.py` explicitly sets `ACCOUNT='pvd2112@columbia.edu'` and passes it to Compute, IAP/SSH and Storage commands. A human-account override defeats the intended workload-identity default. [P2]

The current `probe_identity.py:probe()` verifies the attached identity, obtains a short-lived token internally, and makes an API request for **the Columbia VM itself**. That is a useful host-authentication check, but it does not prove permission to operate a Mantra GPU. Its tokens are not returned in its receipt. [P3]

### Live observations, not proposed guarantees

On the Columbia VM during this preparation:

- The installed identity probe passed, observing `dev-vm@pvd-dev-232.iam.gserviceaccount.com`, host project `pvd-dev-232`, VM `dev`, a token lifetime of 2,680 seconds, and HTTP 200 for the host-instance API request. No token value was printed.
- At **2026-11-08 06:49:16 UTC**, an explicit read-only request for `jep-full-prompt-spot-2-20261107` in Mantra, authenticated as the attached Columbia account, failed: `Required 'compute.instances.get' permission` for the specified Mantra resource. Exit code was 1.
- That failed request is retained at `columbia-projects/jep/data/columbia-mantra-identity-spec-20261108/current-access.json`. This document does not claim current access to Mantra IAM policies or current GPU status.
- Codex CLI on Columbia reported **`Not logged in`**. Therefore the requested three independent reviews are not completed. See §8; no company-host credential was copied or used to manufacture those reviews.

The first observation establishes that the machine can obtain Google credentials. The second establishes that those credentials lack a required downstream permission. More browser-login retries do not repair that IAM grant.

## 2. Gap analysis

**Required claim:** An approved JEP job submitted on Columbia can inspect/control its approved Mantra worker and preserve its outputs without a human re-login or a copied credential.

**Current path (inspected):**

```text
JEP profile
  --job_identity--> project_environment()
  --attached account--> Google metadata credentials
  --authorized request--> Columbia Compute API: succeeds
  --same principal, Mantra target--> Mantra Compute API: permission denied
```

**First unsupported connector:** Authorization from the attached Columbia principal to the required Mantra resources. There is a separate caller-level inconsistency: the collector hardcodes the human account rather than consuming the runner's workload identity.

**Smallest counterexample:** With a functioning Columbia metadata token, run a read-only `instances describe` on the known Mantra worker. The response denies `compute.instances.get`. The existing host-only probe can remain green simultaneously. Hence `keyless_identity_verified=true` must not be interpreted as end-to-end Mantra readiness.

**Disposition:** Gap confirmed for the inspected downstream permission and explicit caller override. Full current Mantra IAM/SSH policy, storage permissions and network readiness remain unverified; no claim is made about uninspected grants.

## 3. Proposed mechanism

A service account is a Google identity for a workload, not a new human account and not a downloaded key. The VM metadata service supplies short-lived access tokens for its attached identity. Google authentication libraries and gcloud can obtain replacement tokens as needed. Google recommends this attached-account approach for workloads on Google Cloud and cautions against persistent human logins for unattended remote jobs. [G1–G4]

The proposed authorization change therefore does not copy the Columbia account's token to Mantra. The Columbia process obtains its own token and uses it to request the allowed resource operation. A GPU process uses the GPU's own attached identity for any API calls it makes. These identities can have different permissions.

**Proposed-change DAG:**

```text
Administrator-reviewed Mantra IAM bindings
  --grant approved operations--> existing Columbia service account

JEP project definition (small workload-target extension)
  --Mantra target + existing assignment reference--> runner/probe/collector
  --expected attached identity--> fail-closed workload checks
```

**Integrated DAG:**

```text
User-approved ChatGPT action
  --existing columbia-vm connection--> Columbia dev VM
  --existing cloud-project environment--> attached Columbia identity
  --Google-managed token--> scoped Mantra Compute / IAP / Storage permissions
  --IAP tunnel + separately authorized SSH--> approved Mantra GPU
  --native checkpoints over existing IAP route--> Columbia collector
  --create/read JEP objects--> verified Cloud Storage artifacts
```

The connector remains a control channel, not a transport for OAuth codes. The worker may be private-only; the current IAP-copy-to-CPU then CPU-to-Storage route remains valid. Credentials do not create network routes, so this proposal does not assume that a private worker suddenly gains outbound access to Storage.

### One source of configuration

Keep `target.gcp_project='pvd-dev-232'` and the host identity unchanged. Extend the **existing project definition** rather than introducing another registry. Proposed fields, not current implementation:

```json
{
  "workload": {
    "resource_project": "mantra-477901",
    "instance_manifest": "<existing approved task-assignment manifest>",
    "artifact_prefix": "gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_full_data_prompt_20261107/"
  }
}
```

`project_profile()` owns persistence of these fields under the existing project configuration. `project_environment()` continues to select `job_identity.service_account_email`; the collector reads that identity and the workload target instead of a hardcoded human `ACCOUNT`. Explicit instance/zone arguments come from the already-approved assignment manifest. Host identity and resource project must never be conflated.

The existing probe gains target checks; it does not become a token server. Its existing receipt can include host, observed principal, target resource, operation, timestamp and structured API result. Never include tokens, refresh credentials, authorization codes or private keys. No new database, background refresh loop or central credential registry is required.

## 4. Permission and trust boundary

An administrator with authority over the relevant Mantra resources applies the setup. The attached Columbia account must not grant permissions to itself. The account's home project may remain Columbia; cross-project resource authorization does not require moving or copying its identity.

| Operation | Proposed scope and implementation rule |
|---|---|
| Read an assigned worker | `compute.instances.get` on approved task workers; add only the project/zone lookup and operation-read permissions that the exact CLI path demonstrably needs. Do not infer readiness from list exit code alone. |
| Start/stop an assigned existing worker | A minimal custom role with the needed start/stop/get permissions at a supported resource scope, or an equivalently constrained reviewed binding. No runtime instance deletion, disk deletion, IAM mutation, service-account creation or unrestricted provisioning. Negative permission checks must establish the boundary. |
| Open its IAP tunnel | `roles/iap.tunnelResourceAccessor` scoped to the relevant instances, limited to SSH port 22 where supported. Keep existing private-network/firewall protections. |
| Authenticate to the guest | IAP is not SSH login. Inspect and retain the current guest-access mode. For metadata-key SSH, use a Columbia-generated host-specific private key and register only its public key on approved workers. Do not copy the private key from another VM. For already-enabled OS Login, use the required OS Login role and, where required, Service Account User on the worker's attached account; grant administrator login only when the execution path actually requires it. Do not enable OS Login project-wide as a side effect. |
| Preserve JEP artifacts | Create/get known objects only under the approved JEP prefix; preserve immutable-write preconditions. Avoid object-delete privileges. Supporting bucket-metadata permissions require an observed reason. |

The exact binding commands are deliberately not presented as applied or complete until the current SSH mode, CLI prerequisites, resource-level IAM support, organization restrictions and administrator's authority are verified. `roles/compute.instanceAdmin.v1` is not casually substituted for narrowly scoped lifecycle control: it can be substantially broader than start/stop.

Storage listing requires special care: an IAM `resource.name` prefix condition cannot make bucket-level `storage.objects.list` a prefix-only privilege. Prefer known object URIs/manifests so listing is unnecessary; if listing is genuinely required, use an appropriate verified storage boundary or explicitly accept the wider listing visibility. Do not claim a string prefix in application code is an IAM security boundary. [G5]

**Shared-host caveat:** Any sufficiently privileged process on the Columbia VM can potentially use its attached service account. Project venvs and gcloud directories reduce mistakes, not host-level privilege sharing. Reusing the existing identity is appropriate for this trusted academic development host. Introducing a second service account on the same host is not, by itself, an isolation boundary. Separately trusted/untrusted workloads require a separate compute boundary, outside this minimum change. [G2]

## 5. Credential renewal, duplication and maintenance

### Do not replicate bearer credentials

Back up and reproduce **configuration and authorization intent**, not a logged-in gcloud home directory. The target state contains no human Google refresh token and no downloaded service-account JSON private key in runtime paths. Do not store access tokens in command arguments, generated scripts, Git, logs, queues or cross-host archives. Google manages the signing keys for metadata credentials; client software renews short-lived tokens. [G1–G4]

Rebuilding Columbia means reattaching the authorized service account, redeploying the existing profile/runner, registering the new host's SSH public key if needed, and passing the readiness checks. It does not mean restoring someone else's OAuth login. Replacing a GPU worker similarly attaches its authorized workload identity and reestablishes task-specific access; changing the instance ID requires a new approved assignment, not editing a credential to impersonate the old machine.

### Remaining credentials are different and need different treatment

The ChatGPT connector's own runtime secret and SSH private key are not replaced by a Google service account. Keep those in their existing protected host-owned storage, with restrictive permissions and clear owner/re-enrollment procedure. Copy neither into portable GPU images. On replacement or suspected compromise, generate/re-enroll the affected connector/key and remove the old authorization after verified handover. This does not require adding Vault or a custom secrets product to the MVP.

Existing full-disk backups may already contain historical credential material. Do not call them sanitized, and do not delete them during this proposal. Treat them as sensitive, restrict access and retention, and separately inventory/revoke obsolete credentials after live dependencies have been retired. For new portable deployment artifacts, exclude user gcloud caches, local ADC files, private SSH keys, connector secrets and model-provider credentials. A clean replacement is preferable to copying an arbitrary authenticated home directory. [G6]

### Small maintenance routine

The official gcloud/client-library refresh behavior owns token renewal; no cron job copies or refreshes token files. Run target-readiness checks before a new job and after a host rebuild or IAM change. An access error reports the principal, intended resource and missing permission; it does not launch a browser login or fall back to Aether. Review the narrowly scoped bindings when the task's resource boundary changes or the work ends. Revoke the task grant when its access is no longer needed; retain independent worker shutdown deadlines during transitions.

## 6. Proposed contract and acceptance tests

**Claim:** Given an administrator-authorized workload identity and available Google/IAP/network services, an approved JEP job originating on Columbia performs only its permitted Mantra operations and preserves its outputs without human Google reauthentication or cross-host credential copying.

These are draft requirements, not claims of implementation. This proposal has not been promoted to an executable `ContractPackage`/`PairBlockPlan`; the accepted design and independent review are prerequisites under the contract skill. Do not introduce a repository-local replacement for the existing contract framework.

| Requirement | Existing owner to extend | Proposed positive and rejection evidence |
|---|---|---|
| R1 — Columbia-only route | Host profile and job launcher | Correct host/account passes; wrong host or explicit human-account override is rejected before workload operations. No Aether fallback. |
| R2 — Keyless identity | `project.py:project_environment` | A job with no user Google login obtains attached identity; environment/ADC override fixture is rejected. Secrets never enter receipts. |
| R3 — Real target authorization | `probe_identity.py:probe` plus target option | Columbia self-check and Mantra describe are reported separately. A host-HTTP-200/Mantra-403 case cannot be reported ready. Exit-0 plus CLI warning/empty-result cases cannot be reported success. |
| R4 — Scoped access | Administrator-owned IAM bindings + task manifest checks | Approved worker/storage canary succeeds; non-task resource permission checks deny mutation. No test stops an unrelated live VM. |
| R5 — Renewal and reconstruction | Google auth libraries + existing runner profile | An authorized call after the original token expiry succeeds without user input; a clean test-host rebuild passes without copied credentials. Metadata unavailability fails clearly. |
| R6 — Complete SSH path | Existing IAP/SSH implementation | IAP TCP establishment and guest `hostname`/write-read canary both pass. Successful Compute access but denied IAP, failed SSH or unreachable network are not conflated with invalid credentials. |
| R7 — Safe collector handover | Existing collector + native checkpoint manifests | New Columbia collector first verifies an existing artifact read-only, then takes exclusive ownership at an acknowledged boundary; duplicate advancement is prevented and prior evidence stays intact. |
| R8 — Correct failure boundary | Existing audit receipt | Preserve actual operation/error/exit status with redaction. A platform tool rejection is not mislabeled as Google IAM failure or silently retried through another connection. |

Focused implementation tests belong in `infrastructure/cloud-dev/tests/test_mantra_workload_identity.py` (proposed). Tests for collector argument construction belong beside the existing collector tests. Actual IAM, SSH, expiry and reconstruction checks need retained integration receipts; passing mocked unit tests cannot establish those effects.

### Worked accepted path (proposed)

An approved job reads its Columbia host profile and Mantra task manifest. The runner obtains its attached principal, verifies the expected host, then successfully describes the exact assigned worker. It opens the approved IAP/SSH route and retrieves an existing checkpoint. The CPU collector writes a new immutable object within the JEP prefix, reads it back and checks its SHA. It records principal/resource/checkpoint evidence without recording the bearer token. The next authorized API call after token expiry is refreshed through the existing client credential provider.

### Worked rejected path

The observed Columbia principal can describe Columbia but cannot describe the assigned Mantra worker. R3 reports the Mantra `compute.instances.get` denial and prevents allocation/launch. It does not ask the user for a code or claim the account needs an expired human login repaired. Separately, when a tool invocation itself is rejected, R8 records a tool-level refusal rather than inventing a Google response.

## 7. Minimum implementation and cutover

**Change set A — owner-approved setup:** inspect effective resource/guest-access policies, apply the minimal grants, register the Columbia SSH public key only if necessary, and prove a nonmutating end-to-end read. Preserve current worker identities and disks. This is an administrator action, not self-escalation by a runtime service account.

**Change set B — existing code only:** extend `projects/jep.json`/`project_profile()` with the workload target, keep host identity separate, extend the existing probe, and remove the hardcoded human account in the collector/owned launch path. Reuse the existing durable runner and secret storage. Deploy no new daemon or database.

**Change set C — verification and handover:** exercise a controlled canary, token renewal and restart/rebuild tests. If an old collector is still active, do not kill it blindly: verify the last sealed checkpoint and acknowledgements, transfer exclusive collector ownership at a safe boundary, and continue the same native training state. This inspection used no Aether tools and does not assert present status of that old collector. Any shutdown of a still-active old host service is a separately authorized cleanup action; do not leave it as the permanent academic dependency. Finally remove runtime reliance on human credentials; revoke/delete obsolete saved credentials only after verifying they are not used elsewhere and obtaining authorization.

**Retain:** Columbia dev VM, attached SA, Mantra workers, IAP, guest SSH mode, systemd runner, native checkpoint/state formats, Storage bucket, connector and its safety checks.

**Retire from normal operation:** human Google login on compute hosts, OAuth-code submission through chat, Aether orchestration, hardcoded human `--account`, and self-project-only readiness claims.

**Do not add:** custom token service, token-sync cron, token database, long-lived Google key files, Kubernetes, new VM fleet, cross-cloud federation, broad IAM administrator roles, or a new agent supervisor. Fresh worker provisioning in another zone remains the existing separately approved infrastructure workflow; it is not necessary to solve token renewal.

**Scope limitation:** This removes the recurring Google login/code-submission dependency. It does not guarantee GPU capacity, network reachability, automatic permission after revocation, or acceptance of every ChatGPT action. OpenAI's action-safety rules remain independent and must not be weakened or bypassed. [O1]

## 8. Three independent reviews: requested, not completed

The available Codex CLI on the Columbia VM was checked using its supported `login status` command and returned `Not logged in`. No authenticated alternative reviewer was found in the available tool discovery. No credential was copied from Aether, no new model-provider login was initiated, and no self-review is counted as an independent review. **Completed: 0/3.** This is a reviewable draft, not an approved implementation specification.

Retained briefs:

1. **Security/IAM reviewer:** test least privilege, host-wide metadata access, separation of IAP and SSH, storage-list/prefix limitations, admin/runtime boundaries, secret-free replication and non-bypass of platform controls. Require exact supporting API documentation and negative tests.
2. **Reliability/recovery reviewer:** challenge target probes, token-refresh assumptions, job restart/rebuild behavior, private-network dependencies, collector handover, current 403 counterexample and error classification. Reject any claim that credentials solve capacity or network failures.
3. **Minimality/contract reviewer:** trace each requirement to the existing owner and a positive/rejection test; remove new stores, redundant authorities and speculative features. Verify that plan prose is not misrepresented as a typed/executable contract or as completed runtime evidence.

Each reviewer should receive this frozen proposal plus cited source excerpts independently and return actual provider/run identity, inspected revision, concrete findings and a verdict. Do not promote this document to `Audited`, `Approved` or `Implemented` until the corresponding evidence exists. Reviewer-provider authentication is distinct from the Google workload identity addressed here.

## Sources and inspected baselines

[P1] Existing cloud host/profile/runner source at JEP commit `a6dea0c952b5f0948e49f8dd4aa06c769e00689c`: `infrastructure/cloud-dev/implementation/project.py`, `cloud_job.py`, `profiles/columbia.json`, `projects/jep.json`, `README.md`. Installed source inspected on Columbia; runner SHA-256 `94ce889e983707bf617a37bfb99173a6a3d3a88ad9eb7a8c71a8ce75015d30e1`.

[P2] `scripts/full_data_prompt_20261107/collect_epochs.py`, experiment commit `9b163a100362580f99722eecc63895420ecec3b1`: explicit human account and IAP collector path.

[P3] `infrastructure/cloud-dev/implementation/probe_identity.py` at the host baseline; installed SHA-256 `06a91b72f5d0e95f57dced4831acd3207270919243277c4696f5aeac2206d262`. Only verifies the configured host-instance API call, not Mantra.

Authoring basis: user's `technical-white-paper`, `gap-analysis`, `minimal-sufficient-design`, and the canonical `pvd232/agents` `contract` and `change-impact-analysis` skills. No existing system white paper was silently substituted for inspected implementation; the technical-white-paper item located in the user's files is an authoring skill.

[G1] Google, Authenticate workloads with service accounts: https://docs.cloud.google.com/compute/docs/access/authenticate-workloads
[G2] Google, Service-account best practices: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts
[G3] Google, ADC search order and attached service accounts: https://docs.cloud.google.com/docs/authentication/application-default-credentials
[G4] Google, gcloud authentication and remote-workload guidance: https://docs.cloud.google.com/sdk/docs/authenticate
[G5] Google, Cloud Storage IAM and prefix/list caveats: https://docs.cloud.google.com/storage/docs/access-control/iam
[G6] Google, Protecting developer/SSH credentials: https://docs.cloud.google.com/docs/security/bps-for-protecting-developer-credentials and https://docs.cloud.google.com/compute/docs/connect/ssh-best-practices/credentials
[G7] Google, IAP TCP permissions: https://docs.cloud.google.com/iap/docs/using-tcp-forwarding
[G8] Google, OS Login: https://docs.cloud.google.com/compute/docs/oslogin/set-up-oslogin
[O1] OpenAI, explicit action-safety blocks versus authorization/approval: https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt
