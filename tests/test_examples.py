"""Check the example request flows without network access."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class ExampleTests(unittest.TestCase):
    def run_example(self, name, *args, key='test-key'):
        output = io.StringIO()
        with patch.object(sys, 'argv', [name, *args]), patch.dict(os.environ, {'OPENROUTER_API_KEY': key}), patch('urllib.request.urlopen') as call, redirect_stdout(output):
            call.return_value = io.BytesIO(b'{"id": "test-result"}')
            runpy.run_path(str(ROOT / 'examples' / name), run_name='__main__')
        return json.loads(output.getvalue()), call

    def test_previews_do_not_send(self):
        for name in ['request.py', 'batch.py']:
            with self.subTest(name=name):
                body, call = self.run_example(name, '--model', 'example/model', key='')
                self.assertEqual(body['model'], 'example/model')
                call.assert_not_called()

    def test_default_route_and_optional_provider(self):
        for extra, expected in [([], {'data_collection': 'deny'}), (['--provider', 'example-provider'], {'data_collection': 'deny', 'order': ['example-provider'], 'allow_fallbacks': False})]:
            with self.subTest(extra=extra):
                _, call = self.run_example('request.py', '--model', 'example/model', '--send', *extra)
                call.assert_called_once()
                req = call.call_args.args[0]
                self.assertEqual(req.get_method(), 'POST')
                self.assertEqual(json.loads(req.data)['provider'], expected)

    def test_batch_submission(self):
        result, call = self.run_example('batch.py', '--model', 'example/model', '--send')
        call.assert_called_once()
        req = call.call_args.args[0]
        self.assertEqual(req.get_method(), 'POST')
        self.assertEqual(json.loads(req.data)['model'], 'example/model')
        self.assertEqual(result['id'], 'test-result')

    def test_batch_get_needs_only_id(self):
        _, call = self.run_example('batch.py', '--get', 'batch/id?x=1')
        call.assert_called_once()
        req = call.call_args.args[0]
        self.assertEqual(req.get_method(), 'GET')
        self.assertIsNone(req.data)
        self.assertTrue(req.full_url.endswith('/batch%2Fid%3Fx%3D1'))

if __name__ == '__main__':
    unittest.main()
