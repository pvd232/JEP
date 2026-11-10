# JEP technical project briefing and agent handoff

Review the next scientific question with the user and define its relevance labels; preserve the two closed runs and their completed outputs.

Operational state checked **10 November 2026, 4:11 p.m. Eastern**. The initial execution request has been fulfilled. The current phase is scientific review after a completed pilot, a partial follow-up, and extraction of the reusable GPU provider.

The project aims to retrieve JEP testimony according to explicit harm or response criteria. Its scientific questions concern whether conditioning improves useful rankings and whether a constrained shared geometry improves scoring. The completed experiments establish a limited capability screen; independently judged Spanish JEP retrieval remains the target evaluation.

**Observed results**

| Study | Inputs and comparison | Observed result | Interpretation |
|---|---|---|---|
| Aspect-conditioned Qwen retrieval | Twenty authored English story families: four development, twelve primary, four reserve. Relevant candidates preserve the requested aspect across stories. | Primary pairwise accuracy: unconditioned 17.5%, short condition 74.1%, explicit definition 98.8%, development-selected paraphrase 99.8%. Definition and paraphrase both reach 100% on reserve families. | The frozen encoder follows explicit aspects on a structured synthetic screen. Ceiling performance motivates harder independent cases. |
| PSD restriction | Identical normalized, training-only 64-dimensional PCA features and loss; signed versus nonnegative diagonal weights. Fits use 64 or 256 cleaned C-STS labels and three PCA seeds. | On 128 reference pairs, PSD heads score Spearman 0.742–0.787; unchanged Qwen cosine scores 0.8327. | The paired heads show a possible regularization effect. The full encoder retains the strongest result. Cosine already defines a PSD kernel for each fixed condition. |
| Ethical-theory reasoning and layers | Fixed care/harm with Utilitarianism, Deontology and Care Ethics framings; released MET-D-Qwen3-4B weights. | All eighteen generated views hit the 96-token limit. Layer vectors were retained. | Useful reasoning views and a reasoning-to-encoder benefit remain unestablished. Layer separation measures framing sensitivity. |
| Directed response follow-up | Twelve authored incident families, 84 candidate responses, 48 queries. Six held-out families supply 24 test queries; each query ranks seven candidates. | Lexical Recall@1: query alone 33.3%, query plus criterion 75.0%. Both criterion rankings correct: 0% versus 66.7%. | A strong criterion-aware lexical control is available. The Qwen arm remains missing after L4 capacity admissions were exhausted. |

Pilot retrieval accuracy compares a relevant candidate against each distractor; random ordering gives 50%. Follow-up Recall@1 measures the top candidate. These metrics describe different tests.

The pilot conditions operationalize expected lives saved with equal person weights, informed and unpressured worker consent, and allocation of sixteen work hours among four equally responsible workers with equal hourly burdens. These are partial resemblance rules. Full ethical-theory definitions require further commitments.

The follow-up holds the incident and candidate pool fixed while changing the requested response criterion: completed specified response for the named party, or acknowledgment/voice. An example query explicitly names farmers and livelihood grants. Its answer key concerns beneficiary, response type and completion evidence. Expert judgments of reparative adequacy remain to be collected.

**Scientific boundaries and recommendation**

“Criterion” occupies the existing natural-language condition input. The planned Qwen follow-up retains the existing prompt and encoder. The executed work contributes an authored diagnostic and a narrow sign-constraint ablation. Research novelty remains an open claim.

Keep human judgments, audited LLM scores and authored synthetic expectations separate. The C-STS reference partitions were previously examined and provide exploratory evidence. Current moral retrieval cases are English and synthetic. Spanish and Colombian cultural transfer require independent assessment.

The restored adapter bytes were verified. Historical numerical replay differed by up to 0.016163 cosine after a runtime change. Compare methods within the pilot runtime: PyTorch 2.9.1+cu129, Transformers 4.57.1 and PEFT 0.17.1. Preserve historical prediction bytes as separate evidence.

