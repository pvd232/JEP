# Approved follow-up: four initial epochs

Status: **queued after both current models finish patience 2 and publish their final comparison**.

Continue both saved initial checkpoints through epoch four on the same 2,135 comparisons. The control learns ratings; the proposition model writes propositions. Each receives 268 total initial updates, preserving the first two epochs.

Then both start full-data ratings training on all 6,051 jep-csts-v1 comparisons, with patience 2 and disabled time and epoch limits. Seed, batches, optimizer settings and frozen dataset hashes remain matched.

Results will continue at the [same epoch score table](epoch_scores.md). The completed preceding comparison will be archived beside it. A positive selected validation difference queues the remaining proposition generations. [Generation progress](generation_progress.md).
