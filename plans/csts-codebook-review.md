# Prototype-screen implementation review

Base: `d0a3984c88962a088af153736f914cc31a0c294b`. Scope: the three new `csts_pilot/codebook*` modules, the new focused test module and configuration, the method document, and the two new ignored runtime directories. Existing experiment implementations are unchanged.

This is an author review, with focused executable counterexamples. No independent or multi-agent review is claimed.

## Invariants and decisions

- Native features identify the selected frozen encoder, exact source extraction, source row bytes, and every question/passage occurrence. Compaction preserves occurrence multiplicity and normalizes the native state without another backbone call.
- Prototype estimation uses training vectors. All development scores are explicitly labeled selected-validation diagnostics. Source-group and canonical-caption overlap is rejected. The command accepts only training and development manifests.
- The paired arms share projection and dictionary initialization and all overlapping epoch batch orders. Continuous rating MSE is identical in both arms. The extra code losses are confined to the prototype arm. Checkpoint selection uses the same strict-improvement patience-five rule.
- The original VQ straight-through estimator is an intentionally biased gradient approximation. Its task term updates the projection; dictionary regression updates selected normalized prototypes. The tests establish finite nonzero gradients to both parameter sets and absence of dictionary force in the control.
- The selected state is cloned. The control's post-hoc dictionary fit does not change its selected projection. Replay checks exact validation metrics in the same one-thread CPU runtime. Resume files preserve terminal optimizer, parameters and RNG state independently of the selected checkpoint.
- Code occupancy, effective size, quantization error and low-rating collisions remain visible even when a dictionary collapses. Numeric prototypes and model-produced examples carry no expert semantic labels.
- Native BUILD/TRAIN/EVAL, existing loaders, metric verification and background publication own experiment provenance. The controller preserves an existing attempt and does not relaunch it automatically. New stages request CPU only. Three fixed seed pairs are aggregated as a mean of paired Spearman differences, not a correlation of averaged predictions.

The existing general projection fitter owns a rating-only loss. Reusing it unchanged would omit the dictionary objective. The added paired fitter owns this distinct objective and keeps the established experiments unaffected. A speculative test-evaluation path was removed from the new evaluator; the initial command has one validation-screen execution path.

## Finding and repair

P2, blocking before repair: `spherical_kmeans` initially computed initialization distances as `2 - 2 * dot(x, center)`. Float32 cancellation let identical normalized directions appear distinct. A constant-vector population passed the requested-distinct-code check and seeded repeated centers. The repair uses coordinate-wise squared differences and rejects a population with fewer distinct directions than requested. The constant-vector counterexample now raises, and repeated seeded fits return identical centers.

No unresolved implementation finding was identified within this screen's scope.

## Verification

Owner runtime: `/home/machina/jep-format-env/bin/python` via the check checkout's `.venv`. The complete observing boundary passed:

```text
python -m pytest -q tests/test_csts_codebook.py tests/test_csts_data.py tests/test_csts_diagnostics.py tests/test_csts_early_stopping.py
24 passed in 11.59s
```

After removing the unused future test path, the affected observer was rerun:

```text
python -m pytest -q tests/test_csts_codebook.py
12 passed in 6.72s
ruff check csts_pilot/codebook.py csts_pilot/codebook_analysis.py csts_pilot/codebook_run.py tests/test_csts_codebook.py
All checks passed!
pyrefly check --ignore-missing-imports csts_pilot/codebook.py csts_pilot/codebook_analysis.py csts_pilot/codebook_run.py tests/test_csts_codebook.py
0 errors
```

The focused end-to-end observer invokes the actual fitter, writes and reloads checkpoints/resume artifacts, runs the evaluator, and compares its statistic with the independent metric implementation. The real native-process boundary is exercised by the subsequent pilot rather than a duplicate deployment test. No dependency, shared fixture, established model, or established stage implementation changed, so the full repository suite is outside the traced impact boundary.

Reviewed implementation SHA-256 values:

