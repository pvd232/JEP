# C-STS extraction comparison

Status: prepared for review. This PR reports no new inference, fidelity scores or similarity results.

## Question and comparisons

Does an explicit evidence representation improve faithful extraction, and does the information survive the input contract used by a conditional-similarity model?

The study refreshes two separate baselines: direct GPT-6.1 similarity judgments and source-only GPT-6.1 propositions. Archived proposition-v1 outputs remain historical context and are excluded from new paired results.

| Arm | Model and output | Interpretation |
|---|---|---|
| `gpt_direct` | GPT-6.1 Sol, max; passage pair and condition to a 1–5 score | Refreshed direct-judgment baseline |
| `gpt_propositions` | Same GPT generator; one passage and condition to claims, quotations and support metadata | Refreshed proposition incumbent |
| `gpt_json` | Same generator; entity/fact JSON | Explicit decomposition and binding |
| `gpt_python` | Same generator; equivalent entity/fact schema as Python objects | Code-based schema expression |
| KnowCoder | Pinned native checkpoint and supported schema | Complete extraction-system comparison |
| GoLLIE | Pinned native checkpoint with annotation guidelines | Complete guideline-following-system comparison |

JSON versus Python holds semantic fields and instructions fixed. Propositions versus entity/fact outputs changes decomposition as well as representation. KnowCoder and GoLLIE also change weights and training, so their results cannot isolate code syntax. KnowCoder-X is deferred to a separate Spanish-transfer study.

## Data

Use audited `jep-csts-v1.1` from main commit `61a48b2fa580c7457155535bcfafde10426dab83`: training 6,051; validation 1,576; test 2,431. Preserve restored `evaluation_2450`.

| Split | Reconstructed export | SHA-256 |
|---|---|---|
| Training | `train.json` | `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4` |
| Validation | `validation.json` | `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff` |
| Test | `test.json` | `d6b40b7b891ed147befb30801c2f85a8787775adebdd98d134157cbb2a6e9f76` |

Reconstruction checks source and package hashes, adjudication overrides, row counts, export hashes and caption separation. Export rows retain `row_id`, both sentences, condition, audited rating, normalized target, `pair_id` and connected-source-component `group_id`.

Select 120 validation comparison rows deterministically, without conditioning on ratings or model errors. Preserve the selection algorithm, seed, row identities, component IDs and input hashes. Derive unique source/condition extraction inputs and paired direct-scoring inputs from this one sample. Report its represented-component count. Sampling rows can retain a subset of a component; use retained component identities during uncertainty estimation.

The old 108-source pilot is a separate diagnostic cohort. Its color slice and evidence-helped controls do not estimate representative performance. Keep its counts outside the new sample denominator.

Validation and test have previously been examined in this project. Neither is a fresh blind holdout. Freeze this study before candidate generation. Full-test preparation requires the identical validation protocol lock and all 2,431 audited test pairs. Later prompt changes create a new study identity and invalidate reuse of that lock.

## Generation contract

Extraction receives only an opaque source ID, its passage and condition. Companion passages, ratings, reference answers, cohort names and model errors are excluded. Direct scoring receives both passages and the condition, with labels joined offline. Passage contents are data. GPT tool activity invalidates a request.

All GPT arms use `gpt-6.1-sol` through the signed-in Codex CLI at `max` reasoning. Archived proposition capture used `high`; this is a refreshed matched max-reasoning baseline. The CLI exposes a model alias rather than an immutable checkpoint. Record the alias, any returned identity, executable version, exact invocation, prompt bytes, timestamps, elapsed time and raw output. Usage remains available in the retained raw Codex event log. Do not claim an unavailable snapshot.

The three extraction formats share an outer response envelope, isolation policy, model alias, max reasoning and 1,200-second request timeout. No verified provider output-token cap is exposed by Codex, so equal GPT token budgets cannot be claimed. A common 65,536-byte payload validation bound rejects oversized responses after capture. This transport differs from historical proposition capture and limits comparison with that archive. JSON/Python receive equivalent semantic guidance and examples. Their prompt lengths differ and remain part of the schema-expression comparison. Native systems use a separate 1,024-token generation cap; their budgets are not matched to GPT.

KnowCoder and GoLLIE require verified checkpoint repositories and immutable revisions, tokenizer identity, native prompt templates, generation settings, software and hardware records. Missing identities block execution. Preserve source-only inputs and the intended policy in each native format. Prompt adaptation is part of the native-system comparison.

## Semantic policy

An answered output preserves all requested supported values, bindings, stated multiplicity, roles, negation and qualifications. A partial count remains answerable with unknown portions qualified; a bare plural supplies no exact count. Broad conditions cover all relevant entities, while role-qualified conditions restrict scope.

Allow explicit facts, elementary counting and direct high-confidence lexical normalization. Typical-color assumptions, unstated motives and absence inferred from nonmention are excluded from the primary policy. Any exploratory inference is labeled and scored separately. An exact quotation establishes provenance; semantic review still checks whether it supports the claim.

Use `answered`, `not_specified` and `ambiguous` consistently. Missing evidence differs from explicit negation. Distinct entities sharing a value retain separate identity or explicit quantity. Unknown values remain unknown.

JSON and Python encode equivalent fields. Python is parsed with an allowlisted AST data parser and never executed. Imports, arbitrary calls, attribute access, expressions and unsupported constructors are rejected. Quote failures, dangling or duplicate IDs and invalid statuses remain observable failures.

Preserve every attempt and error. The runner implements no retries: failed results remain failures, and an interrupted attempt requires a fresh run directory. Existing completed records may be skipped only when bound to the same frozen request. Report validity, coverage and operational failures on the declared denominator. Malformed outputs, refusals and native token-limit truncations remain failures.

