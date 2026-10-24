# Tranche 2 closeout

Completed at 2026-10-24T04:24:21.736736+00:00. The [scientific report](csts_tranche2_report.md) and [results JSON](csts_tranche2_results.json) preserve all seven systems, paired intervals and stopping observations.

The report was published from Git commit `8a19b44053faacd70a96f1b14a57619f4efa2a10` through native VIPER on the Mac CPU. The fixed ZIP contains 9,800,064 bytes, with SHA-256 `f70c01593591ef8db47ac822f61612c8244c5e1ef2cff7914453bf3df1f69bef`. Its [native publication receipt](csts_tranche2_report_publication.json) records the verified graph and exact restored-byte comparison. The study's 19 runs and 89 measurements retain their original source and native references.

The [cloud shutdown receipt](csts_tranche2_shutdown.json) confirms:

- Seoul pilot `jep-csts-format-20261021`, ID `8646910299736412654`, in `asia-northeast3-a`: **TERMINATED**.
- Original `rico-source-l4-uswest4c` in `us-west4-c`: **TERMINATED**.
- The newly created NAT `jep-csts-format-20261021` in `asia-northeast3` was removed after its exact pilot-subnet scope was checked.
- Persistent disks were preserved. The stop guard found zero GPU compute processes or native workers and all 19 study publication jobs complete.

The cloud-recorded start-to-stop interval was 92.59 minutes. Recorded time in native GPU stages totaled 50.78 minutes. The wider instance interval includes startup, preflights, CPU fitting/evaluation, verification and publication. These are elapsed-time observations; the cloud receipt preserves the source timestamps.

The existing monitor is disabled, confirmed at 2026-10-24T04:24:24.158Z. The [completion record](csts_tranche2_completion.json) joins the scientific results, native report reference and cloud outcome.
