# Tranche 4: mathematical derivations and implementation map

This companion derives the representations, subtraction orders, losses, gradients, geometry diagnostics, operating points, and uncertainty calculations in the [proposal](csts-tranche-4-condition-component.md). Algebraic examples are illustrative. Reported benchmark values come from the existing selected checkpoint.

## 1. Objects, dimensions, and conventions

All vectors are columns. A transpose changes a column into a row. The Euclidean inner product is \(v^\top w\); its associated length is \(\|v\|_2=\sqrt{v^\top v}\). The indicator \(\mathbf 1[P]\) equals 1 when proposition \(P\) holds and 0 otherwise. A gradient lists coordinatewise partial derivatives of a scalar. A Jacobian contains the output-coordinate derivatives with respect to input coordinates. The notation \(\mathrm d\) denotes a differential change, and \(\operatorname{tr}\) denotes the sum of a square matrix's diagonal entries.

| Symbol | Meaning |
|---|---|
| \(j\in\{1,\ldots,N\}\) | Comparison index in the partition being evaluated; \(N\) is its row count. |
| \(i\in\{1,2\}\) | Passage side within a comparison. |
| \(x_{ji}\) | Passage text on side \(i\) of comparison \(j\). |
| \(c_j\) | The condition text shared by that comparison's two passages. |
| \(r_j\in[1,5]\) | Reference rating. |
| \(y_j=(r_j-1)/4\in[0,1]\) | Rescaled reference target used by our MSE. |
| \(d=4096\) | Qwen passage-vector width. |
| \(\theta\in\mathbb R^p\) | All trainable adapter parameters; \(p=30{,}670{,}848\) for this configuration. |
| \(\theta_\star\) | The selected, fixed adapter checkpoint used by the immediate diagnostic. |
| \(\varnothing\) | Empty text, represented by `""` in code. |
| \(h_\theta(x,c)\in\mathbb R^d\) | Final attended contextual state before external unit normalization. |
| \(b_\theta(c)=h_\theta(\varnothing,c)\) | Raw condition-containing reference. |
| \(b_{\theta,0}=h_\theta(\varnothing,\varnothing)\) | Raw generic-prompt reference. |
| \(z_\theta(x,c)\) | Unit-normalized passage vector. |
| \(u_\theta(c)\) and \(u_{\theta,0}\) | Unit-normalized condition and generic references. |

Define the normalization function on nonzero vectors:

\[
\operatorname{unit}(v)=\frac{v}{\|v\|_2},
\qquad
z_\theta(x,c)=\operatorname{unit}(h_\theta(x,c)),
\qquad
u_\theta(c)=\operatorname{unit}(b_\theta(c)).
\]

The generic unit reference is \(u_{\theta,0}=\operatorname{unit}(b_{\theta,0})\). Every vector being normalized must have finite coordinates and length greater than the proposed numerical guard \(10^{-8}\). Derivatives below apply in that smooth, nonzero region.

Additional symbols are defined where their operations first appear.

## 2. Input tokens and the native Qwen readout

