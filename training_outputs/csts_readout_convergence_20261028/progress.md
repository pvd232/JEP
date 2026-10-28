# JEP readouts trained to a validation plateau

The nine seed and learning rate candidates are split across two L4s and an A100. Learning rates are selected across all three seeds after their fits complete. Each fitting epoch queues an immutable VIPER Cloud snapshot. Each worker verifies its first snapshot by restoring it from Cloud. Native event times below are UTC.

| Seed | GPU | Last reported status | Sealed checkpoint receipts |
| --- | --- | --- | --- |
| 7 | L4 | running | 22 |
| 8 | A100 | running | 16 |
| 9 | L4 | running | 11 |

## Seed 7

# JEP convergence worker, seed 7

Hardware: NVIDIA L4. Source: `bf167d773df10cf097a3be7e5966b69c299d9227`.

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 17:20:29 | stage started | 7 |  | name: All three learning rates |
| 2026-10-28 17:21:27 | candidate started | 7 |  | name: B/C rate 1e-05 |
| 2026-10-28 17:21:48 | readout epoch | 7 | 1 | B validation rho 0.696972, MSE 0.084140; C validation rho 0.615708, MSE 0.103737; learning_rate: 1e-05 |
| 2026-10-28 17:22:00 | checkpoint published | 7 | 1 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00001; status: sealed |
| 2026-10-28 17:22:08 | readout epoch | 7 | 2 | B validation rho 0.720475, MSE 0.079155; C validation rho 0.641987, MSE 0.097119; learning_rate: 1e-05 |
| 2026-10-28 17:22:17 | checkpoint published | 7 | 2 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00002; status: sealed |
| 2026-10-28 17:22:17 | readout epoch | 7 | 3 | B validation rho 0.726609, MSE 0.076817; C validation rho 0.640944, MSE 0.097737; learning_rate: 1e-05 |
| 2026-10-28 17:22:25 | checkpoint published | 7 | 3 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00003; status: sealed |
| 2026-10-28 17:22:27 | readout epoch | 7 | 4 | B validation rho 0.729102, MSE 0.075328; C validation rho 0.620914, MSE 0.099330; learning_rate: 1e-05 |
| 2026-10-28 17:22:35 | checkpoint published | 7 | 4 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00004; status: sealed |
| 2026-10-28 17:22:36 | readout epoch | 7 | 5 | B validation rho 0.735578, MSE 0.075218; C validation rho 0.640365, MSE 0.095219; learning_rate: 1e-05 |
| 2026-10-28 17:22:43 | checkpoint published | 7 | 5 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00005; status: sealed |
| 2026-10-28 17:22:45 | readout epoch | 7 | 6 | B validation rho 0.722256, MSE 0.074982; C validation rho 0.616316, MSE 0.099007; learning_rate: 1e-05 |
| 2026-10-28 17:22:53 | checkpoint published | 7 | 6 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00006; status: sealed |
| 2026-10-28 17:22:55 | readout epoch | 7 | 7 | B validation rho 0.713706, MSE 0.075870; C validation rho 0.621261, MSE 0.098527; learning_rate: 1e-05 |
| 2026-10-28 17:23:03 | checkpoint published | 7 | 7 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00007; status: sealed |
| 2026-10-28 17:23:04 | readout epoch | 7 | 8 | B validation rho 0.714652, MSE 0.075614; C validation rho 0.630864, MSE 0.094679; learning_rate: 1e-05 |
| 2026-10-28 17:23:11 | checkpoint published | 7 | 8 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00008; status: sealed |
| 2026-10-28 17:23:13 | readout epoch | 7 | 9 | B validation rho 0.728641, MSE 0.075590; C validation rho 0.641289, MSE 0.093302; learning_rate: 1e-05 |
| 2026-10-28 17:23:21 | checkpoint published | 7 | 9 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00009; status: sealed |
| 2026-10-28 17:23:23 | readout epoch | 7 | 10 | B validation rho 0.706518, MSE 0.076663; C validation rho 0.611480, MSE 0.099629; learning_rate: 1e-05 |
| 2026-10-28 17:23:30 | checkpoint published | 7 | 10 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00010; status: sealed |
| 2026-10-28 17:23:32 | readout epoch | 7 | 11 | B validation rho 0.716403, MSE 0.076516; C validation rho 0.623584, MSE 0.095874; learning_rate: 1e-05 |
| 2026-10-28 17:23:39 | checkpoint published | 7 | 11 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00011; status: sealed |
| 2026-10-28 17:23:42 | readout epoch | 7 | 12 | B validation rho 0.711478, MSE 0.077471; C validation rho 0.622241, MSE 0.095366; learning_rate: 1e-05 |
| 2026-10-28 17:23:49 | checkpoint published | 7 | 12 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00012; status: sealed |
| 2026-10-28 17:23:51 | readout epoch | 7 | 13 | B validation rho 0.717194, MSE 0.077688; C validation rho 0.625806, MSE 0.096020; learning_rate: 1e-05 |
| 2026-10-28 17:23:58 | checkpoint published | 7 | 13 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00013; status: sealed |
| 2026-10-28 17:24:00 | readout epoch | 7 | 14 | B validation rho 0.695657, MSE 0.078855; C validation rho 0.618332, MSE 0.096229; learning_rate: 1e-05 |
| 2026-10-28 17:24:07 | checkpoint published | 7 | 14 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00014; status: sealed |
| 2026-10-28 17:24:09 | readout epoch | 7 | 15 | B validation rho 0.693388, MSE 0.079198; C validation rho 0.613120, MSE 0.098504; learning_rate: 1e-05 |
| 2026-10-28 17:24:10 | candidate finished | 7 |  | name: B/C rate 1e-05; epochs 15; selected {'ratings': 5, 'evidence': 2}; status: joint_validation_patience |
| 2026-10-28 17:24:10 | candidate started | 7 |  | name: B/C rate 3e-05 |
| 2026-10-28 17:24:17 | checkpoint published | 7 | 15 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00015; status: sealed |
| 2026-10-28 17:24:25 | checkpoint published | 7 |  | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00016; status: sealed |
| 2026-10-28 17:24:30 | readout epoch | 7 | 1 | B validation rho 0.730484, MSE 0.079059; C validation rho 0.662696, MSE 0.092175; learning_rate: 3e-05 |
| 2026-10-28 17:24:38 | checkpoint published | 7 | 1 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00017; status: sealed |
| 2026-10-28 17:24:39 | readout epoch | 7 | 2 | B validation rho 0.726434, MSE 0.074215; C validation rho 0.628617, MSE 0.097233; learning_rate: 3e-05 |
| 2026-10-28 17:24:47 | checkpoint published | 7 | 2 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00018; status: sealed |
| 2026-10-28 17:24:48 | readout epoch | 7 | 3 | B validation rho 0.734993, MSE 0.073928; C validation rho 0.657003, MSE 0.089840; learning_rate: 3e-05 |
| 2026-10-28 17:24:56 | checkpoint published | 7 | 3 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00019; status: sealed |
| 2026-10-28 17:24:58 | readout epoch | 7 | 4 | B validation rho 0.734922, MSE 0.075054; C validation rho 0.621612, MSE 0.101373; learning_rate: 3e-05 |
| 2026-10-28 17:25:05 | checkpoint published | 7 | 4 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00020; status: sealed |
| 2026-10-28 17:25:08 | readout epoch | 7 | 5 | B validation rho 0.731127, MSE 0.074162; C validation rho 0.639838, MSE 0.093909; learning_rate: 3e-05 |
| 2026-10-28 17:25:15 | checkpoint published | 7 | 5 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00021; status: sealed |
| 2026-10-28 17:25:17 | readout epoch | 7 | 6 | B validation rho 0.721680, MSE 0.076366; C validation rho 0.626218, MSE 0.094115; learning_rate: 3e-05 |
| 2026-10-28 17:25:25 | checkpoint published | 7 | 6 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00022; status: sealed |


