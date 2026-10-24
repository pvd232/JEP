# Rating continuation: publication and shutdown

The authorized continuation is complete. The [reviewed report](csts_continuation_report.md), curves, predictions, traces and paired intervals were published at `097cf289e27045ae132f75c00da0bee5940899fb`. Training used source `ffa81e7bbd6d26d152aadf966a787ce17293b9d0` and pinned native VIPER `e4ce91fa0a9330e769644aba0fccdfe062d5d821`.

Both arms resumed terminal epoch-24 weights with their matching AdamW moments and RNG state. Encoder LR was held at `3e-6`, projection LR at `1e-4`, with zero additional warmup, validation patience five and a ceiling of 48 total epochs. Historical validation winners remained eligible. Checkpoints and validation calibration were frozen before test access.

| Objective | Stopped epoch | Selected epoch | Test Spearman | Raw test MSE |
| --- | ---: | ---: | ---: | ---: |
| MSE | 40 | 35 | 0.506417 | 0.132350 |
| Pearson | 33 | 28 | 0.487140 | 0.130195 |

MSE's Spearman gain over its original winner was +0.009522, with paired 95% interval [+0.006371, +0.012440]. Pearson's gain was +0.002935, interval [-0.000159, +0.006066]. The 2,000 paired draws resampled 1,241 source components from the same 2,620 comparisons. These intervals describe test-sample uncertainty conditional on one seed and an already examined benchmark. MSE remains the validation-selected ranking baseline; Pearson has lower raw test MSE.

Both arms stopped through validation patience. This establishes a validation plateau under the declared rule. A stationary training minimum remains unproven. New fitting took 337.60 seconds in total, and validation took 26.20 seconds. The native GPU-stage envelopes totaled 736.05 seconds, within the separate 1,800-second continuation budget.

All five experiment graphs and 79 measurements passed native verification. All 68 transferred evidence files passed SHA-256 and size checks. The restored evidence reproduced the preview result files exactly. [Native references](csts_continuation_native_verification.json), [collection receipt](csts_continuation_collection.json) and [timing definitions](csts_continuation_timing.json) preserve the details.

The fixed report ZIP was published through a native CPU stage on the Mac, its promoted cloud graph was verified, and its restored bytes matched SHA-256 `c8d96a319636d4c41fb2ddef198ed417f3c1230ac58ce13a960fa07fecb590f2`. The [publication receipt](csts_continuation_report_publication.json) records the sealed GCS artifact and run references. The ZIP captures report commit `097cf289e27045ae132f75c00da0bee5940899fb` before shutdown. This closeout and the cloud receipt supplement that frozen bundle.

Cloud storage promotion ran in a separate CPU worker while later computation and report analysis continued. All five promotions succeeded on their first attempt. Existing native graph verification was retained; VIPER core is unchanged.

At **2026-10-24 01:16:18 UTC**, fresh cloud responses confirmed:

- Seoul VM `jep-csts-format-20261021`, zone `asia-northeast3-a`, ID `8646910299736412654`: **TERMINATED**.
- Original VM `rico-source-l4-uswest4c`, zone `us-west4-c`: **TERMINATED**.
- Only this invocation's newly created `jep-csts-format-20261021` NAT was removed. Its configuration used `LIST_OF_SUBNETWORKS` scoped to the recorded pilot subnet; the router was reread to confirm removal.

The pre-shutdown guard confirmed a complete summary, all five published jobs, an empty GPU compute-process list and zero native trainers. Persistent disks, the router, subnet, existing environments and previous studies were preserved. The original monitor remains disabled. See the [cloud shutdown receipt](csts_continuation_shutdown.json) and [final status](csts_continuation_status.json).

Validation before execution: 46 focused CPU checks, Ruff and Pyrefly passed; all 47 pinned-VM checks passed, including CUDA precision and continuation regressions. Five focused report checks and the CPU-only report import also passed. The [first-pass review](../plans/csts-continuation-review.md) records the optimizer, scheduler, checkpoint and resume safeguards.
