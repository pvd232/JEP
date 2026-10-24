# Tranche 1 closeout

The [experiment report](csts_tranche1_report.md) and [evidence archive](csts_tranche1_evidence.tar.gz) are published to GitHub. The fixed full report bundle also passed native VIPER CPU publication and exact-byte restoration: [publication receipt](csts_tranche1_report_publication.json).

Cloud confirmation at 2026-10-23T23:29:23.563502+00:00 shows:

- Seoul pilot `jep-csts-format-20261021`, ID `8646910299736412654`, is **TERMINATED**.
- Original `rico-source-l4-uswest4c` remains **TERMINATED**.
- Only this invocation's newly created NAT, scoped to the dedicated pilot subnet, was removed. Persistent disks, the router and subnet remain preserved.

The cloud start-to-stop timestamps span **49.16 minutes**. This includes VM startup, CPU work, repair, storage operations, verification and idle periods. The experiment's separate native GPU-stage counter totaled **27.97 minutes**, including the failed evaluation. These are different accounting measures; the VM lifecycle elapsed time exceeds the stage counter. The two training loops used 5.26 and 5.35 fitting minutes, plus 0.42 validation minutes each.

The four successful prediction loops totaled **8.62 seconds**; their full native evaluation envelopes totaled **7.30 minutes**. The initial failed evaluation added **2.23 minutes**, and repair plus CPU checkpoint handoffs and collection added further wall time. Startup, repeated lineage checks and storage work dominated inference. The current evaluation pipeline has excessive overhead for this workload.

The pending safety shutdown closed new SSH logins before the final report transfer. All experiment evidence had already been restored and verified. The report was therefore published on the existing Mac CPU using the same account's current session in memory; the GPU stop used the cloud API. Native report publication and cloud cleanup both completed.

[Cloud receipt](csts_tranche1_shutdown.json) · [Completion record](csts_tranche1_completion.json) · [Timing breakdown](csts_tranche1_evaluation_timing.json).

The collaborative code walkthrough remains open. Prior studies and unrelated resources retain their existing state.
