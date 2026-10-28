import copy
import json
from pathlib import Path
import tempfile
import unittest

from csts_pilot.native_adapter.cli import export_record,main,normalize_record
from csts_pilot.native_adapter.runtime import descriptor,bind_runtime


def record(**overrides):
    value={'source_id':'dev-one','condition':'color of dog','passage':'A brown dog runs.','model':'gollie','raw_output':"[HasColor(object='brown dog',color='brown')]"}
    return {**value,**overrides}


class ExportTest(unittest.TestCase):
    def test_base_and_ie_are_separately_pinned_not_silent_replacements(self):
        base=descriptor('knowcoder_base');ie=descriptor('knowcoder_ie')
        self.assertNotEqual(base['model_id'],ie['model_id'])
        self.assertNotEqual(base['revision'],ie['revision'])
        self.assertEqual(base['grammar'],ie['grammar'])
        receipt={**ie,'tensor_load_verified':True,'backend':'transformers-compatibility','dtype':'float16','tokenizer_files_sha256':{'tokenizer.json':'a'*64},'software_versions':{'transformers':'4.57.6'}}
        self.assertEqual(bind_runtime('knowcoder_ie',receipt)['model'],ie)
        with self.assertRaisesRegex(ValueError,'checkpoint differs'):bind_runtime('knowcoder_base',receipt)
        receipt['tensor_load_verified']=False
        with self.assertRaisesRegex(ValueError,'Actual tensor'):bind_runtime('knowcoder_ie',receipt)
    def test_native_bindings_reach_common_text_and_no_execution_proof_is_invented(self):
        output=export_record(normalize_record(record()))
        self.assertIn('[e0] color [e1].',output['canonical_evidence'])
        self.assertNotIn('HasColor',output['canonical_evidence'])
        self.assertFalse(output['external_protocol_verified'])
        self.assertFalse(output['semantic_support_validated'])
        self.assertFalse(output['route_production_approved'])

    def test_unresolved_model_binding_is_not_exported_as_intrinsic_source_ambiguity(self):
        raw=record(condition='type of animal',passage='a dog runs; a dog sits.',raw_output="[Animal(span='a dog')]")
        output=export_record(normalize_record(raw))
        self.assertEqual(output['candidate_grounding_status'],'ambiguous')
        self.assertIn('candidate_entity_binding_unresolved',output['ambiguity_origins'])
        self.assertIn('unresolved source-span binding',output['canonical_evidence'])
        self.assertNotIn('Requested facet: ambiguous',output['canonical_evidence'])

    def test_operational_parse_and_unsupported_failures_retain_denominators(self):
        for raw in (record(runtime_status='truncated'),record(raw_output='broken['),record(condition='sequence of events')):
            with self.subTest(raw=raw):
                result=normalize_record(raw);output=export_record(result)
                self.assertEqual(output['source_id'],'dev-one')
                self.assertIsNone(output['canonical_evidence'])
                self.assertFalse(output['parse_valid'])
                self.assertTrue(result['raw_capture'])

    def test_mutated_parsed_output_is_rejected_by_reconstruction(self):
        result=normalize_record(record());result['normalized_evidence']['relations'][0]['predicate']='owns'
        with self.assertRaisesRegex(ValueError,'identity changed'):export_record(result)

    def test_offline_cli_normalize_then_export_is_runnable_without_models(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw=root/'raw.json';normalized=root/'normalized.json';exported=root/'common.jsonl'
            raw.write_text(json.dumps([record(),record(source_id='failed',runtime_status='error')]))
            main(['normalize','--input',str(raw),'--output',str(normalized)])
            main(['export','--input',str(normalized),'--output',str(exported)])
            rows=[json.loads(line) for line in exported.read_text().splitlines()]
            self.assertEqual(len(rows),2)
            self.assertIsNone(rows[1]['canonical_evidence'])
            with self.assertRaises(FileExistsError):main(['export','--input',str(normalized),'--output',str(exported)])

    def test_observed_context_is_exported_while_hobby_remains_unstated(self):
        raw=record(condition='type of hobby',passage='A woman plays tennis.',model='knowcoder',stage_outputs={'observed_activity':"[ActivityEvent(trigger='plays',actor=[Entity('A woman')],theme=[Entity('tennis')],place=[])]",'explicit_hobby':'[]'})
        del raw['raw_output']
        output=export_record(normalize_record(raw))
        self.assertEqual(output['status'],'not_specified')
        self.assertIn('Context: activity: plays',output['canonical_evidence'])
        self.assertIn('Requested facet: not specified.',output['canonical_evidence'])


if __name__=='__main__':unittest.main()
