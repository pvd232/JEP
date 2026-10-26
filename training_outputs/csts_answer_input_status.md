# Answer-as-input screen — 26 October 2026

**Both frozen arms complete and ineligible. One trained conditioned-answer projection is in preparation.**

Full validation cohort: **1,830 comparisons**. Each row retains **90.11% recall**. Saved Qwen scores are reused without a baseline rerun.

| System | Validation Spearman | MSE | FPR |
|---|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | **9.69%** |
| Cached answer, original condition | 0.735916 | 0.041714 | 16.70% |
| Cached answer, generic condition | 0.603559 | 0.061040 | 38.97% |
| Conditioned answers + trained projection | preparing | preparing | preparing |

Coverage: **909** pairs have two accepted answers, **545** have one, **376** have neither. On the two-answer subset, conditioned-answer Spearman is **0.723040**, versus **0.788620** for saved Qwen on those same pairs. Missing-answer fallback therefore does not explain the entire loss.

Accepted cached spans replace passage inputs. Missing/rejected answers keep the original passage and condition; neither-answer pairs retain saved scores exactly in the frozen screen. All comparisons remain.

Before candidate scores, one trained conditioned-answer comparator was declared: bias-free 4096→128 projection, seed 7, cosine-MSE, learning rate 0.001, batch 32, patience 5, ceiling 48 epochs / 600 seconds. It reuses the standard native projection trainer on 6,980 training comparisons; Qwen stays fixed. The learned projection also applies to fallback inputs. No new native control head.

This is a cached extractive answer-input experiment, not full generated-proposition extraction or Tu encoder fine-tuning. Validation alone selects candidates; no new test scores are read.

Frozen stage native-sealed successfully. **7 tests, Ruff, Pyrefly and independent review passed.** Source: [`2540590`](https://github.com/pvd232/JEP/tree/2540590c72dbd197addf40bfef3da66d91c52d93). Workspace: `/home/machina/jep-csts-answer-input-20261026`; artifacts: `answer_input_results/initial`.
