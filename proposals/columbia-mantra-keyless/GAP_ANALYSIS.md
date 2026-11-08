# Gap analysis: Columbia workload identity → Mantra

**Disposition: confirmed gaps; exact effective Mantra policy and current worker state are unverified.** This diagnosis describes the inspected system, not the proposed repair. The retained observations are in [evidence.json](evidence.json).

## Claim 1 — actual destination authorization

An approved JEP job originating on Columbia must be able to perform its required operations on the assigned Mantra worker without a human Google login or copied credential.

### Observed path

1. The installed Columbia profile identifies CPU VM `dev` in `pvd-dev-232` and attached principal `dev-vm@pvd-dev-232.iam.gserviceaccount.com`.
2. [`project_profile()` / `project_environment()`](https://github.com/pvd232/JEP/blob/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev/implementation/project.py#L24-L94) select that principal, isolate the job's gcloud configuration, remove common inherited credential overrides, and reject a local ADC file in that configuration directory.
3. [`probe_identity.py:probe()`](https://github.com/pvd232/JEP/blob/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev/implementation/probe_identity.py) checks metadata identity and requests **the host instance in Columbia**, not a Mantra worker.
4. The installed probe returned the expected attached principal, a remaining token lifetime of 2,680 seconds and HTTP 200 for that host request. No token value was exposed.
5. A separate read-only request using the same principal for the known Mantra worker returned exit 1 and `Required 'compute.instances.get' permission` at **2026-11-08 06:49:16 UTC**.

```text
profile.job_identity
  → project_environment: attached principal
  → metadata credentials
  → Columbia host-instance GET: 200
  → Mantra assigned-instance GET: DENIED
```

**First unsupported connector:** the attached principal's authorization for the specified Mantra resource. This is a Google permission failure after successful credential acquisition. It does not establish whether a missing allow binding, an inherited restriction, or another effective-policy condition is the administrator's exact repair; no Mantra IAM policy inspection succeeded in this analysis.

### Counterexample

Keep the host probe green and issue the same read-only Mantra instance request shown in `evidence.json`. The operation fails. A consumer interpreting the host receipt's `keyless_identity_verified=true` as complete Mantra readiness would accept a configuration that cannot inspect its destination.

### Missing evidence

Effective Mantra IAM/organization policies, required CLI auxiliary permissions, IAP authorization, guest SSH mode, storage access, token renewal during a long-lived collector, and current GPU status are not established by the host probe. No instance lifecycle action was attempted for this diagnosis.

## Claim 2 — caller identity consistency

The job's Compute, IAP and Storage calls must use the intended workload identity rather than require an unrelated saved human login.

### Observed path

The runner supplies the attached account. However, [`collect_epochs.py`](https://github.com/pvd232/JEP/blob/9b163a100362580f99722eecc63895420ecec3b1/scripts/full_data_prompt_20261107/collect_epochs.py#L18-L80) defines `ACCOUNT='pvd2112@columbia.edu'` and supplies that explicit `--account` in its subprocess commands. The durable runner's environment does not remove an explicit command-line account choice.

```text
runner: attached account
  → collector: hardcoded human ACCOUNT
  → gcloud --account=pvd2112@columbia.edu
  → requires that host's human-account credentials
```

**First unsupported connector:** the collector constructs a different account argument instead of using the intended runtime principal. This code path can still fail after the attached principal's Mantra access is repaired.

**Counterexample (source-derived):** run that collector on a correctly authorized workload host with no saved human login. Its explicit account selection still asks for credentials that the proposed workload-only environment does not provide. This counterexample follows the inspected argument construction; it was not executed as a live collector in this analysis.

## Independent failure boundaries

The historical OAuth-code submission was reported rejected by the terminal-tool interface. That is neither proof of an invalid Google code nor the cause of the two code/IAM gaps above. An experiment `approval.json` is not a platform permission or Google credential. The current evidence cannot identify the internal rule behind the earlier tool refusal.

Similarly, successful Compute authorization does not prove IAP tunnel access, SSH guest authentication, network reachability, GPU availability or artifact write permissions. Each requires its own observing check.

## Repair obligation

A repair must establish authorized Columbia-to-Mantra operations, prevent the collector from overriding the workload identity with a human account, and verify the destination instead of only the host. It must not copy credentials, weaken IAM or tool controls, or claim that a passing mocked test proves a deployed cloud effect.

The chosen repair and its impact belong in [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md), not in this current-state diagnosis.