The exact [prompt and tokenizer procedure](../csts_pilot/baseline_models.py#L18) concatenate the instruction, condition, and passage and append an attended EOD token. The two passages are independent batch elements sharing model weights.

Let \(V=151665\) be the vocabulary-table row count, \(E\in\mathbb R^{V\times d}\) the fixed token embedding table, and \(k_t\in\{0,\ldots,V-1\}\) the token ID at position \(t\). Let \(T\) be the padded token width and \(m_t^{\rm att}\in\{0,1\}\) indicate an attended position. Then:

\[
e_t=E[k_t,:]^\top\in\mathbb R^d,
\qquad
X^{(0)}=
\begin{bmatrix}
e_1^\top\\
\vdots\\
e_T^\top
\end{bmatrix}
\in\mathbb R^{T\times d}.
\]

The fixed backbone with its adapters maps this input to the final token-state matrix:

\[
H_\theta=F_\theta(X^{(0)},m^{\rm att})\in\mathbb R^{T\times d}.
\]

Here \(F_\theta\) denotes the complete implemented transformer, including its internal normalization and positional operations; the base parameters inside it remain fixed during LoRA training. The [pinned configuration](https://huggingface.co/Qwen/Qwen3-Embedding-8B/blob/c90816d848505624c2434128dfc61132162a0ee9/config.json) specifies 36 blocks and width 4096.

The final attended index and raw readout are:

\[
\ell=\max\{t:m_t^{\rm att}=1\},
\qquad
h_\theta(x,c)=H_{\theta,\ell,:}^\top.
\]

The explicit EOD occupies this attended position. The [native pooling function](../csts_pilot/baseline_models.py#L279) selects it and applies external L2 normalization. Qwen's causal final-token embedding design is described in [the embedding paper, section 2](https://arxiv.org/html/2506.05176v1#S2).

At diagnosis time, evaluate \(F_{\theta_\star}\) with dropout disabled. At continuation time, passage branches use the training dropout policy specified in the proposal.

## 3. What baseline subtraction means in CASE

For this section, \(f_\psi\) is the authors' fixed encoder, with parameters \(\psi\) and output width \(d_C\). The instruction \(I(x_i)\) supplies sentence \(x_i\) as context for encoding condition \(c\). Their condition-containing representation and standalone reference are:

\[
e_{C,i}=f_\psi(c;I(x_i))\in\mathbb R^{d_C},
\qquad
b_C=f_\psi(c;I(\varnothing))\in\mathbb R^{d_C}.
\]

The semicolon denotes contextual instruction information. It is a notation for the input construction. Let \(g_\phi:\mathbb R^{d_C}\to\mathbb R^{k_C}\) be the learned projection, with parameters \(\phi\); the reported projection comparison uses \(k_C=512\). CASE forms:

\[
v_{C,i}=g_\phi(e_{C,i}-b_C),
\qquad
s_C=\frac{v_{C,1}^\top v_{C,2}}
{\|v_{C,1}\|_2\|v_{C,2}\|_2}.
\]

The authors' [generation code](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/generate_embeddings.py#L61) constructs the subtraction, their [wrapper](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/llm_encoders.py#L71) defines the text roles, and their [projection code](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/CASE_performance.py#L126) applies a bias-free linear layer, LeakyReLU, and training dropout.

For the authors' Qwen wrapper, the returned pooled states retain their lengths before subtraction. Their main projection script uses MSE on cosine with target `rating / 5`. Their separate [LoRA comparison script](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/lora_finetune.py#L161) uses one minus batch Pearson correlation.

Our proposed reference retains the condition in our instruction and leaves our passage query empty. The model receives the same template in both passage and reference calls. This defines a different representation family from the main CASE method's condition-given-sentence construction.

## 4. Exact six-arm scoring definitions

Suppress comparison index \(j\) for one pair and write \(h_i=h_\theta(x_i,c)\), \(z_i=\operatorname{unit}(h_i)\), \(b=b_\theta(c)\), and \(u=\operatorname{unit}(b)\). Write \(b_0=b_{\theta,0}\) and \(u_0=\operatorname{unit}(b_0)\) for the generic reference.

For each arm \(a\), define its pre-normalization vector \(d_i^{(a)}\in\mathbb R^d\):

\[
\begin{aligned}
d_i^{(A)}&=h_i,\\
d_i^{(B_u)}&=z_i-u,\\
d_i^{(B_r)}&=h_i-b,\\
d_i^{(C_u)}&=z_i-u_0,\\
d_i^{(C_r)}&=h_i-b_0,\\
d_i^{(D)}&=\bar h_i^{\rm pass}.
\end{aligned}
\]

The passage mean \(\bar h_i^{\rm pass}\) is defined in section 6. All arms use:

\[
\widetilde z_i^{(a)}=\operatorname{unit}(d_i^{(a)}),
\qquad
s^{(a)}=(\widetilde z_1^{(a)})^\top\widetilde z_2^{(a)}.
\]

The arm set is \(\{A,B_u,B_r,C_u,C_r,D\}\). The subtraction coefficient is 1. The immediate diagnostic substitutes \(\theta=\theta_\star\) throughout these equations.

## 5. Why normalization order changes the correction

Let \(a_i=\|h_i\|_2>0\) and \(b_{\rm len}=\|b\|_2>0\). These are scalar lengths, so \(h_i=a_i z_i\) and \(b=b_{\rm len}u\). Raw subtraction gives:

\[
\begin{aligned}
h_i-b
&=a_i z_i-b_{\rm len}u\\
&=a_i\left(z_i-\frac{b_{\rm len}}{a_i}u\right).
\end{aligned}
\]

Normalization cancels the positive factor \(a_i\):

\[
\operatorname{unit}(h_i-b)
=\operatorname{unit}(z_i-\lambda_i u),
\qquad
\lambda_i=\frac{\|b\|_2}{\|h_i\|_2}.
\]

Raw-first subtraction therefore retains an input-specific reference weight \(\lambda_i\). Unit-first subtraction fixes that reference weight at 1:

\[
\operatorname{unit}(z_i-u)
=\operatorname{unit}\left(h_i-\frac{a_i}{b_{\rm len}}b\right).
\]

Equal passage/reference lengths give the same corrected direction, provided the residual is nonzero. Record the empirical norm-ratio distribution to measure how strongly the two proposed arms differ.

An illustrative two-dimensional calculation makes the difference visible:

\[
h=\begin{bmatrix}3\\0\end{bmatrix},
\quad
b=\begin{bmatrix}0\\1\end{bmatrix},
\quad
h-b=\begin{bmatrix}3\\-1\end{bmatrix},
\quad
\operatorname{unit}(h)-\operatorname{unit}(b)
=\begin{bmatrix}1\\-1\end{bmatrix}.
\]

The residual directions differ before their final normalization.

## 6. Sentence-only pooling and its derivative

Let \([a_x,b_x)\) be the passage's character interval in the formatted input. For token position \(t\), let \(\mathrm{start}_t,\mathrm{end}_t\) be its offset endpoints and \(\mathcal S\) the special-token ID set. The proposed mask is:

\[
m_t^{\rm pass}
=m_t^{\rm att}
\mathbf1[\mathrm{end}_t>a_x]
\mathbf1[\mathrm{start}_t<b_x]
\mathbf1[\mathrm{end}_t>\mathrm{start}_t]
\mathbf1[k_t\notin\mathcal S].
\]

This is positive span overlap with padding/special-token exclusions. Appended EOD is assigned an excluded special position. Let \(M_P=\sum_t m_t^{\rm pass}>0\) be the selected token count. Then:

\[
\bar h^{\rm pass}
=\frac1{M_P}\sum_{t=1}^T m_t^{\rm pass}H_{\theta,t,:}^\top
\in\mathbb R^d.
\]

If \(g_{\rm pool}=\nabla_{\bar h^{\rm pass}}L\in\mathbb R^d\), differentiation gives:

\[
\nabla_{H_{\theta,t,:}^\top}L
=\frac{m_t^{\rm pass}}{M_P}g_{\rm pool}.
\]

Selected passage states receive the direct pooling gradient. Their dependency on earlier condition states remains inside \(F_\theta\).

For any positive scalar \(a\), \(\operatorname{unit}(av)=\operatorname{unit}(v)\). Hence unit-normalized mean and sum pooling coincide. With a bias-free matrix \(W\) the same cancellation holds:

\[
\operatorname{unit}\left(W\frac{\sum_t m_t^{\rm pass}H_{\theta,t,:}^\top}{M_P}\right)
=
\operatorname{unit}\left(W\sum_t m_t^{\rm pass}H_{\theta,t,:}^\top\right).
\]

The result assumes a nonzero projected sum. A changed token mask or learned weighted aggregation can change direction.

## 7. Shared-component geometry and a falsifiable example

This section introduces an illustrative additive model. Let \(w_c\in\mathbb R^d\) be a hypothesized shared condition component and \(a_1,a_2\in\mathbb R^d\) the passage-dependent components:

\[
h_1=a_1+w_c,\qquad h_2=a_2+w_c.
\]

Expanding the dot product gives:

\[
h_1^\top h_2
=a_1^\top a_2+a_1^\top w_c+a_2^\top w_c+\|w_c\|_2^2.
\]

Assume \(\|a_1\|_2=\|a_2\|_2=1\), \(a_1^\top a_2=0\), and \(a_i^\top w_c=0\). Define \(\beta=\|w_c\|_2>0\). The original cosine is:

\[
s_A=\frac{\beta^2}{1+\beta^2}.
\]

If the actual reference equals \(w_c\), raw subtraction leaves \(a_1,a_2\) and gives cosine 0. If reference error is \(\delta_c=b_\theta(c)-w_c\), raw subtraction gives \(a_i-\delta_c\). The correction depends on how accurately the reference estimates the shared component.

For unit-first subtraction define \(\gamma=z_1^\top z_2\) and \(\eta_i=z_i^\top u\). Expanding its numerator and lengths gives:

\[
s_{B_u}
=
\frac{\gamma-\eta_1-\eta_2+1}
{\sqrt{(2-2\eta_1)(2-2\eta_2)}}.
\]

Under the orthogonal example, set \(t=\beta/\sqrt{1+\beta^2}\). Then \(\gamma=t^2\) and \(\eta_1=\eta_2=t\), so:

\[
s_{B_u}
=\frac{t^2-2t+1}{2-2t}
=\frac{1-t}{2}.
\]

| Illustrative component length | Native cosine | Raw-first cosine with exact reference | Unit-first cosine |
|---|---:|---:|---:|
| \(\beta=2\) | 0.800000 | 0 | 0.052786 |
| \(\beta=0.1\) | 0.009901 | 0 | 0.450248 |

Unit-first subtraction can reduce or increase a pair's similarity. Both orders therefore belong in the diagnostic.

There is another exact constraint. For any unit \(z,u\) with \(z\ne u\):

\[
u^\top\operatorname{unit}(z-u)
=\frac{z^\top u-1}{\sqrt{2-2z^\top u}}
=-\sqrt{\frac{1-z^\top u}{2}}.
\]

The corrected vectors occupy the opposite closed hemisphere from the reference. This geometric property establishes a transformed representation; predictive evaluation determines its usefulness.

## 8. Derivative of unit normalization

Take a nonzero \(v\in\mathbb R^d\) and define \(r_v=\sqrt{v^\top v}\) and \(z=v/r_v\). The scalar differential is:

\[
\mathrm d r_v=\frac{v^\top\mathrm d v}{r_v}.
\]

Apply the product/quotient rule:

\[
\begin{aligned}
\mathrm d z
&=\frac{\mathrm d v}{r_v}
-\frac{v}{r_v^2}\mathrm d r_v\\
&=\left(\frac{I_d}{r_v}-\frac{vv^\top}{r_v^3}\right)\mathrm d v\\
&=\frac1{\|v\|_2}(I_d-zz^\top)\mathrm d v.
\end{aligned}
\]

Here \(I_d\) is the \(d\)-dimensional identity matrix. The normalization Jacobian is the symmetric matrix:

\[
J_{\rm unit}(v)
=\frac1{\|v\|_2}(I_d-zz^\top)\in\mathbb R^{d\times d}.
\]

It removes the radial component of an incoming vector and rescales its tangential component. A change proportional to \(v\) leaves the normalized direction unchanged.

## 9. Cosine-MSE and its gradients

For one arm and one comparison, write \(d_1,d_2\) for its residual/readout vectors and \(\widetilde z_i=\operatorname{unit}(d_i)\). Set:

\[
s=\widetilde z_1^\top\widetilde z_2,
\qquad
L=(s-y)^2.
\]

Here \(y\) is the rescaled target for this comparison. The derivatives at the score and unit-vector stages are:

\[
\frac{\partial L}{\partial s}=2(s-y),
\qquad
\nabla_{\widetilde z_1}L=2(s-y)\widetilde z_2,
\qquad
\nabla_{\widetilde z_2}L=2(s-y)\widetilde z_1.
\]

Apply section 8:

\[
g_i:=\nabla_{d_i}L
=
\frac{2(s-y)}{\|d_i\|_2}
\left(\widetilde z_{3-i}-s\widetilde z_i\right),
\qquad i\in\{1,2\}.
\]

The subscript \(3-i\) selects the other passage. Since both unit vectors have length 1:

\[
\left\|\widetilde z_{3-i}-s\widetilde z_i\right\|_2^2
=1-s^2.
\]

The angular gradient vanishes at exact alignment or anti-alignment. In particular, identical directions give score 1 and zero vector gradients even for target 0.

This establishes stationarity. For a single pair with \(y<1\), rotate one unit vector by a small angle \(\epsilon\) from an aligned state. Then:

\[
s(\epsilon)=\cos\epsilon
=1-\frac{\epsilon^2}{2}+O(\epsilon^4),
\qquad
L(\epsilon)=(1-y)^2-(1-y)\epsilon^2+O(\epsilon^4).
\]

The embedding-space loss has a second-order descent direction at that aligned state. Accessible parameter perturbations depend on the shared encoder.

The implemented [MSE training loop](../csts_pilot/baseline_stages.py#L316) uses this pairwise loss with batch averaging.

## 10. Full gradients through the reference branch

For raw-first subtraction, \(d_i=h_i-b\) and section 9 supplies \(g_i\). The reference is shared by the two passage sides:

\[
\nabla_{h_i}L=g_i,
\qquad
\nabla_bL=-(g_1+g_2).
\]

Let \(J_{h_i}\in\mathbb R^{d\times p}\) and \(J_b\in\mathbb R^{d\times p}\) be the Jacobians of the passage and reference states with respect to adapters \(\theta\). The full parameter gradient is:

\[
\nabla_\theta L
=\sum_{i=1}^2J_{h_i}^\top g_i
-J_b^\top(g_1+g_2).
\]

For unit-first subtraction, \(d_i=\operatorname{unit}(h_i)-\operatorname{unit}(b)\). Apply the additional normalization Jacobians:

\[
\nabla_\theta L
=
\sum_{i=1}^2J_{h_i}^\top J_{\rm unit}(h_i)g_i
-
J_b^\top J_{\rm unit}(b)(g_1+g_2).
\]

The Jacobians are symmetric, which explains their orientation in this expression.

A detached reference removes the second term and defines a different gradient rule. The proposed continuation uses the full derivatives above. The raw/unit prompt-reference arms have identical expressions with \(b_{\theta,0}\) in place of \(b_\theta(c)\).

For a batch of \(M\) comparisons, use per-comparison gradients \(g_{ji}\) from section 9. The gradient into a raw reference shared by condition \(c\) is:

\[
\nabla_{b_\theta(c)}L_{\rm batch}
=-\frac1M\sum_{j:c_j=c}\sum_{i=1}^2g_{ji}.
\]

Unit-first subtraction adds \(J_{\rm unit}(b_\theta(c))\) to this expression. Correct deduplication preserves the sum over every consumer.

During continuation, the reference uses current adapters. Its proposed dropout is disabled with autograd enabled; passage branches retain training dropout. Recompute references per microbatch to avoid retaining a reference graph across backward calls. At frozen inference, references can be cached by exact checkpoint and input identity.

## 11. LoRA weight gradients and parameter counts

For one adapted attention projection, let \(a\in\mathbb R^{d_{\rm in}}\) be its incoming activation, \(v\in\mathbb R^{d_{\rm out}}\) its output, and \(W_0\in\mathbb R^{d_{\rm out}\times d_{\rm in}}\) its fixed matrix. The LoRA rank is \(r_L=32\), scale numerator \(\alpha_L=32\), and scale factor \(\lambda_L=\alpha_L/r_L=1\).

The trainable matrices have shapes \(A_L\in\mathbb R^{r_L\times d_{\rm in}}\) and \(B_L\in\mathbb R^{d_{\rm out}\times r_L}\). Let \(D(a)\) apply the branch's dropout mask, treated as fixed during the derivative:

\[
v=W_0a+\lambda_L B_LA_LD(a).
\]

This parameterization follows [LoRA, section 4.1](https://arxiv.org/html/2106.09685v2#S4.SS1) and our [adapter attachment](../csts_pilot/baseline_models.py#L299).

Set \(a_D=D(a)\) and let \(g_v=\nabla_vL\in\mathbb R^{d_{\rm out}}\). Differentiating the scalar product \(g_v^\top v\) gives:

\[
\nabla_{B_L}L=\lambda_Lg_v(A_La_D)^\top,
\qquad
\nabla_{A_L}L=\lambda_LB_L^\top g_v a_D^\top.
\]

If \(J_D\) is the dropout-mask Jacobian, the activation gradient is:

\[
\nabla_aL=W_0^\top g_v+
\lambda_LJ_D^\top A_L^\top B_L^\top g_v.
\]

Gradients pass through the fixed base transformation into earlier operations. Optimizer updates apply to adapter parameters.

At the zero-correction initialization \(B_L=0\), the update is zero and \(\nabla_{A_L}L=0\) on the first backward pass; \(\nabla_{B_L}L\) can be nonzero when \(A_L\) is initialized randomly. Subsequent updates allow both matrices to learn.

Each adapter contributes \(r_L(d_{\rm in}+d_{\rm out})\) parameters. The pinned Qwen configuration has 32 query heads, eight key/value heads, and head width 128. Thus query/output widths are 4096 and key/value widths are 1024:

\[
\begin{aligned}
p_{\rm layer}
&=32[(4096+4096)+(4096+1024)\\
&\qquad +(4096+1024)+(4096+4096)]\\
&=851968,\\
p&=36p_{\rm layer}=30670848.
\end{aligned}
\]

The four terms correspond to query, key, value, and output adapters.

## 12. Exact microbatch averaging

Let an effective update contain \(M\) comparisons, partitioned into disjoint microbatches \(\mathcal B_1,\ldots,\mathcal B_K\). Here \(K\) is the number of microbatches. Let \(\ell_j=(s_j-y_j)^2\).

\[
L_{\rm batch}
=\frac1M\sum_{j=1}^M\ell_j
=\sum_{k=1}^K\frac1M\sum_{j\in\mathcal B_k}\ell_j.
\]

Linearity of differentiation gives:

\[
\nabla_\theta L_{\rm batch}
=\sum_{k=1}^K\nabla_\theta
\left(\frac1M\sum_{j\in\mathcal B_k}\ell_j\right).
\]

This justifies summing each microbatch's squared errors and dividing by the effective update's actual comparison count before backward. The last partial update uses its actual \(M\). Our existing loop follows this weighting.

For numerical equivalence checks, use identical forward values and disabled dropout. Stochastic equivalence requires matched dropout masks.

## 13. Pearson loss, its gradient, and the two-pair problem

For this section, \(s,y\in\mathbb R^M\) are the prediction and target score vectors of a batch. Let \(\mathbf1_M\) be the all-ones column vector and define:

\[
C_M=I_M-\frac1M\mathbf1_M\mathbf1_M^\top,
\qquad
s^\circ=C_Ms,
\qquad
y^\circ=C_My.
\]

\(C_M\) is the centering matrix; \(s^\circ,y^\circ\) are mean-centered score vectors. For nonzero centered lengths, Pearson correlation and the authors' LoRA loss are:

\[
R=\frac{(s^\circ)^\top y^\circ}
{\|s^\circ\|_2\|y^\circ\|_2},
\qquad
L_P=1-R.
\]

Using the normalization derivative from section 8:

\[
\nabla_sL_P
=C_M\left[
-\frac{y^\circ}{\|s^\circ\|_2\|y^\circ\|_2}
+\frac{R\,s^\circ}{\|s^\circ\|_2^2}
\right].
\]

Their [implementation](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/lora_finetune.py#L161) computes this as cosine between centered score vectors, with an epsilon guard.

For any positive scale \(\kappa\) and scalar offset \(\delta\):

\[
C_M(\kappa s+\delta\mathbf1_M)=\kappa s^\circ,
\qquad
R(\kappa s+\delta\mathbf1_M,y)=R(s,y).
\]

The loss preserves positive affine changes in score scale and offset. Our MSE gradient is \(2(s-y)/M\), so its numerical-score objective differs.

For \(M=2\), define \(\Delta s=s_1-s_2\) and \(\Delta y=y_1-y_2\). Centering gives:

\[
s^\circ=\frac{\Delta s}{2}\begin{bmatrix}1\\-1\end{bmatrix},
\qquad
y^\circ=\frac{\Delta y}{2}\begin{bmatrix}1\\-1\end{bmatrix},
\qquad
R=\operatorname{sign}(\Delta s\,\Delta y).
\]

For nonzero differences, correlation is locally constant at +1 or -1. Equal targets have zero centered variance. Computing and accumulating these two-pair losses therefore gives a degenerate training objective. A meaningful Pearson comparison must compute the batch-level statistics and gradients over a larger effective batch. Ordinary accumulation of microbatch correlations changes that objective.

## 14. What score compression establishes

Let \(Y\) be a random target conditioned on input tuple \(\xi=(x_1,x_2,c)\), and define \(\mu(\xi)=\mathbb E[Y\mid\xi]\). For an unconstrained scalar prediction \(s\):

\[
\begin{aligned}
\mathbb E[(s-Y)^2\mid\xi]
&=\mathbb E[(s-\mu+\mu-Y)^2\mid\xi]\\
&=(s-\mu)^2+\mathbb E[(Y-\mu)^2\mid\xi].
\end{aligned}
\]

The cross term vanishes because \(\mathbb E[\mu-Y\mid\xi]=0\). The squared-error optimum is \(s=\mu(\xi)\). Intermediate conditional averages can be appropriate under ambiguity or label variation. A shared embedding parameterization couples the achievable scalar predictions.

For empirical score vectors, let \(\bar s,\bar y\) be means, \(\sigma_s,\sigma_y\) their population standard deviations, and \(R\) their Pearson correlation. Expanding centered errors gives:

\[
\operatorname{MSE}
=(\bar s-\bar y)^2+\sigma_s^2+\sigma_y^2
-2R\sigma_s\sigma_y.
\]

The mean prediction at a reference rating measures score behavior in that label stratum. Causal interpretation requires the proposed intervention comparisons.

The fixed checkpoint's test score standard deviation is 0.24846, versus reference standard deviation 0.40851. Its score range and ranking show substantial variation. The next sections define direct concentration and discrimination measurements.

## 15. Mean direction, covariance, and participation rank

For this section, use \(n\) unique input embeddings \(z_1,\ldots,z_n\in\mathbb R^d\), each of unit length. These indices enumerate inputs, independently of comparison-side notation above. Define the empirical mean:

\[
\mu_z=\frac1n\sum_{k=1}^n z_k.
\]

Expand its squared length and use \(z_k^\top z_k=1\):

\[
n^2\|\mu_z\|_2^2
=n+\sum_{k\ne l}z_k^\top z_l.
\]

For \(n>1\), the mean cosine across distinct input pairs is therefore:

\[
\bar s_{\rm off}
=\frac1{n(n-1)}\sum_{k\ne l}z_k^\top z_l
=\frac{n\|\mu_z\|_2^2-1}{n-1}.
\]

The empirical covariance uses denominator \(n\):

\[
C_z=\frac1n\sum_{k=1}^n(z_k-\mu_z)(z_k-\mu_z)^\top,
\qquad
\operatorname{tr}(C_z)=1-\|\mu_z\|_2^2.
\]

Let \(\lambda_1\ge\cdots\ge\lambda_d\ge0\) be its eigenvalues. When their sum is positive, define leading-component variance share and variance participation rank:

\[
f_1=\frac{\lambda_1}{\sum_l\lambda_l},
\qquad
r_{\rm part}=\frac{(\sum_l\lambda_l)^2}{\sum_l\lambda_l^2}.
\]

If exactly \(k\) eigenvalues are positive, nonnegativity gives \((\sum_l\lambda_l)^2\ge\sum_l\lambda_l^2\) and Cauchy–Schwarz gives \((\sum_l\lambda_l)^2\le k\sum_l\lambda_l^2\). Hence:

\[
1\le r_{\rm part}\le k\le\min(d,n-1).
\]

For zero covariance, record zero total variance and define the diagnostic participation rank as 0; leading share is undefined. Report the sample ceiling and optionally \(r_{\rm part}/\min(d,n-1)\) for equal-size comparisons.

These summaries measure directional concentration and variance allocation. Their relationship to task errors is evaluated with the predictive metrics.

For complete directional collapse, every predicted pair cosine would be 1. With empirical target mean \(\bar y\) and population variance \(\sigma_y^2\):

\[
\operatorname{MSE}_{\rm all\,1}
=\frac1N\sum_j(1-y_j)^2
=\sigma_y^2+(1-\bar y)^2.
\]

The retained target statistics give 0.336093 for this configuration, compared with observed model MSE 0.070763. This calculation concerns complete directional collapse; covariance summaries examine partial concentration.

## 16. Confusion counts and the validation recall threshold

Let \(\mathcal P=\{j:r_j\ge4\}\) be the positive comparison indices and \(\mathcal N=\{j:r_j\le2\}\) the negatives. Let \(N_+=|\mathcal P|\) and \(N_-=|\mathcal N|\). These sets are for binary metrics. Ratings between these definitions retain their regression/ranking roles.

For an arm's score \(s_j\) and cutoff \(\tau\), define predicted-positive indicator \(\widehat a_j(\tau)=\mathbf1[s_j\ge\tau]\). Then:

\[
\begin{aligned}
TP(\tau)&=\sum_{j\in\mathcal P}\widehat a_j(\tau),
&FN(\tau)&=N_+-TP(\tau),\\
FP(\tau)&=\sum_{j\in\mathcal N}\widehat a_j(\tau),
&TN(\tau)&=N_--FP(\tau).
\end{aligned}
\]

For positive denominators:

\[
\operatorname{Recall}(\tau)=\frac{TP(\tau)}{N_+},
\qquad
\operatorname{FNR}(\tau)=1-\operatorname{Recall}(\tau),
\qquad
\operatorname{FPR}(\tau)=\frac{FP(\tau)}{N_-}.
\]

The observed test counts reproduce the previous diagnostic:

| Cutoff | TP | FN | FP | TN | Recall | FPR |
|---|---:|---:|---:|---:|---:|---:|
| 0.50 | 1213 | 149 | 128 | 738 | 0.890602 | 0.147806 |
| 0.75 | 793 | 569 | 15 | 851 | 0.582232 | 0.017321 |

For validation threshold selection, let \(K_+\) be the validation positive count and sort its positive scores ascending as \(p_{(1)}\le\cdots\le p_{(K_+)}\). Let \(k_{\rm req}=\lceil0.9K_+\rceil\) be the required recovered count. Choose:

\[
\tau_{90}=p_{(K_+-k_{\rm req}+1)}.
\]

At least \(k_{\rm req}\) positive examples meet this threshold. A larger threshold drops the positive example at the boundary and violates the required count. Including ties can make achieved recall exceed 90%.

Each arm freezes its own validation-derived cutoff. Applying it unchanged on test defines a deployable operating point; test recall is measured again.

## 17. Why monotone calibration leaves matched-recall discrimination unchanged

Let \(f\) be a strictly increasing score transformation. For every score and threshold:

\[
\mathbf1[f(s_j)\ge f(\tau)]
=\mathbf1[s_j\ge\tau].
\]

The two score systems can therefore realize identical confusion counts through corresponding thresholds. Their full recall/FPR operating curves coincide, including score ties.

A strictly increasing transform also preserves every score rank. Thus a numerical rescaling can improve MSE or alter errors at a fixed raw cutoff while preserving Spearman and attainable matched-recall discrimination. This is why the proposal reports both numerical-score metrics and validation-recall operating points.

## 18. Spearman and condition ordering

Let \(R_j(s)\) be the average ascending rank assigned to score \(s_j\), with tied scores sharing their mean occupied rank. Define \(R_j(y)\) similarly and let \(\bar R_s,\bar R_y\) be their means. Spearman is Pearson correlation of those rank vectors:

\[
\rho_S
=
\frac{\sum_j(R_j(s)-\bar R_s)(R_j(y)-\bar R_y)}
{\sqrt{\sum_j(R_j(s)-\bar R_s)^2}
 \sqrt{\sum_j(R_j(y)-\bar R_y)^2}}.
\]

Both rank variances must be positive. This definition handles the benchmark's repeated rating values. The implementation uses [SciPy's rank-order correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).

For condition ordering, enumerate \(K_{\rm ord}\) pairs of rows sharing the same passage-pair ID, with different conditions and different targets. For ordering comparison \(k\), define score difference \(\Delta s_k\) and target difference \(\Delta y_k\). With tie tolerance \(\epsilon_{\rm tie}=10^{-7}\):

\[
A_{\rm cond}
=\frac1{K_{\rm ord}}\sum_{k=1}^{K_{\rm ord}}
\left[
\mathbf1[|\Delta s_k|\ge\epsilon_{\rm tie},\ \Delta s_k\Delta y_k>0]
+\frac12\mathbf1[|\Delta s_k|<\epsilon_{\rm tie}]
\right].
\]

This matches the [existing diagnostic](../csts_pilot/diagnostics.py). Shared captions make these ordering comparisons dependent; source groups remain the resampling unit.

## 19. Paired source-group bootstrap

Let \(G\) be the number of connected source groups and \(\mathcal D_g\) the comparison rows in group \(g\). For bootstrap draw \(b\), independently sample \(G\) group indices with replacement and concatenate all their rows, repeating a group's rows for every repeated draw. Call that row multiset \(\mathcal D^{(b)}\).

For a metric functional \(T\), define:

\[
\Delta^{(b)}
=T(\text{candidate};\mathcal D^{(b)})
-T(\text{baseline};\mathcal D^{(b)}).
\]

Both methods use the same sampled row multiset. Recompute nonlinear metrics such as Spearman on the complete multiset. Use 2,000 draws, seed 61024, and the empirical 2.5th/97.5th percentiles of the differences as a paired percentile interval. Every test draw retains the thresholds selected on validation.

A draw with an undefined denominator/rank variance is recorded as undefined for that metric; the receipt reports its count and requires at least 95% valid draws for an interval. This is a proposed validity rule. Resampling estimates source-sample variation conditional on the fixed model and selected operating points.

## 20. Continuation comparisons and optimization

Let \(T\) be any reported metric. Denote the frozen native parent by \(A_0\), its selected frozen reference correction by \(R_0\), the native continuation by \(A_1\), and the reference-aware continuation by \(R_1\). Report:

\[
\begin{aligned}
\Delta_{\rm post}&=T(R_0)-T(A_0),\\
\Delta_{\rm native\,train}&=T(A_1)-T(A_0),\\
\Delta_{\rm corrected\,train}&=T(R_1)-T(R_0),\\
\Delta_{\rm training\,interaction}
&=[T(R_1)-T(R_0)]-[T(A_1)-T(A_0)].
\end{aligned}
\]

For error metrics, lower values are preferable; for correlation/recall, higher values are preferable. The frozen comparators reuse existing outputs. Only \(A_1,R_1\) require continuation training.

For completeness, let \(g_t^{\rm raw}\) be the adapter gradient at optimizer update \(t\). The ideal real-arithmetic clipping rule gives \(g_t=g_t^{\rm raw}/\max(1,\|g_t^{\rm raw}\|_2)\), with clipping implemented by the existing PyTorch function. Let the first/second moment vectors be \(m_t,v_t\), initialized with \(m_0=v_0=0\). Their decay constants are \(\beta_1=0.9,\beta_2=0.999\), learning rate is \(\eta\), weight decay is \(\lambda_{\rm wd}\), and denominator guard is \(\epsilon_{\rm opt}=10^{-8}\). Operations on moment coordinates are elementwise:

\[
\begin{aligned}
m_t&=\beta_1m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2v_{t-1}+(1-\beta_2)(g_t\odot g_t),\\
\widehat m_t&=\frac{m_t}{1-\beta_1^t},
\qquad
\widehat v_t=\frac{v_t}{1-\beta_2^t},\\
\theta_{t+1}
&=(1-\eta\lambda_{\rm wd})\theta_t
-\eta\frac{\widehat m_t}{\sqrt{\widehat v_t}+\epsilon_{\rm opt}}.
\end{aligned}
\]

\(\odot\) denotes coordinatewise multiplication. These moment vectors live in \(\mathbb R^p\) and remain distinct from the scalar attention masks and earlier example vectors. The current loop uses [PyTorch AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html). The proposal retains \(\eta=2\cdot10^{-5}\) and \(\lambda_{\rm wd}=0.01\) and binds the moment/epsilon constants above explicitly.

Tranche D uses fresh optimizer states in both arms, matched comparison order, epoch-zero candidates, and validation selection. The base model stays fixed and the adapter parameters receive these updates.

## 21. Validation and source map

Numerical verification covers the normalization Jacobian; both cosine-MSE vector gradients; shared-reference gradients for both subtraction orders; LoRA matrix gradients; Pearson gradients on a nondegenerate batch; two-pair degeneracy; microbatch weighting; norm-order identities; the shared-component examples; covariance identities/rank bounds; the recall order statistic; and monotone operating-point invariance.

The numerical checks use float64 central differences and deterministic illustrative inputs. Math payloads are checked with KaTeX and the documents are rendered for review. The companion verification receipt records actual checks and tolerances.

| Imported behavior | Defining source |
|---|---|
| Current prompt, EOD, pooling, adapters, and pair scores | [Qwen model code](../csts_pilot/baseline_models.py) |
| Current MSE, effective-batch weighting, optimizer and clipping | [Training loop](../csts_pilot/baseline_stages.py) |
| Current ordering diagnostic | [Diagnostics](../csts_pilot/diagnostics.py) |
| Model identity and widths | [Settings](../configs/csts-qwen-evidence.json) and [pinned model configuration](https://huggingface.co/Qwen/Qwen3-Embedding-8B/blob/c90816d848505624c2434128dfc61132162a0ee9/config.json) |
| Selected checkpoint and benchmark scores | [Retained results](../training_outputs/csts_qwen_evidence_results.json) |
| Main CASE construction | [Paper, section 3](https://arxiv.org/html/2503.17279v5#S3), [wrapper](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/llm_encoders.py), [subtraction](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/generate_embeddings.py), and [projection](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/CASE_performance.py) |
| Authors' separate LoRA correlation loss | [Pinned LoRA baseline](https://github.com/LivNLP/CASE/blob/8eabf90bd286f46334799bed59575b8e9842b95e/lora_finetune.py) |
| Low-rank update construction | [Hu et al., LoRA, section 4.1](https://arxiv.org/html/2106.09685v2#S4.SS1) |
| Spearman's definition | [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) |
| AdamW update convention | [PyTorch documentation](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html) |

The six-arm construction, numerical guards, adoption tolerances, dropout policy for a reference-aware continuation, and reporting decisions are proposed project choices. The displayed algebra derives their consequences.
