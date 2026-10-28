# Native evidence adapter: current interface

The current package is byte-identical to the reviewed final core: [archive](../training_outputs/csts_native_know_refinement_v1_20261028.tar.gz) SHA-256 `5edcdc64aec6a4f3dbb83a8511da3f5b103024fe76ced9c2eff14763c38c082d`, seal SHA-256 `4f1e23dfe170051699cf93efeae2c5ed9220289a2791400117249f308199cbac`. Its 13 Python modules and 3 JSON assets are all byte-bound. Implementation review does not establish model quality.

```python
from csts_pilot.native_adapter.schema import compile_condition, bounded_input, verify_bound_input
plan = compile_condition(condition,
    contract_recipe="native_spatial_clause_food_recipe_v1")
# Go keeps the original fixed task-contract recipe.
go = bounded_input(plan, "gollie", passage, actual_go_token_count,
    profile="positive_anchor", max_new_tokens=512)
# Know uses the final model-specific refinement.
know = bounded_input(plan, "knowcoder", passage, actual_know_token_count,
    profile="positive_anchor", max_new_tokens=512,
    prompt_profile="native_know_palette_clause_refinement_v1")
verify_bound_input(know, plan, passage, actual_know_token_count)
```

All Go generation strings and Know NER/Color strings remain unchanged. Know spatial uses one fixed completed illustration of every unchanged predicate; action-description stages add one complete independent retrieval/origin/locative example. Selection depends only on model and condition-compiled task/schema/stage, never a source answer/output. No training/LoRA, external prompt append or force-nonempty instruction is added.

Know refined spatial has an explicit 4096 bound: actual maximum 2511 input + 512 reserve = 3023, supported by pinned IE config and author vLLM 4096. Other Know branches retain 2048; Go 16384. Baseline bounds/captures remain unchanged. Exact plans, profile/data choices, stages, prompt/target hashes, actual counts and every helper/data file are bound. The outer harness must also seal checkpoint/tokenizer/runtime/tensor loading/raw capture.

Default compile_condition(condition) retains legacy EE/contracts. normalize_native validates one stage; normalize_stages requires the complete exact stage set before a literal union. Composite plans may require three stages. Entity IDs remain local mention bindings; relations reference them. Repeated exact spans retain every candidate without selecting the first.

Spatial qualifiers come from model-emitted predicate constructors. Full-source cue spans allow fronted syntax, but are necessary lexical consistency only; cue attachment and semantic entailment remain unvalidated. No missing qualifier is reconstructed. ActionDescription records actor + verbatim predicate/clause and explicitly does not resolve a full EE frame. Context keeps answer_role=context and cannot create an unstated goal/state/hobby. Alternative readings keep separate facet_statuses; candidate ambiguity is not asserted source ambiguity.

Symbolic aggregate-count dispatch remains blocked. Quote-only CountEvidence failures remain separate archived diagnostics, not a numeric-total substitute or supported diagnostic route. Unsupported/failed cases stay in the fixed denominator with no fallback calls. Parse validity/quoting do not certify scope, sufficiency or support.

```sh
python3 -m csts_pilot.native_adapter.cli compile --condition 'location of person' --contract-recipe native_spatial_clause_food_recipe_v1
python3 -m csts_pilot.native_adapter.cli descriptor --model-alias knowcoder_ie
python3 -m csts_pilot.native_adapter.cli normalize --input raw_captures.json --output normalized.json
python3 -m csts_pilot.native_adapter.cli export --input normalized.json --output common_evidence.jsonl
```

Offline input has source_id/passage/condition/model, raw_output or complete stage_outputs, profile, contract_recipe and optional runtime/stage/protocol fields. The CLI rederives normalization before export, preserves failure rows, refuses overwrites and retains unvalidated semantic/production/external-proof flags. It never loads a model. Inference/replay uses the separately frozen outer harness.

The repository retains 108 adapter tests (reviewed 105 plus three previous whitespace regressions); all 177 combined tests pass. Real CLI compile/normalize/export checks also pass and retain an invalid row. Historical run identities remain bound to their own snapshots.

History: [scope-v5 interface](csts-native-adapter-repair-interface-scope-v5.md), [scope-v5 design](csts-native-adapter-repair-design-scope-v5.md), [scope-v5 archive](../training_outputs/csts_native_adapter_scope_v5_20261028.tar.gz), [final source/packet archive](../training_outputs/csts_native_know_refinement_v1_20261028.tar.gz), [integration receipt](../training_outputs/csts_native_adapter_integration_final_20261028.json).
