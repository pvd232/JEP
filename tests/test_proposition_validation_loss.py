"""Check proposition loss against independent log probabilities on a small CPU model."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import torch
from csts_pilot.qwen_evidence import answer_loss_sum
from torch import nn

from scripts import evaluate_proposition_checkpoints as evaluation


class ValidationLossTests(unittest.TestCase):
    """Keep prefix masking and equal-answer weighting observable without a GPU."""

    def test_prefix_and_padding_are_excluded_and_answers_receive_equal_weight(self):
        """Variable-length answers contribute their own mean losses, including the EOD target."""
        hidden = torch.tensor(
            [
                [[3.0, 0.0], [0.0, 2.0], [1.0, 0.0], [0.0, 0.0]],
                [[0.0, 4.0], [2.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            ]
        )
        labels = torch.tensor([[-100, -100, 1, 0], [-100, 1, -100, -100]])
        actual = answer_loss_sum(hidden, labels, nn.Identity()) / 2
        logs = hidden.log_softmax(-1)
        expected = ((-logs[0, 1, 1] - logs[0, 2, 0]) / 2 - logs[1, 0, 1]) / 2
        self.assertAlmostEqual(float(actual), float(expected), places=6)

    def test_completed_loss_survives_a_generation_failure(self):
        """Resuming generation and rebuilding a report reuse the completed loss forward."""
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            model = Mock(return_value=SimpleNamespace(last_hidden_state=torch.ones(1)))
            fit = SimpleNamespace(device="cpu")
            args = (
                model,
                None,
                None,
                fit,
                {"id": "a"},
                ([1, 2], [-100, 1]),
                {"checkpoint_sha256": "frozen"},
                destination,
                True,
            )
            with (
                patch.object(evaluation, "pad_sequences", return_value={}),
                patch.object(
                    evaluation, "answer_loss_sum", return_value=torch.tensor(1.25)
                ),
                patch.object(
                    evaluation,
                    "generate",
                    side_effect=RuntimeError("generation interrupted"),
                ),
                self.assertRaises(RuntimeError),
            ):
                evaluation.measure_one(*args)
            self.assertTrue((destination / "a.json").exists())
            with patch.object(
                evaluation, "generate", return_value={"answer": "red"}
            ) as generated:
                evaluation.measure_one(*args)
                evaluation.measure_one(*args)
                generated.assert_called_once()
            self.assertEqual(model.call_count, 1)


if __name__ == "__main__":
    unittest.main()
