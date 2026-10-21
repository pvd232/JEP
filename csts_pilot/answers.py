"""Generate condition-specific evidence spans without exposing similarity labels."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import torch
from pydantic import Field
from transformers import AutoModelForCausalLM, AutoTokenizer
from viper.config import BuildConfig
from viper.stages import StageContext, build

from csts_pilot.data import canonical
from csts_pilot.training import write_json
from jep_pilot.loaders import load_json

TEACHER = "Qwen/Qwen3-4B-Instruct-2507"
TEACHER_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
PROMPT = (
    "Extract the shortest phrase from the caption that answers the comparison "
    "question or describes the comparison aspect. Copy one exact contiguous "
    "phrase from the caption. Preserve qualifications. Return only the phrase, "
    "without quotation marks. If the caption does not specify the answer, "
    "return NOT_SPECIFIED.\nAspect: {condition}\nCaption: {passage}"
)


def answer_id(passage: str, condition: str) -> str:
    """Identify a caption and condition independently of pair membership."""
    value = json.dumps([canonical(passage), canonical(condition)])
    return hashlib.sha256(value.encode()).hexdigest()


def validated_answer(passage: str, answer: str) -> tuple[str, bool]:
    """Accept copied evidence and retain rejected generations for auditing."""
    answer = answer.strip().strip('"').strip()
    valid = bool(answer) and canonical(answer) in canonical(passage)
    if answer == "NOT_SPECIFIED":
        valid = False
    return answer, valid


class AnswerConfig(BuildConfig):
    """Pin the teacher and bound generation for the annotation stage."""

    batch_size: int = Field(default=32, ge=1)
    max_new_tokens: int = Field(default=32, ge=1)
    limit: int | None = None


@build(config=AnswerConfig)
def annotate(context: StageContext[AnswerConfig]) -> None:
    """Write answers for training and development captions as native artifacts."""
    records: dict[str, dict[str, Any]] = {}
    partitions: dict[str, list[dict[str, Any]]] = {}
    for split in ("training", "development"):
        rows = load_json(context.inputs[split])
        partitions[split] = rows
        for row in rows:
            for side in ("sentence1", "sentence2"):
                key = answer_id(row[side], row["condition"])
                records.setdefault(
                    key,
                    {"id": key, "passage": row[side], "condition": row["condition"]},
                )
    items = sorted(records.values(), key=lambda row: row["id"])
    if context.config.limit is not None:
        items = items[: context.config.limit]
    tokenizer = AutoTokenizer.from_pretrained(TEACHER, revision=TEACHER_REVISION)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    teacher = AutoModelForCausalLM.from_pretrained(
        TEACHER, revision=TEACHER_REVISION, dtype=torch.bfloat16
    ).to("cuda")
    teacher.eval()
    prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": PROMPT.format(**row)}],
            tokenize=False,
            add_generation_prompt=True,
        )
        for row in items
    ]
    # Tokenize once. Only each active batch and its generation cache enter VRAM.
    encoded = tokenizer(prompts, padding=True, return_tensors="pt")
    output_path = context.outputs["answers"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.monotonic()
    accepted = 0
    torch.cuda.reset_peak_memory_stats()
    with output_path.open("w") as stream, torch.inference_mode():
        for start in range(0, len(items), context.config.batch_size):
            stop = start + context.config.batch_size
            batch = {
                name: value[start:stop].to("cuda") for name, value in encoded.items()
            }
            generated = teacher.generate(
                **batch,
                do_sample=False,
                max_new_tokens=context.config.max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                use_cache=True,
            )
            answers = tokenizer.batch_decode(
                generated[:, batch["input_ids"].shape[1] :], skip_special_tokens=True
            )
            for row, answer in zip(items[start:stop], answers, strict=True):
                answer, valid = validated_answer(row["passage"], answer)
                stream.write(json.dumps(dict(row, answer=answer, valid=valid)) + "\n")
                accepted += int(valid)
            stream.flush()
            print(
                json.dumps(
                    {
                        "completed": min(stop, len(items)),
                        "total": len(items),
                        "accepted": accepted,
                        "seconds": time.monotonic() - start_time,
                    }
                ),
                flush=True,
            )
    write_json(
        context.outputs["manifest"],
        {
            "teacher": TEACHER,
            "revision": TEACHER_REVISION,
            "prompt": PROMPT,
            "configuration": context.config.model_dump(),
            "unique_caption_conditions": len(items),
            "accepted_extractive_answers": accepted,
            "accepted_fraction": accepted / len(items),
            "seconds": time.monotonic() - start_time,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
            "checks": "Exact source span only. Semantic relevance requires review.",
            "label_source": "Teacher generated. No human answer annotations.",
        },
    )


def load_answers(path: Path) -> dict[str, dict[str, Any]]:
    """Load one immutable answer artifact for the student training stage."""
    return {
        row["id"]: row
        for line in path.read_text().splitlines()
        if (row := json.loads(line))
    }
