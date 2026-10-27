# GPT-6.1 Sol, max reasoning: jep-csts-v1

Status: **running**. Completed **2,240/2,430** test comparisons.

Model: `gpt-6.1-sol`; reasoning effort: `max`. Fixed archived zero-shot rubric; 64 items per fresh request, four requests at a time. The model receives row IDs, both sentences and the condition. Labels are joined after inference; tool use invalidates a batch.

Dataset: published jep-csts-v1, 2,430 test comparisons. Same frozen test bytes as the current encoder experiment. Earlier Sol max result: **0.8029168452 Spearman** on 2,620 earlier test comparisons. [Archived baseline](https://github.com/pvd232/JEP/blob/experiment/csts-jep-v1-full-propositions-20261027/training_outputs/csts_sol61_max_report.md).

[Current encoder score table](epoch_scores.md).
