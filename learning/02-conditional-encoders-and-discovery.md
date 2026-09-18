# Introduction to Conditional Language Representations

## The central idea

A conditional representation lets the comparison criterion change which meanings become neighbors.

Consider these descriptions again:

- **A:** a red bicycle parked beside a tree;
- **B:** a blue bicycle leaning against a wall;
- **C:** a red car waiting at a crossing.

Under “vehicle type,” A should be closer to B. Under “color,” A should be closer to C. The text stays fixed while the question changes. The model must interpret that question and make the requested relationship visible in its similarity scores.

The field brings together two problems. **Representation learning** asks what information a vector should preserve. **Conditional similarity learning** asks how the comparison criterion should control that information. In NLP, **conditional semantic textual similarity (C-STS)** names the task of rating two sentences under a natural-language condition. Conditional sentence embeddings are reusable vectors designed to support such comparisons.

The useful literature progresses through a sequence of design questions:

```text
several valid notions of similarity
    -> describe the desired notion in language
    -> decide where the condition enters the model
    -> teach or elicit the requested relationship
    -> measure whether the relationship transfers
```

The [first primer](01-learning-semantic-similarity.md) supplies the geometry and training foundations. Here we use those ideas to understand the modern methods and the choices they expose.

## Start with these

| Reading | Core idea | Why it belongs here |
|---|---|---|
| Deshpande et al. — *C-STS: Conditional Semantic Textual Similarity* | The same sentence pair can receive different similarity ratings under different conditions. | Defines the task and the main encoder formulations. |
| Su et al. — *One Embedder, Any Task* (INSTRUCTOR) | Natural-language instructions can guide representations across tasks and domains. | Explains how an embedding model can learn to use an instruction. |
| Tu et al. — *Linguistically Conditioned Semantic Textual Similarity* | Extracting an answer makes the selected meaning explicit; annotation also determines the target. | Connects the model’s input to the linguistic distinction being measured. |
| Zhang et al. — *CASE* | Conditional feature extraction can be followed by a compact supervised projection. | Separates what a frozen backbone represents from how its features are aligned to similarity judgments. |
| Yoo et al. — *Hyper-CL* | A condition can generate the transformation applied to cached sentence features. | Shows a different placement of conditional computation. |
| Liu et al. — *Conditional Semantic Textual Similarity via Conditional Contrastive Learning* | Graded reference differences can guide the training objective. | Explains why the loss and example construction deserve their own design. |

Read the first four to understand the task and the Tu–CASE design space. Hyper-CL and Liu then expose architecture and objective changes as separate levers. The later steering paper supplies an optional inference-time branch.

## 1. A condition defines which similarity the model should predict