The restorative translation diagnostic was post hoc: ordinary cosine retrieved the authored repair at rank one in 100% of cases; leave-one-family-out translation achieved 83%. Harm and response form a directed, many-to-many relation. Topic and valence controls, response coverage, beneficiary and implementation status require separate judgments.

Recommendation: **revise the scientific claim and pursue independently judged Spanish retrieval**. The first decision is whether relevance means a documented response for a particular victim or an analogous remedy across victims. Those tasks need different answer keys. The existing follow-up implements documented response linking.

Ten literature agents completed a bounded scoping review: 105 lane records, deduplicated to 98 sources, including five official or normative sources. Reuse the [synthesis](SYNTHESIS.md), [source ledger](merged_studies.json), and [review protocol](REVIEW_PROTOCOL.md). The ledger records inspection depth; 98 sources span several evidence types. Conditional embeddings, moral spaces, reasoning transfer and analogy probes have close predecessors. Assess a specific novelty claim against those sources.

**Execution and retained evidence**

All recorded jobs for both runs are terminal. Their statuses agree between the durable runner's list and individual status queries. Both execution locks are free. Earlier controller errors coexist with completed retained measurements; use artifact verification and cleanup receipts to classify the scientific run.

| Run | Current state | Retention and bounds |
|---|---|---|
| `moral-geometry-20261110` | `complete` | Fifty sealed files verified through VIPER. The single GPU used 24 minutes; its VM and disk deletion were verified. Recovery automation is disabled. Deadline was 8:00 a.m. Eastern; two recovery launches were consumed. |
| `moral-followup-20261110` | `closed_partial_capacity_blocked` | CPU controls and literature retained. Publication receipt records 57 verified files. Resource ledger records zero GPU allocations and zero GPU seconds. Fifteen create intents are terminal failures or reconciled absent. Deadline was 10:30 a.m. Eastern; two recovery launches were consumed. |

Use each run's `publication.json` as the publication authority. Both deadlines have passed. Preserve the closed states, consumed admissions, frozen inputs and recovery counters. A fresh experiment requires a new run directory and a specification with a current deadline and budget.

The [pilot report](../../training_outputs/moral_geometry_20261110/README.md), [exact results](../../training_outputs/moral_geometry_20261110/results.json), [metric verification](../../training_outputs/moral_geometry_20261110/metric_verification.json), [follow-up report](README.md), and [CPU results](benchmark_v2/CPU_REPORT.md) contain the scientific evidence and visualizations. Five original code reviews and five method-ideation reviews were completed.

**Reusable execution provider**

The user chose a reusable skill as the current owner of GCP execution. VIPER remains the separate provenance publisher.

