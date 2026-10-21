# Answer supervision on natural C-STS captions

This follow-up tests whether predicting the evidence relevant to a condition
improves conditional similarity. The captions, questions and rating splits are
the same as in the [rating study](CSTS_RUN.md). This protocol was written before
reviewing its reserved evaluation scores.

## Annotation

The C-STS release supplies similarity ratings. Its answer targets are generated
for this experiment by `Qwen/Qwen3-8B`, revision
`b968826d9c46dd6066d109eabc6255188de91218`. Thinking is disabled. The teacher sees one caption and its
condition. Its response identifies the target entity, requested attribute and an
exact evidence span. The span becomes the student's answer target. It sees neither the
other caption nor the similarity rating. Identical caption and condition inputs
receive one cached answer. Training and development captions receive answers.
The reserved evaluation captions are excluded from annotation generation.

An answer enters the loss when it matches a contiguous span of the caption
and a second teacher prompt accepts its relevance and completeness.
Abstentions and unsupported generations receive no answer loss. This check
establishes source support. The 128-example annotation pilot is reviewed for
relevance to the condition before generating the complete answer artifact.
The first two pilots used a 4B teacher. Their audits found errors in entity
binding and counting. A third pilot used an 8B teacher and exposed incomplete
counts and ambiguous questions. The current pilot adds the second check and
uses the next 128 records in the fixed hash order, excluding the earlier
384 records. These prompt changes use training and development captions only.
The teacher's two checks share model weights, so their errors can be correlated.
The full run stops if fewer than half of generations pass the source-span check.
The answers remain teacher annotations, with their provenance recorded in VIPER.

Tu et al. motivate asking a question about each passage before comparing its
meaning. Their [released material](https://github.com/brandeis-llc/L-CSTS)
contains revised ratings. The evidence-span prompt and shared training objective
are choices for this experiment.

## Model and losses

All comparison arms start from the same pinned FLAN-T5-small model. They contain
its encoder, decoder and a 128-dimensional projection. The encoder receives
`Condition: {q}\nPassage: {x}`. The projection maps mean passage-token states to
a unit vector. Cosine similarity predicts the normalized 0–1 rating.

For an accepted answer `a`, token cross-entropy is averaged within that answer.
The answer loss averages those values across accepted answers in the batch.
Let `D` contain rated pairs and `A` contain accepted caption answers:

\[
L_{rating}=\frac{1}{|D|}\sum_{(x_1,x_2,q,y)\in D}
\big(z(x_1,q)^\top z(x_2,q)-y\big)^2,
\qquad
L_{answer}=-\frac{1}{|A|}\sum_{(x,q,a)\in A}
\frac{1}{|a|}\sum_t\log p(a_t\mid a_{<t},x,q).
\]

Joint training minimizes `L_rating + λ L_answer`. Both gradients reach the shared
encoder. The rating gradient also trains the projection. The answer gradient
also trains the decoder. The decoder consumes the contextual encoder states.
Similarity prediction uses the projected passage vector.

## Comparisons

| Arm | Training |
| --- | --- |
| Ratings | Rating loss |
| Answers | Answer loss, then similarity evaluation of that checkpoint |
| Answers, then ratings | Answer pretraining, followed by rating training |
| Joint | Rating loss plus answer loss |
| Shuffled answers | Joint training with training answers reassigned within conditions |

Answer pretraining selects its checkpoint using development answer loss. Every
rating or joint stage selects its checkpoint using development MSE. The joint
weight is selected from `0.05` and `0.2` with seed 7. Seeds 8 and 9 repeat that
weight. The shuffled control uses the same weight. Reassignment occurs among
unique training caption and condition records. Development answers retain their
original assignment.

The Answers arm uses the same initialized projection as its matched seed. Answer
loss trains the encoder and decoder; the projection receives no gradient. Its
similarity score therefore measures transfer through that unchanged projection.
The sequential arm then trains the projection and encoder with rating labels.

## Annotation recovery

The original annotation stage reached 14,272 of 17,334 inputs before its
14,400-second execution limit expired. Recovery declares the saved JSONL as a
VIPER training input and validates its exact ordered caption and condition IDs,
batch boundary, source spans and acceptance decisions. It copies that prefix
and generates the remaining 3,062 records using the same teacher, prompts,
padding and batch size. Each stage has a six-hour execution limit. The manifest
records the saved-input SHA256, reused count and newly generated count.

Each stage uses the same batch size, eight-epoch cap, patience and optimizer
schedule as the rating study. The encoder learning rate is `3e-5`; the projection
rate is `1e-3`. The sequential arm receives an additional training stage. Its
extra time and labels are reported with its results. Rating-only arms contain
the same model components and initialization as the joint arms.

All settings and selected checkpoints are fixed before reserved evaluation.
MSE, Spearman correlation and condition-ordering accuracy use the same source
pairs. Comparisons across seeds use matched seeds. Source caption components
remain the units for uncertainty analysis. Reported scores apply to this
filtered C-STS split.

## Execution and visibility

The student keeps input tokens, answer tokens and labels on the GPU. Each step
encodes both sides of a pair in one batch. The decoder reuses those encoder
states. Shuffled indices move to the GPU once per epoch. BF16 forward passes
use the corrected VIPER precision handling. Checkpoints and epoch metrics are
native VIPER artifacts. The workspace publishes to the existing GCS repository.

Diagnostics include development scores before training and the fraction of
answers contributing to each split's loss. The first joint update records both
gradient norms on a shared encoder weight, their cosine, and the weighted
answer-to-rating norm ratio. These measurements help identify weak supervision,
dominant auxiliary gradients and conflicting updates.

The [progress command](csts_pilot/progress.py) reports epochs, development scores,
GPU utilization and storage. The annotation stage writes a count after each
generation batch. Its [manifest](csts_pilot/answers.py) records the teacher,
prompt, generation settings, acceptance fraction, time and peak GPU memory.

