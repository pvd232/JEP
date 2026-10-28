# Full Qwen proposition comparison

[Per-epoch validation scores](epoch_scores.md) · [Raw history](epoch_scores.json)

Continuous publication is active through the existing GPU SSH route and connected GitHub tools.
The publisher checks every 30 seconds and appends each newly completed epoch or stage change.
Refresh the GitHub page to see new commits.

The active controller keeps a heartbeat outside the training checkout in
/home/machina/jep-csts-proposition-indicative-20261026-operator/publication_controller_status.json.
The hourly completion check provides recovery and final reporting.

The experiment starts from pretrained Qwen3-Embedding-8B. The short continuation pilot is stored separately under training_outputs/proposition_indicative_20261026.
