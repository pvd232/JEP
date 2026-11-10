# Ethical theory, moral geometry and reasoning-to-encoder: JEP gap audit

Review date: 10 November 2026. This specialist review inspected relevant methods and limitations in ten primary papers. The reproducible search boundary, exclusions and unfinished candidates are in [search_log.json](search_log.json); exact source locations and paper-level evidence are in [evidence_ledger.json](evidence_ledger.json). This is a systematic component of the wider review, not a claim to have exhausted every database.

## Verdict

The broad novelty claims are already occupied: moral sentence spaces, moral-space reconstruction, theoretical scaffolding, layerwise moral conditioning, framework-specific probes and contextual activation directions all have direct precedents. The promising JEP question is narrower: can a representation recover the relevant evidence across unfamiliar accounts while respecting an explicitly requested interpretation, preserving victim-reported facts, and distinguishing a useful rationale from a prompt or label artifact?

## Closest work that defeats easy novelty claims

| Ingredient | Closest inspected precedent | Consequence |
|---|---|---|
| Moral sentence space | Park et al. (2024), [§3](https://aclanthology.org/2024.findings-eacl.45.pdf) | Moral embeddings and contrastive moral labels are established. |
| Human/model moral geometry | [Verheyen–Peterson](https://doi.org/10.1007/s13164-020-00495-5); [Tang](https://doi.org/10.1007/s43681-026-01368-w) | Another pooled moral-space plot is insufficient. |
| Theory-guided reasoning/distillation | [Structured Moral Reasoning](https://aclanthology.org/2025.emnlp-main.1541.pdf); [MET](https://arxiv.org/abs/2607.11736) | Adding ethical scaffolds is an established method. |
| Layerwise response to moral prompts | [Kim et al.](https://aclanthology.org/2026.acl-long.2002.pdf), §5/Appendix H | Moral-conditioning layer curves are not themselves new. |
| Framework-specific representation | [Xu et al.](https://arxiv.org/html/2603.23659v1), §3/Limitations | Template confounds and noncausal probes are documented problems. |
| Similarity improves value learning | [Wynn et al.](https://proceedings.neurips.cc/paper_files/paper/2024/file/3578fd44b2381db12bf16e28a667c934-Paper-Conference.pdf), §§3–4 | Useful moral representations need downstream evidence. |
| Rationale versus verdict | [Machidon et al.](https://arxiv.org/html/2608.12368v1), §§3–5 | Matching a label does not establish matching grounds or causal reasoning. |
| Moral contextual difference vectors | [Sauter–Schirmer](https://aclanthology.org/2026.emnlp-main.178.pdf), §6.1 | Contextual activation subtraction/steering already exists. |

## Ranked, qualified opportunities

**1. Within-case factorization: fixed value, varied theory, stable factual evidence. Confidence: moderate.** MET separates value systems from theories; Xu uses benchmark partitions and Kim uses broad developmental frames. These inspected methods do not establish the proposed JEP evaluation on identical narratives with independently labeled conditional relevance. Build one factorial set in which the factual harm is unchanged, a requested theory changes the salience of responsibility or relationship, and lexical/syntactic nuisance changes are crossed separately. Test cross-family retrieval against factual extraction, theory-only prompts and neutral-role controls. A positive result must improve expert relevance while retaining factual harm evidence. The theory must not license erasing a victim's reported injury.

**2. Grounded reasoning views as retrieval aids, rather than shared verdict tokens. Confidence: moderate.** Existing reasoning scaffolds do not answer whether their views improve this retrieval mandate. Compare raw accounts, extractive evidence cards, generated grounds, and grounds with verdicts removed. Match length and add shuffled-theory and same-verdict/wrong-evidence distractors. Experts label supporting spans and relevance, not a model-generated score. Freeze generation and family splits before scoring. A useful result is improved recall of supporting evidence at fixed review effort, not greater clustering by theory name. Treat rationale faithfulness as a separate intervention question.

**3. Selective invariance with role-sensitive negatives. Confidence: moderate-high as an evaluation need; low as generic methodological novelty.** Xu's explicit paraphrase confound and Contextual MoralChoice's relevant variations motivate a stricter crossed test. Consistent renaming, agent-preserving passive voice and irrelevant presentation changes should preserve a specified abstraction. Consent or role reversal should alter agency/responsibility comparisons when relevant, while holding an outcome-only abstraction fixed. Require retrieval stability and sensitivity together. Controls must include a condition-aware lexical or factual-rule baseline, not only an unconditioned embedding.

**4. Disagreement-aware conditional human similarity linked to retrieval. Confidence: moderate.** INDSCAL already models respondent weighting, so individualized geometry alone is not a contribution. The opportunity is collecting small expert pools' condition-specific comparisons and preserving disagreement when those comparisons guide JEP retrieval. Compare aggregate scoring with separate views/abstention at equal coverage. Evaluate held-out narratives and experts; do not complete a test-label matrix and then call its projected fit generalization.

## What should change in the next experiment

Keep factual harm representation and normative evaluation as distinct outputs. Use explicit dimensions: who suffered what, its severity/time course and evidentiary status; then add requested theoretical views. Include implicit livelihood loss, collective/cultural harms, uncertain speaker knowledge and actor–victim role contrasts. These proposed case types require Colombian expert review before becoming ground truth.

The primary outcome should be useful evidence retrieval across source families, with source-span support and review effort. Similarity correlation, layer plots and matrix diagnostics are secondary. This scope can inform JEP's harm/reparation/acknowledgment/non-repetition mandate without asserting that a geometrically coherent encoder decides what justice requires.

## Counterevidence and remaining search

A fixed harm/theory factorial may already appear under different terminology. Before a novelty claim, inspect the uncompleted candidates in the search log, forward citations, analogy-based legal retrieval, culturally grounded moral benchmarks and restorative-justice NLP. The wider review's Spanish/domain specialists should test Colombian coverage. Language-level Spanish performance is not sufficient evidence of local cultural validity.

## Works cited

The linked ledger contains complete titles, authors, year, venue/preprint status, exact inspected sections and DOI/URL for all ten works cited above. One arXiv item's displayed date is inconsistent with its identifier; the ledger flags that metadata uncertainty. No absence claim here means “nobody has done this.”