## Seed 8

# JEP convergence worker, seed 8

Hardware: NVIDIA A100-SXM4-40GB. Source: `bf167d773df10cf097a3be7e5966b69c299d9227`.

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 17:21:50 | stage started | 8 |  | name: All three learning rates |
| 2026-10-28 17:22:50 | candidate started | 8 |  | name: B/C rate 1e-05 |
| 2026-10-28 17:23:09 | readout epoch | 8 | 1 | B validation rho 0.676910, MSE 0.084044; C validation rho 0.607738, MSE 0.103487; learning_rate: 1e-05 |
| 2026-10-28 17:23:12 | checkpoint published | 8 | 1 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00001; status: sealed |
| 2026-10-28 17:23:20 | readout epoch | 8 | 2 | B validation rho 0.705219, MSE 0.079312; C validation rho 0.627848, MSE 0.098587; learning_rate: 1e-05 |
| 2026-10-28 17:23:22 | checkpoint published | 8 | 2 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00002; status: sealed |
| 2026-10-28 17:23:28 | readout epoch | 8 | 3 | B validation rho 0.722791, MSE 0.078187; C validation rho 0.665031, MSE 0.089537; learning_rate: 1e-05 |
| 2026-10-28 17:23:30 | checkpoint published | 8 | 3 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00003; status: sealed |
| 2026-10-28 17:23:37 | readout epoch | 8 | 4 | B validation rho 0.724785, MSE 0.076231; C validation rho 0.645167, MSE 0.094510; learning_rate: 1e-05 |
| 2026-10-28 17:23:38 | checkpoint published | 8 | 4 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00004; status: sealed |
| 2026-10-28 17:23:45 | readout epoch | 8 | 5 | B validation rho 0.725567, MSE 0.075304; C validation rho 0.653059, MSE 0.092543; learning_rate: 1e-05 |
| 2026-10-28 17:23:47 | checkpoint published | 8 | 5 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00005; status: sealed |
| 2026-10-28 17:23:54 | readout epoch | 8 | 6 | B validation rho 0.719684, MSE 0.076525; C validation rho 0.644301, MSE 0.095677; learning_rate: 1e-05 |
| 2026-10-28 17:23:55 | checkpoint published | 8 | 6 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00006; status: sealed |
| 2026-10-28 17:24:02 | readout epoch | 8 | 7 | B validation rho 0.709993, MSE 0.076022; C validation rho 0.649024, MSE 0.093532; learning_rate: 1e-05 |
| 2026-10-28 17:24:04 | checkpoint published | 8 | 7 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00007; status: sealed |
| 2026-10-28 17:24:11 | readout epoch | 8 | 8 | B validation rho 0.715777, MSE 0.075126; C validation rho 0.638068, MSE 0.096513; learning_rate: 1e-05 |
| 2026-10-28 17:24:13 | checkpoint published | 8 | 8 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00008; status: sealed |
| 2026-10-28 17:24:19 | readout epoch | 8 | 9 | B validation rho 0.719012, MSE 0.074773; C validation rho 0.632438, MSE 0.096297; learning_rate: 1e-05 |
| 2026-10-28 17:24:21 | checkpoint published | 8 | 9 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00009; status: sealed |
| 2026-10-28 17:24:28 | readout epoch | 8 | 10 | B validation rho 0.716390, MSE 0.075377; C validation rho 0.634745, MSE 0.094500; learning_rate: 1e-05 |
| 2026-10-28 17:24:29 | checkpoint published | 8 | 10 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00010; status: sealed |
| 2026-10-28 17:24:36 | readout epoch | 8 | 11 | B validation rho 0.713133, MSE 0.075542; C validation rho 0.631075, MSE 0.094554; learning_rate: 1e-05 |
| 2026-10-28 17:24:38 | checkpoint published | 8 | 11 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00011; status: sealed |
| 2026-10-28 17:24:45 | readout epoch | 8 | 12 | B validation rho 0.711137, MSE 0.075594; C validation rho 0.623394, MSE 0.099147; learning_rate: 1e-05 |
| 2026-10-28 17:24:46 | checkpoint published | 8 | 12 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00012; status: sealed |
| 2026-10-28 17:24:53 | readout epoch | 8 | 13 | B validation rho 0.714449, MSE 0.075873; C validation rho 0.634141, MSE 0.094310; learning_rate: 1e-05 |
| 2026-10-28 17:24:55 | checkpoint published | 8 | 13 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00013; status: sealed |
| 2026-10-28 17:25:02 | readout epoch | 8 | 14 | B validation rho 0.712472, MSE 0.075459; C validation rho 0.624543, MSE 0.095978; learning_rate: 1e-05 |
| 2026-10-28 17:25:03 | checkpoint published | 8 | 14 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00014; status: sealed |
| 2026-10-28 17:25:10 | readout epoch | 8 | 15 | B validation rho 0.710331, MSE 0.075930; C validation rho 0.641825, MSE 0.092979; learning_rate: 1e-05 |
| 2026-10-28 17:25:11 | candidate finished | 8 |  | name: B/C rate 1e-05; epochs 15; selected {'ratings': 5, 'evidence': 3}; status: joint_validation_patience |
| 2026-10-28 17:25:11 | candidate started | 8 |  | name: B/C rate 3e-05 |
| 2026-10-28 17:25:12 | checkpoint published | 8 | 15 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00015; status: sealed |
| 2026-10-28 17:25:14 | checkpoint published | 8 |  | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00016; status: sealed |


