#!/usr/bin/env python3
"""Run bounded, offline completeness counterexamples and replay retained pages.

The reviewed module is loaded without writing bytecode. All synthetic caches
and derived outputs live under this review directory. No network is permitted.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FROZEN = HERE.parents[1] / "base"
SOURCE = FROZEN / "pagination_fix" / "crawl_public_catalog.py"
WORK = HERE.parents[2]


def digest(path):
    """Return the checksum of the exact bytes inspected."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module():
    """Import the frozen implementation and prevent accidental network use."""
    spec = importlib.util.spec_from_file_location("review02_crawler", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def no_network(*args, **kwargs):
        raise AssertionError("Review 2 is strictly offline")

    module.request = no_network
    return module


def write_json(path, value):
    """Write a synthetic fixture only beneath the review's own directory."""
    path = Path(path).resolve()
    path.relative_to(HERE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


@contextlib.contextmanager
def isolated(module):
    """Temporarily route the reviewed module's caches to an isolated fixture."""
    original = module.BASE, module.WORK, module.ORIGINAL
    with tempfile.TemporaryDirectory(dir=HERE, prefix="fixture_") as temp:
        module.BASE = Path(temp) / "crawler"
        module.WORK = Path(temp)
        module.ORIGINAL = Path(temp) / "public_catalog_cache"
        module.BASE.mkdir()
        module.ORIGINAL.mkdir()
        try:
            yield
        finally:
            module.BASE, module.WORK, module.ORIGINAL = original


def channel_fixture(module, label, page_numbers):
    """Supply a derived channel catalog and one ordinary terminal response."""
    pages = []
    for page in page_numbers:
        pages.append({"page": page, "items": [{"id": f"R{page:010d}", "title": f"Fixture page {page}", "kind": "lockupViewModel", "type": "LOCKUP_CONTENT_TYPE_VIDEO"}]})
    write_json(module.WORK / (label + "_full_public_catalog.json"), {"label": label, "pages": pages, "continuation_remaining": False})
    last = page_numbers[-1]
    terminal = module.ORIGINAL / (label + ("_" + str(last) if last else "") + ".json")
    write_json(terminal, {"onResponseReceivedActions": [{"appendContinuationItemsAction": {"targetId": "fixture-grid", "continuationItems": [{"richItemRenderer": {"content": {"lockupViewModel": {"contentId": f"R{last:010d}", "contentType": "LOCKUP_CONTENT_TYPE_VIDEO", "metadata": {"lockupMetadataViewModel": {"title": {"content": f"Fixture page {last}"}}}}}}}]}}]})


def counterexamples(module):
    """Demonstrate false completeness and invisible required-source gaps."""
    findings = []
    with isolated(module):
        channel_fixture(module, "deep_channel_videos", [0, 2])
        result = module.reused_channel("deep_channel_videos", "videos")
        findings.append({
            "id": "R02-01",
            "scenario": "Derived channel catalog has pages 0 and 2; page 1 is absent. Its retained terminal response has no continuation.",
            "expected": "Incomplete channel snapshot; missing page 1 must be reported.",
            "observed": {"status": result["status"], "pagination_exhausted": result["pagination_exhausted"], "errors": result["errors"], "accepted_page_numbers": [0, 2], "returned_memberships": result["visible_memberships"]},
            "defect_reproduced": result["pagination_exhausted"] is True,
        })
    with isolated(module):
        for label in ["deep_channel_videos", "deep_channel_streams"]:
            channel_fixture(module, label, [0])
        label = "casanare"
        collection_id = module.SEEDS[label][0]
        source_url = "https://www.youtube.com/playlist?list=" + collection_id
        membership = {"video_id": "R0000000000", "url": "https://www.youtube.com/watch?v=R0000000000", "title": "Fixture", "collection_id": collection_id, "collection_key": label, "source_url": source_url, "visibility": "listed", "position": 1, "page_index": 0}
        state = {"collection_key": label, "collection_id": collection_id, "collection_type": "playlist", "source_role": "core_declared_source", "source_url": source_url, "memberships": [membership], "errors": [], "pending_token_sha256": [], **module.completion([membership], [], None, 1, 0)}
        write_json(module.BASE / "caches" / label / "state.json", state)
        result = module.export_all()
        exported_keys = {c["collection_key"] for c in result["collections"]}
        missing_core = sorted(set(module.CORE_SEED_KEYS) - exported_keys)
        findings.append({
            "id": "R02-02",
            "scenario": "Only Casanare has a state file; four other declared core playlists were never crawled. Both channel fixtures are valid.",
            "expected": "Every declared core source appears, with an explicit missing/not-started status for uncrawled sources.",
            "observed": {"exported_collection_keys": sorted(exported_keys), "omitted_required_core_sources": missing_core, "all_exported_sources_report_exhausted": all(c.get("pagination_exhausted") for c in result["collections"]), "all_exported_sources_have_no_errors": all(not c.get("errors") for c in result["collections"])},
            "defect_reproduced": len(missing_core) == 4 and all(c.get("pagination_exhausted") for c in result["collections"]),
        })
    return findings


def retained_channel_audit(module, label):
    """Compare every retained channel page to its ordered derived catalog.

    This checks the currently retained data separately from the synthetic code
    defect. It does not infer original retrieval times or refresh the channel.
    """
    path = WORK / (label + "_full_public_catalog.json")
    snapshot = json.loads(path.read_text())
    pages = snapshot["pages"]
    checks, page_evidence, prior_tokens = [], [], set()
    checks.append({"check": "Consecutive page indexes starting at zero", "passed": [p["page"] for p in pages] == list(range(len(pages)))})
    target = None
    last_video_page = max(p["page"] for p in pages if p.get("items"))
    for index, page in enumerate(pages):
        raw_path = WORK / "public_catalog_cache" / (label + ("_" + str(index) if index else "") + ".json")
        if not raw_path.exists():
            checks.append({"check": f"Raw page {index} exists", "passed": False})
            continue
        data = json.loads(raw_path.read_text())
        about_branch = False
        if index == 0:
            tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            selected = [t["tabRenderer"] for t in tabs if t.get("tabRenderer", {}).get("selected")]
            if len(selected) != 1:
                checks.append({"check": "One selected first-page channel tab", "passed": False})
                continue
            grid = selected[0].get("content", {}).get("richGridRenderer", {})
            target = grid.get("targetId")
            items = grid.get("contents", [])
            legacy = []
            target_matches = bool(target)
        else:
            try:
                items, _, legacy, _ = module.continued_list(data, target)
                target_matches = True
            except ValueError:
                # The historical collector traversed the outer About-channel
                # branch too. Account for that named, non-video branch without
                # silently accepting an arbitrary mismatched continuation.
                target_matches = False
                actions = [a["appendContinuationItemsAction"] for key in ["onResponseReceivedActions", "onResponseReceivedCommands", "onResponseReceivedEndpoints"] for a in data.get(key, []) if "appendContinuationItemsAction" in a]
                if len(actions) != 1:
                    raise
                items, legacy = actions[0].get("continuationItems", []), []
                about_branch = bool(items) and all(set(i) == {"aboutChannelRenderer"} for i in items)
                if not about_branch:
                    raise
        unwrapped = [item.get("richItemRenderer", {}).get("content", item) for item in items]
        if about_branch:
            entries, tokens = [], [t for _, t in module.all_tokens(data)]
        else:
            entries, tokens = module.parse_list(unwrapped, legacy)
        expected = [item["id"] for item in page.get("items", [])]
        observed = [item["video_id"] for item in entries]
        identity_ok = expected == observed
        continuation_ok = (len(tokens) == 0 if about_branch or index == last_video_page else len(tokens) == 1)
        cycle_free = not any(t in prior_tokens for t in tokens)
        prior_tokens.update(tokens)
        # Sort/filter chip commands are navigation actions, not next pages.
        # Require the inspected list's continuation, not every global token,
        # to have been recognized by the historical collector.
        old_parser_complete = set(tokens).issubset(set(module.old_tokens(data)))
        checks.extend([
            {"check": f"Page {index} is the selected grid or identified About-channel branch", "passed": target_matches or about_branch},
            {"check": f"Page {index} ordered IDs match raw primary list", "passed": identity_ok},
            {"check": f"Page {index} continuation agrees with sequence", "passed": continuation_ok},
            {"check": f"Page {index} continuation is not repeated", "passed": cycle_free},
            {"check": f"Page {index} inspected-list continuation was supported by historical parser", "passed": old_parser_complete},
        ])
        page_evidence.append({"page_index": index, "raw_response_sha256": digest(raw_path), "derived_item_count": len(expected), "raw_primary_item_count": len(observed), "continuation_count": len(tokens), "ordered_ids_equal": identity_ok, "primary_target_matches": target_matches, "known_nonvideo_about_branch": about_branch, "all_continuations_supported_by_historical_parser": old_parser_complete})
    return {"label": label, "catalog_sha256": digest(path), "pages_checked": len(page_evidence), "all_passed": all(c["passed"] for c in checks), "checks": checks, "page_evidence": page_evidence, "limitation": "Retained responses only; request-token submission provenance and original retrieval times were not recorded. No fresh network request was made."}


def main():
    """Save the complete review observer receipt and print only its summary."""
    module = load_module()
    failures = counterexamples(module)
    channels = [retained_channel_audit(module, label) for label in ["deep_channel_videos", "deep_channel_streams"]]
    manifest = json.loads((FROZEN / "crawl_manifest.json").read_text())
    playlists = [c for c in manifest["collections"] if c["collection_type"] == "playlist"]
    publication_check = {
        "all_ten_playlist_states_present": {c["collection_key"] for c in playlists} == set(module.SEEDS),
        "all_ten_playlist_counts_reconcile": all(c["returned_memberships"] + c.get("hidden_unavailable_count", 0) == c["declared_items"] and c["count_reconciled"] is True for c in playlists),
        "all_selected_completed_surfaces_have_no_errors_or_pending": all(not c.get("errors") and not c.get("pending_token_sha256") for c in manifest["collections"] if c.get("pagination_exhausted")),
    }
    report = {"base_commit": "620cc5eb85860ff77a837058903321876de82b15", "runtime": sys.executable, "network_requests": 0, "reviewed_code_sha256": digest(SOURCE), "counterexamples": failures, "retained_channel_audits": channels, "published_snapshot_checks": publication_check}
    write_json(HERE / "observer_results.json", report)
    print(json.dumps({"counterexamples_reproduced": [f["id"] for f in failures if f["defect_reproduced"]], "retained_channel_pages_checked": sum(c["pages_checked"] for c in channels), "retained_channel_replay_passed": all(c["all_passed"] for c in channels), "published_snapshot_checks": publication_check}, indent=2))


if __name__ == "__main__":
    main()
