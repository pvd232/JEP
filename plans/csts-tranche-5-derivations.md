# Tranche 5: reference estimation and learned residuals — derivations

This companion defines the proposed frozen-encoder experiment, its gradients, its measurements, and the reference updates a later LoRA experiment would require. The [experiment plan](csts-tranche-5-matched-baselines.md) supplies the execution schedule. Every equation in this file uses browser-renderable math delimiters.

## 1. Conventions and objects

All vectors are columns. For two vectors \(v,w\in\mathbb R^k\), their Euclidean inner product is \(v^\top w\), and their Euclidean length is \(\lVert v\rVert_2=\sqrt{v^\top v}\). Here \(k\) is any positive vector width. A transpose turns a column into a row. The matrix \(I_k\in\mathbb R^{k\times k}\) is the identity. The indicator \(\mathbf 1[P]\) equals 1 when proposition \(P\) holds and 0 otherwise. The symbol \(\odot\) denotes coordinatewise multiplication. A gradient contains the coordinate derivatives of a scalar; a Jacobian contains derivatives of output coordinates with respect to input coordinates.

| Symbol | Definition |
|---|---|
| \(j\in\{1,\ldots,N\}\) | Comparison index; \(N\) is the number of rows in the partition being scored. |
| \(i\in\{1,2\}\) | Passage side in a comparison. |
| \(s_{ji}\) | Text of passage \(i\) in comparison \(j\). |
| \(c_j\) | Condition text for comparison \(j\). |
| \(R_j\in[1,5]\) | Reference rating. |
| \(y_j=(R_j-1)/4\) | Target similarity in \([0,1]\). |
| \(d=4096\) | Encoder readout width. |
| \(k=512\) | Learned head output width. |
| \(\theta_\star\) | Frozen selected Qwen LoRA parameters. |
| \(h(s,c)\in\mathbb R^d\) | Raw, externally unnormalized EOD state from that fixed encoder and the native condition-plus-passage prompt. |
| \(c_0\) | Fixed generic condition string: `overall meaning`. |
| \(M=16\) | Number of passages in the reference bank. |
| \(m\in\{1,\ldots,M\}\), \(x_m\) | Bank index and its training passage. Bank passages have distinct connected source groups. |
| \(W\in\mathbb R^{k\times d}\) | Trainable bias-free head matrix for one arm. |
| \(\beta\in\mathbb R\) | Trainable correction logit for an arm with a fitted coefficient. |
| \(\alpha=\sigma(\beta)\) | Correction strength, with \(\sigma(t)=1/(1+e^{-t})\). Exact real arithmetic gives \(0<\alpha<1\) for finite logits. Floating-point evaluation can round extreme values to an endpoint. |

The encoder's internal normalization stays inside \(h\). External unit normalization is defined only when it appears below. The selected checkpoint already encountered the original training data during LoRA training. Bank-group exclusion in this experiment applies to the new head-fitting cohort.

Let \(\mathcal G_B\) be the set of the bank's 16 source groups and \(\mathcal D_{\mathrm{train}}\) the comparison-index set of the original 6,980-row training partition. The shared head-fitting cohort is

\[
\mathcal D_{\mathrm{fit}}
=\{j\in\mathcal D_{\mathrm{train}}:\operatorname{group}(j)\notin\mathcal G_B\}.
\]

Here \(\operatorname{group}(j)\) returns the connected source group of comparison \(j\). The four new heads fit the same retained rows. The resulting count is measured and recorded. Validation contains 1,830 original comparisons; the existing test partition contains 2,620 comparisons. The sole native comparator consumes its existing sealed predictions: validation Spearman 0.7825746597420997 and existing-test Spearman 0.7885050017660868. It receives zero new fitting or reproduction updates.

The bank is selected deterministically with hash salt 61026, one unique passage text per selected group. The implementation's ordered hash keys and text tie-breaking rule are part of the bank manifest.

## 2. Raw readouts and the population reference

For bank passage \(x_m\), define its paired conditioning shift and the empirical shared shift:

\[
\delta_{m,c}=h(x_m,c)-h(x_m,c_0),
\qquad
b_c=\frac1M\sum_{m=1}^{M}\delta_{m,c}
\in\mathbb R^d.
\]

The same passage appears on both sides of each difference. All bank examples come from training data. A new condition can be supplied as text to the same fixed bank without using ratings from the partition being scored. Cache keys bind the checkpoint, tokenizer, exact condition and prompt bytes, EOD convention, bank identities, and batching policy.