[Deshpande et al.](https://aclanthology.org/2023.emnlp-main.345/) turn the intuition in our example into an NLP benchmark. Their C-STS dataset includes sentence pairs evaluated under conditions intended to produce high and low similarity. Read the task construction and §4 in the [local paper](literature/csts-2023.pdf).

This changes the prediction problem from a score for two sentences to a score for two sentences **and a condition**. Let $a,b$ denote sentences, let $c$ describe the criterion and let $s_\theta(a,b\mid c)$ be the model’s prediction.

Our toy example requires:

$$ s_\theta(A,B\mid\text{vehicle type})>s_\theta(A,C\mid\text{vehicle type}), $$

$$ s_\theta(A,C\mid\text{color})>s_\theta(A,B\mid\text{color}). $$

These inequalities specify the behavior an architecture should produce. They also reveal the evaluation unit: the model must distinguish comparisons that look similar at the broad topic level and change its preference when the condition changes.

A condition such as “color” is relatively concrete. Conditions such as “purpose,” “attitude” or “consequence” require more interpretation. Their wording, scope and reference labels become part of what the benchmark measures.

> Define the requested relationship before choosing how to encode it.

## 2. The architecture determines where the condition can act

The C-STS paper studies cross-, bi- and tri-encoder formulations. These names become useful once we trace the information through them.

A **cross-encoder** processes the two sentences and condition together. It can compare their words during encoding and produce a joint score. A **conditional bi-encoder** processes each sentence with the condition, yielding two reusable vectors. A **tri-encoder** encodes the sentences and condition separately, then combines their vectors.

| Formulation | What the heavy encoder sees | What can be cached |
|---|---|---|
| Cross-encoder | Both sentences and the condition together | A result for the specific comparison |
| Conditional bi-encoder | One sentence together with its condition | Each sentence–condition vector |
| Tri-encoder | Each sentence and the condition separately | Sentence and condition vectors |

Suppose there are $N$ sentences and $K$ conditions, and every combination is needed. A conditional bi-encoder requires approximately $NK$ sentence–condition encodings. A separate-encoding design can start with $N+K$ encodings, then apply a smaller composition operation for each combination. This is an operation-count comparison; actual runtime depends on batching, sequence lengths and the composition model.

The computational tradeoff creates an information tradeoff. Early conditioning lets the requested aspect influence token processing. Late conditioning asks a previously computed vector to contain enough information for subsequent questions.

The toy descriptions make the issue visible: if a cached representation preserves vehicle type and loses color, a later projection has little evidence from which to recover the red/blue distinction. An expressive composition function helps use available features; the upstream representation determines what is available.

## 3. Natural-language instructions become useful through training

Providing the condition as text gives the model an interface. Training determines how reliably the model uses that interface.

[INSTRUCTOR](https://aclanthology.org/2023.findings-acl.71/) embeds inputs together with task and domain instructions and trains contrastively across a collection of instruction-annotated datasets. Its experiments study performance across task families and instruction variants. Read §2 and the §4 analyses in the [local paper](literature/instructor-2023.pdf).

For example, “represent this sentence for topic classification” and “represent this sentence for finding a paraphrase” reward different relationships. The instruction tells the shared model which behavior the training example expects.

This supplies a bridge to C-STS. A task instruction describes what the representation will be used for. An aspect condition specifies which part of the sentence should govern a particular comparison. Both are language inputs, and both require a learned connection between the words in the instruction and the representation’s behavior.

General instruction-following performance therefore motivates a conditional encoder, while aspect-specific tests establish whether it makes the desired distinctions. The next question becomes: how can we make the selected meaning easier to inspect and compare?

## 4. Answering the question makes the selected meaning explicit

[Tu et al.](https://aclanthology.org/2024.acl-long.64/) decompose conditional similarity into generating condition-specific answers and comparing those answers. They also examine annotation problems and reannotate C-STS’s validation set. Read §3 for the target-label question, §4 for QA, §5 for trained models and §6 for linguistic analysis in the [local paper](literature/tu-2024.pdf).

Our running example shows what the decomposition buys:

| Text | Answer to “What color is the vehicle?” | Answer to “What type of vehicle is it?” |
|---|---|---|
| A | red | bicycle |
| B | blue | bicycle |
| C | red | car |

The extracted answers contain the desired distinction in a compact form. The embedding model receives much less surrounding content to organize. The intermediate text also lets a reader inspect what was selected.

A schematic Tu-style bi-encoder is:

$$ a=G(x,q(c)),\qquad z=E_\phi(a,c). $$

$G$ generates an answer from sentence $x$ and question $q(c)$. $E_\phi$ embeds the answer with its condition. Tu studies several configurations; this expression illustrates the bi-encoder route.

The paper’s base bi-encoder comparison rises from 49.6 to 73.9 Spearman correlation, scaled by 100, on its reannotated-data experiment. The authors use a 70/30 train/test division of that reannotated set. Their inference-only QA-SimCSE base score is 49.4. Training and the evaluation labels are therefore essential to interpreting the headline result.

### The decomposition creates two places to inspect an error

First ask whether the generated answer captures the requested property. An answer about the bicycle’s location would lose the color comparison before embedding begins. Then ask whether the embedding score preserves the answer’s meaning. Two answers can share vocabulary while expressing different claims.

A controlled diagnostic follows from this decomposition: hold the answer encoder fixed, replace generated answers with independently checked answers, and measure the change. That is a proposed diagnostic strategy derived from the architecture. Its result would help locate a source of error.

The category level also matters. “Bicycle” and “car” share the category “vehicle.” The desired score depends on whether the question asks for that broad category or a finer type. Tu’s linguistic analysis makes this granularity issue central to the task.

> An inspectable answer exposes which meaning was selected; the comparison model still has to preserve the relevant distinctions within that answer.

## 5. A frozen encoder’s geometry can be aligned with a small learned model

Tu makes the selected information explicit as generated language. Another route is to extract conditional features directly and learn how those features should be compared.

[CASE](https://aclanthology.org/2026.eacl-long.231/) takes that route. It constructs a condition-aware embedding, subtracts a standalone condition embedding and trains a projection using similarity ratings while freezing the backbone. Read §§3.1–3.2, equations 1–4 and the §4 ablations in the [local paper](literature/case-2026.pdf).

In the paper’s notation, the passage appears in an instruction and the condition is the text being represented. Write $F(c;I(x))$ for that contextualized condition vector. The construction is:

$$ e(x,c)=F(c;I(x))-F(c;I(\varnothing)),\qquad z=g_\psi(e(x,c)). $$

The subtraction compares the condition in the presence of a passage with the condition under an empty-passage instruction. The projection $g_\psi$ then maps the resulting features into a space aligned with the similarity task. CASE studies linear and nonlinear projections and reports improvements from its construction on C-STS.

In our example, the common condition “color” appears in every comparison. The passage must determine whether the resulting vector represents red or blue. The construction attempts to emphasize passage-dependent variation; interpreting the subtraction as a perfect removal of all irrelevant meaning would require additional evidence.

### What projection learning can change

The projection’s squared-error objective rewards cosine scores that match reference similarity ratings. Only the projection parameters change during this training stage. The backbone’s feature extraction remains fixed.

This separates two questions: are useful distinctions present in the features, and does the current geometry make them easy to compare? A projection can improve the second by reweighting or combining information available from the first.

There is a precise capacity boundary. If two inputs produce exactly the same feature vector, any deterministic projection maps them to the same output. Equality is preserved by function application. Differences that have already collapsed at the projection’s input require additional information or a change upstream.

This explains why a frozen projection is an informative baseline. Its success establishes that useful information can be recovered through the learned transformation. Its failure leaves several possibilities, including feature loss, limited projection capacity, insufficient data and optimization.

## 6. The condition can generate the transformation itself

CASE’s shared projection receives features that already depend on the condition. A different design uses the condition to determine the projection’s weights.

[Hyper-CL](https://aclanthology.org/2024.acl-long.41/) implements this with a **hypernetwork**: a network whose output supplies the parameters of another network. Read §§3.1–3.4 in the [local paper](literature/hyper-cl-2024.pdf).

Let $h_s\in\mathbb{R}^d$ encode the sentence and $h_c\in\mathbb{R}^d$ encode the condition. The schematic computation is:

$$ W_c=q_\psi(h_c),\qquad z(s,c)=W_ch_s. $$

$q_\psi$ generates the transformation matrix $W_c$. A color condition and a vehicle-type condition can therefore apply different transformations to the same cached sentence vector. Hyper-CL also develops a low-rank construction to manage the cost of generating matrices and combines contrastive and score-based supervision.

The architectural distinction is now concrete. A conditional bi-encoder lets sentence and condition tokens interact inside the backbone. Hyper-CL caches their features separately and learns a richer late interaction. CASE’s projection route aligns already conditional features with a shared learned map.

These designs address different computational budgets and information boundaries. The appropriate comparison holds the task, data and evaluation fixed while measuring accuracy, encoding cost and reuse across conditions.

## 7. The loss decides how strongly different meanings should separate

The architecture defines the available transformations. The loss specifies which relationships training rewards.

C-STS’s Quad objective pushes the predicted score under the high-similarity condition above the score under the low-similarity condition by a fixed margin. With predictions $s_{\mathrm{high}}$ and $s_{\mathrm{low}}$:

$$ \ell_{\mathrm{Quad}}=\max\{0,\lambda+s_{\mathrm{low}}-s_{\mathrm{high}}\},\qquad\lambda>0. $$

Suppose reference scores have already been normalized and differ by 0.2. A fixed margin of 1.0 asks for a much larger separation than that reference difference. This numerical example illustrates a distinction between learning the correct ordering and learning its graded magnitude.

[Liu et al.](https://aclanthology.org/2025.coling-main.306/) address this issue through Conditional Contrastive Learning. Their objective combines Weighted Adaptive Contrastive Loss, Balanced Contrastive Loss and regression terms. Read §§3.2–3.4 and equations 3–11 in the [local paper](literature/liu-ccl-2025.pdf).

Define the reference gap $\Delta y=y_{\mathrm{high}}-y_{\mathrm{low}}\geq0$ and the predicted gap $\Delta s=s_{\mathrm{high}}-s_{\mathrm{low}}$. One component of the objective is:

$$ \ell_{\mathrm{W\text{-}ACL}}=\Delta y\,|\Delta y-\Delta s|. $$

The term rewards matching the gap, weighted by its reference magnitude. Liu also changes the construction and weighting of contrastive examples. These operations address training signals; they remain distinct from changing where the condition enters the architecture.

At this point the main levers have concrete meanings:

| Lever | Operation | Representative work |
|---|---|---|
| Inputs | Generate the relevant answer before encoding | Tu |
| Parametrization | Generate a condition-dependent transformation | Hyper-CL |
| Feature construction and alignment | Extract conditional features, subtract a baseline and learn a projection | CASE |
| Objective and sample construction | Reward graded score differences and revise contrastive examples | Liu |
| Annotation | Clarify conditions and revise similarity judgments | Tu; Zhang et al.’s later data study |

A contribution can act on several levers. An ablation is useful when it isolates which operation accounts for a measured gain.

## Then read the inference-time work

## 8. Hidden-state intervention supplies another lever

A frozen model may contain useful information that its ordinary extraction procedure expresses weakly. This motivates changing the inference computation itself.

[Cheng et al.’s *Focusing Condition*](https://aclanthology.org/2026.acl-long.50/) introduces Self-Contrastive Steering. At a selected intermediate layer, it constructs a condition-masked view through attention masking and position adjustment, contrasts that view with the conditional representation, and continues the forward pass with the intervention. Read §4 and the ablations in the [local paper](literature/self-contrastive-steering-2026.pdf).

The method uses an additional self-attention computation at the selected layer and evaluates direct and projection-based elimination variants. Its contrast concerns an input-specific masked view inside the model. CASE’s subtraction concerns a standalone condition vector at the feature-construction stage.

Both approaches motivate questions about which information dominates an extracted representation. Their mechanisms and controls differ. For a steering method, the intervention layer, strength, masking procedure and added cost all belong in the experiment.

## 9. The benchmark defines what an improvement means

Tu’s annotation study and [Zhang et al.’s later data paper](https://arxiv.org/html/2509.14399v1) make a central measurement issue visible: model quality is judged against interpretations encoded in the dataset. Zhang and colleagues refine conditions and combine LLM ratings with existing annotations; CASE uses that later resource.

Keep the annotation version beside every result. Also record the backbone, split, training examples, generated inputs and metric. A number becomes informative when those ingredients explain the comparison it represents.

**Spearman correlation** measures agreement between score orderings. Compute ranks, average tied ranks and take their Pearson correlation. **Pearson correlation** measures linear association between the original scores. **Triplet accuracy** asks whether a preferred candidate receives the higher score. These metrics summarize different errors.

Generalization also has several meanings. A model can be tested on new sentences under familiar conditions, paraphrases of known conditions, entirely new conditions, or new combinations of attributes. Language and domain transfer add further changes. Report which changes the evaluation actually contains.

The toy example suggests a useful test pattern: change color while holding vehicle type fixed, then change vehicle type while holding color fixed. The model should respond according to the supplied condition. Natural-language versions require checking that the edits preserve the intended meanings.

## A practical mental model

```text
text + comparison criterion
        |
        +-> select information in the input       [Tu]
        |
        +-> condition feature extraction          [conditional bi-encoder]
        |
        +-> condition a feature transformation    [Hyper-CL]
        |
        +-> construct and align conditional features [CASE]
        |
        +-> intervene during inference            [self-contrastive steering]
        |
        v
representation -> similarity score -> evaluation under a defined question
                           ^
                           |
                  labels and training objective  [C-STS / Liu]
```

This is a map of intervention points. Individual methods may combine several of them. The unifying question is where the requested meaning becomes accessible and how the training or inference procedure makes comparisons reflect it.

## What to retain

1. Specify the criterion that should change a comparison.
2. Locate the condition inside the computation and identify what can be reused.
3. Separate information selection from the geometry used to compare selected information.
4. Inspect the objective and the construction of its examples together.
5. Bind every empirical comparison to its data version, split, backbone and metric.
6. Test new conditions explicitly when claiming generalization across conditions.
7. Treat semantic discovery through clustering as a downstream test of the learned geometry.

## Reading order

### Minimum core

1. [C-STS](literature/csts-2023.pdf) — learn the task, dataset and encoder formulations.
2. [INSTRUCTOR](literature/instructor-2023.pdf) — understand how instruction training connects language to embedding behavior.
3. [Tu](literature/tu-2024.pdf) — follow the annotation problem into answer-first modeling; keep trained and inference-only results separate.
4. [CASE](literature/case-2026.pdf) — trace the two embedding calls, subtraction and supervised projection.

### Then read

5. [Hyper-CL](literature/hyper-cl-2024.pdf) — draw the path from condition vector to transformation weights.
6. [Liu](literature/liu-ccl-2025.pdf) — work through the difference between a fixed margin and matching a graded reference gap.
7. [Focusing Condition](literature/self-contrastive-steering-2026.pdf) — identify the altered attention computation and the controls that test it.

### Optional depth

- [Zhang et al.’s annotation study](https://arxiv.org/html/2509.14399v1) for the dataset lineage behind CASE.
- [Conditional Similarity Networks](literature/conditional-similarity-networks-2017.pdf) for the earlier masked-subspace formulation in vision.
- [The first primer’s clustering section](01-learning-semantic-similarity.md#7-clustering-organizes-the-geometry-at-a-chosen-resolution) for the move from similarity scores to groups.

After the core readings, take one method and explain its inputs, trainable parameters, comparison rule and evaluation target using only those operations. That is the point at which the literature becomes a set of usable design ideas.
