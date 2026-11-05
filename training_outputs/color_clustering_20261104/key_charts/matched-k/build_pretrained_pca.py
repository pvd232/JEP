#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""Plot matched PC1/PC2 illustrations from saved Qwen embeddings and fits."""
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
from matplotlib.ticker import MultipleLocator
import numpy as np

PALETTE = {'blond': '#c6a74a', 'gold': '#cda400', 'gray': '#888888',
           'unknown': '#bcbcbc', 'maroon': '#800000'}
COHORT, K = 'validation_single', 12
ARMS = [('pretrained_conditioned', 'Off-the-shelf Qwen', 'off-the-shelf-qwen'),
        ('finetuned_conditioned', 'Fine-tuned Qwen', 'fine-tuned-qwen')]


def load_result(z, metrics, arm):
    """Verify one arm's saved fit and recover its original PCA coordinates."""
    cohort = metrics['cohorts'][COHORT]
    result = cohort['arms'][arm]
    run = max((r for r in result['runs'] if r['k'] == K),
              key=lambda r: (r['silhouette'], -r['seed']))
    saved = np.load(io.BytesIO(z.read(f'tables/{COHORT}-{arm}-all-assignments.npz')))
    ids = saved['point_ids'].tolist()
    assert ids == cohort['point_ids']
    assigned = saved[f'K{K}_seed{run["seed"]}']
    labels = {r['point_id']: r for r in json.loads(z.read('color-labels.json'))}
    points = {r['point_id']: r for r in json.loads(z.read('points.json'))}
    coords = {}
    for row in csv.DictReader(io.StringIO(z.read('tables/representative-point-diagnostics.csv').decode())):
        if row['cohort'] == COHORT and row['arm'] == arm:
            xy = (float(row['pc1']), float(row['pc2']))
            assert row['point_id'] not in coords or coords[row['point_id']] == xy
            coords[row['point_id']] = xy
    vectors = np.load(io.BytesIO(z.read(f'embeddings/{arm}.npz')))
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
    return dict(ids=ids, assigned=assigned, xy=xy, truth=truth, points=points, run=run)


def draw_panel(ax, data, bounds):
    """Draw reference colors and cluster spokes with shared sizes and axis limits."""
    xy, assigned, truth = data['xy'], data['assigned'], data['truth']
    for group in range(K):
        mask = assigned == group
        center = xy[mask].mean(axis=0)
        for point in xy[mask]:
            ax.plot([center[0], point[0]], [center[1], point[1]],
                    color='#a7adb3', alpha=.5, lw=.65, zorder=1)
        ax.annotate(str(group+1), center, xytext=(4,4), textcoords='offset points',
                    fontsize=7.5, color='#68727b', zorder=4,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=.7, pad=.4))
    for color in sorted(set(truth)):
        mask = np.array([t == color for t in truth])
        ax.scatter(*xy[mask].T, s=53, color=PALETTE.get(color,color), alpha=.85,
                   edgecolor='#5b6267' if color in ['white','beige'] else 'none',
                   linewidth=.6, label=color, zorder=3)
    ax.set(xlabel='Principal component 1', ylabel='Principal component 2',
           xlim=bounds, ylim=bounds)
    ax.set_aspect('equal', adjustable='box')
    ax.xaxis.set_major_locator(MultipleLocator(.2))
    ax.yaxis.set_major_locator(MultipleLocator(.2))
    ax.grid(alpha=.1)


def save_figure(fig, out, stem):
    """Save one illustration in raster and scalable vector formats."""
    for extension in ['png','svg']:
        fig.savefig(out/f'{stem}.{extension}', dpi=190)
    plt.close(fig)


