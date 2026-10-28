# JEP evidence selection and sentence comparison

Source: `f59d2f8c5c64b96940a624a56d385330cf6a11ca`

Hardware: NVIDIA A100-SXM4-80GB

Seeds: 7, 8, 9. Training: 6,051 comparisons. Validation: 1,576. Test: 2,431.

A: saved cosine score. B: token weighting trained with ratings. C: token weighting trained with ratings and evidence. D: fitted comparison of B vectors. E: fitted comparison of C vectors.

## Live progress

| UTC | Event | Seed | Step | Metrics or progress |
| --- | --- | --- | --- | --- |
| 2026-10-28 04:35:25 | stage started | 7 |  | name: publish_proposition_final |
| 2026-10-28 04:36:05 | stage finished | 7 |  | name: publish_proposition_final; status: succeeded |
| 2026-10-28 04:36:05 | stage started | 7 |  | name: publish_proposition_writing_epoch5 |
| 2026-10-28 04:36:45 | stage finished | 7 |  | name: publish_proposition_writing_epoch5; status: succeeded |
| 2026-10-28 04:36:45 | stage started | 7 |  | name: publish_ratings_final |
| 2026-10-28 04:37:24 | stage finished | 7 |  | name: publish_ratings_final; status: succeeded |
| 2026-10-28 04:37:24 | stage started | 7 |  | name: writing_retention |
| 2026-10-28 04:38:39 | writing retention |  |  | checkpoint: writing; 16/121 |
| 2026-10-28 04:38:50 | writing retention |  |  | checkpoint: writing; 32/121 |
| 2026-10-28 04:38:52 | writing retention |  |  | checkpoint: writing; 48/121 |
| 2026-10-28 04:38:53 | writing retention |  |  | checkpoint: writing; 64/121 |
| 2026-10-28 04:38:55 | writing retention |  |  | checkpoint: writing; 80/121 |
| 2026-10-28 04:38:56 | writing retention |  |  | checkpoint: writing; 96/121 |
| 2026-10-28 04:38:58 | writing retention |  |  | checkpoint: writing; 112/121 |
| 2026-10-28 04:38:59 | writing retention |  |  | checkpoint: writing; 121/121 |
| 2026-10-28 04:39:07 | writing retention |  |  | checkpoint: after_ratings; 16/121 |
| 2026-10-28 04:39:14 | writing retention |  |  | checkpoint: after_ratings; 32/121 |
| 2026-10-28 04:39:16 | writing retention |  |  | checkpoint: after_ratings; 48/121 |
| 2026-10-28 04:39:17 | writing retention |  |  | checkpoint: after_ratings; 64/121 |
| 2026-10-28 04:39:19 | writing retention |  |  | checkpoint: after_ratings; 80/121 |
| 2026-10-28 04:39:20 | writing retention |  |  | checkpoint: after_ratings; 96/121 |
| 2026-10-28 04:39:22 | writing retention |  |  | checkpoint: after_ratings; 112/121 |
| 2026-10-28 04:39:22 | writing retention |  |  | checkpoint: after_ratings; 121/121 |
| 2026-10-28 04:39:23 | writing retention scores |  |  | writing answer CE 0.277840, exact agreement 0.375000; after_ratings answer CE 4.954078, exact agreement 0.000000; paired CE change 4.676239 |
| 2026-10-28 04:39:49 | stage finished | 7 |  | name: writing_retention; status: succeeded |
| 2026-10-28 04:39:49 | stage started | 7 |  | name: extract_training_proposition_final |
| 2026-10-28 04:40:33 | readout extraction |  |  | split: training; 4/12102 |
| 2026-10-28 04:40:38 | readout extraction |  |  | split: training; 204/12102 |
| 2026-10-28 04:40:43 | readout extraction |  |  | split: training; 404/12102 |
| 2026-10-28 04:40:48 | readout extraction |  |  | split: training; 604/12102 |
| 2026-10-28 04:40:53 | readout extraction |  |  | split: training; 804/12102 |
| 2026-10-28 04:40:58 | readout extraction |  |  | split: training; 1004/12102 |
| 2026-10-28 04:41:03 | readout extraction |  |  | split: training; 1204/12102 |
| 2026-10-28 04:41:08 | readout extraction |  |  | split: training; 1404/12102 |
| 2026-10-28 04:41:13 | readout extraction |  |  | split: training; 1604/12102 |
| 2026-10-28 04:41:18 | readout extraction |  |  | split: training; 1804/12102 |
| 2026-10-28 04:41:23 | readout extraction |  |  | split: training; 2004/12102 |
| 2026-10-28 04:41:28 | readout extraction |  |  | split: training; 2204/12102 |
| 2026-10-28 04:41:33 | readout extraction |  |  | split: training; 2404/12102 |
| 2026-10-28 04:41:38 | readout extraction |  |  | split: training; 2604/12102 |
| 2026-10-28 04:41:42 | readout extraction |  |  | split: training; 2804/12102 |
| 2026-10-28 04:41:48 | readout extraction |  |  | split: training; 3004/12102 |
| 2026-10-28 04:41:53 | readout extraction |  |  | split: training; 3204/12102 |
| 2026-10-28 04:41:58 | readout extraction |  |  | split: training; 3404/12102 |
| 2026-10-28 04:42:02 | readout extraction |  |  | split: training; 3604/12102 |
| 2026-10-28 04:42:07 | readout extraction |  |  | split: training; 3804/12102 |
| 2026-10-28 04:42:12 | readout extraction |  |  | split: training; 4004/12102 |
| 2026-10-28 04:42:17 | readout extraction |  |  | split: training; 4204/12102 |
| 2026-10-28 04:42:22 | readout extraction |  |  | split: training; 4404/12102 |
| 2026-10-28 04:42:27 | readout extraction |  |  | split: training; 4604/12102 |
| 2026-10-28 04:42:32 | readout extraction |  |  | split: training; 4804/12102 |
| 2026-10-28 04:42:37 | readout extraction |  |  | split: training; 5004/12102 |
| 2026-10-28 04:42:42 | readout extraction |  |  | split: training; 5204/12102 |
| 2026-10-28 04:42:47 | readout extraction |  |  | split: training; 5404/12102 |
| 2026-10-28 04:42:52 | readout extraction |  |  | split: training; 5604/12102 |
| 2026-10-28 04:42:57 | readout extraction |  |  | split: training; 5804/12102 |
| 2026-10-28 04:43:02 | readout extraction |  |  | split: training; 6004/12102 |
| 2026-10-28 04:43:07 | readout extraction |  |  | split: training; 6204/12102 |
| 2026-10-28 04:43:12 | readout extraction |  |  | split: training; 6404/12102 |
| 2026-10-28 04:43:17 | readout extraction |  |  | split: training; 6604/12102 |
| 2026-10-28 04:43:22 | readout extraction |  |  | split: training; 6804/12102 |
| 2026-10-28 04:43:27 | readout extraction |  |  | split: training; 7004/12102 |
| 2026-10-28 04:43:32 | readout extraction |  |  | split: training; 7204/12102 |
| 2026-10-28 04:43:37 | readout extraction |  |  | split: training; 7404/12102 |
| 2026-10-28 04:43:42 | readout extraction |  |  | split: training; 7604/12102 |
| 2026-10-28 04:43:47 | readout extraction |  |  | split: training; 7804/12102 |
| 2026-10-28 04:43:52 | readout extraction |  |  | split: training; 8004/12102 |
| 2026-10-28 04:43:57 | readout extraction |  |  | split: training; 8204/12102 |
| 2026-10-28 04:44:02 | readout extraction |  |  | split: training; 8404/12102 |
| 2026-10-28 04:44:07 | readout extraction |  |  | split: training; 8604/12102 |
| 2026-10-28 04:44:12 | readout extraction |  |  | split: training; 8804/12102 |
| 2026-10-28 04:44:17 | readout extraction |  |  | split: training; 9004/12102 |
| 2026-10-28 04:44:22 | readout extraction |  |  | split: training; 9204/12102 |
| 2026-10-28 04:44:27 | readout extraction |  |  | split: training; 9404/12102 |
| 2026-10-28 04:44:32 | readout extraction |  |  | split: training; 9604/12102 |
| 2026-10-28 04:44:37 | readout extraction |  |  | split: training; 9804/12102 |
| 2026-10-28 04:44:42 | readout extraction |  |  | split: training; 10004/12102 |
| 2026-10-28 04:44:48 | readout extraction |  |  | split: training; 10204/12102 |
| 2026-10-28 04:44:53 | readout extraction |  |  | split: training; 10404/12102 |
| 2026-10-28 04:44:58 | readout extraction |  |  | split: training; 10604/12102 |
| 2026-10-28 04:45:03 | readout extraction |  |  | split: training; 10804/12102 |
| 2026-10-28 04:45:08 | readout extraction |  |  | split: training; 11004/12102 |
| 2026-10-28 04:45:13 | readout extraction |  |  | split: training; 11204/12102 |
| 2026-10-28 04:45:18 | readout extraction |  |  | split: training; 11404/12102 |
| 2026-10-28 04:45:23 | readout extraction |  |  | split: training; 11604/12102 |
| 2026-10-28 04:45:28 | readout extraction |  |  | split: training; 11804/12102 |
| 2026-10-28 04:45:33 | readout extraction |  |  | split: training; 12004/12102 |
| 2026-10-28 04:45:35 | readout extraction |  |  | split: training; 12102/12102 |
| 2026-10-28 04:46:29 | stage finished | 7 |  | name: extract_training_proposition_final; status: succeeded |
| 2026-10-28 04:46:29 | stage started | 7 |  | name: extract_validation_proposition_final |
| 2026-10-28 04:47:13 | readout extraction |  |  | split: validation; 4/3152 |
| 2026-10-28 04:47:18 | readout extraction |  |  | split: validation; 204/3152 |
| 2026-10-28 04:47:23 | readout extraction |  |  | split: validation; 404/3152 |
| 2026-10-28 04:47:28 | readout extraction |  |  | split: validation; 604/3152 |
| 2026-10-28 04:47:33 | readout extraction |  |  | split: validation; 804/3152 |
| 2026-10-28 04:47:38 | readout extraction |  |  | split: validation; 1004/3152 |
| 2026-10-28 04:47:43 | readout extraction |  |  | split: validation; 1204/3152 |
| 2026-10-28 04:47:48 | readout extraction |  |  | split: validation; 1404/3152 |
| 2026-10-28 04:47:53 | readout extraction |  |  | split: validation; 1604/3152 |
| 2026-10-28 04:47:59 | readout extraction |  |  | split: validation; 1804/3152 |
| 2026-10-28 04:48:04 | readout extraction |  |  | split: validation; 2004/3152 |
| 2026-10-28 04:48:09 | readout extraction |  |  | split: validation; 2204/3152 |
| 2026-10-28 04:48:14 | readout extraction |  |  | split: validation; 2404/3152 |
| 2026-10-28 04:48:19 | readout extraction |  |  | split: validation; 2604/3152 |
| 2026-10-28 04:48:24 | readout extraction |  |  | split: validation; 2804/3152 |
| 2026-10-28 04:48:29 | readout extraction |  |  | split: validation; 3004/3152 |
| 2026-10-28 04:48:33 | readout extraction |  |  | split: validation; 3152/3152 |
| 2026-10-28 04:48:53 | stage finished | 7 |  | name: extract_validation_proposition_final; status: succeeded |
| 2026-10-28 04:49:00 | stage started | 7 |  | name: fit_7 |
| 2026-10-28 04:50:10 | readout epoch | 7 | 1 | B validation rho 0.255872, MSE 0.177885; C validation rho 0.221737, MSE 0.150908 |
| 2026-10-28 04:50:19 | readout epoch | 7 | 2 | B validation rho 0.152632, MSE 0.199155; C validation rho 0.233072, MSE 0.149474 |
| 2026-10-28 04:50:29 | readout epoch | 7 | 3 | B validation rho 0.039977, MSE 0.201632; C validation rho 0.293007, MSE 0.141807 |
| 2026-10-28 04:50:38 | readout epoch | 7 | 4 | B validation rho 0.070237, MSE 0.195947; C validation rho 0.147994, MSE 0.170601 |
| 2026-10-28 04:50:48 | readout epoch | 7 | 5 | B validation rho 0.043362, MSE 0.215740; C validation rho 0.247820, MSE 0.152598 |
| 2026-10-28 04:50:57 | readout epoch | 7 | 6 | B validation rho 0.044341, MSE 0.171840; C validation rho 0.181657, MSE 0.161553 |
| 2026-10-28 04:51:06 | readout epoch | 7 | 7 | B validation rho 0.053798, MSE 0.166360; C validation rho 0.207463, MSE 0.155944 |
| 2026-10-28 04:51:16 | readout epoch | 7 | 8 | B validation rho 0.066286, MSE 0.164494; C validation rho 0.216461, MSE 0.151931 |
| 2026-10-28 04:51:28 | comparison epoch | 7 | 1 | D validation rho 0.315054, MSE 0.129944; E validation rho 0.317128, MSE 0.134520 |
| 2026-10-28 04:51:29 | comparison epoch | 7 | 2 | D validation rho 0.334231, MSE 0.128188; E validation rho 0.334135, MSE 0.132670 |
| 2026-10-28 04:51:30 | comparison epoch | 7 | 3 | D validation rho 0.374386, MSE 0.117072; E validation rho 0.350843, MSE 0.129889 |
| 2026-10-28 04:51:30 | comparison epoch | 7 | 4 | D validation rho 0.400948, MSE 0.119021; E validation rho 0.365759, MSE 0.127769 |
| 2026-10-28 04:51:31 | comparison epoch | 7 | 5 | D validation rho 0.409784, MSE 0.114121; E validation rho 0.375574, MSE 0.126780 |
| 2026-10-28 04:51:32 | comparison epoch | 7 | 6 | D validation rho 0.410401, MSE 0.114822; E validation rho 0.379682, MSE 0.129689 |
| 2026-10-28 04:51:33 | comparison epoch | 7 | 7 | D validation rho 0.424484, MSE 0.112756; E validation rho 0.387894, MSE 0.126614 |
| 2026-10-28 04:51:34 | comparison epoch | 7 | 8 | D validation rho 0.428264, MSE 0.111854; E validation rho 0.392926, MSE 0.126185 |
| 2026-10-28 04:51:34 | comparison epoch | 7 | 9 | D validation rho 0.432186, MSE 0.111953; E validation rho 0.399952, MSE 0.124466 |
| 2026-10-28 04:51:35 | comparison epoch | 7 | 10 | D validation rho 0.431586, MSE 0.111564; E validation rho 0.401049, MSE 0.126158 |
| 2026-10-28 04:51:36 | comparison epoch | 7 | 11 | D validation rho 0.436701, MSE 0.110963; E validation rho 0.409029, MSE 0.125539 |
| 2026-10-28 04:51:37 | comparison epoch | 7 | 12 | D validation rho 0.435937, MSE 0.110981; E validation rho 0.408061, MSE 0.124024 |
| 2026-10-28 04:51:38 | comparison epoch | 7 | 13 | D validation rho 0.438337, MSE 0.110591; E validation rho 0.409688, MSE 0.124106 |
| 2026-10-28 04:51:38 | comparison epoch | 7 | 14 | D validation rho 0.438936, MSE 0.110621; E validation rho 0.413032, MSE 0.123840 |
| 2026-10-28 04:51:39 | comparison epoch | 7 | 15 | D validation rho 0.435608, MSE 0.112654; E validation rho 0.412314, MSE 0.124546 |
| 2026-10-28 04:51:40 | comparison epoch | 7 | 16 | D validation rho 0.438529, MSE 0.110905; E validation rho 0.412603, MSE 0.126361 |
| 2026-10-28 04:51:41 | comparison epoch | 7 | 17 | D validation rho 0.439329, MSE 0.111016; E validation rho 0.415460, MSE 0.123780 |
| 2026-10-28 04:51:42 | comparison epoch | 7 | 18 | D validation rho 0.435659, MSE 0.113191; E validation rho 0.413077, MSE 0.129386 |
| 2026-10-28 04:51:42 | comparison epoch | 7 | 19 | D validation rho 0.433994, MSE 0.115513; E validation rho 0.413504, MSE 0.128138 |
| 2026-10-28 04:51:43 | comparison epoch | 7 | 20 | D validation rho 0.436774, MSE 0.111780; E validation rho 0.414441, MSE 0.124283 |
| 2026-10-28 04:51:44 | comparison epoch | 7 | 21 | D validation rho 0.437187, MSE 0.111357; E validation rho 0.414367, MSE 0.123802 |
| 2026-10-28 04:51:45 | comparison epoch | 7 | 22 | D validation rho 0.435851, MSE 0.111775; E validation rho 0.414212, MSE 0.124192 |
| 2026-10-28 04:52:10 | stage finished | 7 |  | name: fit_7; status: succeeded |
| 2026-10-28 04:52:17 | stage started | 8 |  | name: fit_8 |
| 2026-10-28 04:53:28 | readout epoch | 8 | 1 | B validation rho 0.581703, MSE 0.123471; C validation rho 0.339654, MSE 0.137390 |
| 2026-10-28 04:53:37 | readout epoch | 8 | 2 | B validation rho 0.530675, MSE 0.137100; C validation rho 0.180140, MSE 0.155712 |
| 2026-10-28 04:53:47 | readout epoch | 8 | 3 | B validation rho 0.572172, MSE 0.125718; C validation rho 0.201945, MSE 0.150150 |
| 2026-10-28 04:53:57 | readout epoch | 8 | 4 | B validation rho 0.573592, MSE 0.125538; C validation rho 0.359352, MSE 0.133128 |
| 2026-10-28 04:54:06 | readout epoch | 8 | 5 | B validation rho 0.568951, MSE 0.126089; C validation rho 0.195257, MSE 0.159765 |
| 2026-10-28 04:54:15 | readout epoch | 8 | 6 | B validation rho 0.566996, MSE 0.126606; C validation rho 0.253984, MSE 0.146664 |
| 2026-10-28 04:54:25 | readout epoch | 8 | 7 | B validation rho 0.570764, MSE 0.125564; C validation rho 0.249827, MSE 0.148830 |
| 2026-10-28 04:54:34 | readout epoch | 8 | 8 | B validation rho 0.574787, MSE 0.124681; C validation rho 0.190980, MSE 0.152376 |
| 2026-10-28 04:54:43 | readout epoch | 8 | 9 | B validation rho 0.569681, MSE 0.125438; C validation rho 0.220458, MSE 0.153231 |
| 2026-10-28 04:54:55 | comparison epoch | 8 | 1 | D validation rho 0.672595, MSE 0.094275; E validation rho 0.390036, MSE 0.129396 |
| 2026-10-28 04:54:56 | comparison epoch | 8 | 2 | D validation rho 0.703432, MSE 0.076323; E validation rho 0.414519, MSE 0.118008 |
| 2026-10-28 04:54:57 | comparison epoch | 8 | 3 | D validation rho 0.715282, MSE 0.075458; E validation rho 0.431783, MSE 0.116616 |
| 2026-10-28 04:54:58 | comparison epoch | 8 | 4 | D validation rho 0.721273, MSE 0.072104; E validation rho 0.445098, MSE 0.114539 |
| 2026-10-28 04:54:59 | comparison epoch | 8 | 5 | D validation rho 0.725586, MSE 0.070991; E validation rho 0.456758, MSE 0.112522 |
| 2026-10-28 04:55:00 | comparison epoch | 8 | 6 | D validation rho 0.727584, MSE 0.070265; E validation rho 0.459180, MSE 0.117252 |
| 2026-10-28 04:55:00 | comparison epoch | 8 | 7 | D validation rho 0.728554, MSE 0.071595; E validation rho 0.465640, MSE 0.114268 |
| 2026-10-28 04:55:01 | comparison epoch | 8 | 8 | D validation rho 0.729783, MSE 0.071072; E validation rho 0.470769, MSE 0.112483 |
| 2026-10-28 04:55:02 | comparison epoch | 8 | 9 | D validation rho 0.730727, MSE 0.072246; E validation rho 0.474022, MSE 0.112513 |
| 2026-10-28 04:55:03 | comparison epoch | 8 | 10 | D validation rho 0.731305, MSE 0.071129; E validation rho 0.477855, MSE 0.110413 |
| 2026-10-28 04:55:04 | comparison epoch | 8 | 11 | D validation rho 0.731632, MSE 0.069585; E validation rho 0.479098, MSE 0.111459 |
| 2026-10-28 04:55:04 | comparison epoch | 8 | 12 | D validation rho 0.731641, MSE 0.069375; E validation rho 0.482531, MSE 0.109679 |
| 2026-10-28 04:55:05 | comparison epoch | 8 | 13 | D validation rho 0.730754, MSE 0.070610; E validation rho 0.484911, MSE 0.109325 |
| 2026-10-28 04:55:06 | comparison epoch | 8 | 14 | D validation rho 0.731337, MSE 0.069861; E validation rho 0.485163, MSE 0.109619 |
| 2026-10-28 04:55:07 | comparison epoch | 8 | 15 | D validation rho 0.730927, MSE 0.069684; E validation rho 0.486494, MSE 0.109260 |
| 2026-10-28 04:55:07 | comparison epoch | 8 | 16 | D validation rho 0.730365, MSE 0.070617; E validation rho 0.486223, MSE 0.110009 |
| 2026-10-28 04:55:08 | comparison epoch | 8 | 17 | D validation rho 0.728550, MSE 0.070855; E validation rho 0.487880, MSE 0.109398 |
| 2026-10-28 04:55:09 | comparison epoch | 8 | 18 | D validation rho 0.728765, MSE 0.070176; E validation rho 0.487618, MSE 0.110111 |
| 2026-10-28 04:55:10 | comparison epoch | 8 | 19 | D validation rho 0.728248, MSE 0.070306; E validation rho 0.487366, MSE 0.111352 |
| 2026-10-28 04:55:11 | comparison epoch | 8 | 20 | D validation rho 0.727778, MSE 0.070632; E validation rho 0.488041, MSE 0.109777 |
| 2026-10-28 04:55:12 | comparison epoch | 8 | 21 | D validation rho 0.726729, MSE 0.070321; E validation rho 0.488073, MSE 0.109865 |
| 2026-10-28 04:55:12 | comparison epoch | 8 | 22 | D validation rho 0.725816, MSE 0.070809; E validation rho 0.488917, MSE 0.109963 |
| 2026-10-28 04:55:13 | comparison epoch | 8 | 23 | D validation rho 0.725186, MSE 0.070936; E validation rho 0.487725, MSE 0.112020 |
| 2026-10-28 04:55:14 | comparison epoch | 8 | 24 | D validation rho 0.725708, MSE 0.076506; E validation rho 0.488345, MSE 0.110504 |
| 2026-10-28 04:55:15 | comparison epoch | 8 | 25 | D validation rho 0.723108, MSE 0.071172; E validation rho 0.488922, MSE 0.111225 |
| 2026-10-28 04:55:16 | comparison epoch | 8 | 26 | D validation rho 0.721577, MSE 0.071649; E validation rho 0.488403, MSE 0.110740 |
| 2026-10-28 04:55:16 | comparison epoch | 8 | 27 | D validation rho 0.721631, MSE 0.071900; E validation rho 0.487357, MSE 0.113709 |
| 2026-10-28 04:55:17 | comparison epoch | 8 | 28 | D validation rho 0.720524, MSE 0.071919; E validation rho 0.487618, MSE 0.111058 |
| 2026-10-28 04:55:18 | comparison epoch | 8 | 29 | D validation rho 0.719871, MSE 0.072499; E validation rho 0.486865, MSE 0.113741 |
| 2026-10-28 04:55:19 | comparison epoch | 8 | 30 | D validation rho 0.720402, MSE 0.076481; E validation rho 0.486538, MSE 0.115444 |
| 2026-10-28 04:55:32 | stage finished | 8 |  | name: fit_8; status: succeeded |
| 2026-10-28 04:55:40 | stage started | 9 |  | name: fit_9 |
| 2026-10-28 04:56:51 | readout epoch | 9 | 1 | B validation rho 0.545021, MSE 0.125585; C validation rho 0.236988, MSE 0.152148 |
| 2026-10-28 04:57:00 | readout epoch | 9 | 2 | B validation rho 0.578447, MSE 0.126604; C validation rho 0.264137, MSE 0.150158 |
| 2026-10-28 04:57:10 | readout epoch | 9 | 3 | B validation rho 0.522355, MSE 0.140323; C validation rho 0.305132, MSE 0.140940 |
