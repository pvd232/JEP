# Expert-guided multiple-prototype claim codebook pilot

Status: proposed experiment implementation, awaiting review. No actual expert JEP annotations or claim features are supplied in this PR; no study has run. Synthetic fixtures verify mechanics only. This is separate from the English C-STS score screen and the unsuccessful single hard-code VQ experiment. English pair ratings cannot substitute for expert claim-code membership.

## Question and minimum decision

Can two semantic realizations of each expert-defined code improve independent claim coding over a centroid readout with the same learned parameter count? A claim may receive zero, one or several condition-specific codes. Numeric nearest-prototype IDs or top-k distances alone do not establish validated multilabel coding or a useful legal taxonomy. Loss reduction, prototype occupancy and successful fixture tests do not establish codebook quality.

The dictionary vocabulary and definitions must be frozen by experts before fitting. Every code must have at least two independent positive and negative training groups, at least two positive training claims (or the requested number of prototypes), and two independent positive and negative development groups. Each condition must have at least ten independent source groups in each partition. Unsupported codes fail preflight and are identified explicitly; they are not silently removed. These minima are execution floors, not evidence of adequate statistical power or rare-demand coverage. Experts must determine the sampling unit and whether the source groups are actually independent. Claim metrics weight claims equally, not groups; heavily represented groups can dominate them. Selection metrics are development diagnostics, not confirmatory results.

## Matched comparison

For frozen unit claim feature x, both arms learn the same bias-free projection W, m=2 vectors v per code k, and bias b per code. Set z=normalize(Wx), p=normalize(v), and s[k,j]=z dot p[k,j].

The centroid control uses logit[k] = 5 * mean_j s[k,j] + b[k]. This is similarity to the arithmetic mean of unit prototype vectors, without renormalizing the mean. The candidate uses logit[k] = 5 * 0.2 * (logsumexp_j(s[k,j]/0.2) - log(m)) + b[k]. Independent sigmoid outputs support zero/many assignments. The candidate can respond to different realizations of one code; the control averages them. Parameter counts, trainable tensors, frozen features, labels, seeds, initialization, batches, optimizer settings, epoch/time ceilings and threshold grid match. Their functional expressiveness differs; this is not a theoretical equal-capacity comparison.

Initialize W identically per seed; initialize each code's prototypes from seeded training-only expert-positive projected claim features. No development examples or heldout dictionary construction are permitted. Both arms optimize binary cross entropy averaged over observed applicable codes within each claim and then over claims. Missing/null labels contribute no gradient; there is no L1 term or unobserved-as-negative sparsity penalty. Observed 0 means an explicit expert negative, not absence of a positive annotation.

Checkpoint and one global probability threshold are selected on development macro-F1. At each checkpoint, ties across the fixed thresholds [0.3, 0.5, 0.7] use micro-F1 then the higher threshold. Across epochs retain the earliest strict macro-F1 improvement, including epoch zero. Patience is five validation checks without strict macro-F1 improvement. Maximum 48 epochs, 600 seconds per arm/seed, seeds 7/8/9, CPU only. A time-budget failure preserves a failed native attempt rather than publishing a partial fit as success. Different stopping epochs are reported; exposure is identical only on shared epochs, with identical order hashes retained.

## Annotation and feature contract

Supply a JSON annotation document with exactly these fields:

```json
{
  "schema_version": 1,
  "expert_reviewed": true,
  "annotation_protocol": "Reference to supplied expert coding/adjudication protocol",
  "codebook_version": "Frozen expert vocabulary version",
  "reviewer_ids": ["opaque-reviewer-id"],
  "codes": [{"id": "code-id", "condition": "condition text", "definition": "expert definition"}],
  "training": [{"claim_id": "claim-1", "passage_id": "passage-1", "source_group": "independent-source-1", "condition": "condition text", "text": "Claim text", "labels": {"code-id": 1}}],
  "validation": [{"claim_id": "claim-2", "passage_id": "passage-2", "source_group": "independent-source-2", "condition": "condition text", "text": "Different claim text", "labels": {"code-id": null}}]
}
```

