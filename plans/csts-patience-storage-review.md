# First-pass review: patience and background storage

Base: `c46faf0efaa399399149223f1d9da91d16f212e4`. This review covers the prospective stopping rule, native storage orchestration, final report handoff and their focused tests. The completed experiment artifacts retain their original bytes. VIPER core and the installed environments are unchanged. The collaborative walkthrough and experiment execution remain pending.

The implementer inspected the complete scoped diff and its callers. The stopping counter must count exactly five unsuccessful validation checks, retain the required prefix, keep the best checkpoint separate from terminal weights, and record actual updates. Equal initialization and schedule horizons remain required; adaptive stopping is explicitly distinguished from an equal realized update budget.

Publication must commit its immutable request before launch, preserve it through a crash, serialize cloud writers, permit enqueue while a cloud request blocks, and mark publication complete only after native promotion returns. Waiting publisher processes defer the VIPER import until they own the worker lock. Failed or interrupted publication has no model-execution path. The final CPU report waits for study publication receipts and reads its promoted graph back from GCS.

First-pass findings repaired before publication:

- The adaptive verifier initially weakened the scheduler-horizon guard. It now checks the maximum-epoch horizon, actual update counts, epoch/step counters, common pair order and a replay of each stopping rule.
- Switching the workspace to local storage left the report publisher expecting a GCS snapshot in its local attempt. It now explicitly promotes the report and follows the cloud run and successful attempt before restoring the report artifact.
- Starting a publisher per enqueue could leave several heavyweight VIPER imports waiting on the same lock. The queue module now starts with the standard library and imports VIPER only inside the owning worker's promotion call.

Validation: 40 focused CPU tests passed in 4.62 seconds. Ruff passed with `E,F,I` selected and the repository's existing long lines excluded through `--ignore E501`. Pyrefly reported zero errors using the existing task interpreter, pinned VIPER source and existing report-environment package path. `git diff --check` passed. The exact test invocation from the repository was:

```bash
PYTHONPATH=../csts-tranche1-support/src \
  /Users/machina/.codex/.chatgpt-projects/g-p-6ad6fb9258ac8191b4baa874735994e2/tmp/jep-diagnostics/.venv/bin/python \
  -m pytest -q tests/test_csts_convergence.py tests/test_csts_early_stopping.py \
  tests/test_csts_background_storage.py tests/test_csts_convergence_report.py \
  tests/test_csts_plan.py
```

No unresolved blocking defect was found in this first-pass scope. These tests use controlled cloud collaborators and synthetic CPU model fixtures. Live-cloud latency, a complete live report roundtrip and moving an uploader to another host remain outside this validation. There is no claim of a storage speedup measurement or a stationary training minimum. See the [method and timing definitions](csts-patience-storage.md).
