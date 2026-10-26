# Answer-as-input screen — complete

**Retain saved Qwen. All three candidates missed the validation gate. Independent verification passed; GPU experiments are stopped. No new test evaluation ran.**

| System | Validation Spearman | FPR at 90.11% recall |
|---|---:|---:|
| **Saved Qwen + LoRA** | **0.782575** | **9.69%** |
| Cached answer, original condition | 0.735916 | 16.70% |
| Cached answer, generic condition | 0.603559 | 38.97% |
| Conditioned answers + trained projection | 0.723444 | 17.53% |

The trained comparator selected epoch 3 and stopped after epoch 8 through patience 5. All 1,830 validation comparisons were retained. The saved baseline was not rerun.

The error review found accepted answers that erase relevant entities and relations. This cached extractive answer-input construction lost accuracy; reliable generated propositions and full Tu encoder fine-tuning remain untested.

[Full report, error examples and research direction](csts_answer_input_report.md) · [Verification](csts_answer_input_verification.json) · [Native trained results](csts_answer_projection_results.json) · [Plan](../plans/csts-tranche-7-answer-input.md)
