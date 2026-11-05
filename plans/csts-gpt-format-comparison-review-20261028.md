# GPT format comparison review

Independent design and code reviews found no unresolved P1/P2 issues. Review covered matched batching, capture validation, provenance joins, rendering and fallback, the frozen trained reader, metric code and asynchronous publication. The [final audit](../training_outputs/csts_gpt_format_comparison_20261028/independent_audit.json) verified all 120 pairs, 239 sources and 110 groups, unchanged adapter weights, every point metric and all 2,000 bootstrap draws. Saved vectors reproduced the cosines within 9.01e-8.

The replacement campaign regenerates all three evidence formats under the same model, max reasoning setting, transport and 19 matched batch contexts. Batch membership and order are identical across formats; companion sources and repeated conditions cannot share a context. The stalled single-request campaign remains a separate diagnostic. Every first attempt is retained, with no response selection using similarity results.

The preparer verifies request, response and result hashes, exact source identities and all 717 source/format joins. Capture parsing rejects duplicate keys, non-finite JSON values, incomplete turns, tools and disagreeing final responses. Python parsing accepts data constructors through a restricted AST and never executes generated code. Unresolved local references remain explicit rendering failures.

The scorer uses the recovered proposition LoRA checkpoint and its original reader implementation, including the condition prompt, 160-token ceiling, EOD pooling and two-comparison batch layout. Each unavailable side falls back to its original passage. Gold ratings and direct GPT scores stay outside GPU inputs. Saved token IDs, pooled vectors, predictions, code identities and before/after adapter digests support replay without model calls.

Review fixes include deterministic serialization of loading metadata and shared locking for publication retries. The Codex launcher supplies a verified CA bundle per process while preserving explicit user settings and TLS verification. Publication runs asynchronously after each closed capture or GPU stage; successful full read-back is required before session close.

Validation passed: 59 relevant repository tests, 11 capture-runtime tests, five publication tests and nine runner compatibility tests on Colab. The eight-worker ramp received a separate review; it preserved completed and active calls and changed no model inputs or generation settings.

The first A100 scoring attempt failed because preinstalled torchao 0.10 was incompatible with PEFT's optional dispatch requirement. Removing that unused dependency allowed the same code, checkpoint and inputs to run with plain BF16 LoRA. The failed attempt's receipts and logs remain preserved.

The comparison measures evidence as inference inputs to one fixed trained reader on previously exposed validation examples. It cannot establish better teacher supervision or infer semantic fidelity from valid syntax. The three primary differences are exploratory; 2,000 paired resamples of 110 connected source groups give unadjusted intervals conditional on the frozen outputs. They omit generation variability and dependence within the 19 shared model contexts.

[Executed design](csts-gpt-format-batched-comparison-20261028.md) · [Results](../training_outputs/csts_gpt_format_comparison_20261028.md)
