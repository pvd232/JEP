# Research direction for JEP codebook discovery

Decision memo, 2026-10-26. This connects the C-STS experiments to the supplied project materials. Proposed mechanisms below remain hypotheses. No Spanish JEP benchmark result or new expert review is claimed.

## The research target

The concept note asks whether domain-informed supervision helps an encoder represent particular meanings across new accounts. Its motivating example separates a harm's initiating event from its consequences. The intended uses include retrieval and clustering. The partnership proposal makes the substantive output a traceable evidence corpus and a refined codebook, followed by systematic coding and synthesis. Its extraction stage records a claim's verbatim quotation and source; experts check relevance and later blind-code a sample. [Sources 1, 2]

**The next research question should be whether teaching a reusable passage readout to select supporting evidence improves the distinctions needed to build and review the codebook.** English C-STS supplies a controlled test of this mechanism. JEP usefulness then depends on selecting and grouping distinct claims about reparation, restoration, sanction, and harm while retaining who said what and where.

A passage can express several meanings. The same passage therefore needs several condition-specific views, or several extracted claim units. A single unconditioned cluster label cannot represent that structure. For example, passages sharing the same killing can express different consequences, different reparation demands, and different positions on acknowledgment. This is an illustrative design requirement derived from the project's question, not a newly annotated JEP finding.

## What the experiments establish

| Existing experiment | Observed result | Consequence for the next intervention |
|---|---|---|
| Matched FLAN controls | Ratings → ratings: 0.516796; aligned evidence → ratings: 0.606654; shuffled evidence → ratings: 0.537700 test Spearman. Condition ordering: 80.46%, 84.87%, and 81.13%. [4] | Correctly aligned evidence carries useful learning signal for this model. Investigate where that signal reaches the similarity representation. |
| Matched Qwen controls | Ratings → ratings: 0.788505; evidence → ratings: 0.783645. Difference −0.004860, paired source-group 95% interval [−0.013408, +0.003454]. [5] | The tested auxiliary answer-generation schedule supplied no demonstrated improvement to Qwen. Directly supervising its similarity readout remains a distinct intervention. |
| Tranche 4 readout/subtraction diagnostic | Existing local report records substantial losses for standalone-condition subtraction and passage-only mean pooling; passage-only mean pooling scored 0.207811. [6] | Preserve the selected Qwen readout as the comparator. Any new pooling rule requires its own learned representation and a measured score. |

These results motivate two specific hypotheses. First, Qwen may already encode the relevant answer while its final vector does not select or preserve the distinction the rating needs. Second, answer-token cross-entropy may improve generation through parameters and states whose contribution to similarity is too indirect. The evidence-supervised attention readout tests the first hypothesis and connects the loss more directly to the second. Neither hypothesis is established by the current scores.

Tu's method makes the generated answers the inputs to the similarity model. It explicitly reduces the task to comparing condition-relevant answers; its experiments also report strong results when the answer input carries the condition information without a repeated condition. Our evidence-pretraining experiments still score the original passage representations. The generated-answer representation is therefore another substantive route, especially if the new token readout stays flat. [3, §§5.1–5.3]

## A bounded route forward if overnight gains stay flat

1. **Complete the frozen-feature correction and evidence-readout comparisons.** Keep the saved native Qwen predictions. Use validation to select the construction and the existing test protocol to report its transfer. Record the actual changes to low-rated-pair false positives, high-rated-pair recall, and condition ordering. These distinguish a useful filtering effect from a score change with poor relevance discrimination.

2. **Use the LLM in two explicit roles.** The archived direct pair judge scored 0.8029 in the existing plan. It is a useful performance reference on the verified common cohort. It can also supply training-only difficult-pair scores and passage-specific evidence targets. An LLM that jointly reads both passages has pair-specific reasoning available; a reusable encoder must place each passage independently. For deployment, use a reusable vector to retrieve/group the corpus and reserve pair judgments for ambiguous neighbors, disagreements, and review prioritization. [7]

