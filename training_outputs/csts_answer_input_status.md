# Answer-as-input screen — 26 October 2026

**Frozen validation job running; pinned model loading. No new candidate scores yet.**

Focused checks: **7 tests passed; Ruff and Pyrefly passed.** Independent design/runtime review found no blocking findings.

Source: [`2540590`](https://github.com/pvd232/JEP/tree/2540590c72dbd197addf40bfef3da66d91c52d93). GPU controller PID **76866**; native workspace `/home/machina/jep-csts-answer-input-20261026`. Events: `answer_input_results/initial/events.jsonl`.

| System | Validation Spearman | FPR at ~90.11% recall |
|---|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **9.69%** |
| Cached answer, original condition | pending | pending |
| Cached answer, generic condition | pending | pending |
| Conditioned answers + trained projection | preparing | preparing |

All 1,830 validation comparisons remain. Saved Qwen scores are reused without rerunning the baseline. Accepted cached spans replace the passage input; missing/rejected answers retain the original passage and condition. Neither-accepted pairs reuse native scores exactly in the frozen arms.

Before seeing frozen-arm scores, one trained conditioned-answer comparator was declared: a bias-free 4096→128 projection, seed 7, cosine-MSE, learning rate 0.001, batch 32, patience 5, ceiling 48 epochs / 600 seconds. It reuses the standard native projection trainer and trains on the existing 6,980 training comparisons; the Qwen backbone stays fixed. Its projection applies to fallback inputs too. No new native control head is fitted.

This is a cached extractive answer-input experiment, not full generated-proposition extraction or Tu encoder fine-tuning. Validation alone determines eligibility; no new test scores are read. Each completed score will be published here.
