# Proposition subset trial

Status: **running**. Uses the 2,880 completed training answers and the 30-pair revised-policy development sample. Full answer generation remains stopped; no held-out test is released.

This is a small development triage experiment. Native metrics and training progress are preserved in [the results JSON](csts_tranche8_subset_results.json).

```json
{
  "phase": "native_status",
  "source_commit": "a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1",
  "name": "proposition_subset_v2",
  "status": "running",
  "module": "csts_pilot.proposition_subset",
  "started_unix": 1793047781.5107346,
  "supervisor_sha256": "75205868a63afedecb808276d22525b9dc34d6ca86cd6a4deac66d60b8a129cb",
  "supervisor_pid": 97112,
  "native_pid": 97115,
  "summary": {
    "status": "running",
    "in_flight": {
      "name": "prepare",
      "experiment_id": "csts_subset_a75fa36a_c1514635_prepare"
    },
    "source_commit": "a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1"
  },
  "runs": [],
  "publication_counts": {
    "published": 9
  },
  "free_bytes": 4987482112,
  "result": {},
  "preparation": {}
}
```
