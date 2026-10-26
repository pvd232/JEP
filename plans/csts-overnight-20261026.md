# JEP overnight execution: 26 October 2026

The user authorized completion of the reviewed experiment tranches and logical follow-ups while asleep. The objective is a verified improvement over the archived Qwen system, ideally reaching the archived LLM pair judge, or a specific research direction supported by the completed measurements. Scores are published as stages finish. Cloud promotion runs asynchronously.

## Comparators and fixed constraints

| System | Validation Spearman | Existing-test Spearman |
|---|---:|---:|
| Selected Qwen3-Embedding-8B + LoRA | 0.7825746597420997 | 0.7885050017660868 |
| GPT-6.1 Sol, max, direct pair judgment | No archived validation score located | 0.8029168452132416 |

The user's approximate 0.805 reference resolves to the archived 0.802917 test result. The LLM and Qwen archives match all 2,620 canonical test comparisons and 1,241 source groups. See [comparator provenance](csts-llm-comparator-provenance.md). The LLM judges a pair directly; Qwen supplies reusable single-passage embeddings.

Reuse sealed baseline predictions. Perform no baseline reproduction, new native-control-head fit, training-seed sweep, or invented Spanish JEP evaluation. Use the existing physical GPU VM. Create no new paid resources. Maintain seed 7, source-group separation, full comparison cohorts, validation-only candidate selection, frozen test thresholds, and the existing test-history disclosure.

## Execution sequence

1. Run reviewed Tranche 5, source commit `faa0ae537feea2333b5c245c9b23e0829729441c`: same-passage subtraction, population translation, population projection removal, and CASE-style subtraction, each with its specified small supervised head. Its four-arm eligibility and stop rule remain fixed. Budgets: training/validation extraction 90 GPU minutes, four fits 10 minutes each, conditional test extraction 30 minutes, analysis 30 CPU minutes.
2. Freeze and publish the Tranche 5 result. Inspect its selected coefficients, per-row errors, conditional ordering, and low-/high-rating operating behavior using the saved predictions. A failed validation gate stops that experiment's test stage.
3. Prepare a separate UIE-inspired two-arm screen: a condition-query attention readout over frozen Qwen passage-token states, trained either with rating MSE alone or with rating MSE plus accepted training-teacher-span supervision. Both arms use identical architecture, initialization, cohort, order, and rating supervision. Independent MOA review and focused checks precede launch. Budget: one training/validation extraction 80 GPU minutes, two fits 15 minutes each, conditional test extraction 10 minutes, analysis 30 CPU minutes. Its plan fixes the evidence weight before execution; no test-driven tuning.
4. Select its candidate using validation, measure the matched evidence-supervision contribution, and apply the archived-native eligibility/test transfer rule. A candidate improving on the native system while tying the matched rating head supports the attention pipeline; the auxiliary evidence contribution is measured separately.
5. If the bounded screens miss eligibility, stop training and publish the failure analysis and proposed JEP research direction. If an eligible construction transfers, specify the next in-training LoRA experiment with explicit reference gradients and exposure; start only if independently reviewed and feasible within the remaining budget.

Stop new training by **2026-10-26 12:30 UTC / 08:30 America/New_York**. Preserve completed artifacts, failed attempts, logs and checkpoints. Complete analysis and result publication. An hourly autonomous task checks progress, repairs justified implementation failures, and continues eligible work; it must inspect actual processes/locks and controller identities before starting anything.

## Runtime handoff

- GitHub: `pvd232/JEP`, branch `experiment/csts-matched-baselines-20261026`.
- Public result page: [live status](../training_outputs/csts_overnight_status.md).
- Mac Desktop Commander device: `5098354f-7e3d-4f9a-bb2b-cf4dd2e013b3`.
- GPU SSH: `/Users/machina/google-cloud-sdk/bin/gcloud compute ssh jep-csts-format-20261021 --account=pvd2112@columbia.edu --project=mantra-477901 --zone=asia-northeast3-a --tunnel-through-iap`.
- GPU owner Python: `/home/machina/jep-format-env/bin/python`; use the declared `.venv` activation path in each worktree.
- Original artifacts: `/home/machina/jep-csts-qwen-evidence-20261024`.
- Tranche 5 detached worktree: `/home/machina/jep-csts-matched-baselines-20261026`; controller `matched_baseline_results/overnight_reviewed_physical/summary.json`; sidecar `matched_baseline_results/overnight_reviewed_physical/events.jsonl`.
- Mac publishing clone: `/tmp/jep-tranche4-publish`; initial deployment bundle `/tmp/csts-tranche5-reviewed.bundle`.
- Follow-up worktree and exact job/log identities are recorded on the live status page as launched.

The new worktree has a physical independent local store and its own publication queue; native paths reject symlinked input directories and stores. Parent run references retain the original absolute workspace and its preserved artifact store. The two deployment-only failed attempts (`overnight_reviewed`, `overnight_reviewed_inputs`) consumed no GPU inference or training. Active Tranche 5 controller PID 54342 runs under external flock PID 54341 on `/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock`. The attention controller acquires that same lock internally; do not wrap it in another flock on the same path. Never delete or alter the original model, baseline predictions, or prior attempts. A native failure is repaired with the smallest reviewed change. Reuse of a completed extraction requires exact source/settings/model/cohort/bank/cache identity checks; automatic reuse is not inferred from filename presence.

The read-only live publisher runs on the Mac under caffeinate PID 28055, using `/tmp/jep-overnight-publisher-20261026.py`; its `.pid` and `.log` files share that prefix. It polls every 45 seconds, publishes completed-head/stage changes, and supplies a five-minute heartbeat. It writes only the fixed GitHub status file with an expected-blob-SHA guard. Check that PID before starting a replacement publisher. Publisher state is `/tmp/csts-overnight-publisher-state.json`. Its independent review is [recorded here](csts-overnight-publisher-review.md).

The attention implementation and its [plan with derivations](csts-tranche-6-evidence-attention.md) passed 37 focused CPU tests, Ruff and Pyrefly before queuing. Its physical worktree is `/home/machina/jep-csts-evidence-attention-20261026`, controller directory `evidence_attention_results`; exact queued PID and source commit are recorded after launch. The required predecessor is the full `overnight_reviewed_physical/summary.json` path above. Its internally acquired GPU lock serializes it behind Tranche 5.

## Research interpretation

The source-checked [IPED memo](csts-iped-research-20261026.md) identifies relation/block states as attention queries and edge–sentence states as keys/values; its final relation probabilities are a separate object. The inspected official repository supplies no released model implementation or checkpoint. Our condition-query readout is a defined new adaptation.

The prior FLAN/Qwen contrast motivates placing evidence supervision directly on the similarity readout. The cached teacher targets are condition-specific source evidence spans. The new attention screen measures whether those spans improve selection and similarity, using the same frozen encoder. Report span alignment coverage, ambiguity, held-out attention mass, ranking repairs/regressions, and false-positive/recall behavior. The JEP direction must connect these measurements to expert conditional retrieval, codebook discovery, and the available human-review budget.
