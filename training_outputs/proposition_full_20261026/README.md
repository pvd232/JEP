# Full Qwen proposition comparison

[Per-epoch validation scores](epoch_scores.md) · [Raw history](epoch_scores.json)

A detached native process checks the GPU through SSH every 30 seconds and publishes newly completed epochs and stage changes to this branch. Refresh the GitHub page to see new commits.

The publisher runs independently of the chat session. It uses a singleton process lock, retries transient failures, preserves every recorded epoch and pushes over the latest branch head. A heartbeat is written outside the GPU training checkout at `/home/machina/jep-csts-proposition-indicative-20261026-operator/publication_controller_status.json`.

The publisher source is `scripts/publish_proposition_epoch_scores.py`; `scripts/proposition_epoch_ssh.py` uses the existing Mac SSH identity. Local process status and logs are in the task's `scratch/proposition-epoch-publishing/publisher-state` directory. The hourly completion check provides recovery and final reporting.

The full experiment starts from pretrained Qwen3-Embedding-8B. The completed short continuation pilot is stored separately under `training_outputs/proposition_indicative_20261026`.
