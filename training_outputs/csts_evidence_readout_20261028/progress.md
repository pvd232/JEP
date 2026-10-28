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
