# JEP

Research materials for studying language representations and Colombian transitional-justice narratives.

## C-STS revision

[JEP C-STS revision 1](datasets/csts-jep-revision-v1/README.md) combines the repeated training/test audit with preserved validation V4.2: **6,051 training, 1,576 validation and 2,430 test comparisons**. The package includes ID-keyed annotations, the 25 adjudicated changes, independent initial judgments and verified reconstruction instructions.

The [exclusion audit](datasets/csts-jep-revision-v1/EXCLUSIONS.md) gives a rationale and peer check for each of the **1,587 current exclusions** and **2,532 earlier removals for caption overlap**.

## Start with the literature

The [two-primer learning guide](learning/README.md) introduces representation and similarity learning, then develops the conditional-language methods through Tu, CASE and related work. Each primer combines explanation, primary papers, worked examples and reading guidance.

- [Representation and similarity learning](learning/01-learning-semantic-similarity.md)
- [Conditional language representations](learning/02-conditional-encoders-and-discovery.md)
- [Source library](learning/literature/README.md)

## Application context

[Project Proposal JEP – Columbia (English)](Project%20Proposal%20JEP%20-%20Columbia%20%28English%29.docx) contains the existing substantive project proposal. The learning guide is a standalone introduction to the machine-learning field.

## Proposed collaboration

[Learning the Meanings of Justice](proposal/concept-note.pdf) is a short concept note connecting the Columbia team’s existing JEP research with opportunities for expert-supervised language representation learning.

The one-page PDF uses the NeurIPS 2023 style. Its [LaTeX source](proposal/concept-note.tex) and [expanded Markdown background](CONCEPT_NOTE.md) are available for editing. Rebuild the PDF from the repository root with `./proposal/build.sh`, using a TeX installation that provides `pdflatex`. The build keeps temporary files outside the repository.
