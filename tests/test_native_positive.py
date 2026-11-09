"""Public frozen-provider entrypoint checks; no native or judge calls."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from csts_pilot import native_positive


class NativePositiveEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.provider=self.root/'provider';self.provider.mkdir();self.job=self.root/'job';self.job.mkdir()
        self.driver=self.provider/'evaluate_native.py';self.driver.write_text('raise RuntimeError("must not execute during byte verification")\n')
        digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
        self.manifest=self.provider/'support-seal.json';self.manifest.write_text(json.dumps({'files':{'evaluate_native.py':digest(self.driver)}}))
        self.protocol=self.job/'protocol.json';self.protocol.write_text(json.dumps({'capture_driver_sha256':digest(self.driver),
            'models':{'knowcoder':{'native_capture':{'support_manifest_sha256':digest(self.manifest)}}}}))

    def tearDown(self):self.temp.cleanup()

    def test_verification_reads_bytes_without_executing_driver(self):
        self.assertEqual(native_positive.verify_provider_files(self.provider,self.protocol),self.driver.resolve())

    def test_changed_driver_is_rejected_before_execution(self):
        self.driver.write_text('changed')
        with self.assertRaises(ValueError):native_positive.verify_provider_files(self.provider,self.protocol)

    def test_helper_escape_is_rejected(self):
        outside=self.root/'outside.py';outside.write_text('changed')
        manifest=json.loads(self.manifest.read_text());manifest['files']['../outside.py']=hashlib.sha256(outside.read_bytes()).hexdigest();self.manifest.write_text(json.dumps(manifest))
        protocol=json.loads(self.protocol.read_text());protocol['models']['knowcoder']['native_capture']['support_manifest_sha256']=hashlib.sha256(self.manifest.read_bytes()).hexdigest();self.protocol.write_text(json.dumps(protocol))
        with self.assertRaises(ValueError):native_positive.verify_provider_files(self.provider,self.protocol)

    def test_capture_uses_structured_subprocess_arguments(self):
        output=self.root/'capture'
        with patch.object(native_positive.subprocess,'run')as run:
            run.return_value.returncode=0
            status=native_positive.main(['--provider',str(self.provider),'capture','--job',str(self.job),'--model','knowcoder','--output',str(output),'--python','native-python'])
        self.assertEqual(status,0)
        self.assertEqual(run.call_args.args[0],['native-python',str(self.driver.resolve()),'run-capture','--job',str(self.job),'--model','knowcoder','--output',str(output)])


if __name__=='__main__':unittest.main()
