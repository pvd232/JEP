# Learning similarity under a condition: a literature review

Similarity depends on the question. A red bicycle resembles a red car in color and a blue bicycle in vehicle type. A representation intended to support both comparisons needs a way to select the relevant information. This review maps that problem across metric learning, sentence embeddings, instruction tuning and conditional semantic textual similarity.

The organization follows the field’s conceptual dependencies. The [mathematical primer](01-learning-semantic-similarity.md) supplies the geometry and loss derivations. This review concentrates on what each line of work changes, what its evidence establishes and which questions remain open.

## 1. Map the problem before choosing its name

**Representation learning** learns features from data. **Similarity learning** trains a score that reflects judgments of resemblance. **Metric learning** is a closely related tradition that learns distances or embeddings with useful geometry. Neural similarity scores can have a broader mathematical form than a strict metric.

**Conditional similarity learning** makes the comparison criterion an input. The condition can be a discrete attribute, a task instruction or a natural-language description. **Conditional semantic textual similarity**, abbreviated **C-STS**, is a particular NLP task: predict similarity between two sentences under a supplied condition. **Conditional sentence embeddings** are one class of representation used to solve it. “Conditional semantic encoder” is understandable descriptive language; these more specific terms give clearer search targets. [Conditional Similarity Networks](literature/conditional-similarity-networks-2017.pdf); [C-STS](literature/csts-2023.pdf).

Several neighboring problems contribute useful ideas:

| Neighboring area | Its question | Connection to conditional similarity |
|---|---|---|
| Instruction-tuned embeddings | How should a representation adapt to a task or domain instruction? | Learns an interface between language instructions and embedding behavior |
| Contextual word representations / sense induction | Which meaning does a word express in its surrounding text? | Context resolves usage; a comparison condition selects which aspect matters |
| Disentangled representations | Can different factors be represented with some separation? | May support selecting attributes or semantic dimensions |
| Conditional computation / hypernetworks | Can an input control transformations or weights? | Supplies architectures for condition-dependent projections |
| Retrieval and clustering | Which items should be neighbors or form groups? | Tests how a learned similarity behaves in downstream use |

This table is a conceptual map. The studies below support different parts of it; they have distinct benchmarks and guarantees.

## 2. Similarity can be learned as geometry

Xing and colleagues learn a positive-semidefinite distance matrix from similarity constraints and apply it to clustering. The central abstraction is that observed features and the rule for comparing them are separate objects. Read §2 alongside the primer’s factorization proof. [Xing et al., 2002](literature/xing-2002.pdf).

Veit, Belongie and Karaletsos extend the multiple-similarities idea in computer vision. Their **Conditional Similarity Networks** jointly learn image embeddings and masks that select or reweight dimensions for different similarity notions. Read §3, especially the condition-specific triplets and masking operation. The condition indexes a learned notion of similarity; free-form linguistic conditions require an additional mechanism. [CVPR 2017](literature/conditional-similarity-networks-2017.pdf).

In schematic notation, with representation $h(x)\in\mathbb{R}^d$ and condition mask $m_c\in\mathbb{R}^d$:

$$ z(x,c)=m_c\odot h(x). $$

The symbol $\odot$ means coordinate-wise multiplication. A condition changes the contribution of each coordinate. This is a concrete architectural answer to “similar in which respect?” It also reveals a recurring design choice: organize information so that a later operation can select it, or let the condition influence feature extraction itself.

## 3. Sentence embeddings make language comparisons reusable

Sentence-BERT shares encoder weights across sentence inputs and trains representations using sentence-pair supervision. Its pooling and objectives turn transformer outputs into reusable vectors for similarity comparisons. Read §3 for classification, regression and triplet training. [Reimers and Gurevych, 2019](literature/sentence-bert-2019.pdf).

SimCSE develops contrastive training for sentence embeddings. Dropout supplies paired views in its unsupervised method; natural-language-inference data supplies supervised positives and hard negatives. Read §§2–4 with the primer’s gradient derivation. The construction of positive and alternative examples determines which distinctions training rewards. [Gao, Yao and Chen, 2021](literature/simcse-2021.pdf).

These papers supply general sentence-representation machinery. Conditional similarity adds a further requirement: the same pair may deserve different scores under different questions. An encoder’s general similarity performance and its sensitivity to a specified aspect are therefore separate empirical properties.

## 4. Instructions teach an embedding model what it is being used for

**INSTRUCTOR** embeds text together with task and domain instructions. Su and colleagues train it contrastively on a diverse collection of instruction-annotated embedding datasets. Their experiments span several task families and examine the role of instructions and instruction variation. Read §2 for architecture, loss and training data, then §4 for the analyses. [Su et al., 2023](literature/instructor-2023.pdf).

