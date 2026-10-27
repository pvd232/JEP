"""Verify fixed-step gradient accumulation and fresh optimizer boundaries on CPU."""

import unittest
from types import SimpleNamespace

import torch
from torch import nn

from csts_pilot.proposition_indicative import fixed_batches, fixed_updates


class IndicativeUpdatesTests(unittest.TestCase):
    def test_microbatch_accumulation_matches_fullbatch_and_resets_optimizer(self):
        x, y = (
            torch.tensor([[1.0], [2.0], [3.0], [4.0]]),
            torch.tensor([[2.0], [4.0], [6.0], [8.0]]),
        )
        batches = [[0, 1], [2, 3]]
        terminal = []
        for microbatch in (1, 2):
            model = nn.Linear(1, 1, bias=False)
            with torch.no_grad():
                model.weight.fill_(0.5)
            config = SimpleNamespace(
                learning_rate=0.02, weight_decay=0.01, microbatch_size=microbatch
            )
            trace = []

            def loss(micro, whole, model=model):
                return nn.functional.mse_loss(
                    model(x[micro]), y[micro], reduction="sum"
                ) / len(whole)

            optimizer = fixed_updates(model, batches, config, loss, trace.append)
            self.assertEqual([item["step"] for item in trace], [1, 2])
            self.assertTrue(all(item["gradient_norm"] > 0 for item in trace))
            self.assertTrue(
                all(float(state["step"]) == 2 for state in optimizer.state.values())
            )
            terminal.append(model.weight.detach().clone())
            new_optimizer = fixed_updates(
                model, batches[:1], config, loss, lambda item: None
            )
            self.assertTrue(
                all(float(state["step"]) == 1 for state in new_optimizer.state.values())
            )
        torch.testing.assert_close(terminal[0], terminal[1], atol=1e-7, rtol=0)
        self.assertGreater(float(terminal[0].item()), 0.5)

    def test_fixed_batches_are_reproducible_and_do_not_repeat_sources(self):
        first = fixed_batches(100, 3, 8, 7)
        self.assertEqual(first, fixed_batches(100, 3, 8, 7))
        self.assertEqual(len({index for batch in first for index in batch}), 24)
        self.assertNotEqual(first, fixed_batches(100, 3, 8, 8))
        with self.assertRaises(ValueError):
            fixed_batches(10, 2, 8, 7)

    def test_nonfinite_loss_stops_before_an_optimizer_update(self):
        model = nn.Linear(1, 1)
        before = {
            name: parameter.detach().clone()
            for name, parameter in model.named_parameters()
        }
        config = SimpleNamespace(
            learning_rate=0.02, weight_decay=0.01, microbatch_size=1
        )
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            fixed_updates(
                model,
                [[0]],
                config,
                lambda micro, whole: model.weight.sum() * float("nan"),
                lambda item: None,
            )
        for name, parameter in model.named_parameters():
            torch.testing.assert_close(parameter, before[name], atol=0, rtol=0)


if __name__ == "__main__":
    unittest.main()
