# Tranche 3 strict code review

Review passed before experimental launch. Full repository tests: 123 passed. Pyrefly: zero errors in the three new modules. Ruff lint and formatting passed. The CUDA preflight showed finite, nonzero rating and evidence gradients through the shared FLAN encoder, normalized embeddings and 3.24 GB peak allocation. Exact file hashes and logs are retained in training_outputs/csts_tranche3_review.json.

The review checked source/validation separation, duplicate or unsupported teacher-cache records, effective within-condition shuffling, identical answer masks and first-phase comparison coverage, common initialization and batch permutations, fixed six-epoch exposure, terminal-weight transitions, the original 24-epoch rating schedule, constant lower-rate continuation and patience five, validation-only checkpoint selection, exact test bindings, independent native CPU metrics, resume guards and asynchronous publication.

The terminal checkpoint artifact was standardized to model.pt within its separate artifact container so the phase-B handoff resolves the correct file. The runner rejects unequal first-phase update counts or a transition from an earlier selected checkpoint. Shuffled and aligned supervision use the same 8273 training passage-condition keys and 4903 first-phase comparisons; validation keys never enter the permutation.

No critical or high-severity findings remain. The scientific scope is one seed on a previously examined benchmark, with teacher-checked evidence. Expert factuality, additional-seed variation and Spanish JEP transfer remain later work. FLAN-T5 is the original generative student; the stronger Qwen embedding run remains a separate reference.
