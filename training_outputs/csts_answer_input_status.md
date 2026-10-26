# Answer-as-input screen — 26 October 2026

**Frozen screen complete; trained answer comparator running.**

| System | Validation Spearman | MSE | FPR at 90.11% recall |
|---|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | **9.69%** |
| Cached answer, original condition | 0.735916 | 0.041714 | 16.70% |
| Cached answer, generic condition | 0.603559 | 0.061040 | 38.97% |
| Conditioned answers + trained projection | running | running | running |

All 1,830 validation comparisons are retained. Coverage is 909 two-answer pairs, 545 one-answer pairs, 376 neither-answer pairs. The original-condition frozen arm scores 0.723040 on two-answer pairs versus saved Qwen 0.788620 on those same pairs.

The trained candidate was declared before frozen scores: one bias-free 4096→128 projection on fixed Qwen+LoRA answer/fallback embeddings; seed 7; cosine-MSE; lr 0.001; batch 32; patience 5; ceiling 48 epochs / 600 fitting seconds. It uses the existing 6,980 training comparisons and native projection fitter. Qwen stays fixed. No baseline rerun, native control-head fit or test evaluation.

Both missing and rejected teacher answers retain the original passage and condition. The frozen screen reuses saved native scores on neither-answer pairs; the trained system applies its projection to every input, including fallbacks.

The first two arms are ineligible. Validation eligibility remains +0.005 Spearman with no more than one percentage point worse FPR or condition ordering. This cached extractive experiment does not replicate generated-proposition extraction or full Tu encoder fine-tuning.

Frozen source: `2540590c72dbd197addf40bfef3da66d91c52d93`. Trained follow-up source: `775b315f533acee2435d97d4cbeb599a4f11f524`. Controller PID **77573**, workspace `/home/machina/jep-csts-answer-input-20261026`; events `answer_input_results/projection_initial/events.jsonl`. Both code increments passed focused tests (7 + 11), Ruff, Pyrefly and independent review.

[Plan](../plans/csts-tranche-7-answer-input.md) · [Training runner](../csts_pilot/answer_projection_run.py)
