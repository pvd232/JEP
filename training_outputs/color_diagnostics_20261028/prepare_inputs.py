"""Verify saved checkpoints and screen fresh probe captions against C-STS."""

import argparse
from collections import defaultdict
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import re
import tarfile


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(8*1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def write_json(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def normalize(text):
    return ' '.join(re.findall(r'[a-z0-9]+',text.lower()))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--archive-root',type=Path,required=True)
    p.add_argument('--uid',type=int)
    p.add_argument('--gid',type=int)
    a=p.parse_args()
    a.root.mkdir(parents=True,exist_ok=True)
    weights=a.root/'weights';weights.mkdir(exist_ok=True)
    inputs=a.root/'frozen_source_data';inputs.mkdir(exist_ok=True)
    states=[dict(name='base',seed=None,arm=None,phase=None)]
    for seed in [7,8,9]:
        manifest=json.loads((a.root/f'checkpoints/seed_{seed}.json').read_text())
        archive=(a.archive_root/'checkpoints/selected_checkpoints.tar' if seed==7 else
                 a.archive_root/f'replications-20261027/checkpoints/seed_{seed}/selected_checkpoints.tar')
        with tarfile.open(archive) as tf:
            for name,info in manifest['models'].items():
                arm='P' if name.startswith('proposition_') else 'R'
                phase='A' if ('writing' in name or 'matched' in name) else 'B'
                target=weights/f'seed{seed}_{arm}_{phase}.pt'
                if not target.exists() or digest(target)!=info['sha256']:
                    h=hashlib.sha256()
                    source=tf.extractfile('models/'+name)
                    with target.with_suffix('.partial').open('wb') as f:
                        for part in iter(lambda:source.read(8*1024*1024),b''):
                            h.update(part);f.write(part)
                    if h.hexdigest()!=info['sha256']:
                        raise ValueError('Checkpoint checksum mismatch: '+name)
                    target.with_suffix('.partial').replace(target)
                target.chmod(0o600)
                states.append(dict(name=target.stem,seed=seed,arm=arm,phase=phase,
                                   path=str(target),sha256=info['sha256']))
            if seed==7:
                for src,dest in [('training','train'),('validation','validation'),('test','test')]:
                    (inputs/f'{dest}.json').write_bytes(tf.extractfile(f'data/{src}.json').read())
    write_json(a.root/'models.json',dict(models=states))
    expected=dict(train='9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4',
                  validation='e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff',
                  test='52a9c0d6b8d9f3fc81e698bae1e2564051cf7ec29e8dc1cb4d68167910bb968d')
    corpus=[]
    for split,sha in expected.items():
        path=inputs/f'{split}.json'
        if digest(path)!=sha:
            raise ValueError('Frozen C-STS digest differs: '+split)
        for row in json.loads(path.read_text()):
            for field in ['sentence1','sentence2']:
                corpus.append(row[field])
    corpus=sorted(set(corpus))
    normals=[normalize(x) for x in corpus]
    token_sets=[set(x.split()) for x in normals]
    inverted=defaultdict(set)
    stop=set('a an the is are was were on in at by to of for with and has been from as'.split())
    for i,tokens in enumerate(token_sets):
        for token in tokens-stop:
            inverted[token].add(i)
    probe=json.loads((a.root/'data/probe.json').read_text())
    captions=sorted(set(x['caption'] for x in probe['inputs']))
    records=[];hits=[]
    for caption in captions:
        norm=normalize(caption);tokens=set(norm.split())
        candidates=set().union(*(inverted[t] for t in tokens-stop))
        best_j=(-1,None);best_s=(-1,None)
        for j in candidates:
            inter=len(tokens&token_sets[j]);union=len(tokens|token_sets[j]);jac=inter/union
            if jac>best_j[0]:best_j=(jac,j)
            if jac>=0.25:
                sim=SequenceMatcher(None,norm,normals[j],autojunk=False).ratio()
                if sim>best_s[0]:best_s=(sim,j)
            else:sim=0
            if norm==normals[j] or jac>=0.8 or sim>=0.9:
                hits.append(dict(caption=caption,source_caption=corpus[j],jaccard=jac,character_similarity=sim))
        records.append(dict(caption=caption,max_jaccard=best_j[0],
                            nearest_jaccard_caption=corpus[best_j[1]] if best_j[1] is not None else None,
                            max_screened_character_similarity=best_s[0]))
    receipt=dict(status='passed' if not hits else 'review_required',probe_sha256=digest(a.root/'data/probe.json'),
                 model_states=len(states),adapter_models_verified=12,source_splits=expected,
                 source_unique_captions=len(corpus),probe_unique_captions=len(captions),
                 matching_rules=dict(normalized_exact=True,token_set_jaccard_threshold=0.8,
                                     character_similarity_threshold=0.9,character_screen_min_jaccard=0.25),
                 flagged_matches=hits,nearest_matches=records)
    write_json(a.root/'source_overlap_check.json',receipt)
    if a.uid is not None:
        for path in [a.root,*a.root.rglob('*')]:
            os.chown(path,a.uid,a.gid)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['nearest_matches','flagged_matches']},indent=2),flush=True)
    if hits:
        raise RuntimeError(f'{len(hits)} source-overlap matches require review before inference')


if __name__=='__main__':
    main()