## Seed 9

# JEP convergence worker, seed 9

Hardware: NVIDIA L4. Source: `bf167d773df10cf097a3be7e5966b69c299d9227`.

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 17:21:53 | stage started | 9 |  | name: All three learning rates |
| 2026-10-28 17:22:53 | candidate started | 9 |  | name: B/C rate 1e-05 |
| 2026-10-28 17:23:12 | readout epoch | 9 | 1 | B validation rho 0.693479, MSE 0.084003; C validation rho 0.637041, MSE 0.095527; learning_rate: 1e-05 |
| 2026-10-28 17:23:27 | checkpoint published | 9 | 1 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00001; status: sealed |
| 2026-10-28 17:23:36 | readout epoch | 9 | 2 | B validation rho 0.714845, MSE 0.079174; C validation rho 0.635311, MSE 0.096600; learning_rate: 1e-05 |
| 2026-10-28 17:23:44 | readout epoch | 9 | 3 | B validation rho 0.725735, MSE 0.077321; C validation rho 0.649364, MSE 0.091983; learning_rate: 1e-05 |
| 2026-10-28 17:23:46 | checkpoint published | 9 | 2 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00002; status: sealed |
| 2026-10-28 17:23:53 | readout epoch | 9 | 4 | B validation rho 0.720482, MSE 0.078189; C validation rho 0.631498, MSE 0.098227; learning_rate: 1e-05 |
| 2026-10-28 17:23:55 | checkpoint published | 9 | 3 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00003; status: sealed |
| 2026-10-28 17:24:01 | readout epoch | 9 | 5 | B validation rho 0.711324, MSE 0.077153; C validation rho 0.644007, MSE 0.092146; learning_rate: 1e-05 |
| 2026-10-28 17:24:06 | checkpoint published | 9 | 4 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00004; status: sealed |
| 2026-10-28 17:24:10 | readout epoch | 9 | 6 | B validation rho 0.719536, MSE 0.076794; C validation rho 0.655095, MSE 0.090692; learning_rate: 1e-05 |
| 2026-10-28 17:24:15 | checkpoint published | 9 | 5 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00005; status: sealed |
| 2026-10-28 17:24:19 | readout epoch | 9 | 7 | B validation rho 0.720569, MSE 0.076596; C validation rho 0.645132, MSE 0.092962; learning_rate: 1e-05 |
| 2026-10-28 17:24:26 | checkpoint published | 9 | 6 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00006; status: sealed |
| 2026-10-28 17:24:27 | readout epoch | 9 | 8 | B validation rho 0.710947, MSE 0.076546; C validation rho 0.629292, MSE 0.095506; learning_rate: 1e-05 |
| 2026-10-28 17:24:35 | checkpoint published | 9 | 7 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00007; status: sealed |
| 2026-10-28 17:24:36 | readout epoch | 9 | 9 | B validation rho 0.716364, MSE 0.076455; C validation rho 0.642119, MSE 0.092977; learning_rate: 1e-05 |
| 2026-10-28 17:24:45 | readout epoch | 9 | 10 | B validation rho 0.709803, MSE 0.076633; C validation rho 0.620772, MSE 0.097613; learning_rate: 1e-05 |
| 2026-10-28 17:24:45 | checkpoint published | 9 | 8 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00008; status: sealed |
| 2026-10-28 17:24:53 | readout epoch | 9 | 11 | B validation rho 0.704724, MSE 0.077034; C validation rho 0.605630, MSE 0.101129; learning_rate: 1e-05 |
| 2026-10-28 17:24:56 | checkpoint published | 9 | 9 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00009; status: sealed |
| 2026-10-28 17:25:02 | readout epoch | 9 | 12 | B validation rho 0.711496, MSE 0.077358; C validation rho 0.614272, MSE 0.098619; learning_rate: 1e-05 |
| 2026-10-28 17:25:06 | checkpoint published | 9 | 10 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00010; status: sealed |
| 2026-10-28 17:25:11 | readout epoch | 9 | 13 | B validation rho 0.709559, MSE 0.077361; C validation rho 0.623034, MSE 0.095762; learning_rate: 1e-05 |
| 2026-10-28 17:25:16 | checkpoint published | 9 | 11 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00011; status: sealed |


