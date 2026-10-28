# Review of the native comparison plan

Reviewed the [experiment plan](csts-native-comparison-methods.md) once on October 28, 2026. This is a self review of the mathematics, experimental controls and implementation requirements. Status: ready for user review. Native implementation and scientific execution follow that review.

The user's scope corrections are incorporated: three fresh joint training runs start from the original pretrained Qwen and train directly on similarity ratings. Existing cosine models supply the reference predictions. Comparison decay remains fixed at the completed experiment's value of 0.01.

## Findings resolved in this pass

1. The completed experiment fitted a comparison on fixed embeddings. The proposed experiment updates fresh LoRA and comparison weights together using rating MSE.
2. LoRA is defined as trainable factors inside Qwen's attention matrices. The base matrices stay fixed, and the final sentence embedding retains 4,096 coordinates. Matrix dimensions, symmetry, zero initialization and gradients were checked against the [encoder](../csts_pilot/baseline_models.py) and [comparison](../csts_pilot/evidence_readout.py).
3. The regularization rationale identifies coefficient flexibility as a reason for standard fitting controls. Its empirical benefit remains a measurement question. The joint runs reuse decay 0.01 and validation stopping from the completed experiment.
4. AdamW decay is specified in the optimizer, with separate LoRA and comparison groups. Comparison decay favors cosine on the current embeddings; LoRA decay favors smaller changes to pretrained matrices. These reference points are stated explicitly.
5. Seeds 7, 8 and 9 independently initialize fresh LoRA and a zero initialized comparison from the public pretrained Qwen. The plan contains exactly three native rating fits.
6. Random states are set after constructing every module. Rating dropout and batch order have separate seed rules, and both states are saved for resumption.
7. Saving, restoring and scoring include both LoRA and comparison state, with an explicit scorer kind. The planned native checks cover parameter groups, gradient flow, partial logical batches and prediction equality after restoration.
8. Rating inputs and the public checkpoint have explicit identities. Historical reference predictions retain their original Cloud provenance. Each source is verified once when loaded.
9. The existing ratings control reports 2,430 test rows; the current test has 2,431. Paired evaluation uses verified common input identities and reports coverage. New models also receive full current test evaluation. The interpretation accounts for the reused control's single seed and original training history.

## Experimental interpretation

The primary result compares fresh joint training with the existing ratings control. A and A with comparison supply secondary historical references. This measures the complete new training procedure relative to retained models. Differences in training history and seed coverage remain part of the interpretation.

The existing test supplies exploratory evidence. Paired source group intervals describe uncertainty in that test conditional on retained runs. Fresh reserved source groups supply the confirmation setting.

The plan calls for three native rating fits, using seeds 7, 8 and 9. Each comparison starts at zero, and each parent is the seed's fresh adapter initialization. Native training retains the encoder computation in the gradient graph. Checkpoints and reports use the existing VIPER Cloud and resume facilities with asynchronous publication.

## Verification record

The [mathematical verification receipt](csts-native-comparison-verification.json) records source hashes, numerical gradient checks, MathJax rendering and link checks. Mathematical verification covers the written derivation. The native stage integration checks listed in the plan apply to the forthcoming implementation.

The live private GitHub page requires an authenticated browser. The recorded preview uses local MathJax rendering; saved page inspection remains unobserved.
