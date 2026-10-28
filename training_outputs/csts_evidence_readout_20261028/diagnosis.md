# Why the new sentence heads lost accuracy

The investigation found two problems: the attention scores grew until they selected almost a single token, and the experiment replaced A's trained sentence summary with a different representation. A smaller learning rate substantially improves B and C. A's summary remains the strongest representation in these checks.

These are exploratory diagnostics of the completed A100 experiment. The [original test results](progress.md) remain the recorded outcome. The additional fitting below uses training and validation. [Measurements](diagnosis.json) and the [step size probe](step_size_probe.json) retain the numerical results.

## Attention became almost a hard token choice

The trained matrices can increase the lengths of the query and key vectors. Dividing their dot product by the square root of 128 sets its initial scale. Layer normalization controls the input to these matrices. Their outputs can grow during fitting.

For B's selected weights, the median difference between the largest and smallest token score reached 567, 1,003 and 1,147 across seeds. On validation, 96.7%, 99.5% and 99.2% of sentence occurrences put over 99% of their weight on one token.

| Seed | B selects the last sentence token | Median query length at initialization | Median query length after fitting |
| --- | ---: | ---: | ---: |
| 7 | 16.0% | 6.47 | 142.34 |
| 8 | 92.1% | 6.42 | 129.07 |
| 9 | 83.2% | 6.83 | 149.37 |

The selected token explains part of the seed variation. Seeds 8 and 9 mostly choose the last sentence token. Seed 7 chooses earlier positions much more often. In the car, dog and shirt edits, seed 7 selects exactly the same cached vector before and after the relevant fact changes. Their B scores remain identical.

For softmax weight $\alpha_t$ and token score $\ell_s$,

```math
\frac{\partial\alpha_t}{\partial\ell_s}
=\alpha_t(\mathbf{1}_{t=s}-\alpha_s).
```

A distribution concentrated on one token gives very small derivatives. On the fixed first training batch, B's rating gradient for the query and key weights is exactly zero in float32 for seed 8 and has norm $6.9\times10^{-19}$ for seed 9. This batch probe describes those selected states. Other batches can contain softer distributions and larger gradients.

## A smaller step size improves the result

I repeated one epoch with seed 7 at the original learning rate, one tenth that rate and one hundredth that rate. Every setting receives the same initialization, 190 updates, batch order, weight decay, clipping and evidence coefficient. Measurements are retained at updates 0, 10, 50 and 190. The original rate reproduces both archived epoch one validation scores exactly.

| Learning rate | B validation Spearman | C validation Spearman | B median token score range | B occurrences with over 99% on one token |
| --- | ---: | ---: | ---: | ---: |
| 0.001 | 0.255872 | 0.221737 | 567.36 | 96.7% |
| 0.0001 | 0.739193 | 0.601113 | 5.86 | 19.2% |
| 0.00001 | 0.696973 | 0.615708 | 4.20 | 5.0% |

A's validation Spearman is 0.876789. These are one epoch measurements from one head seed. They establish that the step size materially affects this implementation. Longer fitting and additional seeds would measure the resulting performance more fully.

## The sentence representation also changed

A was trained to compare the vector at the final end of document token. B and C average vectors at words inside the sentence. Those word vectors have a different role in Qwen's computation. Their cosine needs its own empirical check.

| Fixed representation | Validation Spearman |
| --- | ---: |
| A's final summary | 0.876789 |
| Last sentence token | 0.557592 |
| Mean of sentence token vectors | 0.115999 |
| Mean after normalizing each token vector | 0.126836 |

There is also a direct check of evidence selection. On the same 5,382 training pairs with usable quotations on both sentences, averaging the teacher's quoted token vectors gives Spearman 0.160253. A scores 0.927945 on those rows. This uses teacher positions directly and measures raw vector cosine on training data. It identifies a limitation of this pooling and comparison rule.

C does learn more of the teacher's selected evidence. At the selected checkpoints, its mean probability on teacher supported outcomes is 64.9%, 66.9% and 67.6% across seeds; B has 51.7%, 13.3% and 21.5%. These are training measurements. Teacher agreement and sentence similarity need separate evaluation.

## Revised hypothesis and next experiment

**Working hypothesis:** proposition training concentrates useful similarity information in the final sentence summary. Evidence supervision can add information about which facts answer the condition. Its contribution should be tested alongside that summary, with stable attention and a learned comparison of the selected facts.

The next experiment should keep A's score and learn an additional contribution. Let $e_1,e_2$ be A's unit summary vectors and $z_1,z_2$ the full 4,096 coordinate evidence vectors. Define symmetric comparison features and the score:

```math
\begin{aligned}
\phi(a,b)&=[|a-b|;a\odot b],\\
\widehat y&=e_1^\top e_2
+w_e^\top\phi(e_1,e_2)
+w_z^\top\phi(z_1,z_2)+b.
\end{aligned}
```

Initialize $w_e,w_z,b$ at zero. The initial prediction then equals A exactly. Include that initial checkpoint in validation selection.

Use three controls: the summary with its learned comparison; the summary plus token selection learned from ratings; and the same model with quotation supervision. The quotation contribution is the difference between the last two controls. They share architecture, initialization and batches. The summary control measures the benefit of fitting a comparison directly on A's useful vectors.

Keep every sentence vector at 4,096 coordinates. Normalize the projected queries and keys and use a fixed attention scale to bound token score differences. Use the smaller step sizes as validation candidates with the same budgets for both objectives. Record query and key lengths, score ranges, token positions, gradient norms, teacher support mass and validation trajectories from initialization onward. Report the unspecified property probability separately on the fixed answered and missing cases.

The diagnostic probe used one seed. The synthetic edits contain six cases. The completed test set has already informed this investigation, so a follow up evaluated on those rows remains exploratory. A fresh reserved evaluation would support a stronger generalization claim.

## Reproduction and review

The scientific run used source `f59d2f8c5c64b96940a624a56d385330cf6a11ca` on the existing 80 GB Colab A100. Diagnostics reuse its retained caches, selected heads and original rows. They preserve the frozen encoder and the original results. The JSON files record source hashes, input identities, all three probe rates and aggregate measurements. Raw sentence text stays in the existing runtime.

The [diagnostic script](../../scripts/diagnose_evidence_readout.py) reads the original native run summary. The [step size script](../../scripts/probe_evidence_readout_steps.py) takes the same summary and its own output path. Both accept `--root`, `--summary` and `--output`. Run them with the existing project Python environment. The probe acquires `/tmp/jep-gpu.lock`.

Review and validation: 69 tests passed across the readout, attention, proposition preparation and new diagnostic suites. Ruff lint and formatting passed for both scripts and the new tests. The diagnostic tests cover variable sentence lengths, token concentration, exact vector equality under edits and preservation of full vector coordinates. The original rate's exact epoch one reproduction checks the probe against the original fitting loop.
