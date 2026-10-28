# Training the sentence heads to a validation plateau

This extends the [completed experiment](../training_outputs/csts_evidence_readout_20261028/progress.md) and its [diagnosis](../training_outputs/csts_evidence_readout_20261028/diagnosis.md). The user requested full B/C fitting at a selected learning rate, new D/E comparisons and the same comparison fitted directly on A's final vectors. [Results stream](../training_outputs/csts_readout_convergence_20261028/progress.md).

## Question and hypothesis

**Hypothesis:** smaller steps allow the token weighting models to learn useful sentence vectors for longer. A learned comparison can improve the ordering of sentence pairs, including pairs represented by A's final vectors. Quotation supervision may contribute additional information after each model receives equal resources for learning rate selection.

Use the same frozen Qwen checkpoint and its retained token states. Every sentence vector keeps all 4,096 coordinates. The 128 coordinate query and key projections determine the attention weights. The original attention formula, evidence coefficient and rating targets stay fixed for this test.

## B and C through validation stopping

B learns attention weights from ratings. C has the same architecture and adds the quotation loss with coefficient 0.1. Their full derivations appear in the [original methods](csts-evidence-readout-methods.md).

Fit each candidate learning rate, 0.00001, 0.00003 and 0.0001, with seeds 7, 8 and 9. The middle candidate fills the interval between the two rates examined in the diagnostic probe. Each pair starts from the same weights and uses the same batch order. Use AdamW, weight decay 0.01, batch size 32 and gradient clipping at 1. Each fit starts from initialization and has its own optimizer and permutation generator.

Evaluate validation Spearman after every epoch. Keep each model's first strictly best checkpoint, including initialization. Continue both models until ten epochs have passed since either one improved its best validation score. Both models receive the same number of updates within each candidate and seed. This defines completion as a validation plateau. Record the training losses as well.

The ceiling is 256 epochs for each candidate and seed. A fit reaching the ceiling is marked incomplete and requires further fitting before learning rate selection. The selection function rejects such candidates. Each epoch retains the current weights, selected weights, optimizer state and batch generator state in the native resume artifact. Completed candidate models and terminal optimizer states are retained together.

For each objective, average the three seeds' selected validation Spearman at each rate. Choose the rate with the highest mean. An exact tie chooses the smaller rate. The selected rate applies to all three seeds for that objective. This finds the best rate in the declared grid. B and C can select different rates. Report every candidate, seed, selected epoch, terminal epoch and stopping reason.

## D, E and a learned comparison of A

After learning rate selection, freeze the selected B and C weights and their sentence vectors. Fit D using B's vectors and E using C's vectors. Also fit the same function using A's normalized final end of document vectors.

For any pair of unit sentence vectors $a,b\in\mathbb{R}^{4096}$, use

```math
f(a,b)=a^\top b+w_d^\top|a-b|+w_p^\top(a\odot b)+c.
```

The first term is cosine similarity. The learned weights score absolute coordinate differences and matching coordinate products. The function has 8,193 parameters and gives the same prediction when sentence order is reversed. Initialize all additional parameters at zero. The initial function then equals the original cosine score for that representation.

Fit all three comparison functions with ratings MSE, AdamW, learning rate 0.001, weight decay 0.01, batch size 32 and clipping at 1. Use the same batches for all three functions, with permutation seed equal to head seed plus 10,000. Initialization is eligible for selection. Select each function's first strictly best validation Spearman. Continue until ten epochs have passed since any function improved, with the same 256 epoch ceiling and explicit incomplete status.

This comparison isolates the scoring function on identical fixed vectors. The selected B/C vectors receive zero comparison gradients. Verify their parameter hashes before and after fitting.

## Inputs, evaluation and diagnostics

Rebuild training and validation caches from the original model and input files restored through sealed VIPER Cloud references. The model, rows and quotation records retain their original hashes. The configuration binds the completed parent study at source `f59d2f8c5c64b96940a624a56d385330cf6a11ca`. Verify the parent summary, input hashes, new cache hashes and frozen encoder identity. There are 6,051 training, 1,576 validation and 2,431 test comparisons. The fitting worker receives training and validation inputs. Seal all selected models and learning rates, then extract test and fixed edit features for evaluation.

Report A, B, C, D, E and A with its learned comparison for every seed. The primary new contrast is A with comparison minus A. Also report D minus A, E minus A, B minus A, C minus A, C minus B, E minus D, D minus B and E minus C. Include normalized MSE and Spearman for every model, plus all 2,000 draw paired source group bootstrap intervals across the 1,222 test groups.

C minus B and E minus D now compare separately tuned objectives with equal search resources. Their interpretation includes the chosen learning rates. Candidate validation trajectories also retain comparisons at each common rate. D minus B and E minus C hold their sentence vectors fixed while fitting the comparison function.

Record rating loss, quotation loss, teacher agreement, query and key weight norms, attention entropy, the fraction of occurrences with over 99% weight on one token, null probability and the first batch gradient diagnostics each epoch. Evaluation includes all six fixed edit cases, condition results, comparisons across conditions for the same sentence pair and condition families. Null probability supplies a separate addressability measurement. The original test has informed this follow up, so this evaluation is exploratory. Fresh reserved examples and additional backbone seeds would support confirmation.

## Execution and review

The recovery divides fitting across two L4 workers and an A100 worker when available. Each worker fits one seed at every declared learning rate. The coordinator collects all nine candidates and applies the original mean validation selection across seeds. D, E and the comparison on A then use the globally selected rates. Every worker uses the same sealed feature files and records its actual hardware.

Each fitting epoch saves an immutable copy of its current and selected weights, optimizer, batch generator and history. A CPU thread publishes these snapshots through VIPER's existing file publication API. The first snapshot completes a Cloud restore with a matching hash before the second epoch. Later uploads proceed during fitting. Completed candidate bundles, comparison checkpoints and publication receipts are retained through the same native API. Fitting completion waits for these receipts.

The [configuration](../configs/csts-readout-convergence.json) declares the grid and stopping rules. The [native stages](../csts_pilot/evidence_readout_convergence.py) fit and evaluate the models. The [controller](../csts_pilot/evidence_readout_convergence_run.py) consumes the rebuilt native artifacts under the shared GPU lock on a Colab A100 with 40 GB memory. Cache extraction, fitting and evaluation use native VIPER runs. The existing publication queue invokes VIPER Cloud promotion in separate processes as each stage completes. Publication receipts record the sealed Cloud references.

Review covers equal seed coverage, rate selection using validation alone, tie handling, rejection of incomplete fits, initialization selection, checkpoint retention, full coordinate values and frozen B/C parameters during comparison fitting. The initial validation run passed 72 tests across the relevant suites. Three publisher tests also passed. The additional native CPU fixture remains available for integration checks. Scientific execution uses the committed source and configuration. The Markdown stream reports extraction, every epoch and the final results.
