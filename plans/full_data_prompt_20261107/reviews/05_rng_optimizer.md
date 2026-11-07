# Independent reviewer 05: rng_optimizer

Status: **NOT RUN**. This is a task brief, not a completed review.

Review the frozen candidate source revision, protocol hash, PLAN.md, full_data_prompt_protocol.py, full_data_prompt_native.py, the baseline_models.py diff, tests and relevant original trainer callees. Do not inspect other reviewers' findings before your initial assessment. Do not modify files, provision resources, or start training.

Focus: Trace initialization and epoch-boundary continuation, optimizer/scheduler moments and CPU/CUDA RNG, dataloader generator, batch order, best checkpoint and patience. Spot replay must not reset optimizer. Same seed does not guarantee identical masks across lengths.

Return: provider/run ID; exact reviewed source revision and protocol hash; files/lines inspected; invariants; actionable findings with severity, smallest counterexample, repair, and regression test; unresolved exclusions; verdict Approve / Request changes / Incomplete. Passing CPU tests alone does not establish runtime correctness. Only claim executed checks for which you have retained output.
