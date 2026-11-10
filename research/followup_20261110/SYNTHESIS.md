# JEP moral retrieval: systematic scoping review synthesis

**Decision: pursue a source-grounded, criterion-conditional evaluation; revise the broad novelty and geometry claims.** The inspected literature supports the ingredients. It does not yet establish that their combination helps JEP reviewers find supported harms and adequate responses in new Colombian testimony. A negative synthetic result is diagnostic evidence, not a reason to select whichever theory, prompt, or metric produces a positive score.

Review cutoff: 10 November 2026. Ten specialist lanes retained 105 lane records, deduplicated to **98 sources**; seven records were cross-lane duplicates. Five unique sources are official institutional or normative material. The remaining sources include empirical papers, theoretical work, position papers and a weakly reproducible proposal; **98 is not a count of empirical trials**. This is a bounded systematic scoping review, without an exhaustive PRISMA screening denominator or meta-analysis. The evidence ledger preserves every lane's original record, exact inspected sections and status. The aggregator checked consistency and deduplication; it did not independently reread all 98 sources.

## What is established

| Proposed ingredient | Closest inspected predecessor | What remains unsupported for JEP |
|---|---|---|
| Condition similarity on an aspect rather than generic meaning | [C-STS](https://aclanthology.org/2023.emnlp-main.345/), [L-CSTS](https://aclanthology.org/2024.acl-long.64/), [Hyper-CL](https://aclanthology.org/2024.acl-long.41/), [CASE](https://aclanthology.org/2026.eacl-long.231/) | A moral condition that improves expert source-grounded relevance in Colombian hearings. CASE already includes a Qwen embedding comparison; Qwen conditioning itself is not a first. |
| Infer or explicitly specify moral grounds and ethical theories | [MET/MET-D](https://arxiv.org/abs/2607.11736), [Structured Moral Reasoning](https://aclanthology.org/2025.emnlp-main.1541/) | Encoder retrieval benefit, culturally valid labels, and improved harm/response review. MET-D synthetic character-priority labels are not human JEP judgments. |
| Learn or inspect moral semantic geometry | [Pluralist moral sentence embeddings](https://aclanthology.org/2024.findings-eacl.45/), [conceptual moral spaces](https://doi.org/10.1007/s13164-020-00495-5), [human-value representational alignment](https://proceedings.neurips.cc/paper_files/paper/2024/file/3578fd44b2381db12bf16e28a667c934-Paper-Conference.pdf) | Stable retrieval usefulness for the declared JEP relation; visualization or a human-like map alone cannot establish it. |
| Inspect moral conditioning across layers or steer activations | [Kim et al.](https://aclanthology.org/2026.acl-long.2002/), [Xu et al.](https://arxiv.org/abs/2603.23659), [Sauter and Schirmer](https://aclanthology.org/2026.emnlp-main.178/) | A source-grounded causal mechanism that survives paraphrase, position, role, length and factual-retention controls. Xu specifically exposes probe/steering confounds. |
| Distill reasoning or structured legal elements into retrieval | [KELLER](https://aclanthology.org/2024.emnlp-main.73/), [Elem4LCR](https://aclanthology.org/2024.findings-acl.139/), [DELTA](https://arxiv.org/abs/2403.18435), [RADIO](https://aclanthology.org/2025.findings-acl.220/) | Victim-harm relevance and directed restorative adequacy; charge/citation relevance is a different target. |
| Train/test many invariant and changing perturbations | [CheckList](https://aclanthology.org/2020.acl-main.442/), [Contrast Sets](https://aclanthology.org/2020.findings-emnlp.117/), [counterfactual augmentation limits](https://aclanthology.org/2022.acl-long.256/) | Transfer to unseen operators and hearings under a validated criterion. More augmentation does not guarantee generalization; equal-size controls are necessary. |
| Impose PSD geometry rather than an unconstrained similarity | [OASIS](https://jmlr.org/papers/v11/chechik10a.html), [generalization without PSD](https://arxiv.org/abs/1207.5437), [weighted inner products](https://arxiv.org/abs/1902.10409) | A matched, causal gain from the constraint itself. Shared cosine embeddings are already PSD; a distance transform supplies no new intervention. |
| Spanish legal encoders, cultural evaluation, JEP text mining | [MultiLegalPile](https://aclanthology.org/2024.acl-long.805/), [RoBERTalex](https://arxiv.org/abs/2110.12201), [BLEnD](https://arxiv.org/abs/2406.09948), [Case03 hearing mining](https://doi.org/10.15446/rce.v49n1.119765) | Expert-validated implicit individual, collective and territorial harm retrieval. “First JEP NLP,” “first Spanish moral conditioning,” and “first JEP network visualization” are untenable. |
| Retain disagreement, abstain or actively choose annotations | [Jury Learning](https://hci.stanford.edu/publications/2022/gordon_jury_learning_chi22.pdf), [DAAL](https://aclanthology.org/2023.findings-acl.658/), [ACTOR](https://aclanthology.org/2023.emnlp-main.126/), [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html), [EVIRAG](https://aclanthology.org/2026.emnlp-main.2421/) | Measured expert effort, source accuracy and meaningful disagreement preservation in Spanish hearing review. Predicted perspectives are not consultation. |

**Close proposal-level prior art must also be cited.** [Li, “Large Model Semantic Parsing of Court Records with Bias Calibration Benchmark for Restorative Justice”](https://doi.org/10.54254/2755-2721/2026.30609) explicitly proposes events–roles–measures–outcomes, evidence pointers, retrieval, counterfactual invariance and calibration. Lane05 inspected the complete publisher paper and figure. Missing named backbone, dataset counts, splits, numerical reproducibility details and accessible repository limit its empirical weight. Those weaknesses do not erase conceptual priority and do not establish misconduct. A claim to invent that whole pipeline would be unsafe.

The recent [formal Semantic Conditional Similarity framework](https://arxiv.org/abs/2611.08778) is included through lane03's targeted body inspection. Lane01's pending discovery remains pending in its own log; aggregation does not silently upgrade that lane's inspection. Its formal definitions are prior art to inspect when writing mathematical claims, not evidence that a JEP system works.

## Fix the construct before measuring it

“Conditioning on harm” is underspecified. A valid evaluation unit should record:

1. **Source facts and epistemic status:** who said what, when, about whom; explicit assertion, defensible inference, contradiction, unsupported inference or insufficient context. Relevant uncertainty must remain retrievable.
2. **Fixed concept and subject:** for example, deprivation of liberty affecting a named person, loss of community access to a territory, or disrupted cultural transmission. This describes what the reviewer seeks.
3. **Normative authority:** the stated institutional rubric or participant interpretation. An official JEP requirement is authoritative for defining the task, not an empirical ranking label.
4. **Value priorities:** which interests or consequences the condition weights. Holding a concept fixed does not imply all theories rank its manifestations identically.
5. **Ethical theory:** an explicitly operationalized consequentialist, duty-based, restorative or other rationale. A criterion keyword, legal instruction, community standpoint and ethical theory are different conditions.
6. **Target relation:** resemblance between harms; relevance to a question; acknowledgment of a harm; response coverage; implementation status; or guarantees of non-repetition. They need separate judgments.

Theory variation may change normative relevance without changing the underlying testimony or authorizing factual invention. Language is not culture; Colombian, Indigenous and other community interpretations cannot be simulated by Spanish prompts. The official [JEP Case09 source](https://www.jep.gov.co/Sala-de-Prensa/Paginas/JEP-abre-caso-09-investigar-crimenes-contra-pueblos-etnicos.aspx) makes collective and territorial subjects material to task design. It does not provide gold rankings.

Harm-to-reparation is generally **directed and many-to-many**. One response may address only part of a harm; acknowledgment, promised repair, completed repair and non-repetition are distinct. Neither opposite valence nor an algebraic mirror establishes restorative adequacy. Analogical sentence embeddings and reparative-action taxonomies already exist; a universal harm–repair vector is both scientifically weak and normatively questionable.

## Five ranked research directions

The ranking prioritizes JEP usefulness and falsifiability, not the likelihood of obtaining a positive model score. Novelty confidence concerns the inspected corpus, not proof of world-first status.

### 1. Source-grounded, theory-conditional harm retrieval

**Question:** with identical Spanish source facts, fixed harm concept and candidate pool, does an explicit theory/value condition improve expert-judged rankings over ordinary retrieval, concept-only conditioning and a strong structured prompt?

**Nearest counterexamples:** C-STS/L-CSTS/CASE, MET, and actual JEP Case03 mining. The open dimension is their demonstrated joint validity on source-supported individual, collective and territorial harm, rather than conditional semantics or moral judgments in isolation. Candidate empirical gap: moderate confidence.

**Why JEP:** reviewers must find implicit and distributed harms without turning absence of information into a negative harm label. Declare the institutional task separately from optional theory probes.

**Decisive experiment:** freeze a source/hearing-family-held-out Spanish judgment set and rubric before model evaluation. Reuse identical candidate pools under two justified criteria/theories; include conditions expected to alter rankings and wording changes expected not to. Compare BM25, verified frozen encoder, concept-only, theory-conditioned and structured-prompt baselines. Report per-condition nDCG/Recall within the judged pool, evidence-support errors, unsupported cultural inferences and risk/coverage. Corpus recall requires independently assessed omissions or an exhaustively judged bounded transcript.

**Reject/revise:** reject the conditioning claim if gain disappears against the structured prompt, on new hearings, or after lexical/template controls; reject a human-validity claim without independent labels. Do not tune prompts on held-out judgments.

**Human validation burden:** domain practitioners must define and independently judge source support and rankings; affected-community review is required where interpretations are claimed. Preserve reasons and adjudicate factual errors separately from legitimate normative disagreement. Measure actual reading, audio checking and decision time; no hours are assumed here.

### 2. Directed restorative-response coverage rather than a mirror axis

**Question:** can a system distinguish a response that addresses the specific harm from merely positive language, generic apology, punishment, promised action or an unrelated completed intervention?

**Nearest counterexamples:** Li's restorative parsing proposal, [Xiao et al.'s reparative-action mapping](https://arxiv.org/abs/2506.05687), legal element retrieval and order/Tversky embeddings. The gap is expert-validated directed coverage and implementation status in JEP testimony, not invention of typed events or asymmetric similarity. Moderate confidence.

**Why JEP:** restorative adequacy depends on victims, obligations, affected dimensions and implementation; a symmetric resemblance score can conceal omissions.

**Decisive experiment:** annotate addresses/partly/does not/cannot assess for harm–response pairs, with evidence spans and component coverage. Use valence-, topic- and length-matched hard negatives; separate acknowledgment, commitment, completion and non-repetition. Compare directed typed scoring against cosine, text-pair scoring and simple structured attributes. Evaluate both query directions without assuming reciprocal labels.

**Reject/revise:** reject a universal translation/symmetry claim if offsets fail across held-out harms or reverse direction. Reject utility if matched lexical/typed baselines explain performance or if rare collective harms lose coverage.

**Human burden:** practitioners and relevant affected participants must specify adequacy and acceptable partial coverage; implementation claims require source checking. Participation must permit correction and refusal, not merely labeling.

### 3. Criterion-specific invariance with required sensitivity

**Question:** can augmentation teach which changes preserve relevance under one criterion while changing it under another, on unseen edit operators and hearings?

**Nearest counterexamples:** CheckList, Contrast Sets, Tailor, CoBA and negative augmentation studies. Generic invariance, role swaps and “many synthetic directions” are established. Candidate gap is the validated moral/legal preservation contract and cross-operator transfer; moderate confidence.

**Why JEP:** names and presentation may be incidental for one question, while agency, coercion, territorial relation, quotation or temporal status may be decisive. A single global invariant list can erase harm.

**Decisive experiment:** experts freeze preservation/change expectations before seeing model scores. Compare equal-size narrow and diverse augmentation, shuffled/irrelevant controls and no augmentation. Hold out operators and all derivatives of a source family. Measure joint invariance and sensitivity, including constant-predictor failure; report transfer to actual Spanish sources separately from authored fixtures.

**Reject/revise:** reject the generalization claim if only seen templates improve, sensitivity falls, or “unknown” wording drives success. Synthetic expected labels alone do not establish human semantics.

**Human burden:** validate edit faithfulness, scope and criterion-specific effects; source attribution and incident facts must remain stable in epistemic-status interventions. Audit a random sample as well as difficult items.

### 4. Grounded reasoning-to-encoder transfer with mechanism controls

**Question:** does source-grounded structured reasoning improve encoder retrieval beyond directly supplied factual/criterion features, and does a proposed representation intervention explain that improvement?

**Nearest counterexamples:** KELLER, Elem4LCR, DELTA, RADIO, MET-D, Kim/Xu/Sauter and causal probing. Neither rationale distillation nor moral layer plots is new. The JEP-specific retrieval/mechanism link remains a candidate gap; novelty confidence is lower than the practical evaluation value.

**Decisive experiment:** compare raw passage, source-grounded fact card, rationale card, verdict-only, shuffled-rationale, irrelevant-rationale and length-matched inputs using the same backbone and budgets. Preserve facts and test criterion-switch behavior. For a causal claim, intervene on the proposed representation and use neutral-role, paraphrase, position and factual-retention controls. A decodable layer probe or attractive plot is descriptive.

**Reject/revise:** abandon the reasoning mechanism if factual cards or length explain the gain, steering changes answer position rather than criterion behavior, or interventions degrade source fidelity. If representation geometry remains unhelpful, retain useful retrieval engineering without the mechanistic claim.

**Human burden:** audit grounding and omitted facts independently from rationale plausibility; inspect held-out rationales without turning their labels into training data. Generated explanations remain model outputs.

### 5. Measured reviewer effort and reason-preserving disagreement

**Question:** does evidence-card assistance or cost-aware acquisition surface more supported relevant items per measured expert-time budget without suppressing justified dissent?

**Nearest counterexamples:** ACTOR, DAAL, Jury Learning, Plank, Ringger/Haertel annotation-cost studies and [Colombian participation fieldwork](https://doi.org/10.1093/jhuman/huz002). Keeping disagreements or selecting uncertain labels is established. Prospective Spanish hearing effort and evidence-check outcomes remain under-tested in the inspected set; moderate confidence.

**Decisive experiment:** counterbalance source-only, evidence-card and model-proposal assistance on distinct matched item sets. Obtain unaided judgments on an appropriate subset to expose anchoring. Compare random/diverse, ordinary uncertainty and disagreement-aware acquisition, retaining an independent random audit stream. Record active reading, checking, correcting and decision time; separate missing evidence, rubric ambiguity, competing defensible inference and normative conflict.

**Reject/revise:** reject an efficiency claim if fewer labels do not reduce measured effort, support errors increase, minority harms disappear or agreement rises by suppressing legitimate interpretations. Simulated annotators cannot establish participant benefit.

**Human burden:** establish actual willingness, capacity and role before enrollment; allow task/rubric revision and refusal. Expert consensus is not victim consent. Measure burden and control rather than inventing time savings.

## Geometry and the present computational evidence

A PSD constraint deserves a tightly matched ablation only if it answers the target relation. Keep input features, supervision, objective, capacity, selection and compute comparable; intervene on the constraint. A cross-encoder/bi-encoder comparison cannot identify a causal PSD effect. Low rank, projection, regularization and tuning can each explain changes. Test labels must never complete a projection, fit calibration, select rank or tune prompts.

The pilot's reported synthetic ceiling cannot establish moral reasoning, ethical-theory learning or real-hearing retrieval. The compressed heads' improvement over a signed head does not establish improvement over the original encoder. Truncated MET-D inputs do not test the intended condition. These are reasons to audit input and output artifacts before adding training.

Lane09 inspected the original 12-family/48-case fixture and found single-criterion families, conspicuous missing-information cues, and some edits that changed the incident as well as evidence status. Its critique applies to that inspected fixture, not automatically to subsequently revised files. A corrected criterion-switch fixture can test implementation, but remains authored synthetic evidence. Preserve versions and label provenance.

The cleaned C-STS arm is a useful conditional-semantics calibration task and should be preferred over a known flawed original where the protocol specifies it. It remains separate from human moral/JEP validity. Prior Qwen results and compatible outputs should be reused after source/config/model identity checks; unavailable or runtime-incompatible checkpoints must be recorded as missing arms, not silently replaced by a different model under the same name.

## Evaluation, reporting and publication boundaries

Use source/hearing family as the independent group, keeping overlaps, paraphrases, translations and derived cases together. Report raw group outcomes and uncertainty with the resampling unit explicit; dozens of variants from a few stories do not supply dozens of independent observations. Freeze primary comparisons and development-only thresholds. Incomplete judgment pools cannot support total-corpus recall. Abstaining from unsupported assertions must not remove uncertain victim accounts from retrieval.

Keep human labels, model judgments and authored expectations separate in files, metrics and claims. Report negative results, missing arms, resource use and limits; do not chase a positive result by revising the test. A scientifically useful outcome may be that structured source-grounded prompting suffices and learned geometry adds no value.

The review does not establish novelty in every subfield. Weak-supervision and preference-elicitation work was not deeply covered; inaccessible ecological/collective-justice leads remain open. Recent preprints need version-sensitive citations, and one lane flags an unresolved HTML/arXiv posting-date mismatch. Search records are heterogeneous and not all early searches were retained. No statistical pooling across incompatible studies is justified.

Publish authored reviews, ledgers and logs plus this synthesis, merged studies and coverage manifest. **Exclude cached full PDFs, extracted publisher text, screenshots and cache directories.** URLs and section references supply provenance without redistributing reading copies. The execution lead owns benchmark/model publication and should publish their actual versioned outputs separately.

Recommendation: start with directions 1 and 2 as one carefully scoped evaluation, use direction 3 as its diagnostic controls, and attempt direction 4 only after there is a reliable retrieval target. Direction 5 determines whether any model improvement helps reviewers. Pursue useful evidence; revise unsupported novelty; abandon the universal harm–repair mirror or causal-PSD claim unless a matched experiment supports it.
