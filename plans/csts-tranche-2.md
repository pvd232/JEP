# Tranche 2: stronger encoder baselines

**Status: implementation prepared for review.** Experiment launch is a separate action. The branch inherits Tranche 1's completed results, training utilities and asynchronous VIPER publication queue. Previous measurements retain their original source and bytes.

## Question and context

Determine how much conditional ranking improves through a stronger pretrained representation, a trained scoring head and backbone adaptation. The completed FLAN rating baseline scored 0.506417 Spearman after validation-selected continuation. The existing GPT-6.1 reference scored 0.8029 through direct pair judgment. FLAN produces reusable passage vectors; GPT jointly reads both passages. Reuse their saved predictions as distinct reference systems.

Hypotheses: frozen Qwen embeddings can improve over the FLAN reference; supervised geometry can improve over frozen cosine; LoRA can improve over frozen geometry at a recorded additional cost. These are exploratory follow-up comparisons on an already examined benchmark. Evidence-supervision controls belong to Tranche 3.

## Systems and phases

| System | Fitting | Output used for comparison |
| --- | --- | --- |
| Training mean | Mean of training targets | One constant score; a numerical-error reference |
| Frozen Qwen | Pretrained backbone held fixed | Cosine of conditioned passage vectors |
| Ridge | Linear regression on symmetric frozen pair features | A pair score |
| Projection | Bias-free 4,096-to-128 linear map, MSE training | Cosine of projected passage vectors |
| LoRA | Attention adapters, MSE training | Cosine of adapted full-width passage vectors |

Run the first four systems in the `frozen` phase. Encode unique passage–condition inputs once for training and validation, fit every head, and freeze their selection document before exposing test inputs. Cache test embeddings once afterward. This ordering separates reusable measurement from downstream fitting and scoring.

The `lora` phase is a separate explicit launch after reviewing the frozen-phase results and the live memory/throughput observation. Its runner trains and freezes the adapter before test access. The default command only displays settings. This PR includes both phase implementations; setup leaves both unexecuted.

The runner requires a completed frozen-phase summary with the same cohort and representation before LoRA starts. Use `--frozen-summary <path>` to name a frozen run other than `baseline_results/frozen/initial/summary.json`. One workspace-level lock serializes Tranche 2 launches. Publication workers retain their independent CPU lock.

## Representation and data

Use `Qwen/Qwen3-Embedding-8B` at immutable revision `c90816d848505624c2434128dfc61132162a0ee9`, with the tokenizer from that same revision. Use the full 4,096 dimensions, explicit attended `<|endoftext|>`, final attended-token pooling and float32 unit normalization. Eligible backbone operations use BF16 on CUDA. The [pinned official model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B/blob/c90816d848505624c2434128dfc61132162a0ee9/README.md) supplies the pooling and EOD procedure. Adapting its retrieval instruction to conditional similarity is this experiment's choice.