<details>
<summary>Earlier interrupted A100 attempt</summary>

# JEP full readout training

**Status checked October 28 at 11:47 a.m. New York time: interrupted.**

Colab no longer lists the A100 assignment. Its disappearance has no established cause. The last streamed measurement was seed 9, epoch 1, at 11:01 a.m. Native Cloud receipts confirm that both feature caches are published. A complete inventory of this experiment's VIPER Cloud workspace found no published fitting run or fitting checkpoint. The controller queued publication after the full fitting stage; intermediate checkpoints remained on the runtime. A replacement A100 request timed out, and fitting has not restarted.

The next launch requires verified Cloud publication of fitting checkpoints during training. The measurements below preserve the interrupted attempt.


| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 14:45:58 | inputs restored |  |  | name: All seven required inputs restored and hash verified from VIPER Cloud |
| 2026-10-28 14:45:59 | stage started |  |  | name: extract_training_proposition_final |
| 2026-10-28 14:46:42 | readout extraction |  |  | split: training; 4/12102 |
| 2026-10-28 14:46:47 | readout extraction |  |  | split: training; 204/12102 |
| 2026-10-28 14:46:52 | readout extraction |  |  | split: training; 404/12102 |
| 2026-10-28 14:46:57 | readout extraction |  |  | split: training; 604/12102 |
| 2026-10-28 14:47:01 | readout extraction |  |  | split: training; 804/12102 |
| 2026-10-28 14:47:06 | readout extraction |  |  | split: training; 1004/12102 |
| 2026-10-28 14:47:11 | readout extraction |  |  | split: training; 1204/12102 |
| 2026-10-28 14:47:16 | readout extraction |  |  | split: training; 1404/12102 |
| 2026-10-28 14:47:21 | readout extraction |  |  | split: training; 1604/12102 |
| 2026-10-28 14:47:26 | readout extraction |  |  | split: training; 1804/12102 |
| 2026-10-28 14:47:31 | readout extraction |  |  | split: training; 2004/12102 |
| 2026-10-28 14:47:35 | readout extraction |  |  | split: training; 2204/12102 |
| 2026-10-28 14:47:40 | readout extraction |  |  | split: training; 2404/12102 |
| 2026-10-28 14:47:45 | readout extraction |  |  | split: training; 2604/12102 |
| 2026-10-28 14:47:50 | readout extraction |  |  | split: training; 2804/12102 |
| 2026-10-28 14:47:55 | readout extraction |  |  | split: training; 3004/12102 |
| 2026-10-28 14:48:00 | readout extraction |  |  | split: training; 3204/12102 |
| 2026-10-28 14:48:05 | readout extraction |  |  | split: training; 3404/12102 |
| 2026-10-28 14:48:10 | readout extraction |  |  | split: training; 3604/12102 |
| 2026-10-28 14:48:14 | readout extraction |  |  | split: training; 3804/12102 |
| 2026-10-28 14:48:19 | readout extraction |  |  | split: training; 4004/12102 |
| 2026-10-28 14:48:24 | readout extraction |  |  | split: training; 4204/12102 |
| 2026-10-28 14:48:29 | readout extraction |  |  | split: training; 4404/12102 |
| 2026-10-28 14:48:34 | readout extraction |  |  | split: training; 4604/12102 |
| 2026-10-28 14:48:39 | readout extraction |  |  | split: training; 4804/12102 |
| 2026-10-28 14:48:44 | readout extraction |  |  | split: training; 5004/12102 |
| 2026-10-28 14:48:49 | readout extraction |  |  | split: training; 5204/12102 |
| 2026-10-28 14:48:54 | readout extraction |  |  | split: training; 5404/12102 |
| 2026-10-28 14:48:59 | readout extraction |  |  | split: training; 5604/12102 |
| 2026-10-28 14:49:04 | readout extraction |  |  | split: training; 5804/12102 |
| 2026-10-28 14:49:08 | readout extraction |  |  | split: training; 6004/12102 |
| 2026-10-28 14:49:13 | readout extraction |  |  | split: training; 6204/12102 |
| 2026-10-28 14:49:18 | readout extraction |  |  | split: training; 6404/12102 |
| 2026-10-28 14:49:23 | readout extraction |  |  | split: training; 6604/12102 |
| 2026-10-28 14:49:28 | readout extraction |  |  | split: training; 6804/12102 |
| 2026-10-28 14:49:33 | readout extraction |  |  | split: training; 7004/12102 |
| 2026-10-28 14:49:38 | readout extraction |  |  | split: training; 7204/12102 |
| 2026-10-28 14:49:43 | readout extraction |  |  | split: training; 7404/12102 |
| 2026-10-28 14:49:48 | readout extraction |  |  | split: training; 7604/12102 |
| 2026-10-28 14:49:53 | readout extraction |  |  | split: training; 7804/12102 |
| 2026-10-28 14:49:57 | readout extraction |  |  | split: training; 8004/12102 |
| 2026-10-28 14:50:02 | readout extraction |  |  | split: training; 8204/12102 |
| 2026-10-28 14:50:07 | readout extraction |  |  | split: training; 8404/12102 |
| 2026-10-28 14:50:12 | readout extraction |  |  | split: training; 8604/12102 |
| 2026-10-28 14:50:17 | readout extraction |  |  | split: training; 8804/12102 |
| 2026-10-28 14:50:22 | readout extraction |  |  | split: training; 9004/12102 |
| 2026-10-28 14:50:26 | readout extraction |  |  | split: training; 9204/12102 |
| 2026-10-28 14:50:31 | readout extraction |  |  | split: training; 9404/12102 |
| 2026-10-28 14:50:36 | readout extraction |  |  | split: training; 9604/12102 |
| 2026-10-28 14:50:41 | readout extraction |  |  | split: training; 9804/12102 |
| 2026-10-28 14:50:46 | readout extraction |  |  | split: training; 10004/12102 |
| 2026-10-28 14:50:51 | readout extraction |  |  | split: training; 10204/12102 |
| 2026-10-28 14:50:56 | readout extraction |  |  | split: training; 10404/12102 |
| 2026-10-28 14:51:01 | readout extraction |  |  | split: training; 10604/12102 |
| 2026-10-28 14:51:05 | readout extraction |  |  | split: training; 10804/12102 |
| 2026-10-28 14:51:10 | readout extraction |  |  | split: training; 11004/12102 |
| 2026-10-28 14:51:15 | readout extraction |  |  | split: training; 11204/12102 |
| 2026-10-28 14:51:20 | readout extraction |  |  | split: training; 11404/12102 |
| 2026-10-28 14:51:25 | readout extraction |  |  | split: training; 11604/12102 |
| 2026-10-28 14:51:30 | readout extraction |  |  | split: training; 11804/12102 |
| 2026-10-28 14:51:35 | readout extraction |  |  | split: training; 12004/12102 |
| 2026-10-28 14:51:37 | readout extraction |  |  | split: training; 12102/12102 |
| 2026-10-28 14:52:28 | stage finished |  |  | name: extract_training_proposition_final; status: succeeded |
| 2026-10-28 14:52:28 | stage started |  |  | name: extract_validation_proposition_final |
| 2026-10-28 14:53:12 | readout extraction |  |  | split: validation; 4/3152 |
| 2026-10-28 14:53:18 | readout extraction |  |  | split: validation; 204/3152 |
| 2026-10-28 14:53:23 | readout extraction |  |  | split: validation; 404/3152 |
| 2026-10-28 14:53:27 | readout extraction |  |  | split: validation; 604/3152 |
| 2026-10-28 14:53:32 | readout extraction |  |  | split: validation; 804/3152 |
| 2026-10-28 14:53:37 | readout extraction |  |  | split: validation; 1004/3152 |
| 2026-10-28 14:53:43 | readout extraction |  |  | split: validation; 1204/3152 |
| 2026-10-28 14:53:48 | readout extraction |  |  | split: validation; 1404/3152 |
| 2026-10-28 14:53:53 | readout extraction |  |  | split: validation; 1604/3152 |
| 2026-10-28 14:53:57 | readout extraction |  |  | split: validation; 1804/3152 |
| 2026-10-28 14:54:02 | readout extraction |  |  | split: validation; 2004/3152 |
| 2026-10-28 14:54:07 | readout extraction |  |  | split: validation; 2204/3152 |
| 2026-10-28 14:54:12 | readout extraction |  |  | split: validation; 2404/3152 |
| 2026-10-28 14:54:17 | readout extraction |  |  | split: validation; 2604/3152 |
| 2026-10-28 14:54:22 | readout extraction |  |  | split: validation; 2804/3152 |
| 2026-10-28 14:54:26 | readout extraction |  |  | split: validation; 3004/3152 |
| 2026-10-28 14:54:30 | readout extraction |  |  | split: validation; 3152/3152 |
| 2026-10-28 14:54:51 | stage finished |  |  | name: extract_validation_proposition_final; status: succeeded |
| 2026-10-28 14:54:51 | cache recovery complete |  |  | name: Training and validation caches ready; native VIPER Cloud uploads queued |
# JEP readouts trained to a validation plateau

