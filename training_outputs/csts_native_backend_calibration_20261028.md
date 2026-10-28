# Native backend calibration and task-aware repair, 2026-10-28 UTC

Both native inference paths now execute the pinned checkpoints. The selected controls show no observed output-token change from the earlier modern compatibility backends. The remaining C-STS misses therefore still require task/schema and capability diagnosis. These controls are not a representative quality score, and the repaired routes remain unapproved for training.

## KnowCoder: canonical runtime versus modern FP16

The historical environment uses Python3.10, Torch2.1.0+cu118, Transformers4.34.1 and vLLM0.2.2+cu118. BASE and IE are separate pinned checkpoints. Each ran the same15 frozen requests once in a separate process, with author framing, greedy decoding, a640-token cap and triple-quote stop. The disclosed0.6 GPU-memory fraction changes resource reservation; max_num_seqs remains4. The earlier modern FP16 captures used a1024-token cap. Every output ended on EOS before either cap.

All30 prompt strings, supplied/returned input token vectors and generated output vectors match their modern FP16 counterparts exactly. All70 indexed capture hashes verify. There are zero schema failures or truncated outputs. Earlier BASE BF16 and FP16 outputs also matched on the15 selected controls. These observations exclude a detected backend/precision effect on these controls; they do not prove general equivalence.

| Selected task | BASE | IE |
| --- | --- | --- |
| Food NER, two schema variants | sandwich and pickle | sandwich and pickle |
| Wetsuit relation, two variants | empty | Wears(man,wetsuit) |
| Tennis NER, description only | empty | Sport(tennis) |
| Tennis NER, published examples | Activity(tennis) | Activity(tennis) |
| Surfboard color; pizza location; soccer relation | empty | empty |
| Unstated snow color, two variants | empty | empty |
| Published Kurush control |2/3 reference matches plus2 extra relations |3/3 reference matches |

Nonempty counts are4/15 and7/15. They mix author examples, target positives, negative controls and two schema variants; they are not accuracy estimates. Activity(tennis) retains a useful span with a broader declared ancestor label. It is not an empty result. The task-aware candidate requests flat leaf labels to remove that avoidable output ambiguity.

## GoLLIE: original model code and FlashAttention

The original pinned modeling_flash_llama.py (SHA25639ed69a0a8f40344981ba6c142074ea315769a770d959ef214aab41d181a6dbd) runs with Transformers4.34.1, Torch2.1cu118 and official FlashAttention2.3.4, with BF16 model parameters. It retains its actual rotary base10000 and all291 learned parameter names/values. Both active weight shards and all seven configuration/tokenizer/source files match the primary pinned release bytes.

The cached checkpoint had omitted the custom source file because the original stock loader did not require it. The exact official source was added without editing its bytes. Old Triton2.1 could not discover the existing NVIDIA driver because the system ldconfig cache omitted libcuda. A task-local, read-only ldconfig -p wrapper appends the verified real driver path only for the Go process. It changes no global cache, package, driver, kernel or model math. Its receipt retains the real driver and wrapper hashes. The rejected alternate-cache approach was never executed.

Five fixed fixtures compare the original Flash model to stock eager attention in Transformers4.34.1 using128-token manual greedy decoding. The original and stock reference produce identical output IDs on5/5. The four applicable target fixtures also match the prior Transformers5.20 SDPA input and output IDs. All outputs reach EOS without truncation; all sampled cached-versus-full-prefix top1 checks agree. Prefill logits differ by up to0.09375–0.1875, so this is observed token agreement, not numerical or general backend parity.

The published author control recovers its three relations. The descriptive surfboard schema returns HasColor(surfboard,white); the generic surfboard schema and the food-as-relation schema remain empty. The unstated snow-color control remains empty. Task-aware NER/RE/event checks follow separately.

## Implementation and current limits

The new csts_pilot.native_adapter package contains the reviewed condition-only compiler, native prompt profiles, strict non-executing parsers, explicit stage normalization, conservative count projection and common evidence export. It retains source bindings, context, facet absence and operational failures. BASE/IE descriptors remain separate. The initial10-module integration was byte-identical to frozen scope-v5. A subsequent explicit envelope fix strips external whitespace before AST parsing; it changes no annotation or source span. The legacy adapter and its captures are unchanged.

The integrated80 adapter tests and69 existing extraction/transport tests pass (149 total). Independent relocation review also exercised compile, descriptor, normalize and export through the real repository CLI. These checks establish implementation behavior, not model fidelity. Counts remain blocked outside their separately reviewed finite development gate; unsupported routes, parse/runtime failures and lost bindings cannot become correct abstentions.

Nine exposed positive anchors per model, separate KnowCoder Wears/Sport replays, staged count checks and broader scope checks are still empirical gates. Source-only references for locked/fresh evaluation are separately audited and sealed; no locked/fresh native capture has been authorized by this checkpoint. Failed setup/preflight attempts are retained separately and are not counted as model abstentions. No representative model ranking, downstream training or full-test result is claimed here.

Raw captures and exact audit receipts are linked in the accompanying JSON manifest. The prior model-ranking conclusion remains suspended.

## Primary implementation sources

- [KnowCoder author inference code](https://github.com/ICT-GoKnow/KnowCoder/blob/b7859789fc7641e03916074088859aa592332ad3/eval/src/inference.py) and [native task cases](https://github.com/ICT-GoKnow/KnowCoder/blob/b7859789fc7641e03916074088859aa592332ad3/Cases.md).
- [Pinned GoLLIE model implementation](https://huggingface.co/HiTZ/GoLLIE-7B/blob/d3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9/modeling_flash_llama.py) and [primary revision/LFS metadata](https://huggingface.co/api/models/HiTZ/GoLLIE-7B/revision/d3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9?blobs=true).
