"""Counterexamples for staged cohort enforcement, independent of model libraries."""
import copy,json,tempfile,unittest
from pathlib import Path
from csts_pilot.full_data_prompt_protocol import digest_file
from csts_pilot.full_data_prompt_integrity import verify_staged_fit_inputs

class StagedCohortTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.rows={s:[{'row_id':s,'group_id':s,'rating':3,'target':.5}] for s in ('training','validation')}
        self.inputs={s:self.root/f'{s}.json' for s in self.rows}
        self.contract={}
        self.write()
    def write(self):
        for s,rows in self.rows.items():
            self.inputs[s].write_text(json.dumps(rows))
            self.contract[s]={'sha256':digest_file(self.inputs[s]),'rows':len(rows),'groups':len({r['group_id'] for r in rows})}
    def test_exact_cohort_passes(self):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_mutated_bytes_fail(self):
        self.inputs['training'].write_text('[]')
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_wrong_row_count_fails(self):
        self.contract['training']['rows']=2
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_wrong_group_count_fails(self):
        self.contract['training']['groups']=2
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_overlap_fails_even_when_hashes_match(self):
        self.rows['validation'][0]['group_id']='training';self.write()
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_duplicate_rows_fail(self):
        self.rows['training']*=2;self.write()
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_nan_rating_fails(self):
        self.rows['training'][0]['rating']=float('nan');self.write()
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_infinite_rating_fails(self):
        self.rows['training'][0]['rating']=float('inf');self.write()
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_bad_normalization_fails(self):
        self.rows['training'][0]['target']=.75;self.write()
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)
    def test_cannot_add_test_to_training_contract(self):
        self.contract['test']={}
        with self.assertRaises(ValueError):verify_staged_fit_inputs(self.inputs,self.contract)

if __name__=='__main__':unittest.main()
