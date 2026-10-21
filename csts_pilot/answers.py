"""Generate condition-specific evidence spans without exposing similarity labels."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import torch
from csts_pilot.data import canonical
from csts_pilot.training import write_json
from jep_pilot.loaders import load_json
from pydantic import Field
from transformers import AutoModelForCausalLM, AutoTokenizer
from viper.config import BuildConfig
from viper.stages import StageContext, build

TEACHER = "Qwen/Qwen3-8B"
TEACHER_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"
PROMPT = """Extract the caption's answer to the aspect question.
First identify the entity the question concerns and the attribute requested.
Return JSON with exactly three string fields: target, attribute, evidence.
The evidence must copy one contiguous span of the caption that supplies the
requested value for the correct entity. Copy enough words to preserve ALL
relevant entities, values, relations and qualifications. A whole sentence is
allowed when the answer spans several clauses.
For a number, include every instance of the requested entity. Singular nouns
can establish one instance. A bare plural such as 'people' supplies no count.
For a color, copy the color of the requested entity. Check which noun it modifies.
A breed, age, room type, named place or purpose requires explicit support.
When the requested value is absent or its entity is unclear, evidence must be
NOT_SPECIFIED. Return only the JSON.

Aspect: color of ball
Caption: A boy in a red shirt throws a ball.
{{"target":"ball","attribute":"color","evidence":"NOT_SPECIFIED"}}

Aspect: number of dogs
Caption: Two dogs run while a third dog sleeps.
{{"target":"dogs","attribute":"number","evidence":"Two dogs run while a third dog sleeps"}}

Aspect: number of people
Caption: A young boy carries a basket.
{{"target":"people","attribute":"number","evidence":"A young boy"}}

Aspect: dog breed
Caption: A big brown dog jumps over a log.
{{"target":"dog","attribute":"breed","evidence":"NOT_SPECIFIED"}}

Aspect: color of uniform
Caption: A player wears a red and black uniform.
{{"target":"uniform","attribute":"color","evidence":"red and black"}}

TARGET
Aspect: {condition}
Caption: {passage}
JSON:"""

REVIEW_PROMPT = """Check whether the proposed evidence answers the aspect question.
Read the ENTIRE caption before deciding. Return JSON with boolean accept and
a short reason. Accept when the evidence supplies the requested value for the
correct entity and preserves all relevant values and qualifications.
Reject if the value is absent, the question's entity is unclear, the evidence
describes another entity, or the evidence omits a relevant entity or value.
For number questions, count every mentioned instance of the requested kind.
A bare plural supplies no count. A selected singular noun is incomplete when
the caption also mentions other people or animals of the requested kind.
A full caption can be valid evidence. General words such as 'sporting event'
supply no particular game. A description of reading a book supplies no evidence
about aids used or their absence. Broad questions about object type require
all the caption's relevant object types.

