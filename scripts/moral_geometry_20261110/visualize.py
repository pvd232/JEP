"""Scientific figures from saved results, with source tables retained."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
ROOT=Path(__file__).resolve().parents[2];R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110");O=ROOT/"training_outputs/moral_geometry_20261110"
x=json.loads((R/"results_v2.json").read_text())
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"svg.fonttype":"none","axes.spines.top":False,"axes.spines.right":False})
def write(fig,name):
 fig.savefig(O/(name+".svg"),bbox_inches="tight");fig.savefig(O/(name+".png"),dpi=170,bbox_inches="tight");plt.close(fig)
methods=["lexical","unconditioned","neutral","short","defined","paraphrase","residual","difference","oracle_cards"]
labels=["Lexical control","No condition","Neutral condition","Short principle","Defined principle","Paraphrased rule","Condition displacement","Score subtraction","Oracle evidence card"]
fig,ax=plt.subplots(figsize=(9,5))
p=x["retrieval"]["primary"];ys=np.arange(len(methods));vals=np.array([p[m]["accuracy"] for m in methods]);lo=np.array([p[m]["ci95"][0] for m in methods]);hi=np.array([p[m]["ci95"][1] for m in methods])
ax.barh(ys,vals,color=["#8792a2" if m in ["lexical","unconditioned","neutral"] else "#298a88" for m in methods],alpha=.9)
ax.errorbar(vals,ys,xerr=np.stack([np.maximum(vals-lo,0),np.maximum(hi-vals,0)]),fmt="none",ecolor="#20303d",capsize=3)
ax.set(yticks=ys,yticklabels=labels,xlim=(0,1),xlabel="Pairwise ranking accuracy · 12 held-out story families",title="Does explicit conditioning recover the requested similarity?")
ax.axvline(.5,color="#777",ls=":",label="Chance");ax.invert_yaxis();ax.legend(loc="lower right");fig.text(.02,-.02,"Intervals resample story families. Oracle cards provide authored evidence access; they are an upper bound.",fontsize=9);write(fig,"retrieval")
rows=x.get("reference_effects",{})
fig,ax=plt.subplots(figsize=(8,4.4))
names=list(rows);means=np.array([rows[n]["family_mean_mse_difference"] for n in names]);lo=np.array([rows[n]["ci95"][0] for n in names]);hi=np.array([rows[n]["ci95"][1] for n in names])
ax.errorbar(means,np.arange(len(names)),xerr=np.stack([np.maximum(means-lo,0),np.maximum(hi-means,0)]),fmt="o",color="#62558b",capsize=4)
ax.axvline(0,color="#777",ls=":");ax.set(yticks=np.arange(len(names)),yticklabels=[n.replace(" minus signed"," − signed") for n in names],xlabel="Family-mean MSE difference: PSD − signed (negative favors PSD)",title="A matched restriction on the same frozen Qwen features")
fig.text(.01,-.02,"Cleaned C-STS reference track; 64/256 labels. Previously examined test partition. Three PCA seeds.",fontsize=9);write(fig,"geometry")
ext=x["extensions"];layers=[0,9,18,27,36]
fig,axes=plt.subplots(1,2,figsize=(10,3.7))
axes[0].plot(layers,[ext[str(k)]["invariance_mean_cosine"] for k in layers],"o-",color="#2b8c7e");axes[0].set(xlabel="Decoder depth",ylabel="Cosine, original vs irrelevant presentation edit",title="Presentation invariance")
axes[1].plot(layers,[ext[str(k)]["repair_vs_sanction_direction_margin"] for k in layers],"o-",color="#b3633b");axes[1].axhline(0,color="#777",ls=":");axes[1].set(xlabel="Decoder depth",ylabel="Repair-axis alignment − sanction-axis alignment",title="Typed restorative response direction")
for a in axes:a.set_xticks(layers);a.set_xticklabels(["Input\n(null)","9","18","27","Final"])
fig.suptitle("Predeclared layer probes · descriptive synthetic screen",y=1.04);fig.text(.01,-.04,"Input EOD embeddings are identical. A high null-layer invariance score carries no moral information.",fontsize=9);write(fig,"layers")
data=np.load(R/"gpu_return/embeddings.npz");vec=dict(zip([str(k) for k in data["keys"]],data["vectors"]))
cases=json.loads((R/"extension_cases.json").read_text());aspect="material restitution for the harm described";selected=[r for r in cases if r["condition"]==aspect]
pca=PCA(n_components=2).fit(np.stack([vec[r["key"]] for r in selected]));coords=pca.transform(np.stack([vec[r["key"]] for r in selected]))
fig,ax=plt.subplots(figsize=(8,5));families=sorted({r["family"] for r in selected});colors=plt.get_cmap("tab10")
for fi,f in enumerate(families):
 indices={r["type"]:i for i,r in enumerate(selected) if r["family"]==f}
 for typ,mark in [("harm","o"),("repair","^"),("sanction","s")]:
  point=coords[indices[typ]];ax.scatter(*point,color=colors(fi),marker=mark,s=65,label=typ if fi==0 else None);ax.annotate(f+" "+typ[:1].upper(),point,xytext=(3,4),textcoords="offset points",fontsize=8)
 h=coords[indices["harm"]]
 for typ,style in [("repair","-"),("sanction","--")]:
  end=coords[indices[typ]];ax.annotate("",xy=end,xytext=h,arrowprops=dict(arrowstyle="->",color=colors(fi),linestyle=style,alpha=.65))
ax.set(xlabel=f"PC1 ({pca.explained_variance_ratio_[0]:.0%} variance)",ylabel=f"PC2 ({pca.explained_variance_ratio_[1]:.0%} variance)",title="Harm → repair and harm → sanction under one fixed condition");ax.legend();fig.text(.01,-.03,"PCA is an illustration, not a metric-fit result. Arrows do not imply reversibility or sufficient reparation.",fontsize=9);write(fig,"restoration")
generated=json.loads((R/"gpu_return/generated_tasks.json").read_text()) if (R/"gpu_return/generated_tasks.json").exists() else []
if generated:
 theories=["Utilitarianism","Deontology","Care Ethics"];fig,axes=plt.subplots(3,2,figsize=(9,11),constrained_layout=True)
 for ti,theory in enumerate(theories):
  rr=sorted([r for r in generated if r["theory"]==theory],key=lambda r:r["family"])
  for col,(kind,field) in enumerate([("Raw scenario","source_key"),("MET-D forced-ground view","key")]):
   a=np.stack([vec[r[field]] for r in rr]);matrix=a@a.T;im=axes[ti,col].imshow(matrix,vmin=0,vmax=1,cmap="viridis")
   axes[ti,col].set(xticks=range(len(rr)),yticks=range(len(rr)),xticklabels=[r["family"] for r in rr],yticklabels=[r["family"] for r in rr],title=theory+" · "+kind)
   axes[ti,col].tick_params(axis="x",rotation=45)
 fig.colorbar(im,ax=axes.ravel().tolist(),label="Cosine within the fixed theory",shrink=.4);fig.suptitle("Same harm value and same six cases · generated views are not gold labels");write(fig,"reasoning")
# A precise public chart table supports independent reuse.
with (O/"retrieval_chart.csv").open("w") as f:
 writer=csv.writer(f);writer.writerow(["method","primary_accuracy","ci_low","ci_high","reserve_accuracy"])
 for m in methods:writer.writerow([m,p[m]["accuracy"],*p[m]["ci95"],x["retrieval"]["reserve"][m]["accuracy"]])
(R/"figures.json").write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob("*.svg")},indent=2)+"\n")
print("FIGURES_WRITTEN")