Bank selection defines the distribution summarized by \(b_c\). The symbol denotes an empirical mean; its interpretation as a removable shared component is an experimental hypothesis.

To describe sampling variability, suppose an idealized collection of independent, identically distributed paired shifts has covariance \(\Sigma_\delta\in\mathbb R^{d\times d}\). Then

\[
\operatorname{Cov}(b_c)=\frac{\Sigma_\delta}{M}.
\]

Let \(\Sigma_c\) and \(\Sigma_0\) be the covariance matrices of conditioned and generic readouts, and \(C=\operatorname{Cov}(h(x,c),h(x,c_0))\) their cross-covariance. Pairing gives

\[
\Sigma_\delta=\Sigma_c+\Sigma_0-C-C^\top.
\]

Positive shared variation can therefore cancel in the paired difference. This variance calculation is theoretical. The supplied code caches the mean bank direction. Individual-shift storage and leave-one-bank-member-out stability measurements remain future diagnostics motivated by this calculation. Distinct source groups reduce direct caption reuse; statistical independence remains a modeling assumption in the calculation.

## 3. Existing native comparator and four new residual constructions

Suppress comparison index \(j\) for one pair. Write \(h_i=h(s_i,c)\) and \(n_i=h(s_i,c_0)\). Let \(r_i^{(a)}\in\mathbb R^d\) be the residual supplied to arm \(a\)'s head.

| Arm | Residual |
|---|---|
| N: existing native comparator | Its original scoring formula is \(z_i^{(N)}=h_i/\lVert h_i\rVert_2\), followed by \((z_1^{(N)})^\top z_2^{(N)}\). This tranche reads the sealed scores. |
| M: same passage | \(r_i^{(M)}=h_i-\alpha n_i\). |
| B: population translation | \(r_i^{(B)}=h_i-\alpha b_c\). |
| P: population projection removal | \(r_i^{(P)}=h_i-\alpha P_c h_i\). |
| C: CASE-style | \(r_i^{(C)}=e_i-a_c\). |

For the projection arm,

\[
P_c=\frac{b_c b_c^\top}{b_c^\top b_c}\in\mathbb R^{d\times d},
\qquad
q_i=P_c h_i
=b_c\frac{b_c^\top h_i}{b_c^\top b_c}.
\]

Compute \(q_i\) using the scalar fraction and vector multiplication; storing a dense \(4096\times4096\) matrix is unnecessary. The native comparator's existing scoring rule is the zero-correction endpoint. CASE-style uses a fixed subtraction coefficient of one. The three fitted-coefficient arms initialize \(\beta=0\), giving \(\alpha=1/2\).

