# Test and validation results

Mean ± sample SD across the same five paired seeds. Validation selected every checkpoint before test inference.

| Prompt | Validation Spearman | Test Spearman |
| --- | ---: | ---: |
| A_condition_first | 0.874465 ± 0.001630 | 0.852208 ± 0.002541 |
| B_order_only | 0.873737 ± 0.002648 | 0.855385 ± 0.004213 |
| C_case_inspired | 0.875097 ± 0.001532 | 0.853567 ± 0.003981 |

Validation: 1,576 comparisons. Test: 2,430 comparisons in 1,222 source groups.

| Test contrast | Mean paired difference | Positive seed pairs | Conditional 95% group-bootstrap interval |
| --- | ---: | ---: | --- |
| B-A | +0.003177 | 4/5 | [-0.005175, +0.011577] |
| C-A | +0.001359 | 3/5 | [-0.006689, +0.009513] |
| C-B | -0.001819 | 2/5 | [-0.007148, +0.003335] |

Intervals use 10,000 shared source-group bootstrap draws (seed 610707), averaging paired within-seed differences. They condition on these checkpoints. The JSON also retains 97.5% intervals for the two primary contrasts. Five seed pairs provide limited information about training-population uncertainty.

This test partition was examined in earlier work. Treat the comparison as exploratory. No test scores were used to choose checkpoints or extend training.

[Per-trial scores](test_and_validation.csv) · [Full statistics](test_and_validation.json)
