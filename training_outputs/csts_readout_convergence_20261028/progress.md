# JEP readouts trained to a validation plateau

The nine seed and learning rate candidates are split across two L4s and an A100. Learning rates are selected across all three seeds after their fits complete. Each fitting epoch queues an immutable VIPER Cloud snapshot. Each worker verifies its first snapshot by restoring it from Cloud. Native event times below are UTC.

| Seed | GPU | Last reported status | Sealed checkpoint receipts |
| --- | --- | --- | --- |
| 7 | L4 | published | 43 |
| 8 | A100 | published | 44 |
| 9 | L4 | published | 41 |

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
| 2026-10-28 17:25:26 | readout epoch | 7 | 7 | B validation rho 0.713434, MSE 0.076262; C validation rho 0.603906, MSE 0.100264; learning_rate: 3e-05 |
| 2026-10-28 17:25:34 | checkpoint published | 7 | 7 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00023; status: sealed |
| 2026-10-28 17:25:36 | readout epoch | 7 | 8 | B validation rho 0.700352, MSE 0.077010; C validation rho 0.623078, MSE 0.094651; learning_rate: 3e-05 |
| 2026-10-28 17:25:43 | checkpoint published | 7 | 8 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00024; status: sealed |
| 2026-10-28 17:25:45 | readout epoch | 7 | 9 | B validation rho 0.708585, MSE 0.077775; C validation rho 0.622264, MSE 0.096380; learning_rate: 3e-05 |
| 2026-10-28 17:25:54 | checkpoint published | 7 | 9 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00025; status: sealed |
| 2026-10-28 17:25:55 | readout epoch | 7 | 10 | B validation rho 0.697624, MSE 0.078282; C validation rho 0.571147, MSE 0.106679; learning_rate: 3e-05 |
| 2026-10-28 17:26:02 | checkpoint published | 7 | 10 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00026; status: sealed |
| 2026-10-28 17:26:04 | readout epoch | 7 | 11 | B validation rho 0.694802, MSE 0.079386; C validation rho 0.598761, MSE 0.098918; learning_rate: 3e-05 |
| 2026-10-28 17:26:13 | checkpoint published | 7 | 11 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00027; status: sealed |
| 2026-10-28 17:26:14 | readout epoch | 7 | 12 | B validation rho 0.674713, MSE 0.081714; C validation rho 0.591269, MSE 0.099957; learning_rate: 3e-05 |
| 2026-10-28 17:26:22 | checkpoint published | 7 | 12 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00028; status: sealed |
| 2026-10-28 17:26:23 | readout epoch | 7 | 13 | B validation rho 0.672764, MSE 0.082144; C validation rho 0.587658, MSE 0.101774; learning_rate: 3e-05 |
| 2026-10-28 17:26:24 | candidate finished | 7 |  | name: B/C rate 3e-05; epochs 13; selected {'ratings': 3, 'evidence': 1}; status: joint_validation_patience |
| 2026-10-28 17:26:24 | candidate started | 7 |  | name: B/C rate 0.0001 |
| 2026-10-28 17:26:31 | checkpoint published | 7 | 13 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00029; status: sealed |
| 2026-10-28 17:26:41 | checkpoint published | 7 |  | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00030; status: sealed |
| 2026-10-28 17:26:44 | readout epoch | 7 | 1 | B validation rho 0.739195, MSE 0.076475; C validation rho 0.601113, MSE 0.105208; learning_rate: 0.0001 |
| 2026-10-28 17:26:52 | checkpoint published | 7 | 1 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00031; status: sealed |
| 2026-10-28 17:26:54 | readout epoch | 7 | 2 | B validation rho 0.701421, MSE 0.076822; C validation rho 0.646660, MSE 0.088515; learning_rate: 0.0001 |
| 2026-10-28 17:27:02 | checkpoint published | 7 | 2 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00032; status: sealed |
| 2026-10-28 17:27:04 | readout epoch | 7 | 3 | B validation rho 0.732811, MSE 0.078914; C validation rho 0.624863, MSE 0.093064; learning_rate: 0.0001 |
| 2026-10-28 17:27:13 | readout epoch | 7 | 4 | B validation rho 0.703517, MSE 0.078225; C validation rho 0.581323, MSE 0.101259; learning_rate: 0.0001 |
| 2026-10-28 17:27:14 | checkpoint published | 7 | 3 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00033; status: sealed |
| 2026-10-28 17:27:22 | checkpoint published | 7 | 4 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00034; status: sealed |
| 2026-10-28 17:27:23 | readout epoch | 7 | 5 | B validation rho 0.723880, MSE 0.076977; C validation rho 0.541081, MSE 0.111756; learning_rate: 0.0001 |
| 2026-10-28 17:27:31 | checkpoint published | 7 | 5 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00035; status: sealed |
| 2026-10-28 17:27:32 | readout epoch | 7 | 6 | B validation rho 0.711836, MSE 0.076545; C validation rho 0.591110, MSE 0.096749; learning_rate: 0.0001 |
| 2026-10-28 17:27:40 | checkpoint published | 7 | 6 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00036; status: sealed |
| 2026-10-28 17:27:42 | readout epoch | 7 | 7 | B validation rho 0.696724, MSE 0.077809; C validation rho 0.524750, MSE 0.115774; learning_rate: 0.0001 |
| 2026-10-28 17:27:50 | checkpoint published | 7 | 7 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00037; status: sealed |
| 2026-10-28 17:27:52 | readout epoch | 7 | 8 | B validation rho 0.681983, MSE 0.078680; C validation rho 0.558720, MSE 0.103494; learning_rate: 0.0001 |
| 2026-10-28 17:27:59 | checkpoint published | 7 | 8 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00038; status: sealed |
| 2026-10-28 17:28:01 | readout epoch | 7 | 9 | B validation rho 0.694481, MSE 0.079140; C validation rho 0.544023, MSE 0.105714; learning_rate: 0.0001 |
| 2026-10-28 17:28:09 | checkpoint published | 7 | 9 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00039; status: sealed |
| 2026-10-28 17:28:11 | readout epoch | 7 | 10 | B validation rho 0.684904, MSE 0.079594; C validation rho 0.516917, MSE 0.115110; learning_rate: 0.0001 |
| 2026-10-28 17:28:18 | checkpoint published | 7 | 10 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00040; status: sealed |
| 2026-10-28 17:28:21 | readout epoch | 7 | 11 | B validation rho 0.660427, MSE 0.085095; C validation rho 0.549677, MSE 0.104514; learning_rate: 0.0001 |
| 2026-10-28 17:28:29 | checkpoint published | 7 | 11 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00041; status: sealed |
| 2026-10-28 17:28:30 | readout epoch | 7 | 12 | B validation rho 0.672583, MSE 0.083597; C validation rho 0.512184, MSE 0.113349; learning_rate: 0.0001 |
| 2026-10-28 17:28:31 | candidate finished | 7 |  | name: B/C rate 0.0001; epochs 12; selected {'ratings': 1, 'evidence': 2}; status: joint_validation_patience |
| 2026-10-28 17:28:38 | checkpoint published | 7 | 12 | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00042; status: sealed |
| 2026-10-28 17:28:50 | checkpoint published | 7 |  | name: Cloud checkpoint fc24256b28f748e2a0816b85f0edd645/00043; status: sealed |
| 2026-10-28 17:28:50 | head grid complete |  |  | name: Candidate grid published; status: succeeded |
| 2026-10-28 17:29:39 | stage finished | 7 |  | name: Head candidates complete; native publication queued; status: succeeded |


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
| 2026-10-28 17:25:29 | readout epoch | 8 | 1 | B validation rho 0.708926, MSE 0.077935; C validation rho 0.600244, MSE 0.105299; learning_rate: 3e-05 |
| 2026-10-28 17:25:30 | checkpoint published | 8 | 1 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00017; status: sealed |
| 2026-10-28 17:25:38 | readout epoch | 8 | 2 | B validation rho 0.717246, MSE 0.075556; C validation rho 0.636864, MSE 0.095188; learning_rate: 3e-05 |
| 2026-10-28 17:25:39 | checkpoint published | 8 | 2 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00018; status: sealed |
| 2026-10-28 17:25:46 | readout epoch | 8 | 3 | B validation rho 0.731288, MSE 0.073738; C validation rho 0.647345, MSE 0.093784; learning_rate: 3e-05 |
| 2026-10-28 17:25:47 | checkpoint published | 8 | 3 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00019; status: sealed |
| 2026-10-28 17:25:54 | readout epoch | 8 | 4 | B validation rho 0.716868, MSE 0.075044; C validation rho 0.628780, MSE 0.095151; learning_rate: 3e-05 |
| 2026-10-28 17:25:56 | checkpoint published | 8 | 4 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00020; status: sealed |
| 2026-10-28 17:26:03 | readout epoch | 8 | 5 | B validation rho 0.728893, MSE 0.074697; C validation rho 0.626403, MSE 0.097710; learning_rate: 3e-05 |
| 2026-10-28 17:26:04 | checkpoint published | 8 | 5 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00021; status: sealed |
| 2026-10-28 17:26:11 | readout epoch | 8 | 6 | B validation rho 0.716255, MSE 0.074942; C validation rho 0.614603, MSE 0.098691; learning_rate: 3e-05 |
| 2026-10-28 17:26:13 | checkpoint published | 8 | 6 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00022; status: sealed |
| 2026-10-28 17:26:20 | readout epoch | 8 | 7 | B validation rho 0.718543, MSE 0.074719; C validation rho 0.619775, MSE 0.096609; learning_rate: 3e-05 |
| 2026-10-28 17:26:21 | checkpoint published | 8 | 7 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00023; status: sealed |
| 2026-10-28 17:26:28 | readout epoch | 8 | 8 | B validation rho 0.714516, MSE 0.075362; C validation rho 0.624071, MSE 0.097191; learning_rate: 3e-05 |
| 2026-10-28 17:26:30 | checkpoint published | 8 | 8 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00024; status: sealed |
| 2026-10-28 17:26:37 | readout epoch | 8 | 9 | B validation rho 0.703479, MSE 0.076419; C validation rho 0.591591, MSE 0.103960; learning_rate: 3e-05 |
| 2026-10-28 17:26:38 | checkpoint published | 8 | 9 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00025; status: sealed |
| 2026-10-28 17:26:45 | readout epoch | 8 | 10 | B validation rho 0.697956, MSE 0.077958; C validation rho 0.602428, MSE 0.100196; learning_rate: 3e-05 |
| 2026-10-28 17:26:47 | checkpoint published | 8 | 10 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00026; status: sealed |
| 2026-10-28 17:26:54 | readout epoch | 8 | 11 | B validation rho 0.688332, MSE 0.077986; C validation rho 0.581172, MSE 0.105162; learning_rate: 3e-05 |
| 2026-10-28 17:26:55 | checkpoint published | 8 | 11 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00027; status: sealed |
| 2026-10-28 17:27:02 | readout epoch | 8 | 12 | B validation rho 0.679426, MSE 0.079263; C validation rho 0.600723, MSE 0.099246; learning_rate: 3e-05 |
| 2026-10-28 17:27:04 | checkpoint published | 8 | 12 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00028; status: sealed |
| 2026-10-28 17:27:11 | readout epoch | 8 | 13 | B validation rho 0.674036, MSE 0.079745; C validation rho 0.598912, MSE 0.100148; learning_rate: 3e-05 |
| 2026-10-28 17:27:11 | candidate finished | 8 |  | name: B/C rate 3e-05; epochs 13; selected {'ratings': 3, 'evidence': 3}; status: joint_validation_patience |
| 2026-10-28 17:27:11 | candidate started | 8 |  | name: B/C rate 0.0001 |
| 2026-10-28 17:27:12 | checkpoint published | 8 | 13 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00029; status: sealed |
| 2026-10-28 17:27:14 | checkpoint published | 8 |  | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00030; status: sealed |
| 2026-10-28 17:27:30 | readout epoch | 8 | 1 | B validation rho 0.720342, MSE 0.075511; C validation rho 0.638951, MSE 0.096381; learning_rate: 0.0001 |
| 2026-10-28 17:27:31 | checkpoint published | 8 | 1 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00031; status: sealed |
| 2026-10-28 17:27:38 | readout epoch | 8 | 2 | B validation rho 0.728775, MSE 0.073536; C validation rho 0.579805, MSE 0.111605; learning_rate: 0.0001 |
| 2026-10-28 17:27:40 | checkpoint published | 8 | 2 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00032; status: sealed |
| 2026-10-28 17:27:47 | readout epoch | 8 | 3 | B validation rho 0.737643, MSE 0.073141; C validation rho 0.629859, MSE 0.095638; learning_rate: 0.0001 |
| 2026-10-28 17:27:48 | checkpoint published | 8 | 3 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00033; status: sealed |
| 2026-10-28 17:27:55 | readout epoch | 8 | 4 | B validation rho 0.718062, MSE 0.074483; C validation rho 0.552986, MSE 0.113840; learning_rate: 0.0001 |
| 2026-10-28 17:27:57 | checkpoint published | 8 | 4 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00034; status: sealed |
| 2026-10-28 17:28:04 | readout epoch | 8 | 5 | B validation rho 0.713798, MSE 0.077671; C validation rho 0.571751, MSE 0.107942; learning_rate: 0.0001 |
| 2026-10-28 17:28:05 | checkpoint published | 8 | 5 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00035; status: sealed |
| 2026-10-28 17:28:12 | readout epoch | 8 | 6 | B validation rho 0.716086, MSE 0.074518; C validation rho 0.579554, MSE 0.106118; learning_rate: 0.0001 |
| 2026-10-28 17:28:14 | checkpoint published | 8 | 6 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00036; status: sealed |
| 2026-10-28 17:28:21 | readout epoch | 8 | 7 | B validation rho 0.699608, MSE 0.076883; C validation rho 0.572977, MSE 0.103332; learning_rate: 0.0001 |
| 2026-10-28 17:28:22 | checkpoint published | 8 | 7 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00037; status: sealed |
| 2026-10-28 17:28:29 | readout epoch | 8 | 8 | B validation rho 0.702035, MSE 0.077293; C validation rho 0.583186, MSE 0.100047; learning_rate: 0.0001 |
| 2026-10-28 17:28:31 | checkpoint published | 8 | 8 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00038; status: sealed |
| 2026-10-28 17:28:38 | readout epoch | 8 | 9 | B validation rho 0.704424, MSE 0.077111; C validation rho 0.529788, MSE 0.115134; learning_rate: 0.0001 |
| 2026-10-28 17:28:39 | checkpoint published | 8 | 9 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00039; status: sealed |
| 2026-10-28 17:28:46 | readout epoch | 8 | 10 | B validation rho 0.707828, MSE 0.076671; C validation rho 0.565765, MSE 0.103546; learning_rate: 0.0001 |
| 2026-10-28 17:28:49 | checkpoint published | 8 | 10 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00040; status: sealed |
| 2026-10-28 17:28:55 | readout epoch | 8 | 11 | B validation rho 0.692771, MSE 0.078104; C validation rho 0.528100, MSE 0.113751; learning_rate: 0.0001 |
| 2026-10-28 17:28:56 | checkpoint published | 8 | 11 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00041; status: sealed |
| 2026-10-28 17:29:03 | readout epoch | 8 | 12 | B validation rho 0.683313, MSE 0.079535; C validation rho 0.563675, MSE 0.106089; learning_rate: 0.0001 |
| 2026-10-28 17:29:04 | checkpoint published | 8 | 12 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00042; status: sealed |
| 2026-10-28 17:29:12 | readout epoch | 8 | 13 | B validation rho 0.683741, MSE 0.078805; C validation rho 0.531930, MSE 0.109526; learning_rate: 0.0001 |
| 2026-10-28 17:29:12 | candidate finished | 8 |  | name: B/C rate 0.0001; epochs 13; selected {'ratings': 3, 'evidence': 1}; status: joint_validation_patience |
| 2026-10-28 17:29:13 | checkpoint published | 8 | 13 | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00043; status: sealed |
| 2026-10-28 17:29:16 | checkpoint published | 8 |  | name: Cloud checkpoint 1e20177c943c4837802273141c1f8b04/00044; status: sealed |
| 2026-10-28 17:29:16 | head grid complete |  |  | name: Candidate grid published; status: succeeded |
| 2026-10-28 17:30:01 | stage finished | 8 |  | name: Head candidates complete; native publication queued; status: succeeded |


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
| 2026-10-28 17:25:19 | readout epoch | 9 | 14 | B validation rho 0.708633, MSE 0.078338; C validation rho 0.619424, MSE 0.095594; learning_rate: 1e-05 |
| 2026-10-28 17:25:25 | checkpoint published | 9 | 12 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00012; status: sealed |
| 2026-10-28 17:25:28 | readout epoch | 9 | 15 | B validation rho 0.694620, MSE 0.078222; C validation rho 0.604062, MSE 0.100995; learning_rate: 1e-05 |
| 2026-10-28 17:25:34 | checkpoint published | 9 | 13 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00013; status: sealed |
| 2026-10-28 17:25:37 | readout epoch | 9 | 16 | B validation rho 0.692332, MSE 0.078528; C validation rho 0.607316, MSE 0.099109; learning_rate: 1e-05 |
| 2026-10-28 17:25:37 | candidate finished | 9 |  | name: B/C rate 1e-05; epochs 16; selected {'ratings': 3, 'evidence': 6}; status: joint_validation_patience |
| 2026-10-28 17:25:37 | candidate started | 9 |  | name: B/C rate 3e-05 |
| 2026-10-28 17:25:43 | checkpoint published | 9 | 14 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00014; status: sealed |
| 2026-10-28 17:25:53 | checkpoint published | 9 | 15 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00015; status: sealed |
| 2026-10-28 17:25:56 | readout epoch | 9 | 1 | B validation rho 0.727226, MSE 0.077378; C validation rho 0.664148, MSE 0.086830; learning_rate: 3e-05 |
| 2026-10-28 17:26:03 | checkpoint published | 9 | 16 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00016; status: sealed |
| 2026-10-28 17:26:04 | readout epoch | 9 | 2 | B validation rho 0.703771, MSE 0.076657; C validation rho 0.641279, MSE 0.092756; learning_rate: 3e-05 |
| 2026-10-28 17:26:13 | readout epoch | 9 | 3 | B validation rho 0.710947, MSE 0.075711; C validation rho 0.649390, MSE 0.090864; learning_rate: 3e-05 |
| 2026-10-28 17:26:15 | checkpoint published | 9 |  | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00017; status: sealed |
| 2026-10-28 17:26:22 | readout epoch | 9 | 4 | B validation rho 0.720924, MSE 0.074447; C validation rho 0.625180, MSE 0.098588; learning_rate: 3e-05 |
| 2026-10-28 17:26:25 | checkpoint published | 9 | 1 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00018; status: sealed |
| 2026-10-28 17:26:30 | readout epoch | 9 | 5 | B validation rho 0.726883, MSE 0.074403; C validation rho 0.640002, MSE 0.093253; learning_rate: 3e-05 |
| 2026-10-28 17:26:36 | checkpoint published | 9 | 2 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00019; status: sealed |
| 2026-10-28 17:26:39 | readout epoch | 9 | 6 | B validation rho 0.722014, MSE 0.075147; C validation rho 0.626016, MSE 0.094975; learning_rate: 3e-05 |
| 2026-10-28 17:26:46 | checkpoint published | 9 | 3 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00020; status: sealed |
| 2026-10-28 17:26:48 | readout epoch | 9 | 7 | B validation rho 0.718611, MSE 0.076832; C validation rho 0.609498, MSE 0.097656; learning_rate: 3e-05 |
| 2026-10-28 17:26:55 | checkpoint published | 9 | 4 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00021; status: sealed |
| 2026-10-28 17:26:56 | readout epoch | 9 | 8 | B validation rho 0.701269, MSE 0.077059; C validation rho 0.601825, MSE 0.098721; learning_rate: 3e-05 |
| 2026-10-28 17:27:05 | readout epoch | 9 | 9 | B validation rho 0.703841, MSE 0.076290; C validation rho 0.608660, MSE 0.097228; learning_rate: 3e-05 |
| 2026-10-28 17:27:05 | checkpoint published | 9 | 5 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00022; status: sealed |
| 2026-10-28 17:27:13 | readout epoch | 9 | 10 | B validation rho 0.704806, MSE 0.076808; C validation rho 0.583913, MSE 0.103443; learning_rate: 3e-05 |
| 2026-10-28 17:27:15 | checkpoint published | 9 | 6 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00023; status: sealed |
| 2026-10-28 17:27:22 | readout epoch | 9 | 11 | B validation rho 0.683870, MSE 0.078496; C validation rho 0.584115, MSE 0.102426; learning_rate: 3e-05 |
| 2026-10-28 17:27:22 | candidate finished | 9 |  | name: B/C rate 3e-05; epochs 11; selected {'ratings': 1, 'evidence': 1}; status: joint_validation_patience |
| 2026-10-28 17:27:22 | candidate started | 9 |  | name: B/C rate 0.0001 |
| 2026-10-28 17:27:24 | checkpoint published | 9 | 7 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00024; status: sealed |
| 2026-10-28 17:27:33 | checkpoint published | 9 | 8 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00025; status: sealed |
| 2026-10-28 17:27:41 | readout epoch | 9 | 1 | B validation rho 0.730568, MSE 0.076166; C validation rho 0.644259, MSE 0.089564; learning_rate: 0.0001 |
| 2026-10-28 17:27:43 | checkpoint published | 9 | 9 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00026; status: sealed |
| 2026-10-28 17:27:50 | readout epoch | 9 | 2 | B validation rho 0.674248, MSE 0.078723; C validation rho 0.580353, MSE 0.106888; learning_rate: 0.0001 |
| 2026-10-28 17:27:53 | checkpoint published | 9 | 10 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00027; status: sealed |
| 2026-10-28 17:27:58 | readout epoch | 9 | 3 | B validation rho 0.709107, MSE 0.074781; C validation rho 0.605919, MSE 0.096575; learning_rate: 0.0001 |
| 2026-10-28 17:28:04 | checkpoint published | 9 | 11 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00028; status: sealed |
| 2026-10-28 17:28:07 | readout epoch | 9 | 4 | B validation rho 0.685019, MSE 0.081311; C validation rho 0.587066, MSE 0.103176; learning_rate: 0.0001 |
| 2026-10-28 17:28:16 | readout epoch | 9 | 5 | B validation rho 0.701846, MSE 0.077957; C validation rho 0.586603, MSE 0.101021; learning_rate: 0.0001 |
| 2026-10-28 17:28:16 | checkpoint published | 9 |  | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00029; status: sealed |
| 2026-10-28 17:28:24 | readout epoch | 9 | 6 | B validation rho 0.692603, MSE 0.077517; C validation rho 0.552354, MSE 0.107294; learning_rate: 0.0001 |
| 2026-10-28 17:28:25 | checkpoint published | 9 | 1 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00030; status: sealed |
| 2026-10-28 17:28:33 | readout epoch | 9 | 7 | B validation rho 0.682131, MSE 0.079567; C validation rho 0.569649, MSE 0.103696; learning_rate: 0.0001 |
| 2026-10-28 17:28:36 | checkpoint published | 9 | 2 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00031; status: sealed |
| 2026-10-28 17:28:42 | readout epoch | 9 | 8 | B validation rho 0.688633, MSE 0.078822; C validation rho 0.523563, MSE 0.112045; learning_rate: 0.0001 |
| 2026-10-28 17:28:46 | checkpoint published | 9 | 3 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00032; status: sealed |
| 2026-10-28 17:28:50 | readout epoch | 9 | 9 | B validation rho 0.691370, MSE 0.077833; C validation rho 0.522783, MSE 0.112877; learning_rate: 0.0001 |
| 2026-10-28 17:28:55 | checkpoint published | 9 | 4 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00033; status: sealed |
| 2026-10-28 17:28:59 | readout epoch | 9 | 10 | B validation rho 0.688876, MSE 0.080314; C validation rho 0.528480, MSE 0.111971; learning_rate: 0.0001 |
| 2026-10-28 17:29:04 | checkpoint published | 9 | 5 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00034; status: sealed |
| 2026-10-28 17:29:08 | readout epoch | 9 | 11 | B validation rho 0.685174, MSE 0.080592; C validation rho 0.531468, MSE 0.108672; learning_rate: 0.0001 |
| 2026-10-28 17:29:09 | candidate finished | 9 |  | name: B/C rate 0.0001; epochs 11; selected {'ratings': 1, 'evidence': 1}; status: joint_validation_patience |
| 2026-10-28 17:29:15 | checkpoint published | 9 | 6 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00035; status: sealed |
| 2026-10-28 17:29:25 | checkpoint published | 9 | 7 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00036; status: sealed |
| 2026-10-28 17:29:34 | checkpoint published | 9 | 8 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00037; status: sealed |
| 2026-10-28 17:29:43 | checkpoint published | 9 | 9 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00038; status: sealed |
| 2026-10-28 17:29:53 | checkpoint published | 9 | 10 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00039; status: sealed |
| 2026-10-28 17:30:02 | checkpoint published | 9 | 11 | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00040; status: sealed |
| 2026-10-28 17:30:18 | checkpoint published | 9 |  | name: Cloud checkpoint 94dd93c1adf24fb98387388761c5389e/00041; status: sealed |
| 2026-10-28 17:30:18 | head grid complete |  |  | name: Candidate grid published; status: succeeded |
| 2026-10-28 17:31:03 | stage finished | 9 |  | name: Head candidates complete; native publication queued; status: succeeded |


