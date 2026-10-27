"""Numerical and paired-training checks for the frozen evidence readout."""

import copy
from pathlib import Path

import numpy as np
import pytest
import torch
from torch.nn import functional as F

from csts_pilot.answers import answer_id
from csts_pilot.evidence_readout import (
    CONTRASTS,
    EvidenceReadout,
    SymmetricComparison,
    bind_records,
    clone_state,
    gradient_diagnostic,
    matched_initial_heads,
    metric_values,
    pack_batch,
    paired_intervals,
    predict,
    quotation_target,
    selection_loss,
    validate_cache,
    validate_capture,
)
from csts_pilot.evidence_readout_retention import (
    restore_frozen_adapter,
    retention_summary,
)
from csts_pilot.evidence_readout_run import checked_source, queue_identity
from csts_pilot.evidence_readout_stages import (
    ReadoutFitConfig,
    checked_selection,
    family_diagnostics,
    paired_condition_diagnostics,
    train_pair,
)


def fixture(split="training"):
    """Nontrivial source states, uneven lengths, and ordered comparison targets."""
    generator = torch.Generator().manual_seed(41 if split == "training" else 42)
    keys, values, metadata, pointers = [], [], [], [0]
    for i in range(8):
        passage = "red car" if i % 2 else "red small car"
        offsets = [(0, 3), (4, len(passage))]
        if i % 2 == 0:
            offsets = [(0, 3), (4, 9), (10, 13)]
        keys.append(("car color", passage))
        values.append(torch.randn(len(offsets), 5, generator=generator))
        metadata.append({"passage_offsets": offsets})
        pointers.append(pointers[-1] + len(offsets))
    rows = [
        {
            "row_id": str(i),
            "group_id": f"{split}_{i}",
            "condition": "car color",
            "sentence1": keys[2 * i][1],
            "sentence2": keys[2 * i + 1][1],
            "target": i / 3,
        }
        for i in range(4)
    ]
    spans = torch.zeros(pointers[-1])
    if split == "training":
        spans[pointers[:-1]] = 1
    cache = {
        "schema_version": 1,
        "keys": keys,
        "pointers": pointers,
        "embedding_dimension": 5,
        "token_values": torch.cat(values),
        "condition_states": torch.randn(8, 5, generator=generator),
        "eod_vectors": F.normalize(torch.randn(8, 5, generator=generator), dim=1),
        "span_targets": spans,
        "null_targets": torch.zeros(8),
        "metadata": metadata,
        "split": split,
        "records_sha256": "a" * 64 if split == "training" else None,
        "left": list(range(0, 8, 2)),
        "right": list(range(1, 8, 2)),
        "model_sha256": "b" * 64,
        "revision": "c" * 40,
        "prompt": "fixture",
        "adapter_before_sha256": "d" * 64,
        "coverage": {"answered": 8} if split == "training" else {"uncaptured": 8},
    }
    return cache, rows


def config():
    return ReadoutFitConfig(
        device="cpu",
        seed=7,
        query_dim=3,
        batch_size=3,
        max_epochs=3,
        patience=2,
        comparison_max_epochs=3,
        comparison_patience=2,
        **{
            name: "a" * 64
            for name in (
                "training_sha256",
                "validation_sha256",
                "training_cache_sha256",
                "validation_cache_sha256",
            )
        },
    )


def record(passage="red car", status="answered", evidence=None):
    return {
        "id": answer_id(passage, "car color"),
        "status": status,
        "target": "car",
        "attribute": "color",
        "answer": "red" if status == "answered" else "",
        "evidence": ["red"]
        if evidence is None and status == "answered"
        else (evidence or []),
    }


