#!/usr/bin/env python3
"""Audit public playlist metadata.

Python 3.10+ standard library. Writes only beside this script. Original research
caches are read-only fixtures. Playlist appearances and video identities remain
separate. Casanare inclusion requires a separate scope review.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import html.parser
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE = Path(__file__).resolve().parent
WORK = BASE.parent
ORIGINAL = WORK / "public_catalog_cache"
JEP_CHANNEL = "UCay5mclHBbWQTQ8fhoNCWow"
STOP_NETWORK = threading.Event()
SEEDS = {
    "case03": ("PLbtegW3d3L4Id_lrAgBRDGf-k_bwEYH6_", "case03_playlist", "Broad Case 03; discovery metadata only"),
    "casanare": ("PLbtegW3d3L4JR1Y_bfCDS_C8sdKE6195K", "subcaso_casanare_playlist", "Casanare collection; individual scope review required"),
    "audiencias": ("PLbtegW3d3L4JAstPux8ji9-h9balFGI6M", "deep_audiencias_playlist", "Mixed hearings; individual Casanare scope review required"),
    "regimen": ("PLbtegW3d3L4L_sf8wgB26KHOPY3sCOSv9", "deeper_regimen_playlist", "Mixed conditionality proceedings; individual scope review required"),
    "memoria_casanare": ("PLbtegW3d3L4LXHjmpwCMYpO2tzpRtOUco", "deep_memory_playlist", "Casanare memory collection; substantive type review required"),
}
CORE_SEED_KEYS = tuple(SEEDS)
REGIONAL_SEEDS = {
    "region_antioquia": ("PLbtegW3d3L4IzLqaub8l87_fTQvSiZ47C", "Antioquia"),
    "region_costa_caribe": ("PLbtegW3d3L4IjZw5ZdFqDEr3H8x3dZ_sh", "Costa Caribe / La Popa"),
    "region_norte_santander": ("PLbtegW3d3L4KerLKcosDcd9FpE8CPQJVk", "Norte de Santander"),
    "region_huila": ("PLbtegW3d3L4Jxv0UENoIIqo3WYHoNQ3GA", "Huila"),
    "region_meta": ("PLbtegW3d3L4IP1S5w5_jxrCtI686L03dh", "Meta"),
}
for _key, (_playlist_id, _region) in REGIONAL_SEEDS.items():
    SEEDS[_key] = (_playlist_id, "channel_playlists", "Supplemental regional membership join: " + _region + "; metadata only")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path).resolve()
    path.relative_to(BASE)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.{threading.get_ident()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def walk(value, path=()):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (index,))


def text(value):
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ""
    for key in ["simpleText", "content"]:
        if isinstance(value.get(key), str):
            return value[key]
    return "".join(x.get("text", "") for x in value.get("runs", []) if isinstance(x, dict))


def assigned(html, name):
    match = re.search(r"(?:var\s+)?" + re.escape(name) + r"\s*=\s*", html)
    if not match:
        raise ValueError("Expected public page assignment missing: " + name)
    return json.JSONDecoder().raw_decode(html[match.end():])[0]


def context_from(html):
    match = re.search(r'"INNERTUBE_CONTEXT"\s*:', html)
    if not match:
        raise ValueError("Expected anonymous public request context missing")
    return json.JSONDecoder().raw_decode(html[match.end():])[0]


def request(url, body=None):
    if STOP_NETWORK.is_set():
        raise RuntimeError("Network batch stopped after HTTP 429; no retries")
    headers = {"User-Agent": "Mozilla/5.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    started = now()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = response.read()
            meta = {"requested_url": url, "response_url": response.url, "method": "POST" if body else "GET", "http_status": response.status, "content_type": response.headers.get("Content-Type"), "fetched_at": started, "sha256": sha(payload), "bytes": len(payload)}
            return payload, meta
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            STOP_NETWORK.set()
        raise


def all_tokens(value):
    return [(path + ("continuationCommand",), obj["continuationCommand"]["token"]) for path, obj in walk(value) if isinstance(obj.get("continuationCommand"), dict) and obj["continuationCommand"].get("token")]


def old_tokens(value):
    """Exact relevant behavior of the original Renderer-only parser."""
    found = []
    for _, obj in walk(value):
        item = obj.get("continuationItemRenderer", {})
        token = item.get("continuationEndpoint", {}).get("continuationCommand", {}).get("token")
        if token:
            found.append(token)
    return found


def item_token(item):
    old = item.get("continuationItemRenderer")
    if old:
        return old.get("continuationEndpoint", {}).get("continuationCommand", {}).get("token")
    new = item.get("continuationItemViewModel")
    if new:
        command = new.get("continuationCommand", {})
        return command.get("innertubeCommand", {}).get("continuationCommand", {}).get("token") or command.get("token")
    return None


def is_video_item(item):
    if "playlistVideoRenderer" in item or "videoRenderer" in item:
        return True
    view = item.get("lockupViewModel", {})
    return view.get("contentType") == "LOCKUP_CONTENT_TYPE_VIDEO"


def initial_list(data):
    """Choose the primary playlist list, excluding outer/recommended sections."""
    tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
    selected = [(n, x["tabRenderer"]) for n, x in enumerate(tabs) if "tabRenderer" in x and x["tabRenderer"].get("selected")]
    if not selected and len(tabs) == 1 and "tabRenderer" in tabs[0]:
        selected = [(0, tabs[0]["tabRenderer"])]
    if len(selected) != 1:
        raise ValueError("Cannot identify one selected playlist tab")
    n, tab = selected[0]
    root_path = ("contents", "twoColumnBrowseResultsRenderer", "tabs", n, "tabRenderer", "content")
    content = tab.get("content", {})
    old_lists = [(path, obj["playlistVideoListRenderer"]) for path, obj in walk(content) if "playlistVideoListRenderer" in obj]
    if len(old_lists) == 1:
        path, container = old_lists[0]
        return container.get("contents", []), container.get("targetId") or "playlist-video-list", root_path + path + ("playlistVideoListRenderer", "contents"), container.get("continuations", [])
    section = content.get("sectionListRenderer", {})
    candidates = []
    for index, item in enumerate(section.get("contents", [])):
        container = item.get("itemSectionRenderer", {})
        entries = container.get("contents", [])
        if any(is_video_item(x) for x in entries):
            candidates.append((entries, container.get("targetId"), root_path + ("sectionListRenderer", "contents", index, "itemSectionRenderer", "contents"), []))
    if len(candidates) != 1:
        raise ValueError("Expected one primary playlist video list; found " + str(len(candidates)))
    if not isinstance(candidates[0][1], str) or not candidates[0][1].strip():
        raise ValueError("Primary video list has no usable continuation target")
    return candidates[0]


def continued_list(data, target):
    """Select a continuation only when its primary-list identity is explicit."""
    if not isinstance(target, str) or not target.strip():
        raise ValueError("A usable primary-list target is required")
    candidates, ignored = [], []
    for root in ["onResponseReceivedActions", "onResponseReceivedCommands", "onResponseReceivedEndpoints"]:
        for index, action in enumerate(data.get(root, [])):
            for kind in ["appendContinuationItemsAction", "reloadContinuationItemsCommand"]:
                item = action.get(kind)
                if not item:
                    continue
                if item.get("targetId") == target:
                    candidates.append((item.get("continuationItems", []), (root, index, kind, "continuationItems"), []))
                else:
                    ignored.append(item.get("targetId"))
    legacy = data.get("continuationContents", {}).get("playlistVideoListContinuation")
    if legacy and not candidates and legacy.get("targetId", target) == target:
        candidates.append((legacy.get("contents", []), ("continuationContents", "playlistVideoListContinuation", "contents"), legacy.get("continuations", [])))
    if len(candidates) != 1:
        raise ValueError("Expected one continuation for primary target %r; found %d, other targets %r" % (target, len(candidates), ignored))
    return (*candidates[0], ignored)


def parse_entry(item):
    kind = next((k for k in ["playlistVideoRenderer", "videoRenderer", "lockupViewModel"] if k in item), None)
    if not kind:
        return None
    obj = item[kind]
    video_id = obj.get("videoId") or obj.get("contentId")
    if kind == "lockupViewModel" and obj.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO":
        return None
    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Invalid or missing public video ID in list item")
    meta = obj.get("metadata", {}).get("lockupMetadataViewModel", {})
    title = text(obj.get("title")) or text(meta.get("title"))
    channel_id = None
    for _, child in walk(obj):
        bid = child.get("browseEndpoint", {}).get("browseId", "")
        if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", bid):
            channel_id = bid
            break
    owner = text(obj.get("shortBylineText")) or text(obj.get("ownerText"))
    if not owner:
        rows = meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", [])
        if rows:
            owner = " ".join(text(p.get("text")) for p in rows[0].get("metadataParts", []))
    duration = text(obj.get("lengthText"))
    if not duration:
        for _, child in walk(obj.get("contentImage", {})):
            badge = child.get("thumbnailBadgeViewModel", {})
            if re.fullmatch(r"\d+(?::\d{2}){1,2}", badge.get("text", "")):
                duration = badge["text"]
                break
    unavailable = obj.get("isPlayable") is False or bool(re.search(r"private video|deleted video|unavailable|video privado|video eliminado", title, re.I))
    return {"video_id": video_id, "url": "https://www.youtube.com/watch?v=" + video_id, "title": title, "channel_id": channel_id, "channel_name": owner or None, "duration_text": duration or None, "visibility": "unavailable_placeholder" if unavailable else "listed", "renderer": kind, "source_position": text(obj.get("index")) or None}


def parse_list(items, legacy_continuations=()):
    entries, tokens, unknown = [], [], []
    for index, item in enumerate(items):
        token = item_token(item)
        if token:
            tokens.append(token)
            continue
        entry = parse_entry(item)
        if entry:
            entries.append(entry)
        else:
            unknown.append({"index": index, "keys": list(item)})
    for obj in legacy_continuations:
        if not isinstance(obj, dict) or not isinstance(obj.get("nextContinuationData"), dict):
            raise ValueError("Unsupported legacy continuation control")
        token = obj["nextContinuationData"].get("continuation")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Malformed legacy continuation token")
        tokens.append(token)
    tokens = list(dict.fromkeys(tokens))
    if unknown:
        raise ValueError("Unrecognized primary-list items: " + json.dumps(unknown))
    if len(tokens) > 1:
        raise ValueError("Multiple primary-list continuations require review")
    return entries, tokens


def playlist_metadata(data):
    metadata = data.get("metadata", {}).get("playlistMetadataRenderer", {})
    declared = None
    for _, obj in walk({"header": data.get("header", {}), "sidebar": data.get("sidebar", {})}):
        value = text(obj)
        match = re.fullmatch(r"([\d,.]+)\s+v[ií]deos?", value.strip(), re.I)
        if match:
            declared = int(re.sub(r"\D", "", match[1]))
            break
    alerts = []
    for item in data.get("alerts", []):
        for renderer in item.values():
            if isinstance(renderer, dict) and text(renderer.get("text")):
                alerts.append(text(renderer["text"]))
    hidden = sum(int(m.group(1)) for a in alerts if (m := re.search(r"(\d+) unavailable videos? (?:is|are) hidden", a, re.I)))
    return {"title": metadata.get("title"), "declared_items": declared, "hidden_unavailable_count": hidden, "hidden_unavailable_notice": any(re.search(r"unavailable videos? (?:is|are) hidden", a, re.I) for a in alerts), "notices": alerts}


def completion(entries, pending, error, declared, hidden, cycle=False, limit=False):
    visible = len(entries)
    placeholders = sum(x.get("visibility") == "unavailable_placeholder" for x in entries)
    delta = None if declared is None else declared - visible - hidden
    if error:
        status = "error"
    elif cycle:
        status = "cycle_detected"
    elif pending:
        status = "limit_reached" if limit else "pending"
    elif delta not in (None, 0):
        status = "exhausted_count_mismatch"
    elif declared is None:
        status = "exhausted_count_unknown"
    else:
        status = "exhausted_with_unavailable" if hidden or placeholders else "exhausted_reconciled"
    return {"status": status, "pagination_exhausted": not pending and not error and not cycle, "count_reconciled": None if declared is None else delta == 0, "unaccounted_declared_items": delta, "returned_memberships": visible, "visible_memberships": visible, "normal_title_memberships": sum(bool(x.get("title")) and x.get("visibility") != "unavailable_placeholder" for x in entries), "unavailable_placeholder_memberships": placeholders, "unique_video_ids": len({x["video_id"] for x in entries}), "duplicate_memberships": visible - len({x["video_id"] for x in entries})}


def cache_key(label, show_unavailable=False):
    return label + ("__unavailable" if show_unavailable else "")


def observed_unavailable_action(label):
    """Read unavailable-view parameters from the observed normal public menu action."""
    expected_id = SEEDS[label][0]
    for source in sorted((BASE / "caches" / label).glob("page_[0-9][0-9][0-9].json"), reverse=True):
        data = read(source)
        for path, obj in walk(data):
            item = obj.get("menuNavigationItemRenderer", {})
            if text(item.get("text")) != "Show unavailable videos":
                continue
            endpoint = item.get("navigationEndpoint", {})
            browse = endpoint.get("browseEndpoint", {})
            if browse.get("browseId") != "VL" + expected_id:
                raise ValueError("Unavailable-view menu points to a different playlist")
            if endpoint.get("commandMetadata", {}).get("webCommandMetadata", {}).get("apiUrl") != "/youtubei/v1/browse":
                raise ValueError("Unrecognized public unavailable-view action")
            return {k: browse[k] for k in ["browseId", "params"] if k in browse}, {"cache_path": str(source), "cache_sha256": sha(source.read_bytes()), "json_path": list(path + ("menuNavigationItemRenderer", "navigationEndpoint", "browseEndpoint")), "action_label": "Show unavailable videos"}
    raise ValueError("No observed normal public Show unavailable videos action in saved pages")


def load_initial(label, show_unavailable=False):
    playlist_id, _, _ = SEEDS[label]
    url = "https://www.youtube.com/playlist?list=" + playlist_id
    directory = BASE / "caches" / cache_key(label, show_unavailable)
    directory.mkdir(parents=True, exist_ok=True)
    raw_path, meta_path = directory / "page_000.json", directory / "page_000.meta.json"
    if raw_path.exists():
        meta = read(meta_path)
        if not show_unavailable and meta["requested_url"] != url:
            raise ValueError("Cache URL mismatch")
        context = read(directory / "context.json") if show_unavailable else context_from((directory / "initial.html").read_text())
        meta["cache_reused"] = True
        return read(raw_path), context, meta
    if show_unavailable:
        action, observation = observed_unavailable_action(label)
        context = context_from((BASE / "caches" / label / "initial.html").read_text())
        payload, meta = request("https://www.youtube.com/youtubei/v1/browse?prettyPrint=false", json.dumps({"context": context, **action}).encode())
        data = json.loads(payload)
        meta["normal_public_action_provenance"] = observation
        write(directory / "context.json", context)
    else:
        payload, meta = request(url)
        html = payload.decode()
        data, context = assigned(html, "ytInitialData"), context_from(html)
        (directory / "initial.html").write_text(html)
    initial_list(data)
    meta["cache_reused"] = False
    write(raw_path, data)
    write(meta_path, meta)
    return data, context, meta


def load_next(label, page, token, context):
    directory = BASE / "caches" / label
    raw_path, meta_path = directory / f"page_{page:03}.json", directory / f"page_{page:03}.meta.json"
    fingerprint = sha(token)
    if raw_path.exists():
        meta = read(meta_path)
        if meta.get("request_token_sha256") != fingerprint:
            raise ValueError("Continuation cache identity mismatch; preserve both snapshots")
        meta["cache_reused"] = True
        return read(raw_path), meta
    url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
    payload, meta = request(url, json.dumps({"context": context, "continuation": token}).encode())
    data = json.loads(payload)
    meta["request_token_sha256"] = fingerprint
    meta["cache_reused"] = False
    write(raw_path, data)
    write(meta_path, meta)
    return data, meta


def crawl_one(label, max_pages=30, show_unavailable=False):
    playlist_id, fixture_label, scope = SEEDS[label]
    key = cache_key(label, show_unavailable)
    result = {"collection_key": label, "cache_key": key, "snapshot_view": "include_unavailable" if show_unavailable else "default_visible", "collection_id": playlist_id, "collection_type": "playlist", "source_role": "core_declared_source" if label in CORE_SEED_KEYS else "supplemental_regional_membership", "source_url": "https://www.youtube.com/playlist?list=" + playlist_id, "scope": scope, "original_fixture": str(ORIGINAL / (fixture_label + ".json")), "started_at": now(), "pages": [], "memberships": [], "errors": [], "pending_token_sha256": [], "ignored_outer_continuations": 0, "notice_observations": [], "declared_count_observations": []}
    def merge_metadata(data, page):
        nonlocal declared, hidden
        observed = playlist_metadata(data)
        if observed["title"] and not result.get("title"):
            result["title"] = observed["title"]
        if observed["declared_items"] is not None:
            result["declared_count_observations"].append({"page_index": page, "value": observed["declared_items"]})
            if declared is None:
                declared = observed["declared_items"]
            elif declared != observed["declared_items"]:
                raise ValueError("Playlist declared count changed during the same snapshot")
        hidden = max(hidden, observed["hidden_unavailable_count"])
        for notice in observed["notices"]:
            result["notice_observations"].append({"page_index": page, "response_path": str(BASE / "caches" / key / f"page_{page:03}.json"), "text": notice})
        result["notices"] = list(dict.fromkeys(x["text"] for x in result["notice_observations"]))
        result["hidden_unavailable_notice"] = any(re.search(r"unavailable videos? (?:is|are) hidden", a, re.I) for a in result["notices"])
        result["declared_items"], result["hidden_unavailable_count"] = declared, hidden
    pending, seen, error, cycle = [], set(), None, False
    declared, hidden = None, 0
    visible_ids = None
    if show_unavailable:
        visible_state = read(BASE / "caches" / label / "state.json")
        if visible_state.get("pagination_exhausted"):
            visible_ids = {x["video_id"] for x in visible_state["memberships"]}
    def annotate_visibility(entry):
        if visible_ids is not None and entry["video_id"] not in visible_ids:
            entry["hidden_in_default_view"] = True
            entry["visibility_basis"] = "Only returned by observed public Show unavailable videos action; absent from exhausted default view"
            if not entry.get("title"):
                entry["visibility"] = "unavailable_placeholder"
                entry["channel_id"], entry["channel_name"] = None, None
        return entry
    try:
        data, context, meta = load_initial(label, show_unavailable)
        merge_metadata(data, 0)
        items, target, path, legacy = initial_list(data)
        entries, pending = parse_list(items, legacy)
        result["target_id"] = target
        result["ignored_outer_continuations"] = len({t for _, t in all_tokens(data)} - set(pending))
        result["pages"].append({"page_index": 0, "response_path": str(BASE / "caches" / key / "page_000.json"), "list_json_path": list(path), "items": len(entries), "request": meta})
        for entry in entries:
            entry = annotate_visibility(entry)
            result["memberships"].append({**entry, "collection_id": playlist_id, "collection_key": label, "snapshot_view": result["snapshot_view"], "source_url": result["source_url"], "page_index": 0, "position": len(result["memberships"]) + 1})
        for page in range(1, max_pages):
            if not pending:
                break
            token = pending[0]
            if token in seen:
                cycle = True
                break
            seen.add(token)
            data, meta = load_next(key, page, token, context)
            merge_metadata(data, page)
            items, path, legacy, ignored = continued_list(data, target)
            entries, next_tokens = parse_list(items, legacy)
            if not entries and next_tokens:
                raise ValueError("Empty primary page still has continuation; review before advancing")
            result["pages"].append({"page_index": page, "response_path": str(BASE / "caches" / key / f"page_{page:03}.json"), "list_json_path": list(path), "items": len(entries), "ignored_action_targets": ignored, "request": meta})
            for entry in entries:
                entry = annotate_visibility(entry)
                result["memberships"].append({**entry, "collection_id": playlist_id, "collection_key": label, "snapshot_view": result["snapshot_view"], "source_url": result["source_url"], "page_index": page, "position": len(result["memberships"]) + 1})
            pending = next_tokens
            result["pending_token_sha256"] = [sha(t) for t in pending]
            interim = {**result, **completion(result["memberships"], pending, None, declared, hidden)}
            write(BASE / "caches" / key / "state.json", interim)
            print(json.dumps({"collection": label, "page": page, "new_appearances": len(entries), "total_appearances": len(result["memberships"]), "pending": bool(pending)}), flush=True)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "at": now()}
        result["errors"].append(error)
    result["pending_token_sha256"] = [sha(t) for t in pending]
    if show_unavailable and visible_ids is not None:
        result["default_view_video_ids_not_returned"] = sorted(visible_ids - {x["video_id"] for x in result["memberships"]})
        result["hidden_only_video_ids"] = [x["video_id"] for x in result["memberships"] if x.get("hidden_in_default_view")]
    result.update(completion(result["memberships"], pending, error, declared, hidden, cycle, bool(pending) and len(result["pages"]) >= max_pages))
    result["finished_at"] = now()
    write(BASE / "caches" / key / "state.json", result)
    return result


def validate_retained_channel(snapshot, label):
    """Replay every retained page, including the historical About branch.

    The earlier collector queued all public continuation controls. Its request
    times were not stored, so this checks content and queue closure, not freshness.
    """
    errors, receipts, pending, seen_tokens = [], [], [], set()
    target = None
    pages = snapshot.get("pages", [])
    if not pages or [p.get("page") for p in pages] != list(range(len(pages))):
        return [{"type": "NonconsecutiveChannelPages", "message": "Retained channel pages must start at zero and contain every page index"}], []
    for index, page in enumerate(pages):
        raw_path = ORIGINAL / (label + ("_" + str(index) if index else "") + ".json")
        if not raw_path.exists():
            errors.append({"type": "MissingChannelResponse", "page": index, "path": str(raw_path)})
            break
        raw = read(raw_path)
        role = "primary_video_grid"
        try:
            if not index:
                tabs = raw.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
                selected = [t["tabRenderer"] for t in tabs if t.get("tabRenderer", {}).get("selected")]
                if len(selected) != 1:
                    raise ValueError("Expected one selected channel surface")
                grid = selected[0].get("content", {}).get("richGridRenderer", {})
                target = grid.get("targetId")
                if not isinstance(target, str) or not target.strip():
                    raise ValueError("Selected channel grid has no usable target")
                items = grid.get("contents", [])
            else:
                actions = [a.get(k) for root in ["onResponseReceivedActions", "onResponseReceivedCommands", "onResponseReceivedEndpoints"] for a in raw.get(root, []) for k in ["appendContinuationItemsAction", "reloadContinuationItemsCommand"] if a.get(k)]
                matching = [a for a in actions if a.get("targetId") == target]
                if not matching and not page.get("items"):
                    # Only the positively identified historical About branch
                    # may be skipped. An empty derived projection cannot prove
                    # that a wrong-target raw response contains no videos.
                    about_items = actions[0].get("continuationItems", []) if len(actions) == 1 else []
                    about_branch = bool(about_items) and all(isinstance(i, dict) and set(i) == {"aboutChannelRenderer"} for i in about_items)
                    if not about_branch or all_tokens(raw):
                        raise ValueError("Unrecognized non-primary channel response")
                    receipts.append({"page_index": index, "response_path": str(raw_path), "sha256": sha(raw_path.read_bytes()), "items": 0, "role": "verified_about_branch"})
                    continue
                if not pending:
                    raise ValueError("No preceding primary continuation supports this page")
                token = pending[0]
                if token in seen_tokens:
                    raise ValueError("Primary continuation cycle")
                seen_tokens.add(token)
                items, _, legacy, _ = continued_list(raw, target)
                if legacy:
                    raise ValueError("Unexpected legacy playlist controls in channel grid")
            unwrapped = [item["richItemRenderer"]["content"] if "richItemRenderer" in item else item for item in items]
            entries, pending = parse_list(unwrapped)
            raw_ids = list(dict.fromkeys(entry["video_id"] for entry in entries))
        except (KeyError, ValueError, TypeError) as exc:
            errors.append({"type": "ChannelPageReplayFailure", "page": index, "message": str(exc)})
            break
        if raw_ids != [item["id"] for item in page.get("items", [])]:
            errors.append({"type": "ChannelPageProjectionMismatch", "page": index})
        receipts.append({"page_index": index, "response_path": str(raw_path), "sha256": sha(raw_path.read_bytes()), "items": len(raw_ids), "role": role})
    if pending:
        errors.append({"type": "UnconsumedChannelContinuation", "count": len(pending)})
    return errors, receipts


def reused_channel(label, surface):
    """Retain historical metadata only with a replay of the complete page chain."""
    path = WORK / (label + "_full_public_catalog.json")
    if not path.exists():
        return {"collection_key": label, "collection_id": JEP_CHANNEL + ":" + surface, "collection_type": "channel_surface", "source_role": "reused_channel_discovery", "source_url": "https://www.youtube.com/@jepcolombia/" + surface, "title": "JEP Colombia / " + surface, "status": "required_snapshot_missing", "pagination_exhausted": False, "count_reconciled": None, "declared_items": None, "visible_memberships": 0, "unique_video_ids": 0, "errors": [{"type": "MissingSourceSnapshot", "message": "Named full channel snapshot is absent; no channel completeness claim", "path": str(path)}], "pending_token_sha256": [], "memberships": []}
    snapshot = read(path)
    entries = []
    for page in snapshot["pages"]:
        for item in page.get("items", []):
            if item.get("type") == "LOCKUP_CONTENT_TYPE_PLAYLIST":
                raise ValueError("Unexpected playlist in channel video surface")
            entries.append({"video_id": item["id"], "url": "https://www.youtube.com/watch?v=" + item["id"], "title": item["title"], "channel_id": JEP_CHANNEL, "channel_name": "JEP Colombia", "duration_text": item.get("length") or None, "visibility": "listed", "renderer": item.get("kind"), "collection_id": JEP_CHANNEL + ":" + surface, "collection_key": label, "source_url": "https://www.youtube.com/@jepcolombia/" + surface, "page_index": page["page"], "position": len(entries) + 1})
    chain_errors, page_receipts = validate_retained_channel(snapshot, label)
    last = snapshot["pages"][-1]["page"] if snapshot.get("pages") else 0
    terminal = ORIGINAL / (label + ("_" + str(last) if last else "") + ".json")
    if not terminal.exists():
        return {"collection_key": label, "collection_id": JEP_CHANNEL + ":" + surface, "collection_type": "channel_surface", "source_role": "reused_channel_discovery", "source_url": "https://www.youtube.com/@jepcolombia/" + surface, "title": "JEP Colombia / " + surface, "status": "terminal_snapshot_missing", "pagination_exhausted": False, "count_reconciled": None, "declared_items": None, "visible_memberships": len(entries), "unique_video_ids": len({x["video_id"] for x in entries}), "errors": [{"type": "MissingTerminalSnapshot", "message": "Channel records retained but terminal pagination cannot be verified", "path": str(terminal)}], "pending_token_sha256": [], "provenance": {"catalog_path": str(path), "catalog_sha256": sha(path.read_bytes())}, "memberships": entries}
    raw = read(terminal)
    tokens = all_tokens(raw)
    shapes = [list(p) for p, obj in walk(raw) if any(k in obj for k in ["continuationItemViewModel", "continuationItemRenderer", "nextContinuationData", "reloadContinuationData"])]
    errors = [p for p in snapshot["pages"] if "error" in p] + chain_errors
    valid = not tokens and not shapes and not errors and snapshot.get("continuation_remaining") is False
    return {"collection_key": label, "collection_id": JEP_CHANNEL + ":" + surface, "collection_type": "channel_surface", "source_role": "reused_channel_discovery", "source_url": "https://www.youtube.com/@jepcolombia/" + surface, "title": "JEP Colombia / " + surface, "scope": "All-channel discovery metadata only; no Casanare admission implied", "status": "reused_terminal_snapshot" if valid else "reused_snapshot_incomplete", "pagination_exhausted": valid, "count_reconciled": None, "declared_items": None, "visible_memberships": len(entries), "unique_video_ids": len({x["video_id"] for x in entries}), "hidden_unavailable_count": None, "notices": [], "errors": errors, "pending_token_sha256": [sha(t) for _, t in tokens], "pages": page_receipts, "provenance": {"catalog_path": str(path), "catalog_sha256": sha(path.read_bytes()), "terminal_cache_path": str(terminal), "terminal_cache_sha256": sha(terminal.read_bytes()), "terminal_continuation_shapes": shapes, "original_fetch_time": "Not stored by original crawler; reused snapshot, not refetched"}, "memberships": entries}


def parse_shorts_list(items):
    entries, tokens = [], []
    for item in items:
        token = item_token(item)
        if token:
            tokens.append(token)
            continue
        content = item.get("richItemRenderer", {}).get("content", {})
        value = content.get("shortsLockupViewModel", {})
        endpoint = value.get("onTap", {}).get("innertubeCommand", {}).get("reelWatchEndpoint", {})
        vid = endpoint.get("videoId")
        if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            raise ValueError("Unknown primary Shorts item shape: " + str(list(item)))
        entries.append({"video_id": vid, "url": "https://www.youtube.com/watch?v=" + vid, "shorts_url": "https://www.youtube.com/shorts/" + vid, "title": text(value.get("overlayMetadata", {}).get("primaryText")), "channel_id": JEP_CHANNEL, "channel_name": "JEP Colombia", "duration_text": None, "visibility": "listed", "renderer": "shortsLockupViewModel", "source_position": str(value.get("indexInCollection")) if value.get("indexInCollection") is not None else None, "video_type": "Shorts"})
    tokens = list(dict.fromkeys(tokens))
    if len(tokens) > 1:
        raise ValueError("Multiple primary Shorts continuations")
    return entries, tokens


def crawl_shorts(max_pages=50):
    label, url = "channel_shorts", "https://www.youtube.com/@jepcolombia/shorts"
    directory = BASE / "caches" / label
    directory.mkdir(parents=True, exist_ok=True)
    initial_path = directory / "page_000.json"
    result = {"collection_key": label, "collection_id": JEP_CHANNEL + ":shorts", "collection_type": "channel_surface", "source_role": "supplemental_channel_discovery", "source_url": url, "title": "JEP Colombia / Shorts", "scope": "Shorts discovery metadata only; no unrelated substantive content inspected and no full-hearing equivalence assumed", "started_at": now(), "declared_items": None, "notices": [], "pages": [], "memberships": [], "errors": []}
    pending, seen, error, cycle = [], set(), None, False
    try:
        source = ORIGINAL / "deep_channel_videos.json"
        if source.exists():
            observed = read(source)
            tabs = observed.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            matches = [(n, t["tabRenderer"]) for n, t in enumerate(tabs) if t.get("tabRenderer", {}).get("endpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url") == "/@jepcolombia/shorts"]
            if len(matches) != 1:
                raise ValueError("Expected one observed official Shorts tab")
            result["discovery_provenance"] = {"source_path": str(source), "source_sha256": sha(source.read_bytes()), "json_path": ["contents", "twoColumnBrowseResultsRenderer", "tabs", matches[0][0], "tabRenderer", "endpoint"], "observed_url": "/@jepcolombia/shorts"}
        elif not initial_path.exists():
            raise ValueError("Observed Shorts tab provenance and own cached first page are absent; do not silently create a new discovery seed")
        if initial_path.exists():
            data = read(initial_path)
            meta = read(directory / "page_000.meta.json")
            if meta.get("requested_url") != url:
                raise ValueError("Shorts cache URL mismatch")
            html_value = (directory / "initial.html").read_text()
        else:
            payload, meta = request(url)
            html_value = payload.decode()
            data = assigned(html_value, "ytInitialData")
            (directory / "initial.html").write_text(html_value)
            write(initial_path, data)
            write(directory / "page_000.meta.json", meta)
        context = context_from(html_value)
        tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
        selected = [(n, t["tabRenderer"]) for n, t in enumerate(tabs) if t.get("tabRenderer", {}).get("selected")]
        if len(selected) != 1 or selected[0][1].get("title") != "Shorts":
            raise ValueError("Cannot identify selected Shorts grid")
        tab_index, tab = selected[0]
        grid = tab.get("content", {}).get("richGridRenderer", {})
        target = grid.get("targetId")
        if not target:
            raise ValueError("Shorts primary grid has no continuation target")
        result["target_id"] = target
        entries, pending = parse_shorts_list(grid.get("contents", []))
        result["ignored_outer_continuations"] = len({t for _, t in all_tokens(data)} - set(pending))
        for page in range(max_pages):
            if page:
                if not pending:
                    break
                token = pending[0]
                if token in seen:
                    cycle = True
                    break
                seen.add(token)
                data, meta = load_next(label, page, token, context)
                items, path, legacy, ignored = continued_list(data, target)
                if legacy:
                    raise ValueError("Unexpected legacy playlist continuation in Shorts")
                entries, next_tokens = parse_shorts_list(items)
                if not entries and next_tokens:
                    raise ValueError("Empty Shorts page still has continuation")
            else:
                path = ("contents", "twoColumnBrowseResultsRenderer", "tabs", tab_index, "tabRenderer", "content", "richGridRenderer", "contents")
                ignored, next_tokens = [], pending
            result["pages"].append({"page_index": page, "response_path": str(directory / f"page_{page:03}.json"), "list_json_path": list(path), "items": len(entries), "ignored_action_targets": ignored, "request": meta})
            for entry in entries:
                result["memberships"].append({**entry, "collection_id": result["collection_id"], "collection_key": label, "source_url": url, "page_index": page, "position": len(result["memberships"]) + 1})
            pending = next_tokens
            result["pending_token_sha256"] = [sha(t) for t in pending]
            write(directory / "state.json", {**result, **completion(result["memberships"], pending, None, None, 0)})
            print(json.dumps({"collection": label, "page": page, "new_appearances": len(entries), "total_appearances": len(result["memberships"]), "pending": bool(pending)}), flush=True)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "at": now()}
        result["errors"].append(error)
    result["pending_token_sha256"] = [sha(t) for t in pending]
    result.update(completion(result["memberships"], pending, error, None, 0, cycle, bool(pending) and len(result["pages"]) >= max_pages))
    result["finished_at"] = now()
    write(directory / "state.json", result)
    export_all()
    print(json.dumps({k: result.get(k) for k in ["collection_key", "status", "returned_memberships", "unique_video_ids", "pagination_exhausted", "pending_token_sha256", "errors"]}), flush=True)
    return result


def export_all():
    collections = [reused_channel("deep_channel_videos", "videos"), reused_channel("deep_channel_streams", "streams")]
    shorts_path = BASE / "caches" / "channel_shorts" / "state.json"
    if shorts_path.exists():
        collections.append(read(shorts_path))
    alternate_views = []
    for label in SEEDS:
        path = BASE / "caches" / label / "state.json"
        if path.exists():
            chosen = read(path)
            expanded_path = BASE / "caches" / cache_key(label, True) / "state.json"
            if expanded_path.exists():
                expanded = read(expanded_path)
                if expanded.get("pagination_exhausted") and expanded.get("count_reconciled"):
                    alternate_views.append({k: v for k, v in chosen.items() if k != "memberships"})
                    chosen = expanded
                else:
                    alternate_views.append({k: v for k, v in expanded.items() if k != "memberships"})
            collections.append(chosen)
        else:
            playlist_id, _, scope = SEEDS[label]
            collections.append({"collection_key": label, "collection_id": playlist_id, "collection_type": "playlist", "source_role": "core_declared_source" if label in CORE_SEED_KEYS else "supplemental_regional_membership", "source_url": "https://www.youtube.com/playlist?list=" + playlist_id, "scope": scope, "status": "required_snapshot_missing", "pagination_exhausted": False, "count_reconciled": None, "declared_items": None, "visible_memberships": 0, "unique_video_ids": 0, "errors": [{"type": "MissingSourceSnapshot", "message": "Declared playlist has not been crawled"}], "pending_token_sha256": [], "memberships": []})
    memberships = []
    for collection in collections:
        items = collection.pop("memberships")
        memberships.extend(items)
        collection.setdefault("returned_memberships", len(items))
        collection.setdefault("normal_title_memberships", sum(bool(x.get("title")) and x.get("visibility") != "unavailable_placeholder" for x in items))
        collection.setdefault("unavailable_placeholder_memberships", sum(x.get("visibility") == "unavailable_placeholder" for x in items))
        collection.setdefault("duplicate_memberships", len(items) - len({x["video_id"] for x in items}))
    web_path = BASE / "web_seed_memberships.json"
    if web_path.exists():
        items = read(web_path)
        memberships.extend(items)
        web_collection = read(BASE / "web_seed_manifest.json")
        web_collection.update({"normal_title_memberships": len(items), "unavailable_placeholder_memberships": 0, "duplicate_memberships": len(items) - len({x["video_id"] for x in items})})
        collections.append(web_collection)
    details_path = BASE / "video_details.json"
    details = read(details_path) if details_path.exists() else {}
    nodes = {}
    for m in memberships:
        vid = m["video_id"]
        if vid not in nodes:
            nodes[vid] = {"video_id": vid, "url": m["url"], "title": m["title"], "observed_titles": [], "channel_id": m.get("channel_id"), "channel_name": m.get("channel_name"), "duration_text": m.get("duration_text"), "description": None, "listing_visibility": [], "scope_status": "Not classified; collection membership alone does not establish substantive Casanare scope", "collection_ids": [], "source_urls": [], "metadata_provenance": []}
        node = nodes[vid]
        if m["title"] not in node["observed_titles"]:
            node["observed_titles"].append(m["title"])
        if m["collection_id"] not in node["collection_ids"]:
            node["collection_ids"].append(m["collection_id"])
        if m["source_url"] not in node["source_urls"]:
            node["source_urls"].append(m["source_url"])
        if m.get("visibility") not in node["listing_visibility"]:
            node["listing_visibility"].append(m.get("visibility"))
        if not node.get("duration_text") and m.get("duration_text"):
            node["duration_text"] = m["duration_text"]
    for vid, detail in details.items():
        if vid in nodes:
            nodes[vid].update({k: detail[k] for k in ["title", "channel_id", "channel_name", "description", "length_seconds", "upload_date", "publish_date", "live", "playability", "playability_reason", "captions_available"] if k in detail and detail[k] is not None})
            nodes[vid]["metadata_provenance"].append(detail.get("provenance"))
    write(BASE / "catalog.json", list(nodes.values()))
    write(BASE / "memberships.json", memberships)
    unavailable = {}
    for item in memberships:
        if item.get("visibility") == "unavailable_placeholder":
            unavailable.setdefault(item["video_id"], {"video_id": item["video_id"], "url": item["url"], "title": item.get("title") or None, "memberships": [], "limitation": "Public listing placeholder; title/content unavailable in this view. No playability or Casanare scope inferred."})["memberships"].append({"collection_id": item["collection_id"], "collection_key": item["collection_key"], "position": item["position"], "source_url": item["source_url"], "snapshot_view": item.get("snapshot_view"), "visibility_basis": item.get("visibility_basis")})
    manifest = {"schema_version": "1.2", "generated_at": now(), "python": sys.executable, "network_concurrency_limit": 2, "http_429_policy": "Stop the active batch; no retry loop", "scope_contract": "Broad discovery metadata is kept separate from substantive Case 03–Casanare inclusion decisions. This crawler fetches no transcripts or media.", "snapshot_selection_rule": "Prefer an exhausted, count-reconciled include-unavailable view. Preserve the default-visible snapshot under alternate_snapshot_views; its earlier discrepancy remains historical evidence, not an unresolved selected-view gap.", "count_definitions": {"returned_memberships": "Returned list positions, including unavailable placeholders and repeated appearances", "visible_memberships": "Legacy alias of returned_memberships; NOT playable video count", "normal_title_memberships": "Returned positions with a nonempty public title, excluding known unavailable placeholders; playability not implied", "unique_video_ids": "Distinct public video IDs within the collection; includes placeholder IDs", "hidden_unavailable_count": "Numeric hidden count explicitly stated by the selected view; placeholders returned by Show unavailable are counted separately", "unavailable_placeholder_memberships": "Returned blank-title placeholder positions revealed by the normal unavailable-item action", "count_reconciled": "Declared count equals returned positions plus any explicitly numbered entries still hidden", "pagination_exhausted": "No actual primary-list continuation remains, with no crawl error or cycle; does not establish complete historical availability"}, "collections": collections, "alternate_snapshot_views": alternate_views, "unique_video_ids": len(nodes), "membership_count": len(memberships), "unavailable_placeholder_unique_ids": len(unavailable), "unavailable_placeholders": list(unavailable.values()), "bounded_watch_metadata_records": len(details), "bounded_watch_metadata_errors": sum(bool(x.get("error")) for x in details.values()), "playlist_response_pages_in_selected_snapshots": sum(len(c.get("pages", [])) for c in collections if c["collection_type"] == "playlist"), "complete_reverse_audit_claimed": False}
    write(BASE / "crawl_manifest.json", manifest)
    return manifest


class HtmlTree(html.parser.HTMLParser):
    """Small read-only tree for the observed official page; comments are ignored."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "root", "attrs": {}, "children": []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": []}
        self.stack[-1]["children"].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]["tag"] == tag:
                self.stack = self.stack[:index]
                return

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1]["children"].append(data)


