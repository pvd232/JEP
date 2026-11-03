# Casanare video coverage method

**Scope:** JEP Case 03, Subcase Casanare, and the directly connected Casanare proceedings already represented in the supplied Datos collection. Other JEP cases, territorial subcases and unrelated proceedings involving the same people are outside the corpus.

**Status, 3 November 2026:** The pagination correction and reverse video-to-transcript pass have been implemented. The [execution report](reverse_audit_report.md) gives the reproduced failure, live proof, source counts and remaining scope/access limitations. The workbook still inventories 93 consolidated source-transcript records; that count is not the total number of Casanare hearings or public videos.

The [crawl readiness review](crawl_readiness_review.json) found that the retained Videos and Live indexes reach terminal pages, but the older broad Case 03 playlist parser missed a video-list continuation after item 100 despite a header count of 898. The defect was reproduced against the saved response and corrected for both continuation structures. A live request returned 100 new IDs at positions 101–200. Full traversal then accounted for all 898 positions: 895 normal-title entries and three unavailable placeholders. The public “Show unavailable videos” action exposed their IDs without exposing titles or content. The Casanare playlist similarly reconciles 19 normal-title entries and one unavailable placeholder. See the [live proof](live_pagination_proof.json), [source manifest](crawl_manifest.json) and [standalone replay](pagination_fix/README.md). No additional case is admitted by inspecting a broad playlist's metadata.

This was a parser defect in the public YouTube browse response, not a change to the documented Data API’s `nextPageToken` request format. The repaired public-interface request sends the observed primary-list continuation in the normal `{context, continuation}` body. An outer-section continuation is excluded from the video list.

## 1. Fix the inclusion rules

Include hearing recordings and supplied hearing segments whose Casanare connection is established by official title/description, a linked judicial proceeding, or a dated opening checked against official case evidence. This includes voluntary statements, sworn declarations, recognition and late-recognition hearings, victim observations, and directly connected conditionality, truth-contribution and protective-measures proceedings already within the collection's scope.

An appearance by a known participant, a mention of Casanare, a Case 03 label without territorial identification, or presence in a broad playlist is insufficient by itself. Mark ambiguous items **scope unconfirmed** until resolved. For a mixed proceeding, include only an identifiable Casanare segment, with its boundaries; otherwise retain it for scope review.

News, interviews, promotional material, press conferences and highlight clips can be recorded as contextual or derivative listings, with an exclusion reason. They do not become additional hearing records. Keep possible reuploads or excerpts linked to the relevant hearing until their relationship is verified.

## 2. Enumerate defined official sources

