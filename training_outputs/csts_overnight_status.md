# JEP overnight experiments — live status

**Deployment and preflight underway. No new score yet.**

| Comparator | Validation Spearman | Existing-test Spearman |
|---|---:|---:|
| Saved Qwen + LoRA | 0.782575 | 0.788505 |
| Archived LLM pair judge | — | 0.802917 |

Tranche 5 runs four correction heads against the saved Qwen predictions. A separate condition-query attention experiment with cached teacher-span supervision is being implemented and independently reviewed. Neither baseline is rerun.

Completed scores, native stages, and job identities will appear here. [Overnight execution plan](../plans/csts-overnight-20261026.md) · [Tranche 5 plan](../plans/csts-tranche-5-matched-baselines.md) · [IPED source check](../plans/csts-iped-research-20261026.md)
