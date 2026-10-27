# Approved follow-up: four initial epochs

Status: **queued after the current proposition model finishes patience 1 and the comparison is published**.

Continue both saved initial checkpoints through epoch four on the same 2,135 comparisons. The control learns ratings; the proposition model writes propositions. Each receives 268 total initial updates, preserving the first two epochs.

Then both train ratings on all 6,051 jep-csts-v1 comparisons with **patience 1** and disabled time and epoch limits. Keep each model’s best validation checkpoint. Results continue at the [same epoch score table](epoch_scores.md). A positive selected validation difference queues the remaining proposition generations. [Generation progress](generation_progress.md).