def test_readout_gradcheck_and_exact_padding_exclusion():
    torch.manual_seed(4)
    head = EvidenceReadout(5, 3).double()
    x = torch.randn(2, 3, 5, dtype=torch.double, requires_grad=True)
    q = torch.randn(2, 5, dtype=torch.double, requires_grad=True)
    mask = torch.tensor([[True, True, True], [True, True, False]])
    assert torch.autograd.gradcheck(lambda a, b: head(a, b, mask)[0], (x, q), atol=1e-4)
    vector, logits, probabilities = head(x, q, mask)
    assert probabilities[1, -1] == 0
    assert logits[1, -1] == -torch.inf
    changed = x.detach().clone()
    changed[1, -1] = 1e10
    torch.testing.assert_close(head(changed, q, mask)[0], vector)
    with pytest.raises(ValueError, match="nonempty"):
        head(x, q, torch.zeros_like(mask))


def test_null_is_distinct_from_content_normalization():
    cache, _ = fixture()
    x, q, mask, _ = pack_batch(cache, [0, 1], "cpu")
    head = EvidenceReadout(5, 3)
    before = head(x, q, mask)[0]
    with torch.no_grad():
        head.null_bias.fill_(10000)
    after, _, probability = head(x, q, mask)
    torch.testing.assert_close(before, after)
    torch.testing.assert_close(probability[:, 0], torch.ones(2))
    assert torch.isfinite(after).all()


def test_quotation_targets_do_not_treat_missing_capture_as_absence():
    passage, offsets = "red car", [(0, 3), (4, 7)]
    assert quotation_target(passage, offsets, record())[0].tolist() == [0, 1, 0]
    assert quotation_target(passage, offsets, record(status="not_specified"))[
        0
    ].tolist() == [1, 0, 0]
    for item in [None, record(status="ambiguous"), record(evidence=["blue"])]:
        assert quotation_target(passage, offsets, item)[0].sum() == 0
    assert (
        quotation_target("red red", [(0, 3), (4, 7)], record(evidence=["red"]))[1]
        == "ambiguous_quotation_occurrence"
    )
    bad = record(status="not_specified", evidence=["red"])
    with pytest.raises(ValueError, match="empty"):
        quotation_target(passage, offsets, bad)
    with pytest.raises(ValueError, match="foreign"):
        bind_records([("car color", passage)], [record("different")])
    with pytest.raises(ValueError, match="Duplicate"):
        bind_records([("car color", passage)], [record(), record()])


def test_masked_selection_loss_and_shared_gradients_are_finite():
    cache, _ = fixture()
    x, q, mask, gold = pack_batch(cache, [0, 1], "cpu")
    head = EvidenceReadout(5, 3)
    vectors, logits, _ = head(x, q, mask)
    ce, count = selection_loss(logits, mask, gold)
    assert count == 2
    expected = -logits.log_softmax(1)[range(2), [1, 1]].mean()
    torch.testing.assert_close(ce, expected)
    rating = (vectors[0] * vectors[1]).sum().square()
    diagnostics = gradient_diagnostic(head, rating, ce, 0.1)
    shared = torch.autograd.grad(
        ce, (head.query.weight, head.key.weight), retain_graph=True
    )
    assert all(g.norm() > 0 for g in shared)
    assert diagnostics["rating_norm"] > 0 and diagnostics["weighted_evidence_norm"] > 0
    assert all(p.grad is None for p in head.parameters())
    zero, count = selection_loss(logits, mask, torch.zeros_like(gold))
    assert count == 0 and zero == 0
    (rating + ce + zero).backward()
    assert all(
        torch.isfinite(p.grad).all() for p in head.parameters() if p.grad is not None
    )


def test_cache_rejects_row_substitution_heldout_labels_and_partial_cohorts():
    cache, rows = fixture()
    validate_cache(cache, rows)
    changed = copy.deepcopy(rows)
    changed[0]["sentence1"] = "other"
    with pytest.raises(ValueError, match="another"):
        validate_cache(cache, changed)
    cache["split"] = "test"
    with pytest.raises(ValueError, match="Held-out"):
        validate_cache(cache, rows)
    cache, _ = fixture()
    cache["left"].pop()
    with pytest.raises(ValueError, match="coverage"):
        validate_cache(cache, rows)


