# User-stopped LoRA continuation

The user requested training stop after seven completed epochs. The native training attempt remains operator-interrupted. Its validation-selected epoch-5 checkpoint was preserved before test access, then sealed by a separate native BUILD. Its SHA-256 is `1be3cedbeacb494f46010d447564144a7f499d2dc8b174029107ff81651bbea3`.

| Measurement | Value |
|---|---:|
| Selected epoch | 5 |
| Validation Spearman | 0.776790887947513 |
| Test Spearman | **0.7788823829272487** |
| Test MSE, 0–1 | 0.072817277752418 |
| Condition ordering | 91.7625% |
| Test comparisons / source groups | 2620 / 1241 |

GPU BUILD captured fixed-checkpoint predictions. Native CPU EVAL and independent metric workers passed. The checkpoint sealing, prediction capture and EVAL took 30.8, 261.5 and 63.6 seconds respectively, including local native verification. Cloud publication is queued independently; scores and subsequent experiments do not wait for it. The operator-stop selection and complete native references are retained in the adjacent evidence folder.

The earlier one-epoch LoRA result was 0.7021695526490561. The continued checkpoint improves by 0.0767128302781926 Spearman on the same benchmark. Training was stopped by the user; this does not establish convergence or a stationary minimum.

Measurement code: `5f842c8f7915685f7d020ee6f045734151363ff4`. Native VIPER core remains pinned and unchanged.
