# Revised evidence-readout implementation review

Review scope: author self-review of the new full-width readout, symmetric comparator, writing-retention audit, native stages/controller, fixtures, pinned configuration, interventions and methods. This is not an independent external review, and it does not establish scientific efficacy.

## Design changes prompted by the full-bank results

Use the final full-bank proposition checkpoint rather than the earlier ratings parent and all 11,909 captured training identities rather than the 2,496-input pilot. Replace the three-arm proposal with B/C readouts followed by frozen-readout D/E comparison fitting. Recompute both final parent references on C-STS version 1.1. Audit writing before/after the final ratings phase using the same 121 existing writing-validation references and fixed 32-generation sample.

The methods distinguish the exact cosine contrast C−B, the fixed-representation comparison contrasts D−B/E−C, and E−D's inclusion of separately fitted comparison weights. The new comparator starts at cosine and preserves all 4,096 coordinates. This is a limited symmetric coordinate comparator, not a test of all possible semantic comparison functions.

## Correctness review and resolved findings

| Finding | Resolution |
|---|---|
| Updating readouts while fitting D/E would confound the comparison question | Select B/C first, clear old gradients, freeze parameters, detach vectors and verify unchanged readout hashes/no new gradients after comparison fitting. |
| A fresh randomly initialized comparator could destroy a useful score before training | Zero-initialize a symmetric residual so epoch zero equals cosine exactly; retain epoch zero for validation selection. |
| A learned comparison could introduce order-dependent sentence scoring | Use only absolute coordinate differences and coordinate products, alongside cosine; verify swap invariance before and after an optimizer update. |
| Historical breakthrough scores used 2,430 test rows while the approved revision has 2,431 | Re-extract A/R on current pinned inputs and keep historical scores as motivation only. |
| Earlier partial-capture fidelity could be mistaken for final-model factual accuracy | Add pre/post retention CE and deterministic generated probes. Explicitly distinguish exact reference agreement from factual correctness and existing validation from fresh evaluation. |
| Legacy parameter restoration only operates on parameters marked trainable | Temporarily identify the saved LoRA parameters for restoration, then disable all gradients before retention inference; compare adapter bytes before/after. |
| Missing teacher records or ambiguous quotations could become false negatives | Bind canonical training identities; apply evidence loss only to aligned answered or explicit not-specified records, with all rating rows retained. |
| Null softmax near one can cause unstable content normalization | Pool with a separate source-only softmax. Null never gates scoring or row inclusion. |
| Null-only evidence gradients could distort the shared-gradient diagnostic | Measure loss alignment on query/key weights only; diagnostic gradients do not enter optimizer updates. |
| Multiple native cache/model inputs could share a materialization path | Use a unique stored-source binding per cache and seed model. |
| Native EVAL requires stored canonical test/split inputs, an eval ID and objective | Publish test and holdout first, bind canonical model/test plus stored holdout, and declare a stateless C−B report metric with explicit artifact dependency. |
| Native validation metrics may describe terminal rather than selected weights | Replay selected four-cell predictions and publish an explicit final reporting step after both fitting phases. |
| Colour and appearance could be counted as separate corroborating signals | Export family membership IDs and describe overlap explicitly. Same-pair diagnostics group by exact unordered sentence text rather than broad source group. |
| Repeated or uncertain attempts could silently rerun a favorable subset | Preserve native records, selected/terminal states and failures; reject automatic replay of ambiguous attempts and source/input substitutions. |

## Verification

| Check | Result |
|---|---|
| New readout/comparator/retention tests plus inherited attention and preparation suites | 62 tests passed; 10 subtests passed |
| Ruff lint and formatting, all six new Python files | Passed |
| Pyrefly with the actual Python 3.13 environment, four production modules and native driver | Zero errors |
| Pinned full-bank/checkpoint/tokenizer preflight | Passed: all 11,909 canonical records; all three checkpoints rank 32, width 4,096, 288 adapter tensors |
| Literal quotation alignment before backbone inference | 12,102 sentence occurrences: 11,267 answered, 806 explicit null, 28 ambiguous-status skips and one repeated-quotation skip; no rating rows removed |
| Native CPU transport, complete three-seed four-cell fitting and final EVAL | Passed all nine stages, including separate objective worker |

