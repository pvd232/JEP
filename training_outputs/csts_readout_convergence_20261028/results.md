# Final results: sentence vectors and their comparison

Completed October 28, 2026. All nine B/C candidates and all three comparison fits reached validation patience. Training used two L4 workers and one A100 worker. Global selection and evaluation used the A100.

The useful result is a small, consistent gain from learning how to compare A's final vectors. A with comparison averages **0.865230** test Spearman; A scores **0.863398**. The mean gain is **0.001833**, with a paired 95% bootstrap interval of **[0.001108, 0.002569]**. This is the mean of three separately evaluated models.

## Test scores

All models use the same 2,431 test rows. MSE uses ratings scaled to [0, 1].

| Model | Sentence representation and score | Mean Spearman | Mean MSE |
| --- | --- | --- | --- |
| A | Original final vector; cosine | 0.863398 | 0.035636 |
| B | Learned token weights; cosine | 0.706753 | 0.088584 |
| C | Token weights with quotation supervision; cosine | 0.649332 | 0.101058 |
| D | B vectors; learned comparison | 0.751436 | 0.071641 |
| E | C vectors; learned comparison | 0.711650 | 0.084521 |
| A with comparison | A final vectors; learned comparison | 0.865230 | 0.035131 |

| Seed | B | C | D | E | A with comparison |
| --- | --- | --- | --- | --- | --- |
| 7 | 0.707125 | 0.647899 | 0.753125 | 0.716361 | 0.864672 |
| 8 | 0.702160 | 0.631321 | 0.743052 | 0.694009 | 0.865373 |
| 9 | 0.710974 | 0.668775 | 0.758132 | 0.724579 | 0.865646 |

## What this changes

Learning the comparison improves D by 0.044683 over B and E by 0.062318 over C, using identical fixed sentence vectors. This directly supports a contribution from the scoring function. A with the same comparison gives the strongest result.

The selected C heads place their attention across several tokens and follow quotation targets more often during training. B leads C by 0.057421 test Spearman, and D leads E by 0.039787. These results point toward the representation formed from token states and its training objective as further sources of the gap. Attention concentration alone provides an incomplete account of the observed performance.

**Working hypothesis:** A's final sentence vectors retain condition relevant meaning that a small symmetric comparison can use more accurately than cosine. Keep A's vectors as the main representation and use the learned comparison as the current candidate improvement. Quotation supervision supplies a separate measurement of evidence selection; its contribution to better similarity requires further study.

