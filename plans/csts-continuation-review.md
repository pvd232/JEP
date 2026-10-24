# Continuation first-pass review

Base: `c6d4520987644ee38931c7d1a84b8fb8af1eddbb`. Reviewed scope: continuation restore and loop, native input bindings and selection, paired analysis, report generation and final CPU publication arguments. Execution is authorized by the user instruction to proceed.

Invariants: resume terminal weights and their matching completed epoch and AdamW steps; retain moments; restore main-process RNG and pair-permutation state; set both learning-rate fields before creating the constant scheduler; keep the historical winner until validation improves; reset only the new-phase patience counter; keep parent artifacts and original result paths unchanged; freeze selection before test scoring; reuse unchanged evaluations; preserve native producer references and verified cloud publication.

The regression fixtures exercise real tiny CPU model gradients through the continuation, verify optimizer steps and exact next pair order, check all new learning rates, retain an incumbent byte for byte, replace an improved incumbent, and reject mismatched resume epochs. Native stage construction binds `initial_model` to parent `last_model` and `parent_resume` to the same producer's `resume_state`. The report regression uses original full winners and paired IDs. Initial review caught an incorrect dictionary access in a test and a report interval-key mismatch; both were repaired before launch.

Validation: 46 focused CPU tests passed in 4.80 seconds; Ruff passed for E/F/I with inherited E501 lines excluded. Pyrefly passed with the pinned VIPER source and existing report/task environments. No GPU experiment ran during implementation or this first-pass review. The exact source commit, environment and GPU checks will be recorded during the authorized preflight.

Residual limits: one training seed; already examined benchmark; constant-rate restart is an explicit second phase; early stopping supplies a validation plateau observation, while training stationarity remains unproven. Cloud promotion still performs native graph verification, and an independent live publication receipt is required at closeout.