This establishes an important bridge: the encoder can learn to treat natural-language instructions as part of its input interface. A task instruction such as “represent this passage for retrieval” specifies intended use. An aspect condition such as “compare the vehicles by color” specifies which content should govern a particular similarity judgment. Both can influence embeddings; their evaluation questions differ.

The methodological lesson is to test the exact instruction behavior of interest. Broad multitask performance measures task adaptation. Controlled comparisons under different aspects measure selection among meanings inside the text.

## 5. C-STS isolates aspect-dependent similarity

Deshpande and colleagues introduce **C-STS**, pairing sentences with natural-language conditions and similarity ratings. The same pair appears under conditions intended to yield higher and lower similarity. The paper evaluates cross-, bi- and tri-encoder formulations. Read the dataset construction and §4, especially the paired-condition objective. [Deshpande et al., 2023](literature/csts-2023.pdf).

The architectures place interaction at different points:

| Formulation | Computation | Reuse |
|---|---|---|
| Cross-encoder | Jointly process both texts and the condition to produce a score | Joint inference for each pair |
| Conditional bi-encoder | Encode each text together with the condition, then compare | Cache each text–condition representation |
| Tri-encoder | Encode each text and the condition independently, then combine | Cache text and condition features separately |

Define $s_\theta(a,b\mid c)$ as predicted similarity under condition $c$. The Quad margin objective has the form:

$$ \ell_{\mathrm{Quad}}=\max\{0,\lambda+s_\theta(a,b\mid c_{\mathrm{low}})-s_\theta(a,b\mid c_{\mathrm{high}})\},\qquad\lambda>0. $$

This rewards a score gap in the intended direction until a margin is reached. Its relationship to graded reference scores becomes a target for later work.

## 6. Hyper-CL lets the condition generate a transformation

**Hyper-CL** addresses the interaction–reuse tradeoff. A sentence encoder produces $h_s$, a condition encoder produces $h_c$, and a hypernetwork generates a projection matrix from $h_c$. The matrix transforms the sentence embedding. The method also introduces a low-rank formulation to control the cost of generating weights. Read §§3.1–3.4 for the architecture, training and factorization. [Yoo et al., ACL 2024](literature/hyper-cl-2024.pdf).

The central computation is:

$$ W_c=q_\psi(h_c),\qquad z(s,c)=W_ch_s. $$

Here $q_\psi$ is a network whose output parameterizes another transformation. The paper combines contrastive and score-based supervision and evaluates C-STS and knowledge graph completion. Its results support learned late interaction as an accuracy–efficiency option on those tasks.

This architecture changes the parametrization: the condition controls the transformation itself. In a prompted bi-encoder, the condition participates in token processing. Both produce conditional vectors, with different information and computation paths.

## 7. Tu examines the target meaning and introduces answer-first representations

Tu and colleagues’ **Linguistically Conditioned Semantic Textual Similarity** reexamines C-STS annotation and reannotates the validation set. It turns conditions into questions, generates corresponding answers and uses those answers in similarity analysis. Read §3 for annotation issues, §4 for answer generation, §5 for trained models and §6 for linguistic feature analysis. [Tu et al., ACL 2024](literature/tu-2024.pdf).

A schematic pathway is:

$$ a=G(x,q(c)),\qquad z=E_\phi(a,c). $$

$G$ generates an answer to question $q(c)$ from text $x$; $E_\phi$ embeds the answer, with the condition included in applicable variants. The paper’s trained base bi-encoder comparison improves Spearman correlation from 49.6 to 73.9, scaled by 100, on reannotated labels. The inference-only QA-SimCSE base result is 49.4; those are distinct experimental settings.

The conceptual addition is an explicit linguistic intermediate. It makes the selected meaning inspectable and introduces generation as another source of variation. The paper’s category-versus-feature analysis also illustrates why a shared broad category and a shared specific attribute can warrant different judgments.

## 8. Liu changes the training signal

Liu and colleagues’ **Conditional Contrastive Learning** retains bi- and tri-encoder formulations while revising the objective and sample construction. It combines Weighted Adaptive Contrastive Loss, Balanced Contrastive Loss and score-regression terms. Read §§3.2–3.4 and equations 3–11. [Liu et al., COLING 2025](literature/liu-ccl-2025.pdf).

A key argument concerns fixed-margin separation: reference scores also specify how large a conditional similarity gap should be. Define $\Delta y=y_{\mathrm{high}}-y_{\mathrm{low}}\geq0$ and $\Delta s=s_{\mathrm{high}}-s_{\mathrm{low}}$. The weighted adaptive term can be written:

$$ \ell_{\mathrm{W\text{-}ACL}}=\Delta y\,|\Delta y-\Delta s|. $$

This is one component of the full training objective. It weights agreement with the reference gap by the gap’s magnitude. Balanced contrastive learning separately addresses the treatment of generated views and potentially problematic negatives.

