# Pretrained GPU pilot

All three arms completed on an NVIDIA L4 and passed VIPER verification. MSE and Spearman correlation were independently recomputed from saved predictions.

FLAN-T5-small was trained for 120 steps per arm using seed 7. The similarity objective is rating MSE. Joint training adds annotation cross-entropy with weight 0.2. The control reassigns annotation records between training cases. The arms use the same initial weights and sampled passage pairs.

The scripted Spanish passages cover reparations, harm, sanctions and restoration. There are 384 training pairs, 216 development pairs and 672 test pairs. Whole cases remain within one split. Two composed questions appear only in the test set. Their component attributes appear in training.

## Results

| Arm | Test MSE | Spearman | Composed MSE |
| --- | ---: | ---: | ---: |
| Similarity training | 0.079142 | 0.251436 | 0.074267 |
| Joint training | 0.061421 | 0.332900 | 0.051984 |
| Shuffled annotations | 0.061475 | 0.295159 | 0.048026 |

The mean rating predictor had the lowest test MSE. Joint training had the lowest MSE among the trained arms.

A reference predictor assigns the mean training rating, 0.75, to every test pair. Its test MSE is 0.053571.

These results cover one seed on scripted passages. Expert review of testimony will determine whether the learned distinctions help with the JEP task. The annotation weight and step count were fixed for this pilot.

## Records

`gpu_pilot_results.json` includes scores by subject category. `gpu_pilot_evidence` contains predictions, training traces and measurement logs. `gpu_pilot_summary.json` identifies the native records and checkpoints on `rico-source-l4-uswest4c` at `/home/machina/jep-joint-pilot-20261020`. `gpu_runtime_requirements.txt` records the installed dependencies.

Source commit: `a1fb72c32d9f18af1d1c6a75d198ca01a2d189ea`. The pinned model and VIPER revisions are recorded in `gpu_pilot_results.json`.
