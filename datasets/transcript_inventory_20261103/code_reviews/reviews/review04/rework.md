# R04 repair receipt

The assigned repairs pass all **26 focused checks**. All 93 accepted canonical record IDs and 105 source-file assignments are unchanged. The actual draft generator was executed twice with every output write intercepted in memory.

## Stable source identity

The accepted registry maps 105 immutable Drive file IDs into 93 accepted source records. The generator now reuses that identity instead of assigning IDs from filename order. It rejects merges of two established IDs and splits of one established group, preserves identity when a preferred source changes or an alternate is added, and reserves absent accepted IDs. Genuinely new groups receive unused draft IDs; reviewed additions must be accepted into the registry before later snapshots.

The original rename counterexample changed 57 IDs. With the repair, the same title change changes zero IDs; the target stays VV-057. All 75 generated VV IDs and 87 VV source assignments match the accepted inventory.

## Recomputed version metrics

| Record | Field | Previous | Recomputed |
|---|---|---|---|
| VV-008 | shared_fivegrams | 34104 | 34102 |
| VV-010 | words | [34761, 38244] | [34761, 38245] |
| VV-010 | shared_fivegrams | 15051 | 15050 |
| VV-027 | words | [46111, 42353] | [46111, 42354] |

All twelve comparison rows now reproduce exactly. Rounded containment values and all consolidation decisions are unchanged. Normalization lowercases text, removes NFD combining characters, extracts Unicode word tokens, and counts distinct five-token tuples. The receipt records the normalizer source hash, retained extraction-cache hash, and per-file extracted/normalized hashes; no source text is reproduced.

## Handoff

The source copies in `rework_source` preserve the registry path relative to the repaired script. `rework.json` contains exact hashes, affected locations, verification results, and the ownership boundary. `rework_observations.json` contains individual checks and derived measurements.

The parent still owns synchronizing the historical `inventory_work/versiones_version_pairs.json` input and downstream evidence prose (VV-008: 34,104 to 34,102; VV-010: 15,051 to 15,050), rebuilding the workbook, and publication. No canonical inventory regeneration, source mutation, or network activity occurred in this repair. The retained text snapshot was used without re-extracting the original source files.

93 is the number of consolidated source records. It is not a certified count of unique hearing dates or recording segments.
