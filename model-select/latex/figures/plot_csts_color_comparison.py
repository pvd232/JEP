#!/usr/bin/env python3
"""Render the saved C-STS color fits as two symmetrically formatted panels.

The adjacent CSVs preserve the coordinates and assignments published at
9efa1d385fcc67f4daabc7f606f83263e8cdba0a under
training_outputs/color_clustering_20261104/key_charts/matched-k/.
Run with Python, NumPy, and Matplotlib to rebuild the PNG and vector PDF.
"""

import csv
import json
from collections import Counter
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parent
COLORS = ["black", "blond", "blue", "brown", "gray", "green", "navy",
          "orange", "pink", "red", "tan", "white", "yellow"]
PALETTE = {"blond": "#c6a74a", "gray": "#888888"}
PANELS = [
    ("off-the-shelf-qwen-k12-points.csv", "Control Qwen", 0.3478411738462301),
    ("fine-tuned-qwen-k12-points.csv", "Fine-tuned Qwen", 0.9485514003665713),
]


def load_points(filename):
    """Load the original coordinates, colors, and cluster IDs without refitting."""
    with (ROOT / filename).open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    xy = np.array([(float(r["pc1"]), float(r["pc2"])) for r in rows])
    groups = np.array([int(r["cluster"]) for r in rows])
    labels = [r["target_color"] for r in rows]
    assert len(rows) == len({r["point_id"] for r in rows}) == 65
    assert set(groups) == set(range(1, 13))
    assert sorted(set(labels)) == sorted(COLORS)
    assert np.isfinite(xy).all() and np.abs(xy).max() < 0.7
    return rows, xy, groups, labels


def adjusted_rand_index(groups, labels):
    """Measure agreement between saved cluster assignments and color labels."""
    pairs = sum(comb(n, 2) for n in Counter(zip(groups, labels)).values())
    group_pairs = sum(comb(n, 2) for n in Counter(groups).values())
    label_pairs = sum(comb(n, 2) for n in Counter(labels).values())
    expected = group_pairs * label_pairs / comb(len(labels), 2)
    return (pairs - expected) / ((group_pairs + label_pairs) / 2 - expected)


def draw_panel(ax, xy, groups, labels, title, ari, right_side=False):
    """Apply identical plot styles, with vertical labels on the outer edges."""
    for group in range(1, 13):
        selected = xy[groups == group]
        center = selected.mean(axis=0)
        for point in selected:
            ax.plot([center[0], point[0]], [center[1], point[1]],
                    color="#a7adb3", alpha=0.55, linewidth=0.65, zorder=1)
        ax.annotate(str(group), center, xytext=(3, 3),
                    textcoords="offset points", fontsize=6.5,
                    color="#68727b", zorder=4)
    for color in COLORS:
        selected = xy[np.array([label == color for label in labels])]
        ax.scatter(selected[:, 0], selected[:, 1], s=25,
                   color=PALETTE.get(color, color), alpha=0.85,
                   edgecolor="#5b6267" if color == "white" else "none",
                   linewidth=0.55, zorder=3)
    ticks = np.arange(-0.6, 0.61, 0.2)
    ax.set(xlim=(-0.7, 0.7), ylim=(-0.7, 0.7), xticks=ticks, yticks=ticks,
           xlabel="PC1", ylabel="PC2")
    ax.set_aspect("equal", adjustable="box")
    ax.tick_params(labelsize=8, length=3, width=0.6)
    ax.grid(color="#d9dde2", linewidth=0.45, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(right_side)
    ax.spines["left"].set_visible(not right_side)
    for spine in ax.spines.values():
        spine.set_linewidth(0.65)
    if right_side:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
    ax.set_title(f"{title}\nARI {ari:.3f}", fontsize=11, pad=11, linespacing=1.4)


def main():
    """Validate the saved fits and export the matching panel layout."""
    data = [load_points(filename) for filename, _, _ in PANELS]
    identity_fields = ("point_id", "condition", "sentence", "target_color")
    assert [[r[k] for k in identity_fields] for r in data[0][0]] == [
        [r[k] for k in identity_fields] for r in data[1][0]
    ]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.labelcolor": "#172c3d",
        "text.color": "#172c3d", "figure.facecolor": "white",
        "savefig.facecolor": "white", "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(7.2, 4.3))
    width = 0.37
    height = width * 7.2 / 4.3
    axes = [fig.add_axes([left, 0.25, width, height]) for left in (0.09, 0.54)]
    scores = []
    for i, (ax, (_, title, expected), (_, xy, groups, labels)) in enumerate(
            zip(axes, PANELS, data)):
        ari = adjusted_rand_index(groups, labels)
        assert abs(ari - expected) < 1e-12
        scores.append(ari)
        draw_panel(ax, xy, groups, labels, title, ari, right_side=(i == 1))
    handles = [
        Line2D([], [], linestyle="", marker="o", markersize=5.5,
               markerfacecolor=PALETTE.get(color, color),
               markeredgecolor="#5b6267" if color == "white"
               else PALETTE.get(color, color),
               markeredgewidth=0.55, alpha=0.85, label=color)
        for color in COLORS
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.025),
               ncol=7, frameon=False, fontsize=8, handletextpad=0.4,
               columnspacing=1.15, labelspacing=0.8)
    fig.canvas.draw()
    left, right = [ax.get_position() for ax in axes]
    assert np.allclose([left.width, left.height], [right.width, right.height])
    assert np.isclose(left.x0, 1 - right.x1)
    assert np.isclose(left.y0, right.y0)
    for suffix in ("png", "pdf"):
        fig.savefig(ROOT / f"qwen-k12-pca-comparison.{suffix}", dpi=320)
    plt.close(fig)
    print(json.dumps({"points_per_panel": 65, "clusters_per_panel": 12,
                      "ari": scores, "symmetric_axes": True}))


if __name__ == "__main__":
    main()
