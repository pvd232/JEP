# Review

Independent review found no unresolved P1/P2 issues in the executed comparison. It verified all 120 pair identities, 239 source joins, 110 connected groups, the 12 predefined fallbacks and identical label-free GPU inputs. Separate metric code reproduced all point estimates and the 2,000-draw bootstrap interval exactly.

The GPU completed 449 unique encoding inputs and saved all vectors and scores. A Transformers loading-metadata set broke the final JSON receipt. The original code, receipt and failure log remain in the raw archive. A CPU-only recovery reproduced every saved cosine exactly, with no repeated inference. The current serializer handles sets deterministically and has a regression test.

An origin metadata correction distinguishes the preparation manifest from the executed GPT manifest. Both reference byte-identical pairs, sources and labels. The amendment preserves earlier metadata identities and leaves the sealed GPU inputs unchanged. Fresh preparation passed; four altered-provenance checks failed as expected.

Eleven tests passed on Colab, including tensor pooling. The additional serialization regression passed locally. No training, calibration, new GPT calls, native-model calls or fresh-test evaluation occurred.

[Results](../training_outputs/csts_proposition_similarity_120_20261028.md) · [Artifact index](../training_outputs/csts_proposition_similarity_120_20261028/artifacts.json)
