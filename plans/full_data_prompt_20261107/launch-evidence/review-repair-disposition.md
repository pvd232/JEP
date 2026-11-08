# Disposition of ten independent source-text reviews

The initial CLI shell review attempt failed because the host could not initialize its read-only bubblewrap network namespace. No sandbox permissions were relaxed. Ten subsequent independent authenticated Codex executions reviewed the same line-numbered source packet directly as text, without tools. All ten returned substantive scoped static assessments; raw provider receipts are retained separately.

Reviewed baseline: `8fdd0f690dbd46ffd3bfdee5331017aa10726f86`.

Correctness repairs:
- Bind staged train/validation SHA, counts, groups and normalized finite labels inside `fit_lora`, before model loading; do not trust only caller-side declarations.
- Bind actual checkpoint seed/trial and complete validated native selections into held-out capture. Matrix entries now require distinct actual native executions, exact model/trace/prediction generations, prompt hashes, cohort identity and verified selection.
- Reject a parent that actually stopped for validation patience even if the builder received an inconsistent eligible trace. Verify selected validation-prediction SHA and reconstruct patience.
- Restore constant-scheduler counter/state as well as optimizer and CPU/CUDA RNG state.
- Pin the complete statistical analysis object and source paths; require 40-character immutable source IDs at the approval gate.
- Reject NaN/infinite ratings explicitly.
- Remove the avoidable GPU token-count scalar synchronization using cached CPU sequence lengths. Retain the original numerical checks and training arithmetic.
- Fix native VIPER variant/experiment identifiers to the runtime's lowercase identifier grammar. Human trial labels remain A/B/C.

Counterexamples: 61 dependency-free tests, plus five real native PyTorch/VIPER tests on CPU and CUDA. The tiny dropout model's uninterrupted versus segmented continuation checks exact weights, AdamW moments, scheduler state, RNG and row order. These are not full-Qwen accuracy measurements.

Deferred, non-semantic performance work: persistent tokenization caching across native epochs, and aggregation of loss/norm telemetry. Those optimizations are not required to test the scientific question and will not be inserted asymmetrically or without numerical/RNG equivalence evidence.

Spot transport adaptation: the private task VMs comply with the project's no-external-IP constraint. Their direct Google Storage connectivity is unavailable. The existing authenticated IAP bridge performs export and independent cloud download/SHA verification. The GPU worker must receive an exact-generation ACK before advancing. Uploaded model/checkpoint artifacts contain no credentials. The persistent task disk retains the local native artifacts even if export fails. No IAM/network-policy bypass is attempted.

Execution scope: the new worker executes assigned full-data fits. It does not unlock test labels or choose a winning arm. The collector stops each task GPU after verified training collection, or failure; the original historical stopped VM/disk and Columbia CPU connector are excluded. The global fifteen-selection gate remains mandatory for subsequent held-out evaluation.

A final independent static pass must review the patched exact source, worker and exporter before scientific training. Runtime preflight must remain separately evidenced; static approval is not a GPU validation certificate.

Final-pass operational findings and repairs:
- Each worker now binds to an immutable GCP project/name/zone/instance ID and actual GPU UUID, plus a unique execution ID. A host-wide GPU lock excludes both worker labels from sharing one device. A different instance cannot reuse the assignment.
- Generation manifests and ACKs include instance and execution IDs. Cloud objects use create-only generation preconditions; existing objects are downloaded and must have identical SHA bytes before any ACK. Conflicting generations are rejected, never overwritten.
- The GPU worker reads the actual independently installed systemd shutdown timestamp and rejects missing, expired or mismatched deadline evidence before model execution. The collector reports stop failures truthfully with only the deadline it actually observed. Replacement instances are excluded from stop actions by immutable ID.
- The current 72 dependency-free checks include wrong host/project/GPU/lease, missing/expired deadlines, host-wide lock exclusion and corrupted publication ACK counterexamples. Native CPU/CUDA dropout resume tests remain separate.
