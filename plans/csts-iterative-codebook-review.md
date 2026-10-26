# Iterative codebook experiment code review

Review date: 26 October 2026. Base commit: `065951a9038d1f212afb95408632c62cc9402160`. Branch: `experiment/csts-iterative-codebook-20261026`.

The implementation owner and the independent `runtime_validation` agent reviewed the original implementation against the base. The independent reviewer read the code and method and reran its 23 CPU fixture tests. A later source-checkout guard and its regression were authored by `runtime_validation` and independently reviewed by the root agent against commit `cc99b05367435358d603fd26de2573678181004c`, including the final fixture marker and formatting changes. The followup author did not independently review their own change. The table below identifies the final scope after that followup. Final disposition: **no remaining actionable blockers in this snapshot**. This is approval of the draft experiment implementation for user review. Research execution remains pending user review.

## Exact reviewed scope

SHA-256 identifies the full final contents, including new files that are not represented by a tracked-file-only `git diff`. This review record is excluded from its own hash scope and receives a separate prose accuracy check.

| File | SHA-256 |
|---|---|
| `.gitignore` | `97a63d992d514d4f1bea16d9291c6f2c75ec1340f2aecb9e40af46fc950b8837` |
| `csts_pilot/iterative_codebook.py` | `aadb4eb0e11bfca96d5ac2a6e60dc111bd8770d9eb24e727a7479426722668dd` |
| `csts_pilot/iterative_codebook_analysis.py` | `d405976e290e8072092257a0aa0d9b13924f7b0586cf0bf8ab44cd365878728c` |
| `csts_pilot/iterative_codebook_run.py` | `0f1b63924a978f76e89ccf69d0a4d511f27d278317294ae32a9cde9f93168bfd` |
| `configs/csts-iterative-codebook.json` | `4742af0cc72dd38ff165e2da7c9b49ecc613d7028e49c0149085bb6dec678487` |
| `plans/csts-iterative-codebook.md` | `0b0304e93598378dca5d0726be502e57043a936f2b9b439e898668f8b6e6d499` |
| `tests/test_csts_iterative_codebook.py` | `9e84aafb3e778eea291d3e3180b2f6d07d33ccdebb579abfd81de4c83d1c952b` |

## Findings and verified repairs

| Severity | Finding and counterexample | Repair and observer |
|---|---|---|
| Medium | The first metric-step scheme was arm-major while execution was epoch-major, yielding steps such as 1, 50, 2. | Use seed/epoch/arm ordering. The native-stage fixture requires every metric's recorded steps to be unique and increasing. |
| Medium | The initial controller had TRAIN only and exposed selected metrics without the declared paired aggregate or independent native EVAL. | Add canonical native development EVAL using the existing published development rows and `evaluation_inputs`. Independently replay sealed selected models, export predictions and report each seed gain, mean gain and sample standard deviation. The native artifact metric recomputes the mean from predictions. Tests construct the full native EVAL plan with reserved bindings, split inputs and artifact dependency and compare the metric against independently computed SciPy correlations. |
| Medium | Checking the deadline only before batches allowed final updates, validation or diagnostics to overrun and return success. | Start the pair timer before initialization, check after each epoch and before returning after diagnostics. A deterministic fake-clock fixture makes final diagnostics cross the deadline and requires failure. |
| Low | The first native output assertion treated `StageOutputs` iteration as names; iteration exposes name/value pairs containing unhashable output references. | Assert `configured.outputs.keys()`. The fixture now observes canonical `model`, `resume_state` and `trace` outputs without hashing reference objects. |
| Medium | `read_source()` reports committed HEAD even when local source is modified, staged or untracked. The controller could consume inputs and create an attempt from that unreviewed checkout before native source verification. | Reject a nonempty Git porcelain status before execution reads inputs or creates an attempt. Three real temporary-Git cases prove unchanged `read_source()` identity and refusal for modified, staged and untracked Python source. Ignored native results remain allowed; read-only draft preflight remains available. This followup was authored by `runtime_validation` and independently reviewed by the root agent. |

The reviewer also verified the train-only teacher call path, first-unique-key clustering and occurrence-label broadcast, terminal projection refresh, label-permutation handling, matched classifier/AdamW resets, identical masks/batches and exact pre-refresh states, shared patience five, epoch-zero eligibility, source-group isolation, selected-state cloning, cache/model byte gates, replay mismatch rejection, and treatment of rare/unused numeric codes. A constructed projection-change fixture changes the actual target partition; it does not merely observe a refresh function call.

## Validation performed

The derived local CPU fixture environment uses Torch 2.14.0, SciPy 1.18.1, Pydantic 2.13.5, Transformers 5.19.0, PEFT 0.21.2, Accelerate 1.15.0 and the locally installed VIPER development package. This is not evidence of execution in the pinned remote CUDA training runtime.

From the branch checkout, the original implementation owner and reviewer used the following commands. The followup author reran them after the source-checkout guard and regression were added:

```bash
PY=/Users/machina/.codex/.chatgpt-projects/g-p-6ad6fb9258ac8191b4baa874735994e2/work/csts-codebook-test-env-20261026/bin/python
TOOLS=/Users/machina/Developer/ChatGPT/viper/.venv/bin
"$PY" -m pytest -q tests/test_csts_iterative_codebook.py tests/test_csts_codebook.py
"$TOOLS/ruff" check csts_pilot/iterative_codebook.py csts_pilot/iterative_codebook_analysis.py csts_pilot/iterative_codebook_run.py tests/test_csts_iterative_codebook.py
"$TOOLS/ruff" format --check csts_pilot/iterative_codebook.py csts_pilot/iterative_codebook_analysis.py csts_pilot/iterative_codebook_run.py tests/test_csts_iterative_codebook.py
"$TOOLS/pyrefly" check --preset default --python-interpreter-path "$PY" --ignore-missing-imports='*' csts_pilot/iterative_codebook.py csts_pilot/iterative_codebook_analysis.py csts_pilot/iterative_codebook_run.py
```

Original results: **23 tests passed**, Ruff checks and formatting passed, Pyrefly reported zero errors. The independent reviewer reran those same new and original codebook suites: **23 passed**, with Ruff and Pyrefly also passing under the stated scope. Final followup results: **26 tests passed**, Ruff checks and formatting passed, and Pyrefly's default preset reported zero errors. Pyrefly's remaining warning concerns missing SciPy type stubs. The fixtures directly execute the native stage functions with synthetic caches, construct a native experiment/plan, and inspect isolated temporary Git repositories; they do not execute a sealed native research run.

## Scientific and execution limits

The method is a masked-feature self-supervised adaptation with training ratings. It provides no expert corrections, temporal speech task, claim ontology or JEP semantic validity evidence. All validation is unmasked; both arms share exposure and checkpoint-selection opportunities. The treatment includes repeated clustering overhead, so equal FLOPs are not claimed. Validation selects checkpoints and cannot establish fresh-test improvement.

No research experiment, full native launch, backbone inference, GPU job, paid generation or benchmark test evaluation ran for this PR. The controller still requires accessible prior immutable native artifacts in an owner runtime and user review before the proposed experiment launch. Existing experiment implementations are unchanged.
