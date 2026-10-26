# Answer-as-input screen — 26 October 2026

**First frozen-arm score available. Generic arm running; trained conditioned-answer projection in preparation.**

Full validation cohort: **1,830 comparisons**. Each completed row retains **90.11% recall**. Native Qwen scores are reused; the baseline was not rerun.

| System | Validation Spearman | MSE | FPR |
|---|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | **9.69%** |
| Cached answer, original condition | 0.735916 | 0.041714 | 16.70% |
| Cached answer, generic condition | pending | pending | pending |
| Conditioned answers + trained projection | preparing | preparing | preparing |

The first arm misses the validation gate. Its condition-ordering accuracy is **89.04%**. The other frozen arm remains running.

Accepted cached spans replace passage inputs. Missing/rejected answers keep the original passage and condition; neither-accepted pairs retain saved baseline scores exactly for the frozen screen. Every comparison remains.

Before seeing candidate scores, one trained conditioned-answer comparator was declared: bias-free 4096→128 projection, seed 7, cosine-MSE, learning rate 0.001, batch 32, patience 5, ceiling 48 epochs / 600 seconds. It reuses the native projection trainer on 6,980 training comparisons; Qwen remains fixed. The learned projection also applies to fallback inputs. No new native control head.

This is a cached extractive answer-input experiment, not full generated-proposition extraction or Tu encoder fine-tuning. Validation alone selects candidates; no new test scores are read.

Focused checks: **7 tests passed; Ruff and Pyrefly passed.** Independent review found no blockers. Frozen source: [`2540590`](https://github.com/pvd232/JEP/tree/2540590c72dbd197addf40bfef3da66d91c52d93). Workspace: `/home/machina/jep-csts-answer-input-20261026`; events: `answer_input_results/initial/events.jsonl`.
