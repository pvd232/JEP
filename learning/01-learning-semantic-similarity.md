# Introduction to Representation and Similarity Learning

## The central idea

An embedding gives objects coordinates. A similarity model gives those coordinates a purpose: objects judged alike should become neighbors, and distinctions that matter should remain visible.

Consider three descriptions:

- **A:** a red bicycle parked beside a tree;
- **B:** a blue bicycle leaning against a wall;
- **C:** a red car waiting at a crossing.

A resembles B in vehicle type and C in color. Before building a model, we already face the central question of this field: **which relationship should the representation preserve?** The input contains several valid relationships. The learning problem specifies which ones should govern comparison.

The useful conceptual foundation has four parts:

```text
examples and a notion of similarity
    -> a rule for rewarding useful comparisons
    -> a representation whose geometry supports those comparisons
    -> evaluation on new examples
```

This primer explains that chain. The [second primer](02-conditional-encoders-and-discovery.md) asks what changes when the comparison criterion itself becomes an input. Together they cover representation learning, supervised similarity learning and conditional sentence embeddings. Retrieval and clustering are downstream uses of the learned geometry.

## Start with these

| Reading | Core idea | Why it belongs here |
|---|---|---|
| Xing et al. — *Distance metric learning, with application to clustering with side-information* | Similarity judgments can teach a model how to measure distance. | Separates the observed features from the geometry used to compare them. |
| Reimers & Gurevych — *Sentence-BERT* | A language encoder can produce reusable sentence vectors trained for comparison. | Connects learned similarity to practical NLP. |
| Gao et al. — *SimCSE* | The construction of positive and negative examples shapes an embedding space. | Explains what contrastive learning actually teaches. |
| Veit et al. — *Conditional Similarity Networks* | Several notions of similarity can share a representation with condition-specific selection. | Introduces the reason for conditional geometry. |
| von Luxburg — *A Tutorial on Spectral Clustering* | Groups can be studied through a graph built from pairwise similarities. | Explains what happens when comparisons become corpus structure. |

Read the first three as the foundation. Veit supplies the bridge to the next primer. The clustering reading is useful when you want to understand what a learned representation makes discoverable.

## 1. Representation is a choice about what survives

An encoder is a function that turns an object into a vector. Write $h_\theta(x)\in\mathbb{R}^d$ for the vector representing input $x$, with $d$ coordinates and parameters $\theta$.

For a sentence, the input might contain words, syntax, named entities, a topic, a claim and a speaker’s position. The vector must organize information so that some later operation can use it. Different training tasks reward different organizations.

A deliberately artificial representation makes this concrete. Suppose we assign two coordinates to the descriptions above: “red” and “bicycle.” Then:

$$ h(A)=(1,1),\qquad h(B)=(0,1),\qquad h(C)=(1,0). $$

The first coordinate records color; the second records vehicle type. In ordinary Euclidean distance, A is equally far from B and C. The equality is appropriate for a geometry that gives both features equal weight. A task concerned with vehicle type needs a different weighting.

Real sentence embeddings have learned, distributed features: individual coordinates usually mix several properties. The toy construction isolates the issue that training must solve.

> A representation becomes useful through the information it preserves and the operations that can recover that information.

## 2. Learning distance means learning which differences count

