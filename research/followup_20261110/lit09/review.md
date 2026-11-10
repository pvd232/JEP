# Evaluation literature: conditional harm/reparation retrieval

Review date and cutoff: 2026-11-10. Scope: evaluation design, dependent families, incomplete and disputed relevance, contamination, abstention, and reviewer effort. This is a bounded, auditable systematic search and targeted primary-methods review, not a claim of exhaustive coverage or a quantitative meta-analysis. The accompanying ledger distinguishes empirical studies from a position paper and gives the specific sections inspected.

## Decision

**Pursue a narrower, expert-grounded evaluation contribution; revise claims of generic methodological novelty.** Perturbation invariance, expert contrast sets, disagreement preservation, evidence interventions, and selective answering already have substantial prior art. The potentially useful JEP question is whether an explicit, declared harm/reparation criterion helps reviewers find relevant source passages while preserving who said what and what remains unknown, on new sources at a fixed review budget. Its novelty is a candidate requiring domain-expert and cross-lane verification.

The existing structured synthetic ceiling and the new 48-case fixture cannot establish this. They can reveal implementation mistakes and premise-sensitive behavior. They cannot establish moral reasoning, an ethical theory learned by an encoder, human relevance, corpus recall, or a benefit caused by PSD geometry.

## Closest counterexamples to broad novelty

