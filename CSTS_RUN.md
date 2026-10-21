# Training on natural C-STS passages

The experiment measures whether a conditional encoder learns similarity ratings on real captions and uses the supplied comparison question. It uses the public C-STS reannotation employed by CASE. The authors combine LLM reannotations with original human ratings. This release supplies sentence pairs, conditions and ratings.

The joint annotation experiment will require answer targets for these passages. This run trains similarity prediction. Its annotation-loss coefficient is zero. The synthetic edit objective also remains outside this run.

## Data

Dataset: `LivNLP/C-STS-Reannotated`, revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b`. The preparation command checks both source SHA256 hashes. It removes rating `-1`, which the release defines as invalid. Released validation becomes the reserved evaluation set.

Canonical caption identities use Unicode normalization, case folding and collapsed whitespace. Connected caption components remain together. Every training component touching an evaluation caption is removed. The remaining components are assigned to training or development using a fixed hash, with an expected 80/20 allocation. Every question for a passage pair stays with its passages. The manifest reports counts, label distributions and output hashes. VIPER snapshots the declared data files. Raw text and checkpoints remain outside Git.

## Model and objective

The backbone is `google/flan-t5-small`, pinned to revision `0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab`. Its encoder is shared between the two sentences. The input is `Condition: {condition}\nPassage: {sentence}`. Pooling averages contextual states for passage tokens. Condition tokens influence those states through attention. A linear map produces 128 coordinates, followed by unit normalization.

For sentence `x`, question `q`, and expert-scale rating `r`:

\[
z_\theta(x,q)=\frac{W\operatorname{mean}_{t\in x}h_\theta([q;x])_t}
{\|W\operatorname{mean}_{t\in x}h_\theta([q;x])_t\|_2},\quad
s=\frac{1+z_\theta(x_1,q)^\top z_\theta(x_2,q)}2,\quad
y=\frac{r-1}{4},\quad
\mathcal L=\operatorname{mean}(s-y)^2.
\]

This score normalization is declared for this experiment. Error on the original 1–5 scale is 16 times MSE on the 0–1 scale. Correlations are unchanged by the positive affine transformation. Results belong to the filtered evaluation protocol described here.

## Training and selection

- A 64-example fitting check runs first. It must reach MSE below 70% of its training-mean reference and 50% of its initial error before the full study starts. These thresholds are engineering checks selected for this run.
- AdamW uses encoder learning rates `1e-5` and `3e-5`. The new projection uses `1e-3`. Weight decay is `0.01`, gradient clipping is `1.0`, warmup occupies 10% of optimizer steps, and the learning rate then falls linearly.
- Batch size is 32 passage pairs. Each epoch visits every training comparison once in a seeded shuffled order. The maximum is eight epochs. Training stops after three epochs without improvement in development MSE. The checkpoint with minimum development MSE is retained.
- The first seed is 7. Each approach receives both learning-rate trials. Development MSE selects its learning rate, with the lower rate breaking exact ties. Seeds 8 and 9 repeat the selected setting. All settings and checkpoints are fixed before final evaluation.
- The comparison approach omits the condition from the input. It receives the same source pairs, initialization seeds, optimizer search and stopping rules. The mean training-rating predictor supplies a simple reference.
- BF16 autocast reduces GPU memory use. Pooling, vector normalization and scoring use float32. Input tokenization is cached. Only the encoder and projection run during similarity training.

## Diagnostics

Save epoch curves, sampled batch losses, learning rates, gradient norms, selected epochs, elapsed time and peak CUDA memory. Save every final prediction with its sentence-pair identity, condition and connected source group. VIPER independently recomputes MSE and Spearman correlation.

Report score means and dispersion, average prediction for each rating, and errors in the predicted change when the same sentence pair is evaluated under two conditions. For unequal target ratings, report ordering accuracy with ties worth one half. These comparisons reuse captions. Source components define the units for uncertainty analysis.

Sources: [original C-STS code](https://github.com/princeton-nlp/c-sts), [CASE code](https://github.com/LivNLP/CASE), [dataset](https://huggingface.co/datasets/LivNLP/C-STS-Reannotated), [annotation protocol](https://livnlp.github.io/CSTS-reannotation/).
