# Answer-as-input screen — 26 October 2026

**All three candidates missed the validation gate. Retain saved Qwen. Native stages completed; independent trained-output verification is finishing.**

| System | Validation Spearman | MSE | FPR at 90.11% recall |
|---|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | **9.69%** |
| Cached answer, original condition | 0.735916 | 0.041714 | 16.70% |
| Cached answer, generic condition | 0.603559 | 0.061040 | 38.97% |
| Conditioned answers + trained projection | 0.723444 | 0.050707 | 17.53% |

The trained projection selected **epoch 3** and stopped after **epoch 8**, following five nonimproving validation epochs. No baseline rerun, native control-head fit or new test evaluation ran.

Every candidate retains the full 1,830-row validation cohort. Coverage: 909 pairs with two accepted answers, 545 with one, 376 with neither. On the two-answer subset, conditioned frozen-answer Spearman is 0.723040 versus saved Qwen 0.788620.

Independent CPU verification reproduced both frozen arms exactly, with zero score replay error. Paired 2,000-draw source-group validation intervals for Spearman difference versus saved Qwen: conditioned [−0.057964, −0.036110]; generic [−0.206481, −0.152247]. These are validation diagnostics, not fresh-test or seed uncertainty.

The error review found accepted answers that remove relevant entities: horseback riders pursuing a bull and a bull rider both became “a bull,” yielding cosine 1.0. There are 68 exactly identical accepted-answer pairs; 17 have reference rating below 5. This quantifies one information-loss mechanism, not the entire deficit.

This experiment tests cached extractive answers, with original-passage fallback. It does not replicate reliable generated propositions or full Tu encoder fine-tuning. The projection trains on all 6,980 training comparisons while Qwen stays fixed; it also projects fallback inputs. Frozen arms instead reuse saved scores on neither-answer pairs.

[Sealed projection results and native references](csts_answer_projection_results.json) · [Plan](../plans/csts-tranche-7-answer-input.md) · [Code](../csts_pilot/answer_projection_run.py)

Sources: frozen `2540590c72dbd197addf40bfef3da66d91c52d93`; trained `775b315f533acee2435d97d4cbeb599a4f11f524`. Both increments passed focused tests (7 + 11), Ruff, Pyrefly and independent code review.
