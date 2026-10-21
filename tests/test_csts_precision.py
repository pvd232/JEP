"""Ensure optimizer updates reach forwards under the enclosing worker context."""

import pytest
import torch

from csts_pilot.training import CstsConfig, mixed_precision


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA precision regression")
def test_updated_weights_are_visible_under_outer_autocast_context():
    layer = torch.nn.Linear(4, 4, bias=False, device="cuda")
    values = torch.ones(1, 4, device="cuda")
    with torch.no_grad():
        layer.weight.copy_(torch.eye(4, device="cuda"))
    with torch.autocast("cuda", enabled=False):
        with mixed_precision(CstsConfig()):
            before = layer(values).detach().float()
        with torch.no_grad():
            layer.weight.mul_(2)
        with mixed_precision(CstsConfig()):
            after = layer(values).detach().float()
    torch.testing.assert_close(after, 2 * before)