Both passages receive this same format, independently:

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: <condition>
Query: <passage>
```

The 160-token ceiling includes EOD. A longer input stops the stage for review before encoding that passage. Cache identity includes the model revision, prompt, pooling, token ceiling and exact input digests. Shared passage text under different conditions has separate vectors. Cached artifacts preserve exact keys, row order and float32 vectors.

Reuse the prepared 6,980 training, 1,830 validation and 2,620 test comparisons and their connected caption groups. [Frozen settings](../configs/csts-tranche-2.json) bind their exact SHA-256 digests. The [label audit](../training_outputs/csts_sol61_max_label_audit.json) documents Tu's human test reannotations, the 214 excluded invalid comparisons and the separate human/LLM aggregation used for training and validation. Test ratings are rescaled through `(rating - 1) / 4`. Cosine predictions remain in their native range; ridge scores remain unclipped.

## Fitting and continuation

Ridge uses concatenated absolute embedding differences and elementwise products. Fit feature means, scales and the unpenalized intercept using training only. Share one eigendecomposition across the fixed penalty grid. Minimize mean squared training error plus `alpha` times squared coefficients. Select the penalty by validation Spearman; ties favor the larger penalty.

Projection training uses AdamW at `1e-3`, constant rate, zero warmup, weight decay 0.01, pair batch 32 and a ceiling of 48 epochs. Trainable parameters remain float32. LoRA uses rank 32 on `q_proj`, `k_proj`, `v_proj` and `o_proj`, alpha 32, dropout 0.05 and AdamW at `2e-5`. Its initial phase uses a 24-epoch linear schedule with 10% warmup. The base weights stay frozen; gradient checkpointing reduces activation memory. The effective pair batch is 32, accumulated from two-pair microbatches. Weight each microbatch by its actual number of pairs, including the final partial update.

Both neural systems select the highest validation Spearman and retain earlier epochs on ties. Each validation check increments a patience counter; a strict new best resets the counter. Stop when the counter reaches five. Clip gradients at norm 1.0, reject nonfinite values and calculate normalization, cosine and loss in float32. Log training MSE, validation metrics, learning rates, update counts, processed tokens, pair-order digests, preclip gradient norms and separate fit/validation time. Patience supplies a validation stopping observation; training stationarity remains unresolved.

Save best and terminal model artifacts separately. The terminal weights bind their exact completed epoch, optimizer steps and native resume artifact. Continuation restores AdamW moments, main-process RNG and the permutation generator, preserves the historical best, and starts a declared constant-rate phase with zero new warmup. Use a new run name and settings file to preserve the parent. The runner binds every parent input through the same sealed native producer. Pipeline `--resume` reuses completed stages; an uncertain native invocation remains blocked for reconciliation.

The proposed ceilings are 1,800 native GPU-stage seconds for frozen embeddings and 3,600 for the separate LoRA phase, plus 1,800 seconds per CPU stage. These are resource limits. LoRA feasibility and duration require an observed batch on the actual CUDA host before committing to the full run. Reaching a ceiling leaves convergence unresolved.

The adapter fitting allowance is 2,400 seconds inside its 3,600-second phase ceiling, leaving time for loading, local native verification and test evaluation. After a complete epoch, the trainer reserves 125% of the latest observed epoch duration before starting another. A budget stop at that boundary preserves a complete terminal checkpoint for continuation. An unexpected mid-epoch timeout remains a failed native attempt requiring inspection.

## Native execution and asynchronous storage

Use native VIPER TRAIN stages for fitted scorers. A native BUILD stage captures and seals test predictions before a separate CPU EVAL verifies their binding and computes metrics. Every EVAL consumes an artifact named `model`; independent metric workers recompute MSE and Spearman from saved predictions. The mean reference records MSE and reports Spearman as undefined. LoRA prediction capture uses the GPU; verification consumes the saved bytes on CPU.

Reuse [background storage](../csts_pilot/background_storage.py): locally seal and verify a successful native run, persist its publication request, then let an independent CPU worker promote and verify the cloud graph. Downstream work uses the sealed local reference while publication proceeds. Publication retries reuse measured artifacts. Reuse the verified frozen embeddings when downstream fitting or reporting needs repair. VIPER core stays at `e4ce91fa0a9330e769644aba0fccdfe062d5d821`.

The worker runs on its source host. Final cloud receipts and artifact checks are required before source-host shutdown. Moving publication to another host requires a separate durable transfer. VM changes and final cloud cleanup remain explicit operator actions; the runner provides neither provisioning nor automatic instance control.

## Analysis and decision

Recompute metrics independently from saved predictions. Require identical row IDs, targets, pair IDs and source groups across candidates and references. Report raw Spearman, MSE on rescaled ratings, condition ordering and measured cost. Use 2,000 paired source-component bootstrap draws across the same 1,241 test groups.

Predeclare projection minus frozen cosine, ridge minus frozen cosine, and each trained candidate minus the saved FLAN baseline. After the separately launched LoRA phase, report LoRA minus frozen cosine, projection and FLAN. Reuse the GPT pair-judgment reference descriptively. Choose candidates from validation and keep that choice frozen during test analysis. A proposed +0.02 Spearman practical threshold guides expansion to additional seeds; report smaller effects with cost and uncertainty. Final confirmation requires independently reviewed Spanish JEP source groups.

## Review and commands

Review [representation and scorer math](../csts_pilot/baseline_models.py), [native fitting and evaluation](../csts_pilot/baseline_stages.py), [orchestration](../csts_pilot/baseline_run.py) and [CPU reporting](../csts_pilot/baseline_report.py). The [review record](csts-tranche-2-review.md) states tested scope, repairs and remaining live checks.

Use the existing Python environment with the pinned VIPER source and the additional dependencies in [the Tranche 2 manifest](../tranche2_requirements.txt). The setup command preserves current GPU instance states.

```bash
python -m csts_pilot.baseline_run
python -m csts_pilot.baseline_run --check-inputs
```

After reviewing this PR and verifying the source, dependencies, model cache and live CUDA environment, launch a selected phase explicitly:

```bash
python -m csts_pilot.baseline_run --execute --phase frozen
python -m csts_pilot.baseline_run --execute --phase lora
```

Use `--resume` with the same source, settings, phase and name to reuse completed native stages. Use `--continue-from baseline_results/<phase>/<parent>/summary.json --name <new-name> --settings <reviewed-settings.json>` for an epoch-boundary continuation. Include `--execute` only when execution is authorized. The new ceiling must exceed the parent's terminal epoch. All previous studies, checkpoints, environments, disks and cleanup evidence remain preserved.

For a source-code repair after a downstream failure, use `--recover-from <previous-summary.json> --name <new-name>` with the original settings and explicit `--execute`. Recovery reuses verified completed measurements and retries CPU EVAL work. It carries forward the parent's consumed GPU budget and retains failed-run references. An uncertain native invocation or failed model-measurement stage requires inspection before recovery. Continuation, pipeline resume and downstream recovery remain distinct operations.

Collect each phase after its cloud queue drains. Collection rechecks native graphs and exports their exact small artifacts; large model and optimizer bytes retain their sealed references. Generate the report with the existing CPU analysis environment:

```bash
python -m csts_pilot.baseline_collect baseline_results/frozen/initial
python -m csts_pilot.baseline_report baseline_results/frozen/initial
```

After the separate adapter phase, collect it too and pass both phase directories to the reporter. Scalars appear immediately after each local native EVAL; final collection and reporting require completed publication receipts. The report and its fixed ZIP can use the existing [native CPU report publisher](../csts_pilot/convergence_publication.py) with the Tranche 2 bundle path, receipt path and experiment prefix. VM shutdown follows verified final publication and preserves the persistent disks.
