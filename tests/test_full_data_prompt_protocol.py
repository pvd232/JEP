"""CPU-only structural/protocol checks; not independent-agent or GPU validation."""
import ast
import copy
import json
from pathlib import Path
import unittest

from csts_pilot.full_data_prompt_protocol import (
    PROMPTS, REVIEW_ROLES, digest_object, render_prompt, require_complete_selections,
    require_launch_approval, trial_matrix, validate_protocol,
)
from csts_pilot.full_data_prompt_native import fit_arguments, next_epoch_from_trace

ROOT = Path(__file__).resolve().parents[1]


class FullDataPromptTests(unittest.TestCase):
    """Verify protocol invariants without downloading models or opening test data."""

    def setUp(self):
        self.p = json.loads((ROOT / 'configs/csts-full-data-prompt-20261107.json').read_text())

    def test_registered_protocol(self):
        validate_protocol(self.p)

    def test_exactly_fifteen_unique_trials(self):
        rows = trial_matrix(self.p)
        self.assertEqual(len(rows), 15)
        self.assertEqual(len({r['trial_id'] for r in rows}), 15)

    def test_three_arms_for_each_seed(self):
        for seed in self.p['seeds']:
            self.assertEqual({r['arm'] for r in trial_matrix(self.p) if r['seed'] == seed}, set(PROMPTS))

    def test_full_data_from_first_update(self):
        for r in trial_matrix(self.p):
            self.assertEqual(r['training_rows'], 6051)
            self.assertEqual(r['subset_phase_epochs'], 0)
            self.assertTrue(r['fresh_initialization'])
            self.assertFalse(r['evidence_loss'])

    def test_A_text(self):
        self.assertEqual(render_prompt('A_condition_first', 'red car', 'colour'),
            'Instruct: Represent the passage for semantic similarity with respect to this condition: colour\nQuery: red car')

    def test_B_only_reverses_the_two_A_blocks(self):
        a = render_prompt('A_condition_first', 'red car', 'colour')
        b = render_prompt('B_order_only', 'red car', 'colour')
        self.assertEqual(a.splitlines()[::-1], b.splitlines())

    def test_C_condition_is_query_target(self):
        c = render_prompt('C_case_inspired', 'red car', 'colour')
        self.assertTrue(c.endswith('Query: colour'))
        self.assertIn('given the Sentence: red car', c)

    def test_data_braces_are_literal(self):
        self.assertIn('{literal}', render_prompt('C_case_inspired', '{literal}', 'colour'))

    def test_unknown_arm_rejected(self):
        with self.assertRaises(ValueError):
            render_prompt('new', 'a', 'b')

    def test_empty_fields_rejected(self):
        for args in [('A_condition_first', '', 'x'), ('B_order_only', 'x', ' '), ('C_case_inspired', None, 'x')]:
            with self.assertRaises(ValueError):
                render_prompt(*args)

    def test_no_embedded_manual_eod(self):
        self.assertTrue(all('<|endoftext|>' not in s for s in PROMPTS.values()))

    def test_seed_block_pairing(self):
        rows = trial_matrix(self.p)
        for seed in self.p['seeds']:
            self.assertEqual({r['hardware_block'] for r in rows if r['seed'] == seed}, {f'seed{seed}'})

    def test_arm_order_counterbalanced(self):
        rows = trial_matrix(self.p)
        self.assertEqual([rows[i]['arm'] for i in (0, 3, 6)], list(PROMPTS))

    def test_no_subset_training_config(self):
        p = copy.deepcopy(self.p)
        p['training']['subset_phase_epochs'] = 5
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_no_optimizer_reset_config(self):
        p = copy.deepcopy(self.p)
        p['training']['optimizer_resets'] = 1
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_wrong_gpu_project_rejected(self):
        p = copy.deepcopy(self.p)
        p['execution']['gcp_project'] = 'pvd-dev-232'
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_extra_gpu_rejected(self):
        p = copy.deepcopy(self.p)
        p['execution']['max_gcp_gpus'] = 3
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_changed_split_rejected(self):
        p = copy.deepcopy(self.p)
        p['splits']['test']['rows'] = 2431
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_changed_seed_set_rejected(self):
        p = copy.deepcopy(self.p)
        p['seeds'] = [7]
        with self.assertRaises(ValueError):
            validate_protocol(p)

    def test_fit_configuration_all_arms(self):
        for arm in PROMPTS:
            c = fit_arguments(self.p, arm, 7)
            self.assertEqual(c['prompt_template'], PROMPTS[arm])
            self.assertEqual(c['start_epoch'], 0)
            self.assertEqual(c['max_epochs'], 1)
            self.assertEqual(c['learning_rate'], 2e-5)
            self.assertEqual((c['batch_size'], c['microbatch_size']), (32, 32))
            self.assertEqual(c['patience'], 1)
            self.assertFalse(c['train_until_patience'])

    def test_continuation_does_not_change_semantics(self):
        a = fit_arguments(self.p, 'A_condition_first', 8)
        b = fit_arguments(self.p, 'A_condition_first', 8, 3)
        changed = {k for k in a if a[k] != b[k]}
        self.assertEqual(changed, {'start_epoch', 'max_epochs'})

    def test_sealed_epoch_counter(self):
        trace = {'status': 'complete', 'stop_reason': 'epoch_budget',
                 'epochs': [{'epoch':1}, {'epoch':2}], 'actual_updates': 380}
        self.assertEqual(next_epoch_from_trace(trace), 2)

    def test_wrong_subset_update_count_rejected(self):
        trace = {'status': 'complete', 'stop_reason': 'epoch_budget',
                 'epochs': [{'epoch':1}], 'actual_updates': 184}
        with self.assertRaises(ValueError):
            next_epoch_from_trace(trace)

    def test_partial_or_exhausted_parent_rejected(self):
        for state, reason in [('running', 'epoch_budget'), ('complete', 'validation_patience')]:
            with self.assertRaises(ValueError):
                next_epoch_from_trace({'status':state,'stop_reason':reason,'epochs':[{'epoch':1}],'actual_updates':190})

    def test_censored_epoch_cap_rejected(self):
        with self.assertRaises(ValueError):
            fit_arguments(self.p, 'A_condition_first', 7, 24)

    def test_default_no_user_execution_permission(self):
        self.assertFalse(self.p['user_execution_approved'])
        with self.assertRaises(PermissionError):
            require_launch_approval(self.p, 'abc', {}, [])

    def test_missing_independent_review_blocks(self):
        approval = {'user_execution_approved':True, 'source_commit':'abc', 'protocol_sha256':digest_object(self.p)}
        with self.assertRaises(PermissionError):
            require_launch_approval(self.p, 'abc', approval, [])

    def test_ten_reused_provider_ids_not_independent(self):
        approval = {'user_execution_approved':True, 'source_commit':'abc', 'protocol_sha256':digest_object(self.p)}
        synthetic = [{'role':r, 'provider_run_id':'SYNTHETIC_TEST_ONLY_DUPLICATE', 'status':'approved',
                      'source_commit':'abc','protocol_sha256':digest_object(self.p)} for r in REVIEW_ROLES]
        with self.assertRaises(PermissionError):
            require_launch_approval(self.p,'abc',approval,synthetic)

    def test_wrong_review_revision_blocks(self):
        approval = {'user_execution_approved':True,'source_commit':'different','protocol_sha256':digest_object(self.p)}
        with self.assertRaises(PermissionError):
            require_launch_approval(self.p,'abc',approval,[])

    def selections(self):
        return [{'trial_id':r['trial_id'],'selection_metric':'validation_spearman','test_used':False,
                 'stop_reason':'validation_patience','model_sha256':'a'*64,
                 'training_source_commit':'b'*40,'protocol_sha256':digest_object(self.p)} for r in trial_matrix(self.p)]

    def test_selection_matrix_can_freeze(self):
        require_complete_selections(self.p,self.selections())

    def test_partial_matrix_cannot_open_test(self):
        with self.assertRaises(ValueError):
            require_complete_selections(self.p,self.selections()[:-1])

    def test_censored_fit_cannot_open_test(self):
        s = self.selections(); s[0]['stop_reason']='epoch_budget'
        with self.assertRaises(ValueError):
            require_complete_selections(self.p,s)

    def test_test_selected_fit_rejected(self):
        s = self.selections(); s[0]['test_used']=True
        with self.assertRaises(ValueError):
            require_complete_selections(self.p,s)

    def test_invalid_model_digest_rejected(self):
        s = self.selections(); s[0]['model_sha256']='z'*64
        with self.assertRaises(ValueError):
            require_complete_selections(self.p,s)

    def test_native_source_bindings_do_not_duplicate_roles(self):
        tree = ast.parse((ROOT/'csts_pilot/full_data_prompt_native.py').read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='input':
                keys={k.arg for k in node.keywords}
                self.assertFalse('source' in keys and ('data_role' in keys or 'path' in keys))

    def test_prompt_is_bound_in_config_and_encoder_metadata(self):
        text=(ROOT/'csts_pilot/baseline_models.py').read_text()
        self.assertIn('prompt_template: str | None',text)
        self.assertEqual(text.count('config.prompt_template if config.prompt_template is not None else PROMPT'),2)

    def test_selections_must_bind_same_source(self):
        s = self.selections(); s[0]['training_source_commit'] = 'c'*40
        with self.assertRaises(ValueError):
            require_complete_selections(self.p, s)

    def test_selections_must_bind_full_data_protocol(self):
        s = self.selections(); s[0]['protocol_sha256'] = 'd'*64
        with self.assertRaises(ValueError):
            require_complete_selections(self.p, s)

    def test_builder_cannot_execute_or_provision(self):
        text=(ROOT/'csts_pilot/full_data_prompt_native.py').read_text()
        self.assertNotIn('execution.run(',text)
        self.assertNotIn('gcloud',text)
        self.assertNotIn('proposition_final.pt',text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