- Installed skill: [Run GCP L4 Job](https://chatgpt.com/skills?skill_id=6af37acf125881919765af9fc2d934ab).
- Canonical [instructions and scripts](https://github.com/pvd232/agents/blob/31428a22c03fce5d634d2e4c23417570340002a0/skills/run-gcp-l4-job/SKILL.md): `pvd232/agents`, revision `31428a22c03fce5d634d2e4c23417570340002a0`.
- JEP implementation baseline: `efd682ef80c97f40c29b17f6b4b032888af181db`, branch `experiment/moral-geometry-pilot-20261110` in `pvd232/JEP`.
- JEP owns the [workload adapter](execution/controller.py), [explicit configuration and source pins](execution/gcp_provider.json), worker and artifact collector. Shared capacity policy lives in the skill package.

The provider reconciles durable jobs and resources before admission. It ranks eligible placements by `obtainability * estimated_spot_seconds`, defaults to one Spot L4 on `g2-standard-4`, collects and verifies worker bytes, then deletes the exact recorded VM and disk. A verified host-memory preflight failure can admit `g2-standard-8` after atomic archival, cleanup and budget checks. Both host sizes retain the same GPU memory. Cumulative GPU time and the individual worker lease have separate limits.

Advice expires after 120 seconds. The last live three-region smoke found high forecasts in Taiwan and Tokyo with missing existing private egress; Iowa was eligible with a lower score. Refresh advice before future admission. The provider discovers existing private networking and preserves existing infrastructure.

Validation passed: **49 focused tests: 44 provider regressions and five JEP adapter checks**. Provider Pyright ran in strict mode; adapter Pyright ran in basic mode. Ruff, live planning and closed-run resume preservation checks passed. Personal and Columbia exports match the published source. Partial archive-copy recovery and legacy receipts after worker deletion have explicit regressions. The smaller host's actual Qwen loading path remains to be measured.

Two deployment checks remain pending: the full automated skill profile encountered a CLI filesystem sandbox startup error involving NETLINK_ROUTE; the managed Mac export awaits a working relay. Personal and Columbia deployments are verified.

**Canonical host and paths**

Use `columbia-vm`: VM `dev`, project `pvd-dev-232`, zone `us-central1-a`, Linux user `pvd2112_columbia_edu`. Use the existing attached identity. GPU configuration targets project `mantra-477901` and the existing `jep-gpu-jobs@mantra-477901.iam.gserviceaccount.com` service account. Preserve the dev VM, unrelated infrastructure, and the color/Qwen worktrees.

```text
Worktree: /home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110
Pilot: /home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110
Follow-up: /home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-followup-20261110
Provider receipts: /home/pvd2112_columbia_edu/columbia-projects/jep/data/provider-extraction-20261110
Shared scripts: /home/pvd2112_columbia_edu/.local/share/agent-skills/run-gcp-l4-job/scripts
```

Read `state.json`, `events.jsonl`, `resources.json`, and `publication.json` in the applicable run. Provider receipts include `COMPLETION.json`, `jep_smoke.json`, and `live_plan_smoke.json`. Return bounded summaries. Resolve actual job IDs from the run state:

```sh
cloud-project --project jep list
cloud-project --project jep status JOB_ID
```

API errors leave job/resource state unknown. Inspect surviving processes and locks; a stale heartbeat is an inspection trigger. Keep unknown hosted run IDs null. Enter through the provider's nonblocking lock and preserve a healthy owner. Reporting and publication consume retained artifacts through separate paths.

Public JEP Git fetch works. Publish through the connected GitHub tools, then fetch and verify the local checkout. Preserve existing credentials and IAM. Columbia lacks `rg`; use `git grep` or Python file inspection. Inspect durable-runner documentation before submission; `cloud-project run --help` treats `--help` as a command.

**Pinned model and scientific protocol**

Reuse `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`, and the existing cleaned-C-STS condition-first adapter. Its source revision is `925d26ea2040161d3b5847984f705281761de9cd`, trial `A_condition_first_seed10`, adapter SHA256 `84458c9ae1bea5f86a37fc77dd949bccd6f5982c31d5e462aec2ee81f37134cc`. The context limit is 160 tokens. Resolve retained checkpoint locations from `qwen_selection.json` and `encoder_identity.json`.

Original charter: [EXECUTION.md](../../plans/moral_geometry_20261110/EXECUTION.md), adjacent `protocol.json`, and [design_v2.json](../../plans/moral_geometry_20261110/design_v2.json). Original protocol SHA256: `10022159160ebb7b8f66e9159e736512b7421a725c38df2c52278bf5e4f98e67`. Follow-up bounds live in its run's `design_v2.json` and repository [protocol](FOLLOWUP_PROTOCOL.json).

**Next agent's immediate sequence**

1. Read the reports, synthesis and canonical states. Treat existing execution and publication as closed; reuse completed compatible stages.
2. Review the target relation and explicit ethical-theory definitions with the user. Define expected ranking changes, factual support, uncertainty, and criterion-specific invariants before authoring an answer key.
3. Propose a fresh family-held-out Spanish evaluation with independent relevance judgments. Keep conditioned Qwen cosine, a criterion-aware lexical retriever and structured extraction as comparison methods. Fit/PCA/calibrate on training data, select on development data, and reserve held-out labels for evaluation. Carry fresh compute bounds in a new specification when execution becomes the task.

Use concise affirmative prose and Response Muzzle. Keep scientific claims tied to measured outputs and inspected literature. The next agreed relevance definition provides the answer key for a defensible test of useful JEP retrieval.
