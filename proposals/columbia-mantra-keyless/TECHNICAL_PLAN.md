# Technical plan: finish the existing keyless execution route

**State: design proposed for review, not implemented.** The user has accepted the design direction; this PR requests review of the specification. Deployment still requires explicit, resource-scoped administrative authorization and integration evidence. This Markdown is not a generated `ContractPackage` or an executable `PairBlockPlan`.

## Outcome and minimum design

Use Columbia VM `dev` and its existing attached service account to operate the approved Mantra workers and preserve JEP outputs without recurring human Google logins. Reuse the existing runner, Google metadata credentials, IAP/SSH, collector, checkpoint formats and storage. Extend their existing owners rather than introducing a new credential-management product.

The three changes are: **authorize the destination; align the callers; verify and hand over the complete route.** A bare IAM change does not repair the collector's explicit human account, and a caller change does not create missing permissions.

### Fixed boundaries

- Host project: `pvd-dev-232`; host: `dev`; attached principal: `dev-vm@pvd-dev-232.iam.gserviceaccount.com`.
- Resource project: `mantra-477901`; workers and zones come from the existing approved assignment manifest.
- Existing recorded GPU identity: `jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com`; verify actual attachment before relying on it. Do not change it as part of this proposal by default.
- Runtime credentials: attached-account short-lived tokens, obtained through Google-supported clients. No human refresh tokens, copied login caches or downloaded service-account keys.
- No Aether orchestration or credentials, new GPU provisioning/quota requests, model-training changes, token broker, refresh daemon, credential database or new VM fleet.
- This is a trusted academic host: processes able to reach its metadata credentials share the attached identity's authority. Project directories and venvs are not isolation boundaries. Separate untrusted workloads require a separate design.

## Dependency 0: choose the implementation baseline

The installed host implementation is pinned at `a6dea0c952b5f0948e49f8dd4aa06c769e00689c`; the collector is at `9b163a100362580f99722eecc63895420ecec3b1`. The PR is based on `main` at `9ae8379b2ad134561c1d52e61c34f74bc3304dc1` and deliberately carries **documentation only**. The earlier proposal branch also included an unmerged host installation and must not be merged wholesale just to submit this specification.

Before implementation, confirm the owning infrastructure branch/PR and current installed source. Reconcile or stack the small repair on that owner explicitly. Do not claim a repository-relative implementation file exists on `main` merely because it is installed on the VM. Source links below pin the inspected definitions.

## Change A — scoped authorization, applied by an administrator

Inspect effective permissions and the actual guest-access mode for the approved workers. An administrator authorized for the relevant resources—not the runtime service account granting itself privileges—reviews and applies only the necessary bindings.

| Capability | Minimum intent; prerequisite to exact grant |
|---|---|
| Inspect assigned worker | `compute.instances.get` for the approved task resources; add only demonstrated project/zone/operation lookup prerequisites required by the chosen CLI |
| Existing-worker lifecycle | Start/stop approved instances with the required operation-status reads; no runtime disk/instance deletion, IAM administration or general provisioning |
| IAP tunnel | Relevant instance-scoped IAP access, port 22 restriction where supported; retain existing firewall/private-network controls |
| Guest login | Retain current metadata-key SSH or OS Login mode; authorize that path explicitly rather than treating IAP as SSH authentication |
| Artifacts | Create/get known immutable objects at the approved JEP storage boundary, with only demonstrated metadata prerequisites; no default delete permission |

Use the narrowest supported resource binding/custom role or equivalent constrained policy. Verify the complete API action set before declaring it sufficient. Do not substitute project-wide Editor or unqualified `roles/compute.instanceAdmin.v1` for limited lifecycle control. If a narrower scope cannot represent a necessary operation, record that exact exception for administrator review; do not silently broaden it.

For metadata-key SSH, generate a host-specific private key on Columbia and register its public key through the authorized setup path. Specify the key explicitly in the eventual invocation, retain host-key verification, and verify whether the chosen `gcloud compute ssh` path tries to update metadata. Any such permission is a deliberate setup/runtime decision, not an implicit grant. For already-enabled OS Login, verify its required roles, service-account attachment prerequisites, and guest privilege requirements. Do not enable OS Login project-wide or grant unrestricted guest sudo as a side effect.

Storage `resource.name` prefix conditions do **not** make bucket-level `storage.objects.list` prefix-only. Prefer known URIs and manifests so listing is unnecessary; if listing is necessary, verify a suitable storage boundary or explicitly review the wider visibility. Local path checks are not IAM enforcement.

