# Cached annotation format pilot

The user authorized the lightweight cached-record comparison on October 21, 2026. This screen uses existing teacher metadata, with no new ontology, inferred values, normalized values, missing-information labels or teacher generation.

| Arm | Student annotation target for the same example |
| --- | --- |
| A evidence | `red` |
| B prose | `The target is "shirt" and the attribute is "color". The supporting evidence is "red".` |
| C record | `{"target": "shirt", "attribute": "color", "evidence": "red"}` |

A versus B tests the added metadata and its supervision. B versus C tests serialization of the same facts. These cached target and attribute strings are free-form teacher descriptions, rather than a formal type ontology.

## Execution status

The complete 17,334-record teacher cache was restored through its immutable native VIPER reference and independently checked against SHA256 `1dcd743762cfad9f42b78775510c526e3ce6dd0c51716caf4df3234442ac1c94`. It contains 11,312 accepted answers. All three derived formats retain the same records, order, acceptance mask and underlying evidence. Native CPU preparation succeeded and published the inputs and derived artifacts to durable storage; exact retrieval references are in [csts_annotation_format_retrieval.json](csts_annotation_format_retrieval.json).

A stratified assistant review of 100 cached records found 4 ambiguous conditions, 2 partial-information cases and 3 cases requiring contextual inference; 91 had no specific concern identified. This is a source review, not expert accuracy measurement. The cached `target` field varies in semantic role, so this remains a free-form metadata experiment. The common cohort is retained. Review records appear in [csts_annotation_format_metadata_audit.json](csts_annotation_format_metadata_audit.json).

Median annotation target lengths are 5 tokens for evidence, 26 for prose and 35 for JSON; maximum lengths are 50, 71 and 80. No target exceeds the 192-token diagnostic generation limit. Equal update counts therefore have different token costs; these are reported explicitly.

Validation passed: twelve target-preservation, corruption-refusal, checkpoint-selection, fixed-budget training-loop and shared-gradient checks, Ruff, Pyrefly, and live native CPU preparation. The isolated runner is implemented as `python -m csts_pilot.annotation_format_run`. No GPU training has started as of this preparation update.

Google Cloud authentication is restored. The original L4 VM remains stopped, with both disks preserved. Starts in `us-west4-c` failed with GPU stockouts. Following user direction, all three Tokyo zones were tried with 4-, 8- and 12-vCPU L4 configurations; all nine requests returned stockouts. No Japan VM or pilot boot disk was left behind. The prepared deployment reproduces Python 3.13.15, PyTorch 2.14.0+cu130 and the original VIPER precision fix. Capacity retries are enabled. GPU validation and a discarded-model throughput profile precede the common budget freeze. Exact cloud errors and the fresh original VM status appear in [csts_annotation_format_capacity.json](csts_annotation_format_capacity.json). See [csts_annotation_format_preparation.json](csts_annotation_format_preparation.json) for the completed preparation evidence.

## Preparation

Use the existing SSH and Google Cloud helpers and configured credentials. Inspect completion state and process identities before action, then use a separate checkout and output directory. Preserve the previous study, its environment and all completed artifacts.

Locate the full annotation artifact through the original study's native VIPER run and retrieval receipt. Verify its manifest reports 17,334 records and 11,312 accepted answers. Use `python -m csts_pilot.annotation_formats --source FULL_CACHE --destination NEW_EMPTY_DIRECTORY` to derive three JSONL inputs. This command validates each accepted record against its saved teacher response, source-span check and second-review acceptance before rendering targets. It records all input and output hashes and preserves original record identities, order and acceptance decisions. It never calls a teacher or starts training.

Audit a stratified sample of cached target and attribute values before training. Existing teacher acceptance validates the evidence answer; semantic correctness of the added metadata requires a separate check. Record audit judgments and any failure before deciding whether the common cohort can be used.

## Matched training and evaluation

Use FLAN-T5-small at the existing pinned revision, the existing split and seed 7. Each arm receives annotation pretraining followed by rating training, starting from identical initial weights. Freeze the cohort, common annotation updates, rating batches, learning-rate schedules, optimizer restart and selection rules before any arm runs. Keep the existing per-answer-normalized token cross-entropy and rating MSE losses.

Profile the longest targets before setting a common update budget. Check complete target tokenization and record non-padding tokens, target lengths and GPU time. The proposed training ceiling is approximately 30 GPU minutes across the three arms. Prior timings suggest six annotation epochs plus eight rating epochs as a starting budget; freeze the actual common budget after profiling. Select annotation checkpoints by development answer CE within each arm and rating checkpoints by development Spearman. The runner explicitly enables a fixed epoch budget and Spearman selection for rating stages; historical runs retain their existing default behavior.

Run `python -m csts_pilot.annotation_format_run --prepare-only` to publish native target artifacts and a deterministic 100-record audit sample. After auditing the metadata and profiling throughput, launch with `--audited-source-sha EXACT_CACHE_SHA --annotation-epochs COMMON_A_EPOCHS --rating-epochs COMMON_R_EPOCHS`. The exact cache SHA is mandatory, and the runner refuses to overwrite prior training state. An external `flock` must protect the controller and its process identity must be recorded. All three selected models are recorded in `format_results/selection.json` before evaluation inputs are published. Each arm then receives the same 32 accepted development passage-condition examples for deterministic generation; this is a development diagnostic, rather than a new holdout.

Use native VIPER stages for the three derived annotation artifacts, six training stages, model selection records and evaluation. Freeze all three selected rating checkpoints before evaluating the shared 2,620-comparison follow-up benchmark. Report Spearman, MSE and within-pair condition ordering, with paired source-group uncertainty. This previously examined benchmark is not a fresh confirmatory holdout.

Collect a small common development generation sample from each selected model. Report generated answers with original passages, cached fields and expected targets for independent review. Format-specific exact match measures teacher agreement; cross-format CE values are not comparable quality scores. Expand to additional seeds or richer annotations only after reviewing this screen.

## Timing and closeout

Allow approximately 1–2 hours after GPU capacity is obtained, assuming reusable cache and a reproduced environment. This includes preparation, the initial audit, approximately 30 GPU minutes, evaluation and reporting; extended independent review can increase elapsed time. Publish verified results and retrieval instructions, then stop the GPU VM after confirming no other GPU work is active. Do not create duplicate jobs.
