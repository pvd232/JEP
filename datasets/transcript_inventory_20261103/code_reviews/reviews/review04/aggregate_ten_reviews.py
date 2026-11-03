"""Aggregate the ten frozen reviews and separate repair receipts.

This is a reporting follow-up, not another independent code review. It reads
existing evidence and writes only the two authorized aggregate summary files.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/scratch/8a7e64850a04')
WORK = ROOT / 'inventory_work'
TIE = WORK / 'tieout_review_20261103'
AUDIT = WORK / 'reverse_audit'
OUTPUT = ROOT / 'outputs/jep_transcripts_20261103'
BASE_COMMIT = '620cc5eb85860ff77a837058903321876de82b15'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(relative):
    path = TIE / relative
    return {'path': relative, 'sha256': sha(path)}


REVIEW_SPECS = [
    {
        'number': 1, 'scope': 'Primary-list pagination parsing and traversal',
        'findings': [
            ('R01-F01', 'P2', 'guard_only', 'Missing continuation target accepted as equal to another missing target', 'Require a usable primary target; malformed missing-target input now reports an explicit incomplete/error state.'),
            ('R01-F02', 'P2', 'guard_only', 'Malformed legacy continuation treated as terminal', 'Reject missing/unsupported legacy continuation tokens; valid legacy tokens remain supported.'),
        ],
        'repair_receipts': ['root_crawler_rework.json'],
        'verification': 'Both counterexamples reject; valid legacy control passes. Original review replayed all 22 retained playlist pages across ten playlists without membership changes.',
    },
    {
        'number': 2, 'scope': 'Crawl completeness and retained-cache accounting',
        'findings': [
            ('R02-01', 'P1', 'guard_only', 'Terminal page could certify a channel catalog missing a middle page', 'Require consecutive indexes, per-page raw-response agreement, primary-list closure, and positively recognized non-video branches.'),
            ('R02-02', 'P2', 'guard_only', 'Unstarted required playlists disappeared from the manifest', 'Keep every declared source in the manifest with an explicit missing/incomplete status when its state is absent.'),
        ],
        'repair_receipts': ['root_crawler_rework.json'],
        'verification': 'Missing-middle-page and disguised wrong-target branch controls reject; missing source states stay visible. All 120 historical channel responses replay with their original 2,663 Videos / 847 Live IDs; these are explicitly historical counts.',
    },
    {
        'number': 3, 'scope': 'Casanare scope decisions and register projection',
        'findings': [
            ('R03-F1', 'P1', 'actual_output', '74 broad exclusions used unsupported non-hearing rationales', 'Root replaced all 74 rationales with bounded official metadata/opening and territorial evidence; each remains excluded with its corrected reason.'),
            ('R03-F2', 'P2', 'guard_only', 'Broad and main scope decisions could conflict or omit an admitted broad candidate', 'Reject shared decision conflicts and broad inclusions absent from the main admitted map before output writes.'),
        ],
        'repair_receipts': ['tieout_data_decisions.json', 'root_assembler_rework.json'],
        'verification': 'The exact 74-ID review queue is represented by corrected evidence pointers. Both inconsistent scope fixtures reject; valid frozen inputs preserve all accepted rows and links.',
    },
    {
        'number': 4, 'scope': 'Transcript identity, duplicates, versions and many-to-many links',
        'findings': [
            ('R04-01', 'P2', 'guard_only', 'Mutable filenames could renumber established transcript IDs', 'Resolve accepted record identity through immutable Drive-file IDs; reject conflicting established groups; allocate unused draft IDs only for genuinely new groups.'),
            ('R04-02', 'P3', 'actual_output', 'Three comparison rows had small nonreproducible metric differences', 'Recompute four numeric fields across VV-008, VV-010 and VV-027 from retained extracted text; record normalizer and extraction hashes.'),
        ],
        'repair_receipts': ['reviews/review04/rework.json', 'reviews/review04/rework_observations.json'],
        'verification': '26 checks pass. The original title-only counterexample changed 57 IDs; after repair it changes zero. All 93 accepted IDs / 105 assignments stay fixed, all twelve metric rows reproduce, and shared/composite relations remain intact.',
    },
    {
        'number': 5, 'scope': 'Reverse mapping and no-source coverage decisions',
        'findings': [
            ('R05-F1', 'P2', 'guard_only', 'Duplicate reverse IDs or a missing shared-upload relation could silently lose an edge', 'Reject duplicate reverse IDs and require exact equality of all corrected forward/reverse transcript-video edges.'),
            ('R05-F2', 'P2', 'guard_only', 'An unlinked upload automatically became a no-transcript decision', 'Default new unlinked uploads to Coverage unconfirmed; absence requires an accepted session-comparison ledger bound to source identity and exact upload metadata.'),
        ],
        'repair_receipts': ['root_assembler_rework.json', 'reviews/review05/rework_R05_F2.json'],
        'verification': 'Missing/duplicate-edge controls reject. Seven absence-admission checks pass, preserving all 45 accepted baseline dispositions while rejecting unreviewed or same-principal/date ambiguity. Later root content refinements are separate from that frozen ledger replay.',
    },
    {
        'number': 6, 'scope': 'Timestamps, dates, durations and directional coverage',
        'findings': [
            ('R06-01', 'P2', 'guard_only', 'Invalid minute/second components normalized into plausible durations', 'Return unknown for invalid seconds and three-component minutes while preserving valid elapsed durations and unbounded hours.'),
        ],
        'repair_receipts': ['root_assembler_rework.json'],
        'verification': 'All three malformed-duration cases reject and six valid controls preserve expected seconds. The frozen review found no current timestamp/date/duration error and retained the distinction between six supplied-source omissions and two public-recording continuations.',
    },
    {
        'number': 7, 'scope': 'Forward-match verification, recording gaps and protected labels',
        'findings': [
            ('R07-01', 'P2', 'guard_only', 'High identity confidence and hardcoded IDs implied content verification', 'Use explicit verification evidence, clear rejected verification, allow later evidence for formerly metadata-only records, and keep playability separate.'),
        ],
        'repair_receipts': ['reviews/review07/rework_observer.json'],
        'verification': 'All three original merger counterexamples pass after repair; the fifteen recording-gap rows retain correct ownership and links. No incorrect frozen match or protected-label expansion was established.',
    },
    {
        'number': 8, 'scope': 'Workbook projection, hyperlinks, filters and acceptance',
        'findings': [
            ('R08-01', 'P2', 'guard_only', 'Third and later native links could be lost', 'Add native-link columns only when cardinality requires them; preserve every forward and reverse URL.'),
            ('R08-02', 'P2', 'guard_only', 'Acceptance could pass after deleting a native transcript-video hyperlink', 'Compare native hyperlink targets against every expected forward and reverse edge by record ID.'),
            ('R08-03', 'P2', 'actual_output', 'All six data tables lacked serialized filter definitions', 'Write an AutoFilter matching each table range and validate the actual serialized filters.'),
        ],
        'repair_receipts': ['reviews/review08/rework.json'],
        'verification': 'Focused cardinalities 0/1/2/3/15 pass; deleted forward/reverse links and filters reject. The repaired postprocessor changes only the six table parts. Final release workbook rebuild and acceptance remain a separate gate.',
    },
    {
        'number': 9, 'scope': 'Reproducibility, failure reporting and publication provenance',
        'findings': [
            ('R09-F01', 'P2', 'guard_only', 'Failed proof receipts could produce an all-passed report', 'Validate individual and aggregate outcomes and replay exit status before writing a success report.'),
            ('R09-F02', 'P2', 'guard_only', 'Failed requested full crawl returned process success', 'Return a nonzero process status for transport failure, page caps or rate-limited incomplete requested crawls while retaining their receipts.'),
            ('R09-F03', 'P3', 'guard_only', 'Cached proof execution time omitted response-retrieval provenance', 'Record proof execution separately from original fetch times, response hashes and cache-reuse state.'),
        ],
        'repair_receipts': ['reviews/review09/rework.json', 'root_crawler_rework.json'],
        'verification': 'All nine report controls pass without output changes on failed inputs. Crawler failure, cap, successful-completion and 429 controls pass; a zero-network cached proof now exposes original retrieval provenance. Actual frozen receipts and publication hashes were valid.',
    },
    {
        'number': 10, 'scope': 'Fresh channel traversal, cache binding and surface provenance',
        'findings': [
            ('R10-01', 'P2', 'guard_only', 'Parsed first-page cache was not bound to its retained HTML', 'Re-extract the initial data from checksum-verified HTML and reject a different parsed cache before consuming entries.'),
            ('R10-02', 'P2', 'guard_only', 'A selected Videos tab could satisfy a requested Live surface', 'Validate the selected official endpoint against the requested surface and preserve the observed endpoint.'),
        ],
        'repair_receipts': ['reviews/review10/rework.json', 'reviews/review10/rework_replay.json'],
        'verification': 'Both mismatches reject before recording membership; seven failure controls and full replay of all 118 fresh pages pass. The retained fresh source files remain unchanged: 2,663 Videos IDs and 846 Live IDs.',
    },
]


def reviewed_hashes(review):
    for key in ['reviewed_sha256', 'reviewed_hashes', 'hashes']:
        if key in review:
            return review[key]
    return {item['path']: item['sha256'] for item in review.get('reviewed_files', []) if isinstance(item, dict) and 'path' in item and 'sha256' in item}


def main():
    reviews = []
    all_findings = []
    receipt_paths = set()
    for spec in REVIEW_SPECS:
        number = spec['number']
        folder = f'reviews/review{number:02}'
        original = read(TIE / folder / 'review.json')
        # Read both immutable original formats; report hashes bind this aggregate.
        (TIE / folder / 'review.md').read_text()
        original_findings = {finding['id']: finding for finding in original['findings']}
        findings = []
        for identifier, priority, impact, problem, fix in spec['findings']:
            frozen = original_findings[identifier]
            assert frozen.get('priority', frozen.get('severity')) == priority
            findings.append({'id': identifier, 'priority': priority, 'impact_class': impact, 'problem': problem, 'fix': fix, 'status': 'repair_verified_at_review_boundary' if impact == 'guard_only' or identifier != 'R03-F1' else 'data_correction_recorded_with_evidence', 'release_artifact_gate_pending': number == 8})
        assert set(original_findings) == {item['id'] for item in findings}
        all_findings.extend(findings)
        evidence = []
        for relative in spec['repair_receipts']:
            read(TIE / relative)
            evidence.append(receipt(relative))
            receipt_paths.add(relative)
        reviews.append({'review_number': number, 'scope': spec['scope'], 'independent_review': True, 'original_verdict': original['verdict'], 'original_receipts': [receipt(folder + '/review.md'), receipt(folder + '/review.json')], 'reviewed_source_hashes': reviewed_hashes(original), 'findings': findings, 'repair_and_verification': spec['verification'], 'repair_receipts': evidence})
    assert len(reviews) == 10 and len(all_findings) == 20
    assert len({f['id'] for f in all_findings}) == 20

    crawler = read(TIE / 'root_crawler_rework.json')
    assembler = read(TIE / 'root_assembler_rework.json')
    assert crawler['passed'] and all(case['passed'] for case in crawler['cases'])
    assert assembler['all_passed'] and all(case['passed'] for case in assembler['assembly_cases'])
    assert read(TIE / 'reviews/review04/rework_observations.json')['all_checks_passed']
    assert all(case['passed'] for case in read(TIE / 'reviews/review05/rework_R05_F2.json')['checks'])
    assert all(case['invariant_passed'] for case in read(TIE / 'reviews/review07/rework_observer.json')['synthetic_observers'])
    assert read(TIE / 'reviews/review08/rework.json')['all_focused_observers_passed']
    assert read(TIE / 'reviews/review09/rework.json')['all_passed']
    assert read(TIE / 'reviews/review10/rework_replay.json')['passed']

    tieout = read(TIE / 'tieout_data_decisions.json')
    scope = read(AUDIT / 'scope_decisions_initial.json')['records']
    broad = read(AUDIT / 'broad_metadata_scope.json')['records']
    reverse = read(AUDIT / 'reverse_mapping_review.json')['videos']
    inventory = read(OUTPUT / 'inventory.json')
    accepted_inventory = read(TIE / 'base/inventory.json')
    manifest = read(OUTPUT / 'source_manifest.json')
    by_uid = {r['unique_id']: r['source_file_ids'] for r in inventory}
    assert by_uid == {r['unique_id']: r['source_file_ids'] for r in accepted_inventory}
    main_counts = dict(Counter(row['scope_decision'] for row in scope))
    broad_counts = dict(Counter(row['scope_decision'] for row in broad))
    assert main_counts == tieout['main_scope_counts']
    assert broad_counts == tieout['broad_scope_counts']
    risk_ids = {row['video_id'] for row in read(TIE / 'reviews/review03/scope_risk_candidates.json')['records']}
    corrected = [row for row in tieout['scope_changes'] if row['change'] == 'Corrected unsupported exclusion rationale']
    assert {row['video_id'] for row in corrected} == risk_ids and len(corrected) == 74
    assert all(row['evidence'] and row['public_url'] and row.get('supporting_url') for row in corrected)
    broad_by_id = {row['video_id']: row for row in broad}
    assert all(broad_by_id[row['video_id']]['scope_decision'] == row['decision'] and broad_by_id[row['video_id']]['evidence'] == row['evidence'] for row in corrected)
    assert read(WORK / 'versiones_version_pairs.json') == read(OUTPUT / 'version_comparisons.json')
    source_by_id = {row['unique_id']: row for row in inventory}
    assert '34,102' in source_by_id['VV-008']['duplicate_notes']
    assert '15,050' in source_by_id['VV-010']['duplicate_notes']
    unlinked = [row for row in reverse if not row['transcript_ids']]
    metadata_only = [row for row in unlinked if row['coverage_status'] == 'No supplied transcript located for public-metadata session']
    checked = [row for row in unlinked if row not in metadata_only]
    assert len(unlinked) == 45 and all('content' in row['coverage_status'] for row in checked)
    assert len(checked) == 4 + len(tieout['new_public_identity_checks'])
    current_main_uncertain = {row['video_id'] for row in scope if row['scope_decision'] == 'scope_unconfirmed'}
    current_broad_uncertain = {row['video_id'] for row in broad if row['scope_decision'] == 'scope_unconfirmed'}
    fresh = read(TIE / 'fresh_channel_comparison.json')
    assert sum(row['pages'] for row in fresh) == 118
    assert {row['surface']: row['fresh_ids'] for row in fresh} == {'videos': 2663, 'streams': 846}
    historical_only = next(row for row in tieout['scope_changes'] if row['video_id'] == 'Pg8DvszQMME')

    integration_path = TIE / 'fresh_channel_integration_receipt.json'
    integration = {'status': 'pending', 'receipt_expected': 'fresh_channel_integration_receipt.json'}
    if integration_path.exists():
        integration_payload = read(integration_path)
        assert integration_payload['all_passed'] and all(integration_payload['checks'].values())
        assert integration_payload['fresh_cache_integrity']['unchanged'] and integration_payload['all_frozen_hashes_match_manifest']
        integration = {'status': 'verified; check mode reproduced existing outputs', 'receipt': receipt('fresh_channel_integration_receipt.json'), 'recorded_result': integration_payload}
        receipt_paths.add('fresh_channel_integration_receipt.json')

    priority_counts = dict(sorted(Counter(row['priority'] for row in all_findings).items()))
    actual_ids = [row['id'] for row in all_findings if row['impact_class'] == 'actual_output']
    source_snapshot = {
        'consolidated_source_records': len(inventory), 'original_files': len(manifest['files']),
        'transcript_or_notes_files': sum(len(ids) for ids in by_uid.values()), 'consolidated_versions': sum(len(ids)-1 for ids in by_uid.values()),
        'source_folders': len(manifest['folders']), 'source_ids_and_assignments_preserved': True,
        'high_confidence_source_matches': sum(r['confidence'] == 'High' for r in inventory),
        'content_checked_source_matches': sum(bool(r.get('content_verified')) for r in inventory),
        'unmatched_source_records': sum(not r['youtube_url'].strip() for r in inventory),
        'included_uploads': len(reverse), 'uploads_linked_to_supplied_records': sum(bool(r['transcript_ids']) for r in reverse),
        'transcript_video_edges': sum(len(r['transcript_ids']) for r in reverse),
        'uploads_without_located_supplied_transcript': len(unlinked),
        'no_source_uploads_with_bounded_content_identity_check': len(checked),
        'no_source_uploads_with_metadata_basis': len(metadata_only),
        'additional_root_bounded_identity_checks': len(tieout['new_public_identity_checks']),
        'main_scope_rows': len(scope), 'main_scope_counts': main_counts,
        'broad_scope_rows': len(broad), 'broad_scope_counts': broad_counts,
        'corrected_exclusion_rationales': len(corrected),
    }
    snapshot_paths = [
        TIE / 'tieout_data_decisions.json', TIE / 'fresh_channel_comparison.json',
        AUDIT / 'scope_decisions_initial.json', AUDIT / 'broad_metadata_scope.json',
        AUDIT / 'reverse_mapping_review.json', AUDIT / 'root_content_checks.json',
        OUTPUT / 'inventory.json', OUTPUT / 'source_manifest.json', OUTPUT / 'version_comparisons.json',
        WORK / 'versiones_version_pairs.json',
    ]
    summary = {
        'title': 'Ten independent reviews: findings, repairs and remaining research gaps',
        'aggregation_kind': 'Follow-up aggregation; not an additional independent review',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'frozen_published_base_commit': BASE_COMMIT,
        'review_boundary_note': 'Reviews preserve their original verdicts and source hashes. Repairs and root integration are separate later evidence. Review 10 additionally covers the new fresh-channel candidate at its recorded hash.',
        'independent_review_count': 10, 'finding_count': 20, 'priority_counts': priority_counts,
        'current_output_findings': actual_ids, 'guard_only_findings': [row['id'] for row in all_findings if row['impact_class'] == 'guard_only'],
        'resolution_summary': 'All 20 finding remedies are recorded and verified at their stated code/data review boundary. Final release workbook rebuild and acceptance remain pending; this aggregate does not certify a rebuilt or published artifact.',
        'research_uncertainty_is_a_code_defect': False,
        'reviews': reviews,
        'current_data_snapshot': source_snapshot,
        'version_metric_corrections': {'fields': read(TIE / 'reviews/review04/rework.json')['findings']['R04-02']['changed_fields'], 'historical_generator_input_synchronized': True, 'downstream_numeric_evidence_synchronized': True, 'containment_and_consolidation_decisions_changed': False},
        'fresh_discovery': {'fresh_pages': 118, 'videos': {'pages': 89, 'ids': 2663}, 'live': {'pages': 29, 'ids': 846}, 'status': 'exhausted_count_unknown for both surfaces; no independent declared channel total was supplied', 'fresh_fetch_date_utc': '2026-11-03', 'historical_live_ids': 847, 'historical_only_upload': historical_only, 'history_note': 'Retain Pg8DvszQMME as historical discovery. Its bounded opening establishes a Huila hearing, excluded from Casanare; current listing absence is not deletion.', 'integration': integration},
        'root_after_fix_checks': {
            'crawler': {'receipt': receipt('root_crawler_rework.json'), 'source_sha256': crawler['reviewed_source_sha256'], 'focused_cases': len(crawler['cases']), 'all_passed': True, 'historical_pages_replayed': sum(row['pages'] for row in crawler['retained_channel_replays']), 'historical_counts': {row['label']: row['unique_video_ids'] for row in crawler['retained_channel_replays']}},
            'assembler': {'receipt': receipt('root_assembler_rework.json'), 'source_sha256': assembler['source_sha256'], 'assembly_cases': len(assembler['assembly_cases']), 'malformed_duration_cases': len(assembler['duration_cases']['malformed_actual']), 'valid_duration_cases': len(assembler['duration_cases']['valid_actual']), 'all_passed': True, 'baseline_edges': 84},
        },
        'remaining_research_gaps': [
            {'kind': 'Public recording not located for supplied source', 'count': 11, 'unit': 'consolidated source records', 'note': 'Unsuccessful searches do not establish nonpublication or reservation.'},
            {'kind': 'Located upload ends before supplied source continuation', 'count': 2, 'record_ids': ['VV-015', 'VV-038']},
            {'kind': 'Source-to-video match remains metadata-only', 'count': 2, 'note': 'Usable public captions were unavailable; content/coverage and offsets remain unverified.'},
            {'kind': 'Known omitted supplied transcript portions', 'count': 6, 'note': 'Separate direction from missing public continuations; these counts overlap and must not be added.'},
            {'kind': 'No supplied transcript located for admitted upload', 'count': 45, 'bounded_identity_content_checked': len(checked), 'metadata_based': len(metadata_only), 'note': 'Upload counts do not establish additional unique hearings; bounded identity checks do not certify full-audio equivalence.'},
            {'kind': 'Scope unconfirmed', 'main_count': len(current_main_uncertain), 'broad_count': len(current_broad_uncertain), 'overlap_count': len(current_main_uncertain & current_broad_uncertain), 'distinct_ids': len(current_main_uncertain | current_broad_uncertain), 'main_ids': sorted(current_main_uncertain), 'broad_ids': sorted(current_broad_uncertain), 'note': 'These candidates remain outside the admitted corpus. Four unavailable IDs across the two registers have no usable recording identity, including the Casanare playlist placeholder.'},
        ],
        'release_gate': {'final_workbook_rebuilt_and_accepted': False, 'status': 'pending parent-owned final build, native-link/filter postprocessing and acceptance receipt', 'publication_claimed_by_this_aggregate': False},
        'interpretation_limits': [
            '93 means consolidated source records; VV-071 contains two dated sessions, and a shared upload retains two source segments. It is not a certified unique-hearing count.',
            '17 guard/reuse/provenance findings demonstrated failure paths without establishing an incorrect frozen matching or consolidation count.',
            'The source-text and caption checks establish identity and selected boundaries, not a word-for-word audit of every proceeding. Caption date conflicts remain explicit.',
            'The workbook review verified projection of the 93 English summaries; it did not independently fact-check every summary claim.',
            'Ten independently scoped reviews are preserved; repair observers, this aggregation and final integration are follow-up work, not additional reviews.',
        ],
        'data_evidence_sha256': {str(path.relative_to(ROOT)): sha(path) for path in snapshot_paths},
        'repair_receipt_sha256': {relative: sha(TIE / relative) for relative in sorted(receipt_paths)},
    }
    (TIE / 'ten_review_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')

    lines = [
        '# Ten independent reviews — findings, repairs and research gaps', '',
        f'**Exactly ten independent reviews identified 20 findings: {priority_counts["P1"]} P1, {priority_counts["P2"]} P2 and {priority_counts["P3"]} P3.** All remedies have code/data evidence at their stated review boundary. Final workbook rebuild and acceptance remain a separate, pending release gate; this summary does not certify a rebuilt or published artifact.', '',
        f'Three findings affected existing outputs: unsupported exclusion rationales for 74 candidates, small comparison-metric discrepancies in three rows, and missing filter definitions in all six Excel data tables. The other 17 concern guards, regeneration or provenance; none established a wrong existing transcript consolidation or a lost current match. Original review verdicts remain frozen against commit `{BASE_COMMIT}`; later fixes have separate receipts. This aggregation is not an eleventh review.', '',
        '## Exactly ten review scopes', '',
        '| Review and scope | Finding IDs / priority / impact | Fix and verification |',
        '|---|---|---|',
    ]
    row_summaries = {
        1: ('R01-F01, R01-F02 · P2 · guards', 'Missing targets and malformed legacy tokens now reject. Valid controls and retained playlist traversal remain supported.'),
        2: ('R02-01 · P1; R02-02 · P2 · guards', 'Check every retained page and primary continuation; keep missing declared sources visible. All 120 historical responses replay; missing-page and disguised-branch controls reject.'),
        3: ('R03-F1 · P1 · actual rationale defect; R03-F2 · P2 · guard', 'All 74 challenged rationales now have specific public/territorial pointers and remain excluded. Contradictory main/broad decisions or omitted broad admissions reject.'),
        4: ('R04-01 · P2 · guard; R04-02 · P3 · actual metric drift', 'Stable Drive-ID registry: title rename changes zero IDs, versus 57 before. All 93 IDs / 105 assignments preserved. Shared spans become 34,102 (VV-008) and 15,050 (VV-010); VV-010/VV-027 variant word counts each rise by one. All twelve pairs reproduce; 26 checks pass.'),
        5: ('R05-F1, R05-F2 · P2 · guards', 'Exact bilateral edge validation protects the shared upload. New unlinked uploads stay coverage-unconfirmed until admitted by a source-bound review ledger. Seven admission checks preserve all 45 accepted baseline dispositions.'),
        6: ('R06-01 · P2 · guard', 'Reject malformed duration components; three invalid and six valid controls pass. Existing dates, offsets and distinct gap directions were supported.'),
        7: ('R07-01 · P2 · guard', 'Explicit evidence governs content verification; confidence does not create it. All three merger counterexamples pass; fifteen recording-gap rows retain correct ownership.'),
        8: ('R08-01, R08-02 · P2 · guards; R08-03 · P2 · actual filter defect', 'Dynamic native links pass cardinalities 0/1/2/3/15. Missing forward/reverse links and filters reject. Postprocessor writes all six filters; final workbook acceptance is pending.'),
        9: ('R09-F01, R09-F02 · P2; R09-F03 · P3 · guards/provenance', 'Failed proof receipts cannot produce success reports; failed/incomplete crawls exit nonzero. Cached proofs carry original fetch times/hashes. Nine report controls and crawler controls pass.'),
        10: ('R10-01, R10-02 · P2 · guards', 'Bind parsed first-page cache to its HTML and verify the requested channel surface. Both mismatches reject; seven controls and full 118-page fresh replay pass.'),
    }
    for review in reviews:
        n = review['review_number']
        issues, resolution = row_summaries[n]
        proof = review['repair_receipts'][0]['path']
        extra = '' if len(review['repair_receipts']) == 1 else ' / [additional receipt](' + review['repair_receipts'][-1]['path'] + ')'
        lines.append(f'| [R{n:02} — {review["scope"]}](reviews/review{n:02}/review.md) | {issues} | {resolution} [Evidence]({proof}){extra}. |')
    lines += [
        '', '## Reconciled research counts', '',
        '| Unit | Current count |', '|---|---:|',
        '| Original source files / transcript-or-notes files | 116 / 105 |',
        '| Consolidated source records / retained alternate versions | 93 / 12 |',
        '| High-confidence source matches / content-checked source matches | 82 / 80 |',
        '| Admitted uploads / uploads linked to supplied sources / source–video edges | 128 / 83 / 84 |',
        f'| Uploads without a located supplied transcript | 45: **{len(checked)}** bounded content-identity checks; **{len(metadata_only)}** metadata-based |',
        '| Main scope register | 208: 128 included, 76 excluded, 4 unconfirmed |',
        '| Broad Case 03 register | 898: 96 included, 789 excluded, 13 unconfirmed |',
        '',
        f'Root added **{len(tieout["new_public_identity_checks"])} bounded public identity checks**; the underlying 45-upload set did not change. These checks establish participants, dated openings or recording format at named anchors. They do not certify 45 additional unique hearings or complete audio equivalence. The 93 source records remain unchanged; VV-071 is a composite two-date document, and VV-029/VV-030 share one upload with distinct segments. [Data decision receipt](tieout_data_decisions.json).',
        '', '## Fresh discovery and repair checks', '',
        '**Fresh channel discovery is 118 pages: 89 Videos pages with 2,663 IDs, and 29 Live pages with 846 IDs**, fetched on 3 November 2026. Both traversals reached terminal pages; YouTube supplied no independent declared channel total. The older 847 Live IDs are historical evidence, not the fresh count. The single absent current appearance, `Pg8DvszQMME`, remains playable; its bounded opening identifies Huila, so it remains historical discovery and is excluded from the Casanare corpus. [Fresh comparison](fresh_channel_comparison.json) / [118-page replay](reviews/review10/rework.json).', '',
        f'Root’s [crawler repair verification](root_crawler_rework.json) passes **{len(crawler["cases"])} focused cases** and the separate **120-page historical replay**. Its [assembler verification](root_assembler_rework.json) passes **{len(assembler["assembly_cases"])} assembly cases plus nine duration cases**, preserving all 84 accepted edges while rejecting inconsistent inputs before writes. These are follow-up checks, not extra independent reviews.', '',
        'Fresh discovery integration: ' + ('[the completed check-mode receipt](fresh_channel_integration_receipt.json) passes all preservation and repeatability checks. It retains **5,203 appearances = 5,202 current + one historical**, and **3,606 discovery IDs = 3,605 current + one historical-only**. All ten playlist snapshots and other non-channel memberships remain unchanged; discovery counts do not enlarge the Casanare corpus.' if integration_path.exists() else 'the final integration receipt is pending; the fresh traversal itself has passed its independent replay.') + '', '',
        '## Remaining research gaps', '',
        '- **11 supplied source records** still have no located public recording; **two** require missing recording continuations; **two** source matches remain metadata-only. These are the fifteen source-side gap rows.',
        '- **Six known supplied-transcript omissions** describe the opposite coverage direction. They overlap with other gap categories and must not be added to produce a total missing-hearing count.',
        f'- **45 admitted uploads** have no supplied transcript located, with {len(checked)} bounded content-identity checks and {len(metadata_only)} metadata-based decisions. Full-audio coverage and upload-to-unique-hearing equivalence remain uncertified.',
        '- **Four main candidates and thirteen broad-register entries** remain scope-unconfirmed (one ID overlaps). They stay outside the admitted corpus. Four unavailable IDs across those registers lack usable recording identity, including the Casanare playlist placeholder.',
        '',
        'These are explicit evidence/access uncertainties, not unresolved code defects. Caption date conflicts and approximate timestamp limits remain visible. The workbook review verified projection of the 93 English summaries; it did not independently fact-check every summary claim. Final workbook rebuild, native-link/filter postprocessing, acceptance and publication remain parent-owned release work.',
        '',
        'Full frozen review/source hashes, repair-receipt hashes, current data hashes, exact finding IDs and stage limits are recorded in [ten_review_summary.json](ten_review_summary.json). No source document or canonical research data was modified by this aggregation.',
    ]
    (TIE / 'ten_review_summary.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'independent_reviews': len(reviews), 'findings': len(all_findings), 'priorities': priority_counts, 'actual_output_findings': actual_ids, 'new_identity_checks': len(tieout['new_public_identity_checks']), 'no_source_content_checked': len(checked), 'no_source_metadata_based': len(metadata_only), 'fresh_integration_receipt_present': integration_path.exists(), 'summary_files': {name: sha(TIE / name) for name in ['ten_review_summary.json', 'ten_review_summary.md']}}, indent=2))


if __name__ == '__main__':
    main()
