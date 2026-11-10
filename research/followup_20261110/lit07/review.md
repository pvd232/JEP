# Layerwise moral representations, causal probes and rationale distillation
Review date: 2026-11-10. Scope: JEP hearing retrieval concerning harm, reparation, acknowledgment and nonrepetition. This is a bounded systematic search lane, not a claim that all relevant literature was exhausted. Ten primary papers were inspected beyond their abstracts; the JSON ledger identifies exact sections and uncertainty.

## What is already established
Generic layerwise moral-conditioning analysis, ethical-theory activation steering, moral-foundation directions and context steering already have direct precedents: [Kim2026](https://aclanthology.org/2026.acl-long.2002.pdf), [Xu2026](https://arxiv.org/html/2603.23659v1), [Yu2026](https://arxiv.org/html/2601.05437v1), [Tlaie2024](https://arxiv.org/html/2405.17345v2), and [Sauter/Schirmer2026](https://aclanthology.org/2026.emnlp-main.178.pdf). Do not pitch finding moral directions or probing transformer layers as new.

Xu is particularly useful negative evidence: ethical-label decoding and steering can reflect templates and response-position bias. Yu explicitly limits its conclusions to English-centric, questionnaire-style evaluations. Neither establishes transfer to Spanish hearing evidence or restorative adequacy.

[RADIO](https://aclanthology.org/2025.findings-acl.220.pdf) already transfers answer-conditioned rationales into retrieval preferences. Thus “reasoning back into the encoder” is a broad direction with substantial prior art, although that paper trains rerankers rather than establishing JEP shared-geometry improvements.

## Best-supported opportunity
The strongest provisional gap is a source-grounded, Spanish, victim-specific conditional-retrieval evaluation that separates:
1. What happened and to whom, including explicitly unknown facts.
2. Which criterion controls relevance: harm identification, acknowledgment, repair addressing that specific harm, or guarantees of nonrepetition.
3. Whether changing the criterion changes rankings appropriately while irrelevant paraphrases and names preserve them.
4. Whether internal interventions selectively alter those rankings while retaining factual evidence.

This intersection was not tested in the inspected papers. Confidence is medium for an applicable empirical opportunity, low for an exhaustive novelty claim. Other lanes must cover Colombian transitional justice, Spanish legal retrieval, human restoration measures and related benchmarks before a publication novelty claim. Ethical theories must have explicit operational rubrics, not merely names. A theory changes the relevance judgment, not historical facts.

## A decisive bounded experiment
Keep a frozen encoder and use existing compatible outputs. Build paired source-grounded families with fixed facts, different legitimate criteria, hard counterfactuals and explicit unknown/stated distinctions. Split by scenario family before generating training views or selecting layers. Human/expert judgments form the primary relevance target; generated theory views and synthetic invariants are auxiliary labels with separate reporting.

Measure family-held-out nDCG/Recall and pairwise ranking accuracy, conditional-change accuracy, irrelevant-change invariance, and unsupported-attribute sensitivity. Report results by criterion and evidence status with family-bootstrap intervals. Retain original query/source lengths and truncation metadata.

For layer analysis, prespecify an all-layer curve and choose any intervention layer/strength on development families only. Final-token end markers can be invariant; inspect source-span pooling and token counts before interpreting a null. Probes require lexical/type and shuffled-label controls [Hewitt/Liang](https://aclanthology.org/D19-1275.pdf).

For intervention, exchange states from matched source/base examples representing a declared harm-bearer, evidence-status or remedy-target variable. Measure selective ranking change against the corresponding high-level counterfactual. This follows [causal abstraction](https://papers.nips.cc/paper/2021/file/4f5c422f4d49a5a807eda27434231040-Paper.pdf); it does not invent patching. Include same-norm random directions, nuisance directions, equal-rank erasure controls and factual-retention checks [amnesic probing](https://aclanthology.org/2021.tacl-1.10.pdf). A drop after ablation alone can be generic damage.

For reasoning-view distillation, compare (a) original text, (b) source factual extract, (c) grounded theory-specific view, (d) verdict-word-stripped view, and (e) matched shuffled view. Keep teacher generation train-only and answer-blind at evaluation. [Turpin2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/ed3fea9033a80fea1376299fa7863f4a-Paper-Conference.pdf) makes generated rationales unsuitable as automatic causal explanations. Record their factual entailment separately from downstream usefulness.

## Stop/go interpretation
Pursue if grounded views improve held-out criterion-sensitive retrieval over factual extracts and survive paraphrase/unknown-fact controls. Revise if improvements disappear under verdict stripping or longer-context/truncation checks. Abandon the specific representation intervention if matched nuisance interventions produce the same effect, factual retention worsens, or only theory-name classification improves. An observational PCA or linear probe result is descriptive evidence, not moral reasoning.

No new backbone or SAE training is justified for this bounded followup. Questionnaire steering can be a sanity check, but it cannot substitute for JEP usefulness. Harm and repair should be tested as typed, directional relations; a geometric inverse or reflection is a hypothesis, not an established restorative principle.

## Remaining uncertainty
The v1 text of Yu reports two models; a search snippet describing fourteen models was not used. Some 2026 papers may share data or contemporaneous framing; publication dates and version identity should be preserved. This lane has not independently audited released code or replicated reported numbers. Listed pending cultural/moral-trajectory papers in the search log were discovered but not verified and must not support conclusions. No JEP expert labels were created in this literature task.