def test_paired_fit_checkpoint_replay_and_snapshot_independence(tmp_path):
    torch.set_num_threads(1)
    training, rows = fixture()
    validation, heldout = fixture("validation")
    model, trace, predictions, terminal = train_pair(
        training, validation, rows, heldout, config()
    )
    assert trace["updates_per_arm"] == terminal["updates"]
    assert trace["updates_per_arm"] == len(trace["epochs"]) * 2
    assert set(model["selected"]) == {"ratings", "evidence"}
    path = tmp_path / "model.pt"
    torch.save(model, path)
    restored = torch.load(path, weights_only=True)
    for arm in ["ratings", "evidence"]:
        head = EvidenceReadout(5, 3)
        head.load_state_dict(restored["selected"][arm]["state"])
        values, _, _ = predict(head, validation)
        np.testing.assert_allclose(values, predictions[arm], atol=1e-7)
        rho = metric_values(heldout, values)["spearman"]
        assert rho == restored["selected"][arm]["spearman"]
        comparator = SymmetricComparison(5)
        comparator.load_state_dict(restored["comparisons"]["selected"][arm]["state"])
        compared, _, _ = predict(head, validation, comparator=comparator)
        np.testing.assert_allclose(
            compared, predictions[arm + "_comparison"], atol=1e-7
        )
        assert (
            metric_values(heldout, compared)["spearman"]
            == restored["comparisons"]["selected"][arm]["spearman"]
        )
        assert (
            trace["comparison"]["readout_before_sha256"][arm]
            == trace["selected_state_sha256"][arm]
        )
    assert (
        trace["comparison"]["readout_before_sha256"]
        == trace["comparison"]["readout_after_sha256"]
    )
    assert trace["comparison"]["updates_per_arm"] == terminal["comparison"]["updates"]
    assert trace["comparison"]["updates_per_arm"] == 2 * len(
        trace["comparison"]["epochs"]
    )
    heads = matched_initial_heads(5, 3, 7)
    frozen = clone_state(heads["ratings"])
    with torch.no_grad():
        heads["ratings"].query.weight.add_(1)
    torch.testing.assert_close(frozen["query.weight"], heads["evidence"].query.weight)
    assert not torch.equal(frozen["query.weight"], heads["ratings"].query.weight)


def test_no_teacher_loss_means_exactly_matched_trajectories():
    training, rows = fixture()
    training["span_targets"].zero_()
    validation, heldout = fixture("validation")
    model, trace, predictions, _ = train_pair(
        training, validation, rows, heldout, config()
    )
    assert predictions["ratings"] == predictions["evidence"]
    assert predictions["ratings_comparison"] == predictions["evidence_comparison"]
    for name in model["last_state"]["ratings"]:
        torch.testing.assert_close(
            model["last_state"]["ratings"][name], model["last_state"]["evidence"][name]
        )
    assert trace["selected_epoch"]["ratings"] == trace["selected_epoch"]["evidence"]


def test_paired_bootstrap_has_shared_groups_and_reproducible_zero_difference():
    _, rows = fixture()
    values = [0.1, 0.4, 0.3, 0.9]
    predictions = {
        "7": {"ratings": values, "evidence": values},
        "8": {"ratings": values, "evidence": values},
    }
    result = paired_intervals(rows, predictions, 40, 19)
    assert result["low"] == result["high"] == 0
    assert result == paired_intervals(rows, predictions, 40, 19)
    with pytest.raises(ValueError, match="coverage"):
        metric_values(rows, np.array(values[:-1]))


def test_queue_rejects_source_mutation_before_loading_inputs(tmp_path):
    import subprocess

    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    file = tmp_path / "source.py"
    file.write_text("x=1\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "source.py"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    commit = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
    ).strip()
    checked_source(tmp_path, commit)
    file.write_text("x=2\n")
    with pytest.raises(ValueError, match="Commit all"):
        queue_identity(tmp_path, Path("absent.json"), commit)
    with pytest.raises(ValueError, match="commit changed"):
        checked_source(tmp_path, "0" * 40)