The CASE-style vector \(e_i\in\mathbb R^d\) comes from the authors' condition-target prompt using sentence \(s_i\) as context. Its reference \(a_c\in\mathbb R^d\) encodes condition \(c\) under the standalone generic prompt. The [pinned authors' wrapper](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/llm_encoders.py#L71) specifies these strings. This experiment uses our selected checkpoint and declared EOD/readout convention for these prompts, making this arm a local CASE-style adaptation. The [authors' subtraction](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/generate_embeddings.py#L61) and [head](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/CASE_performance.py#L126) motivate its construction.

All references and readouts retain their raw lengths before these operations. No arm applies external unit normalization before subtraction.

## 4. Projection geometry

For \(b_c\ne0\), direct multiplication gives \(P_c^\top=P_c\) and \(P_c^2=P_c\). Decompose

\[
h_i=h_{i,\parallel}+h_{i,\perp},
\qquad
h_{i,\parallel}=P_c h_i,
\qquad
h_{i,\perp}=(I_d-P_c)h_i.
\]

The two components are orthogonal. Projection removal gives

\[
r_i^{(P)}=(1-\alpha)h_{i,\parallel}+h_{i,\perp},
\qquad
\lVert r_i^{(P)}\rVert_2^2
=(1-\alpha)^2\lVert h_{i,\parallel}\rVert_2^2
+\lVert h_{i,\perp}\rVert_2^2.
\]

The intervention scales each input's existing parallel component. Translation moves every input by the same vector \(\alpha b_c\). The sign and magnitude of \(b_c^\top h_i\) determine the projection correction.

Scaling the direction by any nonzero scalar leaves \(P_c\) unchanged. Translation retains the bank vector's length. These are distinct hypotheses about the correction that the task needs.

## 5. Common head, dropout, normalization, and loss

For each side \(i\) of a newly fitted arm \(a\in\{M,B,P,C\}\), define

\[
u_i=Wr_i\in\mathbb R^k,
\qquad
a_i=\ell_\kappa(u_i)\in\mathbb R^k,
\qquad
v_i=D_i a_i\in\mathbb R^k,
\qquad
z_i=\frac{v_i}{\lVert v_i\rVert_2}.
\]

The elementwise LeakyReLU is \(\ell_\kappa(t)=t\) for \(t>0\) and \(\kappa t\) for \(t\le0\), with \(\kappa=0.01\). During head training, the diagonal matrix \(D_i\in\mathbb R^{k\times k}\) contains independent entries \(m_{it}/(1-p_D)\), where \(t\in\{1,\ldots,k\}\), \(m_{it}\) is Bernoulli with success probability \(1-p_D\), and \(p_D=0.15\). Evaluation sets \(D_i=I_k\). This is inverted dropout, so \(\mathbb E[D_i]=I_k\).

The similarity and one-comparison loss are

\[
\widehat y=z_1^\top z_2\in[-1,1],
\qquad
L=(\widehat y-y)^2.
\]

The symbol \(y\) denotes that comparison's rescaled rating. Predictions remain raw cosines. For a fitting batch \(\mathcal B\) containing \(B=|\mathcal B|\) comparisons, the objective is

\[
L_{\mathcal B}=\frac1B\sum_{j\in\mathcal B}(\widehat y_j-y_j)^2.
\]

The four new arms share the head architecture, initialization policy, fitting rows, dropout rate, optimizer schedule, and checkpoint-selection rule. The native model supplies the sole existing frozen comparator through its sealed prediction files. New-head training capacity is part of each candidate's total intervention relative to that comparator.

Reject nonfinite vectors and lengths at or below \(\varepsilon_n=10^{-8}\) at each required normalization boundary. Population arms also require a finite \(b_c\) with \(\lVert b_c\rVert_2>\varepsilon_n\). Coverage failures stop full-cohort scoring. Cache keys and native exceptions support diagnosis; a dedicated comparison-ID coverage artifact remains a future extension. Cohort metrics require all original comparison rows.

## 6. Normalization Jacobian

For \(v\in\mathbb R^k\) with \(n=\lVert v\rVert_2>0\), write \(z=v/n\). Differentiating the length gives \(\mathrm dn=z^\top\mathrm dv\), where \(\mathrm d\) denotes a differential. Therefore

\[
\mathrm dz
=\frac1n\mathrm dv-\frac{v}{n^2}\mathrm dn
=\frac1n(I_k-zz^\top)\mathrm dv.
\]

The Jacobian is

\[
J_{\mathrm{unit}}(v)
=\frac1{\lVert v\rVert_2}(I_k-zz^\top)
\in\mathbb R^{k\times k}.
\]

It is symmetric and annihilates the radial direction: \(J_{\mathrm{unit}}(v)v=0\).

## 7. Cosine-MSE and head gradients

For one comparison, let \(e=\widehat y-y\) be the scalar prediction error. With \(3-i\) denoting the other passage side,

\[
g_{v_i}:=\nabla_{v_i}L
=\frac{2e}{\lVert v_i\rVert_2}
\left(z_{3-i}-\widehat y z_i\right)
\in\mathbb R^k.
\]

Let \(\ell_\kappa'(u_i)\in\mathbb R^k\) contain the coordinate derivatives, equal to 1 on positive coordinates and \(\kappa\) on negative coordinates. The implemented derivative at exactly zero follows the LeakyReLU operator's convention. Numerical gradient checks use inputs away from this kink.

Backpropagation through the head is

\[
g_{a_i}=D_i^\top g_{v_i},
\qquad
g_{u_i}=\ell_\kappa'(u_i)\odot g_{a_i},
\qquad
g_{r_i}=W^\top g_{u_i}\in\mathbb R^d.
\]

The shared head receives contributions from both sides:

\[
\nabla_W L
=g_{u_1}r_1^\top+g_{u_2}r_2^\top
\in\mathbb R^{k\times d}.
\]

For a batch, sum these expressions over comparisons and divide by \(B\). A microbatch contributing a summed loss must divide by the actual effective batch size, including a smaller final batch. This yields the same mean objective under any partition of that effective batch, given identical dropout masks and examples.

The factor \(z_{3-i}-\widehat y z_i\) has squared length \(1-\widehat y^2\). Exact parallel or antiparallel unit outputs have zero angular gradient. This motivates future norm and geometry diagnostics alongside the implemented loss and prediction measurements.

## 8. Fitted correction-strength gradients

During this frozen-encoder experiment, the captured \(h_i,n_i,b_c,e_i,a_c\) are constants with respect to fitted parameters. Define \(g_i=g_{r_i}\) for compactness. The three coefficient derivatives are

\[
\begin{aligned}
\frac{\partial L_M}{\partial\alpha}
&=-\sum_{i=1}^{2}n_i^\top g_i,\\
\frac{\partial L_B}{\partial\alpha}
&=-\sum_{i=1}^{2}b_c^\top g_i,\\
\frac{\partial L_P}{\partial\alpha}
&=-\sum_{i=1}^{2}q_i^\top g_i.
\end{aligned}
\]

For the trainable logit,

\[
\frac{\partial L}{\partial\beta}
=\frac{\partial L}{\partial\alpha}\alpha(1-\alpha).
\]

At initialization, \(\alpha=0.5\) and the sigmoid factor is \(0.25\). Extreme logits give small factors. The implementation records the fitted coefficient. A separate coefficient-gradient trace remains a future diagnostic. The learned coefficient describes the joint scoring pipeline's fitted correction strength.

For fixed references, residual Jacobians with respect to the main readout are \(I_d\) for same-passage and translation arms, and \(I_d-\alpha P_c\) for projection removal. The references have separate derivative paths in a later encoder-training experiment. The identity-residual head calculation is also a useful auxiliary algebra check; the existing native comparator receives zero new head fits.

## 9. Optimization and parameter scale

Let \(\phi\) denote the fitted parameters of one new arm: \(W\), together with \(\beta\) for the three learned-strength arms. For optimizer update \(t\ge1\), concatenate their batch gradients into \(g_t^{\rm raw}=\nabla_\phi L_{\mathcal B}\). The concatenated width is \(kd\) for the fixed-strength CASE-style arm and \(kd+1\) for each learned-strength arm. Apply global norm clipping before the optimizer step:

\[
g_t=g_t^{\rm raw}\min\left(1,\frac{C_g}{\lVert g_t^{\rm raw}\rVert_2+\varepsilon_g}\right),
\qquad C_g=1,\quad \varepsilon_g=10^{-6}.
\]

Here \(C_g\) is the clipping bound and \(\varepsilon_g\) is the stabilizer in PyTorch's clipping coefficient. The matrix and logit participate in the same norm calculation. AdamW uses the clipped gradient \(g_t\), coordinatewise moments \(m_t,v_t\), moment coefficients \(\beta_1,\beta_2\in[0,1)\), learning rate \(\eta_t>0\), numerical stabilizer \(\varepsilon_A>0\), and parameter-group decay \(\lambda\ge0\). Starting from \(m_0=v_0=0\),

\[
\begin{aligned}
m_t&=\beta_1m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2v_{t-1}+(1-\beta_2)(g_t\odot g_t),\\
\widehat m_t&=m_t/(1-\beta_1^t),\qquad
\widehat v_t=v_t/(1-\beta_2^t),\\
\phi_{t+1}&=(1-\eta_t\lambda)\phi_t
-\eta_t\frac{\widehat m_t}{\sqrt{\widehat v_t}+\varepsilon_A}.
\end{aligned}
\]

The square root and division are coordinatewise. The proposed configuration fixes \(\eta_t=10^{-3}\), \(\beta_1=0.9\), \(\beta_2=0.999\), and \(\varepsilon_A=10^{-8}\). Matrix \(W\) has \(\lambda=0.01\); the logit has \(\lambda=0\). Excluding \(\beta\) from decay avoids imposing an additional pull toward \(\alpha=0.5\).

Each epoch visits every retained fitting comparison once in batches of 32, with a smaller final batch allowed. Each of the four new arms resets the same fitting seed 7, head initialization, and permutation generator seed 107. The ceiling is 48 fitting epochs, with patience five on validation Spearman. Epoch zero is an eligible checkpoint. A strict improvement replaces the incumbent; ties retain the earlier epoch. Head operations use float32 on the chosen CPU or GPU device. Encoder readouts are extracted once using their declared backbone precision.

Positive rescaling of the whole matrix \(W\) leaves evaluation cosine unchanged because LeakyReLU is positively homogeneous and final normalization removes that scale. Head decay and optimizer dynamics can still respond to the parameter scale. Validation score quality determines the chosen checkpoint.

## 10. Why raw reference lengths remain relevant

For a nonzero passage readout \(h\) and reference \(b\), let \(z=h/\lVert h\rVert_2\) and \(u=b/\lVert b\rVert_2\). Then

\[
\operatorname{unit}(h-\alpha b)
=\operatorname{unit}\left(z-\alpha\frac{\lVert b\rVert_2}{\lVert h\rVert_2}u\right).
\]

Unit-normalizing both operands first would replace the input-specific length ratio with one. This experiment fixes the raw operation and fits its scalar coefficient. Passage/reference norm-distribution reporting remains a future diagnostic for this choice.

## 11. Validation ranking and condition ordering

Let \(a_j\) and \(b_j\) be the average ranks of prediction \(\widehat y_j\) and target \(y_j\), including average ranks for ties. These rank symbols are scalars, separate from the bank reference \(b_c\). Define their means \(\bar a=N^{-1}\sum_j a_j\) and \(\bar b=N^{-1}\sum_j b_j\). Spearman correlation is

\[
\rho=
\frac{\sum_{j=1}^{N}(a_j-\bar a)(b_j-\bar b)}
{\sqrt{\sum_j(a_j-\bar a)^2}\sqrt{\sum_j(b_j-\bar b)^2}}.
\]

Constant predictions or targets make the denominator zero and require an explicitly undefined correlation result.

For condition ordering, let \(\mathcal Q\) contain unordered pairs of comparison indices \((j,l)\) with the same passage-pair identity, different condition strings, and different targets. Define

\[
d_{jl}=\widehat y_j-\widehat y_l,
\qquad
t_{jl}=y_j-y_l,
\qquad
K=|\mathcal Q|.
\]

With tie tolerance \(\varepsilon_o=10^{-7}\), the ordering score is

\[
A_{\mathrm{cond}}=\frac1K
\sum_{(j,l)\in\mathcal Q}
\left(
\mathbf1[d_{jl}t_{jl}>0\ \land\ |d_{jl}|\ge\varepsilon_o]
+\frac12\mathbf1[|d_{jl}|<\varepsilon_o]
\right).
\]

The symbol \(\land\) means both propositions hold. This metric is undefined when \(K=0\). Comparisons share source passages, so their uncertainty analysis uses source groups.

## 12. Inclusive recall cutoffs and confusion counts

Define validation positives \(\mathcal P=\{j:R_j\ge4\}\), negatives \(\mathcal N=\{j:R_j\le2\}\), and desired recall \(q=0.9\). Let \(n_+=|\mathcal P|\), and sort positive predictions in descending order as \(u_{(1)}\ge\cdots\ge u_{(n_+)}\). The largest observed threshold meeting the recall requirement is

\[
\tau=u_{(\lceil qn_+\rceil)}.
\]

The ceiling \(\lceil v\rceil\) is the smallest integer greater than or equal to scalar \(v\). Predict positive when \(\widehat y_j\ge\tau\), including ties. Define

\[
\begin{aligned}
\mathrm{TP}&=\sum_{j\in\mathcal P}\mathbf1[\widehat y_j\ge\tau],&
\mathrm{FN}&=\sum_{j\in\mathcal P}\mathbf1[\widehat y_j<\tau],\\
\mathrm{FP}&=\sum_{j\in\mathcal N}\mathbf1[\widehat y_j\ge\tau],&
\mathrm{TN}&=\sum_{j\in\mathcal N}\mathbf1[\widehat y_j<\tau].
\end{aligned}
\]

These symbols mean true positives, false negatives, false positives, and true negatives. The rates are

\[
\operatorname{recall}=\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}},
\qquad
\operatorname{FPR}=\frac{\mathrm{FP}}{\mathrm{FP}+\mathrm{TN}},
\qquad
\operatorname{FNR}=\frac{\mathrm{FN}}{\mathrm{TP}+\mathrm{FN}}.
\]

