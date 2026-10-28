# Review of the native comparison plan

Reviewed the [experiment plan](csts-native-comparison-methods.md) once on October 28, 2026. This is a self review of the mathematics, experimental controls and implementation requirements. Status: ready for user review. Native implementation and scientific execution follow that review.

## Findings resolved in this pass

1. The training comparison is explicit: original A trained LoRA through cosine, the completed experiment fitted a comparison on fixed embeddings, and the proposed experiment updates LoRA and comparison together. Both native arms use rating MSE.
2. LoRA is defined as trainable factors inside Qwen's attention matrices. The base matrices stay fixed, and the final sentence embedding retains 4,096 coordinates. Matrix dimensions, symmetry, zero initialization and gradients were checked against the [encoder](../csts_pilot/baseline_models.py) and [comparison](../csts_pilot/evidence_readout.py).
3. The regularization rationale now separates coefficient flexibility from measured generalization. The completed experiment already used decay 0.01 and validation stopping. The proposed CPU screen measures decay 0, 0.01 and 0.1, selects using validation, and retains a frozen reference at the selected setting. The native study measures how that setting transfers to jointly changing embeddings.
4. AdamW decay is specified in the optimizer, with separate LoRA and comparison groups. Comparison decay favors cosine on the current embeddings; LoRA decay favors smaller changes to pretrained matrices. These reference points are stated explicitly.
5. The writing training ceiling was separated from the 64 token diagnostic generation limit. Complete accepted training answers determine the training ceiling through deterministic tokenization. The five pass writing phase has explicit optimizer settings and a shared terminal checkpoint for each fresh pair.
6. Random states are reset after constructing every module. The plan gives writing, rating dropout and batch order separate seed rules so comparison initialization preserves matching dropout exposure within a pair.
7. Saving, restoring and scoring must include both LoRA and comparison state, with an explicit scorer kind. The planned native checks cover parameter groups, gradient flow, partial logical batches and prediction equality after restoration.
8. Required writing inputs are resolved through their original Cloud provenance and pinned hashes before their stage. The completed run receipts identify retained model and feature artifacts. Each source is verified once when loaded.

## Experimental interpretation

The primary result will compare fresh joint training with fresh cosine training after a shared proposition phase within each seed. Continued fitting from A supplies a separate paired result. Three continuation seeds share the historical A adapter; the fresh seeds independently initialize and train their LoRA and writing stages on the same public pretrained Qwen checkpoint.

The existing test supplies exploratory evidence. Paired source group intervals describe uncertainty in that test conditional on retained runs. Fresh reserved source groups supply the confirmation setting. The regularization screen selects a declared candidate for the native experiment, and all screen settings remain reportable.

The plan calls for nine CPU comparison fits, twelve native rating fits and three shared writing fits. Fixed features are reused for the CPU screen. Native training retains the encoder computation in the gradient graph. Checkpoints and reports use the existing VIPER Cloud and resume facilities with asynchronous publication.

## Verification record

The [mathematical verification receipt](csts-native-comparison-verification.json) records source hashes, numerical gradient checks, MathJax rendering and link checks. Mathematical verification covers the written derivation. The native stage integration checks listed in the plan apply to the forthcoming implementation.

The live private GitHub page requires an authenticated browser. The recorded preview uses local MathJax rendering; saved page inspection remains unobserved.
