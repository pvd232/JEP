# Learning semantic similarity: geometry, supervision and clusters

When two objects are compared, which similarities should count? A red bicycle resembles a red car in color and a blue bicycle in vehicle type. Changing the comparison criterion changes which relationship the representation should preserve.

This primer develops the mathematical tools behind that choice. Its derivations establish properties of specified functions and graphs. Whether those functions capture the intended meaning is an empirical question, answered with independently judged text. Read this before [conditional encoders](02-conditional-encoders-and-discovery.md).

## 1. An embedding makes comparison computable

Let $x$ denote a passage and $c$ a question. A conditional encoder $f_\theta$ maps them to a vector in $\mathbb{R}^d$, where $d$ is the number of coordinates and $\theta$ contains the learned parameters:

$$ z=f_\theta(x,c). $$

For nonzero vectors $u$ and $v$, cosine similarity is:

$$ s(u,v)=\frac{u^\top v}{\|u\|_2\|v\|_2}. $$

The dot product adds coordinate-wise products. The denominator removes vector length, leaving a comparison of direction. Coordinate values acquire meaning through training and the comparisons they support; individual coordinates can mix many linguistic properties.

**Derivation: cosine and Euclidean neighbors.** Assume $\|u\|_2=\|v\|_2=1$. Expanding the square gives:

$$ \|u-v\|_2^2=u^\top u+v^\top v-2u^\top v=2-2s(u,v). $$

Thus ranking unit vectors by decreasing cosine gives the same ordering as increasing Euclidean distance. This licenses a change of computational representation for nearest-neighbor search. A clustering procedure can still respond differently to its objective, graph construction and resolution settings.

**Reading bridge.** Sentence-BERT makes independently encoded sentence vectors useful for similarity search. Its architecture shares encoder weights across sentence inputs and trains using sentence-pair objectives. Read §3 for pooling and the classification, regression and triplet objectives. Notice that the label and objective together determine which comparisons training rewards. [Reimers and Gurevych, 2019](literature/sentence-bert-2019.pdf).

Independently encoding each passage under a fixed question permits reuse of its vector across many comparisons and downstream analyses.

## 2. A learned distance changes which differences matter

Suppose a frozen encoder produces features $h(x)\in\mathbb{R}^d$. A learned matrix can stretch, rotate or compress their geometry. The classical form is a Mahalanobis distance:

$$ d_A(u,v)=\sqrt{(u-v)^\top A(u-v)},\qquad A\succeq0. $$

Here $A$ is a symmetric $d\times d$ positive-semidefinite matrix. The condition $A\succeq0$ means $w^\top Aw\geq0$ for every vector $w$.

Xing and colleagues learn such a matrix from pairs judged similar and dissimilar, then use the distance for clustering. Read §2 closely: the optimization keeps similar pairs close while imposing separation on dissimilar pairs. This supplies the historical foundation for learning a geometry from human judgments. [Xing et al., 2002](literature/xing-2002.pdf).

**Proof: a positive-semidefinite matrix defines a Euclidean distance after transformation.** The spectral theorem gives $A=Q\Lambda Q^\top$, with orthogonal $Q$ and nonnegative diagonal entries in $\Lambda$. Set $L=\Lambda^{1/2}Q^\top$. Then $A=L^\top L$, so:

$$ d_A(u,v)=\sqrt{(u-v)^\top L^\top L(u-v)}=\|Lu-Lv\|_2. $$

Nonnegativity and symmetry follow from the norm. Its triangle inequality follows from:

$$ \|Lu-Lw\|_2\leq\|Lu-Lv\|_2+\|Lv-Lw\|_2. $$

If $A$ is positive definite, zero distance implies $u=v$, giving a metric. If $A$ has a nontrivial nullspace, distinct vectors can map to the same point, giving a pseudometric. A low-dimensional projection deliberately permits this collapse.

**Consequence.** A learned projection can suppress variation that contributes little to the question and emphasize features predictive of judged similarity. A frozen representation’s information content limits projection learning: whenever $h(x_1,c)=h(x_2,c)$, every deterministic projection $g$ satisfies $g(h(x_1,c))=g(h(x_2,c))$. That statement follows by substitution. Recovering a distinction lost at this boundary requires additional input or an upstream representation change.

CASE uses a nonlinear projection and cosine scoring, so its exact model differs from this classical quadratic distance. The proof supplies the geometric intuition and the information boundary.

## 3. Labels become forces through a loss function

A triplet contains an anchor $a$, a preferred comparison $p$, and another comparison $n$, all evaluated under condition $c$. Preference means that the annotation protocol judges $p$ more similar to $a$ than $n$ is. It can be encoded using a margin loss:

$$ \ell=\max\{0,m-s(f_\theta(a,c),f_\theta(p,c))+s(f_\theta(a,c),f_\theta(n,c))\},\qquad m>0. $$

This is a teaching example of a standard ranking objective. While the expression inside the maximum is positive, reducing the loss rewards a larger preferred similarity and a smaller alternative similarity. Once the margin is met, that example contributes zero gradient through the hinge’s active expression. Choosing the margin and handling ties are modeling decisions.

A softmax contrastive objective instead chooses one preferred candidate from a set. Let $s_j$ be the anchor’s similarity to candidate $j$, let $p$ index the preferred candidate, and let temperature $\tau>0$ control the score scale:

$$ \ell=-\log\frac{\exp(s_p/\tau)}{\sum_j\exp(s_j/\tau)}. $$

**Derivation: which way training pushes.** Define $q_j=\exp(s_j/\tau)/\sum_k\exp(s_k/\tau)$. Differentiating the log-sum-exp gives:

