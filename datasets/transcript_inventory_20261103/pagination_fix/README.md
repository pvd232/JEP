# Public catalog pagination audit

This folder contains the corrected public-metadata crawler and a reproducible test of the missed Case 03 playlist continuation. It keeps video IDs separate from playlist appearances and leaves Casanare admission to the scope review. Collection is limited to public listing and player metadata.

## Replay the fix

Python 3.10 or later, standard library only:

```bash
python crawl_public_catalog.py reproduce
```

The replay uses the historical response caches when present and otherwise uses `fixtures/`. Reduced fixtures retain public IDs, titles, counts, and list structure; opaque continuation tokens are replaced with fixture strings. `fixtures/fixture_manifest.json` preserves the original full-response SHA-256 values. The isolated replay result demonstrates that the script and reduced fixtures alone are sufficient.

The old parser finds zero Case 03 continuation tokens after 100 of 898 declared positions. The corrected parser finds the primary-list token and ignores the outer-section token. The live proof records a successful next request returning 100 further IDs. Additional checks cover repeated playlist appearances, hidden counts, legacy renderers, invalid placeholder owner IDs, and failure states.

## Supported collection commands

Run these commands sequentially, after reviewing the relevant discovery scope:

```bash
python crawl_public_catalog.py probe-next --collection case03
python crawl_public_catalog.py crawl
python crawl_public_catalog.py crawl --collections case03 casanare audiencias --show-unavailable
python crawl_public_catalog.py crawl --collections region_antioquia region_costa_caribe region_norte_santander region_huila region_meta
python crawl_public_catalog.py crawl --collections region_meta --show-unavailable
python crawl_public_catalog.py web-seed
python crawl_public_catalog.py shorts
python crawl_public_catalog.py metadata --ids-file metadata_requested_ids.json
python crawl_public_catalog.py export
```

`crawl` defaults to the five declared playlists: broad Case 03, Subcaso Casanare, Audiencias & Diligencias, conditionality proceedings, and Camino de la Memoria–Casanare. The regional joins are supplemental metadata for geographic scope decisions. `web-seed` extracts only active Casanare-labelled cards from the known official Case 03 page. `--show-unavailable` follows a previously observed normal public menu action and preserves the default view separately.

`metadata` accepts `--ids ID ...` or a JSON list, or an object containing `video_ids`, `candidates`, or `records`. It permits one or two workers, default two. Playlist requests are sequential. Each request is attempted once; HTTP 429 stops the active batch. `--max-pages` caps playlist or Shorts pagination; reaching the cap preserves a pending state.

## Cache requirements and outputs

Fresh responses and checkpoints are written only beside this script, under `caches/`. Existing responses are reused after URL/token-fingerprint checks. Preserve an old snapshot when collecting a later one; use a separate task directory for a new snapshot.

Channel Videos and Live reuse the sibling `deep_channel_videos_full_public_catalog.json` and `deep_channel_streams_full_public_catalog.json`, plus their terminal responses under sibling `public_catalog_cache/`. Missing catalogs or terminal responses produce explicit manifest gaps. Shorts requires the observed Shorts tab in the original channel Videos first page or an existing crawler-owned Shorts first page. The fixture replay requires neither full channel catalog.

- `catalog.json`: one public node per video ID; Casanare scope requires separate evidence review.
- `memberships.json`: one row per source appearance, preserving playlist positions, overlaps, repeated IDs, and web-card context.
- `crawl_manifest.json`: source roles, selected and alternate views, counts, notices, unavailable placeholders, errors, and pending states.
- `video_details.json`: bounded public title/description/date/duration checks, with provenance and caption-availability metadata only.
- `pagination_reproduction.json`, `live_pagination_proof.json`, and `standalone_replay_result.json`: local replay and observed live-pagination evidence.

## Reading the counts

`returned_memberships` counts positions, including repeats and placeholders. `normal_title_memberships` counts positions with ordinary public titles; playability requires a separate check. `unique_video_ids` includes placeholder IDs. The legacy `visible_memberships` field is an alias for returned positions.

`exhausted_reconciled` means pagination ended and the declared count reconciles. `exhausted_with_unavailable` also preserves unavailable positions. `exhausted_count_unknown` means pagination ended and the platform omitted a declared total, as on Shorts. Count mismatch, error, cycle, pending, and page-limit statuses remain explicit. Historical availability, full hearing coverage, and final Casanare classification each require further evidence beyond exhausted pagination.

Publish only the reduced fixtures and metadata outputs. Keep raw response caches, player payloads, continuation tokens, signed media URLs, and source transcript text outside the publication package.
