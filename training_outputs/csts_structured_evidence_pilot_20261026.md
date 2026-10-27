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
| Actual InstructUIE relation extraction | 30 | 19 | 21 | 19 |

Across all 108 structured inputs, reviewers judged 106 and 98 faithful respectively; both accepted 97. In the 80-input color slice, both accepted 73. Reviewer disagreements remain visible in the evidence files. This pilot favors further inspection of scope, incomplete answers and inference handling. The existing generated-proposition candidate has the highest paired fidelity point count.

These are model-assisted diagnostic judgments. The selected control cohort and small paired color coverage limit generalization. Generator and representation changed together for the new candidate. Similarity scores, optimizer updates and new Qwen encoder inference remain at zero for this pilot.

## InstructUIE GPU arm

The actual `ZWK/InstructUIE` checkpoint, revision `48f45b25a01df1798f8c1c31751a973adb7e8647`, generated all 108 outputs on the existing NVIDIA L4 VM. The run used BF16, one beam, deterministic decoding and a 128-token output limit. All prompts fit the 512-token input limit; the maximum was 103 tokens. Loading took 222.6 seconds. The generation manifest records software, hardware, input identity and runner identity.

The same two readers scored the new raw outputs against their unchanged, previously sealed source-only references. Candidate packets omitted model IDs and similarity ratings. Formats remained visible.

| Cohort | Sources | Faithful: reader A | Faithful: reader B | Both faithful |
|---|---:|---:|---:|---:|
| All diagnostic inputs | 108 | 91 | 93 | 91 |
| Color diagnostic | 80 | 74 | 74 | 74 |
| Selected evidence-helped controls | 28 | 17 | 19 | 17 |

The color diagnostic had six failures under the sealed reference policy. Five were abstentions on accepted typical-color inferences: yellow banana and white snow. One output retained a dog's brown and white colors and omitted the other dog's explicit black color. The reference policy accepts ordinary contextual inference; the tested relation-extraction prompt emphasizes mentions in the sentence.

Control failures included incomplete activities, partial locations and entity multiplicity. For example, the four-bear caption contains one white bear, two yellow bears and one brown bear. The generated relations contain one white, one yellow and one brown color–bear pair. This exposes a representation issue when repeated entities share a relation value. Reader disagreements remain available in the per-candidate files.

There were 11 raw abstentions, 118 parsed triples and two outputs with parser warnings. Semantic review used the preserved raw text. These results characterize this checkpoint, relation prompt and condition-label schema. The matched slice has 28 selected controls and two color sources; its counts describe that diagnostic sample. Archived generated propositions v1 had 29/30 accepted by both readers in the matched slice.

This run measured extraction fidelity. Qwen encoder optimizer updates and new similarity evaluations for this pilot are zero.

## Execution and cleanup

Terminal SSH access is working. Execution used the existing `jep-csts-format-20261021` VM in `mantra-477901`, zone `asia-northeast3-a`, and its shared GPU lock. The 12 checkpoint files total 45,069,805,378 bytes. The private GCS mirror retains each pinned source identity and object generation. Checkpoint hashes were computed during transfer writes.

Cleanup released **51,190,583,296 bytes** across **184 local files** and **56 artifact groups**, leaving 54,125,297,664 bytes free before checkpoint copying. It matched sealed VIPER publication records, local SHA-256 and live GCS CRC32C/size/generation. Run records were retained. The restoration receipt is backed up in the existing private bucket; its immutable address and identity are in `structured_evidence_pilot/cleanup_summary.json`.

After inference, the temporary 45.1 GB checkpoint copy was released. Final free space is **54,127,783,936 bytes (50.4 GiB)**. The private GCS mirror and pinned public source remain available for restoration through the supplied download script.

Execution sources are in `scripts/run_instructuie.py`, `scripts/instructuie_operator/` and `scripts/cleanup_archived_pilot_files.py`. Raw generations, generation provenance, review packets, both completed reviews, source checkpoint addresses and cleanup metadata are in [structured_evidence_pilot](structured_evidence_pilot/).

## Validation and evidence

Six schema/serialization unit tests pass. All 108 source identities, 108 structured records, two 108-item reference sets and two original 168-item review sets and two new 108-item review sets have exact coverage. Every archived target is scored on its original source identity. The complete diagnostic inputs, candidates, mappings, reviews, sampling notes and results are in [structured_evidence_pilot](structured_evidence_pilot/).

Recompute the additional-arm summary with `python scripts/instructuie_review.py summarize training_outputs/structured_evidence_pilot --review-a training_outputs/structured_evidence_pilot/instructuie_review_a.json --review-b training_outputs/structured_evidence_pilot/instructuie_review_b.json`.