Aspect: {condition}
Caption: {passage}
Proposed evidence: {answer}
JSON:"""


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


def parse_response(passage: str, response: str) -> dict[str, Any]:
    """Retain the teacher record and reject malformed or unsupported evidence."""
    try:
        record = json.loads(response)
    except (ValueError, TypeError):
        record = None
    required = ("target", "attribute", "evidence")
    if not isinstance(record, dict) or any(
        not isinstance(record.get(key), str) for key in required
    ):
        return {"answer": "", "valid": False, "response": response}
    answer, valid = validated_answer(passage, record["evidence"])
    return {
        "answer": answer,
        "valid": valid,
        "target": record["target"],
        "attribute": record["attribute"],
        "response": response,
    }


def review_accepts(response: str) -> bool:
    """Accept only an explicit, well-formed affirmative verifier judgment."""
    try:
        record = json.loads(response)
    except (ValueError, TypeError):
        return False
    return isinstance(record, dict) and record.get("accept") is True


def completed_prefix(
    path: Path, items: list[dict[str, Any]], batch_size: int
) -> list[dict[str, Any]]:
    """Validate saved answers against the exact ordered inputs and audit rules."""
    with path.open() as stream:
        saved = [json.loads(line) for line in stream if line.strip()]
    if len(saved) > len(items) or (len(saved) < len(items) and len(saved) % batch_size):
        raise ValueError("Saved answers must end at a complete generation batch.")
    for index, record in enumerate(saved):
        if any(
            record.get(key) != items[index][key]
            for key in ("id", "passage", "condition")
        ):
            raise ValueError(f"Saved answer {index} differs from its ordered input.")
        if type(record.get("valid")) is not bool:
            raise ValueError(f"Saved answer {index} has no acceptance decision.")
        if record["valid"]:
            parsed = parse_response(record["passage"], record.get("response", ""))
            if (
                not parsed["valid"]
                or parsed["answer"] != record.get("answer")
                or not review_accepts(record.get("review_response", ""))
            ):
                raise ValueError(f"Saved answer {index} fails the original checks.")
    return saved


class AnswerConfig(BuildConfig):
    """Pin the teacher and bound generation for the annotation stage."""

    batch_size: int = Field(default=16, ge=1)
    max_new_tokens: int = Field(default=128, ge=1)
    review_max_new_tokens: int = Field(default=96, ge=1)
    limit: int | None = None
    offset: int = Field(default=0, ge=0)


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
        items = items[
            context.config.offset : context.config.offset + context.config.limit
        ]
    prior = context.inputs.get("completed_answers")
    saved = completed_prefix(prior, items, context.config.batch_size) if prior else []
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
            enable_thinking=False,
        )
        for row in items
    ]
    # Tokenize once. Only each active batch and its generation cache enter VRAM.
    encoded = tokenizer(prompts, padding=True, return_tensors="pt")
    output_path = context.outputs["answers"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.monotonic()
    accepted = sum(int(row["valid"]) for row in saved)
    torch.cuda.reset_peak_memory_stats()
    with output_path.open("w") as stream, torch.inference_mode():
        for row in saved:
            stream.write(json.dumps(row) + "\n")
        stream.flush()
        print(
            json.dumps(
                {
                    "completed": len(saved),
                    "total": len(items),
                    "accepted": accepted,
                    "cached": len(saved),
                    "seconds": 0,
                }
            ),
            flush=True,
        )
        for start in range(len(saved), len(items), context.config.batch_size):
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
            records = [
                dict(row, **parse_response(row["passage"], response))
                for row, response in zip(items[start:stop], answers, strict=True)
            ]
            candidates = [row for row in records if row["valid"]]
            if candidates:
                review_prompts = [
                    tokenizer.apply_chat_template(
                        [{"role": "user", "content": REVIEW_PROMPT.format(**row)}],
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    )
                    for row in candidates
                ]
                review_batch = tokenizer(
                    review_prompts, padding=True, return_tensors="pt"
                ).to("cuda")
                reviewed = teacher.generate(
                    **review_batch,
                    do_sample=False,
                    max_new_tokens=context.config.review_max_new_tokens,
                    pad_token_id=tokenizer.pad_token_id,
                    use_cache=True,
                )
                reviews = tokenizer.batch_decode(
                    reviewed[:, review_batch["input_ids"].shape[1] :],
                    skip_special_tokens=True,
                )
                for row, review in zip(candidates, reviews, strict=True):
                    row["source_span_valid"] = True
                    row["review_response"] = review
                    row["valid"] = review_accepts(review)
            for row in records:
                stream.write(json.dumps(row) + "\n")
                accepted += int(row["valid"])
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
            "review_prompt": REVIEW_PROMPT,
            "configuration": context.config.model_dump(),
            "generation": {"do_sample": False, "enable_thinking": False},
            "unique_caption_conditions": len(items),
            "accepted_extractive_answers": accepted,
            "accepted_fraction": accepted / len(items),
            "reused_answers": len(saved),
            "generated_this_attempt": len(items) - len(saved),
            "completed_input_sha256": hashlib.sha256(prior.read_bytes()).hexdigest()
            if prior
            else None,
            "seconds": time.monotonic() - start_time,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
            "checks": "Exact source span and a second teacher check. Semantic relevance requires an independent pilot audit.",
            "label_source": "Teacher generated. No human answer annotations.",
        },
    )
