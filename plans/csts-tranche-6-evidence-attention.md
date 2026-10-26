# Tranche 6: evidence supervision on the condition-dependent similarity readout

## Decision and motivation

Run this bounded follow-up after the reviewed reference-correction tranche if its remaining overnight allowance permits completion. Fit two small attention heads over the same frozen selected Qwen + LoRA token states. One learns from similarity ratings. The other receives an additional loss that directs its attention toward previously accepted, copied teacher evidence. Reuse the archived Qwen comparator; perform zero native-baseline fitting or reproduction. Keep training seed 7.

The previous FLAN experiment found aligned evidence → ratings test Spearman **0.606654**, with ratings → ratings **0.516796** and shuffled evidence → ratings **0.537700**. The Qwen evidence-pretraining experiment found evidence → ratings **0.783645**, with ratings → ratings **0.788505**; the paired difference interval was **[−0.013408, +0.003454]**. Those observations motivate testing whether evidence supervision helps when it directly controls the token aggregation used for similarity. They supply no measured result for the present architecture.

The implementation already generated condition-specific copied evidence spans, with a separate teacher check. FLAN learned those answer tokens through its decoder while similarity pooled passage-token states. Qwen learned answer-token prediction after the embedding prefix and used the prefix's EOD representation for similarity. The new head makes the supervised probabilities themselves the pooling weights used by the similarity calculation. Both the existing frozen encoder and the information available at prediction time remain explicit.

This is a new readout architecture inspired by the evidence-localization idea. IPED's Level Predictor supplies a related architectural motivation: fused candidate-level/block states query its evidence features. Its reported relation-class probability vector is a classifier output. A free-text condition query and evidence-supervised token pooling are the construction defined here. Exact IPED model replication is outside this experiment.

## Inputs and fixed provenance

Use the existing selected ratings-only Qwen checkpoint, SHA-256 `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`, model `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`. The prepared training, validation, and existing test splits remain exactly those in `configs/csts-tranche-5.json`. Every new head fits the same rows left after the same deterministic 16-group bank exclusion. The frozen parent previously trained on the original training partition.

The teacher cache is `csts_data/teacher_answers.jsonl`, SHA-256 `1dcd743762cfad9f42b78775510c526e3ce6dd0c51716caf4df3234442ac1c94`. Its existing preparation path is recorded in `configs/csts-qwen-evidence.json` and `csts_pilot/qwen_evidence_run.py`. The cached records retain source passage, condition, generated JSON, accepted evidence, and verifier response. `checked_cache` rechecks IDs, duplicated records, source support, JSON parsing, and the verifier's acceptance. Only training passage-condition records produce span targets. Validation and test extraction reject a teacher-cache binding and store zero target mass.

