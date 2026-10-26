# Audio-inspired prototype screen

## Question and scope

Does learning a vector dictionary alongside the conditional projection improve similarity or code organization relative to learning the projection and clustering afterward?

This is a new, bounded CPU experiment authorized by the user's 26 October request. It reuses successful frozen native feature extractions from Tranche 5, without reopening or relaunching the closed overnight studies. The selected Qwen + LoRA checkpoint has SHA-256 `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`. No backbone weights change and no new backbone inference runs.

The present deliverable is an English C-STS validation screen. The released ratings supply identical supervision to both arms. They are not new JEP expert judgments. Semantic code coherence, rare-demand coverage, certified edit behavior, multiple-claim coding, and expert correction time require a subsequent JEP review. No human labels are manufactured here. The current screen accesses no test features or test labels.

## Evidence and adaptation

[VQ-VAE, Section 3](https://arxiv.org/html/1711.00937v2#S3) supplies nearest-prototype assignment, dictionary/commitment objectives and straight-through gradients. [SoundStream, Section III-C](https://arxiv.org/html/2107.03312v1#S3.SS3) supplies learned audio dictionaries and usage diagnostics. Our conditional rating distortion and the coefficients below are local experimental choices. This is a single-dictionary adaptation, with no claim to reproduce an audio codec.

[SpeechTokenizer, Section 3.2](https://arxiv.org/html/2308.16692v2#S3.SS2) motivates explicitly guiding what a code representation preserves. [HuBERT, Section II](https://arxiv.org/pdf/2106.07447) motivates iterative provisional targets. This screen tests jointly learned prototypes only: it introduces neither semantic-teacher distillation nor a HuBERT masked-prediction/refinement loop. Those mechanisms remain distinct hypotheses.

The [latest negative results](../training_outputs/csts_overnight_final_report.md) establish why another copied-evidence loss or condition-subtraction sweep would repeat tested mechanisms. A learned discrete dictionary tests representation organization instead. Its benefit is a hypothesis.

## Matched arms and loss

For frozen conditioned features $h(x,q)\in\mathbb R^{4096}$, both arms learn the same bias-free $W\in\mathbb R^{128\times4096}$ and use $z=\operatorname{normalize}(Wh)$ for primary cosine scoring. The codebook contains 128 learned vectors, normalized to $p_k$. For each passage occurrence, $k=\arg\min_j\|z-p_j\|^2$ and $q_z=p_k$. Here $q$ in $h(x,q)$ is the aspect question; $q_z$ is a quantized vector.

The benchmark has 2,565 training condition strings and 917 validation strings. A separate 128-entry dictionary for every string would be poorly supported. This pilot shares one dictionary across the condition-conditioned representations. Its numeric IDs are candidate latent units, with no preassigned legal meanings. A later JEP application can use finite category-specific dictionaries, claims/spans, or multiple assignments; this pilot imposes no one-code-per-whole-JEP-passage rule.

| Arm | Optimization | Dictionary at evaluation |
|---|---|---|
| Projection control | Rating MSE on continuous cosine | Spherical k-means fitted to training representations after validation selects the projection |
| Joint prototype | Same rating MSE plus the VQ auxiliary below | Dictionary from the same validation-selected checkpoint |

The prototype objective is

$$
\mathcal L=\operatorname{MSE}(z_1^\top z_2,y)+0.1\left[\operatorname{MSE}(\tilde q_1^\top\tilde q_2,y)+\mathbb E\|\operatorname{sg}(z)-q_z\|^2+0.25\mathbb E\|z-\operatorname{sg}(q_z)\|^2\right],
$$

where $y=(r-1)/4$, $r$ is the released rating, $\operatorname{sg}$ stops gradients, and $\tilde q=z+\operatorname{sg}(q_z-z)$. The forward value of $\tilde q$ is the selected prototype; its straight-through derivative with respect to $z$ is the identity. Dictionary regression moves the selected normalized prototypes toward assigned representations. The discrete rating term supplies task gradients to the projection through this estimator. Quantized cosine is a secondary diagnostic; the continuous cosine is the primary score in both arms.

Both arms start from the same projection and initial dictionary per seed. Dictionary initialization and the control's post-hoc fit use training-only spherical k-means: one first occurrence per condition/passage identity, seeded farthest-first centers, ten Lloyd updates. Empty centers retain their preceding vectors. No equal-occupancy objective, code deletion, iterative self-labeling, teacher target, or loss-weight search is added.

## Frozen data, optimization and checks

Use all 6,980 original training comparisons / 2,674 source groups and all 1,830 validation comparisons / 688 groups, with [pinned hashes and settings](../configs/csts-codebook.json). The 16 reference-bank groups from Tranche 5 rejoin training because this experiment uses no reference bank or population subtraction. Both arms receive the same full cohort. The backbone's prior training on these groups is unchanged.

Raw feature cache SHA-256 values are training `ae77186808c521dba76d74ee094c5572092fcbcc06a2299a687375fb4b0d383e` and validation `23ac4f1d4ac113666454bb3736cac862752cf6b4c771762a4ba130a08b3f0b22`. Native producer references, row hashes and frozen-encoder identities are checked before compaction. All occurrence keys and indices must match the exact original two-comparison extraction order. Canonical captions and source groups must be disjoint across partitions. Normalization and training use float32 CPU tensors with one thread.

Seeds 7, 8 and 9 each fit both arms. AdamW uses rate 0.001, projection weight decay 0.01, dictionary weight decay zero, batch size 32, gradient clipping 1.0 and a constant rate. Each fit has a 48-epoch ceiling, a 600-second allowance and strict-improvement validation-Spearman patience five. The initial epoch is eligible. Initialization hashes and batch-order hashes must agree within each seed over shared epochs. Different selected epochs and stopping points are reported. Budget exhaustion is an execution failure, with the attempt preserved.

Checkpoints are cloned when validation improves. The projection control's final dictionary is fitted after selecting its projection, using no validation vectors. Replaying each selected model must reproduce all saved validation metrics exactly in the same CPU runtime. Resume artifacts retain terminal parameters, AdamW state, training RNG state, completed run identities and cache hashes.

## Measurements and interpretation

Report each seed's validation Spearman, MSE, condition ordering and false-positive rate at its validation-selected 90% positive-recall cutoff. Ratings 4–5 are positive and 1–2 negative for the operating point; all ratings remain in regression and ranking.

For each dictionary report occupied and effective codes, complete usage counts, largest-code share, quantization distortion, same-code counts for positive/negative pairs, and quantized-score metrics. A shared code for low-rated pairs is a diagnostic collision, not an adjudicated JEP false merge. Usage frequency does not establish semantic quality or rarity of legal claims.

The paired statistic is the arithmetic mean across the three seed-specific prototype-minus-control Spearman differences. Resample the same 688 source groups for every arm/seed in 2,000 draws, seed 61026. Report the seed-specific differences and their sample standard deviation separately. The bootstrap interval conditions on these seeds and selected epochs. Because validation selected the checkpoints, it is a diagnostic interval without selection correction. It is not a fresh-test confidence interval or a confidence interval over training seeds.

Export nearest training and held-out-validation exemplars for the first predeclared seed, retaining the exact question and passage. Definitions and expert judgment fields remain blank. Test evaluation and further hyperparameter searches are outside this first screen; a promising result would justify a separately frozen confirmation rather than tuning on the existing test.

## Implementation, execution and review

Reuse native VIPER BUILD/TRAIN/EVAL, existing artifact loaders, source references, metrics, patience and asynchronous publication. Add only a compact-cache preparation, prototype projection/objective, paired fitter, diagnostic evaluator and bounded controller. Existing experiment implementations stay unchanged. The new modules own the new dictionary invariant; the original fitting function accepts only rating loss and cannot carry it unchanged.

The owner runtime is `/home/machina/jep-format-env/bin/python` on the existing experiment host, invoked through the task checkout's `.venv`. No resources are created and all new stages declare CPU compute. The native stage inputs and stores are physical directories. Require at least 3 GiB free space before launch. Publish native artifacts independently; scoring never waits for cloud upload. Preserve unsuccessful and completed attempts.

Focused observers cover gradients through quantization, control-loss equivalence, occurrence identity, source leakage, dictionary initialization, paired orders, snapshot replay, collapse reporting and the independently recomputed paired metric. Run the new tests and the directly reused data/diagnostics/patience/metric tests, Ruff and Pyrefly before the native pilot. Record the complete reviewed diff and findings in a separate review record before committing the launch revision.

```bash
source .venv/bin/activate
python -m csts_pilot.codebook_run --inputs codebook_data/inputs.json --preflight
python -m csts_pilot.codebook_run --inputs codebook_data/inputs.json --name initial
```

If native evaluation construction fails after all fits are frozen, an explicitly inspected recovery can reuse the four successful preparation/TRAIN/publication stages using `--name evaluation_recovery --recover codebook_results/initial/summary.json`. The original attempt remains failed. The recovery checks settings, manifest and frozen model identity and runs only the final evaluation. The reserved VIPER input `test` in that EVAL is the published development cohort; this screen does not access the benchmark test partition.
