"""Verify terminal results publish promptly while routine updates stay bounded."""

import hashlib

from scripts.publish_colab_readout_progress import publish_due, terminal_state


def test_terminal_states_require_a_completed_controller_marker():
    assert terminal_state("fitting complete; evaluation running") is None
    assert terminal_state("\nEvaluation status: succeeded.\n") == "complete"
    assert (
        terminal_state("| now | controller failed | | | error_type: RuntimeError |")
        == "failed"
    )


def test_final_results_publish_immediately_after_a_recent_update():
    old = "running"
    digest = hashlib.sha256(old.encode()).hexdigest()
    assert not publish_due("more progress", digest, 100, 110, 300)
    assert publish_due("Evaluation status: succeeded.", digest, 100, 110, 300)
    assert publish_due("| controller failed |", digest, 100, 110, 300)


def test_identical_reports_create_no_extra_commits_and_first_report_publishes():
    content = "running"
    digest = hashlib.sha256(content.encode()).hexdigest()
    assert not publish_due(content, digest, 0, 1000, 300)
    assert publish_due(content, None, 0, 1, 300)