def test_capture_policy_and_frozen_selection_fail_closed(tmp_path):
    import json

    from csts_pilot.convergence import file_sha256

    gate = {
        "passed": True,
        "generation_frozen": True,
        **{
            k: k
            for k in (
                "generation_template_sha256",
                "schema_sha256",
                "model_alias",
                "reasoning_effort",
                "capture_source_sha256",
            )
        },
    }
    provenance = {
        **gate,
        "records_sha256": "records",
        "source_training_sha256": "training",
        "audit_gate_sha256": "gate",
        "items": 1,
    }
    validate_capture(provenance, gate, "records", "training", "gate", 1)
    with pytest.raises(ValueError, match="provenance"):
        validate_capture(provenance, gate, "different", "training", "gate", 1)
    gate["model_alias"] = "changed"
    with pytest.raises(ValueError, match="policy"):
        validate_capture(provenance, gate, "records", "training", "gate", 1)
    selection = tmp_path / "selection.json"
    selection.write_text(
        json.dumps(
            {
                "status": "checkpoints_frozen",
                "test_scores_used_for_selection": False,
                "models": {"7": {"sha256": "a" * 64}},
            }
        )
    )
    digest = file_sha256(selection)
    assert checked_selection(selection, digest) == {"7": "a" * 64}
    selection.write_text(selection.read_text().replace("false", "true"))
    with pytest.raises(ValueError, match="Changed"):
        checked_selection(selection, digest)
    with pytest.raises(ValueError, match="without test"):
        checked_selection(selection, file_sha256(selection))


def test_queue_waits_for_lease_without_starting_a_stage(tmp_path, monkeypatch):
    import fcntl
    import json

    import csts_pilot.evidence_readout_run as runner
    from csts_pilot.convergence import file_sha256

    lock_path = tmp_path / "gpu.lock"
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"gpu_locks": [str(lock_path)]}))
    identity = {
        "root": str(tmp_path),
        "source_commit": "a" * 40,
        "settings_sha256": file_sha256(settings),
        "settings_path": str(settings),
    }
    monkeypatch.setattr(runner, "queue_identity", lambda *args: identity)
    monkeypatch.setattr(runner, "checked_source", lambda *args: None)

    def forbidden():
        pytest.fail(
            "The queue must not inspect or run the GPU while another worker holds its lease."
        )

    monkeypatch.setattr(runner, "gpu_idle", forbidden)

    def end_wait(seconds):
        assert seconds <= 60
        raise InterruptedError("fixture ends after one wait")

    monkeypatch.setattr(runner.time, "sleep", end_wait)
    with lock_path.open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(InterruptedError):
            runner.queue_study(tmp_path, settings, "fixture", "a" * 40)
    receipt = json.loads(
        (tmp_path / "qwen_evidence_results/fixture/queue.json").read_text()
    )
    assert receipt["status"] == "queued" and receipt["identity"] == identity


def test_prospective_intervention_file_has_complete_literal_bindings():
    import json

    from csts_pilot.convergence import file_sha256

    root = Path(__file__).parents[1]
    config = json.loads((root / "configs/csts-evidence-readout.json").read_text())
    path = root / config["interventions"]["path"]
    assert file_sha256(path) == config["interventions"]["sha256"]
    rows = json.loads(path.read_text())
    assert len(rows) == len({r["row_id"] for r in rows}) == 24
    for case in {r["case"] for r in rows}:
        variants = [r for r in rows if r["case"] == case]
        assert {r["edit"] for r in variants} == {
            "base",
            "irrelevant",
            "relevant",
            "missing",
        }
        assert len({r["sentence1"] for r in variants}) == 4
        assert (
            len({r["condition"] for r in variants})
            == len({r["sentence2"] for r in variants})
            == 1
        )
        for row in variants:
            assert (not row["evidence_quote"]) == (row["edit"] == "missing")
            if row["evidence_quote"]:
                assert row["sentence1"].count(row["evidence_quote"]) == 1


