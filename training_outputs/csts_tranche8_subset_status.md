# Proposition subset trial

Status: **running**. Uses the 2,880 completed training answers and the 30-pair revised-policy development sample. Full answer generation remains stopped; no held-out test is released.

This is a small development triage experiment. Native metrics and training progress are preserved in [the results JSON](csts_tranche8_subset_results.json).

```json
{
  "phase": "native_status",
  "source_commit": "0314b6ccda11c4eb929754a9d4837f98946fd42c",
  "name": "proposition_subset_v1",
  "status": "running",
  "module": "csts_pilot.proposition_subset",
  "started_unix": 1793046121.5382242,
  "supervisor_sha256": "75205868a63afedecb808276d22525b9dc34d6ca86cd6a4deac66d60b8a129cb",
  "supervisor_pid": 93843,
  "native_pid": 93846,
  "summary": {
    "status": "running",
    "in_flight": {
      "name": "prepare",
      "experiment_id": "csts_subset_0314b6cc_9c518b6d_prepare"
    },
    "source_commit": "0314b6ccda11c4eb929754a9d4837f98946fd42c"
  },
  "runs": [],
  "publication_counts": {
    "published": 7
  },
  "free_bytes": 5180768256,
  "result": {},
  "preparation": {}
}
```
