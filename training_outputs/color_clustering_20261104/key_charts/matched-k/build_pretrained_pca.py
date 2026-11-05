#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""Plot saved off-the-shelf Qwen vectors, labels and K=12 cluster assignments."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PALETTE = {'blond': '#c6a74a', 'gold': '#cda400', 'gray': '#888888',
           'unknown': '#bcbcbc', 'maroon': '#800000'}
ARM, COHORT, K = 'pretrained_conditioned', 'validation_single', 12


def main():
    """Reuse the archived PCA coordinates and highest-silhouette fit at K=12."""
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.archive) as z:
        metrics = json.loads(z.read('metrics.json'))
        cohort = metrics['cohorts'][COHORT]
        result = cohort['arms'][ARM]
        run = max((r for r in result['runs'] if r['k'] == K),
                  key=lambda r: (r['silhouette'], -r['seed']))
        saved = np.load(io.BytesIO(z.read(f'tables/{COHORT}-{ARM}-all-assignments.npz')))
        ids = saved['point_ids'].tolist()
        assert ids == cohort['point_ids']
        assigned = saved[f'K{K}_seed{run["seed"]}']
        labels = {r['point_id']: r for r in json.loads(z.read('color-labels.json'))}
        points = {r['point_id']: r for r in json.loads(z.read('points.json'))}
        coords = {}
        for row in csv.DictReader(io.StringIO(z.read('tables/representative-point-diagnostics.csv').decode())):
            if row['cohort'] == COHORT and row['arm'] == ARM:
                xy = (float(row['pc1']), float(row['pc2']))
                assert row['point_id'] not in coords or coords[row['point_id']] == xy
                coords[row['point_id']] = xy
        vectors = np.load(io.BytesIO(z.read(f'embeddings/{ARM}.npz')))
        lookup = {p: i for i, p in enumerate(vectors['point_ids'].tolist())}
        x = vectors['vectors'][[lookup[p] for p in ids]]
    xy = np.array([coords[p] for p in ids])
    truth = [labels[p]['color_labels'][0] for p in ids]
    assert len(ids) == 65 and len(set(truth)) == 13 and len(set(assigned)) == K
    assert all(labels[p]['status'] == 'single' for p in ids)
    assert np.isfinite(xy).all() and np.allclose(np.linalg.norm(x, axis=1), 1, atol=1e-5)
    distances = np.maximum(0, 1 - x @ x.T)
    np.fill_diagonal(distances, 0)
    scores = []
    for i, group in enumerate(assigned):
        same = assigned == group
        if same.sum() == 1:
            scores.append(0.)
            continue
        a = distances[i, same].sum() / (same.sum() - 1)
        b = min(distances[i, assigned == g].mean() for g in set(assigned) if g != group)
        scores.append(float((b-a) / max(a,b)))
    assert abs(np.mean(scores) - run['silhouette']) < 1e-5
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'text.color': '#172c3d', 'axes.labelcolor': '#172c3d'})
    fig, ax = plt.subplots(figsize=(9.2, 6.7))
    fig.subplots_adjust(left=.11, right=.81, bottom=.16, top=.84)
    fig.text(.11, .945, 'Off-the-shelf Qwen: color structure', fontsize=20, weight='medium')
    fig.text(.11, .9, 'Qwen3-Embedding-8B + condition  |  Same 65 validation inputs  |  K = 12', fontsize=10.5, color='#596975')
    for group in range(K):
        mask = assigned == group
        center = xy[mask].mean(axis=0)
        for point in xy[mask]:
            ax.plot([center[0], point[0]], [center[1], point[1]], color='#a7adb3', alpha=.5, lw=.65, zorder=1)
        ax.annotate(str(group+1), center, xytext=(4,4), textcoords='offset points',
                    fontsize=7.5, color='#68727b', zorder=4,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=.7, pad=.4))
    for color in sorted(set(truth)):
        mask = np.array([t == color for t in truth])
        ax.scatter(*xy[mask].T, s=53, color=PALETTE.get(color,color), alpha=.85,
                   edgecolor='#5b6267' if color in ['white','beige'] else 'none',
                   linewidth=.6, label=color, zorder=3)
    ax.set(xlabel='Principal component 1', ylabel='Principal component 2')
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(alpha=.1)
    ax.legend(title='Target color', loc='center left', bbox_to_anchor=(1.01,.5),
              frameon=False, fontsize=9, title_fontsize=10, labelspacing=.75)
    fig.text(.11,.065,'Dots show reference colors; gray spokes and numbers show the 12 fitted groups.',fontsize=10,color='#596975')
    fig.text(.11,.027,f'Saved PCA coordinates and full-dimensional clustering  |  Plotted-fit ARI: {run["ari"]:.3f}',fontsize=9,color='#596975')
    for extension in ['png','svg']:
        fig.savefig(out/f'off-the-shelf-qwen-k12-pca.{extension}', dpi=190)
    plt.close(fig)
    rows = [dict(point_id=p, condition=points[p]['condition'], sentence=points[p]['sentence'],
                 target_color=truth[i], cluster=int(assigned[i])+1, pc1=xy[i,0], pc2=xy[i,1])
            for i,p in enumerate(ids)]
    with (out/'off-the-shelf-qwen-k12-points.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary = dict(arm=ARM, cohort=COHORT, points=len(ids), reference_colors=len(set(truth)), k=K,
                   k_policy='Match fine-tuned validation silhouette-selected K=12',
                   seed_policy='Highest cosine silhouette among 20 saved starts at fixed K; lower-seed tie break',
                   plotted_run=run, color_palette=PALETTE,
                   pca='Original per-encoder validation PC1/PC2 coordinates, reused exactly',
                   clustering='Saved assignments on normalized 4096-dimensional vectors',
                   spokes='Connect each point to the mean PCA coordinates of its assigned group',
                   source_archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                   median_ari_at_k={arm:float(np.median([r['ari'] for r in a['runs'] if r['k']==K]))
                                    for arm,a in cohort['arms'].items()})
    (out/'off-the-shelf-qwen-k12-metadata.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
