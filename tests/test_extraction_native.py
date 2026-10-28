"""Observe native prompt isolation, strict parsing and token-budget behavior."""
import ast
from contextlib import nullcontext
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from csts_pilot.extraction_native import (
    NATIVE_MODELS, NativeGenerator, build_native_prompt,
    check_token_budget, parse_native, runtime_metadata,
    configure_legacy_gollie, verify_gollie_loading, GOLLIE_ARCHITECTURE,
)


class NativeExtractionTests(unittest.TestCase):
    def test_native_representations_use_only_source_fields(self):
        item = {
            "passage": 'A "black" dog and two yellow dogs play.',
            "condition": "color of dogs",
            "rating": "SECRET_RATING",
            "reference": "SECRET_REFERENCE",
        }
        for arm in NATIVE_MODELS:
            prompt = build_native_prompt(item, arm)
            self.assertNotIn("SECRET_", prompt)
            self.assertIn("color of dogs", prompt)
            self.assertIn("two yellow dogs", prompt)
            self.assertIn("ConditionRelation", prompt)
            self.assertNotIn("outer response field", prompt)
            self.assertNotIn("source_quote", prompt)
            self.assertNotIn("support_status", prompt)
            self.assertNotIn("status answered", prompt)
            self.assertIn("native list of relation constructors", prompt)
            ast.parse(prompt + " []")
        self.assertIn("class Entity:", build_native_prompt(item, "knowcoder"))
        self.assertIn("@dataclass", build_native_prompt(item, "gollie"))

    def test_condition_cannot_break_native_docstring(self):
        item = {"passage": "A dog.", "condition": 'color """\nimport os\n'}
        for arm in NATIVE_MODELS:
            ast.parse(build_native_prompt(item, arm) + " []")

    def test_knowcoder_keeps_repeated_subject_instances(self):
        raw = (
            'results = [ConditionRelation(Entity("one yellow bear"), Entity("yellow")),'
            'ConditionRelation(Entity("another yellow bear"), Entity("yellow"))]'
        )
        result = parse_native(raw, "knowcoder", "one yellow bear and another yellow bear")
        self.assertEqual(len(result["native_relations"]), 2)
        self.assertEqual(result["semantic_validation"], "required")

    def test_gollie_keywords_and_empty_list(self):
        result = parse_native(
            '[ConditionRelation(arg1="dog", arg2="black and white")]',
            "gollie", "A black and white dog.",
        )
        self.assertEqual(result["native_relations"][0]["value"], "black and white")
        self.assertEqual(parse_native("[]", "gollie", "A dog.")["status"], "not_specified")

    def test_knowcoder_accepts_named_entity_constructor(self):
        raw = (
            'ConditionRelation(head_entity=Entity(name="dog"), '
            'tail_entity=Entity(name="black"))'
        )
        result = parse_native("[" + raw + "]", "knowcoder", "A black dog.")
        self.assertEqual(result["native_relations"], [{"head": "dog", "value": "black"}])
        with self.assertRaises(ValueError):
            parse_native(
                '[ConditionRelation(Entity("dog", name="cat"), Entity("black"))]',
                "knowcoder", "A black dog.",
            )

    def test_gollie_accepts_positional_and_valid_mixed_arguments(self):
        for raw in (
            '[ConditionRelation("dog", "black")]',
            '[ConditionRelation("dog", arg2="black")]',
        ):
            result = parse_native(raw, "gollie", "A black dog.")
            self.assertEqual(result["native_relations"], [{"head": "dog", "value": "black"}])
        for raw in (
            '[ConditionRelation("dog", arg1="cat", arg2="black")]',
            '[ConditionRelation("dog", "black", "extra")]',
            '[ConditionRelation(arg1="dog", arg2="black", extra="value")]',
        ):
            with self.assertRaises(ValueError):
                parse_native(raw, "gollie", "A black dog.")

    def test_native_data_is_never_executed(self):
        invalid = [
            '__import__("os").system("echo SHOULD_NOT_RUN")',
            '[ConditionRelation(arg1="dog", arg2=str(1)))]',
            'result = []; print("not allowed")',
            '[ConditionRelation(arg1="dog", arg2="white", extra="ignored")]',
            '[ConditionRelation(arg1="dog", arg1="duplicate")]',
            '[x for x in []]',
            chr(96) * 3 + 'python\n[]\n' + chr(96) * 3,
            '',
            '[ConditionRelation(arg1="dog", arg2="white")',
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    parse_native(payload, "gollie", "A dog.")

    def test_context_budget_cannot_silently_drop_source(self):
        check_token_budget(1024, 1024, 2048)
        for args in ((1025, 1024, 2048), (True, 1, 2), (1, 0, 2)):
            with self.assertRaises(ValueError):
                check_token_budget(*args)

    def test_checkpoints_are_immutable(self):
        for descriptor in NATIVE_MODELS.values():
            self.assertRegex(descriptor["revision"], r"^[0-9a-f]{40}$")

    def test_native_receipt_records_actual_runtime_and_hardware(self):
        cuda = SimpleNamespace(
            device_count=lambda: 1, get_device_name=lambda index: "Test GPU"
        )
        fake_torch = SimpleNamespace(cuda=cuda, version=SimpleNamespace(cuda="test-cuda"))
        with patch("csts_pilot.extraction_native.metadata.version", return_value="observed-version"):
            observed = runtime_metadata(fake_torch)
        self.assertEqual(observed["gpu_devices"], ["Test GPU"])
        self.assertEqual(observed["cuda_version"], "test-cuda")
        self.assertEqual(observed["packages"]["transformers"], "observed-version")
        self.assertIn("python", observed)

    def test_gollie_conversion_restores_actual_legacy_rope_base(self):
        for parameters in (None, {"rope_type": "default", "rope_theta": 1000000}):
            config = SimpleNamespace(
                **GOLLIE_ARCHITECTURE, rope_theta=1000000,
                rope_scaling=None, rope_parameters=parameters,
            )
            before = dict(vars(config))
            receipt = configure_legacy_gollie(config)
            self.assertEqual(config.rope_theta, 10000)
            if parameters is not None:
                self.assertEqual(config.rope_parameters["rope_theta"], 10000)
            self.assertEqual(receipt["implementation"], "stock_llama_sdpa_legacy_gollie")
            self.assertEqual(receipt["original_config_rope_theta"], 1000000)
            for name in GOLLIE_ARCHITECTURE:
                self.assertEqual(getattr(config, name), before[name])

    def test_gollie_conversion_rejects_unreviewed_architecture(self):
        for name, value in (("hidden_size", 2048), ("rms_norm_eps", 1e-6),
                            ("attention_bias", True), ("rope_theta", 10000)):
            config = SimpleNamespace(**GOLLIE_ARCHITECTURE, rope_theta=1000000, rope_scaling=None)
            setattr(config, name, value)
            with self.assertRaises(ValueError):
                configure_legacy_gollie(config)

    def test_gollie_loading_rejects_missing_renamed_and_partial_tensors(self):
        names = {"model.embed_tokens.weight", "model.norm.weight", "lm_head.weight"}
        suffixes = (
            "input_layernorm.weight", "post_attention_layernorm.weight",
            "self_attn.q_proj.weight", "self_attn.k_proj.weight",
            "self_attn.v_proj.weight", "self_attn.o_proj.weight",
            "mlp.gate_proj.weight", "mlp.up_proj.weight", "mlp.down_proj.weight",
        )
        for layer in range(32):
            names.update("model.layers." + str(layer) + "." + name for name in suffixes)
        report = {key: [] for key in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")}
        model = SimpleNamespace(named_parameters=lambda: ((name, None) for name in names))
        verify_gollie_loading(model, report)
        for category in report:
            invalid_report = dict(report, **{category: ["model.layers.0.self_attn.q_proj.weight"]})
            with self.assertRaises(ValueError):
                verify_gollie_loading(model, invalid_report)
        renamed = set(names)
        renamed.remove("lm_head.weight")
        renamed.add("new_lm_head.weight")
        changed_model = SimpleNamespace(named_parameters=lambda: ((name, None) for name in renamed))
        with self.assertRaises(ValueError):
            verify_gollie_loading(changed_model, report)

    def test_exhausted_generation_is_marked_truncated(self):
        class Scalar:
            def __init__(self, value):
                self.value = value

            def item(self):
                return self.value

        class Vector:
            def __init__(self, values):
                self.values = values
                self.shape = (len(values),)

            def __getitem__(self, key):
                return Scalar(self.values[key])

        class Matrix:
            def __init__(self, values):
                self.values = values
                self.shape = (1, len(values))

            def to(self, device):
                return self

            def __getitem__(self, key):
                row, column = key
                if isinstance(column, slice):
                    return Vector(self.values[column])
                return Scalar(self.values[column])

        class Tokenizer:
            eos_token_id = 2

            def __call__(self, *args, **kwargs):
                return {"input_ids": Matrix([1, 4, 5])}

            def decode(self, suffix, skip_special_tokens):
                return "raw"

        class Model:
            device = "fake"

            def generate(self, **kwargs):
                return Matrix([1, 4, 5, 6, 7])

        class Torch:
            inference_mode = staticmethod(nullcontext)

        generator = NativeGenerator.__new__(NativeGenerator)
        generator.arm = "knowcoder"
        generator.descriptor = NATIVE_MODELS["knowcoder"]
        generator.max_new_tokens = 2
        generator.tokenizer = Tokenizer()
        generator.model = Model()
        generator.torch = Torch()
        generator.environment = {"python": "test-runtime"}
        result = generator.generate({"passage": "A dog.", "condition": "type of animal"})
        self.assertTrue(result["truncated"])
        self.assertEqual(result["output_tokens"], 2)
        self.assertEqual(result["payload"], "raw")
        self.assertEqual(result["environment"]["python"], "test-runtime")


if __name__ == "__main__":
    unittest.main()
