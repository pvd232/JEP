# C-STS COLOR clustering results

The conditioned fine-tuned encoder preserves explicit target-color structure strongly in this cohort. It leads both controls in color agreement and original-pair cosine similarity. All 13440 seeded fits completed below the 500-iteration cap, with no undefined fits.

The dataset contributes 531 color-related pairs and 1,017 unique condition/sentence inputs. Validation is the primary analysis: 65 single-color points, 13 represented colors, and 74 original pairs for Spearman. Three encoder arms share the same frozen input cohort.

| Encoder | Median ARI at C | Seed IQR | K selected by silhouette | Median silhouette at selected K | Pair Spearman |
|---|---:|---|---:|---:|---:|
| Fine-tuned, conditioned | 0.9184 | 0.9013–0.9525 | 12 | 0.8012 | 0.8580 |
| Pretrained, conditioned | 0.3427 | 0.3205–0.3751 | 26 | 0.2266 | 0.2196 |
| Fine-tuned, condition omitted | 0.0982 | 0.0758–0.1185 | 26 | 0.2476 | -0.3436 |

The test single-color cohort has 119 points and 11 colors. The conditioned fine-tuned encoder has ARI 0.9431 and selects K=11; its original-pair test Spearman is 0.8690 across 121 pairs. The validation controls select the upper search boundary, K=26. These are within-grid selections.

## K and cohort composition

K is selected by the greatest median cosine silhouette over 20 seeds, with the fixed smaller-K tie rule. The sweep covers every integer from 2 through twice the cohort’s single-color count. “Near C” means an absolute difference of at most max(1, ceil(0.25 C)).

| Cohort | Points | C | Fine-tuned conditioned K | Within accepted tolerance |
|---|---:|---:|---:|---|
| validation_single | 65 | 13 | 12 | Yes |
| validation_all | 137 | 13 | 25 | No |
| train_single | 313 | 17 | 12 | Yes |
| train_all | 641 | 17 | 16 | Yes |
| test_single | 119 | 11 | 11 | Yes |
| test_all | 239 | 11 | 21 | No |
| pooled_single | 497 | 17 | 12 | Yes |
| pooled_all | 1017 | 17 | 20 | Yes |

The single-color validation and test results support the color-count hypothesis. Train and pooled single-color cohorts select 12 clusters for 17 colors; their rare named colors remain separate reference labels. Validation and test mixed cohorts favor larger K. K selection varies with cohort composition.

## Paired uncertainty

The 1,000 paired draws resample connected-caption families and rescore the retained fits. These percentile intervals describe uncertainty conditional on those fits; all draws were valid.

| Main minus control | ARI difference | 95% interval | Spearman difference | 95% interval |
|---|---:|---|---:|---|
| Pretrained, conditioned | 0.5757 | [0.3522, 0.6226] | 0.6383 | [0.4150, 0.8552] |
| Fine-tuned, condition omitted | 0.8202 | [0.5918, 0.8065] | 1.2016 | [0.9241, 1.4457] |

The omitted-condition ARI difference exceeds its percentile interval. Family resampling shifts this fixed-fit ARI distribution relative to the full cohort; treat the interval as a descriptive resampling diagnostic. The paired-interval plot marks the actual full-cohort estimates.

## Condition switching

The 50 source-derived probes describe two explicitly colored objects in the same sentence. Prototypes exclude the probe’s full caption family and require five other families per color. Forty-seven probes are eligible; beige, purple and silver coverage excludes the remaining three.

| Encoder | Both target-direction margins positive | Mean bidirectional margin |
|---|---:|---:|
| Fine-tuned, conditioned | 47/47 | 0.8138 |
| Pretrained, conditioned | 14/47 | 0.0567 |
| Fine-tuned, condition omitted | 0/47 | ≈0 |

The omitted-condition mean margin is −0.0000484.

## Labels and scope

Reference annotations are provisional, derived from explicit source spans with assistant review of target-binding rules, 70 initial assignments, 41 risk-flagged examples and the probe examples. They were frozen before encoder execution. The 1,017 points contain 497 single-color, 232 multiple-color, 218 unresolved and 70 unspecified cases. Named colors stay distinct; light/dark modifiers are stored separately. The independent pair endpoint uses the published audited similarity ratings.

These results support explicit conditional color similarity. Implicit semantics and JEP-domain transfer remain useful follow-up experiments. All split and pooled results in this first run are exploratory.

## Review files and reproducibility

Open diagnostics.pdf for every indexed plot, or extract the review archive and open dashboard.html to filter by split, encoder and diagnostic. PNG and SVG versions, every K/seed metric and assignment, representative point diagnostics, cluster exemplars, cross-family neighbors, pair scores, source evidence and the vectors are retained. PCA is an inspection view; fits and numeric scores use normalized 4096-dimensional vectors.

Native VIPER executes and verifies separate embedding, clustering and reporting stages. Local evidence satisfies completion. A separate durable worker exports a local portable outbox and uploads it asynchronously; cloud status never gates the experiment or review delivery. Exact native references, output hashes and upload status are retained in provenance/.

The encoder is the existing proposition_final.pt checkpoint, SHA-256 d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f, on Qwen/Qwen3-Embedding-8B revision c90816d848505624c2434128dfc61132162a0ee9. The archived 0.865230 result averages three learned-comparator fits on this encoder; its archived raw-cosine test Spearman is 0.863398. This experiment measures the frozen vectors and raw cosine.

Dataset: [JEP C-STS revision 1.1](https://github.com/pvd232/JEP/tree/5dde4314e90f92eb4ac84b122e3b312402b18931/datasets/csts-jep-revision-v1-1). Embedding/clustering source: [072289a](https://github.com/pvd232/JEP/tree/072289a86276349914f9484c6ada269fa199450e). Report source: [c09d6a4](https://github.com/pvd232/JEP/tree/c09d6a4c7cae5a54a559df88bb37c03b04c95227). Accepted methods and asynchronous replication: [experiment branch](https://github.com/pvd232/JEP/tree/experiment/csts-color-clustering-20261104).
