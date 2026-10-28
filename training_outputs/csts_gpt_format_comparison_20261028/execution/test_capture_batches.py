import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import capture_batches as c

class BatchTests(unittest.TestCase):
 def items(self):return [{'id':'a','passage':'A black dog stands.','condition':'color of dog'},{'id':'b','passage':'A white cat sits.','condition':'color of cat'}]
 def payload(self,quote='A black dog'):
  return json.dumps({'status':'answered','reason':'','propositions':[{'text':'The dog is black.','source_quote':quote,'support_status':'explicit','reason':''}]})
 def proof(self,response,warning=None):
  events=[{'type':'thread.started','thread_id':'x'},{'type':'turn.started'}]
  if warning:events.append({'type':'error','message':warning})
  return events+[{'type':'item.completed','item':{'type':'agent_message','text':json.dumps(response)}},{'type':'turn.completed'}]
 def test_envelope_rejects_missing_extra_or_wrong_wrappers(self):
  good={'records':{'a':{'payload':'x'},'b':{'payload':'y'}}}
  self.assertEqual(c.validate_envelope(good,['a','b']),good['records'])
  bad=[{'records':{'a':{'payload':'x'}}},{'records':dict(good['records'],other={'payload':'x'})},{'records':{'a':{'payload':1},'b':{'payload':'x'}}},{'records':{'a':{'payload':'x','extra':0},'b':{'payload':'x'}}},dict(good,extra=0)]
  for value in bad:
   with self.subTest(value=value):
    with self.assertRaises(ValueError):c.validate_envelope(value,['a','b'])
 def test_decoder_rejects_duplicate_keys_and_nonfinite_everywhere(self):
  for text in ['{"records":{"a":{"payload":"x","payload":"y"}}}','{"records":{"a":{"payload":"x"},"a":{"payload":"y"}}}','{"x":NaN}','{"x":Infinity}','{"x":-Infinity}']:
   with self.subTest(text=text):
    with self.assertRaises(ValueError):c.decode(text)
 def test_exact_schema_has_no_extra_keys_at_any_level(self):
  schema=c.envelope_schema(['a','b']);self.assertFalse(schema['additionalProperties'])
  records=schema['properties']['records'];self.assertEqual(records['required'],['a','b']);self.assertFalse(records['additionalProperties'])
  for item in records['properties'].values():self.assertEqual(item['required'],['payload']);self.assertFalse(item['additionalProperties']);self.assertEqual(item['properties']['payload'],{'type':'string'})
 def test_complete_proof_and_narrow_transport_notices(self):
  response={'records':{'a':{'payload':'x'}}}
  for warning in [None,'Reconnecting... 2/5 (exceeded retry limit, last status: 429 Too Many Requests)','Reconnecting... 1/5 (workspace routing discovery timed out)','Reconnecting... 3/5 (stream disconnected before completion: invalid peer certificate: UnknownIssuer)']:
   self.assertEqual(c.completed_batch(self.proof(response,warning),response,['a']),response['records'])
 def test_tools_failed_turn_unknown_error_or_final_mismatch_rejected(self):
  response={'records':{'a':{'payload':'x'}}};base=self.proof(response);cases=[]
  for event in [{'type':'turn.failed'},{'type':'item.completed','item':{'type':'command_execution'}},{'type':'error','message':'not allowed'},{'type':'unknown'}]:
   rows=copy.deepcopy(base);rows.insert(-1,event);cases.append((rows,response))
  rows=copy.deepcopy(base);rows.insert(0,{'type':'thread.started'});cases.append((rows,response))
  rows=copy.deepcopy(base);rows.insert(1,{'type':'turn.started'});cases.append((rows,response))
  rows=copy.deepcopy(base);rows.insert(-1,copy.deepcopy(rows[-2]));cases.append((rows,response))
  cases.extend([(base[:-1],response),(base,{'records':{'a':{'payload':'different'}}}),(base+[{'type':'turn.completed'}],response)])
  for i,(events,answer) in enumerate(cases):
   with self.subTest(case=i):
    with self.assertRaises(ValueError):c.completed_batch(events,answer,['a'])
 def test_final_answer_duplicate_keys_rejected(self):
  response={'records':{'a':{'payload':'x'}}};events=self.proof(response);events[-2]['item']['text']='{"records":{"a":{"payload":"x","payload":"x"}}}'
  with self.assertRaises(ValueError):c.completed_batch(events,response,['a'])
 def test_per_source_failure_preserves_other_valid_output_and_all_ids(self):
  job={'id':'job','arm':'gpt_propositions','batch_id':'batch'}
  records={'a':{'payload':self.payload()},'b':{'payload':self.payload()}}
  rows=c.source_rows(job,self.items(),records)
  self.assertEqual([r['id'] for r in rows],['a','b']);self.assertTrue(rows[0]['valid']);self.assertFalse(rows[1]['valid']);self.assertIsNone(rows[1]['parsed']);self.assertIn('error',rows[1])
 def test_batch_failure_retains_every_id_without_parsed_evidence(self):
  rows=c.source_rows({'id':'job','arm':'gpt_json','batch_id':'batch'},self.items(),error='bad envelope')
  self.assertEqual([r['id'] for r in rows],['a','b']);self.assertTrue(all(not r['valid'] and r['parsed'] is None and r['status']=='invalid' for r in rows))
 def test_invalid_nonfinite_source_payload_retained_as_failure(self):
  rows=c.source_rows({'id':'job','arm':'gpt_json','batch_id':'batch'},self.items(),{'a':{'payload':'{"status":NaN}'},'b':{'payload':'{}'}})
  self.assertFalse(any(r['valid'] for r in rows));self.assertIn('Nonfinite',rows[0]['error'])
 def test_request_contains_only_projected_source_items_and_exact_hashes(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'protocol.json').write_text('{}');(root/'p').write_text('prompt');(root/'s').write_text('{}')
   items={s['id']:s for s in self.items()};job={'id':'job','arm':'gpt_json','batch_id':'batch','source_ids':['a','b'],'prompt_file':'p','schema_file':'s'}
   request=c.build_request(root,job,items)
   self.assertEqual(request['items'],self.items());self.assertEqual(request['prompt_sha256'],hashlib.sha256(b'prompt').hexdigest());self.assertTrue(all(set(i)=={'id','passage','condition'} for i in request['items']))
 def test_actual_prepared_jobs_share_case_order_and_one_policy_per_prompt(self):
  root=Path(__file__).parent
  if not (root/'jobs.json').exists():self.skipTest('Prepared study absent')
  jobs=c.read(root/'jobs.json');by_batch={}
  for job in jobs:
   by_batch.setdefault(job['batch_id'],[]).append(job)
   prompt=(root/job['prompt_file']).read_text()
   self.assertEqual(prompt.count('Extract all information relevant to CONDITION from PASSAGE alone.'),1)
   self.assertEqual(c.read(root/job['schema_file']),c.envelope_schema(job['source_ids']))
  for values in by_batch.values():
   self.assertEqual({v['arm'] for v in values},set(c.ARMS));self.assertTrue(all(v['source_ids']==values[0]['source_ids'] for v in values))

if __name__=='__main__':unittest.main()
