# IPED lead: source check and executable consequence

Research date: 2026-10-26. This memo verifies the proposed IPED connection and supplies an implementation decision. It reports no experimental result.

## Verified paper facts

Zhao, Xu and Jiang's **IPED: An Implicit Perspective for Relational Triple Extraction based on Diffusion Model**, NAACL 2024, extracts entity–relation–entity triples by denoising candidate blocks. Its sentence encoder combines BERT and a bidirectional LSTM. The sentence states have shape \(L\times d\); \(L\) counts sentence positions and \(d\) is the hidden width. Its learned relation table has shape \(K\times d\), where \(K\) counts predefined relation labels. Candidate blocks supply \(N\times d\) level states, where \(N\) counts blocks.

Section 3.3.2 assigns the Level Predictor's **queries to the fused level states**. Its **keys and values come from max-pooled edge–sentence features** produced by the boundary predictors. The resulting \(R_{EVH}\) feeds an MLP and final relation softmax \(P^v\in\mathbb R^{N\times K}\). Thus \(P^v\) names the relation probabilities. The paper supplies no equation for this attention block's projections, pooling axis, attention mask, or head count.

Source: [official paper, §§3.3.1–3.3.2 and Figure 2, pp. 2084–2085](https://aclanthology.org/2024.naacl-long.114.pdf); [ACL publication record](https://aclanthology.org/2024.naacl-long.114/). The PDF pages containing the figure and predictor description were visually inspected.

## Public implementation availability

The paper's `girlsuuu/IPED` URL redirects to [`gentlyzhao/IPED`](https://github.com/gentlyzhao/IPED). The inspected main commit is [`e4ac68a3a74c5caddeda7db37f10448f8e3341f1`](https://github.com/gentlyzhao/IPED/commit/e4ac68a3a74c5caddeda7db37f10448f8e3341f1), dated 2024-07-01; its tree is `837a6e36b50cb71eb42217fbbaeb62fc915768a7`. A recursive tree request returned 16 entries, without truncation: README, MIT license, and NYT/WebNLG dataset files/directories. No model implementation, training script, or model-weight file appears in that snapshot. The releases endpoint returned an empty list. Its [README at the inspected commit](https://github.com/gentlyzhao/IPED/blob/e4ac68a3a74c5caddeda7db37f10448f8e3341f1/README.md) says implementation material remains forthcoming. These observations establish the inspected official release state; they do not establish that no third-party implementation exists.

Evidence endpoints: [recursive tree](https://api.github.com/repos/gentlyzhao/IPED/git/trees/main?recursive=1), [commit](https://api.github.com/repos/gentlyzhao/IPED/commits/main), [releases](https://api.github.com/repos/gentlyzhao/IPED/releases). A machine-readable receipt accompanies this memo.

## What the proposed analogy supports

The useful architectural idea is to let a representation of the requested relation select evidence-bearing text features. That selection can precede the passage embedding used by the similarity objective. This gives our model a direct place to learn which positions matter for a condition, and a direct place to inspect what it selected.

The quoted Gemini description reverses IPED's query and memory roles and conflates its final relation probabilities with an attention map. A learned ID table also provides a different input contract from our natural-language conditions. Our question is whether the semantics of a previously unseen condition can guide a reusable passage representation. Extracting a hidden state from a system trained to recognize a fixed relation inventory does not establish that behavior.

The literal IPED transfer is currently unavailable: we have no released module or trained checkpoint from which to extract \(R_{EVH}\). Its internal attention implementation also cannot be specified exactly from the publication. Training an entire diffusion extractor would add entity-boundary targets, a fixed relation inventory, denoising, and candidate matching to the task. Those choices supply little immediate evidence about our C-STS failure modes.

**Decision:** pursue a small, explicitly defined condition-query readout over frozen Qwen passage states. Give its token weights direct evidence supervision from the cached teacher spans when reliable alignments exist. Treat this as a new UIE-inspired experiment. The IPED reading motivates the role assignment; it supplies neither pretrained features nor evidence that this adaptation will improve C-STS.

## Fully specified minimal attention operator

The following equations define our proposed operator. They are a new design; the paper does not publish these as its implementation.

All feature vectors below are columns. For one passage and its condition, let:

| Symbol | Definition |
|---|---|
| \(n\) | Number of passage token positions admitted by the passage mask. |
| \(D=4096\) | Width of the selected frozen Qwen encoder's contextual states. |
| \(h_i\in\mathbb R^D\) | Contextual state at admitted passage position \(i\), for \(i\in\{1,\ldots,n\}\). |
| \(c\in\mathbb R^D\) | Mean of the contextual states at condition-prefix positions; those positions precede the passage in the causal input. |
| \(a\) | Attention key/query width, proposed value 128. |
| \(b\) | Value/readout width, proposed value 512. |
| \(W_Q,W_K\in\mathbb R^{a\times D}\) | Learned condition-query and passage-key maps, shared across examples. |
| \(W_V\in\mathbb R^{b\times D}\) | Learned passage-value map, shared across examples. |
| \(q,k_i\in\mathbb R^a\) | Projected condition query and passage key. |
| \(v_i\in\mathbb R^b\) | Projected passage value. |
| \(e_i\in\mathbb R\) | Unnormalized attention score at position \(i\). |
| \(p_i\in[0,1]\) | Softmax attention weight; the weights sum to one. |
| \(u,z\in\mathbb R^b\) | Weighted passage representation and its unit-normalized form. |

\[
q=W_Qc,\qquad k_i=W_Kh_i,\qquad v_i=W_Vh_i,
\]
\[
e_i=\frac{q^\top k_i}{\sqrt a},\qquad
p_i=\frac{\exp(e_i)}{\sum_{j=1}^{n}\exp(e_j)},\qquad
u=\sum_{i=1}^{n}p_iv_i,\qquad
z=\frac{u}{\lVert u\rVert_2}.
\]

The denominator \(\lVert u\rVert_2=\sqrt{u^\top u}\) is the Euclidean length. A zero or nonfinite length must fail explicitly. The implementation should use the numerically stable softmax and an exact passage mask. Prefix, separator, padding, and final readout-token positions receive zero attention probability. Two independently encoded passages under the same condition produce \(z_1,z_2\); their predicted similarity is \(s=z_1^\top z_2\). The existing rating target and MSE apply without redefining the task.

The condition contributes through the weights. The weighted values come from passage positions. Contextual passage states already contain information from the preceding condition, so this design does not guarantee removal of condition-related shared directions. It creates an inspectable and trainable selection mechanism.

With the proposed widths, the three bias-free maps contain \(2aD+bD=3{,}145{,}728\) parameters. Qwen and its selected LoRA adapters remain frozen. New token-state extraction is required: the Tranche 5 caches retain the final readout states. Storage and extraction time must be measured before committing to the complete cohort; retaining every token at width 4096 is materially larger than final-token caching.

## Evidence supervision and overnight decision

The follow-up implementation owner is defining alignment of each teacher answer to passage token positions and the evidence loss. Audit those alignments before training. Record copied-span coverage, ambiguity, out-of-passage answers, and truncation. Restrict evidence supervision to valid alignments while retaining all comparison rows for the rating objective. A successful answer-generation run alone supplies no observation that a similarity readout attends to those answer spans.

Run the one fixed seed already selected for the project. Compare with the saved native Qwen predictions and the archived LLM score on their verified common cohort. Use the existing validation gates and fixed test cutoffs. Report low-rated-pair cosine/FPR, high-rated-pair recall, condition-ordering behavior, and span attention mass. These measurements connect a score change to the original concerns about insufficient condition use and shared-prefix inflation.

If attention mass improves while similarity stays flat, investigate whether the extracted answer content preserves the distinctions needed by the rating. If the model assigns weight to accurate spans and still inflates low-rated pairs, inspect the learned value geometry and score calibration. If evidence loss cannot produce stable span selection, the teacher alignment or learned query interaction is the immediate research target. A score gain with strong span selection supports scaling this mechanism into LoRA continuation with explicit gradients and a measured compute allowance.
