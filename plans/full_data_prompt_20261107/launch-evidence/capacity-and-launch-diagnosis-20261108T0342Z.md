# Capacity and launch diagnosis — 2026-11-08 03:42 UTC

This is an observed status report, not a training or launch approval.

## Quota and capacity

At 03:37 UTC, Mantra's GPUS_ALL_REGIONS quota was 2, with usage 1. Tokyo and Taiwan each had regional PREEMPTIBLE_NVIDIA_L4_GPUS limit 1 and usage 0. Seoul's corresponding usage was 1. The prior Tokyo resource-exhaustion responses did not establish a project-wide GPU shortage.

At 03:38:39 UTC, a successful `gcloud beta compute advice capacity` query for one Spot g2-standard-4/g2-standard-8 reported:
- Tokyo: recommended g2-standard-4 in asia-northeast1-b, obtainability 0.9, estimated uptime 600 seconds.
- Taiwan: recommended g2-standard-4 in asia-east1-b, obtainability 0.9, estimated uptime 3600 seconds.
These are advisory scores, not guarantees or reservations.

A subsequent start of the existing task worker `jep-full-prompt-spot-2-20261107` in asia-northeast1-b SUCCEEDED. The VM was RUNNING with SPOT provisioning. SSH verified the exact reviewed training commit `9b163a100362580f99722eecc63895420ecec3b1`, a real NVIDIA L4, no competing GPU process, no prior worker2 training state and the preserved task filesystem. No scientific training ran on worker2.

## Actual launch blocker

The next proposed terminal call would validate the preserved ten-review receipts and prior user authorization, write a new instance-bound worker2 launch record with its current GPU identity and independent poweroff deadline, and copy the launch JSON files through IAP. The execution interface rejected that call before execution, returning: `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` No specific triggering rule was provided. No bypass or alternate execution of that denied staging action was attempted.

The earlier local incident record at 00:19 UTC likewise described a combined launcher-staging call rejected before execution. That was a different failure class from Google's zone-capacity errors. Earlier expired Google login was already resolved. The exact reason for the execution-interface rejection is not established by the available evidence.

To avoid paying for an idle GPU, worker2 was stopped. Final inventory at 03:42:53 UTC confirms worker2 TERMINATED and worker1 RUNNING. The worker2 persistent disk remains preserved. No IAM or organization-policy changes were made.

## Active scientific work remains unaffected

At 03:42:08 UTC, Seoul worker1's service `jep-full-data-worker1-20261108T0311.service` was active/running with PID 1387 and NVIDIA L4 utilization 100%, memory 19,390 MiB. Arm A, seed 7 had completed epoch 1; its 492,021,760-byte native recovery archive was SHA-verified after cloud upload and download. Epoch 2 started at 03:34:02.928788 UTC. The collector remains active. No changes were made to its live source, protocol, approval, assignment or process.

## Design limitation discovered in the allocation handling

The reviewed lease and collector pin worker2 to the existing Tokyo instance and zone rather than selecting from an authorized deployment manifest. This made another-zone placement an orchestration change rather than an ordinary resource-selection operation. Repeated retries in one zone were too narrow. This limitation does not mean another GPU allocation is impossible; the successful allocation above demonstrates otherwise.
