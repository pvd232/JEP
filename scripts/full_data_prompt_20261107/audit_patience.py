"""Replay positive validation-patience counts on retained, validation-only curves."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from csts_pilot.early_stopping import ValidationPatience

def replay(epochs, patience):
    """Stop at the first exhausted counter while retaining the best checkpoint seen."""
    stopping=ValidationPatience(patience=patience,min_delta=0.0)
    selected=None
    stopped=False
    for position,row in enumerate(epochs):
        score=row["validation_spearman"]
        if selected is None or score>selected["validation_spearman"]:
            selected=row
        if stopping.observe(score):
            stopped=True
            break
    return {"stop_epoch":row["epoch"],"selected_epoch":selected["epoch"],
            "validation_spearman":selected["validation_spearman"],
            "epochs_consumed":position+1,"stop_observed":stopped}

def analyze(data):
    """Compare strict first-non-improvement stopping with each curve's observed peak."""
    results=[]
    for curve in data["curves"]:
        epochs=curve["epochs"]
        if not epochs or [r["epoch"] for r in epochs]!=list(range(1,len(epochs)+1)):
            raise ValueError("Histories must contain consecutive epochs beginning at one.")
        observed=max(epochs,key=lambda row:row["validation_spearman"])
        policies={str(p):replay(epochs,p) for p in [1,2,3,4,5,10]}
        minimum=next(p for p in range(1,len(epochs)+1) if replay(epochs,p)["validation_spearman"]==observed["validation_spearman"])
        results.append({"label":curve["label"],"scope":curve["scope"],"model":curve["model"],
                        "epochs_observed":len(epochs),"best_observed":observed,"policies":policies,
                        "patience1_missed_observed_peak":policies["1"]["validation_spearman"]<observed["validation_spearman"],
                        "gain_over_patience1":observed["validation_spearman"]-policies["1"]["validation_spearman"],
                        "minimum_patience_to_reach_observed_peak":minimum,
                        "original_stop_reason":curve["original_stop_reason"],"source":curve["source"]})
    return {"current_patience":data["current_training"]["patience"],
            "counterfactual_rule":"Strict validation Spearman improvement; min_delta=0; replay starts at epoch one. This matches the current stopper, not every historical objective or minimum-epoch rule.",
            "interpretation":"An observed recovery proves patience 1 would miss that recorded peak. A retained peak does not rule out unobserved later recovery. Architecture, data and schedule differences limit transfer.",
            "histories":results,"live_fits":data["live_fits"]}

def main():
    """Read portable validation excerpts and write auditable counterfactual results."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=analyze(json.loads(args.inputs.read_text()))
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    for row in result["histories"]:
        if row["scope"] in {"older_qwen_lora","older_qwen_projection","recent_frozen_comparator","recent_qwen_ratings"}:
            print(json.dumps({k:row[k] for k in ["label","scope","epochs_observed","best_observed","gain_over_patience1","minimum_patience_to_reach_observed_peak"]}))
if __name__=="__main__":
    main()
