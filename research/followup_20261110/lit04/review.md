# JEP follow-up literature review: semantic invariance and synthetic robustness

Reviewed 10 November 2026. This is a focused systematic search with twelve primary papers inspected at methods/results level, plus explicit novelty-warning leads. It is not an exhaustive absence proof. The machine-readable ledger contains URLs, DOIs, inspected sections, data/label descriptions, search decisions and a proposed augmentation contract.

## Finding

Generic synthetic perturbation, semantic-role controls, varying one dimension, condition-dependent label preservation and embedding semantic-coherence tests are established methods. The promising contribution is empirical: independently validated Spanish JEP retrieval with explicit normative criteria, joint invariance and sensitivity, epistemic subject/status, and transfer to new source families and perturbation types. Confidence in its usefulness is moderate; confidence in global novelty is low until specialist Colombian/JEP and restorative literature is reconciled.

The initial 98.8% authored-factorial result is an easy-screen ceiling, not evidence of moral reasoning. Passing a larger authored screen would remain diagnostic evidence. Positive results should mean improved independently evaluated retrieval or selective sensitivity, not finding a convenient synthetic score.

## Closest prior work and adverse evidence

| Primary paper | What prevents an inflated novelty claim |
|---|---|
| [Ribeiro et al., 2020](https://aclanthology.org/2020.acl-main.442.pdf) | Prior art for abundant invariance testing, including negation and roles. Adapt as criterion-indexed tests; never globally declare role swap invariant. |
| [Gardner et al., 2020](https://aclanthology.org/2020.findings-emnlp.117.pdf) | Expert-reviewed local contrasts and no model-in-loop test selection are precedents; keep descendants in one source-family split. |
| [Joshi and He, 2022](https://aclanthology.org/2022.acl-long.256.pdf) | Strong counterevidence to 'max out invariants'. Hold out operator types and compare equal-size multi-operator versus narrow-operator augmentation. |
| [Huang, Liu and Bowman, 2020](https://aclanthology.org/2020.insights-1.13.pdf) | Control examples/tokens and expert effort. Compare ordinary labeled source data with synthetic additions at the same budget. |
| [Wu et al., 2021](https://aclanthology.org/2021.acl-long.523.pdf) | Direct counterexample to claiming condition-dependent augmentation itself novel; use generator only as proposal engine, with separate annotation. |
| [Ross et al., 2022](https://aclanthology.org/2022.acl-long.228.pdf) | Prior art for retained-agent passive and explicit role controls. Test role-preserving positives jointly with role-changing negatives. |
| [McCoy, Pavlick and Linzen, 2019](https://aclanthology.org/P19-1334.pdf) | Use same-word role reversals, plausible actors/patients and controls for implausibility. Keyword-only baselines are essential. |
| [Yang et al., 2019](https://aclanthology.org/D19-1382.pdf) | Native Spanish JEP source is reference. A bilingual reviewer must check actor, patient, scope, evidentiality and temporal relations. |
| [Mahajan et al., 2024](https://aclanthology.org/2024.findings-emnlp.436.pdf) | Direct prior art for semantic coherence/invariant-direction embedding tests. Novelty needs explicit JEP criteria and independent validation. |
| [Jin et al., 2025](https://aclanthology.org/2025.emnlp-main.520.pdf) | Triple-based augmentation is existing work. Authority, status or place cannot be presumed spurious in Colombian legal narratives. |
| [Gebreegziabher et al., 2025](https://aclanthology.org/2025.findings-acl.50.pdf) | Direct prior art for holding all but one aspect fixed. Compare review cost and independent validity, not generated volume alone. |
| [Cao, 2025](https://arxiv.org/html/2504.00584v1) | Negation-aware lightweight geometry is prior work. Scope-sensitive weighting and unknown-versus-negative separation need domain validation. |

The strongest warning is augmentation diversity. Joshi and He show that narrow edits can suppress untouched robust features; Huang and colleagues find no advantage over equal-sized ordinary NLI data. Evaluation contrasts can be valuable even when training on them is ineffective. An abundance of generated pairs is therefore a hypothesis to test against natural-data and balanced-operator controls, not a guarantee of semantic understanding.

CheckList and Polyjuice already make expected behavior task dependent. Tailor already gives semantic-role controls. ALIGN-SIM already studies embedding invariants, antonyms and word-order perturbations. Variation Theory explicitly varies one dimension while fixing others. CoBA explicitly changes principal semantic triples while retaining spurious features. None licenses treating arbitrary legal-role or culturally meaningful edits as irrelevant.

## Audit of the actually executed follow-up fixture

Inspected benchmark/build.py, cases.json and lexical_screen.json directly on Columbia. The fixture has twelve hypothetical English families and forty-eight cases, each with one assigned harm condition, four variants and author-synthetic provenance. Its family split is correctly disjoint. Alternating pairs place the same harm kinds and operator types on both sides; it tests new stories within familiar kinds, not unseen-kind/operator transfer. TF-IDF fits all texts, so it is descriptive transductive screening, not an independently fitted held-out baseline.

The main limitation is that each text family has only one condition. Comparing paraphrases and omitted consequences under that single condition cannot measure the proposed same-text change across criteria. The uncertainty perturbations also frequently alter antecedent actions: questioning replaces detention; approaching replaces abduction; nearby damage replaces house burning. These confound missing outcome evidence with a different event. Some paraphrases strengthen facts: the market version changes inability to pay for food into inability to buy food; the missing-son paraphrase drops explicit uncertainty about survival in favor of broader fate uncertainty. These need semantic review if treated as strict invariants.

The presentation variant appends the identical plain-text sentence to every base. It is a useful smoke test only. Unknown variants have overt account-does-not-report wording absent from most stated variants. Models can exploit reporting-style cues. More subtly, uncertainty experienced by relatives is itself a harm; lack of information in the narrator's account is not evidence that relatives were uncertain. Those subjects must be distinct fields.

Minimal changes before freezing Qwen inference:

1. Add two explicit criteria to identical text/candidate sets. Example facts include both forced flight and lost earnings. One candidate preserves flight but restores earnings; another preserves earnings loss but permits remaining at home. A displacement criterion and livelihood criterion should reverse their ordering under the declared synthetic expectations. This is an aspect switch, not yet ethical-theory validation.
2. Preserve the antecedent action verbatim when omitting consequence evidence. Add separate edits for action severity. Mark unknown as unknown, never a negative harm label.
3. Balance negation/reporting style across classes: asserted-outcome cases may contain an irrelevant fact not reported; unknown outcomes can be expressed by neutral omission. Cross these constructions with outcomes rather than tying phrases to labels.
4. Use actor-retaining passives as positives and actor/patient reversals as responsibility-sensitive controls. Do not require role sensitivity under a criterion explicitly stipulated to ignore identity and count total harm only.
5. Freeze families and labels before model outputs; reserve unseen operator combinations. Keep this as an English author-diagnostic layer. Native Spanish and human/expert annotation are missing arms.

A rank reversal alone can be prompted keyword matching. Require both selective invariance and sensitivity, compare unconditioned/base Qwen, conditioned checkpoint, lexical and condition-shuffled controls, and inspect worst-operator results. No thresholds, prompts or case revisions may use final-test outputs.

## Proposed augmentation contract

The contract's unit is a source family. All original, paraphrase, counterfactual and translation descendants stay together. Each condition declares normative authority/value system, ethical theory, comparison criterion, focal actor, affected party, time and epistemic status. A criterion named physical harm is an aspect; naming it does not supply an ethical theory.

| Operator | Expected relationship and validation |
|---|---|
| Retained-agent active/passive | Preserve actor, patient, scope, attribution, modality and time; semantic review required. |
| Consistent pseudonyms | Preserve identity links; invariant only if identity/social/legal role is explicitly irrelevant. |
| Actor/patient reversal | Sensitive for attributed responsibility; not a universal aggregate-harm change. |
| Scoped negation | Record the exact proposition negated; condition-dependent direction requires annotation. |
| Missing information | Unknown rather than absent/false; preserve all other facts and evaluate uncertainty separately. |
| Alleged/admitted/found/denied | Distinguish claim status from event truth; maintain source and focal epistemic subject. |
| Repair target/adequacy | Positive wording alone cannot establish repair; retain whose deficit is addressed, consent and completion. |
| Spanish/English | Preserve evidentiality, roles, time, negation and culturally specific meanings; bilingual adjudication required. |

The JSON records fields, automated checks, review requirements and metrics in executable-friendly form. Automatic checks can catch actor omission, inconsistent entity swaps, number/date edits, truncation, duplicates and split leakage. They cannot certify legal relevance, harm equivalence, cultural meaning, reparation adequacy or theory-dependent judgment. Generated hypotheses, LLM judgments, independent human labels and expert-adjudicated labels must have separate provenance.

Collective harm, culturally specific restoration, legal authority/status relevance, ambiguous causal or evidential claims and bilingual preservation require people with appropriate expertise. A model discriminator may triage candidates; it does not convert proposed labels into human gold. Do not label future reviewer identities or agreement as if review already happened.

## Decisive bounded experiment

Use recovered frozen embeddings first. Compare balanced condition-aware augmentation against equal-token/example and review-effort natural-label controls, a narrow-operator augmentation arm and no augmentation. Train only the permitted small heads and preserve the same backbone/checkpoint outputs. Pair invariant positives with criterion-sensitive hard negatives; do not force all related views close.

Evaluate independently fixed family-held-out retrieval (MRR/Recall), invariant score/rank drift, expected sensitive direction, and joint success requiring both. Report worst operator/criterion, unknown-versus-negated confusion, validity yield and reviewer cost. Bootstrap families, not individual descendants. Additional transfer slices hold out operator types, operator compositions, condition paraphrases and Spanish source domains. More than one slice is needed because source-family separation alone cannot reveal template/operator memorization.

Pursue this empirical benchmark if independent labels and transfer are feasible. Revise if a model only recognizes wording or if generated cases fail validation. Do not expand generation volume or add backbone training in response to that failure.

## Search and exclusion record

Targeted ACL searches covered CheckList, contrast sets, counterfactual augmentation positive/negative studies, Polyjuice, Tailor, HANS, PAWS-X, sentence-embedding negation and 2025–2026 augmentation. Snowballing followed Joshi/He, Polyjuice and Variation Theory. A stronger general search tested restorative justice, transitional justice, JEP harm retrieval and conditional semantic invariance novelty. Exact query themes and dispositions are in ledger.json.

ConSERT methods were inspected as supporting background and excluded from the core twelve because token/dropout contrastive views offer less domain-specific evidence. Secondary summaries and repository mirrors were not used when primary papers were available.

A close adjacent lead must not be erased: [Li, Large Model Semantic Parsing of Court Records with Bias Calibration Benchmark for Restorative Justice](https://doi.org/10.54254/2755-2721/2026.30609). The publisher dates it 18 December 2025 despite the DOI's 2026 suffix. The landing page claims restorative event-role parsing, retrieval, counterfactual invariance and calibration; data are available upon request. Only that primary landing page was inspected here. Methods, dataset identities and reproducibility remain unverified, so its quantitative claims are excluded. It is sufficient to defeat an unchecked claim that nobody connected restorative justice and invariance; specialist review must examine it further.

No new experiment, training, cloud resource, Git commit or publication was performed by this reviewer. The fixture audit was read-only; this report and ledger are confined to lit04.
