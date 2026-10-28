# Review of the native comparison plan

Reviewed the [experiment plan](csts-native-comparison-methods.md) and its implementation again on October 28, 2026, following the user's execution request. This is a self review of the mathematics, experimental controls and implementation requirements. Status: authorized for execution after the implementation checks below.

The user's scope corrections are incorporated: seed 7 runs first, starting from the original pretrained Qwen and training fresh LoRA and comparison weights directly on similarity ratings. A positive validation result releases seeds 8 and 9 under the same configuration. Existing cosine models supply the reference predictions. Comparison decay remains fixed at the completed experiment's value of 0.01.

## Findings resolved in this pass

1. The completed experiment fitted a comparison on fixed embeddings. The proposed experiment updates fresh LoRA and comparison weights together using rating MSE.
2. LoRA is defined as trainable factors inside Qwen's attention matrices. The base matrices stay fixed, and the final sentence embedding retains 4,096 coordinates. Matrix dimensions, symmetry, zero initialization and gradients were checked against the [encoder](../csts_pilot/baseline_models.py) and [comparison](../csts_pilot/evidence_readout.py).
3. The regularization rationale identifies coefficient flexibility as a reason for standard fitting controls. Its empirical benefit remains a measurement question. The joint runs reuse decay 0.01 and validation stopping from the completed experiment.
4. AdamW decay is specified in the optimizer, with separate LoRA and comparison groups. Comparison decay favors cosine on the current embeddings; LoRA decay favors smaller changes to pretrained matrices. These reference points are stated explicitly.
5. A completed seed 7 epoch releases seeds 8 and 9 once its selected validation Spearman strictly exceeds the saved ratings control on the same frozen rows and the epoch snapshot is sealed in Cloud. Seed 7 continues to validation patience; strict best checkpoint selection preserves the positive score. The comparison uses full precision archived predictions. The plan contains one initial fit and two conditional fits.
6. Random states are set after constructing every module. Rating dropout and batch order have separate seed rules, and both states are saved for resumption.
7. Saving, restoring and scoring include both LoRA and comparison state, with an explicit scorer kind. The planned native checks cover parameter groups, gradient flow, partial logical batches and prediction equality after restoration.
8. Rating inputs and the public checkpoint have explicit identities. Historical reference predictions retain their original Cloud provenance. Each source is verified once when loaded.
9. The existing ratings control reports 2,430 test rows; the current test has 2,431. Paired evaluation uses verified common input identities and reports coverage. New models also receive full current test evaluation. The interpretation accounts for the reused control's single seed and original training history.

## Experimental interpretation

The primary result compares fresh joint training with the existing ratings control. A and A with comparison supply secondary historical references. This measures the complete new training procedure relative to retained models. Differences in training history and seed coverage remain part of the interpretation.

The existing test supplies exploratory evidence. Paired source group intervals describe uncertainty in that test conditional on retained runs. Fresh reserved source groups supply the confirmation setting.

The plan calls for one initial native rating fit, using seed 7. A positive validation result releases seeds 8 and 9, giving a maximum of three fits. The continuation decision and selected states are fixed before test evaluation. Reporting retains the initial seed result and the conditional nature of any three seed summary. Each comparison starts at zero, and each parent is the seed's fresh adapter initialization. Native training retains the encoder computation in the gradient graph. Checkpoints and reports use the existing VIPER Cloud and resume facilities with asynchronous publication.

## Verification record

The [mathematical verification receipt](csts-native-comparison-verification.json) records source hashes, numerical gradient checks, MathJax rendering and link checks. Mathematical verification covers the written derivation. Eight focused tests passed in the existing L4 environment. They exercise LoRA and comparison gradients, frozen base matrices, exact cosine initialization, sentence order symmetry, save and restore of both components, partial logical batch gradients, optimizer and random state restoration across an epoch boundary, the strict validation continuation rule, and asynchronous checkpoint publication. Ruff and Python syntax checks passed locally.

The live private GitHub page requires an authenticated browser. The recorded preview uses local MathJax rendering; saved page inspection remains unobserved.

## Second review before execution

The [native implementation](../csts_pilot/native_comparison.py) preserves both trained components under an explicit scorer kind. Its [controller](../csts_pilot/native_comparison_run.py) binds the reviewed configuration, repeats an incomplete epoch ceiling from the native terminal state, and releases follow on seeds using the saved validation decision. Physical microbatch profiling performs gradient computation with unchanged weights and restores random states before fitting.

The review found an initial blocking network wait in the existing checkpoint wrapper. The native experiment sets its new optional `wait_for_first` argument to false. File copies remain immutable, uploads use the existing VIPER file publication API on a background thread, and the terminal barrier checks every publication before worker release. The previous experiment retains its original default. A focused asynchronous first upload test passed.

The archived ratings validation predictions cover the exact 1,576 frozen rows with identical text and targets. Their full precision Spearman is 0.8718754731182672. This is the continuation threshold. The control is reused. GPU integration, actual hardware identity, epoch measurements and final Cloud receipts will be recorded by execution.

The execution controller can therefore use all three GPUs after the first positive completed epoch. The release helper checks the published checkpoint identity, recomputes the tested validation comparison, and seals its decision in VIPER Cloud. Scientific fitting functions remain pinned to their original source commit.

Epoch recovery accepts a complete sealed snapshot manifest. It verifies seed, configuration and epoch counters, restores both trained components and optimizer moments, and includes recovery provenance in the native inputs. Destination profiling restores the saved random state before further updates. The focused resume check exercises that random state restoration.

Nine focused checks passed in 8.05 seconds after adding destination profiling to epoch recovery. The added case deliberately changes random states during profiling and verifies that recovery still reproduces the uninterrupted weights and batch order.

## Review of final scoring and publication

Seed 7 crossed the continuation threshold at epoch 3, with validation Spearman 0.8751512974333209. Seeds 8 and 9 started from fresh adapters. Seed 8 resumed its complete epoch 2 Cloud state on a replacement A100 40 GB after its first assignment became unavailable. Seeds 7 and 9 continued on their L4 workers.

The [final scoring driver](../scripts/finalize_csts_native_comparison.py) freezes the executed seed list and validation rule, then freezes each completed model before opening its test inputs. It uses the existing native prediction stage, including restoration of LoRA and comparison together. The report joins complete input identities for the historical control, reports coverage, and computes paired source group intervals and seed variation separately. It retains the six fixed edit cases, condition diagnostics, fitting traces and original control history.

Two [focused final scoring checks](../tests/test_native_comparison_finalization.py) passed in 7.24 seconds. They check reference subset ordering, changed inputs, duplicate identities and the source group bootstrap with identical predictions. Ruff and syntax checks passed. This review covers orchestration and reporting; final GPU prediction execution follows completion of the three fits. Cloud receipts and GitHub delivery precede final worker shutdown. Shared GPU locks and process inspection preserve unrelated work.

The reporting schedule now publishes a finished fit's test score while the remaining fits continue under the same committed validation rule. Each scored model has completed patience and Cloud publication. The aggregate report retains all three selected models and the conditional seed summary.
