# Diagnostics from the pretrained pilot

This analysis uses the saved predictions and training traces from the 120-step L4 runs. It adds descriptive calculations to the original results.

## Training

The joint model’s mean annotation cross-entropy fell from 0.246720 in steps 1–30 to 0.019050 in steps 91–120. Its rating MSE fell from 0.090434 to 0.076084 over the same blocks. These are losses on sampled training batches. Generated records on held-out passages still need evaluation.

At the first step, the weighted annotation gradient was 3.047 times the rating gradient in the recorded encoder attention matrix. Their cosine was -0.059671. This observation concerns one matrix at one step. The annotation weight was fixed at 0.2 for the pilot.

## Conditional ratings

| Question | Similarity only MSE | Joint MSE | Shuffled MSE |
| --- | ---: | ---: | ---: |
| Speaker | 0.097017 | 0.011559 | 0.035878 |
| Action or event | 0.101239 | 0.077324 | 0.083814 |
| Outcome or purpose | 0.097234 | 0.094613 | 0.098409 |
| Affected group | 0.035700 | 0.090496 | 0.068143 |

The constant training-mean predictor has MSE 0.0625 on each of these four atomic questions.

The saved test predictions include 54 comparisons in which the same passage pair appears under two atomic questions with different target ratings. Joint training orders these ratings correctly in 29 comparisons. Similarity-only and shuffled-annotation training each order 31 correctly. Comparisons reuse passages and pairs. These counts are descriptive.

For the joint model, the mean absolute score change across those questions was 0.076731. The corresponding target change was 0.5.

## Score distribution

The joint model assigns a mean score of 0.801454 to pairs with target 0.5, and 0.902547 to pairs with target 1. Its overall mean prediction is 0.856529. The mean target is 0.75. Squared mean bias accounts for 18.48% of its test MSE. Calibration needs development predictions and a separate held-out evaluation.

## Split and selection

The dataset contains 120 training cases, 24 development cases and 72 test cases. Whole cases are disjoint. The development cases have a single speaker and action within each subject category. Consequently, every development speaker and action comparison has target 1.0. The next development split needs both matching and differing examples under every question.

The executed runner consumes the training and test files. The generated development file was unused. Training ended at the fixed 120-step limit, with learning rate 0.001 for the full model. A subsequent experiment needs development-based settings and checkpoint selection.

## Recorded scope

The decoder reads the encoder token states. The similarity head reads a pooled projection of those states. Both losses reach the encoder. The run used one seed and scripted Spanish passages. The proposed cross-narrative semantic-edit penalty was absent from this joint-task pilot.

Source results: [GPU pilot](GPU_PILOT_RESULTS.md). Numerical diagnostics: [JSON](gpu_pilot_diagnostics.json).


## Next experiment on natural text

The public C-STS reannotation used by CASE has 11,342 training comparisons and 2,834 validation comparisons at revision 058ac842f5f19d27b08ad54f6d4a2c50b3f9578b. The sentences are natural English captions. The authors combine LLM reannotations with original human labels. Their card defines validation label -1 as invalid. There are 214 such rows, leaving 2,620 valid validation comparisons. Three sentence pairs appear in both source splits. The manifest records the downloaded file hashes and these checks.

Start with the rating-only T5 objective. Verify that it can fit a small training subset, then choose the backbone learning rate and training duration using a balanced development set. Keep every question about a sentence pair in one partition. Use the mean-rating predictor and the released CASE method as references on the same evaluation data. Keep the scorer and label normalization explicit for every comparison.

The joint experiment also needs annotation targets for the natural passages. A proposed change is to make generation predict the field selected by the comparison question. For a purpose question, the target is the purpose field. This tests whether annotation supervision helps select the relevant information. Preserve the rating-only and shuffled-target controls with the same backbone and examples. Human-checked records provide stronger targets. LLM-produced records require recorded provenance and fidelity checks.

For JEP, reuse passages and source-linked records from the existing extraction workflow across reparations, harm, sanctions and restoration. Researchers prepare the initial records and pair ratings. JEP specialists validate the question definitions and resolve substantive disagreements. Split connected proceedings before constructing training and evaluation pairs.

Data sources: [CASE repository](https://github.com/LivNLP/CASE), [dataset card](https://huggingface.co/datasets/LivNLP/C-STS-Reannotated), [authors' annotation protocol](https://livnlp.github.io/CSTS-reannotation/). The [manifest](natural_data_manifest.json) records this download. Tu et al.'s [answer-based comparison method](https://aclanthology.org/2024.acl-long.64/) supplies precedent for extracting condition-relevant answers. Using those answers as a joint generation target is a proposed extension for the next experiment.
