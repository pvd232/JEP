"""Verify diagnostic contrasts using constructed answers and unit vectors."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import analyze_diagnostics as analysis
import probe


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.probe=probe.build()
        self.ids=[x["id"] for x in self.probe["inputs"]]
        self.items={x["id"]:x for x in self.probe["inputs"]}
        colors=sorted(set(c for x in self.probe["inputs"] for c in x["pragmatic_colors"]))
        self.color_index={c:i for i,c in enumerate(colors)}
        self.dimension=len(colors)+1
        self.predictions=[dict(id=x["id"],answer=" and ".join(x["literal_colors"]) if x["literal_colors"] else "not specified",
                               generated_tokens=4,stopped_on_eos=True) for x in self.probe["inputs"]]
        self.z=np.stack([self.color_vector(x["pragmatic_colors"]) for x in self.probe["inputs"]])

    def color_vector(self,colors):
        x=np.zeros(self.dimension)
        for c in colors:
            x[self.color_index[c]]=1
        if not colors:
            x[-1]=1
        return x/np.linalg.norm(x)

    def state(self,z=None,predictions=None):
        return analysis.state_from_arrays(self.probe,self.predictions if predictions is None else predictions,
                                          self.ids,self.z if z is None else z)

    def all_states(self):
        # Sharing immutable synthetic states also tests that analysis preserves input state.
        state=self.state()
        return {name:state for name in analysis.STATE_NAMES}

    def test_equal_arms_have_exact_zero_paired_intervals(self):
        results=analysis.contrasts(self.probe,self.all_states(),draws=250,seed=44)
        for metric in analysis.METRICS:
            self.assertEqual(results["contrasts"][metric]["estimate"],0)
            self.assertEqual(results["contrasts"][metric]["interval"],[0,0])
        self.assertFalse(any(results["patterns"].values()))
        self.assertTrue(results["contrasts"]["M_G"]["geometry_threshold_met"])
        self.assertEqual(results["gate"]["7"]["eligible_triplets"],240)

    def test_geometry_loss_retains_correct_readouts(self):
        z=self.z.copy()
        primary={f["id"] for f in self.probe["families"] if f["stratum"] in ("explicit","multiple")}
        for i,item in enumerate(self.probe["inputs"]):
            if item["family"] in primary:
                z[i]=self.color_vector([])
        states=self.all_states()
        for k in analysis.SEEDS:
            states[f"seed{k}_P_B"]=self.state(z)
        results=analysis.contrasts(self.probe,states,draws=250,seed=10)
        self.assertEqual(results["contrasts"]["E"]["estimate"],0)
        self.assertTrue(results["patterns"]["distance_loss_among_correct_readouts"])
        self.assertLess(results["contrasts"]["M_G"]["interval"][1],0)
        for row in results["stage_accounting"].values():
            self.assertAlmostEqual(row["D_A"]+row["D_B"],row["final_gap"])

    def test_wrong_object_readout_and_condition_swap(self):
        predictions=copy.deepcopy(self.predictions)
        z=self.z.copy()
        for i,item in enumerate(self.probe["inputs"]):
            if item["distractor_colors"]:
                predictions[i]["answer"]=" and ".join(item["distractor_colors"])
                z[i]=self.color_vector(item["distractor_colors"])
        states=self.all_states()
        for k in analysis.SEEDS:
            states[f"seed{k}_P_B"]=self.state(z,predictions)
        results=analysis.contrasts(self.probe,states,draws=250,seed=13)
        self.assertEqual(results["contrasts"]["F"]["estimate"],1)
        self.assertLess(results["contrasts"]["C"]["interval"][1],0)
        self.assertEqual(results["contrasts"]["E"]["estimate"],-0.5)
        self.assertTrue(results["patterns"]["object_confusion"])

    def test_condition_independent_similarity_cancels(self):
        z=self.z.copy()
        for i,item in enumerate(self.probe["inputs"]):
            if item["distractor_colors"]:
                z[i]=self.color_vector(item["literal_colors"]+item["distractor_colors"])
        state=self.state(z)
        self.assertAlmostEqual(state["summary"]["C"],0)
        for row in state["families"].values():
            if row["stratum"]=="multiple":
                self.assertAlmostEqual(row["target_condition_margin"]+row["distractor_condition_margin"],0)

    def test_implied_interaction_requires_both_interval_signs(self):
        z=self.z.copy()
        implicit={f["implicit"] for f in self.probe["families"] if f["stratum"]=="implied"}
        for i,uid in enumerate(self.ids):
            if uid in implicit:
                z[i]=self.color_vector([])
        states=self.all_states()
        for k in analysis.SEEDS:
            states[f"seed{k}_P_B"]=self.state(z)
        results=analysis.contrasts(self.probe,states,draws=250,seed=17)
        self.assertTrue(results["patterns"]["implied_color_loss"])
        for k in analysis.SEEDS:
            p=states[f"seed{k}_P_B"]["summary"]
            r=states[f"seed{k}_R_B"]["summary"]
            self.assertAlmostEqual(p["Q"]-r["Q"],(p["explicit_margin"]-r["explicit_margin"])-
                                   (p["implicit_margin"]-r["implicit_margin"]))

    def test_gated_ratio_weights_triplets_then_seeds(self):
        sums=np.array([[1,0],[0,0]])
        counts=np.array([[1,3],[3,0]])
        value=analysis.gated_ratio_mean(sums.sum(axis=1),counts.sum(axis=1))
        self.assertEqual(value,0.125)
        self.assertNotEqual(value,sums.sum()/counts.sum())

    def test_geometry_gate_rejects_small_represented_set(self):
        predictions=copy.deepcopy(self.predictions)
        allowed={f["id"] for f in self.probe["families"] if f["stratum"]=="explicit"}
        allowed=set(sorted(allowed)[:3])
        for i,item in enumerate(self.probe["inputs"]):
            if item["family"] not in allowed:
                predictions[i]["answer"]="unrecognized output"
        states=self.all_states()
        for k in analysis.SEEDS:
            states[f"seed{k}_P_B"]=self.state(predictions=predictions)
        results=analysis.contrasts(self.probe,states,draws=250,seed=91)
        self.assertFalse(results["contrasts"]["M_G"]["geometry_threshold_met"])
        self.assertFalse(results["patterns"]["distance_loss_among_correct_readouts"])
        self.assertEqual(results["gate"]["7"]["represented_families"],3)

    def test_rejects_missing_and_corrupt_output(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            (directory/"receipt.json").write_text(json.dumps(dict(status="complete",probe_sha256="probe",
                                                                 predictions_sha256="wrong")))
            (directory/"predictions.json").write_text(json.dumps(self.predictions))
            np.savez(directory/"embeddings.npz",ids=self.ids,z=self.z)
            with self.assertRaisesRegex(ValueError,"Output digest differs"):
                analysis.load_state(self.probe,"probe",directory)
        with self.assertRaisesRegex(ValueError,"unit length"):
            self.state(self.z*2)
        with self.assertRaisesRegex(ValueError,"Prediction IDs differ"):
            self.state(predictions=self.predictions[:-1])

    def test_distance_margin_identity(self):
        rng=np.random.default_rng(34)
        x=rng.normal(size=(100,3,16))
        x=x/np.linalg.norm(x,axis=-1,keepdims=True)
        dot_margin=np.sum(x[:,0]*x[:,1],axis=1)-np.sum(x[:,0]*x[:,2],axis=1)
        distance_margin=(np.sum((x[:,0]-x[:,2])**2,axis=1)-np.sum((x[:,0]-x[:,1])**2,axis=1))/2
        np.testing.assert_allclose(dot_margin,distance_margin,atol=1e-14)


if __name__ == "__main__":
    unittest.main()
