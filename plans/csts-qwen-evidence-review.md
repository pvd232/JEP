# Qwen evidence comparison: implementation review

Code review is complete. Execution remains gated on the real-model CUDA preflight and the exact restored output-head identity.

## Checks completed

- All **147 tests passed**, including the complete two-arm, two-phase transition with real tiny Qwen and PEFT models.
- Ruff passed. Pyrefly reported **zero errors**, using the pinned GPU Python environment through `--python-interpreter-path`.
- Prefix and padding labels are ignored. Answer labels are shifted causally. Per-answer mean cross-entropy and gradient accumulation agree with an independently computed reference.
- Appending answer tokens cannot change prefix hidden states under causal attention. Inference uses only the original conditioned-passage prefix.
- Both first phases restore the same original backbone and initialize the same attention adapters. Row subsets, permutations and update counts match. First-phase termination is fixed; second-phase initialization restores terminal, rather than validation-selected, adapters.
- Both second phases reset optimizer/RNG state, use the same MSE schedule, select checkpoints on validation and stop through patience five or the common epoch ceiling. A resource-budget stop blocks the final comparison instead of being presented as completed patience training.
- Head preparation checks every supported token ID against the pinned source tokenizer. The generation head is frozen and excluded from encoder checkpoints. Its finite shape, values and SHA-256 are checked before use.
- Both final checkpoints are frozen before test publication. Existing native prediction capture and independent CPU EVAL are reused without changing their metric or cohort contracts.
- Native attempts and input identities are retained. Existing local sealing and asynchronous VIPER publication are reused. No training or score reporting waits for cloud promotion.
- Live trace updates now expose batch progress and completed-epoch validation results while a native rating stage is running.

The preflight caught repeated full-vocabulary reads during evidence tokenization. Prefixes and answers now tokenize in batches; the regression check bounds vocabulary reads independently of the number of examples.

## CUDA gate

Before execution, require finite nonzero evidence gradients in the shared adapters, a deterministic tiny-batch loss decrease of at least one percent, and a successful backward pass on the longest accepted training sequence at the declared microbatch size. The preflight adapters are discarded. Record peak memory, timings, the head hash and settings hash. Stop and inspect any failed gate before creating a full training attempt.

## Interpretation

This compares evidence-first training with an additional-rating control on the strongest tested encoder. It matches examples and optimizer updates; evidence adds answer tokens and therefore different compute cost. It is one seed on an already examined English benchmark. No additive-gain assumption, training-seed uncertainty estimate or Spanish-transfer claim is made.
