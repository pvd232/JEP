# GPT evidence formats

Compare the saved GPT propositions with new GPT JSON and Python entity/fact outputs on the same 239 source inputs and 120 validation pairs. The JSON and Python prompts, fields, examples, model alias and max reasoning setting are already frozen in the extraction protocol. Preserve every first attempt.

Score all three representations with the saved trained proposition model, checkpoint SHA `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`, using its existing LoRA weights, condition prompt, explicit EOD, final-token normalization and cosine scorer. Include original-text scores as a control and the saved direct GPT scores as a reference. Run no training, calibration or checkpoint selection.

Use the existing canonical renderer for each format. JSON and Python share the same renderer. Retain the trained model's 160-token limit and two-comparison batch layout. Keep the original passage on each unavailable side, matching the incumbent input-replacement rule. Record unanswered evidence, capture/parse failures, unresolved references and token overflow separately. Preserve all 120 pairs.

Before rendering structured evidence, flag code-style local entity IDs used as fact values when those IDs do not occur literally in the source. Detect whole-token references with digits or underscores, excluding IDs equal to an entity type; do not guess their intended referents. Such records use the declared original-text fallback. Preserve their raw generated content.

Primary comparisons are JSON minus propositions, Python minus propositions and Python minus JSON. Report Spearman and uncalibrated normalized MSE, with 2,000 paired bootstrap resamples of the 110 connected source groups (seed 42). Treat the comparisons as exploratory. Do not filter using semantic fidelity judgments or tune on the resulting scores.

Keep ratings and direct GPT scores outside the GPU inputs. Preserve requests, responses, parser amendments, token IDs, pooled vectors, predictions, code identities and adapter digests. A transport-warning amendment may accept an otherwise complete response only with one completed, tool-free turn and an agreeing final response; retain the original validity flag.

This tests evidence representations as inference inputs to one fixed trained model on previously exposed validation examples. It does not compare training supervision or establish semantic fidelity from structural validity.