This illustrates the schema only and intentionally lacks required support; it cannot pass preflight. Each included claim needs at least one observed applicable label. Labels must be integer 0/1 or null; omitted labels are unknown. The expert_reviewed field and reviewer IDs record a supplier assertion; software cannot authenticate expertise or adjudication. Review the real annotation source and sampling protocol before authorizing any run. Claim segmentation and code definitions must be expert supplied or certified, never invented by this runner. Broader deployment needs independent JEP heldout coding, rare-code review, within-condition ambiguity/adjudication checks, and certified claim edits. None is claimed here.

Each split's torch feature file contains exactly `keys`, `vectors`, `provenance`. Keys are unique `[condition, text]` pairs covering the annotated split exactly; vectors are finite unit FP32 CPU N-by-D tensors, and provenance has `model_sha256` for the externally frozen encoder artifact. Files and the frozen encoder digest are pinned in the input manifest. Source groups, passage IDs, claim IDs and canonical claim texts must be disjoint across partitions. Duplicate canonical condition/claim inputs are rejected so repeated claims cannot overweight training. Training/validation feature widths and model digests must agree. This pilot performs no encoder inference or update. Cache provenance is an assertion backed by supplied sealed artifacts, not an automatic proof of how features were created; inspect the encoder/source producer records during review.

The portable input manifest resolves relative file paths against its own directory:

```json
{
  "annotations": {"path": "expert-claims.json", "sha256": "<64 lowercase hex>"},
  "training": {"path": "training-claim-features.pt", "sha256": "<64 lowercase hex>"},
  "validation": {"path": "validation-claim-features.pt", "sha256": "<64 lowercase hex>"},
  "model_sha256": "<frozen encoder artifact SHA256>"
}
```

## Outputs and execution

Run `python -m csts_pilot.multiple_codebook_run --root /path/to/checkout --inputs /path/to/manifest.json`. The default performs validation only. After code and actual input review, add `--execute --name unique-attempt-name` to create a native VIPER CPU TRAIN stage with immutable copied inputs followed by a byte-copy development-input publisher and independent EVAL replay. Execution rejects a dirty checkout. Use a reviewed clean Git checkout and the repository's pinned environment. Native model, resume state, trace and metric artifacts are sealed locally; existing asynchronous publication queues promotion to the configured workspace. Existing attempts are never overwritten. The EVAL stage restores selected weights, verifies the exact selected probabilities and metrics, then exports a native artifact-recomputed candidate-minus-centroid macro-F1 gain for every seed and their mean. It uses the same development partition used for selection; canonical native `test` is only a binding name for these development rows. There is no fresh heldout or benchmark-test access; a separately reviewed independent evaluation must freeze all selections first.

For each seed/arm retain initial state digest, shared-epoch batch-order hashes, chosen weights, threshold, probabilities aligned to development claim IDs, per-code/per-condition claim metrics, observation coverage, source-group support, passage OR metrics, terminal model/optimizer/batch-generator states and a native RNG envelope. Passage predictions OR only the supplied included claim assignments within (passage, condition); the output marks this scope explicitly. The pilot does not validate an exhaustive claim inventory. These are not full-passage coding metrics unless experts certify that every relevant claim was included. Gold passage membership is positive when any claim is known positive, negative only when every included claim is explicitly negative, and otherwise unknown. No noisy-OR independence assumption is made.

The preregistered comparison is paired candidate-minus-centroid development macro-F1, inspected alongside all seeds, per-code confusion counts and passage OR results. Do not choose one favorable seed. No inference of statistical significance is planned from this small development pilot. A promising result licenses an independently powered expert evaluation with source-group uncertainty and locked thresholds/checkpoints, not deployment.
