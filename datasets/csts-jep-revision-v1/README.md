# JEP C-STS revision 1

A project-authored revision of C-STS, combining a second semantic review of training and test labels with validation V4.2. This package distributes source IDs, label dispositions, review decisions and reconstruction code.

| Split | Reviewed | Usable | Invalid | Unresolved scope | Split restriction |
|---|---:|---:|---:|---:|---:|
| Training | 6,980 | 6,051 | 920 | 9 | 0 |
| Validation | 1,830 | 1,576 | 253 | 1 | 0 |
| Test | 2,834 | 2,430 | 395 | 4 | 5 |

Use **`jep-csts-v1`** when reporting results. The project training/validation partitions come from connected-caption components of the upstream training CSV. Project test comes from the upstream released validation CSV. The 2,532 original training rows removed for overlap stay excluded. Labels and evaluation denominators differ from earlier releases, so scores should be identified by revision.

## Repeat review

All **9,814 training/test comparisons** received a fresh manual assistant reading. Initial decisions were saved before the previous labels were compared; two records were exposed during schema inspection. Five assistant contexts divided the rows, with a separate assistant adjudicating candidate changes and the root reviewer approving the final 25 changes. These contexts provide a recorded model review, with human label accuracy still unmeasured.

Initial exact agreement with the prior assistant audit was **7,891/9,814 (80.4%)**. All initial grades remain in `independent_grades.json`. Differences include ordinary graded judgments and reviewer mistakes; they were reviewed rather than automatically substituted. The final change list contains **8 numerical corrections, 11 new invalid cases and 6 new scope exclusions**. The source-only rubric and user anchors remain fixed. No encoder predictions or new model scores were used to choose changes.

Validation V4.2 is included byte-for-byte. Its four inclusion restorations are `train_624=5`, `train_1075=3`, `train_1809=3` and `train_2022=3`; the user approved inclusion and the assistant assigned these grades. All other 1,826 validation records, the prior 1,572 usable rows and the twelve confirmed exclusion rationales are preserved.

## Reconstruct

Obtain `csts_train_reannotated.csv` and `csts_validation_reannotated.csv` from [LivNLP/C-STS-Reannotated](https://huggingface.co/datasets/LivNLP/C-STS-Reannotated/tree/058ac842f5f19d27b08ad54f6d4a2c50b3f9578b) at revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b`, under the upstream access terms. Python 3.9 or later is sufficient; no extra packages are required.

```bash
python datasets/csts-jep-revision-v1/reconstruct.py --source /path/to/upstream-csvs --output /path/to/jep-csts-v1
```

The script applies the 25 explicit overrides to the training/test baseline dispositions, joins unchanged validation labels, verifies source/package/output hashes and split separation, then writes `train.json`, `validation.json`, `test.json` and a receipt. Output rows retain source IDs, captions, condition, 1–5 rating, normalized target `(rating-1)/4`, pair ID and connected-caption group ID. Excluded dispositions remain in the ID-based annotation package.

## Files and checks

- `training.base.labels.json`, `test.base.labels.json`: frozen baseline dispositions from [audit commit `97ffb9a`](https://github.com/pvd232/JEP/commit/97ffb9a7168b76b5d9cd08d71768e81e4ffb56e3); apply `changes.json` for this revision.
- `validation.labels.json`: approved validation V4.2, unchanged.
- `changes.json`: every correction, alternative scope reading and explicitly adjudicated retention.
- `independent_grades.json`: initial per-row independent judgments with their encoding and counts.
- `rubric.md`: frozen semantic policy and user adjudications.
- `manifest.json`: final counts, input hashes and reconstructed output hashes.
- `verification.json`: source reconstruction, validation preservation and final package checks.

Reconstruction checks include zero exact or canonicalized caption overlap between splits and zero conflicting labels for duplicate caption-pair/condition rows. Repeated rows within splits are retained for source-ID continuity and listed in verification. The original audit's compressed evidence archive could not be retrieved for a fresh hash check; this limitation is recorded separately from the successfully reproduced CSVs and exports. Full prior evidence remains at the pinned audit commit.

## Attribution and access

The upstream reannotation is [Zhang, Zhou and Bollegala (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1373/), based on [Deshpande et al.'s C-STS](https://github.com/princeton-nlp/c-sts) and [Tu et al.'s reannotation](https://github.com/brandeis-llc/L-CSTS). The pinned LivNLP dataset card declares [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The original C-STS distributor requests that unencrypted captions and passwords stay with authorized users. This package supplies IDs and annotation changes; obtain captions through the upstream distributors. Changes here cover labels, exclusions and project partitions. See `NOTICE.md` for source links.