def main():
    """Render standalone and paired illustrations with identical panel formatting."""
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.archive) as z:
        metrics = json.loads(z.read('metrics.json'))
        data = {arm: load_result(z, metrics, arm) for arm,_,_ in ARMS}
    first, second = [data[arm] for arm,_,_ in ARMS]
    assert first['ids'] == second['ids'] and first['truth'] == second['truth']
    extent = max(float(np.abs(d['xy']).max()) for d in data.values())
    limit = float(np.ceil((extent + .05) * 10) / 10)
    bounds = (-limit, limit)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'text.color': '#172c3d', 'axes.labelcolor': '#172c3d'})
    common = 'Qwen3-Embedding-8B + condition  |  Same 65 validation inputs  |  K = 12'
    caption = 'Dots show reference colors; gray spokes and numbers show the 12 fitted groups.'
    archive_hash = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    for arm, title, stem in ARMS:
        d = data[arm]
        fig, ax = plt.subplots(figsize=(9.2, 6.7))
        fig.subplots_adjust(left=.11, right=.81, bottom=.16, top=.84)
        fig.text(.11, .945, title + ': color structure', fontsize=20)
        fig.text(.11, .9, common, fontsize=10.5, color='#596975')
        draw_panel(ax, d, bounds)
        ax.legend(title='Target color', loc='center left', bbox_to_anchor=(1.01,.5),
                  frameon=False, fontsize=9, title_fontsize=10, labelspacing=.75)
        fig.text(.11,.065,caption,fontsize=10,color='#596975')
        fig.text(.11,.027,f'Saved PCA coordinates and full-dimensional clustering  |  Plotted-fit ARI: {d["run"]["ari"]:.3f}',
                 fontsize=9,color='#596975')
        save_figure(fig,out,stem+'-k12-pca')
        rows = [dict(point_id=p, condition=d['points'][p]['condition'], sentence=d['points'][p]['sentence'],
                     target_color=d['truth'][i], cluster=int(d['assigned'][i])+1,
                     pc1=d['xy'][i,0], pc2=d['xy'][i,1]) for i,p in enumerate(d['ids'])]
        with (out/(stem+'-k12-points.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        summary = dict(arm=arm, cohort=COHORT, points=65, reference_colors=13, k=K,
                       k_policy='Match fine-tuned validation silhouette-selected K=12',
                       seed_policy='Highest cosine silhouette among 20 saved starts at fixed K; lower-seed tie break',
                       plotted_run=d['run'], color_palette=PALETTE,
                       pca='Original per-encoder validation PC1/PC2 coordinates, reused exactly',
                       clustering='Saved assignments on normalized 4096-dimensional vectors',
                       spokes='Connect each point to the mean PCA coordinates of its assigned group',
                       axis_limits=list(bounds), equal_axis_aspect=True, group_numbers='Local to each encoder',
                       source_archive_sha256=archive_hash,
                       median_ari_at_k={a:float(np.median([r['ari'] for r in result['runs'] if r['k']==K]))
                                        for a,result in metrics['cohorts'][COHORT]['arms'].items()})
        (out/(stem+'-k12-metadata.json')).write_text(json.dumps(summary,indent=2)+'\n')
    fig, axes = plt.subplots(1,2,figsize=(16.4,7.4))
    fig.subplots_adjust(left=.055,right=.875,bottom=.19,top=.78,wspace=.2)
    fig.text(.055,.945,'Qwen color structure: matched comparison',fontsize=23)
    fig.text(.055,.895,common,fontsize=11,color='#596975')
    for ax,(arm,title,_) in zip(axes,ARMS):
        draw_panel(ax,data[arm],bounds)
        ax.set_title(f'{title}  |  ARI {data[arm]["run"]["ari"]:.3f}',fontsize=14,pad=14)
    axes[-1].legend(title='Target color',loc='center left',bbox_to_anchor=(1.02,.5),
                    frameon=False,fontsize=9,title_fontsize=10,labelspacing=.75)
    assert axes[0].get_xlim() == axes[1].get_xlim() == bounds
    assert axes[0].get_ylim() == axes[1].get_ylim() == bounds
    fig.text(.055,.08,caption,fontsize=11,color='#596975')
    fig.text(.055,.035,'Same axis limits, point sizes and palette. Each encoder uses its own PC1/PC2; group numbers are local to each panel.',
             fontsize=10,color='#596975')
    save_figure(fig,out,'qwen-k12-pca-comparison')
    print(json.dumps({arm:d['run'] for arm,d in data.items()},indent=2))


if __name__ == '__main__':
    main()
