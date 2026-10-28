# Proposition similarity comparison

Compare original passages and refreshed GPT-6.1 propositions on the existing 120 validation pairs (239 source/condition inputs; 110 connected source groups).

- Use frozen Qwen3-Embedding-8B revision `c90816d848505624c2434128dfc61132162a0ee9` with the project's condition instruction, explicit end-of-document token, final-token pooling and unit normalization.
- Change only the passage text: original passage versus canonical proposition claims. Use the same cosine scorer. Run no training or calibration.
- Keep every pair. If either proposition source is unanswered or empty, use the original-text score for that pair. Report fallback coverage and the answered-pair subset separately. Do not filter using fidelity judgments.
- Reuse the saved direct GPT scores. Make no new GPT calls and no native-model calls.
- Primary measure: Spearman correlation with human ratings. Report proposition-minus-original and proposition-minus-GPT differences with 2,000 paired bootstrap resamples of connected source groups (seed 42).
- Also report uncalibrated MSE against normalized ratings, following the project's unclipped-cosine convention. Do not fit a mapping using evaluation labels.
- Reject token overflow rather than truncate; use a common 512-token ceiling and batch size four. Preserve input IDs, embeddings, predictions, model-file hashes and runtime details.
- Keep ratings and direct GPT predictions outside the GPU encoding package. Join them only after the encoding output is complete.

This measures the effect of proposition text on a frozen embedding scorer. The validation sample has prior project exposure. Results do not establish performance on a fresh blind holdout, the effect of training a proposition student, or a cost saving.
