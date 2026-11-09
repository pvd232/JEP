# Fixed positive-recipe native diagnostic

`python -m csts_pilot.native_positive` is the capture and CPU replay entrypoint for
the final positive-recipe diagnostic. The earlier generic extraction pipeline is
preserved in `csts_pilot/extraction_native.py` as a historical implementation.

The new path uses a fixed Go recipe and the final Know spatial/action refinement.
The condition alone compiles the schema. Source passages supply inference input;
gold, ratings and paired passages do not enter the model request. Typed NER and
condition-compiled relation constructors are authorized for an experimental
48-case diagnostic. Symbolic counts and CountEvidence quote substitution are
disabled. Unsupported routes, parse errors, runtime failures and missing outputs
remain failures in the fixed denominator.

The provider is an immutable archive with the exact top-level import layout:
`native_capture.py`, `native_capture_backends.py`, `native_cpu_codec.py`,
`native_adapter/` and pinned helper/tokenizer metadata. All 13 core Python files
and three JSON assets match the approved core. Do not rewrite imports or replace
these files with an earlier adapter. The CLI verifies the driver and all support
hashes before executing the provider. Each command uses a fresh process.

Byte-identical readable source views are available for the
[handler](../experiments/native_positive_diagnostic48_v1/native_capture.py),
[backend](../experiments/native_positive_diagnostic48_v1/native_capture_backends.py),
[CPU codec](../experiments/native_positive_diagnostic48_v1/native_cpu_codec.py),
[driver](../experiments/native_positive_diagnostic48_v1/evaluate_native.py), and
[protocol builder](../experiments/native_positive_diagnostic48_v1/build_protocol.py).
These are inspection copies; runtime restores the complete immutable archive.

## Frozen identities

| Artifact | SHA256 |
| --- | --- |
| Provider archive v3 | `ea06d13eadaaa7127d7a0555de689a107c05018eaaa9b942d8c9e2ce2faea6bd` |
| Protocol archive v3 | `1671a8d3c7f7e2cfa74c8dca8b2c38844ae6d0feb162030f112191e041cd568e` |
| Inference-only job archive v1 | `010c7e88035d4041051e046c0d044a5bca5832f8f66e5e3f04ecb560efb12109` |
| Protocol JSON | `235a817398017a780cc354694dd9c48337200818983a1f52d0a33b00629b6946` |
| Capture driver | `3f1d1e2e898f426bf4019ea2e476dd0315b3751bf1129380aba767297e25dd89` |
| Job seal | `434bdbb118ebeb3246b094c47163d3e352087141a44163940ecf4f4097e89a1d` |

The readable protocol/configuration and per-arm origin receipts are in
`configs/native_positive_diagnostic48_v1/`. The protocol binds each authorized ID
to the SHA256 of its exact `{id, passage, condition}` triple. It cannot authorize
fresh evaluation or silently admit another source with the same ID.

## Reproduction commands

Run the commands below from the repository root. Restore the three named archives
from `training_outputs/` under `/tmp`; their top-level directories and
absolute configuration paths are part of the recorded experiment. The job holds
only the 48 inference triples and sealed protocol/compiler receipts. References
and ratings are separate from the inference artifact.

```sh
tar -xzf training_outputs/jep-native-positive-diagnostic-provider-v3-20261028.tar.gz -C /tmp
tar -xzf training_outputs/jep-native-positive-diagnostic-protocol-v3-20261028.tar.gz -C /tmp
tar -xzf training_outputs/jep-native-positive-diagnostic-job-v1-20261028.tar.gz -C /tmp

python -m csts_pilot.native_positive \
  --provider /tmp/jep-native-positive-diagnostic-capture-20261028 verify \
  --protocol /tmp/jep-native-positive-diagnostic-protocol-v3-20261028/protocol.json \
  --model knowcoder
```

Capture requires the recorded native environment and pinned checkpoint snapshots
in the protocol. Know uses the historical vLLM runtime; Go uses the pinned original
Flash/BF16 implementation. The refined Know spatial input has a 4096-token bound;
other Know inputs retain 2048, and Go retains 16384. Every request preserves its
actual tokenizer IDs, prompt profile, output reserve and generation options.

Run one model per fresh process, serialize access to the GPU, and atomically claim
the execution before dispatch. The driver also claims each job/model and source;
it does not retry generations or add companion cases.

```sh
python -m csts_pilot.native_positive \
  --provider /tmp/jep-native-positive-diagnostic-capture-20261028 capture \
  --job /tmp/jep-native-positive-diagnostic-job-v1-20261028 \
  --model knowcoder --python /path/to/recorded/native/python --output /path/to/knowcoder
```

CPU replay needs `tokenizers==0.23.3` and the frozen compatibility codec. Encoding
uses unchanged tokenizer JSON. The Go decode-only compatibility adjustment
preserves declared special-token IDs and matches retained historical output IDs
and text; it does not rewrite generations.

```sh
python -m csts_pilot.native_positive \
  --provider /tmp/jep-native-positive-diagnostic-capture-20261028 replay \
  --job /tmp/jep-native-positive-diagnostic-job-v1-20261028 \
  --model knowcoder --captures /path/to/knowcoder --output /path/to/replay.json
```

Replay validates request/manifest/raw-return hashes and recomputes normalization
from retained token IDs. It makes no model calls and does not certify semantic
support. The separate blinded evaluation uses the original gold and seven
substantive criteria, two independent model-assisted contexts, and all 48 cases
per model in eight families of six. Diagnostic resampling measures suite
stability; it is not representative population accuracy or a model ranking.
Even hypothetical 48/48 diagnostic acceptance cannot issue a fresh/production
qualification gate. Numeric counting, downstream readout and its added cost are
not established by this experiment.
