"""Write the scientific report before optional figures/publication."""
import json
from pathlib import Path
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
O=Path(__file__).resolve().parents[2]/"training_outputs/moral_geometry_20261110"
def write_report(x):
 selection=x["selection"]["selected"];primary=x["retrieval"]["primary"];reserve=x["retrieval"]["reserve"]
 e=x["paired_effects"]["primary/defined minus unconditioned"]
 gain=x["paired_effects"]["reserve/"+selection+" minus defined"]
 recommendation="revise"
 if e["ci95"][0]>0 and gain["ci95"][0]>0 and reserve[selection]["accuracy"]>reserve["lexical"]["accuracy"]:recommendation="pursue a bounded expert-annotated follow-up"
 if max(reserve[m]["accuracy"] for m in ["short","defined","residual","difference"])<=reserve["lexical"]["accuracy"] and reserve["oracle_cards"]["accuracy"]<=reserve["lexical"]["accuracy"]:recommendation="abandon a standalone moral-geometry claim; retain the encoder project and revise the retrieval task"
 lines=["# JEP moral geometry pilot","",f"**Recommendation: {recommendation}.**","",
 "This is a computational falsification screen using authored synthetic cases and the existing cleaned JEP C-STS dataset. It supplies no new human moral validation.",
 "", "## What was actually run","",
 "- Reused the validation-selected Qwen3-Embedding-8B condition-first LoRA checkpoint; no backbone or adapter retraining.",
 "- Compared raw, neutral, short-condition, operational-definition, paraphrase, condition-displacement, pair-score subtraction, and oracle evidence-card views on the same cross-family candidates.",
 "- Fitted paired signed versus nonnegative diagonal kernels on frozen Qwen features, with 64/256 cleaned training labels and three randomized train-only PCA seeds. This is a narrow PSD intervention.",
 "- Used released MET-D-Qwen3-4B weights to produce short, forced-theory views under fixed care/harm. This modifies MET inference; it does not reproduce its ground selector or self-distillation training.",
 "- Collected predeclared layer 0/9/18/27/final EOD vectors for the theory/repair screen. Layer 0 is an identical-token null baseline.",
 "", "## Conditioning and controlled retrieval","",
 "The specified interpretations are equal-person-weight expected lives saved; informed, unpressured worker consent; and equal work burdens among four equally responsible people. All cases stipulate equal linear work disutility and sixteen total work hours. These interpretations define partial expected resemblance orders, not complete ethical theories or unique numeric moral ratings.",
 "",
 "There are twenty story families: four development, twelve primary, four reserve. A relevant candidate changes topic while preserving the requested aspect; distractors include a same-story candidate changing that aspect. Synthetic families are never used to train Qwen or the geometry heads. Candidate position ties receive expected random-tie credit.",
 "",
 f"The development-selected method was **{selection}**. Its identity was recorded before reserve metrics. Oracle cards were excluded from selection because they reveal authored relevant evidence spans.",
 "", "| Method | Primary ranking accuracy | Family 95% interval | Reserve accuracy |","|---|---:|---|---:|"]
 for m in ["lexical","unconditioned","neutral","short","defined","paraphrase","residual","difference","oracle_cards"]:
  p=primary[m];r=reserve[m]
  lines.append(f"| {m} | {p['accuracy']:.3f} | [{p['ci95'][0]:.3f}, {p['ci95'][1]:.3f}] | {r['accuracy']:.3f} |")
 lines+=["","Ranking accuracy compares the relevant candidate with each distractor (chance 0.5). Recall@1 and MRR use the three-candidate pool and are retained in results.json. Bootstrap units are original story families, not their correlated perturbations. With only four reserve families, confirmation remains weak.",
 "", "![Conditioned retrieval](retrieval.svg)","",
 "## Does imposing geometry help?","",
 "Both kernels use the same normalized, training-only PCA features, target mapping, ridge penalty and exact convex objective. Only the restriction to nonnegative diagonal weights changes. Ordinary conditional cosine was already PSD; no distance transform is treated as an improvement. Raw kernel diagonals are preserved. No held-out labels complete or project a matrix.",
 "", "| Arm | Reference Spearman | Reference MSE |","|---|---:|---:|"]
 for arm,m in x["reference"].items():
  lines.append(f"| {arm} | {m['spearman'] if m['spearman'] is not None else 'undefined'} | {m['mse']:.5f} |")
 lines+=["","The reference is the existing cleaned, audited JEP C-STS labels, kept in their existing partitions. Its test examples were previously examined in other work; this is exploratory reference evidence, not a new human or untouched test benchmark. Low-label fits use the remaining training vectors without labels for PCA. Seed variation concerns the randomized basis; it is not independent evidence from new people.",
 "", "![PSD intervention](geometry.svg)","",
 "## Fixed harm, different theories; reasoning and layers","",
 "The auxiliary screen holds care/harm fixed while varying explicit Utilitarianism, Deontology and Care Ethics framings. Supplied grounds and generated reasoning views remain separate from synthetic expectations. Prompt-induced separation is framing sensitivity, not evidence that a theory is correct. The short MET-D views are available for inspection in reasoning_views.json, including truncation flags.",
 "", f"Retained generated views: {len(x['reasoning_views'])}; generation at its token bound: {sum(bool(v['truncated']) for v in x['reasoning_views'])}. No view is used as a gold moral judgment.",
 "", "Short decoder views that hit the token limit or contain introductory meta-discussion are not validated reasoning representations. Their geometry is a diagnostic of this failed or incomplete auxiliary arm, not evidence of a reasoning gain.", "", "![Layer diagnostics](layers.svg)","",
 "## Harm, reparation and sanction","",
 "The six authored harm-response families cover land, housing, health, education, water and truth about disappearance. We compare the direction from harm to an illustrative repair with harm to a punitive response, leaving each family out of the reference direction in turn.",
 "",
 "This tests a typed relation. It does not assume that reparation is a reflection, inverse, or erasure of harm. Multiple remedies may be appropriate; some losses cannot be reversed. Sanctions can concern the responsible actor rather than the victim's deficit. The candidates have not been certified as sufficient reparation by JEP experts.",
 "", "![Restorative relations](restoration.svg)","",
 "## Execution validity, failures and limits","",
 f"Behavioral checkpoint replay on {x['behavioral_replay']['rows']} cleaned validation pairs: maximum absolute cosine difference {x['behavioral_replay']['max_abs_difference']:.6f}; mean {x['behavioral_replay']['mean_abs_difference']:.6f}. Exact original prediction bytes were recovered and verified before this comparison.",
 "",
 "Five agents reviewed the code and five separately proposed methods. The rejected MiniLM/raw-dataset draft never ran as the experiment. Reviews caught wrong partition reuse, inadequate probe construction, a fake resume check, a normalization error, metadata size limits, and unsafe automatic resource deletion. Replacement boundaries and the independent metric verifier were checked separately.",
 "",
 "Actual launch issues included an external-IP policy denial, Seoul Spot capacity failures, a missing image runtime path, an auxiliary Jinja dependency mismatch, retained model memory after an exception, and denied GPU-side return publication. These are execution failures, not negative scientific findings. The existing private network and authenticated IAP transfer preserve outputs without IAM/account changes.",
 "",
 "No successful training or inference is repeated for plotting, reporting or upload. The hashed local outbox is authoritative while asynchronous VIPER publication is pending. Resource ownership and cleanup are retained in execution.json/cleanup.json when available.",
 "",
 "Remaining limitations: small and structured synthetic data; partial perturbation coverage; oracle evidence access; no new expert retrieval labels; no generative-model fine-tuning; no validated moral similarity numbers; and multiple predeclared exploratory methods. A positive synthetic result motivates expert evaluation, not a moral-reasoning claim.",
 "", "## Prior work and novelty boundary","",
 "- [C-STS](https://aclanthology.org/2023.emnlp-main.345/) already defines natural-language-conditioned similarity.",
 "- [CASE](https://aclanthology.org/2026.eacl-long.231/) and [SCS](https://aclanthology.org/2026.acl-long.50/) already study conditional representation improvement and contrast. Output subtraction here is an ablation, not a reproduction of attention-level SCS.",
 "- [Verheyen and Peterson](https://doi.org/10.1007/s13164-020-00495-5) and [Tang 2026](https://doi.org/10.1007/s43681-026-01368-w) already examine moral spaces and model–human structural alignment.",
 "- [MET/MET-D](https://arxiv.org/abs/2607.11736) supplies theory-grounded moral reasoning and self-distillation; this pilot uses released weights with explicitly forced grounds.",
 "- [Analogy-preserving sentence embeddings](https://aclanthology.org/K19-1085/) and [sentence analogies](https://aclanthology.org/2020.coling-main.300/) precede relation-vector probes.",
 "- [What Comes After Harm?](https://arxiv.org/abs/2506.05687) already develops a reparative-action taxonomy. This search did not establish that conditional JEP harm-to-response translation has already been demonstrated, and does not establish novelty by absence.",
 "",
 "The potential contribution is a controlled, theory-explicit cross-situation evaluation and useful retrieval behavior—not the existence of PSD embeddings or moral geometry.",
 ""]
 text="\n".join(lines);(R/"REPORT.md").write_text(text);(O/"REPORT.md").write_text(text);(O/"README.md").write_text(text)
 (R/"recommendation.json").write_text(json.dumps(dict(recommendation=recommendation),indent=2)+"\n")