def html_nodes(node):
    if isinstance(node, dict):
        yield node
        for child in node["children"]:
            yield from html_nodes(child)


def html_text(node):
    if isinstance(node, str):
        return node
    return " ".join(html_text(x) for x in node["children"])


def youtube_id(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host in {"youtube.com", "m.youtube.com"}:
        value = parse_qs(parsed.query).get("v", [None])[0]
        if not value and parsed.path.startswith(("/embed/", "/live/", "/shorts/")):
            value = parsed.path.split("/")[2]
    elif host == "youtu.be":
        value = parsed.path.lstrip("/").split("/")[0]
    else:
        return None
    return value if value and re.fullmatch(r"[A-Za-z0-9_-]{11}", value) else None


def web_seed():
    """Extract only explicitly Casanare-labelled active cards on the known page."""
    url = "https://www.jep.gov.co/macrocasos/caso03.html"
    directory = BASE / "caches" / "web_case03"
    directory.mkdir(parents=True, exist_ok=True)
    path, meta_path = directory / "page.html", directory / "page.meta.json"
    if not path.exists():
        payload, meta = request(url)
        path.write_bytes(payload)
        write(meta_path, meta)
    meta = read(meta_path)
    if meta["requested_url"] != url:
        raise ValueError("Official page cache URL mismatch")
    parser = HtmlTree()
    parser.feed(path.read_text())
    cards = [n for n in html_nodes(parser.root) if n["tag"] == "div" and "cause-entry" in n["attrs"].get("class", "").split()]
    memberships, selected = [], []
    collection_id = url + "#casanare-labelled-cards"
    for index, card in enumerate(cards, 1):
        headings = [" ".join(html_text(n).split()) for n in html_nodes(card) if n["tag"] == "h3"]
        heading = " | ".join(headings)
        if not re.search(r"\bcasanare\b", heading, re.I):
            continue
        links = {}
        for node in html_nodes(card):
            if node["tag"] not in {"a", "iframe"}:
                continue
            href = node["attrs"].get("href") or node["attrs"].get("src") or ""
            vid = youtube_id(href)
            if not vid:
                continue
            role = "iframe" if node["tag"] == "iframe" else "image_link" if any(x["tag"] == "img" for x in html_nodes(node)) else "text_link"
            links.setdefault(vid, []).append({"href": href, "role": role, "anchor_text": " ".join(html_text(node).split())})
        selected.append({"card_index": index, "heading": heading, "video_ids": list(links), "multiple_video_ids": len(links) > 1})
        for vid, link_evidence in links.items():
            memberships.append({"video_id": vid, "url": "https://www.youtube.com/watch?v=" + vid, "title": heading, "channel_id": None, "channel_name": None, "duration_text": None, "visibility": "listed", "renderer": "official_page_casanare_labelled_card", "collection_id": collection_id, "collection_key": "web_case03_casanare_cards", "source_url": url, "page_index": 0, "position": len(memberships) + 1, "source_position": str(index), "source_context": {"heading": heading, "card_index": index, "links": link_evidence, "card_has_multiple_video_ids": len(links) > 1, "cache_path": str(path), "cache_sha256": sha(path.read_bytes())}})
    result = {"collection_id": collection_id, "collection_key": "web_case03_casanare_cards", "collection_type": "official_web_page_section", "source_role": "core_declared_source", "source_url": url, "title": "Official JEP Case 03 page — Casanare-labelled hearing cards", "scope": "Only active cards whose heading explicitly says Casanare. HTML comments and other regional cards excluded; heading/thumbnail link disagreement preserved.", "status": "observed_cards_extracted", "pagination_exhausted": None, "count_reconciled": None, "declared_items": None, "returned_memberships": len(memberships), "visible_memberships": len(memberships), "unique_video_ids": len({x["video_id"] for x in memberships}), "casanare_labelled_cards": len(selected), "all_active_cards": len(cards), "cards": selected, "provenance": meta, "errors": [], "pending_token_sha256": []}
    write(BASE / "web_seed_memberships.json", memberships)
    write(BASE / "web_seed_manifest.json", result)
    export_all()
    print(json.dumps({k: result[k] for k in ["casanare_labelled_cards", "returned_memberships", "unique_video_ids"]}), flush=True)


def set_json_path(root, path, value):
    current = root
    for index, key in enumerate(path[:-1]):
        next_key = path[index + 1]
        if isinstance(current, list):
            while len(current) <= key:
                current.append(None)
            if current[key] is None:
                current[key] = [] if isinstance(next_key, int) else {}
        else:
            current.setdefault(key, [] if isinstance(next_key, int) else {})
        current = current[key]
    key = path[-1]
    if isinstance(current, list):
        while len(current) <= key:
            current.append(None)
    current[key] = value


def reduced_item(item, fixture_token):
    if item_token(item):
        if "continuationItemViewModel" in item:
            return {"continuationItemViewModel": {"continuationCommand": {"innertubeCommand": {"continuationCommand": {"token": fixture_token}}}}}
        return {"continuationItemRenderer": {"continuationEndpoint": {"continuationCommand": {"token": fixture_token}}}}
    entry = parse_entry(item)
    if not entry:
        raise ValueError("Cannot sanitize unknown primary item")
    if entry["renderer"] == "lockupViewModel":
        return {"lockupViewModel": {"contentId": entry["video_id"], "contentType": "LOCKUP_CONTENT_TYPE_VIDEO", "metadata": {"lockupMetadataViewModel": {"title": {"content": entry["title"]}}}}}
    value = {"videoId": entry["video_id"], "title": {"simpleText": entry["title"]}}
    if entry["source_position"]:
        value["index"] = {"simpleText": entry["source_position"]}
    if entry["duration_text"]:
        value["lengthText"] = {"simpleText": entry["duration_text"]}
    if entry["visibility"] == "unavailable_placeholder":
        value["isPlayable"] = False
    return {entry["renderer"]: value}


def sanitize_fixtures():
    """Save minimal public metadata structures; replace every opaque list token."""
    directory = BASE / "fixtures"
    manifest = {"purpose": "Standalone parser replay. Public IDs/titles/counts and structural keys retained; opaque continuation tokens replaced with fixture strings. Full historical caches are not included.", "sources": {}, "channel_terminals": {}, "created_at": now()}
    for label in ["case03", "casanare", "audiencias"]:
        source = ORIGINAL / (SEEDS[label][1] + ".json")
        data = read(source)
        items, target, path, legacy = initial_list(data)
        entries, primary = parse_list(items, legacy)
        reduced = {}
        set_json_path(reduced, path, [reduced_item(x, "fixture-" + label + "-primary") for x in items])
        set_json_path(reduced, path[:-1] + ("targetId",), target)
        set_json_path(reduced, ("contents", "twoColumnBrowseResultsRenderer", "tabs", 0, "tabRenderer", "selected"), True)
        for other_path, item in walk(data):
            token = item_token(item)
            if token and token not in primary:
                set_json_path(reduced, other_path, reduced_item(item, "fixture-" + label + "-outer"))
        meta = playlist_metadata(data)
        reduced["metadata"] = {"playlistMetadataRenderer": {"title": meta["title"]}}
        reduced["header"] = {"pageHeaderRenderer": {"content": {"pageHeaderViewModel": {"metadata": {"contentMetadataViewModel": {"metadataRows": [{"metadataParts": [{"text": {"content": str(meta["declared_items"]) + " videos"}}]}]}}}}}}
        reduced["alerts"] = [{"alertRenderer": {"text": {"simpleText": notice}}} for notice in meta["notices"]]
        destination = directory / (label + "_first_page.json")
        write(destination, reduced)
        manifest["sources"][label] = {"original_path": str(source), "original_sha256": sha(source.read_bytes()), "source_url": "https://www.youtube.com/playlist?list=" + SEEDS[label][0], "sanitized_fixture": destination.name, "sanitized_sha256": sha(destination.read_bytes()), "primary_list_path": list(path), "primary_target_id": target, "declared_items": meta["declared_items"], "first_page_appearances": len(entries)}
    for label in ["deep_channel_videos", "deep_channel_streams"]:
        snapshot_path = WORK / (label + "_full_public_catalog.json")
        snapshot = read(snapshot_path)
        last = snapshot["pages"][-1]
        source = ORIGINAL / (label + "_" + str(last["page"]) + ".json")
        raw = read(source)
        shapes = [list(p) for p, obj in walk(raw) if any(k in obj for k in ["continuationItemViewModel", "continuationItemRenderer", "nextContinuationData", "reloadContinuationData"])]
        terminal = {"onResponseReceivedActions": [{"appendContinuationItemsAction": {"targetId": "fixture-channel-video-list", "continuationItems": [{"videoRenderer": {"videoId": x["id"], "title": {"simpleText": x["title"]}}} for x in last["items"]]}}]}
        if shapes or all_tokens(raw):
            raise ValueError("Observed channel terminal fixture unexpectedly has continuation")
        destination = directory / (label + "_terminal.json")
        write(destination, terminal)
        manifest["channel_terminals"][label] = {"original_path": str(source), "original_sha256": sha(source.read_bytes()), "sanitized_fixture": destination.name, "sanitized_sha256": sha(destination.read_bytes()), "terminal_page": last["page"], "terminal_items": len(last["items"]), "original_continuation_shapes": shapes, "original_continuation_remaining": snapshot.get("continuation_remaining"), "full_catalog_items": sum(len(p["items"]) for p in snapshot["pages"]), "full_catalog_sha256": sha(snapshot_path.read_bytes()), "limitation": "Reduced terminal structure proves this observed parser case; it does not recreate or independently re-enumerate the full channel catalog."}
    old_source = WORK / "extend_public_catalog.py"
    manifest["old_parser_source"] = str(old_source)
    manifest["old_parser_source_sha256"] = sha(old_source.read_bytes())
    write(directory / "fixture_manifest.json", manifest)
    print(json.dumps({"fixtures": 5, "path": str(directory), "opaque_tokens_replaced": True}), flush=True)


def reproduce():
    checks = []
    def check(name, observed, expected):
        checks.append({"check": name, "observed": observed, "expected": expected, "passed": observed == expected})
    fixtures = []
    reduced_manifest_path = BASE / "fixtures" / "fixture_manifest.json"
    reduced_manifest = read(reduced_manifest_path) if reduced_manifest_path.exists() else {}
    for label in ["case03", "casanare", "audiencias"]:
        historic_source = ORIGINAL / (SEEDS[label][1] + ".json")
        source = historic_source if historic_source.exists() else BASE / "fixtures" / (label + "_first_page.json")
        data = read(source)
        items, target, path, legacy = initial_list(data)
        entries, pending = parse_list(items, legacy)
        metadata = playlist_metadata(data)
        fixtures.append({"label": label, "source_path": str(source), "sha256": sha(source.read_bytes()), "replay_source": "original_saved_response" if source == historic_source else "sanitized_standalone_fixture", "historical_full_response_sha256": sha(historic_source.read_bytes()) if historic_source.exists() else reduced_manifest.get("sources", {}).get(label, {}).get("original_sha256"), "primary_list_path": list(path), "primary_target": target, "old_parser_tokens": len(old_tokens(data)), "new_primary_list_tokens": len(pending), "ignored_other_tokens": len({t for _, t in all_tokens(data)} - set(pending)), "appearances": len(entries), "unique_video_ids": len({e["video_id"] for e in entries}), **metadata})
    case, casanare, audiencias = fixtures
    check("Original parser misses actual Case03 continuation", case["old_parser_tokens"], 0)
    check("New parser selects one Case03 list token", case["new_primary_list_tokens"], 1)
    check("New parser excludes outer Case03 continuation", case["ignored_other_tokens"], 1)
    check("Case03 first page and declared count", [case["appearances"], case["declared_items"]], [100, 898])
    check("Casanare hidden entry preserved", [casanare["appearances"], casanare["hidden_unavailable_count"], casanare["declared_items"], casanare["new_primary_list_tokens"]], [19, 1, 20, 0])
    check("Audiencias repeated membership preserved", [audiencias["appearances"], audiencias["unique_video_ids"], audiencias["hidden_unavailable_count"], audiencias["declared_items"]], [42, 41, 2, 44])
    legacy = {"continuationItemRenderer": {"continuationEndpoint": {"continuationCommand": {"token": "fixture-old-token"}}}}
    check("Legacy Renderer shape supported", item_token(legacy), "fixture-old-token")
    fake_entry = {"video_id": "fixture"}
    check("Failed pending request cannot claim exhaustion", completion([fake_entry], ["pending"], {"error": "timeout"}, 3, 0)["pagination_exhausted"], False)
    check("Cycle cannot claim exhaustion", completion([fake_entry], ["pending"], None, 3, 0, cycle=True)["status"], "cycle_detected")
    check("Page limit remains explicit", completion([fake_entry], ["pending"], None, 3, 0, limit=True)["status"], "limit_reached")
    unavailable_entry = {"video_id": "fixture-unavailable", "title": "", "visibility": "unavailable_placeholder"}
    unavailable_result = completion([fake_entry, unavailable_entry], [], None, 2, 0)
    check("Returned placeholder is counted without implying playability", [unavailable_result["returned_memberships"], unavailable_result["unavailable_placeholder_memberships"], unavailable_result["status"]], [2, 1, "exhausted_with_unavailable"])
    blank = {"lockupViewModel": {"contentId": "o6q9K9GMm4E", "contentType": "LOCKUP_CONTENT_TYPE_VIDEO", "metadata": {"lockupMetadataViewModel": {"metadata": {"contentMetadataViewModel": {"metadataRows": [{"metadataParts": [{"text": {"content": ""}, "commandRuns": [{"onTap": {"innertubeCommand": {"browseEndpoint": {"browseId": "UC"}}}}]}]}]}}}}}}
    check("Invalid placeholder channel sentinel is not an owner ID", parse_entry(blank)["channel_id"], None)
    for label, surface in [("deep_channel_videos", "videos"), ("deep_channel_streams", "streams")]:
        terminal_fixture = BASE / "fixtures" / (label + "_terminal.json")
        if (WORK / (label + "_full_public_catalog.json")).exists():
            channel = reused_channel(label, surface)
            valid = channel["pagination_exhausted"]
        elif terminal_fixture.exists():
            terminal = read(terminal_fixture)
            valid = not all_tokens(terminal) and not any(any(k in obj for k in ["continuationItemViewModel", "continuationItemRenderer", "nextContinuationData", "reloadContinuationData"]) for _, obj in walk(terminal))
        else:
            valid = False
        check(label + " terminal snapshot has no missed continuation", valid, True)
    terminal_case = BASE / "caches" / "case03" / "page_008.json"
    if terminal_case.exists():
        check("Terminal-page hidden notice retained", playlist_metadata(read(terminal_case))["hidden_unavailable_notice"], True)
    old_source = WORK / "extend_public_catalog.py"
    report = {"command": "python crawl_public_catalog.py reproduce", "at": now(), "old_parser_source": str(old_source), "old_parser_source_sha256": sha(old_source.read_bytes()) if old_source.exists() else reduced_manifest.get("old_parser_source_sha256"), "fixtures": fixtures, "channel_terminal_fixture_provenance": reduced_manifest.get("channel_terminals", {}), "checks": checks, "all_passed": all(x["passed"] for x in checks)}
    write(BASE / "pagination_reproduction.json", report)
    print(json.dumps({"all_passed": report["all_passed"], "checks": len(checks), "fixtures": fixtures}, ensure_ascii=False), flush=True)
    if not report["all_passed"]:
        raise SystemExit(1)


def fetch_detail(vid):
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
        raise ValueError("Invalid video ID")
    url = "https://www.youtube.com/watch?v=" + vid
    original = WORK / "public_video_cache" / (vid + ".player.json")
    own = BASE / "caches" / "watch_metadata" / (vid + ".player.json")
    try:
        if own.exists():
            player = read(own)
            provenance = read(own.with_suffix(".meta.json"))
        elif original.exists():
            player = read(original)
            provenance = {"source_url": url, "cache_path": str(original), "sha256": sha(original.read_bytes()), "retrieval": "Existing public player metadata reused; original fetch time not stored"}
        else:
            payload, provenance = request(url)
            player = assigned(payload.decode(), "ytInitialPlayerResponse")
            write(own, player)
            write(own.with_suffix(".meta.json"), provenance)
        detail = player.get("videoDetails", {})
        mf = player.get("microformat", {}).get("playerMicroformatRenderer", {})
        if detail.get("videoId") and detail["videoId"] != vid:
            raise ValueError("Player video identity mismatch")
        if not detail and not player.get("playabilityStatus"):
            raise ValueError("Missing expected public player metadata")
        return vid, {"video_id": vid, "url": url, "title": detail.get("title") or text(mf.get("title")), "channel_id": detail.get("channelId") or mf.get("externalChannelId"), "channel_name": detail.get("author") or mf.get("ownerChannelName"), "description": detail.get("shortDescription") or text(mf.get("description")), "length_seconds": int(detail["lengthSeconds"]) if detail.get("lengthSeconds") else None, "upload_date": mf.get("uploadDate"), "publish_date": mf.get("publishDate"), "live": mf.get("liveBroadcastDetails"), "playability": player.get("playabilityStatus", {}).get("status"), "playability_reason": player.get("playabilityStatus", {}).get("reason"), "captions_available": bool(player.get("captions")), "caption_availability_basis": "Public player metadata only; no caption track acquired", "provenance": provenance}
    except Exception as exc:
        return vid, {"video_id": vid, "url": url, "error": {"type": type(exc).__name__, "message": str(exc)}, "checked_at": now()}


def metadata(ids, workers=2):
    path = BASE / "video_details.json"
    results = read(path) if path.exists() else {}
    pending = [v for v in dict.fromkeys(ids) if v not in results]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for vid, detail in pool.map(fetch_detail, pending):
            results[vid] = detail
            write(path, results)
            print(json.dumps({"video_id": vid, "title": detail.get("title"), "channel_id": detail.get("channel_id"), "error": detail.get("error")}, ensure_ascii=False), flush=True)
    export_all()
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("reproduce")
    sub.add_parser("sanitize-fixtures")
    sub.add_parser("web-seed")
    shorts = sub.add_parser("shorts")
    shorts.add_argument("--max-pages", type=int, default=50)
    probe = sub.add_parser("probe-next")
    probe.add_argument("--collection", choices=SEEDS, default="case03")
    crawl = sub.add_parser("crawl")
    crawl.add_argument("--collections", nargs="+", choices=SEEDS, default=list(CORE_SEED_KEYS))
    crawl.add_argument("--max-pages", type=int, default=30)
    crawl.add_argument("--show-unavailable", action="store_true", help="Follow only a saved observed public Show unavailable videos menu action")
    detail = sub.add_parser("metadata")
    detail.add_argument("--ids", nargs="*", default=[])
    detail.add_argument("--ids-file")
    detail.add_argument("--workers", type=int, choices=[1, 2], default=2)
    sub.add_parser("export")
    args = parser.parse_args()
    if args.command == "reproduce":
        reproduce()
    elif args.command == "sanitize-fixtures":
        sanitize_fixtures()
    elif args.command == "web-seed":
        web_seed()
    elif args.command == "shorts":
        result = crawl_shorts(args.max_pages)
        if not result.get("pagination_exhausted"):
            raise SystemExit(1)
    elif args.command == "probe-next":
        reproduction = read(BASE / "pagination_reproduction.json")
        if not reproduction.get("all_passed"):
            raise SystemExit("Local reproduction must pass first")
        result = crawl_one(args.collection, 2)
        first = {x["video_id"] for x in result["memberships"] if x["page_index"] == 0}
        beyond = [x for x in result["memberships"] if x["page_index"] == 1]
        proof = {"command": "python inventory_work/reverse_audit/crawl_public_catalog.py probe-next --collection " + args.collection, "at": now(), "collection": args.collection, "first_page_appearances": len([x for x in result["memberships"] if x["page_index"] == 0]), "next_page_appearances": len(beyond), "new_video_ids_beyond_first_page": len({x["video_id"] for x in beyond} - first), "examples": [{k: x[k] for k in ["position", "video_id", "title", "url"]} for x in beyond[:3]], "passed": bool(beyond) and bool({x["video_id"] for x in beyond} - first), "errors": result["errors"]}
        proof["passed"] = proof["passed"] and not bool(result["errors"])
        proof["page_request_provenance"] = [{"page_index": p["page_index"], "fetched_at": p["request"].get("fetched_at"), "cache_reused": p["request"].get("cache_reused"), "response_sha256": p["request"].get("sha256")} for p in result["pages"]]
        proof["proof_type"] = "live_continuation_request" if len(result["pages"])>1 and result["pages"][1]["request"].get("cache_reused") is False else "cached_response_replay"
        write(BASE / "live_pagination_proof.json", proof)
        export_all()
        print(json.dumps(proof, ensure_ascii=False), flush=True)
        if not proof["passed"]:
            raise SystemExit(1)
    elif args.command == "crawl":
        if not read(BASE / "live_pagination_proof.json").get("passed"):
            raise SystemExit("Live next-page proof must pass before full crawl")
        successful = []
        for label in args.collections:
            result = crawl_one(label, args.max_pages, args.show_unavailable)
            export_all()
            print(json.dumps({k: result.get(k) for k in ["collection_key", "status", "declared_items", "visible_memberships", "unique_video_ids", "hidden_unavailable_count", "count_reconciled", "pending_token_sha256", "errors"]}, ensure_ascii=False), flush=True)
            successful.append(result.get("pagination_exhausted") is True and result.get("count_reconciled") is not False)
            if STOP_NETWORK.is_set():
                break
        if len(successful)!=len(args.collections) or not all(successful):
            raise SystemExit(1)
    elif args.command == "metadata":
        ids = args.ids
        if args.ids_file:
            values = read(args.ids_file)
            if isinstance(values, dict):
                values = values.get("video_ids", values.get("candidates", values.get("records", [])))
            ids += [x if isinstance(x, str) else x.get("video_id", x.get("id")) for x in values]
        requested = [x for x in ids if x]
        results = metadata(requested, args.workers)
        if any(results.get(vid,{}).get("error") or vid not in results for vid in requested):
            raise SystemExit(1)
    else:
        print(json.dumps(export_all(), ensure_ascii=False))


if __name__ == "__main__":
    main()
