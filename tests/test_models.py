"""The shared JSON is data; examples remain direct REST clients."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SharedModelsTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'models.json').read_text())
        self.ids = [model for group in self.config['allowed_models'].values() for model in group]

    def run_example(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT / 'examples' / name), *args], capture_output=True, text=True)

    def test_explicit_unique_ids(self):
        self.assertEqual(len(self.ids), len(set(self.ids)))
        self.assertTrue(all('/' in model and '*' not in model and ':' not in model for model in self.ids))
        self.assertNotIn('openrouter/auto', self.ids)

    def test_previews_share_defaults(self):
        sync = self.run_example('request.py','--model',self.ids[0],'--provider','example-provider')
        batch = self.run_example('batch.py','--model',self.ids[0])
        self.assertEqual(sync.returncode,0,sync.stderr)
        self.assertEqual(batch.returncode,0,batch.stderr)
        sync_body, batch_body = json.loads(sync.stdout), json.loads(batch.stdout)
        self.assertEqual(sync_body['max_tokens'],self.config['request_defaults']['max_tokens'])
        self.assertEqual(batch_body['requests'][0]['body']['max_tokens'],sync_body['max_tokens'])
        self.assertFalse(sync_body['provider']['allow_fallbacks'])
        self.assertEqual(sync_body['provider']['data_collection'],'deny')
        self.assertEqual(list(batch_body)[:3],['endpoint','model','requests'])

    def test_unknown_model_rejected_before_send(self):
        for name, extra in [('request.py',['--provider','example-provider']),('batch.py',['--verified-support'])]:
            result = self.run_example(name,'--model','not-allowed/model','--send',*extra)
            self.assertEqual(result.returncode,2)
            self.assertIn('Model is not in models.json',result.stderr)

if __name__ == '__main__': unittest.main()