Each selected arm has its own validation threshold. Carry it into the existing test partition unchanged and report realized test recall. Rating-3 rows remain in regression and ranking metrics. Any zero rate denominator is explicitly undefined.

## 13. Paired source-group uncertainty

Let \(G\) be the number of connected source groups in a scored cohort and \(\mathcal I_g\) the comparison indices belonging to group \(g\in\{1,\ldots,G\}\). Bootstrap draw \(b\in\{1,\ldots,B_{\mathrm{boot}}\}\) samples \(G\) group indices independently with replacement, then concatenates all rows from the sampled groups. Here \(B_{\mathrm{boot}}=2000\), using the fixed bootstrap seed in the plan.

The implemented bootstrap metrics are Spearman, MSE, false-positive rate, and recall. For one of these metrics \(T\) and candidate arm \(a\), compute

\[
\Delta_b^{(a)}=T_b^{(a)}-T_b^{(N)}.
\]

The superscript \(N\) denotes the sole existing native comparator, using its sealed predictions. Every system uses identical sampled groups within a draw, and classification thresholds remain fixed at their validation values. The 2.5th and 97.5th percentiles of valid \(\Delta_b^{(a)}\) values form the paired percentile interval. Record invalid draws and require at least 95% valid draws for each metric. These intervals describe cohort-sampling uncertainty for the fitted checkpoints and existing comparator.