$$ \frac{\partial\ell}{\partial s_j}=\frac{q_j-\mathbf{1}[j=p]}{\tau}. $$

Gradient descent therefore increases the preferred score and decreases alternative scores, subject to their shared dependence on model parameters. If an alternative is also genuinely similar under the question, this training signal penalizes a valid relationship. The annotation and candidate-selection protocol controls that risk.

SimCSE trains sentence embeddings with contrastive learning: dropout supplies paired views in its unsupervised setting, and natural-language-inference labels supply supervised positives and hard negatives. Read §§2–4 for the objective and construction of those training pairs. [Gao, Yao and Chen, 2021](literature/simcse-2021.pdf).

For object descriptions, a useful candidate might share the same color while describing a different vehicle type. Its training role depends on the condition. An example’s broad topic therefore supplies only part of the information needed to assign its label.

## 4. Better judgments change the target being learned

Consider a score-regression model $g(X)$, where $X$ contains two passages and their question, and $Y$ is an annotator’s similarity score. Assume $Y$ has finite second moment. For a fixed input, let $\mu(X)=\mathbb{E}[Y\mid X]$.

**Derivation: what squared error learns.** Add and subtract $\mu(X)$ inside the square and take conditional expectations. The cross-term is zero because $\mathbb{E}[Y-\mu(X)\mid X]=0$:

$$ \mathbb{E}[(Y-g(X))^2\mid X]=\operatorname{Var}(Y\mid X)+(\mu(X)-g(X))^2. $$

The population-optimal unrestricted predictor is therefore the conditional mean. A finite neural model approximates this target under its capacity, data and optimization constraints.

This result explains why annotation design matters. If “appearance” mixes color, shape and size, the average score may combine several legitimate readings. Clarifying the question changes the target distribution. Retaining ambiguity or multiple readings may also be appropriate when the substantive concept has several defensible interpretations.

**Derivation: repeated judgments and correlated error.** Assume $m$ judgments have equal error variance $\sigma^2$ and pairwise error correlation $\rho$. The average error has variance:

$$ \operatorname{Var}(\bar\epsilon)=\sigma^2\left(\rho+\frac{1-\rho}{m}\right). $$

To obtain this, expand the variance of $m^{-1}\sum_i\epsilon_i$: there are $m$ variance terms and $m(m-1)$ ordered covariance terms. Independent errors set $\rho=0$. Positive correlation leaves a shared component as $m$ grows. Any shared bias also survives averaging.

This calculation is a model of annotation error, with explicit assumptions. It explains why several related LLM judgments can agree while preserving a common interpretation, and why independent domain-informed review addresses a different question from repeated model sampling.

## 5. Clustering adds assumptions about groups

An encoder produces points. A clustering procedure chooses groups using those points and its own assumptions. For example, $k$-means chooses assignments $a_i\in\{1,\ldots,k\}$ and centers $\mu_j\in\mathbb{R}^d$ to reduce:

$$ J=\sum_{i=1}^{N}\|z_i-\mu_{a_i}\|_2^2. $$

Here $N$ is the number of passages. Specifying $k$ supplies a resolution. The squared-distance objective favors compact groups around means.

**Derivation: why the centroid update helps.** For a fixed nonempty group $C$, differentiate $\sum_{i\in C}\|z_i-\mu\|_2^2$ with respect to $\mu$. The derivative is $2|C|\mu-2\sum_{i\in C}z_i$, which vanishes at the mean. The positive Hessian $2|C|I$ establishes its unique minimum. Assigning each point to its nearest center also weakly decreases $J$. Alternating these two updates makes the objective nonincreasing; initialization and tie handling affect the attained solution.

These guarantees concern the specified geometric objective. Expert interpretation supplies the relationship between the resulting groups and substantive categories of interest.

A graph view offers a second foundation. Construct a symmetric, nonnegative affinity matrix $W$ between passages. Let $D_{ii}=\sum_jW_{ij}$ and define the graph Laplacian $L=D-W$.

**Proof: connected components appear in the Laplacian’s nullspace.** For any $v\in\mathbb{R}^N$:

$$ v^\top Lv=\frac12\sum_{i,j}W_{ij}(v_i-v_j)^2\geq0. $$

Expand the square and use symmetry of $W$ to obtain the equality. The expression is zero exactly when $v_i=v_j$ across every positive-weight edge. Following paths makes $v$ constant on each connected component. Each component’s indicator vector belongs to the nullspace, and these indicators span it. Thus the nullspace dimension equals the number of connected components, including isolated vertices.

Read von Luxburg §§2–4 for graph construction, Laplacians and spectral clustering. The identity explains why low-eigenvalue directions reveal weakly connected structure. Choosing the affinity graph determines what connectivity means for the corpus. [von Luxburg, 2007](literature/von-luxburg-2007.pdf).

**Consequence.** Similarity training can improve the graph’s edges, while clustering still needs choices about resolution, overlap and sparse regions. Human pairwise preferences alone permit many possible partitions. For example, “A is closer to B than C” is compatible with grouping all three together at a coarse resolution or separating C at a finer resolution.

## What to carry into the next primer

The encoder selects features; supervision teaches their relationships; the loss converts judgments into parameter updates; clustering organizes the resulting geometry. Each stage adds a claim that needs its own evidence.

Before moving on, explain these three cases in your own words:

1. Two passages describe vehicles with the same color and different shapes. Under which question should they be neighbors?
2. A projection receives identical vectors for two passages. Which operation could recover their distinction?
3. A clustering algorithm produces stable groups by document source. What additional observation would establish their semantic usefulness?

Now read [how C-STS, Tu and CASE implement conditional similarity](02-conditional-encoders-and-discovery.md).
