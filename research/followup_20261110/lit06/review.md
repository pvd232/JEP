# Legal retrieval lane: JEP harm and response
Date: 10 November 2026. This is one targeted review lane, not a fieldwide absence proof. Eleven primary texts were selectively inspected for methods, data, evaluation and limitations. Findings are author-reported, not reproduced. The evidence ledger records source locations and version caveats.

## Decision
Pursue a victim-centered retrieval and uncertainty benchmark; revise the novelty claim. Structured fact cards, legal-element conditioning, fact–reasoning bridges, hierarchical legal embeddings, synthetic query training and reasoning supervision of encoders all have close precedents. Their adaptation may be useful engineering, but cannot support a claim of methodological novelty on its own.

The strongest defensible contribution is to establish what retrieval means for JEP narratives: whose harm, under which aspect or theory, supported by which testimony, and what proposed response addresses which deficit. Neither matching an offense nor recovering a cited precedent validates these judgments. No result here establishes that a positive-valence response repairs harm, or that a PSD representation reasons morally.

## Closest counterexamples
| Proposed direction | Closest inspected precedent | Consequence |
|---|---|---|
| Rewrite cases as interpretable facets and match facets | KELLER (2024) | Test source fidelity and harm-specific labels; do not claim facet matching is new. |
| Teach encoder explicit moral/legal elements | Elem4LCR (2024) | Internalizing elements is established; validate conditional meaning and label authority. |
| Use reasoning to train the encoder | DELTA (2024 preprint; AAAI2025) | The novelty must lie in faithful theory-conditioned supervision and decisive controls. |
| Connect factual and normative evidence graphs | FR-MEG (2026) | Preserve raw retrieval when graph coverage fails; verify accepted links. |
| Represent missing facts | SAGA (2026) | Explicit unknown facts already exist in retrieval; source-traceable contested testimony remains a task-specific need. |
| Learn a hierarchy of legal embeddings | DSLaw (2026) | Latent hierarchy does not establish expert harm structure. |
| Generate many synthetic training pairs | LEAD (2024), CaseFacts (2026) | Synthetic scale is established; counterfactual validity and human transfer decide usefulness. |
| Hard-negative pooling and realistic evaluation | LeCaRDv2 (2024), CLERC (2025) | Diverse pools and citation benchmarks are precedents; use them carefully rather than equating their labels with JEP relevance. |

## What should be measured
Keep four questions separate: factual support for a claim; relevance to a specified harm aspect; response type; adequacy or eligibility of that response given available evidence. Expert disagreement and “not inferable” are data. An LLM-generated reason cannot silently become a verified testimony fact.

Split hearing/episode families before chunking or fitting. Construct candidate sets with same-event/wrong-harm and different-event/same-harm cases; individual versus collective harms; absence or uncertainty of consent; generic positive language; acknowledgment, sanction, reparation and non-repetition responses that address different deficits. These are candidate challenge categories requiring expert validation, not asserted moral laws.

Compare BM25, raw cached encoder retrieval, conditional retrieval, automatically extracted cards, expert cards and raw-plus-card fusion at the same retrieval budget. Expert cards isolate extraction error; they are an upper-bound diagnostic rather than deployable evidence. Keep condition-label-only, shuffled-condition, shuffled-reason and outcome/verdict-removed controls. Compare factual relevance and conditional harm relevance separately. For reasoning-to-encoder work, use candidate-blind source-supported reasons and freeze prompts before the held-out set.

Report nDCG/Recall/MRR with incomplete-qrel caveats, source-support errors, abstention or uncertainty, and expert review effort at fixed coverage. Pool multiple systems and audit a sample of unjudged candidates. Family-based uncertainty is preferable to treating many related chunks as independent observations. No expert annotations or review-effort measurements currently exist merely because this report proposes them.

## Gaps and confidence
1. **Task and label gap — strongest.** The reviewed datasets generally encode legal relevance via judicial elements, citation, statute applicability, charges or expert legal analogy. These cannot substitute for victim-centered harm and response adequacy. High confidence in the mismatch; only moderate confidence that the broader task is novel.
2. **Epistemic gap — useful, narrower than first appears.** SAGA already represents missing facts. The JEP experiment should test source attribution and preservation of contested/unknown testimony, including who asserted a claim. Do not pitch missing-fact frames themselves as new.
3. **Evaluation gap — necessary adaptation.** LeCaRDv2 already diversifies retrieval pools; CLERC separates citation recovery from generation and exposes fidelity problems. A JEP benchmark needs rare/implicit harm challengers, family-held-out evaluation, and expert usability. This is a concrete contribution if implemented well, not a new metric-space theorem.
4. **Representation gap — experimental hypothesis.** DELTA and Elem4LCR rebut broad novelty claims about reasoning or concepts reaching an encoder. A useful question is whether source-faithful theory conditioning changes retrieval on genuine same-scenario/different-theory contrasts after controlling for words, topics, verdicts and theory labels.
5. **Transfer gap — incompletely searched.** The inspected set is predominantly Chinese and English adjudicated-case work. This supports caution about transfer to Colombian Spanish testimony, oral register and collective/cultural harm. It does not establish that no Spanish, Colombian or transitional-justice work exists. The targeted JEP/Spanish searches were not adjudicated sufficiently to make absence claims.

## Boundaries
NS-LCR demonstrates structured explanations, but visible rules are not an independent proof of explanation truth. CaseFacts separates evidence and verdict judgments; its web-search degradation is specific to its closed evidence evaluation. FR-MEG reports limited validation of generated links, so its pipeline should not license unverified testimony edges. Judicial decisions and charges can leak outcomes unavailable at hearing time; test deployment-available fields only.

## Sources
Each source has a separate evidence entry in evidence.json. Full texts were selectively inspected, not read line-by-line in their entirety.
- KELLER: https://aclanthology.org/2024.emnlp-main.73/
- Elem4LCR: https://aclanthology.org/2024.findings-acl.139/
- NS-LCR: https://aclanthology.org/2024.lrec-main.939/
- LEAD: https://aclanthology.org/2024.emnlp-main.402/
- CLERC: https://aclanthology.org/2025.findings-naacl.441/
- FR-MEG: https://aclanthology.org/2026.findings-emnlp.2013/
- SAGA: https://aclanthology.org/2026.emnlp-main.702/
- DSLaw: https://aclanthology.org/2026.findings-emnlp.853/
- CaseFacts: https://aclanthology.org/2026.acl-long.785/
- DELTA: https://arxiv.org/html/2403.18435v1 ; final venue DOI 10.1609/AAAI.V39I25.34914, final text not inspected.
- LeCaRDv2: https://arxiv.org/pdf/2310.17609 ; DOI 10.1145/3626772.3657887.
