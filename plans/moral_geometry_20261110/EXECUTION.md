# Moral geometry overnight pilot

This is the execution charter for the already authorized computational pilot. Finish useful measurements before the deadline. Preserve the scientific question through failure and recovery.

## Questions

1. Does specifying a moral condition improve similarity and retrieval on held-out scenario families?
2. Does imposing inner-product geometry add measurable value to an unconstrained scorer?

The second question is unresolved unless the comparison changes a geometric restriction while controlling other differences. Ordinary conditional cosine embeddings already supply PSD Gram matrices. A square-root distance transform preserves their ranking and is not a new method.

The complete frozen bounds and scientific rules are in [protocol.json](protocol.json). Hash that file and retain its hash with every stage. A needed correction must receive a new protocol version; retain old predictions and report the correction. Never tune the protocol after seeing held-out results.

## Execution sequence

1. Spend at most 45 minutes finding reusable model checkpoints, published human similarity labels, runtimes and existing runner code. Reuse the existing JEP sources and selected checkpoints. Do not retrain an 8B backbone. If the main checkpoint cannot be restored within the cap, record that arm as unavailable and run the available baselines without calling that a completed four-arm comparison.
2. Freeze a modest controlled probe set with repeated situations across conditions. Prefer 12–20 scenario families and three clear conditions (harm, intention/responsibility, coercion/agency). Include lexical distractors, relevant factual changes, irrelevant wording changes and condition paraphrases. Author-designed expectations are synthetic, not expert labels. Keep human-rated published evidence in a separate evaluation track; do not let its unavailability block the synthetic screen.
3. Freeze family-based splits, score mappings, prompts, model identities and metrics before full scoring. Keep human judgments in evaluation unless a separately declared small-head training arm explicitly uses a training portion. Never fit PSD projections using held-out target similarities, even indirectly through a completed full label matrix.
4. Run the four named arms in protocol.json where feasible. Batch and cache embeddings/inference once. Reuse compatible completed outputs on restart. If training lightweight heads is warranted, use three seeds; otherwise do deterministic evaluation without pretending seeds create independent data.
5. Perform only the four sufficient checks in protocol.json. Add another check only for a concrete discovered scientific defect, not code coverage, general CI, lint policy, documentation completeness or hypothetical edge cases.
6. Save predictions first, then recompute metrics independently and report by scenario family/condition, with uncertainty grouped by family. Report matrix-fit diagnostics separately from actual generalization or retrieval. A negative or null result is a successful pilot outcome.
7. Publish a concise report, machine-readable results, exact data/protocol/source/model identities and failure log to this branch. Report at the deadline even if some arms or cloud uploads remain incomplete.

## Efficiency rules

- Setup/data discovery: 45 minutes total. One issue: at most 20 minutes and two repair attempts before isolating it and continuing useful work. At most two recovery launches for the overall run.
- Full-backbone training, multi-agent review panels, new frameworks, broad CI, exhaustive test authorship and unrelated refactors are outside this pilot.
- Maximum one GPU, two GPU-hours total. Prefer cached outputs and CPU analysis. If provisioning access is denied, preserve the failure and continue CPU work; do not change IAM, credentials or login configuration.
- VIPER integration has a 15-minute implementation cap. Keep the existing model runtime; do not migrate the experiment into new native execution contracts. Preserve provenance locally and use a separate asynchronous publisher with bounded retries. Upload failure is publication_pending, not a failed scientific stage. No per-batch artifact uploads or repeated hashing of unchanged checkpoints.
- Preserve unique output bytes on the durable CPU host before deleting task GPU storage. Finish verified publication and cleanup separately from the scientific score report. The pre-existing dev host is shared and must remain.

## Durable execution and recovery

Runtime state lives at /home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110/state.json. Keep code and protocol here; keep generated outputs outside Git until selected publication artifacts are ready. Write state updates atomically and append stage events. Record the actual durable job ID immediately after submission; keep unknown hosted agent IDs null rather than inventing them.

Use the existing runner:

    cloud-project --project jep submit --cwd /home/pvd2112_columbia_edu/columbia-worktrees/jep-moral-geometry-20261110 --checkpoint /home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110 --resume-json '["ABSOLUTE_PYTHON","ABSOLUTE_RUNNER","--resume"]' -- ABSOLUTE_PYTHON ABSOLUTE_RUNNER --resume

Replace these placeholders only after implementing and smoke-running the real checkpoint-aware command. Execute the main pipeline under a nonblocking file lock at /home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110/execution.lock. Hold it for the compute process lifetime so duplicate submissions cannot duplicate work. An automatic retry must resume completed stages, not restart the study from scratch.

Every recovery invocation must first:

1. Read protocol.json, state.json, events and saved outputs.
2. Ask cloud-project status for each recorded job ID. Reconcile cloud-project list for unrecorded jobs matching this exact worktree and inspect surviving writers/locks. An API error is unknown status, not failure.
3. Leave a live healthy compute job alone even if the original chat ended. Quiet logs alone do not establish failure. If stalled progress is suspected, inspect the exact process and stage before cancellation.
4. If a job is terminal-failed/interrupted and no surviving writer owns the lock, take the execution lease, increment the recovery generation and repair only the failed stage. If no job was ever launched and state says ready_for_execution, the scheduled agent is explicitly authorized to implement and launch the pilot from this charter.
5. Reuse immutable compatible completed predictions, embeddings and checkpoints. Preserve input/protocol hashes. Never rerun successful training because the report or uploader failed.
6. Stop new compute at the deadline. Finalize the partial/full report, reconcile owned resource cleanup and disable the automation once the report and cleanup are settled. Cap the monitoring schedule so it cannot run indefinitely.

The scheduled task creates a fresh agent invocation at most hourly; it is not an immediate VM-failure callback. The VM durable runner keeps work alive between checks. Separate-agent recovery is configured when the scheduler accepts the task; its first actual execution is a distinct observation.

## Publication

Repository: pvd232/JEP. Branch: experiment/moral-geometry-pilot-20261110.

Publish progress/results under training_outputs/moral_geometry_20261110/. Commit only this pilot's plan, scripts and selected outputs. Preserve other worktrees and branches. Avoid public redistribution of restricted datasets; publish references, hashes and permitted derived outputs.

Current handoff: the execution charter and recovery mechanism are being prepared. No main experimental job has been launched yet. The scheduled agent must make that distinction in its first status.
