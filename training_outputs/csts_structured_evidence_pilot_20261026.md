# Structured evidence pilot

Completed a source-only structured-fact generation and semantic review pilot on 108 development inputs: 80 unique passage/condition inputs from the 45-comparison color diagnostic, plus 28 source groups where the existing evidence-trained encoder reduced absolute error. Sampling uses finalized development version 2 at source commit `769114a4967de1cb8fbb26709a13119e01df1cff`.

Four isolated assistant contexts generated the structured candidate. Every record preserves local entities, condition-specific predicates and values, exact source quotations, and explicit/inferred support status. Structural validation accepts all 108 records. Generation provenance is assistant semantic generation; the exact assistant checkpoint identity is unavailable.

Two fresh assistant reviewers independently formed source-only references before seeing candidate evidence. Their sealed reference hashes are preserved. Review then covered 168 randomized candidates with arm identities withheld and output formats visible.

## Matched extraction results

All three archived/candidate representations were available on the same 30 sources: 28 selected controls and two color sources. The remaining 78 color inputs have structured candidates and source references; their original cached targets were unavailable in the exported archive.

| Evidence arm | Sources | Faithful: reviewer A | Faithful: reviewer B | Both faithful |
|---|---:|---:|---:|---:|
| Archived Qwen spans | 30 | 21 | 20 | 20 |
| Archived generated propositions v1 | 30 | 29 | 30 | 29 |
| New assistant structured facts | 30 | 29 | 27 | 26 |

Across all 108 structured inputs, reviewers judged 106 and 98 faithful respectively; both accepted 97. In the 80-input color slice, both accepted 73. Reviewer disagreements remain visible in the evidence files. This pilot favors further inspection of scope, incomplete answers and inference handling. The existing generated-proposition candidate has the highest paired fidelity point count.

These are model-assisted diagnostic judgments. The selected control cohort and small paired color coverage limit generalization. Generator and representation changed together for the new candidate. Similarity scores, optimizer updates and new Qwen encoder inference remain at zero for this pilot.

## InstructUIE GPU arm

The runner pins `ZWK/InstructUIE` revision `48f45b25a01df1798f8c1c31751a973adb7e8647`. Source-only inputs provide explicit relation options; this is a custom schema-transfer evaluation. Raw generations and parser warnings are retained.

Execution target: existing GPU VM `jep-csts-format-20261021`, project `mantra-477901`, zone `asia-northeast3-a`, account `pvd2112@columbia.edu`. Existing plans identify an NVIDIA L4; live hardware and disk preflight await access. The shared GPU serialization lock is `/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock`.

The Mac polling worker reached its deadline. Direct browser reconnection redirected to Columbia CAS, where automatic approval review blocked institutional authentication pending explicit user authorization. InstructUIE generated zero predictions. The 108-input arm is staged in this branch for GPU execution after authentication.

After copying the runner and source inputs into `/home/machina/jep-instructuie-pilot-20261026`, use:

```bash
sudo -n -u machina flock -n \
  /home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock \
  /home/machina/jep-format-env/bin/python \
  /home/machina/jep-instructuie-pilot-20261026/run_instructuie.py \
  --inputs /home/machina/jep-instructuie-pilot-20261026/inputs.json \
  --output /home/machina/jep-instructuie-pilot-20261026/outputs.jsonl \
  --device cuda --dtype bfloat16 --execute
```

The local container cleanup removed 3.64 MiB of disposable caches. Project records and the reusable Python environment were preserved. Local inventory found no native VIPER artifact stores eligible for verified archive cleanup; GPU-side archival verification awaits access.

## Validation and evidence

Six schema/serialization unit tests pass. All 108 source identities, 108 structured records, two 108-item reference sets and two 168-item review sets have exact coverage. Every archived target is scored on its original source identity. The complete diagnostic inputs, candidates, mappings, reviews, sampling notes and results are in [structured_evidence_pilot](structured_evidence_pilot/).