def test_comparator_is_symmetric_starts_at_cosine_and_can_fit():
    torch.manual_seed(3)
    left, right = (
        F.normalize(torch.randn(6, 5), dim=1),
        F.normalize(torch.randn(6, 5), dim=1),
    )
    comparator = SymmetricComparison(5)
    torch.testing.assert_close(
        comparator(left, right), (left * right).sum(1), rtol=0, atol=0
    )
    before = comparator(left, right).detach().clone()
    loss = F.mse_loss(comparator(left, right), torch.linspace(0, 1, 6))
    loss.backward()
    assert comparator.residual.weight.grad.norm() > 0
    optimizer = torch.optim.SGD(comparator.parameters(), lr=0.1)
    optimizer.step()
    assert not torch.equal(comparator(left, right), before)
    torch.testing.assert_close(
        comparator(left, right), comparator(right, left), rtol=0, atol=0
    )


def test_factorial_bootstrap_and_overlapping_families():
    _, rows = fixture()
    values = [0.1, 0.4, 0.3, 0.9]
    predictions = {
        "7": {
            a: values
            for a in (
                "ratings",
                "evidence",
                "ratings_comparison",
                "evidence_comparison",
            )
        }
    }
    for contrast in CONTRASTS.values():
        interval = paired_intervals(rows, predictions, 40, 19, contrast)
        assert interval["low"] == interval["high"] == 0
        assert interval["mse_low"] == interval["mse_high"] == 0
    cohorts = {
        "colour_regex": "color",
        "splits": {"test": {"condition_families": {"car color": "appearance"}}},
    }
    families = family_diagnostics(rows, np.asarray(values), cohorts)
    assert families["colour"]["row_ids"] == families["appearance"]["row_ids"]


def test_condition_changes_require_the_same_sentence_pair_and_score_ties_half():
    rows = [
        {"sentence1": "a", "sentence2": "b", "condition": "color", "target": 1.0},
        {"sentence1": "b", "sentence2": "a", "condition": "count", "target": 0.0},
        {"sentence1": "a", "sentence2": "c", "condition": "count", "target": 0.0},
    ]
    result = paired_condition_diagnostics(rows, np.array([0.5, 0.5, 0.1]))
    assert result == {
        "comparisons": 1,
        "strict_correct": 0,
        "ties": 1,
        "accuracy_half_ties": 0.5,
        "difference_mse_0_1": 1.0,
    }


def test_writing_retention_keeps_exact_agreement_separate_from_factual_accuracy():
    before = [
        {
            "id": "a",
            "answer_mean_ce": 0.2,
            "reference": "red car",
            "generated": "red  car",
            "ended_with_eod": True,
        },
        {
            "id": "b",
            "answer_mean_ce": 0.4,
            "reference": "two",
            "generated": None,
            "ended_with_eod": None,
        },
    ]
    after = copy.deepcopy(before)
    after[0].update(answer_mean_ce=0.6, generated="blue car", ended_with_eod=False)
    result = retention_summary(before, after)
    assert result["writing"]["whitespace_normalized_exact_match"] == 1
    assert result["after_ratings"]["whitespace_normalized_exact_match"] == 0
    assert result["paired_mean_ce_after_minus_before"] == pytest.approx(0.2)
    assert result["after_ratings"]["generation_cap_hits"] == 1
    with pytest.raises(ValueError, match="identical"):
        retention_summary(before, list(reversed(after)))


def test_retention_can_restore_two_adapters_while_leaving_every_parameter_frozen():
    model = torch.nn.Module()
    model.base = torch.nn.Linear(2, 2)
    model.lora_A = torch.nn.Parameter(torch.zeros(2))
    original_base = model.base.weight.detach().clone()
    first = restore_frozen_adapter(model, {"lora_A": torch.ones(2)})
    assert not any(p.requires_grad for p in model.parameters())
    second = restore_frozen_adapter(model, {"lora_A": torch.zeros(2)})
    assert first != second
    assert not any(p.requires_grad for p in model.parameters())
    torch.testing.assert_close(model.base.weight, original_base)
    torch.testing.assert_close(model.lora_A, torch.zeros(2))
