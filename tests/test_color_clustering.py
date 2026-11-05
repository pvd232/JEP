"""Exercise the sixteen success/rejection observers declared by the COLOR contract."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest
from scripts import color_clustering


def source_fixture(tmp_path, monkeypatch):
    """Create three caption-disjoint miniature splits with verified source bytes."""
    hashes = {}
    for split, color in (("train", "red"), ("validation", "blue"), ("test", "green")):
        row = {
            "row_id": split + "_1",
            "group_id": split,
            "pair_id": split,
            "condition": "color of shirt",
            "sentence1": "A " + color + " shirt.",
            "sentence2": "Another " + color + " shirt.",
            "rating": 5,
            "target": 1,
        }
        path = tmp_path / (split + ".json")
        path.write_text(json.dumps([row, dict(row, row_id=split + "_2")]))
        hashes[split] = color_clustering.sha(path)
    monkeypatch.setattr(color_clustering, "SOURCE_HASHES", hashes)
    return tmp_path


def point_fixture(
    condition="color of shirt", sentence="A red shirt and blue trousers."
):
    """Build one original input with an exact stable point identity."""
    return {
        "point_id": color_clustering.point_id(condition, sentence),
        "condition": condition,
        "sentence": sentence,
        "group_id": "family",
        "occurrences": [],
    }


def model_fixture(tmp_path):
    """Create a small identity-bearing stand-in for checkpoint validation."""
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"fixed checkpoint bytes")
    return {
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": color_clustering.sha(checkpoint),
        "source_repository": str(tmp_path),
        "source_commit": "a" * 40,
        "config": {"embedding_dimension": 4096},
        "source_result": "archived-result.json",
    }


def sweep_fixture():
    """Return the declared twenty independently seeded fits at one K."""
    return [{"k": 2, "seed": seed, "ari": 0.5, "silhouette": 0.4} for seed in range(20)]


def test_cohort_preserves_rows_points_and_splits(tmp_path, monkeypatch):
    """Repeated original pairs share vectors while retaining all six source rows."""
    data = source_fixture(tmp_path, monkeypatch)
    output = tmp_path / "out"
    result = color_clustering.prepare_cohort(data, output)
    assert result["pairs"] == 6 and result["points"] == 6
    assert result["row_counts"] == {"train": 2, "validation": 2, "test": 2}
    assert all(
        len(p["occurrences"]) == 2
        for p in color_clustering.read(output / "points.json")
    )


def test_cohort_rejects_source_or_membership_mismatch(tmp_path, monkeypatch):
    """A modified source export fails before cohort preparation."""
    data = source_fixture(tmp_path, monkeypatch)
    (data / "test.json").write_text("[]")
    with pytest.raises(ValueError, match="color cohort: source mismatch"):
        color_clustering.prepare_cohort(data, tmp_path / "out")


def test_labels_resolve_the_named_target():
    """Relevant coat markings are included while the collar's color is excluded."""
    point = point_fixture(
        "color of dog", "A white dog with a red collar and black spots."
    )
    label = color_clustering.annotate(point)
    label.update(reviewed=True, reviewer="fixture")
    color_clustering.validate_labels([point], [label])
    assert label["color_labels"] == ["black", "white"]


def test_labels_reject_missing_or_conflicting_evidence():
    """A color annotation without a source-supported span is rejected."""
    point = point_fixture()
    label = color_clustering.annotate(point)
    label.update(reviewed=True, evidence=["green shirt"])
    with pytest.raises(ValueError, match="color label: missing target evidence"):
        color_clustering.validate_labels([point], [label])


def test_encoder_matches_the_archived_run(tmp_path):
    """The resolver admits the exact declared checkpoint bytes and width."""
    manifest = model_fixture(tmp_path)
    assert color_clustering.resolve_encoder(manifest) == manifest


def test_encoder_rejects_checkpoint_substitution(tmp_path):
    """A same-path checkpoint replacement fails its archived digest."""
    manifest = model_fixture(tmp_path)
    Path(manifest["checkpoint"]).write_bytes(b"different checkpoint")
    with pytest.raises(ValueError, match="encoder identity: checkpoint mismatch"):
        color_clustering.resolve_encoder(manifest)


def test_embeddings_preserve_arm_and_input_identity():
    """Finite float32 unit vectors satisfy the declared representation check."""
    color_clustering.validate_vectors(np.eye(3, dtype=np.float32), 3, 3)


def test_embeddings_reject_stale_or_invalid_vectors():
    """A non-unit vector is rejected before clustering."""
    with pytest.raises(ValueError, match="embedding cache: identity mismatch"):
        color_clustering.validate_vectors(np.array([[2, 0]], dtype=np.float32), 1, 2)


def test_sweep_covers_each_supported_k_and_seed():
    """The complete declared seed set is accepted once per K."""
    color_clustering.validate_sweep(sweep_fixture(), [2])


def test_sweep_rejects_missing_or_changed_settings():
    """An omitted unfavorable seed fails sweep completeness."""
    with pytest.raises(ValueError, match="kmeans sweep: incomplete grid"):
        color_clustering.validate_sweep(sweep_fixture()[:-1], [2])


def test_scores_follow_fixed_selection_and_pair_links():
    """Silhouette selection resolves an effective tie toward the smaller K."""
    assert (
        color_clustering.select_k(
            [{"k": 2, "silhouette": 0.5}, {"k": 3, "silhouette": 0.5000001}]
        )
        == 2
    )


def test_scores_reject_label_selected_k_or_broken_pairs():
    """Ground-truth agreement cannot be used to select the unsupervised K."""
    with pytest.raises(ValueError, match="metric policy: unsupported selection"):
        color_clustering.select_k(sweep_fixture(), metric="ari")


def test_switch_scores_follow_target_changes():
    """A requested target's prototype may use independent source families."""
    color_clustering.validate_prototype_families("probe", {"family-a", "family-b"})


def test_switch_rejects_overlapping_prototypes():
    """A prototype containing the probe family fails its exclusion check."""
    with pytest.raises(ValueError, match="condition switch: prototype overlap"):
        color_clustering.validate_prototype_families("probe", {"probe", "other"})


def test_report_accounts_for_all_inputs_and_results():
    """A report with every declared arm and seed passes completeness."""
    arms = {
        arm: {"grid": [2], "runs": sweep_fixture()} for arm in color_clustering.ARMS
    }
    color_clustering.validate_report({"cohorts": {"validation_single": {"arms": arms}}})


def test_report_rejects_omissions_or_outcome_gates():
    """A missing seeded fit prevents publication of an incomplete report."""
    arms = {
        arm: {"grid": [2], "runs": sweep_fixture()} for arm in color_clustering.ARMS
    }
    metrics = {"cohorts": {"validation_single": {"arms": arms}}}
    damaged = copy.deepcopy(metrics)
    damaged["cohorts"]["validation_single"]["arms"][color_clustering.ARMS[0]][
        "runs"
    ].pop()
    with pytest.raises(ValueError, match="report: incomplete evidence"):
        color_clustering.validate_report(damaged)