Start from the [official Case 03 page](https://www.jep.gov.co/macrocasos/caso03.html), the [Subcaso Casanare playlist](https://www.youtube.com/playlist?list=PLbtegW3d3L4JR1Y_bfCDS_C8sdKE6195K), relevant official hearing playlists, and the source collection's existing video links. Extract links and embedded video IDs within the relevant page sections; do not follow unrelated site navigation or recommended-video panels.

Use the official JEP channel's upload catalog as a metadata cross-check for Casanare recordings omitted from a topical playlist. Reuse existing channel metadata and retrieve missing metadata in batches. Channel-wide discovery does not authorize adding other cases to the corpus. An alternate publisher is followed only when evidence connects a specific recording to an in-scope Casanare hearing.

Prefer the documented YouTube Data API when access is available: resolve the channel's `contentDetails.relatedPlaylists.uploads`, enumerate the channel's playlists, and retrieve each relevant playlist's items through every `nextPageToken`. If only the public interface is available, record and traverse its actual list pagination with the same completion rules. Search results supplement discovery; search rank or an arbitrary page limit never establishes completeness.

Sources: [channel uploads property](https://developers.google.com/youtube/data/reference/rest/v3/channels), [playlist enumeration](https://developers.google.com/youtube/data/reference/rest/v3/playlists/list), [playlist-item pagination](https://developers.google.com/youtube/data/reference/rest/v3/playlistItems/list).

## 3. Preserve the discovery structure

Record source page/playlist, parent-child relationship, playlist position, video ID, publisher/channel ID, title, description, duration, publication time, stated hearing date, retrieval time and availability. Hearing date and upload date remain separate fields.

Use the exact video ID to deduplicate appearances of the same upload while retaining every source membership. A title is not a unique identifier. Different IDs remain distinct uploads until content checks establish whether they are reuploads, excerpts or complementary parts. One upload may contain several proceedings; one hearing may span several uploads.

For pagination, retain pending, successful and failed requests separately. A failed request, repeated token, parsing failure or page limit produces an incomplete-crawl flag. Removing a token from the queue before a failed request must not make that branch appear complete. Preserve known unavailable item IDs or placeholders; do not silently drop them. Exclude recommendations from list extraction.

The retained public pages contain both `continuationItemRenderer` and `continuationItemViewModel` structures. The latter may contain a nested `innertubeCommand`. A continuation's structural parent determines whether it extends the actual video list or an outer section; collecting every token indiscriminately would also be incorrect. Reconcile visible item counts and explicit unavailable-item notices with displayed playlist totals, and retain unexplained discrepancies as gaps. When an unavailable video's ID is not exposed, record the hidden-item count without inventing an ID.

## 4. Apply the case boundary before substantive processing

Assign each discovered candidate **included**, **excluded with reason**, or **scope unconfirmed**, with a short evidence pointer. Confirm publisher identity from the channel ID, not a display-name string. Preserve original-language metadata where available; localized titles are supplementary.

Read captions or brief recording passages only as needed to resolve case membership, recording identity, duplicate relationships and coverage. Broad channel metadata remains a discovery index; substantive processing remains confined to the approved Casanare scope. Do not search using expanded protected identities.

## 5. Compare in both directions

Maintain links among source transcript IDs, hearing/session IDs and video IDs, with source and video ranges where available.

- **Transcript to video:** identify each supplied transcript's recording(s), including missing continuations and unlocated recordings.
- **Video to transcript:** identify each admitted video's corresponding supplied transcript(s), untranscribed sessions and portions lacking source coverage.
- **Session sequence:** reconcile announced dates, morning/afternoon sessions, numbered parts and continuations against the admitted inventory.

Check dated openings, participant roles and concise content anchors. Do not infer coverage from matching names or dates alone. Preserve the existing 93 source-record IDs; newly discovered public videos do not become new source transcripts until a transcript is obtained or created. A supplied document combining several dates retains its document ID with separate session links.

YouTube caption availability is a separate attribute. Public automatic captions do not count as an existing supplied transcript or an audio-validated benchmark reference. Verified caption cues remain approximate unless the relevant audio has been checked.

## 6. Report separate quantities and limits

Report distinct source files, consolidated transcript records, admitted video IDs, distinct hearing sessions, verified transcript-video links, videos/segments without a supplied transcript, supplied transcripts without a located video, and unresolved scope/access/content checks. These quantities are not interchangeable and some gap categories overlap.

Extend the existing workbook with a **Videos** tab and concise coverage status while preserving the original transcript inventory and source links. Persist the video metadata, link table, inclusion/exclusion decisions and crawl-completion evidence to JEP GitHub. Keep source transcripts and recordings in their existing locations and retain their access settings. No external messages are sent as part of this audit.

## 7. Completion standard

The public-source pass is complete only when every declared source branch has exhausted pagination without unresolved request or parsing failures, every discovered candidate has a recorded scope decision, and every admitted recording has a transcript-coverage status. Unresolved relationships and known inaccessible items remain counted and visible; they prevent a claim of fully verified mapping.

The result must name its sources and review date. It can establish coverage of public material discoverable from those sources; it cannot prove the absence of unlisted, private, deleted or never-published recordings. JEP follow-up should identify those residual recording/access questions. Public videos lacking our transcripts are a separate corpus-expansion task that can proceed without waiting for JEP to locate the videos.
