"""Exercise example CLI behavior with all network access mocked."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]

class ExampleTests(unittest.TestCase):
    def run_example(self, name, *args, response=None, error=None, key='test-secret'):
        out, err = io.StringIO(), io.StringIO()
        payload = json.dumps(response if response is not None else {'id': 'test-result'}).encode()
        with patch.object(sys, 'argv', [name, *args]), patch.dict(os.environ, {'OPENROUTER_API_KEY': key}), patch('urllib.request.urlopen') as call, redirect_stdout(out), redirect_stderr(err):
            call.return_value = io.BytesIO(payload)
            call.side_effect = error
            code = 0
            try:
                runpy.run_path(str(ROOT / 'examples' / name), run_name='__main__')
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue(), call

    def test_previews_need_no_key_or_network(self):
        for name in ['request.py', 'batch.py']:
            with self.subTest(name=name):
                code, out, err, call = self.run_example(name, '--model', 'example/any-model', key='')
                self.assertEqual(code, 0, err)
                self.assertEqual(json.loads(out)['model'], 'example/any-model')
                call.assert_not_called()

    def test_default_route_and_optional_provider(self):
        for extra, expected in [([], {'data_collection': 'deny'}), (['--provider', 'example-provider'], {'data_collection': 'deny', 'order': ['example-provider'], 'allow_fallbacks': False})]:
            with self.subTest(extra=extra):
                code, out, err, call = self.run_example('request.py', '--model', 'example/model', '--send', *extra, response={'id': 'gen-1', 'model': 'example/model', 'provider': 'actual-provider', 'usage': {'cost': 0.01}, 'choices': []})
                self.assertEqual(code, 0, err)
                call.assert_called_once()
                req = call.call_args.args[0]
                self.assertEqual(req.get_method(), 'POST')
                body = json.loads(req.data)
                self.assertEqual(body['provider'], expected)
                self.assertEqual(body['max_tokens'], 64)
                self.assertEqual(json.loads(out)['provider'], 'actual-provider')
                self.assertNotIn('test-secret', out)

    def test_batch_submission_without_confirmation_flag(self):
        code, out, err, call = self.run_example('batch.py', '--model', 'example/model', '--send')
        self.assertEqual(code, 0, err)
        req = call.call_args.args[0]
        self.assertEqual(req.get_method(), 'POST')
        body = json.loads(req.data)
        self.assertEqual(body['model'], 'example/model')
        self.assertEqual(body['requests'][0]['body']['max_tokens'], 64)

    def test_batch_get_needs_only_id(self):
        code, out, err, call = self.run_example('batch.py', '--get', 'batch/id?x=1')
        self.assertEqual(code, 0, err)
        req = call.call_args.args[0]
        self.assertEqual(req.get_method(), 'GET')
        self.assertIsNone(req.data)
        self.assertTrue(req.full_url.endswith('/batch%2Fid%3Fx%3D1'))

    def test_invalid_arguments_do_not_call_network(self):
        for name, args in [('request.py', []), ('batch.py', []), ('batch.py', ['--send']), ('batch.py', ['--get', 'id', '--send'])]:
            with self.subTest(name=name, args=args):
                code, _, _, call = self.run_example(name, *args)
                self.assertEqual(code, 2)
                call.assert_not_called()

    def test_missing_key_does_not_call_network(self):
        for name, args in [('request.py', ['--model', 'example/model', '--send']), ('batch.py', ['--get', 'id'])]:
            with self.subTest(name=name):
                code, _, err, call = self.run_example(name, *args, key='')
                self.assertEqual(code, 2)
                self.assertIn('OPENROUTER_API_KEY', err)
                call.assert_not_called()

    def test_http_status_reported_without_raw_secrets(self):
        for name in ['request.py', 'batch.py']:
            for status in [400, 401, 402, 403, 404, 429, 503]:
                with self.subTest(name=name, status=status):
                    error = HTTPError('https://example.invalid/test-secret', status, 'test-secret', {}, io.BytesIO(b'test-secret'))
                    code, out, err, call = self.run_example(name, '--model', 'example/model', '--send', error=error)
                    self.assertIn(f'HTTP {status}:', str(code))
                    self.assertNotIn('test-secret', str(code) + out + err)
                    call.assert_called_once()

    def test_connection_error_does_not_retry_or_leak(self):
        for name in ['request.py', 'batch.py']:
            with self.subTest(name=name):
                code, out, err, call = self.run_example(name, '--model', 'example/model', '--send', error=URLError('test-secret'))
                self.assertIn('outcome may be uncertain', str(code))
                self.assertNotIn('test-secret', str(code) + out + err)
                call.assert_called_once()

if __name__ == '__main__':
    unittest.main()