The baseline is the Qwen model after proposition training and similarity training, as documented in the [original comparison](https://github.com/pvd232/JEP/blob/bef8cfb0f8f85a602f0ec86ff9450f9d467fa9d5/training_outputs/proposition_full_20261026/comparison_report.md). Its training used the final sentence vector with cosine. This study held those LoRA weights fixed, as implemented by `extract_readout()` in the [extraction stage](../../csts_pilot/evidence_readout_stages.py). All three seeds train new heads on that one backbone.

**Interpretation:** A uses the representation and score through which Qwen received its rating supervision. B/C introduce another way to combine the same frozen token states. We infer that this training history can favor A's representation. The measured B/C results therefore describe adding these heads after the original training. Joint training would also allow Qwen's token states to adapt to the new heads and loss. The gain from comparing A's fixed vectors gives direct motivation for the [proposed joint comparison experiment](../../plans/csts-readout-convergence-methods.md#proposed-next-step-train-qwen-and-the-comparison-together).

This is an exploratory result on the existing test set, which informed the follow up. The intervals measure uncertainty across test source groups conditional on these three head seeds and this one frozen backbone. Confirmation calls for fresh reserved examples and additional backbone seeds.

## Paired comparisons

Each interval uses 2,000 paired bootstrap draws across 1,222 source groups. Every draw was defined.

| Comparison | Mean Spearman change | 95% interval | Mean MSE change |
| --- | --- | --- | --- |
| A with comparison minus A | 0.001833 | [0.001108, 0.002569] | -0.000505 |
| D minus A | -0.111961 | [-0.128541, -0.096727] | 0.036005 |
| E minus A | -0.151748 | [-0.171034, -0.133617] | 0.048885 |
| B minus A | -0.156645 | [-0.177335, -0.136874] | 0.052948 |
| C minus A | -0.214066 | [-0.235647, -0.191408] | 0.065422 |
| C minus B | -0.057421 | [-0.072073, -0.042191] | 0.012474 |
| E minus D | -0.039787 | [-0.050917, -0.028491] | 0.012881 |
| D minus B | 0.044683 | [0.036194, 0.053467] | -0.016944 |
| E minus C | 0.062318 | [0.052710, 0.071996] | -0.016537 |

## Training through the validation plateau

The declared grid selected learning rate 0.0001 for B and 0.00003 for C by mean best validation Spearman across seeds. These are the selected rates within this grid. Each candidate continued for ten epochs after the last improvement by either model. The saved model comes from its own best validation epoch.

| Learning rate | Seed | Epochs trained | B selected epoch | C selected epoch | Best B validation rho | Best C validation rho |
| --- | --- | --- | --- | --- | --- | --- |
| 1e-05 | 7 | 15 | 5 | 2 | 0.735578 | 0.641987 |
| 1e-05 | 8 | 15 | 5 | 3 | 0.725567 | 0.665031 |
| 1e-05 | 9 | 16 | 3 | 6 | 0.725735 | 0.655095 |
| 3e-05 | 7 | 13 | 3 | 1 | 0.734993 | 0.662696 |
| 3e-05 | 8 | 13 | 3 | 3 | 0.731288 | 0.647345 |
| 3e-05 | 9 | 11 | 1 | 1 | 0.727226 | 0.664148 |
| 0.0001 | 7 | 12 | 1 | 2 | 0.739195 | 0.646660 |
| 0.0001 | 8 | 13 | 3 | 1 | 0.737643 | 0.638951 |
| 0.0001 | 9 | 11 | 1 | 1 | 0.730568 | 0.644259 |

| Seed | Comparison epochs trained | D selected epoch | E selected epoch | A comparison selected epoch |
| --- | --- | --- | --- | --- |
| 7 | 21 | 9 | 11 | 1 |
| 8 | 23 | 11 | 13 | 2 |
| 9 | 27 | 12 | 17 | 4 |

## Attention and evidence diagnostics

Values below describe each selected head at its selected epoch. Entropy and concentration use validation occurrences. Quotation agreement is the training average recorded during that epoch, while weights were being updated. Each seed has 12,073 supervised training occurrences.

| Head | Seed | Attention entropy | Occurrences above 99% on one token | Training quotation top choice agreement |
| --- | --- | --- | --- | --- |
| B | 7 | 1.164 | 19.2% | 27.8% |
| B | 8 | 1.332 | 15.8% | 35.6% |
| B | 9 | 1.255 | 13.9% | 27.0% |
| C | 7 | 2.132 | 0.0% | 37.9% |
| C | 8 | 2.145 | 0.0% | 54.1% |
| C | 9 | 2.048 | 0.0% | 41.5% |

C has zero occurrences above the 99% concentration threshold at its selected checkpoints. Its mean test null probability is about 0.069, and B's is about 0.018. All test rows contribute to similarity scoring. The [training traces](fit-trace.json) retain rating and quotation losses, query and key norms, attention measurements, batch order hashes and first batch gradients for every epoch.

## Controlled edits

The fixed six cases cover car, dog and shirt colour, cat posture, cup count and ball location. Each case contains its original sentence pair plus irrelevant, relevant and missing information edits. The table averages equally over the six cases and three seeds. A uses its one fixed reference model. Scores use each model's raw output.

| Model | Mean absolute change for irrelevant edit | Mean score decrease for relevant edit |
| --- | --- | --- |
| A | 0.005174 | 0.781013 |
| B | 0.019471 | 0.278530 |
| C | 0.015985 | 0.239713 |
| D | 0.031977 | 0.502592 |
| E | 0.030169 | 0.493370 |
| A with comparison | 0.005354 | 0.854176 |

A with comparison gives the largest average response to relevant edits and retains a small average response to irrelevant edits. These six cases serve as descriptive diagnostics. The learned comparison produces an unrestricted scalar; some predictions extend beyond [0, 1].

[Diagnostic values](diagnostics.json) include every selected test metric, all contrasts, every edit case, null changes, evidence mass, condition families and ordering across conditions for the same sentence pair. The full native report additionally retains every condition and row identifier.

## Artifacts and review

All three seed fitting runs and all five final stages have published VIPER Cloud receipts. The native checkpoint publisher also sealed each epoch snapshot. [Cloud references](cloud-receipts.json) identify the durable runs and candidate bundles. Models, feature caches, resume states, validation and test predictions and the complete report are retained in Cloud.

Candidate fitting source: `bf167d773df10cf097a3be7e5966b69c299d9227`. Global selection, comparison fitting, extraction and evaluation functions: `fdbcb3461f63cf44d7cb3cde4de27332594e452d`. The final controller repair seals evaluation rows through the existing native publication stage. The retained model and feature hashes were used for the completed evaluation.

[Frozen selection](selection.json) records the model hash and the validation selection. [Methods](../../plans/csts-readout-convergence-methods.md) and [code review](../../plans/csts-readout-convergence-review.md) describe the implementation, checks and evaluation binding repair. The [execution stream](progress.md) retains the recovery history.

