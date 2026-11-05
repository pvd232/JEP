#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""Create a compact review of the saved fine-tuned encoder and cluster winners."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgb
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/csts-color-clustering"
OUT = SOURCE / "key-charts"
WORK = ROOT / "tmp/pdfs/csts-color-key-charts"
ARM = "finetuned_conditioned"
ORDER = ["validation_single", "test_single", "pooled_single", "pooled_all",
         "validation_all", "test_all", "train_single", "train_all"]
FOCUS = ORDER[:4]
NAMES = {
    "validation_single": "Validation / one color",
    "test_single": "Test / one color",
    "pooled_single": "All splits / one color",
    "pooled_all": "All splits / all inputs",
    "validation_all": "Validation / all inputs",
    "test_all": "Test / all inputs",
    "train_single": "Training / one color",
    "train_all": "Training / all inputs",
}
BLUE, INK, MUTED = "#125b8e", "#172c3d", "#596975"
PALETTE = {"blond": "#c6a74a", "gold": "#cda400", "gray": "#888888",
           "unknown": "#bcbcbc", "maroon": "#800000"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "medium", "axes.titlepad": 10,
                     "axes.labelcolor": INK, "text.color": INK})


def write_csv(path: Path, rows: list[dict]) -> None:
    """Retain the exact values behind one review table."""
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def silhouette_values(x: np.ndarray, assigned: np.ndarray) -> np.ndarray:
    """Rescore saved assignments using the original cosine-distance policy."""
    distances = np.maximum(0, 1 - x @ x.T)
    np.fill_diagonal(distances, 0)
    clusters = np.unique(assigned)
    means = np.stack([distances[:, assigned == c].mean(axis=1) for c in clusters], axis=1)
    sizes = np.array([(assigned == c).sum() for c in clusters])
    own = np.searchsorted(clusters, assigned)
    a = means[np.arange(len(x)), own] * sizes[own] / np.maximum(sizes[own] - 1, 1)
    means[np.arange(len(x)), own] = np.inf
    b = means.min(axis=1)
    scores = (b - a) / np.maximum(a, b)
    scores[sizes[own] == 1] = 0
    return scores


