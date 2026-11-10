# Restorative justice, harm-response relations, and JEP: critical literature review

**Finding:** the defensible target is evidence-grounded, asymmetric retrieval of responses that address a specified deficit under victim-centered constraints. A universal harm→repair mirror is neither a sound starting assumption nor an unclaimed computational idea.

This is a structured scoped review through 10 November 2026, with **11 inspected primary/official sources**: seven research papers and four institutional sources. It is not an exhaustive PRISMA review. The JEP pages overlap; they are not independent empirical studies. [Search log](search_log.json) records queries, exclusions and coverage limits. [Evidence ledger](evidence_ledger.json) records methods, authority, inspected sections and limitations.

## What prior work already establishes

| Source | Relevant established work | What it does not establish |
|---|---|---|
| [S01: JEP sanctions ABC](https://www.jep.gov.co/Paginas/ABC-de-las-Sanciones-Propias-que-impondr%C3%A1-la-JEP.aspx) | Participation, truth and responsibility are part of the restorative setting. | A universal numeric similarity scale. |
| [S02: JEP 2023 complementary guidance](https://www.jep.gov.co/Sala-de-Prensa/Paginas/Tribunal-para-la-paz-de-la-JEP-adopta-lineamientos-complementarios-en-materia-de-sanciones-propias-y-Trabajos,-Obras-y-Acti.aspx) | Victims have a role in designing and executing proposed sanctions. | That an extracted proposal is implemented or endorsed. |
| [S03: JEP participation guidance](https://www.jep.gov.co/Paginas/participacion-en-la-formulacion-de-politicas.aspx) | TOAR is a restorative component, accompanied by restrictions in the sanction. | Equivalence between punishment and repair. |
| [S04: UN official explanatory note](https://legal.un.org/avl/ha/ga_60-147/ga_60-147.html) | Distinct material and symbolic forms of reparation. | A one-to-one response to every harm. |
| [S05: Xiao et al., AIES 2025](https://arxiv.org/html/2506.05687v2) | Reparative-action taxonomy and computational stakeholder/action coding. | Colombian-hearing response adequacy or embedding translation. |
| [S06: Gilmore & Moffett, 2021](https://doi.org/10.1111/jols.12311) | Empirical attention to continuing victim agency and informal/self-repair. | A representative population estimate or complete-remedy oracle. |
| [S07: Davis et al., 2021](https://doi.org/10.1177/20539517211044808) | Algorithmic reparation as a structural, social and technical project. | That a fairer embedding itself repairs injustice. |
| [S08: Doyle et al., 2024](https://doi.org/10.1177/20539517241270670) | Critique of targeting an overly narrow technical source of harm. | Automatic adequacy of a specialized remedy. |
| [S09: Diallo et al., CoNLL 2019](https://aclanthology.org/K19-1085/) | Supervised sentence-pair analogy, shared encoders and relation shifts. | A novel basis for simply training harm→repair offsets. |
| [S10: Zhu & de Melo, COLING 2020](https://aclanthology.org/2020.coling-main.300/) | Sentence analogies, relation perturbations and candidate-set controls. | Universal arithmetic regularity in arbitrary sentence embeddings. |
| [S11: Li, posted 2025](https://doi.org/10.54254/2755-2721/2026.30609) | An explicit restorative court-parsing/ontology/invariance proposal. | A sufficiently specified, publicly reproducible JEP benchmark. |

### A close computational precedent that must be acknowledged

Xiao et al. use stakeholder-action extraction and multi-label coding, organized into acknowledgment, attribution, remedy and reform. Their methods and limitations distinguish public reporting from private actions and LLM coding from human interpretation (S05, Methods and Limitations). Thus, “computationally distinguish responses after harm” is already prior art.

Li is a close proposal-level counterexample, with insufficient empirical reproducibility. The full PDF was inspected. See S11 in the [evidence ledger](evidence_ledger.json) and [audit note](li_audit.md).

### Why repair is not an inverse

A reflection is a strong mathematical claim: it is distance-preserving and self-inverse. Reparation is ordinarily **many-to-many and context-dependent**. Formal measures can coexist with continuing needs and victim agency; receiving a measure does not imply complete repair (S06, §§5–6). Material restitution, truth, rehabilitation and institutional prevention also address different dimensions (S04, principles19–23).

Consequently, neither a mirror nor a single global translation should define the target. A typed, directed compatibility relation can ask whether a response addresses a specified harm, for specified people, through a specified restorative function. It need not score equally when query and response roles are exchanged. Shared embeddings can still support retrieval; symmetry of cosine must not be confused with symmetry of the underlying normative relation.

## Candidate gaps applicable to the mandate

These are **synthesis and research proposals**, not established absence claims.

| Candidate gap | Confidence and closest counterexample | Decisive JEP experiment |
|---|---|---|
| **Victim-specific, typed harm→response coverage** instead of generic semantic proximity | Medium confidence in a useful evaluation gap within this scope. S05 already codes responses; S09 already learns relational analogy. | Hold out whole narrative families. Rank same-valence remedies addressing the wrong deficit, wrong beneficiary, or only part of a multi-part harm. Compare unchanged cosine, conditioned cosine, and a directed relation scorer. |
| **Response status and evidentiary support**: proposed, ordered, undertaken, completed, or outcome merely claimed | Strong task rationale; novelty uncertain. S02's correspondence process and S11's procedural/evidence schema are close precedents. | Contrast “we propose,” “the court ordered,” “we completed,” and an attributed/denied completion claim. Require supporting spans, actor, beneficiary and temporal status. |
| **Participation-sensitive adequacy without pretending participation is interchangeable with outcome** | Strong normative relevance from S03; benchmark novelty remains medium/uncertain. | Match material benefits while varying informed participation or an explicitly recorded objection. Ask experts for separate coverage and agency labels, retaining disagreement. |
| **Persistent harm despite a reparative response** | Strong conceptual grounding; little direct encoder evidence established here. S06 is the strongest challenge to simplistic closure. | Pair the same historical harm with partial repair. The model should retain evidence that the harm occurred and identify remaining deficits, rather than cancelling the harm representation. |
| **Cross-family relation transfer with hard non-reparative positive controls** | Method novelty weak because of S09/S10. JEP-specific empirical value could still be substantial. | Compare a matched repair, unrelated helpful action, sanction-only response, acknowledgment-only response, and materially useful but unconsented intervention. Report every valid response, not one manufactured gold answer. |

The existing [pilot](../../../training_outputs/moral_geometry_20261110/README.md) already gives a reason to be cautious: its post-hoc translation control did not outperform direct cosine. A new experiment should defeat topic and valence shortcuts before interpreting relation-vector alignment as restorative understanding.

## Minimal annotation and evaluation contract

The following is a **proposed local protocol**:

1. Use authored challenge cases for mechanical checks, then a distinct set of deidentified JEP excerpts that satisfy the project's audio-validation rule. Keep synthetic expectations, model judgments and expert labels in separate fields.
2. Annotate the harm bearer, harm dimension, affected right/capability, responsible actor, response beneficiary, response type, evidence span and status. Permit multiple labels and unknown information.
3. Separate **addresses this deficit**, **covers it partially**, **matches the affected people**, **supports agency**, **is evidenced as completed**, and **is judged adequate**. Do not collapse those questions into positive sentiment.
4. Compare equally positive candidate responses. Include multiple reasonable remedies, not only an obviously correct lexical counterpart. Preserve a fixed candidate pool and family-level splits.
5. Measure multi-relevant Recall@k/nDCG, coverage of separately labeled deficits, unsupported-completion errors, and review effort at fixed recall. If a model abstains, report coverage alongside precision.
6. Evaluate any proposed relation learning against the unchanged encoder, topical lexical retrieval, a condition-aware factual extraction baseline and valence-matched distractors. Select thresholds on development families only.
7. Let expert disagreement remain observable. Retrieved testimony or a plausible response is research evidence for a reviewer, not an automated legal conclusion about sufficient reparation.

Avoid a global demography-invariance rule. Identity or community membership can be relevant to the harm and the meaning of restoration. Specify the morally or legally relevant factors before deciding which edits should leave the target unchanged.

## What to abandon, retain, and pursue

**Abandon as contribution claims:** “embeddings have restorative geometry”; “repair is the semantic opposite of harm”; “training relation-vector shifts is new”; or “ontology plus counterfactual invariance for restorative court texts has not been proposed.”

**Retain as useful engineering:** conditional retrieval, evidence extraction, relation learning and careful calibration, when they reduce expert review effort under an explicitly evaluated mandate.

**Pursue first:** a transparent, expert-reviewed benchmark of **typed deficit coverage, status, participation and unresolved harm**, with difficult positive controls and cross-family transfer. The most credible contribution may be the evaluation and the documented failure modes rather than a new geometric architecture.

## Works cited and inspection record

Full bibliographic metadata, stable links, exact inspected sections, data/language/label authority, caveats and evidence weight for S01–S11 are in [evidence_ledger.json](evidence_ledger.json). Search and access restrictions are in [search_log.json](search_log.json). These linked records form the bibliography and audit trail; sources listed as inaccessible were not used to establish substantive findings.