**Acceptance:** a nonmutating known-worker describe; authorized IAP plus guest identity check; a task canary write/read; and effective-permission negative checks for unrelated mutation. Never test denial by attempting to stop an unrelated live VM. Save binding changes/versions, principal, operations and results, without tokens. Stop on unresolved IAM, guest-access or network prerequisites.

## Change B — extend the existing configuration and callers

### Proposed configuration delta

Keep the host's `target.gcp_project` unchanged. Add the following nonsecret workload object to the existing JEP project definition, owned by `project_profile()`:

```json
{
  "workload": {
    "resource_project": "mantra-477901",
    "instance_manifest": "<existing approved task-assignment manifest>",
    "artifact_prefix": "gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_full_data_prompt_20261107/"
  }
}
```

These are **proposed fields**, not deployed schema. `resource_project` is one project-ID string; `instance_manifest` is one reference to the already-owned assignments, not a duplicate worker list; `artifact_prefix` is one approved storage destination. `project_profile()` validates and persists them inside the existing project profile. The probe/collector consume those resolved values. There is no new configuration store.

| Existing owner | Planned bounded change | Behavior retained |
|---|---|---|
| [JEP project definition](https://github.com/pvd232/JEP/blob/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev/projects/jep.json) and [`project_profile()`](https://github.com/pvd232/JEP/blob/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev/implementation/project.py) | Separate workload destination from host target; resolve existing assignment reference | CPU host/principal, project isolation, resource caps and current job interface |
| `project_environment()` / `cloud_job.py:run_job()` | Keep attached identity, sanitize inherited credential overrides, reject forbidden credentials in runtime configuration, verify actual SDK identity | No global credential deletion; isolated `CLOUDSDK_CONFIG`; existing durable execution |
| [`probe_identity.py:probe()`](https://github.com/pvd232/JEP/blob/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev/implementation/probe_identity.py) | Add separately reported actual-target readiness checks | Host identity check and secret-free receipt |
| [`collect_epochs.py`](https://github.com/pvd232/JEP/blob/9b163a100362580f99722eecc63895420ecec3b1/scripts/full_data_prompt_20261107/collect_epochs.py) and owned launch callers | Remove hardcoded human account; obtain the expected attached principal/workload target from the existing profile | Instance-ID/lease checks, immutable artifacts, checksum verification, task-only stop |

The collector must not accept an unvalidated human account override. The inherited environment is sanitized; an explicit incompatible job configuration is rejected. This distinction matches the current environment owner rather than promising it intercepts arbitrary shell commands. Verify Google client credential discovery in the real environment; do not assume setting `CLOUDSDK_CORE_ACCOUNT` alone controls every SDK.

No command may print/copy tokens, authorization codes, refresh credentials or private keys. Error receipts contain timestamp, host, expected/observed principal, exact nonsecret resource/operation, exit/API status and redacted diagnostics. A tool refusal is not reported as a Google response.

### Proposed contract obligations and focused tests

The test paths/names below are planned additions, not currently passing tests. Reuse the repository's existing test framework; do not create a second contract schema or status database.

| ID | Requirement and implementation owner | Proposed success / rejection test |
|---|---|---|
| R1 | Runner verifies Columbia host and attached identity | `test_expected_host_identity` / `test_wrong_host_or_human_account_rejected` |
| R2 | Profile keeps host and workload targets distinct | `test_mantra_workload_keeps_columbia_host` / `test_missing_or_conflicting_target_rejected` |
| R3 | Probe proves actual required destination operations | `test_host_and_target_results_separate` / `test_host_200_target_403_not_ready`; also reject exit-zero warnings/missing result |
| R4 | Collector uses profile identity, not a hardcoded human account | `test_collector_uses_expected_principal` / `test_explicit_human_override_rejected` |
| R5 | Runtime cannot depend on portable bearer credentials | `test_attached_identity_without_user_login` / `test_local_adc_or_credential_override_rejected`; assert redacted logs |
| R6 | Durable renewal and reconstruction work through official clients | Actual post-expiry API call and clean-host reconstruction receipts; mocks are not sufficient |
| R7 | IAM/IAP/SSH/storage boundaries are independently verified | Authorized task canaries and nonmutating negative permission checks; no live unrelated-worker destructive test |
| R8 | Collector handover preserves checkpoint ownership and shutdown | Fault-injected graceful handover, no duplicate advancement, unchanged last verified checkpoint, independent shutdown retained |

Place configuration/probe tests in proposed `infrastructure/cloud-dev/tests/test_mantra_workload_identity.py`. Place collector argument and handover tests beside its existing tests on the reconciled implementation baseline. Cover effective config, real principal and destination separately; do not compress them into a single ambiguous `ready=true` claim.

## Change C — live verification and collector cutover

Perform tests in this order: host/principal → known target read → IAP tunnel → SSH guest check → storage canary/round-trip → read-only recovery of an existing checkpoint → controlled lifecycle/shutdown canary → long-lived renewal → reconstruction. Keep permission setup independent from any capacity allocation.

For renewal, record the original credential lifetime without its value, then verify an authenticated call after expiry with no user input. Do not promise a fixed completion time or infer refresh from a short preflight. For reconstruction, deploy on an explicitly authorized clean test host using configuration and attached identity, not restored login caches. A normal reboot proves less than a clean-host rebuild; report them separately.

### Handover safeguard discovered during author inspection

The old collector's `monitor()` executes `stop()` in a `finally` block. Therefore **stopping that collector is not a safe neutral handoff operation**: it can shut down a worker still training. This source fact must be addressed before migration, not hidden behind “stop the old service.”

Choose the smallest safe route at cutover: normally allow the old assignment to finish, collect its sealed artifacts, and start the next assignment under Columbia. If live migration is necessary, first implement/review a deliberate handoff path that relinquishes only the collector's ownership without executing the normal failure-shutdown branch. Test it with simulated interruption and stale acknowledgements before using it. The new collector must not publish acknowledgements or issue stop commands until it owns the assignment. Preserve the independent worker poweroff deadline throughout. Do not kill the old collector blindly or disable shutdown protection broadly.

Retirement of a still-running old-host service requires separately authorized cleanup on that host; this PR performs none and assumes no current live state. Columbia becomes the only normal academic orchestration host. Do not leave Aether as a permanent fallback.

### Rollback

Before cutover: leave the existing execution untouched; revert only the candidate configuration/code and remove only the newly added bindings identified by their exact change receipt. Do not revoke shared grants or delete credentials used elsewhere.

After cutover: stop new submissions, preserve the last verified checkpoint and native resume state, and keep shutdown protection. Roll back only the newly deployed identity/collector changes after the current owner has safely relinquished control. Do not restore copied human tokens or silently route work to Aether. If neither controller can operate safely, preserve evidence and stop the affected task worker through its authorized deadline rather than duplicate control.

## Credential maintenance and scope limits

Google clients own access-token renewal. Back up nonsecret configuration and reviewed authorization intent, not gcloud login databases. Existing full-disk snapshots may contain secrets; retain/restrict them as sensitive until inventory and authorized retirement, rather than claiming they are sanitized. New portable images exclude user credential caches, ADC files, private SSH keys and connector/provider secrets.

The connector's runtime secret and SSH key have their own protected host storage and replacement/re-enrollment procedure. A Google service account does not replace them. Model-review authentication is another independent dependency; missing Codex login must not become a reason to copy provider credentials.

This change removes routine Google OAuth-code submission through chat. It does not guarantee cloud capacity, network access, recovery after arbitrary IAM revocation, or acceptance of every ChatGPT tool action. Platform safety controls remain in force.

## Exit conditions and review scope

Accept implementation only when R1–R8 have their stated unit/integration evidence on the approved source, all three independent reviews are resolved, and the administrator-approved grants plus handover are verified. A document approval, mocked success, or request to a reviewer is not completion evidence.

The contract skill remains the owner of a future typed package/PairBlock plan when implementation is materialized on the selected baseline. This proposal deliberately avoids adding a local substitute schema. The directory-README and gap-analysis skills govern orientation and diagnosis; the canonical contract/change-impact planning conventions govern owners, dependencies and acceptance. No exact `technical-planning` skill was found in the inspected skill inventory, so no use of an unlocated skill is claimed.

## Primary references

- [Attached service-account authentication](https://docs.cloud.google.com/docs/authentication/set-up-adc-attached-service-account)
- [Service-account security and host trust](https://docs.cloud.google.com/iam/docs/best-practices-service-accounts)
- [IAP TCP forwarding and SSH prerequisites](https://docs.cloud.google.com/iap/docs/using-tcp-forwarding)
- [Cloud Storage IAM and prefix/list limits](https://docs.cloud.google.com/storage/docs/access-control/iam)
- [Protecting developer credentials](https://docs.cloud.google.com/docs/security/bps-for-protecting-developer-credentials)
- [App troubleshooting: safety blocks are distinct from provider authorization](https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt)
