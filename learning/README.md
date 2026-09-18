# Representation and similarity learning: a map of the literature

The organizing question is **how a model should represent similarity when the aspect of interest changes**. This is a standalone literature review and mathematical onramp. Its structure follows the research domain and the dependencies among its ideas.

## Where the names fit

| Level | Useful terminology | Scope |
|---|---|---|
| Broad ML field | Representation learning | Learn features useful for later tasks |
| Learning problem | Similarity learning / metric learning | Learn scores or distances from judgments and examples |
| Conditional form | Conditional similarity learning | Make the criterion of comparison an input |
| Specific NLP task | Conditional semantic textual similarity (C-STS) | Score sentence similarity under a natural-language condition |
| Model family | Conditional sentence embeddings / instruction-conditioned text embeddings | Produce reusable vectors whose behavior depends on conditions or instructions |
| Downstream uses | Retrieval, clustering and semantic discovery | Use the learned geometry to organize or search a collection |

“Conditional semantic encoder” is a reasonable description of a model. The terms above identify the broader field, specific task and model families more precisely. The review explains their relationships and links to the original papers.

## Start here

1. Read [the mathematical foundations](01-learning-semantic-similarity.md): embeddings, learned distances, training objectives, annotation targets and the geometry of clustering. Worked derivations state their assumptions.
2. Read [the literature review](02-conditional-encoders-and-discovery.md): how the field moves from several notions of similarity to natural-language conditioning, competing architectures and recent inference methods.
3. Use [the source library](literature/README.md) to read the primary papers. Local PDFs accompany the citations.

The primers follow the `/moa` teaching format: an explanation built through an ordered argument, followed by reading guidance. The filename of the second primer is retained for existing links; its content now surveys the field independently of the proposal.

## Reading sequence

**Prerequisites.** Read Xing et al. §2 for metric learning, Sentence-BERT §3 for sentence-vector training, and SimCSE §§2–4 for contrastive objectives. Use the first primer’s derivations while reading. Clustering proofs are an optional downstream branch.

The core sequence then gives each paper a distinct role:

| Order | Paper | Central question | Read closely |
|---|---|---|---|
| 1 | Conditional Similarity Networks — Veit et al., 2017 | Can one representation support several notions of similarity? | §3: masks and conditional triplets |
| 2 | INSTRUCTOR — Su et al., 2023 | Can natural-language instructions control embeddings across tasks? | §2 and §4 analyses |
| 3 | C-STS — Deshpande et al., 2023 | How should aspect-dependent sentence similarity be specified and tested? | Dataset construction and §4 |
| 4 | Hyper-CL — Yoo et al., 2024 | Can a condition generate a reusable transformation of sentence features? | §§3.1–3.4 |
| 5 | L-CSTS — Tu et al., 2024 | What happens when the requested meaning is made explicit as an answer? | §§3–6 |
| 6 | Conditional Contrastive Learning — Liu et al., 2025 | How should the objective use graded conditional similarity differences? | §§3.2–3.4, equations 3–11 |
| 7 | CASE — Zhang et al., 2026 | How much can conditional extraction and a compact learned projection achieve? | §§3–4 |
| 8 | Focusing Condition — Cheng et al., 2026 | Can inference-time intervention elicit better conditional representations? | §4 and ablations |

**Optional branches.** Zhang et al.’s 2025 annotation paper explains the data lineage used by CASE. Bilenko et al. and von Luxburg connect learned geometry to clustering. Nelson addresses computational qualitative interpretation. These branches answer different questions and can be read according to interest.

## How to use the review

For every method, identify the representation’s inputs, where the condition enters, the parameters that training changes, the loss, and the benchmark’s annotation version. Then ask which generalization setting the reported result actually measures.

The source library records downloaded bytes in `literature/SHA256SUMS`. Verify from that directory with `shasum -a 256 -c SHA256SUMS`.
