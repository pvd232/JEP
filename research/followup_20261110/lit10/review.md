# Expert annotation and participation: critical JEP gap review
Review date: 2026-11-10. Agent 10. This is a bounded, structured critical review, not a claim of exhaustive coverage. Eleven primary sources were inspected, including empirical studies and explicitly identified position papers. Full citations, exact inspected sections, data, label authority, limitations and confidence are in evidence_ledger.json.

## Finding
The defensible next contribution is a prospective, source-grounded Spanish hearing study that measures expert effort and preserves justified disagreement. “Use active learning,” “retain disagreement,” “condition on perspectives,” and “use LLM annotations” are established directions. There is no basis here for claiming these ideas are new, nor for promising annotation-hour savings or treating expert consensus as normative truth.

The most direct algorithmic counterexamples are [ACTOR](https://aclanthology.org/2023.emnlp-main.126/) and [DAAL](https://aclanthology.org/2023.findings-acl.658/). Any proposed acquisition method should compare against them or explain precisely which assumption prevents reuse. A few labels or an entropy score cannot distinguish missing evidence, genuine normative conflict and annotation error automatically.

## What is already covered
| Proposed claim | Closest inspected counterexample | Consequence |
|---|---|---|
| Select which expert labels which item | ACTOR §3–5 | Not a novel general acquisition task. |
| Repeat labels selectively to capture disagreement | DAAL §3.5, §5, §7 | Compare against disagreement-aware acquisition; do not equate uncertainty with error. |
| Preserve minority or individual judgments | Plank §2–4; Jury Learning §4–7 | Separate observed responses from simulated perspectives and explicit aggregation policy. |
| Explain disagreement rather than average it away | Jiang/de Marneffe §3–4; Fleisig et al. §3 | Adopt reason codes and quality controls; label distributions alone do not explain causes. |
| Fewer selected items mean cheaper expert work | Haertel §2–4; Ringger §2–4 | Measure actual time, granularity, correction and evidence-inspection costs. |
| LLM assistance improves annotation | Gilardi §2–4 | Domain-specific utility and source-grounding remain unproven. |
| Participation follows from collecting labels | Suresh §4–5; de Waardt/Weber empirical sections | Task control, refusal, representation and burden must be measured separately. |

The Colombian participation study is especially consequential: adding a labeling exercise can itself impose costs without giving participants power over outcomes. Its findings do not establish that the current JEP project has those failures; they refute treating participation as automatically beneficial.

## Narrow gap and decisive next study
**Candidate gap (moderate confidence):** under-tested integration of measured expert time, typed source evidence, directed harm-to-response coverage, and reason-preserving disagreement for Spanish JEP hearing retrieval. None of the inspected methods establishes effectiveness on this combination. This is an evidence gap in the inspected corpus, not proof of worldwide absence or a claim that assembling existing components is itself methodological novelty.

A feasible next study with Valentina's available expert pool should begin with a small timed calibration session and an agreed task. Do not assume pool size, hours, victim representation or willingness. Determine actual capacity first and report participant roles. Use existing permitted, source-validated excerpts and audio-linked spans where available; no invented human judgments.

**Unit:** a fixed retrieval question/condition, candidate excerpt or harm–response pair, and supporting Spanish source span. Keep separate fields for:
1. Evidence status: stated / defensible inference / unsupported / insufficient context.
2. Harm, reparation, acknowledgment and non-repetition relevance; allow multiple labels.
3. Directed coverage: addresses / partly / does not address / cannot assess, with reason.
4. Explicit normative interpretation, annotator role/ID, confidence and cited evidence.
5. Active reading, decision, evidence-check and correction time, plus pass/stop and burden feedback.

“Cannot assess” must not become a negative harm label. A generic theory prompt must not overwrite the JEP rubric or the interpretation recorded by an actual participant.

**Assistance experiment:** counterbalance source-only, source plus evidence card, and source plus model proposal across distinct matched item sets. Obtain unaided judgments before showing suggestions on an appropriate subset; otherwise anchoring can masquerade as improved agreement. Compare correctness against source support separately from normative agreement. Guidance may improve consistency by suppressing justified differences, so measure both.

**Acquisition experiment:** compare random/diverse sampling, ordinary uncertainty sampling, and an ACTOR/DAAL-inspired strategy with measured cost and diversity. Preserve a random audit stream. Freeze held-out hearing/family groups before selection; do not reuse audit labels to fit timing models, select prompts or tune acquisition. A tiny prospective pool may support descriptive feasibility, not a stable trained annotator-specific model; use simpler baselines if there are too few observations.

**Primary endpoint:** supported relevant items surfaced at a fixed measured expert-time budget, with audit-set recall and unsupported-claim rate. Secondary endpoints: evidence-check effort, reason-coded disagreements, abstention/coverage, individual-label distribution fidelity, burden and perceived control. Report uncertainty by hearing/family, not millions of pseudo-independent pairs.

**Decision rule:** pursue only if assistance or selection reduces effort without losing source accuracy, coverage of less frequent harms, or meaningful disagreement. Revise the interface/rubric if the apparent gain comes from anchoring or easy cases. Abandon an automatic adequacy claim if source evidence cannot support it. This is a study of review assistance; it does not authorize an automated legal or restorative judgment.

## Synthetic and weak supervision boundary
Synthetic fixtures can stress-test invariants, missing-context handling, role swaps and unsupported conclusions. Their expected labels remain synthetic. LLM proposals remain a separate supervision source until a source-grounded expert audit demonstrates utility. This lane did not deeply review a weak-supervision generative-label-model method, so it makes no novelty claim for that literature and no recommendation to build one overnight.

## Review limits and publication
English toxicity, POS and social-media annotation dominate the inspected algorithmic evidence; Spanish testimony, long-context audio verification, trauma burden and jurisdiction-specific interpretation are material transfer gaps. Pairwise preference elicitation was screened but not deeply reviewed; conclusions about that subfield remain open. No fieldwide “first” claim is warranted.

Publish this review, evidence ledger and search log with the overall synthesis. Cached full PDFs are internal reading copies; do not publish them to GitHub. No expert labels, prospective timing data, causal benefit or annotation-hour savings were generated by this review.
