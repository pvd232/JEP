"""Check that observers handle live appends and follow the launched source."""

import json

from csts_pilot.progress import collect, measurements


def test_observer_keeps_complete_measurements_during_append(tmp_path):
    path = tmp_path / "metrics.jsonl"
    path.write_text('{"step":1,"value":0.2}\n{"step":2,')
    assert measurements(path) == {1: 0.2}


def test_observer_uses_current_source_and_skips_evaluation_input(tmp_path):
    results = tmp_path / "csts_results"
    results.mkdir()
    (results / "launcher.json").write_text(
        json.dumps({"source_commit": "abcdef012345", "pid": 0})
    )
    (results / "summary.json").write_text(
        json.dumps({"source_commit": "abcdef012345", "status": "complete"})
    )
    data = tmp_path / "csts_data"
    data.mkdir()
    (data / "evaluation.json").write_text(
        "This input must remain unopened by the observer."
    )
    for source in ("abcdef0", "oldcode"):
        folder = (
            tmp_path
            / f"experiments/csts_natural_20261021_{source}_trial/runs/trial/run"
        )
        logs = folder / "attempts/1/measurements"
        logs.mkdir(parents=True)
        (logs / "train.development_mse.jsonl").write_text('{"step":1,"value":0.2}\n')
    progress = collect(tmp_path)
    assert progress["status"] == "complete"
    assert len(progress["trials"]) == 1
    assert progress["trials"][0]["best_development"]["mse_0_1"] == 0.2
