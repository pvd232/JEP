# Review record: expert claim multiple-prototype pilot

Reviewed base: `065951a9038d1f212afb95408632c62cc9402160` (the audio codebook branch). Scope: seven implementation/configuration/plan/test paths below. This review record is excluded from the scoped hash list. No code or configuration changed after the reviewed hashes were frozen.

An independent agent (`/root/review_multiple`) read every scoped changed line, inspected native input/output and metric contracts, ran the CPU fixtures, Ruff and Pyrefly independently, and approved this snapshot for a draft PR with no open code findings. The parent agent also read the new EVAL/controller and had no additional findings. This is code review for a proposed experiment, not validation of scientific efficacy.

| Path | SHA256 |
|---|---|
| `.gitignore` | `168f01f84560f5c944bb2cddf48584f6605ffd0a8087beefcb3578a64a8211ca` |
| `csts_pilot/multiple_codebook.py` | `1fe834194924aaaae7eae08381536a4e24fd75d803afde55d5362e385c38ad1d` |
| `csts_pilot/multiple_codebook_run.py` | `56a9dc0043512ace3b13adda5d599f4f1f9725c5294e5f86e5184d6b4760f0f5` |
| `csts_pilot/multiple_codebook_analysis.py` | `bf710a27abcb72298738218f87df397b8b54393008de947500f6bda0f9e7e61f` |
| `configs/csts-multiple-codebook.json` | `0c1b934a9989de2581d266020baaa13d8f694d212fe50eabb9dc896afacfc260` |
| `plans/csts-multiple-codebook.md` | `252615e2dbe40cb884bf2052348190ba144f1b50771d78595bbbaa23021511c7` |
| `tests/test_csts_multiple_codebook.py` | `a6fcecf64b0b8b3adaf8783342d49a100933095d9ecfbf9d48564dea405d9f52` |

## Findings and repairs

1. The draft terminal `state_dict()` referenced live model tensors. Restoring an earlier selected checkpoint then replaced the purported terminal weights while preserving terminal optimizer steps. Repair: clone terminal weights before restoring selection and retain the per-fit torch RNG state. A regression forces epoch zero to win after nonzero optimizer updates and checks that terminal weights differ and do not alias selected weights.
2. Passage OR labels cannot establish whole-passage coding when the supplied claim inventory may be incomplete. Repair: report `passage_or_scope: supplied_claims_only` and state the requirement for expert certification of an exhaustive inventory before interpreting full-passage metrics. Unknown included claim labels remain unknown; a passage negative requires every included claim to be explicitly negative.
3. The first draft only reported TRAIN's selected metrics. Repair: a native development-data publisher and independent EVAL stage bind canonical `model`, `test` and `holdout` names to sealed producers, revalidate exact input/bundle pins and code/claim alignment, restore selected weights, reproduce probabilities and metrics, and export per-seed candidate-minus-control macro-F1 and their mean. The primary native metric independently recomputes confusion counts from sealed prediction artifacts; there is no EVAL metric recorder.
4. Pre-batch time checks permitted the final validation or selected-prediction replay to overrun a fit budget. Repair: check the deadline after both operations; regressions force overruns at each point and require failure.
5. `read_source()` reports the committed Git source even when experiment modules are untracked or modified. Repair: explicit execution rejects a dirty tracked/untracked checkout before creating an attempt or calling native execution; ignored immutable data/output paths remain usable. A regression verifies failure before a launch.

## Checks and limits

The supplied derived CPU fixture interpreter was:
`/Users/machina/.codex/.chatgpt-projects/g-p-6ad6fb9258ac8191b4baa874735994e2/work/csts-codebook-test-env-20261026/bin/python`.
It includes torch 2.14.0, scipy 1.18.1, pydantic 2.13.5, the local editable viper-provenance 0.1.2, peft 0.21.2, transformers 5.19.0 and accelerate 1.15.0. This is not a claim of validation in the pinned remote CUDA environment.

Commands from the reviewed checkout (set `PY` to that interpreter and `VIPER_VENV` to `/Users/machina/Developer/ChatGPT/viper/.venv`):

```sh
"$PY" -m pytest -q tests/test_csts_multiple_codebook.py tests/test_csts_codebook.py
"$VIPER_VENV/bin/ruff" check csts_pilot/multiple_codebook.py csts_pilot/multiple_codebook_run.py csts_pilot/multiple_codebook_analysis.py tests/test_csts_multiple_codebook.py
"$VIPER_VENV/bin/pyrefly" check --python-interpreter-path "$PY" --ignore-missing-imports='*' csts_pilot/multiple_codebook.py csts_pilot/multiple_codebook_run.py csts_pilot/multiple_codebook_analysis.py tests/test_csts_multiple_codebook.py
```

Results: **26 passed** (13 new fixture cases plus 13 inherited audio codebook cases), Ruff clean, Pyrefly zero errors. The independent reviewer repeated these checks successfully. Coverage includes unknown-label zero gradients, exact pooling/parameter matching, train-only initialization, support/leakage/model/cache failure cases, paired order hashes, selected replay, terminal-state preservation, native resume serialization, independent development artifact recomputation, canonical EVAL producer roles, tampered replay rejection, preflight non-execution, dirty-source rejection and deadline failures. A mocked native TRAIN plan construction also passed without executing a native stage. Full native end-to-end execution has not been run.

No actual expert JEP annotations, frozen claim-feature inputs, expert credentials, adjudication records or complete claim inventory were supplied or verified. Synthetic fixtures explicitly identify their artificial provenance. No full study, encoder inference, paid training/generation, benchmark test, remote pinned runtime or performance/significance claim has been executed or established. The reviewed code requires the real pinned expert inputs and explicit execution opt-in. Development selection and replay use the same development cohort and cannot establish fresh-test performance. Source-group independence and annotation quality require human review before execution.
