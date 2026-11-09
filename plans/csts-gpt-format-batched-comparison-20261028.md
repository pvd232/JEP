# Matched GPT evidence formats

Generate propositions, entity/fact JSON and equivalent Python objects from the same 239 source inputs. Use 19 matched batches, with identical membership and order across formats. Every batch has distinct connected source groups and conditions, so companion passages never appear together. No ratings, reference answers or previous evidence outputs enter generation.

This replaces the stalled single-request campaign. Preserve that incomplete campaign as an execution diagnostic. The replacement regenerates all three formats under one shared-daemon transport, GPT-6.1 Sol at max reasoning, the same semantic guidance and examples, and a common batch envelope. The protocol and exact schedules were sealed before generation; no response is retried or selected using similarity scores.

Score all formats through the same saved trained proposition checkpoint, SHA `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`. Preserve its existing LoRA weights, condition prompt, 160-token ceiling, EOD pooling, two-comparison layout and cosine scorer. Include original-text and retained direct-GPT scores as references. No training or calibration occurs.

Use original text per unavailable side, including unanswered or malformed evidence, unresolved local references and token overflow. Report each cause separately and retain all 120 pairs. Compare JSON minus propositions, Python minus propositions and Python minus JSON. Report unadjusted exploratory intervals from 2,000 paired bootstrap resamples of the 110 connected source groups. These intervals condition on the frozen generations; they do not measure variability or dependence introduced by the 19 shared model contexts.

This tests evidence representations as inference inputs to a fixed trained model on previously exposed validation examples. Structural validity is separate from semantic fidelity. Better teacher supervision would require a separate matched training experiment.

Upload artifacts asynchronously after each completed batch and GPU stage. Computation never waits for an upload. Verify every publication completed successfully before releasing a runtime or closing the experiment. The checkpoint and previous artifacts have already passed full cloud read-back verification; their [references](../training_outputs/csts_gpt_format_comparison_20261028/durability.json) are retained.
