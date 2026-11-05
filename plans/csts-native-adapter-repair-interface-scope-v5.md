# Task-aware native evidence adapter

This package compiles a source-independent task from a condition, renders native KnowCoder/GoLLIE tasks, parses literal output without executing it, and exports common evidence. No model runtime is imported by the compiler, normalizer or CLI. Existing legacy arms and original captures must remain available when integrating this package.

The current schemas are development proposals. Code tests do not establish model fidelity. Every production route remains unapproved; model gates and fresh evaluation belong to the outer frozen experiment. BASE and IE are separate pinned variants, not interchangeable aliases.

```sh
python3 -m csts_pilot.native_adapter.cli compile --condition 'color of animal'
python3 -m csts_pilot.native_adapter.cli descriptor --model-alias knowcoder_ie
python3 -m csts_pilot.native_adapter.cli normalize --input source_captures.json --output normalized.json
python3 -m csts_pilot.native_adapter.cli export --input normalized.json --output common_evidence.jsonl
python3 -m unittest discover -s tests -q
```

The same commands work under `csts_pilot.native_adapter.cli` if the package is integrated there. Inputs can be one record or a list. A normalizer record contains `source_id`, `passage`, `condition`, `model` (`knowcoder` or `gollie` grammar), and `raw_output`; optionally `profile`, `task_stage`, `count_stage`, `runtime_status`, and `external_protocol_sha256`. For a complete staged task, provide `stage_outputs` mapping every declared stage to its original raw output instead of `raw_output`. The CLI retains source projection and raw payload, rederives normalization before exporting, refuses to overwrite outputs, and retains runtime/parse/unsupported failures as rows with null evidence. It never invents model-execution verification. The outer runner must validate its frozen model/checkpoint, prompt, tokenizer, tensor-load and raw-capture receipt before treating an export as experimentally verified.

Use `compile_condition`, `native_prompt`, `bounded_input`, `verify_bound_input`, `normalize_native`, `normalize_stages`, `canonical_text`, `descriptor`, and `bind_runtime` as the public Python API. The production core has no `/tmp` or `/content` paths. Development artifact builders identify the original frozen exposed-source inventory explicitly; they are not runtime entrypoints.

`positive_anchor` renders only positive requested classes, with the canonical KnowCoder NER/RE instantiation instruction and required bases. `scoped_experimental` retains separately unapproved polarity variants. Composite description tasks require explicit `task_stage`; the parser accepts only that stage's constructors. The literal union of all individually schema-valid stage captures adds no claims, fills no omitted stages, and leaves semantic support/coverage unvalidated.

Counts remain disabled in `bounded_input`. The separately frozen finite count-stage packet is for reviewed exposed development canaries only. It tests mentions/quantity phrases, quantity bindings and identity as independent native tasks, never a broad generated reasoning graph. CPU count arithmetic has been reviewed only conditional on externally validated support, scope, coreference and completeness. The six proposed development cases assert conservative lower bounds or unknown, never exact scene totals.

A common entity has a local ID, semantic type, original source span with all candidate offsets, polarity, quantity and answer roles. Relation subjects/objects and event roles reference those IDs. A source-supported observed activity can remain context when a purpose, attention state, sweetness or persistent hobby is unstated: `requested_facet_status=not_specified` preserves the context graph. Canonical text marks context and does not turn it into a direct state/goal claim. Food-context relations do not assert ownership/eating; food amounts preserve original units without combining them.

Alternative condition readings carry separate `facet_statuses`; category evidence is not an answer about actual use. `candidate_grounding_status` and `ambiguity_origins` distinguish unresolved model bindings from condition interpretation. Offline exports retain `semantic_support_validated=false`, `route_production_approved=false`, and `external_protocol_verified=false`; a separate semantic/deployment gate is required.
