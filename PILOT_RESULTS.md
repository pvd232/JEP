# Pilot execution results

The three training arms completed through VIPER on CPU. Each passed verification of its model and training state. Evaluation metrics were recomputed from saved predictions. Each run contains eight training measurements and two evaluation metrics.

The dataset contains scripted Spanish passages about reparations, harm, sanctions and restoration. It has 384 training pairs, 216 development pairs and 672 test pairs. Whole cases stay in one split. The test includes two composed questions. Each arm used one seed and eight optimizer steps. The model was a randomly initialized T5 with one encoder layer and one decoder layer.

These runs establish that the training and evaluation code executes. Estimating the value of annotation supervision requires longer pretrained runs, development settings and repeated seeds. Testing JEP transfer requires reviewed testimony and expert ratings.

## Recorded scores

| Arm | Test MSE | Test Spearman | Composed MSE |
| --- | ---: | ---: | ---: |
| ratings | 0.084791 | 0.268372 | 0.084690 |
| joint | 0.097770 | 0.277271 | 0.092842 |
| shuffled | 0.097480 | 0.283141 | 0.092605 |

Similarity training alone had the lowest MSE in this short run. The joint and shuffled annotation arms produced similar scores. The scores describe eight optimization steps on this scripted dataset.

## Additional checks

The split and gradient tests passed. Ruff passed. Pyrefly reported zero errors. A separate CPU check loaded the pinned pretrained FLAN-T5-small model and confirmed that both losses reach the encoder. Its recorded values are in `pretrained_check.json`. That probe used a single forward pass and gradient calculation.

## GPU status

Both registered MANTRA L4 runners were offline at inspection. Starting the GPU through the connected development VM requires Google Cloud reauthentication for `peter@aetherlabs.live`. The pretrained GPU run remains pending. The exact command and model revision are in `PILOT.md`.

## Files

`pilot_results.json` contains the calculated scores. `pilot_summary.json` identifies the native VIPER records on the development VM. `pilot_evidence` contains traces, predictions and measurement logs. Full native evidence remains on that VM.

Source commit: `f60003f261fd2095d8ab5b04899126d305ac3a48`. VIPER commit: `8ae163150f15613743d2a016c84bc42bfa0baa32`.
