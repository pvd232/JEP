# Columbia-to-Mantra workload identity

This directory contains the proposal, evidence and review instructions for running JEP jobs from the Columbia VM without recurring human Google logins.

**Decision proposed:** reuse the service account already attached to Columbia, authorize its required Mantra operations, and make the existing runner and collector consistently use that identity. Do not build a credential broker, copy user login caches, or add long-lived Google keys.

**This is a proposal-only PR.** It does not change IAM, install code, allocate GPUs, migrate a collector, or authorize bypassing a tool refusal. Merging these documents does not deploy the design. Independent review completion is tracked separately in [REVIEW.md](REVIEW.md).

## Read this packet

| File | Responsibility |
|---|---|
| [GAP_ANALYSIS.md](GAP_ANALYSIS.md) | Inspected current path, two distinct failures, counterexamples and evidence limits; contains no proposed repair |
| [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md) | Bounded design, exact code owners, implementation order, acceptance tests, handover and rollback |
| [evidence.json](evidence.json) | Redacted observed identities, API outcomes and pinned implementation references |
| [REVIEW.md](REVIEW.md) | Three independent reviewer assignments, acceptance rules and current execution status |

The flow is **observed gap → proposed change → implementation evidence → operational handover**. Reviewer comments can challenge any step; an approval of this document is not evidence that a cloud permission or recovery test has passed.

## What changes

Columbia remains VM `dev` in `pvd-dev-232`. Its existing attached principal remains `dev-vm@pvd-dev-232.iam.gserviceaccount.com`. Mantra remains the GPU resource project, `mantra-477901`.

```text
Approved terminal action
  → Columbia's existing job runner
  → Google's attached-workload credentials
  → explicitly authorized Mantra Compute / IAP / Storage operations
  → assigned GPU and verified checkpoints
```

The minimum change is a reviewed IAM setup, a small workload-target extension to the current configuration, consistent account selection in the existing collector, and a probe of the actual destination. Google credential renewal remains Google's client-library/CLI responsibility. The connector and SSH authentication remain separate.

No Aether execution, credentials or account migration is part of this proposal. No new database, refresh daemon, token-sync service, Kubernetes system, VM fleet or model-training change is proposed.

## Baseline and PR boundary

The implementation inspected on Columbia is at [host baseline `a6dea0c`](https://github.com/pvd232/JEP/tree/a6dea0c952b5f0948e49f8dd4aa06c769e00689c/infrastructure/cloud-dev), and the experiment collector is at [training baseline `9b163a1`](https://github.com/pvd232/JEP/blob/9b163a100362580f99722eecc63895420ecec3b1/scripts/full_data_prompt_20261107/collect_epochs.py). Those revisions are **not imported by this documentation PR**. Some inspected infrastructure is not on the PR's `main` baseline; implementation must explicitly choose/reconcile its owning branch rather than accidentally merging the whole installation.

This packet develops the [earlier accepted design proposal](https://github.com/pvd232/JEP/blob/0659e24e866969ea1fb57743b399d154ea01ef29/proposals/columbia-mantra-keyless-20261108.md). The current packet owns the PR's implementation plan; that earlier document is retained as design history, not a second runtime configuration.

## Review and validation

Read the gap before the plan. Check the pinned source links and recorded counterexample. Verify that each requirement in the plan names an existing owner and both an accepted and a rejected case. Keep source observations, proposals and live acceptance results separate.

There is no deployment command in this directory. Documentation checks should verify relative links, JSON validity and the PR's changed-file allowlist. Existing cloud-development unit tests are at the pinned host baseline; they are not claimed to validate this unimplemented change.

The design remains incomplete operationally until an authorized administrator grants the reviewed permissions, the real target/SSH/storage checks pass, renewal is demonstrated, and any collector is handed over safely. An OpenAI action refusal remains a separate failure and is never treated as a reason to route through another account or tool.
