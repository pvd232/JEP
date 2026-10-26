# Archived LLM comparator: provenance and comparability

Read-only verification performed 2026-10-26. No inference, model fitting, or baseline scoring was launched.

The archived LLM result is **0.8029168452132416 test Spearman**. The selected Qwen + LoRA ratings-only model has **0.7885050017660868 test Spearman** on the same comparison rows, giving an archived point difference of **0.0144118434471548** in favor of the LLM. This is the closest archived measurement verified for the earlier shorthand “about 0.805”; no separate 0.805 measurement was found in the inspected sources.

| System | Test Spearman | Test MSE, normalized 0–1 | Conditional ordering |
|---|---:|---:|---:|
| GPT-6.1 Sol, max reasoning | 0.8029168452132416 | 0.0642614503816794 | 0.9224137931034483 |
| Selected Qwen + LoRA, ratings-only | 0.7885050017660868 | 0.07076334011896077 | 0.921455938697318 |

The LLM record is the project's `evaluation`/test split. Its result does not supply a validation target. Current Qwen validation Spearman 0.7825746597420997 belongs to the separate 1,830-row validation cohort.

## Exact shared cohort

Both archived prediction files were checked against the current original Qwen study's prepared test file, `/home/machina/jep-csts-qwen-evidence-20261024/csts_data/evaluation.json`:

- 2,620 comparison rows from 1,241 connected source groups.
- Dataset SHA-256: `2c8b6f2b62740c85c376eacd02ef222c2bfacdfe8df5f772a4dd7d52b6d38f1e`.
- Exact ordered row equality, including sentence texts, conditions, ratings, normalized targets, row IDs, pair IDs, and group IDs. Only each system's prediction-specific fields were removed for this equality check.
- Labels follow the recorded audit: LivNLP/C-STS-Reannotated revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b`; all 2,834 released validation labels match Tu et al.'s 2024 human reannotations, and excluding 214 invalid rows yields this 2,620-row test set. The recorded audit distinguishes the release's separate human/LLM training-label aggregation.

| Artifact | SHA-256 |
|---|---|
| LLM saved predictions, `training_outputs/csts_sol61_max_predictions.json` | `305d74025d64768cb0c2b8421fa8a1c79219d9774d5726f6e8c1e5b8a3c95eb5` |
| Qwen saved test predictions, native `predict_ratings` artifact | `9ececbf76ac63b420196b4b4ef1285b5f632601a81043915d9236d9190cd1f24` |
| LLM results, `csts_sol61_max_results.json` | `94b8eac2965177d04969402b608a5de51ba05c18f2cf5aed0835b1f5715fcd54` |
| LLM inference manifest, `csts_sol61_max_manifest.json` | `62548ff91b402050abe61a5ab23cd181392eca4b6e5e1b11f14db20940495401` |
| LLM native verification receipt, `csts_sol61_max_verification.json` | `34df56fd228155cc17f89f63aabe0f3a2f280b82bd4db641f8208313669fa0fb` |
| LLM label audit, `csts_sol61_max_label_audit.json` | `048192d5cf9b1073070ba6f75a551ac72ee6306ccade79582bc1035f4b6e638d` |

## LLM model, prompt, and scoring protocol

The inference manifest records `gpt-6.1-sol` with requested reasoning effort `max`, through the authenticated Codex CLI on 2026-10-21. The CLI exposed the model alias and returned no finer model snapshot. Sampling temperature remained the provider/CLI default.

The fixed zero-shot rubric instructs the model to judge semantic similarity specifically under the supplied condition, use a 1–5 score at 0.1 precision, rely on the supplied sentences, and return JSON scores with each row ID exactly once. Each input contains an item identifier, both sentences, and the condition. The recorded manifest states that reference labels were withheld and tools were forbidden; tool activity invalidated a batch. Labels were joined during offline evaluation. An eight-row source-distinct development timing/protocol check preceded evaluation, with one rubric and no evaluation-based prompt selection.

Inference used 64 items per fresh request, four concurrent requests, and 41 batches. Items within a batch shared context. The manifest hashes the rubric (`813c66acdbc5acb2c99c7c711d045fdc729c39a9b2edf4b0d1cbf9a06845fb3f`), capture source (`6861bb6df31b56666f26b09fbbd64c9de8cdf7238493b479d67331a9b393b051`), and output schema (`52454c14d03860c76645da2f65573d7be79b0e2b99bf3e5d90f3f535de3cc0c3`).

LLM scores were transformed with `(score - 1) / 4`. Spearman uses all 2,620 rows with average ranks for ties. Conditional ordering separately compares changed conditions for the same sentence pair and awards half credit for ties. The LLM produced a direct score after jointly reading each pair. Qwen produces separately reusable passage embeddings and scores their cosine. This comparison therefore measures the complete systems on the shared benchmark task.

The report records an existing test set already examined historically. Its 2,000-draw source-group bootstrap interval for LLM Spearman is [0.7842717991355665, 0.8202559037259056]. This is the LLM's standalone interval; the archived point gap above has no newly computed paired interval in this verification.

## Native evidence chain and inspected sources

The LLM inference was captured externally and published through VIPER. Native source commit `9254e4f9bdf738bb1dcd36a573f296ec459c326a` independently evaluated the captured predictions and verified two measurements, MSE and Spearman. The evaluation resolved-run SHA-256 is `8858fb17067e046c7080dffa0ebfe4b18d044dd59f32bee3651261c8bc8f80de`; recorded cloud workspace is `pvd232/jep_csts_joint_20261021`.

Primary LLM reports/manifests/results/verification/audit were read from `/Users/machina/Developer/ChatGPT/JEP-tranche2-exec-20261023/training_outputs/`. The same prediction hash was verified on the GPU original Qwen worktree. The Qwen native producer was `csts_qwen_evidence_cd720270_6b877324_predict_ratings`, run `01M5RTQN2A03M06DF8CVGGKVKY`; its successful resolved-run SHA-256 is `c84ef86cb701f7585559d8e5a22c11ab684438c3f15bc2930be629f797affadd`.

The local source `csts_pilot/llm_record.py` was inspected for protocol, coverage, row-ID, range, manifest/data-hash, and external-model-descriptor checks, plus the native independent metric-worker declarations. Qwen results were read from the original study's `summary.json` and its saved native prediction artifact. All metric values above are archived measurements. This verification independently inspected source/artifact identities and cohort equality.
