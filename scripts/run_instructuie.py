"""Run the actual pinned InstructUIE checkpoint on source-only extraction inputs.

Input: JSON list (or {"items": [...]}) of {id, passage, condition, relations}.
The relations field is an explicit list of schema labels for this experiment.
No similarity ratings, reference evidence, or encoder scores are model inputs.
"""

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

MODEL = "ZWK/InstructUIE"
REVISION = "48f45b25a01df1798f8c1c31751a973adb7e8647"
INSTRUCTION = (
    "Given a sentence, please extract the subject and object containing a certain "
    "relation in the sentence according to the following relation types, in the "
    'format of "relation1: word1, word2; relation2: word3, word4". \n'
)


def prompt_for(item):
    """Use the official RE instruction/options/text/answer serialization."""
    if not isinstance(item.get("passage"), str) or not item["passage"].strip():
        raise ValueError("A nonempty passage is required.")
    relations = item.get("relations")
    if not isinstance(relations, list) or not relations or not all(
        isinstance(label, str) and label.strip() for label in relations
    ):
        raise ValueError("Supply explicit relation labels, e.g. ['has color'].")
    return (
        INSTRUCTION
        + "Option: " + ", ".join(relations)
        + " \nText: " + item["passage"] + " \nAnswer:"
    )


def parse_relations(raw):
    """Keep raw output; surface malformed fragments in parse warnings."""
    if raw.strip().casefold() in {"none", "none."}:
        return [], []
    triples, warnings = [], []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part or "," not in part.split(":", 1)[1]:
            warnings.append(part)
            continue
        relation, args = part.split(":", 1)
        head, tail = args.split(",", 1)
        triples.append({"head": head.strip(), "relation": relation.strip(),
                        "tail": tail.strip()})
    return triples, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--dtype", choices=["float32", "float16", "bfloat16"],
                        default="float16")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    raw_inputs = args.inputs.read_bytes()
    items = json.loads(raw_inputs)
    if isinstance(items, dict):
        items = items["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("Expected nonempty extraction inputs.")
    prompts = [prompt_for(item) for item in items]
    manifest = {
        "model_id": args.model, "revision": args.revision,
        "input_sha256": hashlib.sha256(raw_inputs).hexdigest(),
        "items": len(items), "generation": {"do_sample": False, "num_beams": 1,
        "max_new_tokens": args.max_new_tokens},
        "schema_scope": "User-supplied relation labels; out-of-domain schema transfer",
        "prompt_source": "BeyonderXX/InstructUIE configs/instruction_config.json RE[2] "
                         "and src/uie_dataset.py RE serialization",
    }
    missing = [name for name in ["torch", "transformers", "accelerate", "sentencepiece"]
               if importlib.util.find_spec(name) is None]
    if not args.execute or missing:
        manifest.update(status="blocked_missing_dependencies" if missing else "planned",
                        missing_dependencies=missing, outputs_generated=0)
        print(json.dumps(manifest, indent=2))
        return 2 if missing and args.execute else 0
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; actual model was not executed.")
    tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model, revision=args.revision,
        torch_dtype=getattr(torch, args.dtype),
        device_map={"": args.device}, low_cpu_mem_usage=True,
    ).eval()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        for item, prompt in zip(items, prompts):
            batch = tokenizer(prompt, return_tensors="pt", truncation=False)
            if batch["input_ids"].shape[1] > 512:
                raise ValueError("Input exceeds official 512-token limit; no silent truncation.")
            batch = {key: value.to(model.device) for key, value in batch.items()}
            with torch.inference_mode():
                ids = model.generate(**batch, **manifest["generation"])
            raw = tokenizer.decode(ids[0], skip_special_tokens=True)
            triples, warnings = parse_relations(raw)
            output.write(json.dumps({"id": item["id"], "condition": item.get("condition"),
                "passage": item["passage"], "relations": item["relations"],
                "prompt": prompt, "raw_output": raw, "triples": triples,
                "parse_warnings": warnings, "model_id": args.model,
                "revision": args.revision}, ensure_ascii=False) + "\n")
            output.flush()
    manifest.update(status="complete", outputs_generated=len(items))
    args.output.with_suffix(args.output.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
