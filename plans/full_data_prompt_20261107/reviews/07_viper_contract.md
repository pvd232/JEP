# Independent reviewer 07: viper_contract

Status: **NOT RUN**. This is a task brief, not a completed review.

Review the frozen candidate source revision, protocol hash, PLAN.md, full_data_prompt_protocol.py, full_data_prompt_native.py, the baseline_models.py diff, tests and relevant original trainer callees. Do not inspect other reviewers' findings before your initial assessment. Do not modify files, provision resources, or start training.

Focus: Review actual stage/config/inputs/outputs/source identities and native plan builder APIs. Bound-source inputs must not redeclare data_role. Ensure new prompt field survives checkpoint save/load, scoring verification and resume.

Return: provider/run ID; exact reviewed source revision and protocol hash; files/lines inspected; invariants; actionable findings with severity, smallest counterexample, repair, and regression test; unresolved exclusions; verdict Approve / Request changes / Incomplete. Passing CPU tests alone does not establish runtime correctness. Only claim executed checks for which you have retained output.
