# Learning the Meanings of Justice

*A proposed collaboration in language representation learning and transitional justice*

There is an opportunity to connect computer-science research with an ongoing Columbia team’s work on Colombia’s Special Jurisdiction for Peace (JEP). The central question is whether domain-informed human supervision can help language models represent the different meanings people express through abstract concepts such as justice, harm and reparation. The collaboration would pair a substantive research program and expert interpretation with technical oversight, reproducible evaluation and model development.

The team includes **Peter Dixon**, Associate Professor of Practice and Director of Columbia’s M.S. in Negotiation and Conflict Resolution, and a Senior Fellow at the Center for Justice. His research examines how local knowledge can inform peace and justice in conflict-affected communities. The team’s Spanish-language and transitional-justice expertise provides a foundation for deciding which distinctions matter and interpreting them in context. [Columbia profile](https://sps.columbia.edu/person/peter-dixon-phd); [professional biography](https://www.peterdixon.org/).

## An existing research foundation

The team has assembled a corpus of **243 public-hearing videos, spanning more than 1,500 hours**. Its summaries report an initial pilot covering **40 videos**, a dataset of **2,145 coded justice claims**, and a codebook containing **25 conceptions of justice**. It has also conducted repeated AI coding and an expert review of a 30-segment sample. These are team-reported results; inspecting the underlying annotations is the first step toward their reuse for machine learning. [Project context](sources/project-context.docx); [pilot presentation](sources/pilot-presentation.docx).

Their findings already expose a representation problem: victims, magistrates and comparecientes can discuss a shared dimension of justice while expressing different expectations about what it requires. A useful model should preserve both the shared concept and these differences in meaning. The planned Casanare extension examines demands for reparation, restoration and sanction, alongside narratives of harm.

The proposed workflow combines **AI extraction, human validation, inductive codebook development, AI coding, expert review and interpretive analysis**, with a further human review of interpretation proposed. This creates repeated opportunities to capture expert corrections, ambiguous cases and substantive distinctions as research data. [Workflow outline](sources/planned-workflow.jpeg).

## The computer-science opportunity

The technical space is **representation learning**, particularly **conditional semantic similarity**: learning text vectors that reflect a specified aspect of meaning. Deshpande et al.’s **C-STS** formalizes the task; **Tu et al.** generate aspect-specific answers before comparison; **CASE** learns a compact transformation of conditional embeddings; and **Liu et al.** refine conditional contrastive training. These supply established baselines and concrete choices about inputs, supervision and training objectives. [C-STS, 2023](https://aclanthology.org/2023.emnlp-main.345/); [Tu, 2024](https://aclanthology.org/2024.acl-long.64/); [CASE, 2026](https://aclanthology.org/2026.eacl-long.231/); [Liu, 2025](https://aclanthology.org/2025.coling-main.306/).

The working hypothesis is that carefully selected expert comparisons can improve the distinctions these representations preserve across new accounts. Existing codes provide starting examples. The Columbia team’s judgments—and, through an agreed partnership, annotations from JEP experts—could establish finer relationships within and across those codes. Capable LLMs could propose comparisons and flag disagreement, allowing expert attention to focus on informative cases alongside a representative sample.

An initial study would compare standard conditional embeddings, answer-first methods and models trained with this supervision. It would hold evaluation accounts separate and compare annotation strategies at matched effort. The primary outcome would be agreement with independent expert similarity judgments, followed by whether corpus retrieval and clustering produce useful, interpretable patterns. Measured gains would guide further encoder development; parity would direct attention toward annotation quality or extraction. The initial contribution would be a grounded benchmark and a controlled test of the value of expert supervision.

## Why coordinate now

The team is seeking technical oversight as it develops its AI-assisted methodology. CS participation could strengthen model selection, evaluation and reproducibility while gaining access to authentic research questions and informed feedback. Coordinating the annotation process early would let the same expert work support qualitative analysis and representation-learning experiments.

The social value is direct: helping researchers find, compare and preserve victims’ accounts of justice and repair across an archive that is difficult to examine at scale. This is an opportunity to do technically substantive work alongside people pursuing accountability, memory and peacebuilding. Faculty involvement would help shape a bounded first study and build a collaboration in which methodological progress and practical usefulness inform one another.