| Prior work | Established point | Consequence for JEP |
|---|---|---|
| [CheckList](https://aclanthology.org/2020.acl-main.442/) | Task-specific capability, invariance and directional testing | Adding many perturbations is an established evaluation approach. Expectations must depend on the criterion. |
| [Contrast Sets](https://aclanthology.org/2020.findings-emnlp.117/) | Expert local label-changing edits and all-members consistency | A family-level semantic test is useful, but not itself a new metric. |
| [CounterMem, 2026](https://aclanthology.org/2026.findings-emnlp.1054/) | Fixed-configuration evidence deletion/update/contradiction probes | Evidence sensitivity and pipeline localization are already occupied; the paper does not establish internal moral geometry. |
| [EVIRAG, 2026](https://aclanthology.org/2026.emnlp-main.2421/) | Disagreement-aware retrieval and synthesis | Preserving disagreement alone is insufficient novelty. Its own limitations emphasize compute matching and metric direction validity. |
| [CONCURRENTQA/SPIRAL](https://aclanthology.org/2023.tacl-1.51/) | Retrieval QA risk/coverage differs by distribution | Abstention must be evaluated by source/criterion strata, beyond an overall curve. |

CounterMem uses LLM-written interventions and a limited human detector audit. JEP expert-authored, legally meaningful edits would address a different validity problem, but this is an application opportunity rather than proof of a new method. EVIRAG lacks the strict call/token-matched version of its own strategy that would cleanly separate structure from inference expenditure. A JEP comparison should run that control from the start.

## What the current fixture measures

Direct inspection of benchmark/cases.json and execution.json found 12 hypothetical English families, four variants per family, six dev and six test families, and labels explicitly marked author_synthetic_not_expert. The criterion names describe consequences such as livelihood loss, freedom to leave, and ability to remain at home. These are operational harm dimensions, not an explicit utilitarian, deontological, restorative, or other ethical theory.

The fixture tests preservation under a paraphrase or appended presentation detail, plus reduced assertability when evidence is missing. That is a useful smoke test. It does not yet test how rankings change for the same fixed scenario under different ethical theories or criterion choices, since each family has one condition.

Specific threats observed:

- The appended sentence about saving an account as plain text is a conspicuous repeated template. Success can reflect ignoring that suffix rather than broad presentation invariance.
- The unknown variants have explicit absence-of-information wording. A model can learn this surface cue. Include implicit uncertainty, reporting verbs, contradictory witnesses, quoted versus endorsed claims, and affirmative statements that an outcome did not occur.
- Some unknown edits change the event as well as its evidence status: locked-room detention becomes questioning; abduction becomes approach. Such pairs cannot isolate uncertainty handling.
- Unknown relevance and unknown truth must be separated. A passage about uncertain disappearance may remain highly relevant to a reviewer even when a definite deprivation claim cannot be asserted.
- Four variants share a family. Counting 48 independent observations inflates precision. Six test families support descriptive challenge results, not a convincing generalization estimate.
- Source-level partitioning and Spanish testimony remain untested. A split by fictional family does not measure new-hearing transfer.

These findings are fixture-specific, not claims that the new method necessarily fails. Preserve the present fixture as a unit-level challenge set; build the confirmatory benchmark separately.

## Decisive next experiment

The following design is a proposal from this review, not an outcome already obtained.

**Inputs.** Use permission-compatible Spanish hearing/transcript passages with stable source identifiers and, where available, audio-checked evidence spans. Retain original wording and speaker attribution. Select new held-out hearings or source documents before generating variants. Keep paraphrases, overlapping spans, translations and derived scenarios in the same group.

**Condition.** Ask a JEP domain expert to freeze a small set of operational criteria and their theoretical rationale. For each fixed query and candidate pool, evaluate at least two genuinely different criteria. State which consequences, duties, agent intentions, victim perspectives or reparative requirements each criterion treats as relevant. Do not silently equate a theory with a keyword.

**Judgments.** Independently annotate three separate objects: relevance to the declared criterion, whether a factual assertion is supported by the source, and whether a proposed response/reparation addresses the identified harm. Preserve evidence spans, assessor reasons and legitimate alternative rankings. Unknown is a distinct state, not a negative harm label. Source authors, annotators, model judges and synthetic authors remain separate provenance categories.

**Comparisons.** Reuse the same candidate pool across BM25, the verified frozen encoder, criterion-conditioned encoding, and an unconstrained scorer if available. Compare structured prompts as a strong baseline. Match inference and annotation budgets. A geometry comparison needs matched features/objective/capacity and intervention on the constraint; cross-encoder versus bi-encoder alone cannot attribute differences to PSD.

**Behavioral challenge.** Pair criterion-preserving edits with criterion-changing edits on held-out families. Freeze expectations without seeing candidate model scores. Use changes in role, coercion, negation scope, intent, testimony status, temporal relation and reparation adequacy only where experts justify the expected effect. Require both invariance and sensitivity; an invariant constant predictor should fail.

**Retrieval outcomes.** Report per-criterion ranked retrieval quality against the stated judgment set. Incomplete pools do not permit a corpus-recall claim. Pool diverse retrievers plus an independently sampled set of omitted passages; exhaustively annotate a bounded held-out transcript if possible. Report reviewer decisions/time and supported harms found at a fixed review budget. These effort measures are proposed operational endpoints, not validated results of the present pilot.

**Uncertainty and abstention.** Report paired changes at source/family level, raw family results, confidence intervals with the resampling unit explicit, and how many independent groups underpin them. Freeze primary comparisons and development-only thresholds. Report coverage and error jointly, stratified by criterion/source and epistemic status. Abstain from unsupported assertions without discarding uncertain victim accounts from retrieval.

## Why these controls are necessary

[Dror et al.](https://aclanthology.org/P18-1128/) discuss dependent observations and test assumptions; [Berg-Kirkpatrick et al.](https://aclanthology.org/D12-1091/) show why in-domain significance cannot stand in for out-of-domain improvement. Family/source-clustered comparisons are our application of these warnings, and few clusters still give weak uncertainty estimates.

[Lee et al.](https://aclanthology.org/2022.acl-long.577/) motivate duplicate and split-overlap auditing. Grouped splits address known local overlap; they cannot certify absence of contamination in an unavailable pretraining corpus. Record that uncertainty.

[Plank](https://aclanthology.org/2022.emnlp-main.731/) motivates keeping meaningful assessor variation. This is a position/synthesis source, not empirical evidence that a particular JEP annotation scheme improves retrieval. Separate disagreement about factual support from disagreement about a normative criterion.

[Buckley and Voorhees](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=150469) support robust comparison with incomplete judgments, with pooling caveats. bpref does not discover every relevant passage, fix nonrandom pool bias, or provide total-corpus recall.

[SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html) supplies established risk/coverage machinery. A low-error result achieved by excluding many cases must disclose that exclusion; cosine similarity is not automatically a confidence probability.

## Stop/go rule

Pursue if improvement survives new source groups, switches in the declared criterion, epistemic-status challenges, and matched review/compute budgets. Revise if a structured-prompt or lexical baseline explains the gain. Abandon the claimed representation mechanism if behavior improves without evidence that the proposed geometry intervention caused it. Retain useful baselines and annotation resources even if the geometric hypothesis fails.

Gap confidence is moderate for this bounded research design and low for any universal claim that no one has studied harm/reparation geometry. This lane did not establish literature-wide absence. Domain-specific Spanish/JEP sources, ethical-theory work and representation/geometry papers require the other review lanes.

## Audit and artifacts

Eleven primary papers have body-level inspection records in evidence_ledger.json. Methods and limitations were prioritized, with selected appendices where they resolve a specific claim. The 2014 Cormack/Grossman technology-assisted-review paper is a relevant pending lead: author bibliography verified, attempted primary PDF/study URLs returned 404, so no detailed empirical claim is based on it.

search_log.json records search families, inclusion/exclusion and access failures. Downloaded PDFs in this folder are temporary reading caches and must not be included in public repository publication. Only the authored review, ledger and search log are publication deliverables.
