# Color diagnostic run

The frozen-model diagnostic is running on the existing JEP L4 VM.
GPU checks passed: cached decoding matched full-sequence decoding for the shared base and seed 7's final proposition model.
The supervisor resumes the timed sample, evaluates all 13 states, then computes the paired contrasts.

The probe contains 100 families, 400 captions and 520 caption-condition inputs.
All 12 adapter files passed their saved SHA-256 checks.
The caption screen compared the probe with 10,315 unique captions from the original frozen C-STS splits.
The configured exact and near-duplicate rules flagged zero matches.

**Preliminary labels.** One model author proposed the color labels.
The two-human review specified in the saved plan remains pending.
Results from this pass describe those proposed labels.

The run freezes the original input prefix, vocabulary head, normalized encoder embeddings, and 64-token greedy-decoding ceiling.
Analysis uses 10,000 paired family bootstrap draws and 99.1667% intervals for six contrasts.
Geometry interpretation requires 20 represented families in each seed's shared correct-readout set.

The native run directory is `/home/machina/jep-color-diagnostic-20261028`.
The supervisor writes `results/status.json`, `supervisor_status.json` and `analysis/report.md` there.
The report becomes available after all states finish.

The frozen definitions are in `diagnostic_protocol.json`, `probe.py` and `protocol_plan.md`.
The inference and analysis scripts retain hashes of their inputs and outputs.