## Combined selection and evaluation

# JEP readouts trained to a validation plateau

Source: `fdbcb3461f63cf44d7cb3cde4de27332594e452d`. Hardware: NVIDIA A100-SXM4-40GB.

Rates: 0.00001, 0.00003, 0.0001. Seeds: 7, 8, 9. Select one rate per objective by mean best validation Spearman. Continue until ten epochs pass without validation improvement. An epoch ceiling is reported as an incomplete fit.

Fit D, E and the same comparison on A's final vectors after selecting B/C. Qwen stays frozen. Sentence vectors retain all 4,096 coordinates.

## Progress

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 17:39:16 | stage started |  |  | name: fit |
| 2026-10-28 17:40:19 | rates selected |  |  | name: {'rates': {'ratings': '0.0001', 'evidence': '3e-05'}, 'mean_validation_spearman': {'1e-05': {'ratings': 0.7289597848476839, 'evidence': 0.6540379057093372}, '3e-05': {'ratings': 0.7311690437588748, 'evidence': 0.658062880051329}, '0.0001': {'ratings': 0.7358020957352472, 'evidence': 0.6432903881060573}}, 'tie_rule': 'smallest learning rate'} |
| 2026-10-28 17:40:19 | comparison started | 7 |  | name: A with comparison, D, E |
| 2026-10-28 17:40:30 | comparison epoch | 7 | 1 | D validation rho 0.756639, MSE 0.063631; E validation rho 0.683031, MSE 0.080764; A with comparison validation rho 0.877052, MSE 0.031171; learning_rate: 0.001 |
| 2026-10-28 17:40:31 | checkpoint published | 7 | 1 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00001; status: sealed |
| 2026-10-28 17:40:32 | comparison epoch | 7 | 2 | D validation rho 0.763765, MSE 0.061887; E validation rho 0.693520, MSE 0.078526; A with comparison validation rho 0.877000, MSE 0.031145; learning_rate: 0.001 |
| 2026-10-28 17:40:33 | checkpoint published | 7 | 2 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00002; status: sealed |
| 2026-10-28 17:40:34 | comparison epoch | 7 | 3 | D validation rho 0.768351, MSE 0.060850; E validation rho 0.701995, MSE 0.075910; A with comparison validation rho 0.876859, MSE 0.031543; learning_rate: 0.001 |
| 2026-10-28 17:40:34 | checkpoint published | 7 | 3 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00003; status: sealed |
| 2026-10-28 17:40:35 | comparison epoch | 7 | 4 | D validation rho 0.771335, MSE 0.060960; E validation rho 0.709063, MSE 0.075355; A with comparison validation rho 0.876673, MSE 0.031592; learning_rate: 0.001 |
| 2026-10-28 17:40:35 | checkpoint published | 7 | 4 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00004; status: sealed |
| 2026-10-28 17:40:36 | comparison epoch | 7 | 5 | D validation rho 0.772947, MSE 0.062538; E validation rho 0.714055, MSE 0.075678; A with comparison validation rho 0.876792, MSE 0.030999; learning_rate: 0.001 |
| 2026-10-28 17:40:37 | checkpoint published | 7 | 5 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00005; status: sealed |
| 2026-10-28 17:40:37 | comparison epoch | 7 | 6 | D validation rho 0.773686, MSE 0.060922; E validation rho 0.715862, MSE 0.073228; A with comparison validation rho 0.876938, MSE 0.034276; learning_rate: 0.001 |
| 2026-10-28 17:40:38 | checkpoint published | 7 | 6 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00006; status: sealed |
| 2026-10-28 17:40:38 | comparison epoch | 7 | 7 | D validation rho 0.774532, MSE 0.059435; E validation rho 0.718156, MSE 0.072888; A with comparison validation rho 0.876716, MSE 0.031485; learning_rate: 0.001 |
| 2026-10-28 17:40:39 | checkpoint published | 7 | 7 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00007; status: sealed |
| 2026-10-28 17:40:39 | comparison epoch | 7 | 8 | D validation rho 0.774770, MSE 0.060324; E validation rho 0.719730, MSE 0.072831; A with comparison validation rho 0.876588, MSE 0.031092; learning_rate: 0.001 |
| 2026-10-28 17:40:40 | checkpoint published | 7 | 8 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00008; status: sealed |
| 2026-10-28 17:40:41 | comparison epoch | 7 | 9 | D validation rho 0.774848, MSE 0.059455; E validation rho 0.721216, MSE 0.072310; A with comparison validation rho 0.876443, MSE 0.031672; learning_rate: 0.001 |
| 2026-10-28 17:40:41 | checkpoint published | 7 | 9 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00009; status: sealed |
| 2026-10-28 17:40:42 | comparison epoch | 7 | 10 | D validation rho 0.774833, MSE 0.061581; E validation rho 0.721665, MSE 0.073211; A with comparison validation rho 0.876409, MSE 0.033546; learning_rate: 0.001 |
| 2026-10-28 17:40:42 | checkpoint published | 7 | 10 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00010; status: sealed |
| 2026-10-28 17:40:43 | comparison epoch | 7 | 11 | D validation rho 0.774301, MSE 0.060908; E validation rho 0.723942, MSE 0.075416; A with comparison validation rho 0.875971, MSE 0.031212; learning_rate: 0.001 |
| 2026-10-28 17:40:44 | checkpoint published | 7 | 11 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00011; status: sealed |
| 2026-10-28 17:40:44 | comparison epoch | 7 | 12 | D validation rho 0.774295, MSE 0.060416; E validation rho 0.723568, MSE 0.072226; A with comparison validation rho 0.876134, MSE 0.032029; learning_rate: 0.001 |
| 2026-10-28 17:40:45 | checkpoint published | 7 | 12 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00012; status: sealed |
| 2026-10-28 17:40:45 | comparison epoch | 7 | 13 | D validation rho 0.774123, MSE 0.061598; E validation rho 0.723473, MSE 0.072277; A with comparison validation rho 0.876130, MSE 0.033806; learning_rate: 0.001 |
| 2026-10-28 17:40:46 | checkpoint published | 7 | 13 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00013; status: sealed |
| 2026-10-28 17:40:46 | comparison epoch | 7 | 14 | D validation rho 0.773388, MSE 0.059959; E validation rho 0.723724, MSE 0.072457; A with comparison validation rho 0.875759, MSE 0.032127; learning_rate: 0.001 |
| 2026-10-28 17:40:47 | checkpoint published | 7 | 14 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00014; status: sealed |
| 2026-10-28 17:40:48 | comparison epoch | 7 | 15 | D validation rho 0.772901, MSE 0.060449; E validation rho 0.723454, MSE 0.072337; A with comparison validation rho 0.875700, MSE 0.032536; learning_rate: 0.001 |
| 2026-10-28 17:40:48 | checkpoint published | 7 | 15 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00015; status: sealed |
| 2026-10-28 17:40:49 | comparison epoch | 7 | 16 | D validation rho 0.772627, MSE 0.062750; E validation rho 0.723415, MSE 0.072714; A with comparison validation rho 0.875505, MSE 0.033585; learning_rate: 0.001 |
| 2026-10-28 17:40:49 | checkpoint published | 7 | 16 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00016; status: sealed |
| 2026-10-28 17:40:50 | comparison epoch | 7 | 17 | D validation rho 0.772146, MSE 0.061451; E validation rho 0.723439, MSE 0.073098; A with comparison validation rho 0.875187, MSE 0.032560; learning_rate: 0.001 |
| 2026-10-28 17:40:51 | checkpoint published | 7 | 17 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00017; status: sealed |
| 2026-10-28 17:40:51 | comparison epoch | 7 | 18 | D validation rho 0.771944, MSE 0.066190; E validation rho 0.722784, MSE 0.080194; A with comparison validation rho 0.874970, MSE 0.032409; learning_rate: 0.001 |
| 2026-10-28 17:40:52 | checkpoint published | 7 | 18 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00018; status: sealed |
| 2026-10-28 17:40:52 | comparison epoch | 7 | 19 | D validation rho 0.770869, MSE 0.061505; E validation rho 0.722991, MSE 0.072760; A with comparison validation rho 0.874462, MSE 0.031870; learning_rate: 0.001 |
| 2026-10-28 17:40:53 | checkpoint published | 7 | 19 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00019; status: sealed |
| 2026-10-28 17:40:53 | comparison epoch | 7 | 20 | D validation rho 0.770293, MSE 0.062520; E validation rho 0.722622, MSE 0.074076; A with comparison validation rho 0.874330, MSE 0.031751; learning_rate: 0.001 |
| 2026-10-28 17:40:54 | checkpoint published | 7 | 20 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00020; status: sealed |
| 2026-10-28 17:40:55 | comparison epoch | 7 | 21 | D validation rho 0.769419, MSE 0.061585; E validation rho 0.722408, MSE 0.072878; A with comparison validation rho 0.874023, MSE 0.031842; learning_rate: 0.001 |
| 2026-10-28 17:40:55 | comparison started | 8 |  | name: A with comparison, D, E |
| 2026-10-28 17:40:55 | checkpoint published | 7 | 21 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00021; status: sealed |
| 2026-10-28 17:41:05 | comparison epoch | 8 | 1 | D validation rho 0.749469, MSE 0.072288; E validation rho 0.660969, MSE 0.090265; A with comparison validation rho 0.876996, MSE 0.035021; learning_rate: 0.001 |
| 2026-10-28 17:41:06 | checkpoint published | 8 | 1 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00022; status: sealed |
| 2026-10-28 17:41:07 | comparison epoch | 8 | 2 | D validation rho 0.755363, MSE 0.062682; E validation rho 0.669641, MSE 0.081654; A with comparison validation rho 0.877045, MSE 0.031527; learning_rate: 0.001 |
| 2026-10-28 17:41:07 | checkpoint published | 8 | 2 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00023; status: sealed |
| 2026-10-28 17:41:08 | comparison epoch | 8 | 3 | D validation rho 0.760056, MSE 0.063548; E validation rho 0.677216, MSE 0.080426; A with comparison validation rho 0.876904, MSE 0.032590; learning_rate: 0.001 |
| 2026-10-28 17:41:08 | checkpoint published | 8 | 3 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00024; status: sealed |
| 2026-10-28 17:41:09 | comparison epoch | 8 | 4 | D validation rho 0.763242, MSE 0.061905; E validation rho 0.683656, MSE 0.080164; A with comparison validation rho 0.876676, MSE 0.031105; learning_rate: 0.001 |
| 2026-10-28 17:41:10 | checkpoint published | 8 | 4 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00025; status: sealed |
| 2026-10-28 17:41:10 | comparison epoch | 8 | 5 | D validation rho 0.765594, MSE 0.061095; E validation rho 0.688037, MSE 0.079270; A with comparison validation rho 0.876887, MSE 0.031278; learning_rate: 0.001 |
| 2026-10-28 17:41:11 | checkpoint published | 8 | 5 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00026; status: sealed |
| 2026-10-28 17:41:11 | comparison epoch | 8 | 6 | D validation rho 0.767183, MSE 0.060854; E validation rho 0.691797, MSE 0.078875; A with comparison validation rho 0.876758, MSE 0.031192; learning_rate: 0.001 |
| 2026-10-28 17:41:12 | checkpoint published | 8 | 6 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00027; status: sealed |
| 2026-10-28 17:41:12 | comparison epoch | 8 | 7 | D validation rho 0.767784, MSE 0.060813; E validation rho 0.694470, MSE 0.078564; A with comparison validation rho 0.876481, MSE 0.031057; learning_rate: 0.001 |
| 2026-10-28 17:41:13 | checkpoint published | 8 | 7 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00028; status: sealed |
| 2026-10-28 17:41:14 | comparison epoch | 8 | 8 | D validation rho 0.768126, MSE 0.060846; E validation rho 0.696441, MSE 0.078430; A with comparison validation rho 0.876486, MSE 0.032029; learning_rate: 0.001 |
| 2026-10-28 17:41:14 | checkpoint published | 8 | 8 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00029; status: sealed |
| 2026-10-28 17:41:15 | comparison epoch | 8 | 9 | D validation rho 0.768272, MSE 0.062046; E validation rho 0.697499, MSE 0.079258; A with comparison validation rho 0.876511, MSE 0.032199; learning_rate: 0.001 |
| 2026-10-28 17:41:16 | comparison epoch | 8 | 10 | D validation rho 0.768220, MSE 0.060946; E validation rho 0.698734, MSE 0.078055; A with comparison validation rho 0.875987, MSE 0.032050; learning_rate: 0.001 |
| 2026-10-28 17:41:16 | checkpoint published | 8 | 9 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00030; status: sealed |
| 2026-10-28 17:41:17 | checkpoint published | 8 | 10 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00031; status: sealed |
| 2026-10-28 17:41:17 | comparison epoch | 8 | 11 | D validation rho 0.768371, MSE 0.063043; E validation rho 0.699041, MSE 0.078442; A with comparison validation rho 0.876143, MSE 0.031476; learning_rate: 0.001 |
| 2026-10-28 17:41:18 | checkpoint published | 8 | 11 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00032; status: sealed |
| 2026-10-28 17:41:18 | comparison epoch | 8 | 12 | D validation rho 0.768131, MSE 0.060874; E validation rho 0.699958, MSE 0.077806; A with comparison validation rho 0.876067, MSE 0.032969; learning_rate: 0.001 |
| 2026-10-28 17:41:19 | checkpoint published | 8 | 12 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00033; status: sealed |
| 2026-10-28 17:41:19 | comparison epoch | 8 | 13 | D validation rho 0.768110, MSE 0.061036; E validation rho 0.700855, MSE 0.078800; A with comparison validation rho 0.875862, MSE 0.032420; learning_rate: 0.001 |
| 2026-10-28 17:41:20 | checkpoint published | 8 | 13 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00034; status: sealed |
| 2026-10-28 17:41:21 | comparison epoch | 8 | 14 | D validation rho 0.767885, MSE 0.061010; E validation rho 0.700690, MSE 0.077718; A with comparison validation rho 0.875560, MSE 0.033704; learning_rate: 0.001 |
| 2026-10-28 17:41:22 | checkpoint published | 8 | 14 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00035; status: sealed |
| 2026-10-28 17:41:22 | comparison epoch | 8 | 15 | D validation rho 0.767802, MSE 0.061965; E validation rho 0.700831, MSE 0.077812; A with comparison validation rho 0.875430, MSE 0.032389; learning_rate: 0.001 |
| 2026-10-28 17:41:23 | checkpoint published | 8 | 15 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00036; status: sealed |
| 2026-10-28 17:41:23 | comparison epoch | 8 | 16 | D validation rho 0.767090, MSE 0.061265; E validation rho 0.700711, MSE 0.077787; A with comparison validation rho 0.874632, MSE 0.031595; learning_rate: 0.001 |
| 2026-10-28 17:41:24 | checkpoint published | 8 | 16 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00037; status: sealed |
| 2026-10-28 17:41:24 | comparison epoch | 8 | 17 | D validation rho 0.766894, MSE 0.061438; E validation rho 0.700465, MSE 0.078059; A with comparison validation rho 0.875264, MSE 0.032378; learning_rate: 0.001 |
| 2026-10-28 17:41:25 | checkpoint published | 8 | 17 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00038; status: sealed |
| 2026-10-28 17:41:25 | comparison epoch | 8 | 18 | D validation rho 0.766575, MSE 0.061486; E validation rho 0.700212, MSE 0.077940; A with comparison validation rho 0.874860, MSE 0.032180; learning_rate: 0.001 |
| 2026-10-28 17:41:26 | checkpoint published | 8 | 18 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00039; status: sealed |
| 2026-10-28 17:41:27 | comparison epoch | 8 | 19 | D validation rho 0.766495, MSE 0.061710; E validation rho 0.700001, MSE 0.078377; A with comparison validation rho 0.874652, MSE 0.032845; learning_rate: 0.001 |
| 2026-10-28 17:41:27 | checkpoint published | 8 | 19 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00040; status: sealed |
| 2026-10-28 17:41:28 | comparison epoch | 8 | 20 | D validation rho 0.766209, MSE 0.063206; E validation rho 0.699518, MSE 0.078375; A with comparison validation rho 0.873830, MSE 0.031981; learning_rate: 0.001 |
| 2026-10-28 17:41:28 | checkpoint published | 8 | 20 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00041; status: sealed |
| 2026-10-28 17:41:29 | comparison epoch | 8 | 21 | D validation rho 0.765786, MSE 0.061983; E validation rho 0.699016, MSE 0.078594; A with comparison validation rho 0.874791, MSE 0.034716; learning_rate: 0.001 |
| 2026-10-28 17:41:30 | checkpoint published | 8 | 21 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00042; status: sealed |
| 2026-10-28 17:41:30 | comparison epoch | 8 | 22 | D validation rho 0.764935, MSE 0.062060; E validation rho 0.698997, MSE 0.078272; A with comparison validation rho 0.874156, MSE 0.032090; learning_rate: 0.001 |
| 2026-10-28 17:41:31 | checkpoint published | 8 | 22 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00043; status: sealed |
| 2026-10-28 17:41:31 | comparison epoch | 8 | 23 | D validation rho 0.764752, MSE 0.062576; E validation rho 0.698706, MSE 0.078541; A with comparison validation rho 0.873831, MSE 0.032158; learning_rate: 0.001 |
| 2026-10-28 17:41:31 | comparison started | 9 |  | name: A with comparison, D, E |
| 2026-10-28 17:41:32 | checkpoint published | 8 | 23 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00044; status: sealed |
| 2026-10-28 17:41:42 | comparison epoch | 9 | 1 | D validation rho 0.743201, MSE 0.066808; E validation rho 0.676492, MSE 0.081003; A with comparison validation rho 0.876937, MSE 0.034439; learning_rate: 0.001 |
| 2026-10-28 17:41:43 | checkpoint published | 9 | 1 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00045; status: sealed |
| 2026-10-28 17:41:43 | comparison epoch | 9 | 2 | D validation rho 0.750793, MSE 0.063944; E validation rho 0.684612, MSE 0.077980; A with comparison validation rho 0.876928, MSE 0.034289; learning_rate: 0.001 |
| 2026-10-28 17:41:44 | checkpoint published | 9 | 2 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00046; status: sealed |
| 2026-10-28 17:41:44 | comparison epoch | 9 | 3 | D validation rho 0.755551, MSE 0.064332; E validation rho 0.690386, MSE 0.078361; A with comparison validation rho 0.876901, MSE 0.032081; learning_rate: 0.001 |
| 2026-10-28 17:41:45 | checkpoint published | 9 | 3 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00047; status: sealed |
| 2026-10-28 17:41:45 | comparison epoch | 9 | 4 | D validation rho 0.759696, MSE 0.062658; E validation rho 0.695841, MSE 0.076056; A with comparison validation rho 0.877107, MSE 0.032456; learning_rate: 0.001 |
| 2026-10-28 17:41:46 | checkpoint published | 9 | 4 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00048; status: sealed |
| 2026-10-28 17:41:47 | comparison epoch | 9 | 5 | D validation rho 0.761752, MSE 0.063595; E validation rho 0.699158, MSE 0.076239; A with comparison validation rho 0.876909, MSE 0.031504; learning_rate: 0.001 |
| 2026-10-28 17:41:47 | checkpoint published | 9 | 5 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00049; status: sealed |
| 2026-10-28 17:41:48 | comparison epoch | 9 | 6 | D validation rho 0.763088, MSE 0.062917; E validation rho 0.701661, MSE 0.076169; A with comparison validation rho 0.876817, MSE 0.034799; learning_rate: 0.001 |
| 2026-10-28 17:41:48 | checkpoint published | 9 | 6 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00050; status: sealed |
| 2026-10-28 17:41:49 | comparison epoch | 9 | 7 | D validation rho 0.764656, MSE 0.061545; E validation rho 0.704275, MSE 0.074817; A with comparison validation rho 0.876719, MSE 0.031015; learning_rate: 0.001 |
| 2026-10-28 17:41:50 | checkpoint published | 9 | 7 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00051; status: sealed |
| 2026-10-28 17:41:50 | comparison epoch | 9 | 8 | D validation rho 0.765569, MSE 0.061382; E validation rho 0.705970, MSE 0.075164; A with comparison validation rho 0.876627, MSE 0.031405; learning_rate: 0.001 |
| 2026-10-28 17:41:51 | checkpoint published | 9 | 8 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00052; status: sealed |
| 2026-10-28 17:41:51 | comparison epoch | 9 | 9 | D validation rho 0.765903, MSE 0.061566; E validation rho 0.707222, MSE 0.075669; A with comparison validation rho 0.876719, MSE 0.033091; learning_rate: 0.001 |
| 2026-10-28 17:41:52 | checkpoint published | 9 | 9 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00053; status: sealed |
| 2026-10-28 17:41:52 | comparison epoch | 9 | 10 | D validation rho 0.765957, MSE 0.065452; E validation rho 0.708264, MSE 0.076209; A with comparison validation rho 0.876323, MSE 0.032303; learning_rate: 0.001 |
| 2026-10-28 17:41:53 | checkpoint published | 9 | 10 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00054; status: sealed |
| 2026-10-28 17:41:54 | comparison epoch | 9 | 11 | D validation rho 0.766284, MSE 0.061243; E validation rho 0.709871, MSE 0.073922; A with comparison validation rho 0.876376, MSE 0.031200; learning_rate: 0.001 |
| 2026-10-28 17:41:54 | checkpoint published | 9 | 11 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00055; status: sealed |
| 2026-10-28 17:41:55 | comparison epoch | 9 | 12 | D validation rho 0.766395, MSE 0.061265; E validation rho 0.710664, MSE 0.074239; A with comparison validation rho 0.875936, MSE 0.031293; learning_rate: 0.001 |
| 2026-10-28 17:41:55 | checkpoint published | 9 | 12 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00056; status: sealed |
| 2026-10-28 17:41:56 | comparison epoch | 9 | 13 | D validation rho 0.766385, MSE 0.061316; E validation rho 0.711188, MSE 0.074205; A with comparison validation rho 0.876161, MSE 0.032202; learning_rate: 0.001 |
| 2026-10-28 17:41:57 | comparison epoch | 9 | 14 | D validation rho 0.766278, MSE 0.061562; E validation rho 0.711456, MSE 0.073940; A with comparison validation rho 0.875751, MSE 0.031676; learning_rate: 0.001 |
| 2026-10-28 17:41:57 | checkpoint published | 9 | 13 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00057; status: sealed |
| 2026-10-28 17:41:58 | checkpoint published | 9 | 14 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00058; status: sealed |
| 2026-10-28 17:41:58 | comparison epoch | 9 | 15 | D validation rho 0.766081, MSE 0.061521; E validation rho 0.711894, MSE 0.073994; A with comparison validation rho 0.875879, MSE 0.033426; learning_rate: 0.001 |
| 2026-10-28 17:41:59 | checkpoint published | 9 | 15 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00059; status: sealed |
| 2026-10-28 17:41:59 | comparison epoch | 9 | 16 | D validation rho 0.766032, MSE 0.063533; E validation rho 0.711960, MSE 0.074876; A with comparison validation rho 0.875711, MSE 0.034744; learning_rate: 0.001 |
| 2026-10-28 17:42:01 | comparison epoch | 9 | 17 | D validation rho 0.765489, MSE 0.062681; E validation rho 0.712372, MSE 0.075291; A with comparison validation rho 0.875343, MSE 0.031644; learning_rate: 0.001 |
| 2026-10-28 17:42:01 | checkpoint published | 9 | 16 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00060; status: sealed |
| 2026-10-28 17:42:02 | checkpoint published | 9 | 17 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00061; status: sealed |
| 2026-10-28 17:42:02 | comparison epoch | 9 | 18 | D validation rho 0.765299, MSE 0.061843; E validation rho 0.712161, MSE 0.073699; A with comparison validation rho 0.874837, MSE 0.031644; learning_rate: 0.001 |
| 2026-10-28 17:42:03 | checkpoint published | 9 | 18 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00062; status: sealed |
| 2026-10-28 17:42:03 | comparison epoch | 9 | 19 | D validation rho 0.764985, MSE 0.061874; E validation rho 0.712224, MSE 0.073946; A with comparison validation rho 0.874741, MSE 0.031851; learning_rate: 0.001 |
| 2026-10-28 17:42:04 | checkpoint published | 9 | 19 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00063; status: sealed |
| 2026-10-28 17:42:04 | comparison epoch | 9 | 20 | D validation rho 0.764412, MSE 0.062011; E validation rho 0.712169, MSE 0.073815; A with comparison validation rho 0.874567, MSE 0.032124; learning_rate: 0.001 |
| 2026-10-28 17:42:05 | checkpoint published | 9 | 20 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00064; status: sealed |
| 2026-10-28 17:42:05 | comparison epoch | 9 | 21 | D validation rho 0.763899, MSE 0.063520; E validation rho 0.712002, MSE 0.074747; A with comparison validation rho 0.874565, MSE 0.032356; learning_rate: 0.001 |
| 2026-10-28 17:42:06 | checkpoint published | 9 | 21 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00065; status: sealed |
| 2026-10-28 17:42:06 | comparison epoch | 9 | 22 | D validation rho 0.763833, MSE 0.062290; E validation rho 0.711458, MSE 0.073998; A with comparison validation rho 0.873922, MSE 0.032050; learning_rate: 0.001 |
| 2026-10-28 17:42:07 | checkpoint published | 9 | 22 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00066; status: sealed |
| 2026-10-28 17:42:08 | comparison epoch | 9 | 23 | D validation rho 0.763112, MSE 0.062476; E validation rho 0.711288, MSE 0.074128; A with comparison validation rho 0.873665, MSE 0.031862; learning_rate: 0.001 |
| 2026-10-28 17:42:08 | checkpoint published | 9 | 23 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00067; status: sealed |
| 2026-10-28 17:42:09 | comparison epoch | 9 | 24 | D validation rho 0.763437, MSE 0.064793; E validation rho 0.711263, MSE 0.074991; A with comparison validation rho 0.874366, MSE 0.035292; learning_rate: 0.001 |
| 2026-10-28 17:42:10 | comparison epoch | 9 | 25 | D validation rho 0.762333, MSE 0.062774; E validation rho 0.710816, MSE 0.074321; A with comparison validation rho 0.873919, MSE 0.032992; learning_rate: 0.001 |
| 2026-10-28 17:42:10 | checkpoint published | 9 | 24 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00068; status: sealed |
| 2026-10-28 17:42:11 | checkpoint published | 9 | 25 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00069; status: sealed |
| 2026-10-28 17:42:11 | comparison epoch | 9 | 26 | D validation rho 0.762238, MSE 0.064606; E validation rho 0.710436, MSE 0.075189; A with comparison validation rho 0.873458, MSE 0.032434; learning_rate: 0.001 |
| 2026-10-28 17:42:12 | checkpoint published | 9 | 26 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00070; status: sealed |
| 2026-10-28 17:42:12 | comparison epoch | 9 | 27 | D validation rho 0.761471, MSE 0.063573; E validation rho 0.710045, MSE 0.074860; A with comparison validation rho 0.873565, MSE 0.033503; learning_rate: 0.001 |
| 2026-10-28 17:42:14 | checkpoint published | 9 | 27 | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00071; status: sealed |
| 2026-10-28 17:42:15 | checkpoint published |  |  | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00072; status: sealed |
| 2026-10-28 17:42:21 | checkpoint published |  |  | name: Cloud checkpoint 1702802689404f9cac66e2119e843408/00073; status: sealed |
| 2026-10-28 17:42:21 | fitting complete |  |  | name: Learning rates and all checkpoints selected using validation |
| 2026-10-28 17:43:12 | stage finished |  |  | name: fit; status: succeeded |
| 2026-10-28 17:43:12 | stage started |  |  | name: extract_test |
| 2026-10-28 17:43:51 | readout extraction |  |  | split: test; 4/4862 |
| 2026-10-28 17:43:56 | readout extraction |  |  | split: test; 204/4862 |
| 2026-10-28 17:44:01 | readout extraction |  |  | split: test; 404/4862 |
| 2026-10-28 17:44:06 | readout extraction |  |  | split: test; 604/4862 |
| 2026-10-28 17:44:11 | readout extraction |  |  | split: test; 804/4862 |
| 2026-10-28 17:44:16 | readout extraction |  |  | split: test; 1004/4862 |
| 2026-10-28 17:44:21 | readout extraction |  |  | split: test; 1204/4862 |
| 2026-10-28 17:44:26 | readout extraction |  |  | split: test; 1404/4862 |
| 2026-10-28 17:44:31 | readout extraction |  |  | split: test; 1604/4862 |
| 2026-10-28 17:44:36 | readout extraction |  |  | split: test; 1804/4862 |
| 2026-10-28 17:44:41 | readout extraction |  |  | split: test; 2004/4862 |
| 2026-10-28 17:44:45 | readout extraction |  |  | split: test; 2204/4862 |
| 2026-10-28 17:44:50 | readout extraction |  |  | split: test; 2404/4862 |
| 2026-10-28 17:44:55 | readout extraction |  |  | split: test; 2604/4862 |
| 2026-10-28 17:45:00 | readout extraction |  |  | split: test; 2804/4862 |
| 2026-10-28 17:45:05 | readout extraction |  |  | split: test; 3004/4862 |
| 2026-10-28 17:45:10 | readout extraction |  |  | split: test; 3204/4862 |
| 2026-10-28 17:45:15 | readout extraction |  |  | split: test; 3404/4862 |
| 2026-10-28 17:45:20 | readout extraction |  |  | split: test; 3604/4862 |
| 2026-10-28 17:45:24 | readout extraction |  |  | split: test; 3804/4862 |
| 2026-10-28 17:45:29 | readout extraction |  |  | split: test; 4004/4862 |
| 2026-10-28 17:45:34 | readout extraction |  |  | split: test; 4204/4862 |
| 2026-10-28 17:45:39 | readout extraction |  |  | split: test; 4404/4862 |
| 2026-10-28 17:45:44 | readout extraction |  |  | split: test; 4604/4862 |
| 2026-10-28 17:45:49 | readout extraction |  |  | split: test; 4804/4862 |
| 2026-10-28 17:45:50 | readout extraction |  |  | split: test; 4862/4862 |
| 2026-10-28 17:46:18 | stage finished |  |  | name: extract_test; status: succeeded |
| 2026-10-28 17:46:20 | stage started |  |  | name: extract_interventions |
| 2026-10-28 17:47:00 | readout extraction |  |  | split: interventions; 4/48 |
| 2026-10-28 17:47:01 | readout extraction |  |  | split: interventions; 48/48 |
| 2026-10-28 17:47:09 | stage finished |  |  | name: extract_interventions; status: succeeded |
| 2026-10-28 17:47:09 | stage started |  |  | name: evaluate |
| 2026-10-28 17:47:09 | controller failed |  |  | error_type: ValidationError |


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
