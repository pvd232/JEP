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

Execution uses terminal SSH to the existing VM `jep-csts-format-20261021` in `mantra-477901`, zone `asia-northeast3-a`. Live preflight confirmed an idle NVIDIA L4 with 23,034 MiB VRAM, PyTorch 2.14.0+cu130 and Transformers 5.20.2. All 108 extraction prompts fit the official input limit; the longest has 103 tokens.

The checkpoint's 12 required files total 45,069,805,378 bytes. Delivery uses the pinned Hugging Face revision through the existing private GCS bucket. Source identities are checked during upload; GPU download checksums are computed during the file write. The model is reusable experiment input.

The GPU worker waits for checkpoint delivery and then acquires the existing shared GPU lock. It runs all 108 inputs with BF16 weights, deterministic generation, one beam and a 128-token output limit. Current predictions: zero, with checkpoint transfer in progress.

```bash
/home/machina/jep-format-env/bin/python \
  /home/machina/jep-instructuie-pilot-20261026/run_instructuie.py \
  --inputs /home/machina/jep-instructuie-pilot-20261026/inputs.json \
  --output /home/machina/jep-instructuie-pilot-20261026/outputs.jsonl \
  --model-path /home/machina/jep-instructuie-pilot-20261026/model \
  --device cuda --dtype bfloat16 --execute
```

Cleanup released 51,190,583,296 bytes across 184 local files and 56 artifact groups, leaving 54,125,297,664 bytes free before checkpoint copying. It matched sealed publication records, local SHA-256 and live GCS CRC32C/size/generation. Original run records and a durable restoration receipt are retained. Execution state is recorded in `structured_evidence_pilot/instructuie_status.json`.

## Validation and evidence

Six schema/serialization unit tests pass. All 108 source identities, 108 structured records, two 108-item reference sets and two 168-item review sets have exact coverage. Every archived target is scored on its original source identity. The complete diagnostic inputs, candidates, mappings, reviews, sampling notes and results are in [structured_evidence_pilot](structured_evidence_pilot/).
