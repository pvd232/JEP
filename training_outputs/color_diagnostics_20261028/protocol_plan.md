Locate the color regression in the saved models before choosing a training change.

**Probe.** Freeze 100 fresh caption families with four variants each: 30 explicit color families, 30 implied color families, 30 families with several colored objects, and 10 unspecified-color controls. Balance color values and object roles. Exclude C-STS captions and near duplicates. Two human raters label target colors before inference. Literal gold records stated colors; pragmatic gold also allows agreed defaults. Adjudicate disagreements, then hash the captions, labels and answer parser.

**Models.** Evaluate seeds 7, 8 and 9 at the selected writing checkpoint, matched control parent, and both final checkpoints. Include the shared pretrained encoder: 13 states. Keep weights frozen. Use the original caption prefix, normalized embeddings and vocabulary head; decode greedily with the existing 64-token ceiling. P and R denote proposition and control arms; A and B denote first-phase and final checkpoints.

**Color readout.** Map answers to color sets, preserving qualifications and object roles. Let V be the gold set and V-hat the decoded set. X_i contains a family's caption-condition inputs; N counts families. Exact accuracy averages answers within families, then families:

```math
E_a=\frac1N\sum_i\frac1{|X_i|}
       \sum_{(x,c)\in X_i}\mathbf1[\widehat V_a(x,c)=V(x,c)].
```

Primary E uses explicit and multiple-object families. Score implied answers against both gold judgments. Use unspecified controls for readout and abstention; report the fraction that invent a color. E measures readout through the fixed head.

**Embedding distance.** Under condition c, construct x+ by changing an irrelevant detail in anchor x0. Construct x− by changing only the target color. Normalize embedding h:

```math
z=\frac{h}{\|h\|},\qquad s(x,y;c)=z(x,c)^\top z(y,c),
\qquad d_\pm^2=2-2s(x_0,x_\pm;c).
```

The squared-distance difference therefore gives the color margin:

```math
m=s(x_0,x_+;c)-s(x_0,x_-;c)=\frac{d_-^2-d_+^2}{2}.
```

A positive margin places the matching color closer. Score four anchor orientations per explicit or multiple-object family, using one balanced target role. For seed k, let G_k contain triplets whose three answers are correct for both final arms:

```math
\Delta M_{G,k}=\frac1{|G_k|}\sum_{j\in G_k}(m_{j,P,k}-m_{j,R,k}).
```

Report eligible triplets, represented families and the margin over all families. Require 20 represented families per seed for a geometry interpretation. Smaller sets leave geometry unresolved.

**Object selection.** Cross two target colors with two distractor colors, giving x00, x01, x10 and x11. Under target condition ct, x01 matches x00. Under distractor condition cd, x10 matches x00. Define:

```math
C_a=\frac12\left[
 s_a(x_{00},x_{01};c_t)-s_a(x_{00},x_{10};c_t)
+s_a(x_{00},x_{10};c_d)-s_a(x_{00},x_{01};c_d)
\right].
```

Ignoring the condition gives C = 0 because the differences cancel. Average anchor orientations and report both condition margins. Let Vd be the distractor's color set. The wrong-object answer rate F averages multiple-object families:

```math
F_a=\operatorname{mean}_i\operatorname{mean}_{(x,c)\in X_i}
       \mathbf1[\widehat V_a(x,c)=V_d(x,c)].
```

Distinct target and distractor colors make F identify the wrong object.

**Implied color.** Pair each implicit caption xI with xE that states the human-agreed color. Use identical, separately worded matching and mismatching anchors for both captions:

```math
Q_a=\operatorname{mean}_i[m_a(x_i^E)-m_a(x_i^I)],
\qquad \Delta Q=Q_P-Q_R=\Delta\overline m_E-\Delta\overline m_I.
```

Q measures the explicit-cue benefit. Greater reliance on that cue requires a larger P-minus-R Q. An implied-color regression also requires a lower P-minus-R implicit margin. Pragmatic judgments supply comparison labels; literal-source judgments score abstention separately.

**Training stage.** The shared pretrained margin m0 cancels from the first-stage contrast:

```math
D_A=(m_{P,A}-m_0)-(m_{R,A}-m_0)=m_{P,A}-m_{R,A},
```

```math
D_B=(m_{P,B}-m_{P,A})-(m_{R,B}-m_{R,A}),
\qquad m_{P,B}-m_{R,B}=D_A+D_B.
```

These identities locate the gap along the saved training trajectories.

**Analysis.** Report six final contrasts: E, M_G, F, C, Q and the implicit margin, each as P minus R. Bootstrap families within strata 10,000 times, retaining every variant and all seeds. Average seeds within families before averaging families. For M_G, recompute each seed's eligible-triplet ratio in every draw, then average seeds. Use 99.17% paired intervals: 1 − 0.05/6. Show each seed separately. Intervals describe fresh-family variation conditional on these three training seeds. Stage contrasts remain descriptive.

Each required interval must lie entirely on the stated side of zero:

| Supported pattern | Required signs |
|---|---|
| Readout loss | ΔE < 0 |
| Distance loss among correctly read answers | ΔM_G < 0 |
| Confusion between objects | ΔF > 0 and ΔC < 0 |
| Loss on implied colors | ΔQ > 0 and Δ implicit margin < 0 |

Intervals crossing zero leave the corresponding interpretation unresolved. Several patterns can occur together. Choose a separate training ablation from the supported pattern.

Source: [frozen replication protocol](https://github.com/pvd232/JEP/blob/8bff661ecc58e8df8ede124808c53a3588e26ca4/training_outputs/proposition_full_20261026/replication_protocol.json).
