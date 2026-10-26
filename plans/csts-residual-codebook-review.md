# Residual codebook review

Base: de9a32dc4ff93f0e31253eeca470d145c3be3411. Verdict: Approve the exact
implementation hashes below. User authorized implementation and execution.

Reuse decision: retain original objective, prototype diagnostics, cache loaders,
native TRAIN/EVAL and execution controller. Add a full-width residual model and
paired fitter because identity initialization and shared exposure are required.
Existing experiments keep their behavior. No abstraction registry is added.

Root inspected the complete scoped change and reused callees. Independent
residual_tests_review inspected the core, native replay and controller;
residual_native_review inspected all EVAL/controller/config/plan additions.
Resolved findings: control centres now fit selected TRAIN representations;
constant group predictions remain valid; boundary ties use exact fractional
coverage. No remaining blocking findings.

Validation: 33 new/inherited tests passed; Ruff check and format passed on all
five scoped Python files; Pyrefly default reported zero errors on all four
implementation files (one inherited missing-stubs warning). Observers cover
4096D identity, first gradient/update, matched batches/exposure, cloned states,
shared patience, baseline refusal, gradient measurements, tied scores and
independent native EVAL/metric replay.

The owner cache independently reproduced baseline Spearman 0.7825753746534037
with 4096 coordinates before launch. Full-data training outcomes are pending.

| File | SHA-256 |
| --- | --- |
| `.gitignore` | `9b0a7dad848e39ef4e1660b617bafd47a657526f97aecb90589855e87b4142b0` |
| `csts_pilot/codebook.py` | `8874da61b207e48954c922403837d4b79fdc9ace8752393f16ce1d6f7169ecef` |
| `csts_pilot/iterative_codebook_run.py` | `c8d24fb4ea4d5ac424f129ee02f37adfa27ba8149ecd6237792dfc2007d1ca1d` |
| `csts_pilot/residual_codebook.py` | `219d8e24bc6269a1837f86a320af4955194c6d9adc19879728a45b42d0556169` |
| `csts_pilot/residual_codebook_analysis.py` | `09d6876c200195e188f54af2c3681ec47b041004538d7b435bc148625f3a609d` |
| `configs/csts-residual-codebook.json` | `baf24977f9983feecd3961b7e99dc4a2bd072d512784f4311d7f1fc121b79531` |
| `plans/csts-residual-codebook.md` | `bbe135e120ca61cf8279cd37d6f5db22ea978ac7191f150e2cb44bff721d1048` |
| `tests/test_csts_residual_codebook.py` | `bc59dbe4d82f3a6c3c1c8b0209dbc2840033259b589a096cf20f8aae8949e01a` |