Conditional ordering is a point estimate and a point-difference selection guard in this implementation. Its bootstrap interval remains a future extension.

For validation selection, let \(\rho_a,A_a,F_a\) be candidate \(a\)'s Spearman correlation, conditional-ordering accuracy, and false-positive rate at its validation recall cutoff. Let \(\rho_N,A_N,F_N\) be the corresponding quantities for the existing native predictions. Eligibility requires all three inequalities:

\[
\rho_a-\rho_N\ge0.005,
\qquad A_a-A_N\ge-0.01,
\qquad F_a-F_N\le0.01.
\]

Select the eligible candidate with greatest validation Spearman, using the plan's fixed tie order. Existing-test transfer applies these guards and also requires candidate recall to decline by at most 0.01 relative to native recall, using the frozen validation thresholds. The rate and accuracy tolerances are absolute fractions; 0.01 is one percentage point.

## 14. Geometry formulas for future diagnostics

The following identities supply mathematical context. Explicit mean-vector, covariance-spectrum, and participation-rank reporting remains future diagnostic work in this implementation.

For \(n\) unique unit output vectors \(z_t\in\mathbb R^k\), where \(t\in\{1,\ldots,n\}\), define the mean \(\mu=n^{-1}\sum_tz_t\) and population covariance \(C=n^{-1}\sum_t(z_t-\mu)(z_t-\mu)^\top\). Then

