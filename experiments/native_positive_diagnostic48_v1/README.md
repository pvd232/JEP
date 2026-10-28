# Code for the original 48-case diagnostic

These Python files are byte-identical copies from the executed provider archive. They expose the capture handler, native backends, CPU codec, evaluator, preparation code and relevant pinned author helpers for review. [source-files.json](source-files.json) records each file's SHA-256.

The complete runtime layout also needs its frozen adapter, JSON assets and tokenizer metadata. Restore the [provider archive](../../training_outputs/jep-native-positive-diagnostic-provider-v3-20261028.tar.gz) and use the [public CLI instructions](../../docs/native_positive_repair.md) to reproduce capture or replay. Running this inspection subset directly is unsupported.

The adapter snapshot is preserved in the archive and in commit `caf68c9`. The current `csts_pilot/native_adapter` subsequently repairs the empty-string renderer/normalizer contract; that later change has its own origin and does not alter these executed files or the original 96 cases.

The [archive index](../../training_outputs/csts_native_positive_diagnostic48_archives_20261028.json) binds the original inference-only job, protocol and both model captures. Source references and ratings were excluded from generation. This is a designed diagnostic suite, with no representative accuracy or model-ranking claim.