Source: `a79373d07b0dd7570ce4346edb758a6efb9d3611`. Hardware: NVIDIA A100-SXM4-40GB.

Rates: 0.00001, 0.00003, 0.0001. Seeds: 7, 8, 9. Select one rate per objective by mean best validation Spearman. Continue until ten epochs pass without validation improvement. An epoch ceiling is reported as an incomplete fit.

Fit D, E and the same comparison on A's final vectors after selecting B/C. Qwen stays frozen. Sentence vectors retain all 4,096 coordinates.

## Progress

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 14:55:10 | stage started |  |  | name: fit |
| 2026-10-28 14:56:00 | candidate started | 7 |  | name: B/C rate 1e-05 |
| 2026-10-28 14:56:20 | readout epoch | 7 | 1 | B validation rho 0.696973, MSE 0.084140; C validation rho 0.615708, MSE 0.103737; learning_rate: 1e-05 |
| 2026-10-28 14:56:29 | readout epoch | 7 | 2 | B validation rho 0.720475, MSE 0.079155; C validation rho 0.641987, MSE 0.097119; learning_rate: 1e-05 |
| 2026-10-28 14:56:37 | readout epoch | 7 | 3 | B validation rho 0.726609, MSE 0.076817; C validation rho 0.640944, MSE 0.097737; learning_rate: 1e-05 |
| 2026-10-28 14:56:46 | readout epoch | 7 | 4 | B validation rho 0.729102, MSE 0.075328; C validation rho 0.620914, MSE 0.099330; learning_rate: 1e-05 |
| 2026-10-28 14:56:55 | readout epoch | 7 | 5 | B validation rho 0.735578, MSE 0.075218; C validation rho 0.640365, MSE 0.095219; learning_rate: 1e-05 |
| 2026-10-28 14:57:03 | readout epoch | 7 | 6 | B validation rho 0.722256, MSE 0.074982; C validation rho 0.616316, MSE 0.099007; learning_rate: 1e-05 |
| 2026-10-28 14:57:12 | readout epoch | 7 | 7 | B validation rho 0.713706, MSE 0.075870; C validation rho 0.621261, MSE 0.098527; learning_rate: 1e-05 |
| 2026-10-28 14:57:21 | readout epoch | 7 | 8 | B validation rho 0.714652, MSE 0.075614; C validation rho 0.630864, MSE 0.094679; learning_rate: 1e-05 |
| 2026-10-28 14:57:29 | readout epoch | 7 | 9 | B validation rho 0.728641, MSE 0.075590; C validation rho 0.641289, MSE 0.093302; learning_rate: 1e-05 |
| 2026-10-28 14:57:38 | readout epoch | 7 | 10 | B validation rho 0.706518, MSE 0.076663; C validation rho 0.611480, MSE 0.099629; learning_rate: 1e-05 |
| 2026-10-28 14:57:47 | readout epoch | 7 | 11 | B validation rho 0.716403, MSE 0.076516; C validation rho 0.623584, MSE 0.095874; learning_rate: 1e-05 |
| 2026-10-28 14:57:55 | readout epoch | 7 | 12 | B validation rho 0.711478, MSE 0.077471; C validation rho 0.622241, MSE 0.095366; learning_rate: 1e-05 |
| 2026-10-28 14:58:04 | readout epoch | 7 | 13 | B validation rho 0.717194, MSE 0.077688; C validation rho 0.625807, MSE 0.096020; learning_rate: 1e-05 |
| 2026-10-28 14:58:12 | readout epoch | 7 | 14 | B validation rho 0.695657, MSE 0.078855; C validation rho 0.618332, MSE 0.096229; learning_rate: 1e-05 |
| 2026-10-28 14:58:21 | readout epoch | 7 | 15 | B validation rho 0.693388, MSE 0.079198; C validation rho 0.613120, MSE 0.098504; learning_rate: 1e-05 |
| 2026-10-28 14:58:22 | candidate finished | 7 |  | name: B/C rate 1e-05; epochs 15; selected {'ratings': 5, 'evidence': 2}; status: joint_validation_patience |
| 2026-10-28 14:58:22 | candidate started | 8 |  | name: B/C rate 1e-05 |
| 2026-10-28 14:58:40 | readout epoch | 8 | 1 | B validation rho 0.676910, MSE 0.084044; C validation rho 0.607738, MSE 0.103487; learning_rate: 1e-05 |
| 2026-10-28 14:58:49 | readout epoch | 8 | 2 | B validation rho 0.705219, MSE 0.079312; C validation rho 0.627848, MSE 0.098587; learning_rate: 1e-05 |
| 2026-10-28 14:58:58 | readout epoch | 8 | 3 | B validation rho 0.722791, MSE 0.078187; C validation rho 0.665031, MSE 0.089537; learning_rate: 1e-05 |
| 2026-10-28 14:59:07 | readout epoch | 8 | 4 | B validation rho 0.724785, MSE 0.076231; C validation rho 0.645167, MSE 0.094510; learning_rate: 1e-05 |
| 2026-10-28 14:59:16 | readout epoch | 8 | 5 | B validation rho 0.725567, MSE 0.075304; C validation rho 0.653059, MSE 0.092543; learning_rate: 1e-05 |
| 2026-10-28 14:59:25 | readout epoch | 8 | 6 | B validation rho 0.719684, MSE 0.076525; C validation rho 0.644301, MSE 0.095677; learning_rate: 1e-05 |
| 2026-10-28 14:59:34 | readout epoch | 8 | 7 | B validation rho 0.709993, MSE 0.076022; C validation rho 0.649024, MSE 0.093532; learning_rate: 1e-05 |
| 2026-10-28 14:59:43 | readout epoch | 8 | 8 | B validation rho 0.715777, MSE 0.075126; C validation rho 0.638068, MSE 0.096513; learning_rate: 1e-05 |
| 2026-10-28 14:59:52 | readout epoch | 8 | 9 | B validation rho 0.719012, MSE 0.074773; C validation rho 0.632438, MSE 0.096297; learning_rate: 1e-05 |
| 2026-10-28 15:00:01 | readout epoch | 8 | 10 | B validation rho 0.716390, MSE 0.075377; C validation rho 0.634745, MSE 0.094500; learning_rate: 1e-05 |
| 2026-10-28 15:00:10 | readout epoch | 8 | 11 | B validation rho 0.713133, MSE 0.075542; C validation rho 0.631075, MSE 0.094554; learning_rate: 1e-05 |
| 2026-10-28 15:00:19 | readout epoch | 8 | 12 | B validation rho 0.711137, MSE 0.075594; C validation rho 0.623394, MSE 0.099147; learning_rate: 1e-05 |
| 2026-10-28 15:00:28 | readout epoch | 8 | 13 | B validation rho 0.714449, MSE 0.075873; C validation rho 0.634141, MSE 0.094310; learning_rate: 1e-05 |
| 2026-10-28 15:00:37 | readout epoch | 8 | 14 | B validation rho 0.712472, MSE 0.075459; C validation rho 0.624543, MSE 0.095978; learning_rate: 1e-05 |
| 2026-10-28 15:00:46 | readout epoch | 8 | 15 | B validation rho 0.710331, MSE 0.075930; C validation rho 0.641825, MSE 0.092979; learning_rate: 1e-05 |
| 2026-10-28 15:00:46 | candidate finished | 8 |  | name: B/C rate 1e-05; epochs 15; selected {'ratings': 5, 'evidence': 3}; status: joint_validation_patience |
| 2026-10-28 15:00:46 | candidate started | 9 |  | name: B/C rate 1e-05 |
| 2026-10-28 15:01:05 | readout epoch | 9 | 1 | B validation rho 0.693479, MSE 0.084003; C validation rho 0.637041, MSE 0.095527; learning_rate: 1e-05 |


</details>
