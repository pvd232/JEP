"""Export the complete COLOR clustering visual and example-review pack."""

from __future__ import annotations

import csv
import html
import io
import tarfile
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from scripts import color_clustering
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_samples


def csv_file(path: Path, rows: list[dict]) -> None:
    """Write every diagnostic row with a stable union of its field names."""
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_review_pack(root: Path, cluster_archive: Path) -> None:
    """Save all cohort/arm diagnostics, exemplar tables and a visual review index."""
    points = color_clustering.read(root / "points.json")
    labels = color_clustering.read(root / "color-labels.json")
    metrics = color_clustering.read(root / "metrics.json")
    point_lookup = {p["point_id"]: i for i, p in enumerate(points)}
    label_lookup = {a["point_id"]: a for a in labels}
    tables, figures = root / "tables", root / "figures"
    tables.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    pages = []
    exported_metrics, exemplars, neighbors, silhouette_rows = [], [], [], []
    palette = {
        "blond": "#e6c875",
        "cream": "#fff4ba",
        "gold": "#dab700",
        "gray": "#888888",
        "maroon": "#800000",
        "unknown": "#b8b8b8",
    }
    all_vectors = {
        arm: np.load(root / "embeddings" / (arm + ".npz"))["vectors"]
        for arm in color_clustering.ARMS
    }

    def save(fig, name: str, title: str, pdf) -> None:
        """Retain one figure in raster, vector and paginated review formats."""
        fig.suptitle(title, fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, 0.96))
        fig.savefig(figures / (name + ".png"), dpi=150)
        fig.savefig(figures / (name + ".svg"))
        pdf.savefig(fig)
        pages.append({"name": name, "title": title})
        plt.close(fig)

    with (
        tarfile.open(cluster_archive) as archive,
        PdfPages(root / "diagnostics.pdf") as pdf,
    ):

        def load_run(cohort: str, arm: str, k: int, seed: int):
            """Read the exact retained assignments and centroids for one fitted run."""
            member = archive.extractfile(f"clusters/{cohort}/{arm}/{k}-{seed}.npz")
            if member is None:
                raise ValueError("report: incomplete evidence")
            return np.load(io.BytesIO(member.read()))

        counts = {}
        for label in labels:
            counts[label["status"]] = counts.get(label["status"], 0) + 1
        colors = {}
        for label in labels:
            if label["status"] == "single":
                color = label["color_labels"][0]
                colors[color] = colors.get(color, 0) + 1
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].bar(list(counts), list(counts.values()))
        axes[0].set(
            ylabel="Unique condition–sentence inputs", title="Annotation coverage"
        )
        names = sorted(colors, key=colors.get, reverse=True)
        axes[1].bar(
            names,
            [colors[c] for c in names],
            color=[palette.get(c, c) for c in names],
            edgecolor="#444",
            linewidth=0.5,
        )
        axes[1].tick_params(axis="x", rotation=65)
        axes[1].set(title="Represented single target colors", ylabel="Points")
        save(fig, "cohort-coverage", "Source and label coverage", pdf)

        for cohort_name, cohort in metrics["cohorts"].items():
            if not cohort["arms"]:
                continue
            fig, axes = plt.subplots(2, 2, figsize=(11, 8))
            for arm, result in cohort["arms"].items():
                records = result["runs"]
                for row in records:
                    exported_metrics.append(dict(cohort=cohort_name, arm=arm, **row))
                for ax, metric in zip(
                    axes.flat, ("ari", "silhouette", "inertia", "iterations")
                ):
                    rows = [
                        [
                            r[metric]
                            for r in records
                            if r["k"] == k and r[metric] is not None
                        ]
                        for k in result["grid"]
                    ]
                    middle = [np.median(r) if r else np.nan for r in rows]
                    low = [np.percentile(r, 25) if r else np.nan for r in rows]
                    high = [np.percentile(r, 75) if r else np.nan for r in rows]
                    ax.plot(result["grid"], middle, label=arm.replace("_", " "))
                    ax.fill_between(result["grid"], low, high, alpha=0.16)
                    ax.axvline(cohort["colors"], color="#777", ls="--", lw=0.8)
                    ax.set(xlabel="K", ylabel=metric, title=metric.replace("_", " "))
            axes[0, 0].legend(fontsize=7)
            save(
                fig,
                cohort_name + "-sweep",
                f"{cohort_name}: complete K sweep; bands show seed IQR",
                pdf,
            )
            indices = [point_lookup[pid] for pid in cohort["point_ids"]]
            truth = [
                label_lookup[pid]["color_labels"][0]
                if label_lookup[pid]["status"] == "single"
                else "unknown"
                for pid in cohort["point_ids"]
            ]
            color_names = sorted(set(truth))
            for arm, result in cohort["arms"].items():
                x = all_vectors[arm][indices]
                if len(x) < 3:
                    continue
                projection_model = PCA(
                    n_components=2, svd_solver="randomized", random_state=7
                )
                projection = projection_model.fit_transform(x)
                distances = np.maximum(0, 1 - x @ x.T)
                np.fill_diagonal(distances, 0)
                selected_k = sorted(
                    {
                        k
                        for k in (cohort["colors"], result["k_star"])
                        if k in result["grid"]
                    }
                )
                for k in selected_k:
                    candidates = [
                        r
                        for r in result["runs"]
                        if r["k"] == k and r["inertia"] is not None
                    ]
                    if not candidates:
                        continue
                    seed = min(candidates, key=lambda r: (r["inertia"], r["seed"]))[
                        "seed"
                    ]
                    fitted = load_run(cohort_name, arm, k, seed)
                    assigned, centroids = fitted["assignments"], fitted["centroids"]
                    observed_clusters = sorted(set(assigned))
                    sample_silhouette = (
                        silhouette_samples(distances, assigned, metric="precomputed")
                        if 1 < len(observed_clusters) < len(x)
                        else np.full(len(x), np.nan)
                    )
                    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
                    for color in color_names:
                        mask = np.array([c == color for c in truth])
                        axes[0, 0].scatter(
                            *projection[mask].T,
                            s=12,
                            color=palette.get(color, color),
                            edgecolor="#555" if color == "white" else "none",
                            linewidth=0.3,
                            alpha=0.75,
                            label=color,
                        )
                    axes[0, 0].legend(fontsize=6, ncol=3)
                    axes[0, 0].set(
                        title="PCA: source color labels", xlabel="PC 1", ylabel="PC 2"
                    )
                    axes[0, 1].scatter(
                        *projection.T, s=12, c=assigned, cmap="tab20", alpha=0.8
                    )
                    axes[0, 1].set(
                        title="PCA: fitted cluster assignments",
                        xlabel="PC 1",
                        ylabel="PC 2",
                    )
                    offset = 0
                    for cluster_id in observed_clusters:
                        values = np.sort(sample_silhouette[assigned == cluster_id])
                        axes[0, 2].fill_betweenx(
                            np.arange(offset, offset + len(values)),
                            0,
                            values,
                            alpha=0.7,
                        )
                        offset += len(values) + 3
                    axes[0, 2].axvline(
                        np.nanmean(sample_silhouette), color="#333", ls="--"
                    )
                    axes[0, 2].set(
                        title="Cosine silhouette by cluster",
                        xlabel="Silhouette",
                        yticks=[],
                    )
                    sizes = [int((assigned == c).sum()) for c in observed_clusters]
                    axes[1, 0].bar(observed_clusters, sizes)
                    axes[1, 0].set(
                        title="Cluster sizes", xlabel="Cluster", ylabel="Points"
                    )
                    contingency = np.array(
                        [
                            [
                                sum(
                                    t == color and c == cluster_id
                                    for t, c in zip(truth, assigned)
                                )
                                for cluster_id in observed_clusters
                            ]
                            for color in color_names
                        ]
                    )
                    axes[1, 1].imshow(contingency, aspect="auto", cmap="Blues")
                    axes[1, 1].set(
                        yticks=range(len(color_names)),
                        yticklabels=color_names,
                        xticks=range(len(observed_clusters)),
                        xticklabels=observed_clusters,
                        xlabel="Cluster",
                        title="Source-color / cluster counts",
                    )
                    axes[1, 1].tick_params(labelsize=7)
                    unit_centroids = centroids / np.maximum(
                        np.linalg.norm(centroids, axis=1, keepdims=True), 1e-12
                    )
                    axes[1, 2].imshow(
                        1 - unit_centroids @ unit_centroids.T,
                        vmin=0,
                        vmax=2,
                        cmap="viridis",
                    )
                    axes[1, 2].set(
                        title="Centroid cosine distances",
                        xlabel="Cluster",
                        ylabel="Cluster",
                    )
                    title = f"{cohort_name} · {arm} · K={k}, seed={seed}; PCA explains {projection_model.explained_variance_ratio_.sum():.1%}"
                    save(fig, f"{cohort_name}-{arm}-K{k}", title, pdf)
                    for j, pid in enumerate(cohort["point_ids"]):
                        silhouette_rows.append(
                            {
                                "cohort": cohort_name,
                                "arm": arm,
                                "k": k,
                                "seed": seed,
                                "point_id": pid,
                                "cluster": int(assigned[j]),
                                "silhouette": float(sample_silhouette[j]),
                                "pc1": float(projection[j, 0]),
                                "pc2": float(projection[j, 1]),
                                "source_color": truth[j],
                            }
                        )
                    for cluster_id in observed_clusters:
                        members = np.flatnonzero(assigned == cluster_id)
                        ranked = members[
                            np.argsort(-(x[members] @ unit_centroids[cluster_id]))
                        ]
                        central = list(ranked[:5])
                        peripheral = [j for j in ranked[-3:] if j not in central]
                        for rank, j in enumerate(central + peripheral):
                            point = points[indices[j]]
                            exemplars.append(
                                {
                                    "cohort": cohort_name,
                                    "arm": arm,
                                    "k": k,
                                    "seed": seed,
                                    "cluster": int(cluster_id),
                                    "position": "central"
                                    if rank < min(5, len(ranked))
                                    else "peripheral",
                                    "rank": rank,
                                    "point_id": point["point_id"],
                                    "condition": point["condition"],
                                    "sentence": point["sentence"],
                                    "source_colors": ";".join(
                                        label_lookup[point["point_id"]]["color_labels"]
                                    ),
                                    "cosine_to_centroid": float(
                                        x[j] @ unit_centroids[cluster_id]
                                    ),
                                }
                            )
                    csv_file(
                        tables / f"{cohort_name}-{arm}-K{k}-contingency.csv",
                        [
                            {
                                "color": color,
                                **{
                                    str(c): int(contingency[j, col])
                                    for col, c in enumerate(observed_clusters)
                                },
                            }
                            for j, color in enumerate(color_names)
                        ],
                    )
                selected = result["k_star"]
                if selected is not None:
                    seed_assignments = [
                        load_run(cohort_name, arm, selected, seed)["assignments"]
                        for seed in range(20)
                    ]
                    matrix = np.array(
                        [
                            [adjusted_rand_score(a, b) for b in seed_assignments]
                            for a in seed_assignments
                        ]
                    )
                    fig, ax = plt.subplots(figsize=(6, 5))
                    image = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis")
                    fig.colorbar(image, ax=ax, label="Assignment ARI")
                    ax.set(
                        xlabel="Seed",
                        ylabel="Seed",
                        xticks=range(0, 20, 2),
                        yticks=range(0, 20, 2),
                    )
                    save(
                        fig,
                        f"{cohort_name}-{arm}-stability",
                        f"{cohort_name} · {arm}: seed stability at K={selected}",
                        pdf,
                    )
                # A compact wide table retains every K/seed assignment without repeating captions.
                wide = {"point_ids": np.array(cohort["point_ids"])}
                for row in result["runs"]:
                    if row["inertia"] is not None:
                        wide[f"K{row['k']}_seed{row['seed']}"] = load_run(
                            cohort_name, arm, row["k"], row["seed"]
                        )["assignments"]
                np.savez_compressed(
                    tables / f"{cohort_name}-{arm}-all-assignments.npz", **wide
                )

        for arm, vectors in all_vectors.items():
            similarities = vectors @ vectors.T
            for i, point in enumerate(points):
                allowed = np.array([p["group_id"] != point["group_id"] for p in points])
                order = np.argsort(-np.where(allowed, similarities[i], -np.inf))[:5]
                for rank, j in enumerate(order, 1):
                    other = points[j]
                    neighbors.append(
                        {
                            "arm": arm,
                            "point_id": point["point_id"],
                            "condition": point["condition"],
                            "sentence": point["sentence"],
                            "source_colors": ";".join(
                                label_lookup[point["point_id"]]["color_labels"]
                            ),
                            "rank": rank,
                            "neighbor_id": other["point_id"],
                            "neighbor_condition": other["condition"],
                            "neighbor_sentence": other["sentence"],
                            "neighbor_colors": ";".join(
                                label_lookup[other["point_id"]]["color_labels"]
                            ),
                            "cosine": float(similarities[i, j]),
                        }
                    )
        for split in ("validation", "train", "test", "pooled"):
            fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True, sharey=True)
            for ax, arm in zip(axes, color_clustering.ARMS):
                pair = metrics["pair_similarity"][arm][split]
                ax.scatter(pair["ratings"], pair["predictions"], s=12, alpha=0.5)
                ax.set(
                    title=arm.replace("_", " "),
                    xlabel="Audited rating (1–5)",
                    ylabel="Raw cosine",
                )
                csv_file(
                    tables / f"{split}-{arm}-pair-scores.csv",
                    [
                        {
                            "index": i,
                            "group_id": group,
                            "rating": rating,
                            "cosine": pred,
                        }
                        for i, (group, rating, pred) in enumerate(
                            zip(pair["groups"], pair["ratings"], pair["predictions"])
                        )
                    ],
                )
            save(
                fig,
                split + "-pair-similarity",
                f"{split}: original-pair ratings and raw cosine",
                pdf,
            )
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for arm in color_clustering.ARMS:
            rows = [
                r for r in metrics["switch"][arm]["rows"] if r["status"] == "scored"
            ]
            axes[0].hist(
                [r["mean_margin"] for r in rows],
                bins=15,
                histtype="step",
                label=arm.replace("_", " "),
            )
        arms = list(color_clustering.ARMS)
        axes[1].bar(
            range(3),
            [metrics["switch"][a]["both_directions_positive_rate"] or 0 for a in arms],
        )
        axes[1].set(
            xticks=range(3),
            xticklabels=[a.replace("_", "\n") for a in arms],
            ylabel="Both directions positive",
            ylim=(0, 1),
        )
        axes[0].axvline(0, color="#777", ls="--")
        axes[0].set(xlabel="Bidirectional target-color margin", ylabel="Probes")
        axes[0].legend(fontsize=6)
        save(
            fig, "condition-switch", "Condition-switch coverage and directionality", pdf
        )
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        controls = list(color_clustering.ARMS[1:])
        for ax, measure in zip(axes, ("delta_ari", "delta_spearman")):
            for j, control in enumerate(controls):
                interval = metrics["paired_intervals"][control][measure]["interval_95"]
                if interval is not None:
                    ax.plot(interval, [j, j], lw=4)
                    if measure == "delta_ari":
                        arms = metrics["cohorts"]["validation_single"]["arms"]
                        estimate = (
                            arms[color_clustering.ARMS[0]]["median_ari_at_C"]
                            - arms[control]["median_ari_at_C"]
                        )
                    else:
                        scores = metrics["pair_similarity"]
                        estimate = (
                            scores[color_clustering.ARMS[0]]["validation"]["spearman"]
                            - scores[control]["validation"]["spearman"]
                        )
                    ax.scatter([estimate], [j], s=30)
            ax.axvline(0, color="#777", ls="--")
            ax.set(
                yticks=range(len(controls)),
                yticklabels=[c.replace("_", " ") for c in controls],
                xlabel="Main minus control",
                title=measure.replace("_", " "),
            )
        save(
            fig,
            "paired-intervals",
            "Validation: paired 95% source-family bootstrap intervals",
            pdf,
        )
        if pdf.get_pagecount() != len(pages):
            raise ValueError("report: incomplete visual evidence")

    csv_file(tables / "all-run-metrics.csv", exported_metrics)
    csv_file(tables / "cluster-exemplars.csv", exemplars)
    csv_file(tables / "cross-family-neighbors.csv", neighbors)
    csv_file(tables / "representative-point-diagnostics.csv", silhouette_rows)
    csv_file(
        tables / "source-points.csv",
        [
            dict(
                point_id=p["point_id"],
                condition=p["condition"],
                sentence=p["sentence"],
                group_id=p["group_id"],
                colors=";".join(label_lookup[p["point_id"]]["color_labels"]),
                status=label_lookup[p["point_id"]]["status"],
                evidence=";".join(label_lookup[p["point_id"]]["evidence"]),
            )
            for p in points
        ],
    )
    color_clustering.write(root / "visualization-index.json", pages)
    for page in pages:
        for suffix in (".png", ".svg"):
            if not (figures / (page["name"] + suffix)).is_file():
                raise ValueError("report: incomplete visual evidence")
    cards = "\n".join(
        f'<section data-title="{html.escape(p["title"].lower())}"><h2>{html.escape(p["title"])}</h2><a href="figures/{p["name"]}.svg"><img loading="lazy" src="figures/{p["name"]}.png" alt="{html.escape(p["title"])}"></a></section>'
        for p in pages
    )
    document = (
        '<!doctype html><meta charset="utf-8"><title>C-STS COLOR diagnostic review</title><style>body{font:15px system-ui;max-width:1450px;margin:30px auto;padding:0 20px;background:#fafafa;color:#18202a}header{position:sticky;top:0;background:#fafafaf5;padding:12px 0;border-bottom:1px solid #ddd}input{font:inherit;padding:9px;width:65%}section{background:white;padding:18px;margin:24px 0;border:1px solid #ddd;border-radius:8px}img{max-width:100%}h2{font-size:17px}a{color:#155e8b}</style><header><h1>C-STS COLOR diagnostic review</h1><p>Filter by split, cohort, encoder, or diagnostic. Click a plot for its SVG. Full assignments and example-level diagnostics are in tables/.</p><input placeholder="Search: validation, stability, pretrained, K…" oninput="document.querySelectorAll(\'section\').forEach(e=>e.hidden=!e.dataset.title.includes(this.value.toLowerCase()))"></header>'
        + cards
    )
    (root / "dashboard.html").write_text(document, encoding="utf-8")
    readme = "# Review Pack\n\nOpen dashboard.html after extracting this archive, or read diagnostics.pdf. figures/ contains every plot in PNG and SVG. tables/ contains all K/seed metrics, all assignments, representative point diagnostics, exemplars and cross-family neighbors. embeddings/ retains the full-dimensional vectors used by the analysis. Cluster centroids for every fit remain in the native VIPER clustering artifact. PCA is a two-dimensional view; clustering and numeric scores use the original normalized 4096 dimensions.\n"
    (root / "REVIEW.md").write_text(readme, encoding="utf-8")
    with zipfile.ZipFile(
        root / "review.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as bundle:
        for folder in ("figures", "tables", "embeddings"):
            for path in sorted((root / folder).rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(root))
        for filename in (
            "dashboard.html",
            "diagnostics.pdf",
            "report.md",
            "REVIEW.md",
            "visualization-index.json",
            "metrics.json",
            "points.json",
            "pairs.json",
            "color-labels.json",
            "cohort-manifest.json",
            "model-manifest.json",
            "experiment.toml",
            "switch-probe.json",
            "run-receipt.json",
        ):
            bundle.write(root / filename, filename)
