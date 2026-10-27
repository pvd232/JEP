# Full Qwen proposition comparison

[Per-epoch validation scores](epoch_scores.md) · [Raw history](epoch_scores.json)

Publication status: the first full-run epoch is published. Continuous publisher launch is awaiting terminal reconnection; the Work Mode execution environment disconnected during setup.

The persistent publisher checks the GPU every 30 seconds and pushes each newly completed epoch or stage change. Refresh the GitHub page to see new commits. It runs outside the active GPU training checkout and preserves every recorded epoch across all four stages.

Source: scripts/publish_proposition_epoch_scores.py, scripts/proposition_epoch_ssh.py and scripts/export_proposition_epoch_scores.py. The GPU exporter is already installed in /home/machina/jep-csts-proposition-indicative-20261026-operator/export_epoch_scores.py.

On the Mac, use an isolated clone, run the publisher with --once, then detach it with --poll-seconds 30 and --state-directory outside the clone. Keep its PID, local publisher_status.json and logs. A singleton lock prevents duplicate publishers; transient errors retry automatically. Pushes build on the fetched head and preserve concurrent source changes.

The experiment trains from pretrained Qwen3-Embedding-8B. The completed short continuation pilot is recorded separately under training_outputs/proposition_indicative_20261026.