3. **Test the answer bottleneck when token readout does not solve the problem.** Represent a passage through a short condition-specific answer plus its exact supporting span and a missing-information flag. Train the small encoder on that representation or distill it into the passage encoder. Reuse trustworthy cached teacher answers first. For JEP claims, a useful schema could retain the requested meaning, target, actor, stance, and source quotation. Which fields are necessary is an expert-guided research decision. This route keeps the extracted evidence visible to the codebook analyst.

4. **Make the next human work a compact JEP diagnostic.** Keep the previously discussed 8–12 pooled expert-hour pilot across the four categories as a planning ceiling; it is not an observed annotation budget in these attachments. Reuse each passage reading across its category questions. Collect the supporting quote, an applicability/missing-information judgment, and a small number of informative comparisons: same event/different consequence, same category/different demand, and different wording/same meaning. Record source group and actor. Spend review on model disagreement and boundary cases while retaining a source-sampled component for evaluation. Existing team-reported expert checks do not supply an independently reviewed benchmark for these new distinctions.

The practical success criterion should connect representation learning to analyst work: retrieve more relevant claims at a manageable review burden, preserve distinctive or minority meanings when grouping them, and reduce unsupported or mixed-aspect summaries. Codebook categories should emerge from reviewed evidence and remain revisable. A high C-STS rank correlation alone cannot establish any of these outcomes.

## Benchmark boundary

Our test comprises 2,620 human-reannotated English C-STS comparisons after 214 invalid comparisons were excluded; training and validation use the separately released human/LLM training ratings. The test has already been examined. Caption-level distinctions provide a useful mechanism check, while JEP testimony adds Spanish, long context, causal accounts, institutional vocabulary, contested meanings, multiple claims, and ASR error. [7; 3, §§3–5]

Tu documents ambiguous conditions, inference-policy differences, invalid conditions, and mismatch between binary properties and a graded scale. The JEP protocol should explicitly specify missing evidence, allowable inference, and which semantic facet is compared. [3, §3] The overnight benchmark can support an executable research direction. It cannot replace the pending domain judgments.

## Source map

1. `/workspace/scratch/4547408f28d5/project_sources/02-concept-note.pdf`, p. 1, “The technical question,” “Exploratory analysis,” and “A shared research opportunity.” The pilot accuracy figures in this attachment are team/project-reported exploratory findings.
2. `/workspace/scratch/4547408f28d5/project_sources/05-project-context.docx`, Spanish “Piloto de Investigación” and “Proceso participativo”; corresponding English body paragraphs 47–53 and 59–61. Also `/workspace/scratch/4547408f28d5/project_sources/06-Project-Proposal-JEP-Columbia-English-.docx`, §§4–7.5 and Phase 4/Phase 6. These supplied documents describe the intended workflow and team-reported pilot; they do not demonstrate availability of the new independently reviewed Spanish test set.
3. `/workspace/scratch/4547408f28d5/project_sources/01-Tu-2024.pdf`, printed pp. 1163–1168 (PDF pages 3–8), §§3–6; especially §5.1's answer-input method and Table 5's condition ablation. The paper is **Linguistically Conditioned Semantic Textual Similarity**, ACL 2024.
4. [Matched FLAN report](https://github.com/pvd232/JEP/blob/experiment/csts-tranche3-evidence-controls-20261024/training_outputs/csts_tranche3_report.md), retrieved 2026-10-26. The report identifies these as exploratory one-seed results.
5. [Matched Qwen report](https://github.com/pvd232/JEP/blob/experiment/csts-qwen-evidence-20261024/training_outputs/csts_qwen_evidence_report.md), retrieved 2026-10-26. Its interval is conditional on seed 7.
6. `training_outputs/csts_condition_reference_report.md`, result table and interpretation of passage-only pooling.
7. `plans/csts-tranche-2.md`, opening reference-system description and “Data and label provenance”; `plans/csts-tranche-1.md`, “Data” and label audit description. These record the archived LLM score, source-group partition, examined-test status, and separate test/training label provenance.

Attachment note: `/workspace/scratch/4547408f28d5/project_sources/08-proposal.pdf`, p. 1, is a Spanish-language **LLM model-selection** draft covering XQuAD, XL-Sum, and MMLU-ProX-Lite. Its contents support baseline capability selection; it is not the full current representation-learning or expert-annotation protocol. It supplies no new codebook-discovery result or available independent JEP test labels.