Numerical checks cover differentiable readout gradients and exact padding exclusion; finite source normalization at near-unit null probability; teacher-status and quotation handling; selected-checkpoint replay and independent snapshots; identical trajectories when evidence targets are absent; comparator symmetry and exact cosine initialization; fixed readout hashes through comparator fitting; all five paired bootstrap contrasts and overlapping family membership; exact-pair condition diagnostics with half-credit ties; and restoring two adapters while freezing every parameter. Queue fixtures reject source changes and wait for an occupied GPU lease without starting computation.

The CPU native fixture uses random 5D states and does not load Qwen or use the GPU. The preflight loads tokenizer/checkpoint metadata and verifies source alignment, but does not run the backbone. These checks are implementation evidence, not empirical support for the working hypothesis.


## Original native receipt and source identity

The original CPU check passed all nine native stages, including held-out EVAL and the separate objective metric worker. It replayed all four cells for seeds 7/8/9, both parent reference bindings and all five contrasts. Fixture values describe the transport check.

| Stage | Native run ID | Result |
|---|---|---|
| publish_training | `01M5ZN532GMDTWAZHBB1AWWBPG` | succeeded |
| publish_validation | `01M5ZN5WY8CHQAWSG02R7T5DPW` | succeeded |
| fit_7 | `01M5ZN6PWGRMAN4CDYF949GM2N` | succeeded |
| fit_8 | `01M5ZN7VCNGKPF4JR9DS7WKEA1` | succeeded |
| fit_9 | `01M5ZN8WC9178SPY38XZHC3BQM` | succeeded |
| publish_test | `01M5ZN9X0QJ0WHVFT6YYYBVMYS` | succeeded |
| publish_interventions | `01M5ZNAP9KSVGY2QGF84JH24E9` | succeeded |
| publish_evaluation | `01M5ZNBF8A74JZ0J553D8M1F5H` | succeeded |
| evaluate | `01M5ZNC11QSF9GEA2B1TJ65RCJ` | succeeded |

Receipt: `qwen_evidence_results/readout_native_smoke_c11631b6/receipt.json` in the isolated JEP checkout. Fixture source was local preview `776baee5a6dfbe058efaf6f1abdd3fef9dadc8f9`. The hashes below identify the six files in that preview and published implementation commit `0f57e244f897dc8fcc8d321ea4b7cb10f571e324`. The A100 reporting update has its own validation record below.

| File | SHA-256 |
|---|---|
| `csts_pilot/evidence_readout.py` | `45b5d2117de7637753710898a92d9c16b2344385d4553286b4f6843ac7126f45` |
| `csts_pilot/evidence_readout_stages.py` | `36774d9a5099d16aeffe8f0ef4985f8bc2df798f60d9f8a6823c9024d419c707` |
| `csts_pilot/evidence_readout_retention.py` | `a9dd86b94a8abee8e8a3e8840c45267f23f9fe022ce698a57ecf2725fb3fb21f` |
| `csts_pilot/evidence_readout_run.py` | `bcf51155f6b76d31c0cdb49f72f9910f676cec100c40ecf67bf579b960e4bf77` |
| `scripts/check_evidence_readout_native.py` | `170c1930c9b68a48c3a8b84169dfd46ec2800f03587ba6c65f3c4dea3a8bc6cf` |
| `tests/test_csts_evidence_readout.py` | `258fbfaab2339928831ef875d07b691a54be91664b02935f72dc7e52836c92a9` |

The writing-probe preflight also verified all 121 targets against validation identities and exclusion from training. The longest target uses 23 tokens including EOD, below the fixed ceiling of 64. Real-Qwen writing inference remains part of the unstarted scientific run.

Reproduce the completed code checks in the installed experiment environment:

```bash
python -m pytest -q tests/test_csts_evidence_readout.py tests/test_csts_evidence_attention.py tests/test_csts_proposition_pretraining.py
ruff check csts_pilot/evidence_readout*.py tests/test_csts_evidence_readout.py scripts/check_evidence_readout_native.py
ruff format --check csts_pilot/evidence_readout*.py tests/test_csts_evidence_readout.py scripts/check_evidence_readout_native.py
pyrefly check --python-interpreter-path /home/machina/jep-format-env/bin/python csts_pilot/evidence_readout.py csts_pilot/evidence_readout_stages.py csts_pilot/evidence_readout_run.py csts_pilot/evidence_readout_retention.py scripts/check_evidence_readout_native.py
CUDA_VISIBLE_DEVICES="" python -m scripts.check_evidence_readout_native
```

