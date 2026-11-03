"""Read-only source identity and consolidation observer for review 04.

Reports IDs, hashes, counts and overlap measurements only; never source text.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path('/workspace/scratch/8a7e64850a04')
WORK = ROOT / 'inventory_work'
BASE = WORK / 'tieout_review_20261103/base'
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def tokens(text):
    lowered = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if not unicodedata.combining(c))
    return re.findall(r'\w+', lowered)


def grams(words, span):
    return {tuple(words[i:i + span]) for i in range(len(words) - span + 1)}


def main():
    inv = read(BASE / 'inventory.json')
    manifest = read(BASE / 'source_manifest.json')
    pairs = read(BASE / 'version_comparisons.json')
    video = read(BASE / 'video_inventory.json')
    rows = {r['unique_id']: r for r in inv}
    files = {r['file_id']: r for r in manifest['files']}
    assigned = [fid for r in inv for fid in r['source_file_ids']]
    by_source = {fid: r['unique_id'] for r in inv for fid in r['source_file_ids']}
    checks = []

    def check(name, actual, expected):
        checks.append({'check': name, 'passed': actual == expected, 'actual': actual, 'expected': expected})

    check('source manifest file IDs unique', len(files), len(manifest['files']))
    check('116 files present', len(files), 116)
    check('10 folders present', len(manifest['folders']), 10)
    check('canonical record IDs unique', len(rows), len(inv))
    check('93 consolidated source records', len(inv), 93)
    check('105 source assignments', len(assigned), 105)
    check('each source file assigned once', len(set(assigned)), len(assigned))
    check('all assigned sources exist', sorted(set(assigned) - set(files)), [])
    check('every transcript/notes manifest file assigned', sorted(f['file_id'] for f in files.values() if f['classification'] == 'Transcript / notes'), sorted(assigned))
    check('manifest inverse assignment agrees', all(files[fid]['unique_id'] == uid for fid, uid in by_source.items()), True)
    check('all canonical and version links retained', all(r['all_file_links'] == [files[fid]['url'] for fid in r['source_file_ids']] for r in inv), True)
    check('canonical direct link is first source', all(r['direct_file_link'] == files[r['source_file_ids'][0]]['url'] for r in inv), True)
    check('extra assigned files equal versions', len(assigned) - len(inv), len(pairs))
    check('12 distinct version records', len({p['variant_id'] for p in pairs}), 12)
    check('no canonical also treated as variant', sorted({p['canonical_id'] for p in pairs} & {p['variant_id'] for p in pairs}), [])
    check('paired files share exactly one record', all(by_source.get(p['canonical_id']) == by_source.get(p['variant_id']) for p in pairs), True)
    check('all nonprimary assignments appear in comparison register', sorted(fid for r in inv for fid in r['source_file_ids'][1:]), sorted(p['variant_id'] for p in pairs))
    check('eleven alternate transcriptions and one notes version', dict(collections.Counter(p['relation'] for p in pairs)), {'alternate transcription': 11, 'condensed notes / full transcript': 1})
    url_pattern = re.compile(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})')
    forward = [(r['unique_id'], vid) for r in inv for vid in url_pattern.findall(r['youtube_url'])]
    reverse = [(uid, r['video_id']) for r in video if r['scope_label'] == 'Included' for uid in r['transcript_ids']]
    check('forward links have no repeated edges', len(forward), len(set(forward)))
    check('forward/reverse edge sets agree', sorted(forward), sorted(reverse))
    check('84 transcript-video edges', len(forward), 84)
    check('83 linked uploads', len({vid for uid, vid in forward}), 83)
    check('shared upload retains two distinct source segments', sorted(uid for uid, vid in forward if vid == 'eM8ZrqhZbgQ'), ['VV-029', 'VV-030'])
    check('VV-057 retains both alternate uploads', sorted(vid for uid, vid in forward if uid == 'VV-057'), ['FoAy5Qfphcs', 'ztGtBj4AbQA'])
    check('VV-071 preserves both hearing dates', rows['VV-071']['date'], '2021-08-12; 2021-08-20')

    source_data = read(WORK / 'versiones_text_private.json')
    texts = {fid: d['text'] for fid, d in source_data.items()}
    for d in read(WORK / 'root_contents.json'):
        fid = d['metadata']['id']
        if fid in assigned:
            texts[fid] = d['content']
    for n, uid in enumerate(['CAS03-20230918-AM', 'CAS03-20230918-PM', 'CAS03-20230919-AM', 'CAS03-20230920-AM'], 1):
        raw = (WORK / f'casanare_{n}.csv').read_text()
        records = list(csv.DictReader(io.StringIO(raw)))
        dialogue = next(k for k in records[0] if k.strip() == 'Diálogo')
        texts[rows[uid]['source_file_ids'][0]] = '\n'.join(x[dialogue] for x in records)
    check('readable text for all 105 assigned source files', sorted(set(assigned) - set(texts)), [])
    wordmap = {fid: tokens(texts[fid]) for fid in assigned}
    hashes = {fid: hashlib.sha256(' '.join(words).encode()).hexdigest() for fid, words in wordmap.items()}
    exact = collections.defaultdict(list)
    for fid, h in hashes.items():
        exact[h].append(fid)
    exact_duplicates = [ids for ids in exact.values() if len(ids) > 1]
    check('no undisclosed normalized exact duplicates', exact_duplicates, [])
    fivegrams = {fid: grams(words, 5) for fid, words in wordmap.items()}
    pair_results = []
    for p in pairs:
        a, b = p['canonical_id'], p['variant_id']
        ga, gb = fivegrams[a], fivegrams[b]
        shared = len(ga & gb)
        containment = round(shared / min(len(ga), len(gb)), 3)
        result = {'record_id': by_source[a], 'canonical_id': a, 'variant_id': b, 'words': [len(wordmap[a]), len(wordmap[b])], 'shared_fivegrams': shared, 'containment': containment, 'relation': p['relation']}
        pair_results.append(result)
        check('pair metrics ' + by_source[a], {k: result[k] for k in ['words', 'shared_fivegrams', 'containment']}, {k: p[k] for k in ['words', 'shared_fivegrams', 'containment']})
    candidates = []
    for a, b in itertools.combinations(assigned, 2):
        if by_source[a] == by_source[b]:
            continue
        shared = len(fivegrams[a] & fivegrams[b])
        rate = shared / max(1, min(len(fivegrams[a]), len(fivegrams[b])))
        if shared >= 200 and rate >= .12:
            candidates.append({'source_ids': [a, b], 'record_ids': [by_source[a], by_source[b]], 'titles': [files[a]['title'], files[b]['title']], 'shared_fivegrams': shared, 'containment': round(rate, 4)})
    candidates.sort(key=lambda r: -r['containment'])
    result = {'frozen_commit': '620cc5eb85860ff77a837058903321876de82b15', 'all_checks_passed': all(x['passed'] for x in checks), 'identity_checks_passed': all(x['passed'] for x in checks if not x['check'].startswith('pair metrics')), 'checks': checks, 'pair_recomputations': pair_results, 'cross_record_overlap_candidates': candidates, 'normalized_text_hashes': hashes, 'source_hashes_private_cache': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [WORK/'versiones_text_private.json', WORK/'root_contents.json']}}
    (OUT / 'observations.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'checks': len(checks), 'failed': [x['check'] for x in checks if not x['passed']], 'cross_record_candidates': candidates}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