[Xing et al.](https://ai.stanford.edu/~ang/papers/nips02-metric.pdf) learn a distance from pairs judged similar or dissimilar. Their method starts from feature vectors and adjusts the geometry used to compare them. Read §2 in the [local paper](literature/xing-2002.pdf).

Let $u,v\in\mathbb{R}^d$ be two feature vectors. A Mahalanobis distance is:

$$ d_M(u,v)=\sqrt{(u-v)^\top M(u-v)},\qquad M\succeq0. $$

$M$ is a symmetric positive-semidefinite $d\times d$ matrix. Positive semidefinite means that $w^\top Mw\geq0$ for every vector $w$, making the expression under the square root nonnegative.

Return to the toy example. Set:

$$ M=\begin{pmatrix}0&0\\0&1\end{pmatrix}. $$

Only the bicycle coordinate contributes. A and B now have distance zero; A and C have distance one. Reversing the diagonal weights makes color control the comparison. A full matrix can also combine coordinates, allowing learned features to be compared along new directions.

The training examples tell the optimization which distances should shrink or grow. This is the central operation of metric learning: learn a geometry from evidence about useful relationships.

### Why this really is a transformed Euclidean distance

The following derivation explains the positive-semidefinite requirement. By the spectral theorem, $M=Q\Lambda Q^\top$, where $Q$ is orthogonal and the eigenvalues on the diagonal of $\Lambda$ are nonnegative. Define $L=\Lambda^{1/2}Q^\top$. Then $M=L^\top L$, and:

$$ d_M(u,v)=\sqrt{(u-v)^\top L^\top L(u-v)}=\|Lu-Lv\|_2. $$

The model first transforms the points with $L$, then measures Euclidean distance. Symmetry and nonnegativity follow immediately. The triangle inequality follows from the norm inequality:

$$ \|Lu-Lw\|_2\leq\|Lu-Lv\|_2+\|Lv-Lw\|_2. $$

A positive-definite $M$ gives a metric. A singular $M$ permits distinct inputs to have zero distance, giving a pseudometric. Our toy example deliberately collapses color differences.

The proof establishes the geometry’s mathematical properties. Whether collapsing a particular distinction helps a language task depends on the task and the judgments used to train it.

## 3. A language encoder can learn the features as well

The previous model changed the comparison rule over existing features. A neural encoder can also change the features themselves. This opens a second lever: the model can learn which patterns in the input should contribute to the representation.

[Sentence-BERT](https://aclanthology.org/D19-1410/) makes this useful for sentence comparison. It applies shared encoder weights to sentences and pools token representations into sentence vectors. Sentence-pair training aligns those vectors with the desired relationships. Its §3 describes classification, regression and triplet objectives; see the [local paper](literature/sentence-bert-2019.pdf).

The practical advantage is reuse:

```text
sentence A -> shared encoder -> vector A --+
                                          +-> similarity score
sentence B -> shared encoder -> vector B --+
```

Once a sentence has a vector, many comparisons can reuse it. A model that jointly processes both sentences can examine their token interactions directly, while separate encoding places more responsibility on what each vector preserves.

A common comparison is cosine similarity. For nonzero vectors $u$ and $v$:

$$ s(u,v)=\frac{u^\top v}{\|u\|_2\|v\|_2}. $$

The numerator measures alignment; the denominator removes their lengths. For unit-length vectors, the connection to Euclidean geometry follows by expansion:

$$ \|u-v\|_2^2=u^\top u+v^\top v-2u^\top v=2-2s(u,v). $$

Thus decreasing Euclidean distance and increasing cosine similarity give the same neighbor ordering on normalized vectors. This is a useful computational equivalence under the stated normalization assumption.

> Reusable embeddings move the comparison problem into the representation: each vector must preserve what future comparisons need.

## 4. A training objective turns examples into geometric pressure

Suppose a training example says that A should resemble B more than C. Call A the anchor, B the positive candidate and C the negative candidate. These names describe their roles in this comparison. They can change with the task.

A triplet margin objective is:

$$ \ell=\max\{0,m-s(A,B)+s(A,C)\},\qquad m>0. $$

Here $s$ is the model’s similarity and $m$ is the required margin. If the positive similarity exceeds the negative by less than $m$, the example incurs a loss. Optimization can reduce it by increasing $s(A,B)$, decreasing $s(A,C)$, or both. Once the gap exceeds the margin, the loss is locally zero.

The crucial choice is how B became a positive and C became a negative. Under vehicle type, those roles fit our example. Under color, their roles reverse. The objective faithfully rewards the relationship supplied to it.

[SimCSE](https://aclanthology.org/2021.emnlp-main.552/) illustrates how positive-example construction can define a sentence-learning task. Its unsupervised variant uses two dropout views of the same sentence. Its supervised variant uses natural-language-inference data, with entailments supplying positives and contradictions supplying hard negatives. Read §§2–4 in the [local paper](literature/simcse-2021.pdf).

A standard softmax contrastive loss compares one preferred candidate with a set of alternatives. Let $s_j$ be the score for candidate $j$, let $p$ index the preferred candidate and let temperature $\tau>0$ set the score scale:

$$ \ell=-\log\frac{\exp(s_p/\tau)}{\sum_j\exp(s_j/\tau)}. $$

### What the gradient rewards

Define $q_j=\exp(s_j/\tau)/\sum_k\exp(s_k/\tau)$. Differentiating the negative preferred score and the log-sum-exp gives:

$$ \frac{\partial\ell}{\partial s_j}=\frac{q_j-\mathbf{1}[j=p]}{\tau}. $$

For the preferred candidate, the derivative is nonpositive. For alternatives, it is nonnegative. Gradient descent therefore rewards a higher preferred score and lower alternative scores, subject to their shared dependence on the model’s parameters.

An alternative that is also semantically appropriate receives pressure in the wrong direction for that interpretation. Such examples are often called false negatives. More generally, the quality of contrastive learning depends on how well the constructed comparisons express the desired task.

This connects the literature’s training methods to a practical design rule:

> Inspect the positive and negative construction before interpreting what a contrastive objective has taught the model.

## 5. Supervision specifies a relationship, at a chosen level of detail

A category label says that an example belongs to a named group. A pairwise score says how strongly two examples resemble each other. A triplet judgment specifies a relative preference. Each gives the learning algorithm a different amount and kind of information.

For our descriptions, a “vehicle” label includes A, B and C. A “bicycle” label separates C. A color comparison groups A with C. The labels can all be sensible because they answer different questions.

This explains how supervision selects a desired relationship among several available structures. An unsupervised method brings its own assumptions through its features and objective. A supervised method receives additional evidence about which relationships the evaluator wants it to preserve.

Graded scores introduce another issue: different annotators may interpret a broad instruction differently. A short derivation shows what squared-error regression learns from such judgments.

Let $X$ contain the compared items and their instruction, and let $Y$ be an annotator’s score with finite second moment. Write $\mu(X)=\mathbb{E}[Y\mid X]$. For a prediction $g(X)$:

$$ \mathbb{E}[(Y-g(X))^2\mid X]=\operatorname{Var}(Y\mid X)+(\mu(X)-g(X))^2. $$

To verify the identity, add and subtract $\mu(X)$ inside the square, expand it and use $\mathbb{E}[Y-\mu(X)\mid X]=0$. The unrestricted population optimum is the conditional mean. A finite model approximates it under its capacity and optimization constraints.

If annotators interpret “appearance” as a mixture of color and shape, the mean can reflect that mixture. Clarifying the instruction changes the target being learned. Agreement analysis therefore belongs alongside model evaluation.

## 6. Multiple valid similarities motivate conditional representations

A single fixed score orders B and C relative to A one way, or gives a tie. Our example requires opposite orderings under color and vehicle type. Both preferences can be represented by allowing the criterion to enter the computation:

$$ z=f_\theta(x,c),\qquad s(a,b\mid c)=\cos(f_\theta(a,c),f_\theta(b,c)). $$

Here $c$ specifies the comparison criterion. This is the conceptual move from general similarity to conditional similarity.

[Conditional Similarity Networks](https://openaccess.thecvf.com/content_cvpr_2017/html/Veit_Conditional_Similarity_Networks_CVPR_2017_paper.html) demonstrates this idea for images using learned masks over a shared embedding. Each condition selects or reweights dimensions. Read §3 in the [local paper](literature/conditional-similarity-networks-2017.pdf).

The schematic operation is $z(x,c)=m_c\odot h(x)$, where $m_c\in\mathbb{R}^d$ is the condition’s mask and $\odot$ means coordinate-wise multiplication. A color mask and a vehicle-type mask recover the two geometries in our toy example.

Natural-language conditions make the task richer. They require a model to interpret a linguistic description of the criterion, potentially including conditions introduced only at evaluation time. That is the starting point of the second primer.

## 7. Clustering organizes the geometry at a chosen resolution

A similarity function supports local comparisons. Clustering adds assumptions about how a whole collection should be grouped.

For example, $k$-means assigns vectors $z_i\in\mathbb{R}^d$ to $k$ centers $\mu_j$ by reducing:

$$ J=\sum_{i=1}^{N}\|z_i-\mu_{a_i}\|_2^2,\qquad a_i\in\{1,\ldots,k\}. $$

$N$ is the number of points and $a_i$ is the group assigned to point $i$. The choice of $k$ supplies a resolution; the objective favors compact groups around means.

For a fixed nonempty group $C$, the derivative with respect to its center is $2|C|\mu-2\sum_{i\in C}z_i$. It vanishes at the group mean, and the positive Hessian $2|C|I$ establishes the minimum. Assigning each point to its nearest fixed center also weakly decreases the objective. Alternating these operations makes the objective nonincreasing. This establishes an optimization property; interpretation of the groups requires additional evidence.

[von Luxburg’s tutorial](https://people.eecs.berkeley.edu/~jordan/sail/readings/Luxburg07_tutorial.pdf) gives a complementary graph view. Read §§2–4 in the [local paper](literature/von-luxburg-2007.pdf). Build a symmetric nonnegative affinity matrix $W$, set $D_{ii}=\sum_jW_{ij}$ and define the graph Laplacian $L=D-W$.

For any $v\in\mathbb{R}^N$:

$$ v^\top Lv=\frac12\sum_{i,j}W_{ij}(v_i-v_j)^2. $$

Expansion and symmetry establish the identity. It is zero exactly when $v$ is constant across every positive-weight edge, hence constant on each connected component. Component indicators span the nullspace. This explains how graph connectivity appears in the Laplacian’s eigenvectors.

The graph comes from a chosen similarity. Changing the criterion can therefore change both neighborhoods and apparent group structure. Studying such changes is a legitimate use of conditional representations.

## Mental model

```text
input -> encoder -> features -> comparison rule -> neighbors or groups
             ^                       ^
             |                       |
             +--- training examples -+
```

An encoder determines what information survives. A comparison rule determines how that information contributes to resemblance. A loss rewards particular relationships. A downstream procedure organizes the resulting geometry.

## What to retain

1. Define the relationship a useful comparison should preserve.
2. Separate feature learning from learning how to compare features.
3. Treat positive and negative construction as part of the task definition.
4. Use mathematical guarantees at the level they establish: geometry or optimization under stated assumptions.
5. Evaluate semantic agreement on new examples and, when relevant, new conditions.
6. Treat clustering resolution and interpretation as additional modeling decisions.

## Reading order

**Minimum core:** [Xing §2](literature/xing-2002.pdf), [Sentence-BERT §3](literature/sentence-bert-2019.pdf), then [SimCSE §§2–4](literature/simcse-2021.pdf). Trace each paper through the input, representation, score and loss it uses.

**Then read:** [Conditional Similarity Networks §3](literature/conditional-similarity-networks-2017.pdf), followed by [Introduction to Conditional Language Representations](02-conditional-encoders-and-discovery.md).

**Optional depth:** [von Luxburg §§2–4](literature/von-luxburg-2007.pdf) for graph-based clustering. The proofs above can be revisited independently while reading the model papers.
