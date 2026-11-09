# Original 48-case native diagnostic

The original first-attempt pipeline passed the joint seven-criterion model-assisted judgment on 12/48 Go cases and 9/48 Know cases. Each model produced 31 operational outputs; 10 routes were unsupported and 7 intentional empty-input controls failed before generation. These are diagnostic suite results, not representative population accuracy or a model ranking.

| Family | Cases/model | Go operative | Go accepted | Know operative | Know accepted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Identity/category |6|5|3|5|3|
| Color |6|5|1|5|1|
| Age/gender/size |6|5|1|5|1|
| Counts |6|0|0|0|0|
| Actions/roles |6|5|3|5|2|
| Spatial |6|1|1|1|1|
| Presence/negation |6|5|0|5|0|
| Scope/uncertainty |6|5|3|5|1|

| Fixed-denominator measure | Go | Know |
| --- | ---: | ---: |
| Joint all-criteria accepted |12/48|9/48|
| Answerable joint acceptance |11/32|8/32|
| Correct abstention on source absence |1/16|1/16|

“Answerable” includes source-supported uncertain and negative facts. Completeness alone does not establish supported evidence quality. All 48 cases remain in each model denominator, with eight families of six. Binding/multiplicity violations are separated from unverified operational cases in the full report.

References were source-only model-assisted and independently source-audited, with no human adjudication. The two fresh review contexts share the same model alias and reference anchoring; their agreement is not human accuracy calibration. Decisions use conjunction across all seven criteria; A/B accepted 13/12 Go and 10/9 Know, with 18 criterion disagreements and two final-acceptance disagreements.

All seven zero-call empty passages per model are intentional `empty_absent` negative controls, not a projection bug. The frozen renderer rejected empty strings before prompt construction. Seven Know error-debug fields also carried an earlier source response; those contexts were never judged as answers to the empty inputs. Original records remain immutable and receive no retrospective abstention credit. Token/raw replay verified the 62 actual generations; byte integrity does not establish semantic correctness.

These original 96 pipeline cases exclude the later seven-per-model first-generation recovery. That sensitivity has its own origin and cannot silently replace this report. Count dispatch remains unsupported; CountEvidence was not a fallback. No semantic, production or fresh-evaluation qualification was issued. Resampling intervals describe suite/component stability only.

Evidence archive: `csts_native_positive_diagnostic48_evidence_20261028.tar.gz`; SHA256 `1540c0cdd66dad1cc64494448f4a660c73f19a1bb578b609d346ae1ac7e26910`.
Primary summary SHA256 `0a7d7c270080e4dd782ede0a50c501c9ca5d9c2ef55c8056255458c86c2dae4f`.

The [separate recovery](csts_native_empty_input_first_generation_recovery_20261028.md) subsequently completed all 14 first calls with literal empty lists and successful token replay. It does not change these primary scores.
