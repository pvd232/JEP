"""Check shared gradients, masked answers and source-span supervision."""

import torch
from torch import nn
from transformers import T5Config, T5ForConditionalGeneration

from csts_pilot.answers import answer_id, validated_answer
from csts_pilot.joint import AnswerEncoder


def tiny_model() -> AnswerEncoder:
    """Build the same heads with a small offline T5 for gradient checks."""
    model = AnswerEncoder.__new__(AnswerEncoder)
    nn.Module.__init__(model)
    config = T5Config(
        vocab_size=20,
        d_model=16,
        d_ff=32,
        num_layers=1,
        num_decoder_layers=1,
        num_heads=2,
        d_kv=8,
        dropout_rate=0,
        pad_token_id=0,
        eos_token_id=1,
    )
    config.decoder_start_token_id = 0
    model.t5 = T5ForConditionalGeneration(config)
    model.projection = nn.Linear(16, 8, bias=False)
    return model


def test_both_objectives_reach_shared_encoder():
    model = tiny_model()
    batch = {
        "input_ids": torch.tensor([[2, 3, 4, 1], [5, 6, 7, 1]]),
        "attention_mask": torch.ones(2, 4, dtype=torch.long),
        "pool_mask": torch.tensor([[0, 1, 1, 0], [0, 1, 1, 0]], dtype=torch.bool),
    }
    z, hidden = model.encode(batch)
    mse = ((z[0] * z[1]).sum() - 0.2).square()
    ce = model.answer_loss(
        hidden, batch["attention_mask"], torch.tensor([[3, 1], [6, 1]])
    )
    shared = model.t5.encoder.block[0].layer[0].SelfAttention.q.weight
    rating_gradient = torch.autograd.grad(mse, shared, retain_graph=True)[0]
    answer_gradient = torch.autograd.grad(ce, shared, retain_graph=True)[0]
    assert rating_gradient.norm() > 0
    assert answer_gradient.norm() > 0
    assert (
        torch.autograd.grad(ce, model.projection.weight, allow_unused=True)[0] is None
    )


def test_unaccepted_answer_contributes_zero_cross_entropy():
    model = tiny_model()
    inputs = torch.tensor([[2, 3, 4, 1], [5, 6, 7, 1]])
    mask = torch.ones_like(inputs)
    hidden = model.t5.encoder(input_ids=inputs, attention_mask=mask).last_hidden_state
    labels = torch.tensor([[3, 1], [-100, -100]])
    both = model.answer_loss(hidden, mask, labels)
    accepted = model.answer_loss(hidden[:1], mask[:1], labels[:1])
    torch.testing.assert_close(both, accepted)


def test_answer_identity_and_source_validation():
    assert answer_id("A blue shirt.", "clothing") != answer_id(
        "A blue shirt.", "location"
    )
    assert validated_answer("A blue shirt.", "blue shirt") == ("blue shirt", True)
    assert validated_answer("A blue shirt.", "red shirt")[1] is False
    assert validated_answer("A blue shirt.", "NOT_SPECIFIED")[1] is False
