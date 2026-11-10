# Geometry review for JEP conditional harm and reparation retrieval

Review date: 10 November 2026. Stream 03. This is a structured focused review of primary methods and theory, not an exhaustive literature census. Eleven papers received targeted full-text inspection; two additional items were screened but excluded from that count. The adjacent ledger records exact sections, source URLs, data and label types, limitations, search queries and snowballing. No code, jobs, resources or historical results were changed.

## Decision

**Revise the scientific claim and prioritize typed retrieval.** Shared inner products, PSD metric learning, signed similarities, conditional subspaces and asymmetric semantic relations all have substantial prior art. The defensible JEP question concerns whether explicitly specified needs, principles and response roles improve expert-relevant cross-case retrieval under scarcity and domain shift. A new architecture claim is presently unsupported.

The retained pilot already gives a useful falsification: PSD helps the compressed heads relative to their signed counterparts, while every head loses to unchanged Qwen cosine. The conditioning screen is near ceiling and harm-to-repair translation loses to raw cosine. Those observations favor harder controls and stronger labels over adding geometric machinery.

## What prior work rules out

The closest methodological counterexample is [OASIS](https://jmlr.org/papers/volume11/chechik10a/chechik10a.pdf), especially §§6.1–6.2. It already studies unconstrained bilinear similarity, symmetry, online versus final PSD projection, and overfitting. A claim that PSD can act as regularization is established, not a novel moral-learning result.

[Cao, Guo and Ying](https://arxiv.org/pdf/1207.5437), §§2–4, explicitly analyze generalization without requiring PSD. [Bellet and Habrard](https://arxiv.org/pdf/1209.1086), §§2–6, connect robustness to generalization under stated distributional assumptions. Neither theory turns many correlated sentence pairs into many independent observations or licenses an untested Colombian domain transfer.

[WIPS](https://arxiv.org/pdf/1902.10409), §§4–6, already learns positive and negative shared-embedding weights; the pilot signed diagonal arm is a restricted member of this established family. Krein-space methods likewise show that preserving indefinite similarities is technically legitimate. Negative eigenvalues are not automatically annotation errors.

Classical PSD and local-metric baselines precede this project: [Xing et al.](https://proceedings.neurips.cc/paper_files/paper/2002/file/c3e4035af2a1cde9f21e1ae1951ac80b-Paper.pdf) and [LMNN](https://www.jmlr.org/papers/volume10/weinberger09a/weinberger09a.pdf). Conditional subspace novelty also faces Conditional Similarity Networks; that paper was only screened here, and its full methods belong in the conditional-similarity review stream.

## Mathematical distinctions that matter

A PSD kernel and a metric are different objects. A shared inner product produces PSD Gram matrices for any finite set, but its values need not be nonnegative and it is not itself a distance. With unit-normalized vectors, sqrt(2-2cosine) is Euclidean distance and preserves nearest-neighbor order under the same candidate set. A monotone distance conversion cannot supply a retrieval gain.

An indefinite target matrix may arise from inconsistent scales, self-similarity conventions, missingness, noise, or a meaningful relation that is not a kernel. Its spectrum alone cannot distinguish these explanations. Rating transformations must be fixed with development data; no completed or projected test-label matrix may become a prediction mechanism.

Symmetric harm analogy and directed remedy adequacy are different targets. A victim's unmet water access can be addressed partly by a water-restoration plan. The reverse relation is not the same question. A sanction may target a perpetrator's responsibility without covering the victim's deficit. None of this implies a transitive order or a mirror inverse between harm and repair.

[Order-Embeddings](https://arxiv.org/pdf/1511.06361), §2, provides an established asymmetric relational construction, while [Learning Tversky Similarity](https://arxiv.org/pdf/2006.11372), §§3–5, provides common-versus-distinct-feature scoring. Crucially, its image experiments enforce symmetric weights because the training labels are symmetric class equivalence. They do not validate asymmetric legal relevance. The newer [Tversky Neural Networks](https://arxiv.org/html/2506.11035v1) is an additional readout candidate, with capacity and optimization controls required; its classification/language-model gains do not demonstrate moral alignment.

The November 5 [Semantic Conditional Similarity framework](https://arxiv.org/html/2611.08778v1), §§5–11, is a separate use of SCS: another document removes shared lexical content before residual comparison. Its inspected demonstration uses synthetic lemma sets. This can inspire an evidence-attribution baseline, but it does not supply empirical validation of ethical aspect conditioning. Lexical residualization can remove important shared context and mishandle paraphrase or negation.

## Ranked gaps and decisive experiments

| Priority | Candidate gap for the mandate | Closest prior art / novelty risk | Decisive test |
|---|---|---|---|
| 1 | Expert-validated, theory-explicit separation of harm analogy and need→response adequacy across JEP cases | Order embeddings, Tversky and asymmetric ranking already provide methods. Moderate confidence in application gap; requires legal-stream confirmation. | Hold encoder fixed; compare cosine, directed bilinear and interpretable deficit-coverage score on graded expert rankings with same-topic wrong remedies and equal-valence distractors. |
| 2 | When PSD restriction helps scarce expert labels without sacrificing the strong encoder | OASIS is a direct prior counterexample; generic method novelty is low. | Learning curves with matched signed/PSD heads, matched rank/norm controls and unchanged Qwen. Hold out original case families/transcripts; measure expert nDCG/Recall, graded fidelity and uncertainty. |
| 3 | Which semantic variations are invariant under a specified principle and which must change retrieval | Robustness and metric-learning theory precede it; factual and ethical invariance need new validation. | Separate harmless wording/irrelevant-fact edits from consent, responsibility, coercion and victim-role changes; require selective sensitivity and stable ranking across Spanish/English versions. |
| 4 | Whether indefinite expert similarity carries reproducible information | WIPS/Krein methods make the machinery old; diagnostic application may be useful. | Bootstrap people and case families; examine stable signed components under development-fixed mappings, then test frozen out-of-sample scorer. Compare retrieval gains, not matrix reconstruction alone. |

For priority 1, train only on independently graded pairs/triplets or structured expert needs/coverage annotations. Keep human judgments separate from synthetic expectations and LLM rationales. Include multiple acceptable remedies and incomplete remedies. Evaluate directed adequacy independently of moral approval or topic similarity. A useful positive result is improved expert retrieval of partial and complementary responses with transparent residual deficits.

For priority 2, causal attribution is limited to the narrow restriction actually changed. Same backbone, features, fitting target, capacity controls, tuning budget and splits are necessary. A bi-encoder versus cross-encoder contrast cannot isolate PSD. A PSD head beating only an under-regularized signed head should be reported as ordinary regularization, especially when unchanged Qwen remains stronger.

The constraint should be imposed only within a fixed, explicit condition. Mixing theory labels, undefined rating scales and role directions into one Gram matrix can fabricate an apparent contradiction. A noncompensatory rule such as requiring coverage of every critical need should compete against average similarity where the legal task demands it; its admissibility must come from domain annotations rather than convenient geometry. This review has not established that JEP expert judgments satisfy such a rule.

## Abandon or defer

- Abandon novelty claims based on PSD alone, cosine-to-distance conversion, signed diagonal weights, or the existence of a moral embedding space.
- Abandon architectural PSD as evidence of moral reasoning or correctness.
- Abandon generic harm→repair reflection/inverse assumptions; preserve typed direction and irreversibility.
- Defer richer non-Euclidean machinery until simple frozen-encoder baselines fail on independently reviewed hard cases.
- Reject held-out label completion/projection as an out-of-sample retrieval result.
- Do not count a small synthetic ceiling as evidence that restorative justice retrieval has been solved.

## Audit and limits

The machine-readable ledger contains eleven targeted full-text inspections spanning 2002–2026. It explicitly identifies theoretical papers, image-derived similarity labels and recent preprints; none is presented as an expert Spanish JEP benchmark. This geometry stream found strong prior art against broad method novelty, but does not prove that the intersection with JEP has never been studied. Cross-reference the legal, restorative, conditional-language and moral-representation streams before declaring a literature gap. No quantitative meta-analysis is appropriate across these heterogeneous tasks.