Pass the original prompt and append its explicit attended EOD:

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
Query: {passage}<|endoftext|>
```

Use the same pinned tokenizer, a 160-token ceiling, and deterministic original two-pair, left-then-right forward batches. Tokenize without truncation. Obtain character offsets in the same tokenizer call, then require the token IDs to match the existing `token_sequences` output exactly. Record original token IDs, condition positions, passage positions, local passage character offsets, packed-state boundaries, and comparison occurrence indices. Special tokens, EOD, separators, instruction text, and padding receive no pooling weight.

## Forward calculation

All vectors in the equations below are columns. For a passage-condition input, let \(n\ge1\) be its number of selected passage-token positions and let \(m\ge1\) be its number of selected condition-token positions. Let \(d=4096\), \(r=128\), and \(p=512\) be the backbone width, query/key width, and final embedding width. Let \(h_i\in\mathbb R^d\) be the frozen final hidden state at passage position \(i\), and let \(g_j\in\mathbb R^d\) be the frozen final hidden state at condition position \(j\). Define

\[
g=\frac1m\sum_{j=1}^{m}g_j.
\]

The condition positions precede the passage in Qwen's causal input. Their hidden states contain the instruction and condition prefix. Each selected passage state can incorporate the preceding condition and passage prefix through the frozen transformer. An earlier passage token has no access to later passage tokens. Qwen's pretrained retrieval readout uses the final token; this new aggregation tests whether supervision can make these earlier contextual states useful for similarity.

For any \(x\in\mathbb R^d\), define the non-affine layer-normalization operation used by the attention keys and query:

\[
\mu(x)=\frac1d\sum_{a=1}^{d}x_a,
\qquad
v(x)=\frac1d\sum_{a=1}^{d}(x_a-\mu(x))^2,
\qquad
\operatorname{LN}(x)=\frac{x-\mu(x)\mathbf1_d}{\sqrt{v(x)+10^{-5}}}.
\]

Here \(a\) indexes vector coordinates and \(\mathbf1_d\) is the length-\(d\) all-ones column. Learn bias-free matrices \(W_Q,W_K\in\mathbb R^{r\times d}\) and \(W_O\in\mathbb R^{p\times d}\). Define the query \(q\), each key \(k_i\), each logit \(\ell_i\), each attention weight \(\alpha_i\), and the pooled value \(u\) by

\[
q=W_Q\operatorname{LN}(g),
\qquad
k_i=W_K\operatorname{LN}(h_i),
\qquad
\ell_i=\frac{k_i^\top q}{\sqrt r},
\]

\[
\alpha_i=\frac{\exp(\ell_i)}{\sum_{a=1}^{n}\exp(\ell_a)},
\qquad
u=\sum_{i=1}^{n}\alpha_i h_i.
\]

Padding logits receive negative infinity before softmax; padding weights are zero. Every input must have at least one valid passage position. Values remain the original frozen passage states. Define \(\varphi(x)=\max(x,0)+0.01\min(x,0)\), applied coordinate-wise. Define \(D\) as inverted dropout with probability 0.15 during training and the identity during evaluation. The final passage vector is

\[
w=D\bigl(\varphi(W_Ou)\bigr),
\qquad
z=\frac{w}{\lVert w\rVert_2}.
\]

Reject nonfinite features and vectors with pre-normalization length at most \(10^{-8}\). Run the head and reductions in float32, with enclosing native-worker autocast disabled. Preserve float64 when explicitly checking derivatives with a double-precision head. The backbone forward uses the declared BF16 path and remains frozen in evaluation mode.

## Evidence targets and losses

For each accepted training answer, require exactly one exact literal occurrence of its text inside the original passage. Build \(E\subseteq\{1,\ldots,n\}\) from passage-token offsets having positive character overlap with that occurrence. If the accepted answer is present only after canonical normalization, occurs repeatedly, or produces an empty token set, record the missing unambiguous alignment and supply no span target for that occurrence. Preserve its rating comparisons in both arms. This avoids assigning evidence to the wrong entity when the same copied words recur.

For an aligned occurrence, define the fixed token target distribution \(t\in\mathbb R^n\) by

\[
t_i=\frac{\mathbf1[i\in E]}{|E|}.
\]

Here \(|E|\) is the number of selected evidence tokens and \(\mathbf1[P]\) equals one when proposition \(P\) holds and zero otherwise. This distribution is uniform over the copied span's token positions. It is a supervision target; it is unrelated to a teacher vocabulary-probability distribution.

Let \(B\) be the actual number of comparisons in a training batch. For comparison \(b\), let \(z_{b1},z_{b2}\) be its two unit embeddings, let \(y_b\in[0,1]\) be its released rating rescaled through \((\text{rating}-1)/4\), and let \(s_b=z_{b1}^\top z_{b2}\). The rating objective is

\[
L_{\mathrm{rating}}=\frac1B\sum_{b=1}^{B}(s_b-y_b)^2.
\]

Let \(A\) be the set of the batch's individual passage occurrences having aligned evidence. An occurrence can recur through pair sampling. For occurrence \(j\in A\), let \(n_j\) be its passage-token count and let \(t_{ji},\alpha_{ji}\) be its target and predicted weight at position \(i\). Define

\[
L_{\mathrm{span}}=
\begin{cases}
-\dfrac1{|A|}\displaystyle\sum_{j\in A}\sum_{i=1}^{n_j}t_{ji}\log\alpha_{ji},&|A|>0,\\
0,&|A|=0.
\end{cases}
\]

Compute masked log probabilities before the target product, setting masked log probabilities to zero to avoid a zero-times-negative-infinity operation. The empty-target case returns a differentiable finite zero. Targets have unit mass for aligned occurrences and zero mass for unsupervised occurrences.

| Arm | Training objective |
|---|---|
| `attention_ratings` | \(L_{\mathrm{rating}}\) |
| `attention_evidence` | \(L_{\mathrm{rating}}+0.1L_{\mathrm{span}}\) |

The coefficient **0.1** is fixed before new validation/test outcomes. Both heads share all architecture, initialization, minibatches, fitting rows, dropout policy, stopping rules, and optimization settings. Similarity prediction requires the condition and passage; it uses no generated answer or copied evidence target.

## Gradient connection to the actual readout

For one supervised occurrence, the span derivative with respect to its valid logit is

\[
\frac{\partial L_{\mathrm{span}}}{\partial\ell_{ji}}=
\frac{\alpha_{ji}-t_{ji}}{|A|}.
\]

In the evidence arm, multiply this derivative by 0.1 before combining it with the rating derivative. For the rating derivative, let \(\bar z_{b1}=\partial L_{\mathrm{rating}}/\partial z_{b1}\); then \(\bar z_{b1}=2(s_b-y_b)z_{b2}/B\), with the analogous expression for the other passage. Through normalization,

\[
\bar w=\frac{(I_p-zz^\top)\bar z}{\lVert w\rVert_2}.
\]

Here \(I_p\) is the \(p\)-dimensional identity matrix and a bar denotes the derivative of the scalar objective with respect to that variable. After differentiating dropout, LeakyReLU and \(W_O\), let \(\bar u\in\mathbb R^d\) be the resulting derivative at the pooled value. Its attention-logit contribution is

\[
\bar\ell_i=\alpha_i(h_i-u)^\top\bar u.
\]

The learned query and keys therefore receive rating supervision through the same weights that receive span supervision. For combined logit derivatives \(\bar\ell_i\), the attention projections receive

\[
\bar q=\frac1{\sqrt r}\sum_{i=1}^{n}\bar\ell_i k_i,
\qquad
\bar k_i=\frac{\bar\ell_i}{\sqrt r}q,
\]

\[
\nabla_{W_Q}L=\bar q\operatorname{LN}(g)^\top,
\qquad
\nabla_{W_K}L=\sum_{i=1}^{n}\bar k_i\operatorname{LN}(h_i)^\top.
\]

Sum these contributions across passage occurrences. The frozen Qwen and adapter parameters receive zero optimizer updates. Autograd supplies the implemented derivatives; numerical tests check the query, key, output projection, attention simplex, masked CE, padding, exact joins and restored-score behavior.

## Fitting, selection, and stop conditions

Reset seed 7 and every head weight before each arm. Use AdamW with learning rate 0.001, weight decay 0.01, betas (0.9, 0.999), epsilon \(10^{-8}\), batch size 32 comparisons, global gradient clipping at norm 1, maximum 48 epochs, and validation-Spearman patience five. Epoch zero can win; strict improvement replaces selected weights, so ties retain the earlier epoch. Use the same seeded comparison permutations. Select all weights with validation, restore them, then freeze candidate identities and operating cutoffs before candidate test extraction and scoring. Declared split-identity checks can read the existing test file.

Use the existing native comparator's sealed validation predictions. A candidate requires validation Spearman gain at least 0.005, conditional-ordering drop at most 0.01, and false-positive-rate increase at most 0.01 at each system's largest validation cutoff retaining at least 90% recall. Positive ratings are at least 4; negative ratings are at most 2. Middle ratings remain in regression/rank metrics. Rank eligible arms by validation Spearman, then lower FPR, then declared arm order. If neither qualifies, stop before test extraction.

Only the validation-selected eligible arm receives existing-test evaluation. Preserve validation cutoffs. Report full-cohort Spearman, MSE, FPR, recall, conditional ordering, and paired source-group bootstrap intervals using the existing 2,000-draw seed-61024 procedure. A native-baseline gain of 0.005 with the existing FPR/recall/ordering guards is the transfer rule. The verified archived GPT comparator scored **0.8029168452132416** on the same 2,620 comparisons / 1,241 groups, cohort SHA-256 `2c8b6f2b62740c85c376eacd02ef222c2bfacdfe8df5f772a4dd7d52b6d38f1e`. Its provenance is recorded in [the comparator receipt](csts-llm-comparator-provenance.md). Report this exact comparator alongside the archived Qwen score; calculate paired comparisons only from the verified per-row prediction artifact.

Report the validation difference between the two heads even if neither passes. A positive evidence-arm difference motivates additional evidence-localization work; a null or negative difference directs attention toward target quality, condition ambiguity, and the readout's ability to preserve distinctions. Interpret these as outcomes of the fixed tested configuration. No seed reruns, lambda sweep, or architecture grid is included.

Allow at most **80 GPU minutes for training/validation token extraction, 15 GPU minutes per head, and 10 GPU minutes for conditional test extraction**, totaling at most 120 additional GPU minutes. Allow 30 CPU minutes for selection and analysis. Complete no new training after **2026-10-26 12:30 UTC**. Preserve failed attempts and intermediate diagnostics. Native source/environment/artifact identities, progress emission, and asynchronous cloud publication follow the reviewed Tranche 5 contracts. Emit extraction progress every 15 seconds, epoch metrics immediately, and completed-arm selected metrics before starting the next arm.

## Implementation and sources

Core implementation: [`csts_pilot/evidence_attention.py`](../csts_pilot/evidence_attention.py). The native controller is [`csts_pilot/evidence_attention_run.py`](../csts_pilot/evidence_attention_run.py). Independent MOA review and meaningful CPU tests must pass before this new follow-up launches.

Grounding: [FLAN evidence controls report](https://github.com/pvd232/JEP/blob/experiment/csts-tranche3-evidence-controls-20261024/training_outputs/csts_tranche3_report.md); [Qwen evidence report](https://github.com/pvd232/JEP/blob/experiment/csts-qwen-evidence-20261024/training_outputs/csts_qwen_evidence_report.md); actual [`answers.py`](../csts_pilot/answers.py), [`joint.py`](../csts_pilot/joint.py), [`qwen_evidence.py`](../csts_pilot/qwen_evidence.py), and [`baseline_models.py`](../csts_pilot/baseline_models.py). The supplied Tu et al. 2024 paper motivates condition-specific answers; the supplied CASE paper motivates condition-aware representations and small supervised readouts. This experiment's equations and labels are the construction specified above.
