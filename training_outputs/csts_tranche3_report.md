# Tranche 3: matched evidence-supervision controls

All three rating checkpoints were selected with validation and frozen before test scoring. Native CPU EVAL and independent metric workers verified the saved predictions. Cloud publication runs separately.

| Training sequence | Test Spearman | MSE, 0–1 | Condition ordering |
|---|---:|---:|---:|
| Ratings → ratings | 0.516796 | 0.129362 | 80.46% |
| Aligned evidence → ratings | 0.606654 | 0.112571 | 84.87% |
| Shuffled evidence → ratings | 0.537700 | 0.126089 | 81.13% |

The first phase uses the same comparison subset and answer mask. Every arm completes six epochs and transitions from its terminal weights. The rating phases share the original 24-epoch schedule and lower constant-rate continuation, with a 40-epoch ceiling and patience five in the continuation.

The JSON report includes both predeclared paired source-group bootstrap contrasts, retained evidence coverage, selected epochs, actual updates and native references. These are exploratory one-seed results. Independent Spanish JEP confirmation remains open.