\[
\operatorname{tr}(C)=1-\lVert\mu\rVert_2^2,
\qquad
\frac{\sum_{t\ne u}z_t^\top z_u}{n(n-1)}
=\frac{n\lVert\mu\rVert_2^2-1}{n-1}.
\]

Here \(u\) is a second vector index, distinct from \(t\), and \(\operatorname{tr}\) sums diagonal matrix entries. If \(\lambda_1\ge\cdots\ge\lambda_k\ge0\) are covariance eigenvalues, define leading variance share \(\lambda_1/\sum_t\lambda_t\) and participation rank

\[
R_{\mathrm{part}}=
\frac{(\sum_t\lambda_t)^2}{\sum_t\lambda_t^2}.
\]

In the eigenvalue sums, the index runs over \(1,\ldots,k\). The nonzero covariance rank is at most \(\min(k,n-1)\). Zero total covariance makes these ratios undefined. These measurements describe spread; task ranking and classification determine predictive utility.

## 15. Future encoder-training gradients

This section describes a later LoRA comparison. The frozen-feature stage implemented for this tranche has zero encoder updates.

Let \(\theta\in\mathbb R^p\) denote current adapter parameters, where \(p\) is their total count. For any vector-valued readout \(f_\theta\in\mathbb R^d\), let \(J_{f,\theta}=\partial f_\theta/\partial\theta\in\mathbb R^{d\times p}\). Bank references would become current-weight functions

\[
b_\theta(c)=\frac1M\sum_{m=1}^{M}
\left[h_\theta(x_m,c)-h_\theta(x_m,c_0)\right],
\qquad
J_{b,\theta}=\frac1M\sum_m
\left[J_{h(x_m,c),\theta}-J_{h(x_m,c_0),\theta}\right].
\]

For one pair, the same-passage, translation, and CASE-style encoder gradients are

