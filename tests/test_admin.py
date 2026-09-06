import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import admin

class Fake:
    def __init__(self):
        self.data = {}
        self.posts = 0
        self.fail = False
    def keys(self):
        return list(self.data.values())
    def call(self, method, path, body=None):
        if method == 'POST':
            self.posts += 1
            h = str(self.posts)
            self.data[h] = dict(body, hash=h, usage_monthly=0, disabled=False)
            if self.fail:
                raise admin.SafeError('Uncertain API outcome')
            return {'data': self.data[h], 'key': 'TEST_SECRET_NEVER_PRINT'}
        h = path.split('/')[-1]
        if method == 'PATCH':
            self.data[h].update(body)
        return {'data': self.data[h]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.api = Fake()
        self.obj = admin.Admin(self.api, Path(self.tmp.name) / 'state.json')
    def add(self):
        return self.obj.run('onboard', 'researcher', apply=True)
    def test_preview_and_duplicate(self):
        self.obj.run('onboard', 'researcher')
        self.assertEqual(self.api.posts, 0)
        self.add()
        self.assertTrue(self.obj.run('onboard','researcher',apply=True)['existing'])
        self.assertEqual(self.api.posts, 1)
    def test_override(self):
        self.add()
        self.obj.run('limit','researcher',allowance=175,apply=True)
        self.assertEqual(self.api.data['1']['limit'],175)
    def test_rotation_and_rollover(self):
        self.add()
        self.api.data['1']['usage_monthly'] = 37.25
        self.obj.run('rotate','researcher',apply=True,drained=True)
        self.assertTrue(self.api.data['1']['disabled'])
        self.assertEqual(self.api.data['2']['limit'],62.75)
        self.api.data['2']['usage_monthly'] = 5
        self.obj.run('rotate','researcher',apply=True,drained=True)
        self.assertEqual(self.api.data['3']['limit'],57.75)
        # OpenRouter's UTC monthly counters reset; sync restores full policy.
        for k in self.api.data.values():
            k['usage_monthly'] = 0
        self.obj.run('sync','researcher',apply=True)
        self.assertEqual(self.api.data['3']['limit'],100)
    def test_utc(self):
        with patch('admin.datetime') as dt:
            dt.now.return_value.strftime.return_value = '2026-10'
            self.assertEqual(admin.month(),'2026-10')
            dt.now.assert_called_once_with(admin.timezone.utc)
    def test_secret_files_and_redaction(self):
        result = self.add()
        p = Path(result['handoff_file'])
        self.assertEqual(p.stat().st_mode & 0o777,0o600)
        self.assertNotIn('TEST_SECRET',json.dumps(result))
        self.assertNotIn('TEST_SECRET',self.obj.path.read_text())
    def test_uncertain_creation(self):
        self.api.fail = True
        with self.assertRaises(admin.SafeError): self.add()
        with self.assertRaises(admin.SafeError): self.add()
        self.assertEqual(self.api.posts,1)
        self.obj.run('reconcile',apply=True)
        self.assertTrue(self.api.data['1']['disabled'])
    def test_state_loss(self):
        self.add()
        other = admin.Admin(self.api,Path(self.tmp.name)/'other.json')
        with self.assertRaises(admin.SafeError): other.run('onboard','researcher',apply=True)
    def test_http_error_redaction(self):
        with patch('admin.urlopen',side_effect=RuntimeError('TEST_SECRET_NEVER_PRINT')):
            with self.assertRaises(admin.SafeError) as e:
                admin.API('TEST_SECRET_NEVER_PRINT').call('POST','/keys',{})
        self.assertNotIn('TEST_SECRET',str(e.exception))
    def test_exhausted_and_negative(self):
        self.add()
        self.api.data['1']['usage_monthly']=101
        self.obj.run('rotate','researcher',apply=True,drained=True)
        self.assertEqual(self.api.data['2']['limit'],0)
        with self.assertRaises(admin.SafeError): admin.money(-1)

if __name__ == '__main__': unittest.main()
