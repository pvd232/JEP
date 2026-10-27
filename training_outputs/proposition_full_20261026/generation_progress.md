## Proposition validation and full-training generation

Monitor: **running**.

Training inputs captured: **4,928/11,909**; missing inputs requested: **9,413**. The current training bank remains frozen.

Held-out sample: **128 validation source groups**, one passage-condition input per group. References and generated answers are kept outside training. Evaluation waits for the current GPU training run to finish.

| Proposition checkpoint | Held-out answer loss | Model-reviewed factual accuracy | Reviewed answers |
|---|---:|---:|---:|
| After 2 proposition-writing epochs | Pending | Pending | — |
| After 4 proposition-writing epochs | Pending | Pending | — |

Loss averages each answer's next-token cross-entropy, then averages answers. Factual checks use free-generated answers and two independent source-only model reviews; they report support, omissions, unsupported assertions and reviewer agreement. These measurements describe proposition writing and do not change the running experiment's stopping rule.

Earlier checkpoints were overwritten by the original trainer; epochs 2 and 4 have retained checkpoints. [Detailed status and results](proposition_validation.json).

Held-out reference review: **125/128** fully correct by both model reviewers; **0** flagged for unsupported assertions; reviewer agreement **99.2%**.