The contribution sits primarily in the loss and training examples. A clear comparison with Hyper-CL therefore asks different questions: what changes the available transformation, and what changes the relationships that optimization rewards?

## 9. CASE separates conditional feature extraction from supervised alignment

**CASE** constructs condition-aware embeddings with an LLM encoder, subtracts a standalone condition embedding, and trains a compact projection using similarity ratings. Read §§3.1–3.2 and equations 1–4, followed by the §4 ablations. [Zhang, Zhou and Bollegala, EACL 2026](literature/case-2026.pdf).

In notation matching the paper’s conceptual construction:

$$ e(x,c)=F(c;I(x))-F(c;I(\varnothing)),\qquad z=g_\psi(e(x,c)). $$

$F$ uses the paper’s prompting and pooling; $I(x)$ supplies the passage-bearing instruction. The backbone stays frozen during projection training. The supervised objective minimizes squared error between projected cosine similarity and reference ratings. The paper studies linear and nonlinear projections.

This provides two levers: the representation extracted from the backbone and the learned alignment to the similarity task. The shared projection receives already conditioned features. Hyper-CL instead generates transformation weights from the condition embedding.

CASE uses a later C-STS annotation resource. Zhang and colleagues’ 2025 data paper refines conditions and combines LLM ratings with existing annotations. Tu’s reannotation and this larger resource belong to the same measurement discussion, with distinct procedures and dataset versions. [Data paper, arXiv v1](https://arxiv.org/html/2509.14399v1).

## 10. Inference-time steering changes internal computation

Cheng and colleagues’ **Focusing Condition** introduces Self-Contrastive Steering. At an intermediate layer, it forms conditional and condition-masked views, adjusts positions for the masked view, and uses their contrast to steer the representation before continuing the forward pass. Read §§4.1–4.3 and the ablations. [ACL 2026](literature/self-contrastive-steering-2026.pdf).

The paper evaluates a training-free intervention requiring an additional self-attention computation at the selected layer. It offers direct and projection-based elimination variants. This differs operationally from subtracting a standalone condition vector after embedding extraction: the contrast uses an input-specific, condition-masked view inside the network.

The general research question is whether useful conditional information already exists in hidden states and can be elicited through a better inference procedure. Answering that question requires matched backbone and prompt controls, sensitivity to intervention settings and measured computational overhead.

## 11. Read results through their measurement choices

These papers vary the benchmark, annotation version, backbone, training data and evaluation protocol. Their reported scores become comparable when those ingredients match.

**Spearman correlation** measures agreement between score orderings: rank predictions and references, average tied ranks, then compute Pearson correlation between the ranks. **Pearson correlation** measures linear association between scores. **Triplet accuracy** measures whether a preferred candidate receives the higher similarity. Each metric preserves different information about a model’s errors.

A useful review asks about several forms of generalization:

- new sentences under familiar conditions;
- paraphrases of a familiar condition;
- new conditions or attribute combinations;
- changes in language, domain or passage length;
- transfer from similarity scoring to retrieval or clustering.

These are evaluation dimensions for comparing studies, with evidence assessed paper by paper. A benchmark gain can arise through improved feature selection, improved score calibration, cleaner reference judgments or several changes together. Matched ablations identify the contribution of each operation.

## 12. What remains open in the problem domain

The literature supports multiple functioning ways to condition a representation. Several broader questions remain productive research directions, with scope to be established for each dataset:

**Condition interpretation.** A natural-language condition may admit different granularity or refer to several entities. Annotation analysis and model analysis interact here.

**Compositional generalization.** A model may learn familiar conditions while struggling to combine attributes or follow novel, finely specified comparisons. Evaluation needs separate condition splits to measure that ability.

**Information selection and capacity.** A cached embedding trades reusable computation against the information needed for future conditions. Hypernetworks, early conditioning, answer generation and hidden-state interventions explore different points in this tradeoff.

**Faithfulness and invariance.** Desired similarity should respond to relevant changes and remain stable under meaning-preserving paraphrase. Evidence spans and controlled edits can help test that behavior, with appropriate checks on the edits’ validity.

**Downstream structure.** Retrieval and clustering impose additional requirements on the geometry. The [foundations primer](01-learning-semantic-similarity.md) explains why local similarity judgments and global partitions need separate validation.

These are synthesis questions drawn from the methods’ assumptions and evaluation boundaries. A specific algorithmic hypothesis should identify which boundary it targets and the experiment that would distinguish its explanation from alternatives.

## What to retain

Locate the condition in the computation. Identify which parameters training changes. Inspect how labels define similarity. Compare models on the same target and data version. Separate proofs about a mathematical operation from empirical claims about meaning.

For an ordered reading path, use [the guide index](README.md). The purpose is to understand the research landscape well enough to formulate and evaluate several possible research directions.