def main() -> None:
    """Build seven readable pages from frozen results without fitting new models."""
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    metrics = json.loads((SOURCE / "metrics.json").read_text())
    archive = zipfile.ZipFile(SOURCE / "native-review.zip")
    labels = {p["point_id"]: p for p in json.loads(archive.read("color-labels.json"))}
    points = {p["point_id"]: p for p in json.loads(archive.read("points.json"))}
    cache = np.load(io.BytesIO(archive.read("embeddings/" + ARM + ".npz")))
    vector_ids = cache["point_ids"].tolist()
    vectors = cache["vectors"]
    vector_lookup = {pid: i for i, pid in enumerate(vector_ids)}
    coordinates = {}
    for row in csv.DictReader(io.StringIO(archive.read("tables/representative-point-diagnostics.csv").decode())):
        if row["arm"] == ARM:
            coordinates[(row["cohort"], row["point_id"])] = (float(row["pc1"]), float(row["pc2"]))
    winners, selected, curve_rows = [], {}, []
    for name in ORDER:
        cohort = metrics["cohorts"][name]
        arm = cohort["arms"][ARM]
        k = arm["k_star"]
        best_at_k = max((r for r in arm["runs"] if r["k"] == k), key=lambda r: (r["silhouette"], -r["seed"]))
        best = max(arm["runs"], key=lambda r: (r["silhouette"], -r["k"], -r["seed"]))
        vals = [r["silhouette"] for r in arm["runs"] if r["k"] == k]
        winners.append(dict(cohort=name,description=NAMES[name],points=cohort["points"],
                            known_colors=cohort["colors"],chosen_k=k,median_silhouette=float(np.median(vals)),
                            best_seed_at_chosen_k=best_at_k["seed"],best_score_at_chosen_k=best_at_k["silhouette"],
                            highest_single_run_k=best["k"],highest_single_run_seed=best["seed"],highest_single_run_score=best["silhouette"]))
        selected[name] = best_at_k
        for kk in arm["grid"]:
            values = [r["silhouette"] for r in arm["runs"] if r["k"] == kk]
            curve_rows.append(dict(cohort=name,k=kk,median=float(np.median(values)),
                                   lower_quartile=float(np.percentile(values,25)),upper_quartile=float(np.percentile(values,75)),
                                   best_score=float(max(values)),starts=len(values)))
    write_csv(OUT / "k-winners.csv", winners)
    write_csv(OUT / "silhouette-by-k.csv", curve_rows)
    write_csv(OUT / "selected-runs.csv", [dict(cohort=n,**selected[n]) for n in FOCUS])

    cover = WORK / "cover.pdf"
    page = canvas.Canvas(str(cover), pagesize=(1008,648))
    page.setFillColor(colors.HexColor(INK)); page.setFont("Helvetica-Bold",27)
    page.drawString(42,597,"C-STS color clustering: key results")
    page.setFont("Helvetica",13);page.drawString(42,571,"Fine-tuned Qwen3-Embedding-8B, with the original color condition included")
    body = ParagraphStyle("body",fontName="Helvetica",fontSize=11,leading=16,textColor=colors.HexColor(INK))
    def para(text: str,x: float,y: float,width: float) -> float:
        paragraph=Paragraph(text,body);_,height=paragraph.wrap(width,200);paragraph.drawOn(page,x,y-height);return y-height
    para("<b>What the earlier numbers mean.</b> The single-color validation subset contains 13 color labels; 12 groups gave the best typical separation score. The test subset contains 11 color labels and favors 11 groups. Across all 1,017 inputs, the selected result is 20 groups.",42,545,924)
    page.setFont("Helvetica-Bold",13);page.drawString(42,470,"Winning encoder setup")
    para("<b>Checkpoint:</b> proposition_final.pt &nbsp; | &nbsp; <b>LoRA:</b> rank 32, alpha 32, dropout 0.05<br/><b>Embeddings:</b> final non-padding end token, 4,096 dimensions, unit-length normalized; 160-token limit.<br/><b>Clustering:</b> k-means++ / Lloyd; 20 random starts per cluster count; at most 500 iterations. Existing frozen vectors are reused.",42,453,924)
    page.setFont("Helvetica-Bold",13);page.drawString(42,375,"Cluster-count winners for this encoder")
    table_data=[["Input group","Inputs","Colors*","Chosen K","Median score","Single-run K","Highest score"]]
    for w in winners:
        table_data.append([w["description"],str(w["points"]),str(w["known_colors"]),str(w["chosen_k"]),f'{w["median_silhouette"]:.4f}',str(w["highest_single_run_k"]),f'{w["highest_single_run_score"]:.4f}'])
    table=Table(table_data,colWidths=[263,67,67,90,110,110,110],rowHeights=[29]+[25]*8)
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                               ("FONTSIZE",(0,0),(-1,-1),11),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor(INK)),
                               ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9eff4")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f7f9fb")]),
                               ("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEBELOW",(0,0),(-1,0),0.7,colors.HexColor("#bdcbd6"))]))
    table.wrapOn(page,924,300);table.drawOn(page,42,134)
    para("<b>Chosen K:</b> highest median silhouette score over 20 starts. The median rewards a result that repeats across starting points. <b>Highest single run:</b> the best individual fit across all counts and starts. The cluster pages use the best start at the chosen K.",42,119,924)
    page.setFont("Helvetica",9);page.setFillColor(colors.HexColor(MUTED))
    page.drawString(42,48,"* Colors counted among clearly resolved, single-color inputs. Other inputs stay in the all-inputs analyses. Labels are provisional.")
    page.drawString(42,32,"Scores range from -1 to 1; higher means groups are tighter and further apart. No encoder training or clustering is repeated for this pack.")
    page.drawRightString(966,16,"1 / 7");page.save()

    pages=[]
    def finish(fig,slug,title,subtitle,page_number,pdf):
        fig.suptitle(title,fontsize=20,x=0.045,ha="left",y=0.972,color=INK)
        fig.text(0.045,0.927,subtitle,fontsize=10.5,color=MUTED)
        fig.text(0.045,0.025,"Fine-tuned Qwen3-Embedding-8B + condition | Saved experiment results",fontsize=9,color=MUTED)
        fig.text(0.955,0.025,f"{page_number} / 7",ha="right",fontsize=9,color=MUTED)
        fig.tight_layout(rect=(0.026,0.05,0.985,0.9),h_pad=2.4,w_pad=2.0)
        fig.savefig(OUT/"figures"/(slug+".png"),dpi=160)
        fig.savefig(OUT/"figures"/(slug+".svg"))
        pdf.savefig(fig);plt.close(fig);pages.append(dict(name=slug,title=title))

    selected_points=[]
    with PdfPages(WORK/"charts.pdf") as pdf:
        fig,axes=plt.subplots(2,2,figsize=(14,9))
        for ax,name in zip(axes.flat,FOCUS):
            rows=[r for r in curve_rows if r["cohort"]==name];w=next(r for r in winners if r["cohort"]==name)
            x=[r["k"] for r in rows];y=[r["median"] for r in rows]
            ax.fill_between(x,[r["lower_quartile"] for r in rows],[r["upper_quartile"] for r in rows],color=BLUE,alpha=.16,label="Middle 50% of starts")
            ax.plot(x,y,color=BLUE,lw=2,label="Median score")
            ax.axvline(w["known_colors"],color="#8b9298",ls="--",lw=1.2,label="Number of color labels")
            ax.scatter([w["chosen_k"]],[w["median_silhouette"]],s=75,color=BLUE,zorder=5)
            ax.annotate(f'Chosen: {w["chosen_k"]} clusters\nScore: {w["median_silhouette"]:.4f}',(w["chosen_k"],w["median_silhouette"]),xytext=(16,-43),textcoords="offset points",fontsize=11,color=BLUE,
                        bbox=dict(boxstyle="round,pad=0.3",facecolor="white",edgecolor="none",alpha=.92))
            ax.set(title=f'{NAMES[name]} | {w["points"]:,} inputs',xlabel="Number of clusters (K)",ylabel="Separation score (silhouette)",ylim=(0,1))
            ax.grid(axis="y",alpha=.15)
        axes.flat[0].legend(loc="lower right",fontsize=8)
        finish(fig,"01-cluster-count-winners","Which cluster count gives the clearest groups?","Each curve uses the winning fine-tuned encoder. Blue dots mark the highest median score across 20 starts.",2,pdf)

        for number,name in enumerate(FOCUS,3):
            c=metrics["cohorts"][name];run=selected[name];k,seed=run["k"],run["seed"]
            saved=np.load(io.BytesIO(archive.read(f"tables/{name}-{ARM}-all-assignments.npz")))
            ids=saved["point_ids"].tolist();assert ids==c["point_ids"]
            assigned=saved[f"K{k}_seed{seed}"];x=vectors[[vector_lookup[p] for p in ids]]
            scores=silhouette_values(x,assigned)
            assert abs(float(scores.mean())-run["silhouette"])<1e-5,(name,scores.mean(),run["silhouette"])
            projection=np.array([coordinates[(name,p)] for p in ids])
            truth=[labels[p]["color_labels"][0] if labels[p]["status"]=="single" else "unknown" for p in ids]
            color_names=sorted(set(truth),key=lambda z:(z=="unknown",z))
            fig,axes=plt.subplots(2,3,figsize=(14,9))
            for color in color_names:
                mask=np.array([t==color for t in truth]);label="Multiple / unclear" if color=="unknown" else color
                axes[0,0].scatter(*projection[mask].T,s=17 if len(ids)<200 else 9,color=PALETTE.get(color,color),alpha=.78,
                                  edgecolor="#5b6267" if color in ["white","beige"] else "none",linewidth=.35,label=label)
            axes[0,0].legend(fontsize=6.9,ncol=3,loc="best",framealpha=.94)
            axes[0,0].set(title="Reference colors",xlabel="PCA coordinate 1",ylabel="PCA coordinate 2")
            axes[0,1].scatter(*projection.T,c=assigned,s=18 if len(ids)<200 else 10,cmap="tab20",alpha=.8)
            axes[0,1].set(title=f"The {k} fitted groups",xlabel="PCA coordinate 1",ylabel="PCA coordinate 2")
            offset=0
            for cluster in range(k):
                values=np.sort(scores[assigned==cluster]);y=np.arange(offset,offset+len(values))
                axes[0,2].fill_betweenx(y,0,values,color=plt.get_cmap("tab20")(cluster/max(k-1,1)),alpha=.8)
                offset+=len(values)+max(2,int(len(ids)*.005))
            axes[0,2].axvline(run["silhouette"],ls="--",color=INK,lw=1)
            axes[0,2].set(title="Separation of individual inputs",xlabel="Silhouette score",yticks=[])
            sizes=np.bincount(assigned,minlength=k)
            axes[1,0].bar(np.arange(1,k+1),sizes,color=BLUE)
            axes[1,0].set(title="How many inputs each group contains",xlabel="Group",ylabel="Inputs",xticks=np.arange(1,k+1,2 if k>15 else 1))
            counts=np.array([[sum(t==color and a==cl for t,a in zip(truth,assigned)) for cl in range(k)] for color in color_names])
            fractions=counts/np.maximum(counts.sum(axis=1,keepdims=True),1)
            image=axes[1,1].imshow(fractions,aspect="auto",vmin=0,vmax=1,cmap="Blues")
            for y in range(len(color_names)):
                for cl in range(k):
                    if counts[y,cl]:axes[1,1].text(cl,y,str(counts[y,cl]),ha="center",va="center",fontsize=6.1,color="white" if fractions[y,cl]>.55 else INK)
            axes[1,1].set(title="Which colors landed in which groups?",xlabel="Group",yticks=range(len(color_names)),
                          yticklabels=["Multiple / unclear" if q=="unknown" else q for q in color_names],xticks=np.arange(0,k,2 if k>15 else 1),xticklabels=np.arange(1,k+1,2 if k>15 else 1))
            axes[1,1].tick_params(axis="y",labelsize=7.5);axes[1,1].tick_params(axis="x",labelsize=8)
            fig.colorbar(image,ax=axes[1,1],shrink=.72,pad=.025,label="Fraction of each row")
            centroids=np.stack([x[assigned==cl].mean(axis=0) for cl in range(k)])
            centroids/=np.linalg.norm(centroids,axis=1,keepdims=True)
            distances=np.maximum(0,1-centroids@centroids.T)
            image=axes[1,2].imshow(distances,vmin=0,vmax=2,cmap="viridis")
            axes[1,2].set(title="Distances between group centers",xlabel="Group",ylabel="Group",xticks=np.arange(0,k,3),yticks=np.arange(0,k,3),xticklabels=np.arange(1,k+1,3),yticklabels=np.arange(1,k+1,3))
            fig.colorbar(image,ax=axes[1,2],shrink=.72,pad=.025,label="Cosine distance")
            for i,pid in enumerate(ids):
                p=points[pid];selected_points.append(dict(cohort=name,point_id=pid,condition=p["condition"],sentence=p["sentence"],
                                                         color=";".join(labels[pid]["color_labels"]),label_status=labels[pid]["status"],k=k,seed=seed,
                                                         group=int(assigned[i])+1,silhouette=float(scores[i]),pc1=float(projection[i,0]),pc2=float(projection[i,1])))
            slug=f"0{number-1}-{name.replace('_','-')}-{k}-clusters"
            title=f"{NAMES[name]}: {k} clusters"
            subtitle=f'{len(ids):,} inputs | {c["colors"]} known colors | Best start at chosen K: seed {seed} | Silhouette {run["silhouette"]:.4f} | Color agreement (ARI) {run["ari"]:.4f}'
            finish(fig,slug,title,subtitle,number,pdf)

        fig,axes=plt.subplots(1,3,figsize=(14,9));arms=list(metrics["pair_similarity"])
        names=["Fine-tuned\n+ condition","Pretrained\n+ condition","Fine-tuned\ncondition omitted"]
        values=[[metrics["cohorts"]["validation_single"]["arms"][a]["median_ari_at_C"] for a in arms],
                [metrics["pair_similarity"][a]["validation"]["spearman"] for a in arms],
                [metrics["switch"][a]["both_directions_positive_rate"] for a in arms]]
        titles=["Color-label agreement at 13 clusters","Cosine similarity vs audited ratings","Correct color under both conditions"]
        units=["Adjusted Rand index (ARI)",r"Spearman correlation ($\rho$)","Eligible probes passing (%)"]
        details=["65 single-color validation inputs\nK=13 for every model; median of 20 starts",
                 "74 color-related validation pairs\nRaw cosine compared with audited ratings",
                 "47 eligible of 50 source-derived probes\nMixed splits; reference colors from other families"]
        for j,(ax,vals,title,unit,detail) in enumerate(zip(axes,values,titles,units,details)):
            shown=[100*v for v in vals] if j==2 else vals
            ax.bar(range(3),shown,color=[BLUE,"#97a7b3","#c4cdd4"],width=.62)
            for i,v in enumerate(shown):
                label=f"{round(vals[i]*metrics['switch'][arms[i]]['scored'])}/{metrics['switch'][arms[i]]['scored']}" if j==2 else f"{v:.3f}"
                offset=3 if j==2 else .03
                ax.text(i,v+(offset if v>=0 else -offset),label,ha="center",va="bottom" if v>=0 else "top",fontsize=13,color=INK)
            ax.axhline(0,color=MUTED,lw=.8)
            ax.set(xticks=range(3),xticklabels=names,ylim=(0,112) if j==2 else ((-1,1.12) if j==1 else (0,1.12)),title=title,ylabel=unit)
            ax.text(.5,-.21,detail,transform=ax.transAxes,ha="center",va="top",fontsize=9.5,color=MUTED)
            ax.grid(axis="y",alpha=.14);ax.set_axisbelow(True)
        fig.subplots_adjust(bottom=.26)
        finish(fig,"06-winning-encoder-controls","Fine-tuned Qwen3-Embedding-8B and the two controls","Left and middle: validation metrics. Right: exploratory condition-switch probes drawn from the dataset.",7,pdf)

    writer=PdfWriter()
    for source in [cover,WORK/"charts.pdf"]:
        for p in PdfReader(source).pages:writer.add_page(p)
    writer.add_metadata({"/Title":"C-STS color clustering - key charts","/Author":"JEP experiment","/Subject":"Fine-tuned encoder and cluster-count winners"})
    with (OUT/"csts-color-key-charts.pdf").open("wb") as f:writer.write(f)
    assert len(PdfReader(OUT/"csts-color-key-charts.pdf").pages)==7
    write_csv(OUT/"selected-point-data.csv",selected_points)
    model=json.loads(archive.read("model-manifest.json"))
    (OUT/"winning-model.json").write_text(json.dumps(model,indent=2)+"\n")
    (OUT/"chart-index.json").write_text(json.dumps(pages,indent=2)+"\n")
    readme="""# Key charts: fine-tuned Qwen + color condition

Open csts-color-key-charts.pdf (7 pages). The individual charts are in figures/ as PNG and SVG.

The chosen cluster count has the highest median silhouette across 20 random starts. The table also reports the highest individual run across all cluster counts. Cluster pages show the highest-scoring start at the chosen count. These are separate, explicitly labeled selections.

All-inputs results use 1,017 points, including multiple-color, unspecified and unresolved cases. Single-color results use 497 points with one clearly resolved relevant color. Validation and test are also shown separately. Color labels are provisional and were frozen before inference.

k-winners.csv includes both selection policies for every cohort. silhouette-by-k.csv contains the curves and seed variability. selected-runs.csv identifies the four plotted fits; selected-point-data.csv links each plotted point to its caption, condition, label, group, silhouette and original PCA coordinates. Group numbers in this pack start at 1.

The existing encoder vectors, original PCA coordinates and saved assignments are reused. No model training, encoding or k-means fitting is performed. Per-point silhouettes are recomputed from the original vectors and checked against each saved fit score within 1e-5.

winning-model.json pins the checkpoint and archived settings. build_key_pack.py creates this pack from outputs/csts-color-clustering/native-review.zip and metrics.json in the original experiment workspace. Full retained vectors remain in the earlier complete review bundle.
"""
    (OUT/"README.md").write_text(readme)
    shutil.copyfile(Path(__file__),OUT/"build_key_pack.py")
    hashes={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob("*")) if p.is_file() and p.name not in ["manifest.json","csts-color-key-charts.zip"]}
    (OUT/"manifest.json").write_text(json.dumps(dict(source_metrics_sha256=hashlib.sha256((SOURCE/"metrics.json").read_bytes()).hexdigest(),
                                                    source_archive_sha256=hashlib.sha256((SOURCE/"native-review.zip").read_bytes()).hexdigest(),
                                                    runtime=dict(python=sys.version,numpy=np.__version__,matplotlib=matplotlib.__version__),files=hashes),indent=2)+"\n")
    with zipfile.ZipFile(OUT/"csts-color-key-charts.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file() and p.suffix!=".zip":z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(OUT/"csts-color-key-charts.zip") as z:assert z.testzip() is None
    print(json.dumps(dict(pdf=str(OUT/"csts-color-key-charts.pdf"),pages=7,charts=len(pages),points=len(selected_points),winners=len(winners))))


if __name__=="__main__":
    main()
