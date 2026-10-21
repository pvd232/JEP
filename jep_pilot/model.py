"""Share a T5 encoder between annotation generation and similarity prediction."""

import re
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer, T5Config, T5ForConditionalGeneration
from transformers.modeling_outputs import BaseModelOutput


def words(text: str) -> list[str]:
    """Tokenize the tiny offline diagnostic deterministically."""
    return re.findall(r"[\wáéíóúñü]+|[;:]", text.lower())


class JointModel(nn.Module):
    """Expose one trainable encoder to both losses."""

    def __init__(self, spec: dict[str, Any]) -> None:
        """Build either an offline tiny T5 or a pinned pretrained T5."""
        super().__init__()
        self.spec = spec
        if spec["mode"] == "tiny":
            self.tokenizer = None
            self.vocab = spec["vocab"]
            config = T5Config(
                vocab_size=len(self.vocab),
                d_model=32,
                d_ff=64,
                num_layers=1,
                num_decoder_layers=1,
                num_heads=2,
                d_kv=16,
                dropout_rate=0.0,
                pad_token_id=0,
                eos_token_id=1,
            )
            config.decoder_start_token_id = 0
            self.t5 = T5ForConditionalGeneration(config)
        else:
            self.vocab = {}
            self.tokenizer = AutoTokenizer.from_pretrained(
                spec["model_id"], revision=spec["revision"]
            )
            self.t5 = T5ForConditionalGeneration.from_pretrained(
                spec["model_id"], revision=spec["revision"]
            )
        self.projection = nn.Linear(self.t5.config.d_model, 32, bias=False)

    @property
    def device(self) -> torch.device:
        """Return the model's current device."""
        return self.projection.weight.device

    def tokenize(
        self, texts: list[str], *, targets: bool = False
    ) -> dict[str, torch.Tensor]:
        """Create padded source or output token tensors."""
        limit = 112 if targets else 160
        if self.tokenizer is not None:
            batch = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=limit,
                return_tensors="pt",
            )
            return {
                k: v.to(self.device)
                for k, v in batch.items()
                if k in {"input_ids", "attention_mask"}
            }
        ids = [
            [self.vocab.get(t, 2) for t in words(s)[: limit - 1]] + [1] for s in texts
        ]
        width = max(map(len, ids))
        padded = torch.tensor(
            [r + [0] * (width - len(r)) for r in ids], device=self.device
        )
        return {"input_ids": padded, "attention_mask": padded.ne(0).long()}

    def representations(self, texts: list[str], questions: list[str]) -> tuple:
        """Encode each passage with its question and pool contextual token states."""
        inputs = [
            f"Condición: {q} Pasaje: {x}" for x, q in zip(texts, questions, strict=True)
        ]
        batch = self.tokenize(inputs)
        hidden = self.t5.encoder(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp_min(1)
        z = F.normalize(self.projection(pooled), dim=-1)
        return z, hidden, batch["attention_mask"]

    def losses(
        self, rows: list[dict], *, shuffled: dict[str, str] | None = None
    ) -> tuple:
        """Compute cosine MSE and mean per-answer annotation cross-entropy."""
        sides = [r[side] for side in ("left", "right") for r in rows]
        questions = [r["question"] for r in rows] * 2
        z, hidden, mask = self.representations([r["text"] for r in sides], questions)
        left, right = z.chunk(2)
        scores = (1 + (left * right).sum(-1)) / 2
        targets = torch.tensor([r["target"] for r in rows], device=self.device)
        mse = F.mse_loss(scores, targets)
        answers = [
            shuffled[r["case_id"]] if shuffled else r["annotation"] for r in sides
        ]
        answer_batch = self.tokenize(answers, targets=True)
        labels = answer_batch["input_ids"].masked_fill(
            answer_batch["attention_mask"].eq(0), -100
        )
        decoded = self.t5(
            encoder_outputs=BaseModelOutput(last_hidden_state=hidden),
            attention_mask=mask,
            labels=labels,
            use_cache=False,
        )
        token_loss = F.cross_entropy(
            decoded.logits.transpose(1, 2), labels, ignore_index=-100, reduction="none"
        )
        valid = labels.ne(-100)
        annotation_loss = (
            (token_loss * valid).sum(1) / valid.sum(1).clamp_min(1)
        ).mean()
        return mse, annotation_loss, scores

    @torch.no_grad()
    def score(self, rows: list[dict]) -> list[float]:
        """Score held-out passage pairs without their annotation targets."""
        sides = [r[side] for side in ("left", "right") for r in rows]
        questions = [r["question"] for r in rows] * 2
        z, _, _ = self.representations([r["text"] for r in sides], questions)
        left, right = z.chunk(2)
        return ((1 + (left * right).sum(-1)) / 2).cpu().tolist()


def tiny_spec(rows: list[dict]) -> dict:
    """Fix a training-only vocabulary for the offline implementation check."""
    texts = [
        text
        for r in rows
        for text in (
            r["question"],
            r["left"]["text"],
            r["right"]["text"],
            r["left"]["annotation"],
            r["right"]["annotation"],
        )
    ]
    vocabulary = ["<pad>", "</s>", "<unk>"] + sorted(
        set(words(" ".join(texts) + " Condición Pasaje"))
    )
    return {"mode": "tiny", "vocab": {t: i for i, t in enumerate(vocabulary)}}
