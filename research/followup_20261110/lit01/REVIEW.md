# Conditional similarity: established methods and JEP-relevant gaps

Search date: 10 November 2026. This is one bounded lane of the wider review, not an exhaustive global systematic review. Nine primary papers were included after methods/evaluation inspection. Search strings, screening decisions, section locations and proposed experiments are in [evidence_ledger.json](evidence_ledger.json). The PDFs were inspected beyond abstracts; SEAVER's large PDF was read locally. No quoted JEP testimony was created or treated as validated data.

## Finding

The architecture-level novelty claim is weak. The more defensible contribution is evaluating **which condition-relevant facts are justified by testimony**, and retrieving analogous harms across unfamiliar narratives under explicitly specified interpretations. That is an application/evaluation hypothesis requiring expert evidence, not an established literature-wide absence.

Two particularly important novelty counterexamples:

- CASE already compares its method with LoRA-finetuned **Qwen3-Embedding-8B**, not merely small encoders. See §4.4, pp.9–10. Merely adapting Qwen or adding a small projection is insufficient as a new contribution. [CASE](https://aclanthology.org/2026.eacl-long.231/)
- SCS already studies intervention/output layers and includes **Spanish and German conditional clustering** in Appendix E. “Layerwise moral conditioning” needs a narrower hypothesis; “Spanish conditional embeddings have not been studied” is false broadly. Spanish expert judgments for JEP testimony are a different target. [SCS](https://aclanthology.org/2026.acl-long.50/)

## What prior work already covers

| Work | Covered ingredient | Consequence for this project |
|---|---|---|
| [C-STS 2023](https://aclanthology.org/2023.emnlp-main.345/) | Natural-language aspects and condition-switch comparisons | Moral aspects extend an existing task. |
| [L-CSTS 2024](https://aclanthology.org/2024.acl-long.64/) | Ambiguous/missing evidence, inference rules, QA answers and typed features | Explicit evidence sufficiency must go beyond existing error handling. |
| [Hyper-CL 2024](https://aclanthology.org/2024.acl-long.41/) | Condition-generated projections and amortized caching | Dynamic ethical subspaces are not new by construction. |
| [CSR 2024](https://aclanthology.org/2024.emnlp-main.963/) | Condition-sensitive token routing | Salience reweighting is an established baseline. |
| [SEAVER 2024](https://aclanthology.org/2024.findings-emnlp.5/) | Attention-based mitigation of irrelevant features | “Remove distracting narrative detail” needs task-specific evidence. |
| [CCL 2025](https://aclanthology.org/2025.coling-main.306/) | Adaptive score-aware contrastive optimization and controversial negatives | An abundance of synthetic negatives alone adds little. |
| [Reannotation 2025](https://aclanthology.org/2025.emnlp-main.1373/) | Condition cleanup, combined annotation signals, overlap concerns | Keep the user's cleaned cohorts and original partition identities. |
| [CASE 2026](https://aclanthology.org/2026.eacl-long.231/) | Conditional pooling, subtraction, shared projections and Qwen adaptation | These are controls or starting points, not fresh inventions. |
| [SCS 2026](https://aclanthology.org/2026.acl-long.50/) | Internal conditional/unconditional contrast, layer analysis and language transfer | Output subtraction is neither a faithful reproduction nor a broad novelty claim. |

## Four candidate gaps worth testing

### 1. Evidence sufficiency rather than forced similarity

L-CSTS permits high-confidence direct inference and excludes invalid cases (§3.3). The reannotation work also recognizes conditions whose evidence cannot be inferred (§2.1.2). Thus, unknown information is not an undiscovered problem.

The proposed JEP extension is to **retain uncertainty as an evaluated state**: explicit harm, supported implicit harm, and insufficient evidence. Annotate the supporting span and the inference warrant separately from similarity/relevance. A model should not equate an unstated harm with absence of harm or hallucinate details to produce a confident match.

Decisive comparison: raw conditional embeddings, QA/extractive evidence, and pairwise reranking on the same expert-labeled pool. Report unsupported-inference rate, selective Recall@k, review effort and coverage. Separate genuine expert disagreement from annotation error. Confidence: moderate within this reviewed core; broader NLI/uncertainty literature must be cross-checked by the corresponding review lane.

### 2. Spanish and culturally situated expert meaning

CASE explicitly evaluates English and identifies multilingual conditional datasets as future work (§6). SCS's Spanish review-clustering appendix narrows that opening: language transfer itself is not enough.

A credible JEP benchmark would test Colombian Spanish testimony, culturally specific implicit harms, collective loss and condition interpretations reviewed by relevant experts. A translated English synthetic template is not sufficient cultural validation.

Decisive comparison: independently reviewed Spanish/English cases, grouped by original narrative family, with language-specific errors and disagreements preserved. Actual transcript excerpts must follow the project's audio-validation rule. Confidence: moderate application gap, pending domain/language-lane counterexamples.

### 3. Selective invariance with role-sensitive negatives

The strongest proposed screen is not universal invariance. A name change should preserve meaning only when the name is incidental; agent–patient reversal should change comparisons under responsibility/control, but might preserve an explicitly outcome-only interpretation.

Freeze a factual profile, a condition's scope and an allowed transformation together. Contrast meaning-preserving paraphrases with minimal edits to consent, knowledge, control, recipient identity and consequences. Include a condition-aware factual parser and oracle evidence cards, since the overnight pilot's easy cases reached ceiling.

This builds on established paired conditions and contrastive negatives. Its plausible contribution is independently audited validity and difficult transfer, not “we generated many perturbations.” Confidence: proposed comparative evaluation, not a proven algorithmic gap.

### 4. Corpus-scale reuse under changing expert criteria

Hyper-CL and CSR directly address reusable sentence/condition representations. A practical JEP study can compare these methods against joint Qwen conditioning and reranking while holding expert relevance and the candidate budget fixed.

Measure end-to-end quality, storage, latency and the cost of adding a criterion. Distinguish retrieving a passage from explaining its relevance. A lightweight method may be useful without being architecturally novel. Confidence: strong engineering relevance, weak standalone novelty without a new empirical finding.

## Recommended execution priority

1. Build and audit the harder evidence-status and selective-invariance dataset first.
2. Freeze expert annotation instructions, family splits and missing-evidence rules before model scoring.
3. Retain simple conditional Qwen, a condition-aware factual baseline, oracle cards and a strong pairwise scorer.
4. Evaluate bilingual/domain transfer separately from synthetic instruction-following.
5. Add a faithful CASE/Hyper-CL/CSR/SCS baseline only when its comparison resolves a specific failure and fits the budget.

No inspected paper establishes that architectural PSD, a conditional embedding cluster, or a 2D projection proves moral reasoning. Shared cosine embeddings already provide an inner-product kernel for a fixed condition; a useful causal geometry experiment must add a restriction to an otherwise matched scorer.

## Coverage and unresolved leads

The search combined targeted ACL/primary-source queries with backward/forward leads from the core papers. Generic Spanish STS benchmarks were excluded as direct evidence for conditional judgments. Dynamic RAG papers using “conditional retrieval” for a retrieval-trigger decision were excluded as a different problem. Secondary mirrors were discovery aids only.

A very recent [formal SCS preprint, arXiv:2611.08778](https://arxiv.org/abs/2611.08778), remains pending full-text mathematical screening. Its apparent set-theoretic formulation differs from free-form aspect conditioning; that is a screening observation, not a verified dismissal. The parent was notified.

## Works cited

- Deshpande et al. (2023). *C-STS: Conditional Semantic Textual Similarity*. EMNLP. [doi:10.18653/v1/2023.emnlp-main.345](https://doi.org/10.18653/v1/2023.emnlp-main.345).
- Tu et al. (2024). *Linguistically Conditioned Semantic Textual Similarity*. ACL. [doi:10.18653/v1/2024.acl-long.64](https://doi.org/10.18653/v1/2024.acl-long.64).
- Yoo et al. (2024). *Hyper-CL: Conditioning Sentence Representations with Hypernetworks*. ACL. [doi:10.18653/v1/2024.acl-long.41](https://doi.org/10.18653/v1/2024.acl-long.41).
- Lin et al. (2024). *Varying Sentence Representations via Condition-Specified Routers*. EMNLP. [doi:10.18653/v1/2024.emnlp-main.963](https://doi.org/10.18653/v1/2024.emnlp-main.963).
- Li, Fan and Gao (2024). *SEAVER: Attention Reallocation for Mitigating Distractions in Language Models for Conditional Semantic Textual Similarity Measurement*. Findings of EMNLP. [doi:10.18653/v1/2024.findings-emnlp.5](https://doi.org/10.18653/v1/2024.findings-emnlp.5).
- Liu et al. (2025). *Conditional Semantic Textual Similarity via Conditional Contrastive Learning*. COLING. [doi:10.18653/v1/2025.coling-main.306](https://doi.org/10.18653/v1/2025.coling-main.306).
- Zhang et al. (2025). *Annotating Training Data for Conditional Semantic Textual Similarity Measurement using Large Language Models*. EMNLP. [doi:10.18653/v1/2025.emnlp-main.1373](https://doi.org/10.18653/v1/2025.emnlp-main.1373).
- Zhang et al. (2026). *CASE – Condition-Aware Sentence Embeddings for Conditional Semantic Textual Similarity Measurement*. EACL. [doi:10.18653/v1/2026.eacl-long.231](https://doi.org/10.18653/v1/2026.eacl-long.231).
- Cheng et al. (2026). *Focusing Condition: Inference-Time Self-Contrastive Steering Elicits Better Conditional Text Embeddings in LLMs*. ACL. [doi:10.18653/v1/2026.acl-long.50](https://doi.org/10.18653/v1/2026.acl-long.50).