\[
\begin{aligned}
\nabla_\theta L_M
&=\sum_{i=1}^{2}
\left(J_{h_i,\theta}^{\top}g_i
-\alpha J_{n_i,\theta}^{\top}g_i\right),\\
\nabla_\theta L_B
&=\sum_{i=1}^{2}J_{h_i,\theta}^{\top}g_i
-\alpha J_{b,\theta}^{\top}(g_1+g_2),\\
\nabla_\theta L_C
&=\sum_{i=1}^{2}J_{e_i,\theta}^{\top}g_i
-J_{a_c,\theta}^{\top}(g_1+g_2).
\end{aligned}
\]

For the projection arm, abbreviate \(b=b_\theta(c)\), \(a=b^\top b>0\), and \(t_i=b^\top h_i/a\). Holding \(h_i\) fixed, the Jacobian of \(q_i=t_ib\) with respect to \(b\) is

\[
J_{q_i,b}
=t_iI_d+\frac{bh_i^\top}{a}
-\frac{2t_i bb^\top}{a}.
\]

Holding \(b\) fixed gives \(J_{q_i,h_i}=P_c\). Therefore

\[
\nabla_\theta L_P
=\sum_{i=1}^{2}
J_{h_i,\theta}^{\top}(I_d-\alpha P_c)g_i
-\alpha J_{b,\theta}^{\top}
\sum_{i=1}^{2}J_{q_i,b}^{\top}g_i.
\]

The reference-side vector-Jacobian product can be evaluated without constructing its dense Jacobian:

\[
J_{q_i,b}^{\top}g_i
=t_i g_i
+\frac{h_i(b^\top g_i)}a
-\frac{2t_i b(b^\top g_i)}a.
\]

Both the numerator and denominator of the projection depend on current bank states. Detaching those states changes this derivative. Within-microbatch reference deduplication must preserve the sum of every use's gradient. A later training design must budget current-reference recomputation and explicitly specify the reference dropout/autograd policy before launch.

## 16. LoRA matrix updates in that future stage

For one adapted linear map, let \(W_0\in\mathbb R^{d_{\mathrm{out}}\times d_{\mathrm{in}}}\) be the frozen base matrix, \(A\in\mathbb R^{r_L\times d_{\mathrm{in}}}\) and \(B\in\mathbb R^{d_{\mathrm{out}}\times r_L}\) the adapter matrices, \(r_L=32\) the rank, and \(\gamma_L=32\) the scaling numerator. Let \(x\in\mathbb R^{d_{\mathrm{in}}}\) be the layer input, \(\widetilde x\) its adapter-dropout version, \(y_{\mathrm{lin}}\in\mathbb R^{d_{\mathrm{out}}}\) the layer output, and \(g_y=\nabla_{y_{\mathrm{lin}}}L\). The implemented map is

\[
y_{\mathrm{lin}}=W_0x+\frac{\gamma_L}{r_L}BA\widetilde x.
\]

Its adapter derivatives are

\[
\nabla_B L=\frac{\gamma_L}{r_L}g_y(A\widetilde x)^\top,
\qquad
\nabla_A L=\frac{\gamma_L}{r_L}B^\top g_y\widetilde x^\top.
\]

Every passage and reference use contributes through its own encoder path. The shared adapter gradients add before an optimizer update. For Qwen's q/o projections, \(d_{\mathrm{in}}=d_{\mathrm{out}}=4096\); for k/v projections, \(d_{\mathrm{in}}=4096\) and \(d_{\mathrm{out}}=1024\). The experiment's frozen-feature implementation updates only its head and fitted coefficient.

## 17. Verification targets

Numerical checks should cover head and coefficient gradients for each residual; the sigmoid chain; paired-bank construction; projection scale invariance and its perpendicular/parallel decomposition; full reference-side projection derivatives; shared-reference gradient accumulation; inclusive recall cutoffs and ties; shared-group bootstrap indices and frozen thresholds; complete cohort coverage; and equivalence of effective-batch loss under microbatch partitioning with controlled dropout masks.

Use double-precision finite differences away from LeakyReLU kinks, zero vectors, and threshold ties for smooth-gradient checks. The standalone [algebra check](../scripts/check_tranche5_math.py) evaluates these mathematical expressions independently of the production implementation. Its [math receipt](csts-tranche-5-math-verification.json) records executed checks and source hashes. Production tests separately check discrete cutoff, tie, bank-exclusion, cache-binding, and checkpoint-selection behavior; their outcome belongs in the implementation validation receipt.