## Review and evaluation

Seal source-only references before any extraction candidate is generated. Reviewers see source text and condition without arm names, model names, similarity ratings or improvement labels. Formats remain visible, so describe the procedure as masking arm names.

Review records require faithful, complete, scope_correct, binding_correct, multiplicity_correct, abstention_correct and inference_correct boolean judgments, plus rationale and reviewer_id. The supplied reviewer_id is a provenance field, not automatic proof of human authorship or independent expertise. Human adjudication and reviewer independence remain operator responsibilities. Structural validity and semantic acceptance are distinct. Label model-assisted judgments explicitly; the acceptance summary requires all criteria and structural validity.

Pair comparisons on identical sources. Report coverage and missingness first. Bootstrap connected source components together and report paired differences with intervals; a small point-count lead is insufficient to establish a winner. Treat multiple comparisons as exploratory.

The direct GPT refresh scores the selected validation pairs and, after locked preparation, all 2,431 test pairs. Apply the frozen 1–5 rubric and compute Spearman plus MSE on the 1–5 and normalized 0–1 scales. Require exact coverage and finite in-range scores before joining labels. This refreshed protocol uses independent per-item requests and the new explicit inference policy; historical direct scoring used batches and its earlier rubric, so the refresh is a new baseline rather than a byte-identical reproduction.

The common export preserves source identity, condition, status, reason and canonical evidence, together with capture_path and capture_sha256 for retained-output provenance. Preserve multiplicity and uncertainty through the canonical representation. Export requires complete structurally valid coverage; it does not certify semantic correctness.

This PR prepares extraction and export, with no Qwen training. Higher fidelity alone does not establish better similarity. A later downstream comparison must hold encoder weights, readout, training budget and source pairs fixed. Report full-cohort failure handling and accepted-output coverage, so dropping hard sources cannot masquerade as improved similarity. Any learned readout uses training data alone.

## Run

Reconstruct upstream inputs using the package's existing script:

```bash
python datasets/csts-jep-revision-v1-1/reconstruct.py --source /path/to/upstream-csvs --output /path/to/jep-csts-v1.1
```

Prepare the fixed sample and seal independently formed references before generation:

```bash
python -m csts_pilot.extraction_comparison prepare --config configs/csts-extraction-comparison.json --data-dir /path/to/jep-csts-v1.1 --output /path/to/extraction-validation
python -m csts_pilot.extraction_comparison seal-references --output /path/to/extraction-validation --references /path/to/source-only-references.json
```

Preparation freezes config, source and prompt fingerprints in `protocol.json`; there is no separate freeze command. The default `run` prints a dry-run plan. Add `--execute` to launch a configured arm. GPT capture supports `--workers` from 1 to 16, with isolated per-source requests; the default is 1. The operator setting is retained separately from the scientific protocol:

```bash
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm gpt_direct --cli /path/to/codex
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm gpt_propositions --cli /path/to/codex
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm gpt_json --cli /path/to/codex
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm gpt_python --cli /path/to/codex
```

Native arms require their pinned config and the recorded torch/transformers runtime. On the Colab A100, GoLLIE uses the stock Llama SDPA compatibility backend with its unchanged checkpoint tensors. The adapter validates all 291 learned tensor names and the legacy implementation's actual rotary base of 10000, overriding the inconsistent base of 1000000 in its configuration. Kernel and normalization rounding can differ from the original custom FlashAttention implementation. This is a checkpoint comparison with a recorded compatibility backend; exact numerical parity and reproduction of published scores are unverified. Their dry-run commands are:

```bash
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm knowcoder --device auto
python -m csts_pilot.extraction_comparison run --output /path/to/extraction-validation --arm gollie --device auto
```

GPT readiness does not establish native-model readiness. After generation, create review packets and complete human reviews:

```bash
python -m csts_pilot.extraction_comparison review-packet --output /path/to/extraction-validation
python -m csts_pilot.extraction_comparison summarize --output /path/to/extraction-validation --reviews /path/to/completed-reviews.json
python -m csts_pilot.extraction_comparison export --output /path/to/extraction-validation --arm gpt_json
```

Without `--reviews`, summarization reports operational counts rather than semantic fidelity. Each report is saved as a content-addressed `summary-HASH.json`, allowing operational and later reviewed reports to coexist. Prepare the full-test refresh only with the fixed protocol:

```bash
python -m csts_pilot.extraction_comparison prepare --config configs/csts-extraction-comparison.json --data-dir /path/to/jep-csts-v1.1 --output /path/to/extraction-test --split test --protocol-lock /path/to/extraction-validation/protocol.json
```

The same arm execution commands then operate on the test directory. Preserve complete coverage for direct scoring and source-only propositions. No inference has been launched as part of preparation.

## Research basis

[Code4Struct (ACL 2023)](https://aclanthology.org/2023.acl-long.202/) represents event structures as generated class objects and motivates explicit argument binding.

[KnowCoder (ACL 2024)](https://aclanthology.org/2024.acl-long.475/) combines Python schemas with schema-understanding and schema-following training. Prompt-only Python tests part of that design.

[GoLLIE (ICLR 2024)](https://arxiv.org/abs/2310.03668) trains models to follow annotation guidelines and motivates explicit scope, inference and abstention rules.

[Code4UIE](https://arxiv.org/abs/2311.02962) retrieves demonstrations for code-based extraction. Retrieval is deferred and would require training-only examples and a matched demonstration control.

[KnowCoder-X (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.748/) evaluates multilingual alignment, including Spanish NER. Spanish hearing-claim extraction remains a separate transfer hypothesis.
