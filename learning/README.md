# Representation Learning and Conditional Similarity: Two Primers

This directory contains two literature-guided introductions:

1. [Introduction to Representation and Similarity Learning](01-learning-semantic-similarity.md) — how examples define useful relationships, how training turns them into geometry, and what embeddings make possible for comparison and clustering.
2. [Introduction to Conditional Language Representations](02-conditional-encoders-and-discovery.md) — how a natural-language criterion changes the comparison problem, where the condition can enter a model, and how Tu, CASE and related methods address it.

The local source collection is indexed in [literature/README.md](literature/README.md). Thirteen papers are included as PDFs; additional primary sources are linked there.

## Suggested order

Read the foundations primer first. Its central chain—examples, objective, representation, comparison and evaluation—supplies the vocabulary used by the conditional methods.

Then read the conditional-language primer. It develops one question:

> How can a model preserve several meanings in the same text and let the requested criterion determine which ones govern similarity?

Both primers follow a running example and introduce papers as their ideas become necessary. Each starts with a reading table and ends with the principles to retain and an exact reading order. Proofs appear beside the claims they establish. Clustering is an optional downstream branch.

## Where this sits in machine learning

Representation learning is the broad field. Similarity and metric learning study how to learn useful comparisons. Conditional similarity makes the comparison criterion an input. C-STS is the specific sentence-similarity task; conditional sentence embeddings are one model family used to solve it.

The primers stand independently of the JEP proposal. They explain the research area and its design choices so that several possible applications and research directions can be assessed.

## Directory contents

```text
learning/
├── README.md
├── 01-learning-semantic-similarity.md
├── 02-conditional-encoders-and-discovery.md
└── literature/
    ├── README.md
    ├── SHA256SUMS
    └── *.pdf
```

The PDF manifest records the source bytes. From `learning/literature`, run `shasum -a 256 -c SHA256SUMS` to verify the local copies.