## Limits and execution status

Three head seeds condition on one backbone seed and one teacher policy. The benchmark has already informed project decisions. Bootstrap intervals omit selection and project-wide search uncertainty. Attention agreement is not causal faithfulness, null probability is uncalibrated/length-sensitive, family subsets overlap, and six synthetic cases do not establish generality. The same validation set is used in two fitting phases. The restricted comparator cannot rule out richer cross-coordinate or token-level comparison on a negative result.

Scientific execution follows the A100 launch checks below.

## A100 execution and Markdown reporting update

The configured device is `NVIDIA A100-SXM4-80GB`, verified through the existing Colab session. The runtime uses Python 3.13.16, Torch 2.14.0, Transformers 5.20.2 and PEFT 0.21.2. The controller checks the exact configured device and active compute processes, then holds the shared GPU lease through execution.

Each native stage receives the attempt's absolute `progress.md` path in its recorded configuration. Workers append aggregate measurements under a process shared file lock. The report includes writing retention, extraction counts, separate B/C and D/E validation measurements, final test scores for every seed and all five planned differences. The native CPU fixture supplies a real report path to exercise this cross process stream.

Validation on the Colab runtime: 66 tests passed across the readout, attention and proposition preparation suites; Ruff lint and formatting passed for the five modified Python files; Pyrefly reported zero errors in the four modified production modules. Tests cover A100 device identity, occupied GPU handling, validation phase labels and final Markdown metrics. Training uses the methods document's fixed objectives, inputs, seeds and checkpoint selection rule.

The current native CPU check passed all nine stages from source `f59d2f8c5c64b96940a624a56d385330cf6a11ca`, including the shared Markdown path and the separate evaluation metric worker. Its receipt is `qwen_evidence_results/readout_native_smoke_ad5e6daf/receipt.json` in the Colab checkout.

The active scientific attempt is `evidence_readout_a100_20261028_r1`. Its predecessor ended during retention input preparation at a linked vocabulary head. The active attempt uses a regular copy with the same pinned hash. The earlier three publication records and failure log are preserved in `relaunch-reconciliation.json` beside the checkout. All split files and three model checkpoints match their fixed hashes.

The [live Markdown report](../training_outputs/csts_evidence_readout_20261028/progress.md) receives worker measurements throughout execution. The Mac publisher refreshes the GitHub file every five minutes and publishes the final result immediately.

## Review after execution

All 14 scientific stages completed. The [diagnosis](../training_outputs/csts_evidence_readout_20261028/diagnosis.md) records attention saturation, seed dependent token positions, the effect of step size and fixed pooling controls. The original scientific outcomes remain in the results report.

The new scripts operate on retained native artifacts. The fitting probe uses training and validation, one seed and one epoch at each of three declared rates. Its original rate reproduces the archived epoch one scores for B and C exactly. Each probe setting starts from identical weights and batch order. Its output retains every setting, intermediate measurements and terminal parameters with optimizer states. The probe acquires the shared GPU lock. Selected scientific checkpoints retain their original paths and bytes.

The review identified a missing control in the original design: direct comparison of the final summary with simple sentence token pooling and teacher quotation pooling. These checks now expose the representation change alongside attention instability. The proposed follow up retains A's score, includes a learned comparison on A itself and makes initialization eligible for validation selection.

Validation after adding diagnostics: 69 tests passed across four relevant suites. Ruff lint and formatting passed for the two scripts and their tests. Three new tests verify position statistics with variable sentence lengths, the distinction between matching positions and matching vectors under edits, and quotation pooling over full coordinate values.

The diagnostic scripts report aggregate measurements. Their JSON contains input hashes, numerical summaries and the six fixed case names. Source sentences and individual natural data predictions remain in the existing runtime. Conclusions about gradients refer to an explicitly fixed batch, teacher agreement refers to training inputs and the step size probe concerns one head seed. Further fitting and test evaluation are a separate proposed experiment.
