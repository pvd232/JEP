# Checked propositions and LoRA — live results

**authentication_required — waiting_for_google_cloud_sign_in**. Updated Oct 26, 2026, 10:55 AM EDT.

Google Cloud requires interactive sign-in renewal. Existing local proposition generation continues; native sample, adaptation and test stages await clean owner checks.

Full training/development generation: **2,112/17,334** accepted structural records; 0 preserved failed attempts. Capture: running. Provider latency has varied; no fixed ETA is asserted.

Source sample: awaiting_clean_owner_checks. Adaptation: awaiting_clean_owner_checks. Held-out test: not_released.

## Audit evidence and limits

| Development audit | Faithful decisions | Severe unsupported assertions | Gate |
|---|---:|---:|---|
| Original cached spans, initial sources | 73/120 | 2 | Descriptive comparator |
| Generated propositions, initial policy | 115/120 | 1 | Failed |
| Revised frozen policy, fresh disjoint sources | 58/60 | 0 | Passed |

Each audit used source-sampled groups and two independent model reviewers. Each reviewer saw at most one passage from a source group and saved source-only references before reviewing candidates. Reviewers saw no ratings or companion passages. The initial old/new candidates were randomly labeled A/B; fresh candidates used the opaque label P. This is a model-assisted development check, not human expert validation or a guarantee of population fidelity. Exact quotations are checked separately from semantic fidelity.

Audit records, source-only references, blinded judgments, failures and the hash-bound gate are preserved in [proposition_audit](proposition_audit/). The native runs preserve checkpoints, input identities, epoch traces and asynchronous publication receipts. Runtime failures are retained separately from statistical results.


The source sample compares old spans with blind-screened generated v1 answers, changing both generation and screening. It is a development diagnostic. The revised full bank uses the separate frozen v2 policy. Native validation alone chooses eligibility and the held-out test is evaluated once only for an eligible frozen candidate.

Operator source: `d5b7e513e7067538159aaffeb8d2ce463b845739`. Native source: `965aeb48be6f6e4f71b927757191956cbb3fb867`. Original capture source: `8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb`. Detailed live state: [csts_tranche8_results.json](csts_tranche8_results.json). Native artifacts seal locally and queue asynchronous cloud promotion.
