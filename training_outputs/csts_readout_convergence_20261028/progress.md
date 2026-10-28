# JEP readouts trained to a validation plateau

Status: prepared. The Mac connection used for Colab terminated during final checks. Native CPU transport and scientific launch await reconnection.

The study fits B and C at learning rates 0.00001, 0.00003 and 0.0001 with seeds 7, 8 and 9. Each fit continues until ten epochs pass without validation improvement. It then fits D, E and the same comparison function on A's final vectors. Learning rate selection uses validation.

[Methods and selection rules](../../plans/csts-readout-convergence-methods.md). The initial check passed 72 tests. This file will receive live epoch measurements and final scores from the existing Colab A100.