| Path | SHA-256 |
|---|---|
| `csts_pilot/codebook.py` | `2b05ef366f861e02f6671e8a0b1b5aaa9e046515af7e83ab55688dd042d7184b` |
| `csts_pilot/codebook_analysis.py` | `b9c2bcdda37ab97532e0eb717bd18bc8f6f16f1990254e85e3f3c7e431c74cb9` |
| `csts_pilot/codebook_run.py` | `c534b49c0bbec10b566d7b237de626b22162bf46e59efd58582b9e5772b321b5` |
| `tests/test_csts_codebook.py` | `28d84c2470a7c69241481a401d95a873d978d80c9be4da19a4154f47c3f02147` |
| `configs/csts-codebook.json` | `d81d33fbe7af7d5fdf282dbf85da445192147cd91f3c6dc949b19ad745c9271c` |

Verdict: approve for the defined validation mechanism screen. Residual scientific uncertainty includes dictionary semantics, choice of one fixed auxiliary weight/code count, validation selection bias, and transfer to overlapping JEP claims. These limitations are measurements or future research questions, not implementation guarantees.

## Native binding repair

The initial attempt `98a103bf`, source `2cd66d61b3c1a08e58b1a91b911574612a447ed4`, completed both cache preparations, all six fits, and immutable development publication. Constructing EVAL then failed because VIPER requires reserved `model` and stored `test` inputs. The original attempt remains failed. The direct fitter/evaluator test did not observe this authoring contract.

The repair supplies those canonical inputs, binds the published development rows as the protocol's `test` dataset, checks their exact equality to the development cache, and checks that frozen model configuration hashes identify the same fitting caches. This protocol input name does not authorize or access the benchmark's actual test partition. `evaluation_inputs` owns this binding and has a focused observer for the names, producer and roles.

An explicit `--recover` option reuses exactly the four successful original stages. It rejects nonfailed parents, changed settings or manifest identities, other stage sets, failed reused runs, or changed frozen model bytes. It creates a new attempt rather than changing the original one. The fitter, loss, settings and codebook implementation remain byte-identical; no retraining is needed. Recovery records identify the original source, failure and summary SHA-256.

Verification after repair: `python -m pytest -q tests/test_csts_codebook.py` passed **13 tests in 9.00s**; Ruff passed and scoped Pyrefly reported **0 errors**. Review verdict: approve the binding repair and explicit evaluation recovery. The new native EVAL remains the observing boundary for the repaired authoring protocol.

The recovery preflight initially applied the fresh-screen 3 GiB free-space allowance after that screen had already sealed its caches. The evaluator reuses those caches and creates no raw-feature cache. The phase-specific recovery allowance now derives from twice the exact compact-cache/model byte total plus 512 MiB for source and outputs. The fresh-screen allowance is unchanged. No original cache, model or immutable store object is removed to make room. The actual recovery preflight and native evaluation observe this operational change; no model setting or numerical tolerance changes.

The explicit scoped type-check command is `pyrefly check --ignore-missing-imports="*" csts_pilot/codebook.py csts_pilot/codebook_analysis.py csts_pilot/codebook_run.py tests/test_csts_codebook.py`, which reports 0 errors. Supplying the optional missing-import pattern explicitly avoids accidentally treating a positional source path as that pattern. A bare single-file variant instead checked unrelated plotting modules and reported missing `matplotlib`; no plotting dependency is needed or installed for this screen.

The first native recovery computed every report/prediction but failed at an in-stage recorder lookup: artifact-recomputed metrics are executed by VIPER after the stage and have no `context.metrics` recorder. The manual record call was removed. The stage-level integration test now supplies the empty recorder map used by this native path and independently recomputes the statistic from its exported predictions. The failed native EVAL remains preserved; subsequent evaluation reuses the original frozen TRAIN and cache producers. No score, tolerance, checkpoint or training setting changes.

Because every primary checkpoint selected epoch zero, a separate retrospective CPU diagnostic inspects the already-trained terminal states. It preserves the primary selection and fits the control's terminal dictionary on training vectors only. Its script and encoder implementation hashes, original summary/model/resume/trace/cache hashes, and observed metrics are exported. This is post-selection development analysis, not new training or independent confirmation.

After the recorder repair, all **13 focused tests passed in 8.78s**, Ruff passed, and the explicit scoped Pyrefly check across the three experiment modules, terminal diagnostic and focused tests reported **0 errors**. The real terminal diagnostic completed successfully in the owner environment. The updated integration test's empty metric recorder map is the counterexample for the removed manual record call.
