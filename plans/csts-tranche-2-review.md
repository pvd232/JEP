# Tranche 2 implementation review

Base: `86b629d54395057465244d708139984929895900`. Scope: the five new `baseline_*` modules, frozen settings, dependency manifest, focused tests and experiment plan. The completed Tranche 1 branch and reports remain unchanged. This PR is stacked on PR #1.

The first implementation adds a frozen-embedding phase and a separately launched LoRA phase. It reuses the existing native stage interfaces, validation stopping tracker, artifact loaders, independent metric workers and durable publication queue. The new code owns the Qwen representation, scorer fitting and phase selection. Existing VIPER and JEP interfaces retain their behavior.

Review invariants: the same model revision and conditioned representation feed all frozen scorers; training fits all preprocessing; validation chooses every checkpoint; model, optimizer and data-order state agree at continuation; selection precedes test access; downstream repair reuses the original measurements; publication stays separate from model execution; the default command displays settings.

Verdict: **Approve for the prepared-code scope.** The review covered the complete implementation after its first pass and the repairs below. The [preparation receipt](../training_outputs/csts_tranche2_preparation.json) binds the checked source files and recorded validation. Experiment execution remains a separate launch.

## Findings and repairs

| Finding | Repair | Observer |
| --- | --- | --- |
| P1: static TRAIN stages lacked VIPER's required resume output in `baseline_run.training_stage`. | Publish native closed-form completion state alongside each fitted model. | Parameterized native stage construction and actual static fitting checks. |
| P1: the 8B backbone was initially constructed on CPU before transfer in `baseline_models.load_backbone`. | Stream the pretrained weights onto the target device through `device_map`. | Loader inspection and the real tiny-Qwen PEFT forward/backward fixture; full-size CUDA memory remains a live check. |
| P1: a downstream verification repair could require another model forward in `baseline_stages.evaluate_baseline`. | Seal prediction capture in its own BUILD run, then verify it in CPU EVAL. Source recovery reuses successful producers, preserves consumed GPU time and blocks uncertain invocations. | Snapshot byte checks, CPU evaluation with backbone loading blocked, and recovery rejection/reuse cases. |
| P2: a budget stop could leave the terminal epoch counter inconsistent in `baseline_stages.fit_neural`. | Check remaining time at complete epoch boundaries and bind terminal weights to the completed history length. | Deterministic-clock budget test verifies matching terminal and resume counters. |
| P2: mapping order could determine a tied winner in `baseline_run.freeze_selection`. | Use an explicit scorer order. | Reversed mapping order produces the same selection. |
| P2: repeated tokenization and late token-ceiling errors could waste model work. | Cache CPU token sequences and validate all lengths before loading the frozen backbone. | Tokenizer call count and overlength input rejection before model loading. |
| P2: a stale reporting copy could diverge from a verified native prediction file. | Collection exports exact native producer bytes and records their hashes; reporting requires the complete manifest. | Stale-export replacement, byte alteration and omitted-manifest-file cases. |
| P2: a broadcastable malformed tensor could fill an entire projection during restoration. | Require exact trainable parameter names and shapes. | Wrong-shape restoration is rejected. |

All findings above are repaired. The code retains one shared neural training loop for projection and LoRA, one canonical frozen representation, and the existing publication queue. The completed source uses native TRAIN stages for fitting, BUILD stages for immutable predictions and CPU EVAL stages for independent metrics. It adds neither a replacement storage system nor a VIPER core patch.

## Validation

The final focused boundary includes the three new baseline test modules and the unchanged background-storage tests: **44 checks passed**. Pyrefly, Ruff formatting, Ruff E/F/I and docstring checks passed. The default review command and exact prepared-input hashes were checked. The first run of 25 checks preceded the broader recovery and reporting checks. The actual pinned Qwen tokenizer was checked on all 17,340 unique training/validation passage–condition inputs: maximum length including EOD was 65 tokens, within the 160-token ceiling. The [tokenizer receipt](../training_outputs/csts_tranche2_tokenizer_preflight.json) records that check; model weights stayed unloaded.

The test environment uses the existing Python environment and pinned VIPER support source. PEFT 0.21.2, Accelerate 1.15.0 and psutil 7.2.2 were added there; pre-existing package versions were preserved. The host's HTTP proxy also required socksio 1.0.0 for Hugging Face downloads. Ridge uses the existing NumPy/SciPy implementation.

The CPU fixtures exercise actual Qwen and PEFT gradients, ridge normal equations in both matrix regimes, symmetric pair features, partial-batch weighting, validation patience, terminal-state continuation, deterministic pair order, source recovery, test-data checks, native stage declarations, report identities and delayed publication behavior.

Live boundaries: the full 8B weights, actual CUDA peak memory, throughput, GPU numerical behavior and production cloud promotion are outside these CPU checks. A live source/runtime check precedes experiment launch. The source-host uploader requires completed publication receipts before shutdown; cross-host publication transfer remains separate work.
