"""Check cached decoding, stop tokens, token ceilings and inference resume guards."""

from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import numpy as np

SPEC = importlib.util.spec_from_file_location("run_inference", Path(__file__).with_name("run_inference.py"))
run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run)


class Tensor(np.ndarray):
    def __new__(cls, value, dtype=None):
        return np.asarray(value, dtype=dtype).view(cls)

    def to(self, *args, **kwargs):
        return self

    def float(self):
        return Tensor(self, np.float32)

    def norm(self, dim, keepdim):
        return Tensor(np.linalg.norm(self, axis=dim, keepdims=keepdim))

    def cpu(self):
        return self

    def numpy(self):
        return np.asarray(self)

    def argmax(self, dim=None, **kwargs):
        return Tensor(np.asarray(self).argmax(axis=dim, **kwargs))

    def unsqueeze(self, dim):
        return Tensor(np.expand_dims(self, dim))


class FakeTorch:
    bfloat16 = "bfloat16"
    long = np.int64
    inference_mode = staticmethod(nullcontext)
    autocast = staticmethod(lambda *a, **kw: nullcontext())
    isfinite = staticmethod(lambda x: Tensor(np.isfinite(x)))
    arange = staticmethod(lambda n, **kw: Tensor(np.arange(n)))
    full = staticmethod(lambda shape, value, dtype, **kw: Tensor(np.full(shape, value, dtype=dtype)))
    ones = staticmethod(lambda shape, dtype, **kw: Tensor(np.ones(shape, dtype=dtype)))
    cat = staticmethod(lambda arrays, dim: Tensor(np.concatenate(arrays, axis=dim)))


class Tokenizer:
    def pad(self, value, **kwargs):
        width = max(map(len, value["input_ids"]))
        return dict(input_ids=Tensor([[0]*(width-len(s))+s for s in value["input_ids"]]),
                    attention_mask=Tensor([[0]*(width-len(s))+s for s in value["attention_mask"]]))

    def decode(self, value, skip_special_tokens):
        return " ".join(str(x) for x in value if x != 2)


class Model:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def __call__(self, input_ids, attention_mask, position_ids, use_cache, return_dict, past_key_values=None):
        width = 0 if past_key_values is None else past_key_values["width"]
        expected_positions = np.arange(width, width+input_ids.shape[1])[None, :]
        np.testing.assert_array_equal(position_ids, expected_positions)
        assert attention_mask.shape[1] == width+input_ids.shape[1]
        assert use_cache and return_dict
        self.calls.append(dict(input_ids=np.asarray(input_ids).copy(), mask=np.asarray(attention_mask).copy()))
        step = len(self.calls)-1
        next_ids = [row[min(step, len(row)-1)] for row in self.outputs]
        hidden = np.zeros((*input_ids.shape,run.WIDTH),np.float32)
        hidden[:, -1, 0] = next_ids
        hidden[:, -1, 1] = 1
        return SimpleNamespace(last_hidden_state=Tensor(hidden),
                               past_key_values={"width":width+input_ids.shape[1]})


def head(raw):
    result = np.zeros((len(raw), 12))
    result[np.arange(len(raw)), np.asarray(raw[:,0],dtype=int)] = 1
    return Tensor(result)


class InferenceContractTests(unittest.TestCase):
    def test_cached_positions_left_padding_and_stopping(self):
        model = Model([[9,2,11],[5,8,2]])
        predictions,z = run.generate_batch(model,head,Tokenizer(),[[6,2],[7,8,2]],{2},FakeTorch)
        self.assertEqual([x["generated_token_ids"] for x in predictions],[[9,2],[5,8,2]])
        self.assertTrue(all(x["stopped_on_eos"] for x in predictions))
        self.assertEqual([x["answer"] for x in predictions],["9","5 8"])
        self.assertEqual(len(model.calls),3)
        np.testing.assert_array_equal(model.calls[0]["mask"],[[0,1,1],[1,1,1]])
        np.testing.assert_array_equal(model.calls[1]["input_ids"],[[9],[5]])
        run.validate_arrays(["a","b"],z,["a","b"])

    def test_token_ceiling_stops_cached_forward(self):
        model = Model([[9],[5]])
        predictions,_ = run.generate_batch(model,head,Tokenizer(),[[6,2],[7,2]],{2},FakeTorch,max_tokens=2)
        self.assertEqual([x["generated_tokens"] for x in predictions],[2,2])
        self.assertFalse(any(x["stopped_on_eos"] for x in predictions))
        self.assertEqual(len(model.calls),2)

    def test_resume_requires_identity_hashes_and_order(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            z=np.zeros((2,run.WIDTH),np.float32);z[:,0]=1
            predictions=[dict(id="a",answer="red"),dict(id="b",answer="blue")]
            run.write_saved(path,predictions,z,dict(status="batch_complete",contract_sha256="contract",state_sha256="state"))
            self.assertIsNotNone(run.read_saved(path,["a","b"],"contract","state"))
            with self.assertRaisesRegex(ValueError,"different frozen run"):
                run.read_saved(path,["a","b"],"changed","state")
            with self.assertRaisesRegex(ValueError,"input order"):
                run.read_saved(path,["b","a"],"contract","state")
            (path/"predictions.json").write_text("[]")
            with self.assertRaisesRegex(ValueError,"bytes differ"):
                run.read_saved(path,["a","b"],"contract","state")

    def test_unit_norm_and_finite_guards(self):
        z=np.zeros((1,run.WIDTH),np.float32)
        with self.assertRaisesRegex(ValueError,"unit norms"):
            run.validate_arrays(["a"],z,["a"])
        z[:,0]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite values"):
            run.validate_arrays(["a"],z,["a"])

    def test_human_review_gate(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"probe.json"
            path.write_text(json.dumps(dict(inputs=[dict(id="a",caption="A red cup.",condition="color")],human_review="pending")))
            with self.assertRaisesRegex(ValueError,"Human review is pending"):
                run.validated_probe(path,False)
            self.assertEqual(run.validated_probe(path,True)["human_review"],"pending")

    def test_prefix_ceiling_includes_eod(self):
        class Tokens:
            n=159
            def __call__(self,*a,**kw):
                assert kw==dict(padding=False,truncation=False,add_special_tokens=False)
                return dict(input_ids=[[1]*self.n])
            def get_vocab(self):
                return {run.EOD:2}
        tok=Tokens()
        rows=[dict(condition="color",caption="A cup.")]
        self.assertEqual(len(run.token_sequences(tok,rows)[0]),160)
        tok.n=160
        with self.assertRaisesRegex(ValueError,"160-token"):
            run.token_sequences(tok,rows)


if __name__ == "__main__":
    unittest.main()
