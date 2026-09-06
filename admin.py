#!/usr/bin/env python3
"""Jimmy-only OpenRouter administration. Python 3.10+, standard library."""
import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent

class SafeError(Exception):
    pass

def month():
    return datetime.now(timezone.utc).strftime('%Y-%m')

def money(value):
    x = Decimal(str(value))
    if not x.is_finite() or x < 0:
        raise SafeError('Allowance must be finite and nonnegative.')
    return float(x)

def monthly_usage(key):
    if key.get('usage_monthly') is None:
        raise SafeError('Monthly usage is unavailable; refusing to estimate remaining allowance.')
    return money(key['usage_monthly'])

def private_path(path):
    p = Path(path).expanduser().resolve()
    if p == ROOT or ROOT in p.parents:
        raise SafeError('Private files must be outside the checkout.')
    return p

def write_private(path, obj):
    path = private_path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + '.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=2))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

class API:
    def __init__(self, token):
        self.token = token
    def call(self, method, path, body=None):
        req = Request('https://openrouter.ai/api/v1' + path,
                      data=None if body is None else json.dumps(body).encode(),
                      headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}, method=method)
        try:
            with urlopen(req, timeout=30) as r:
                return json.load(r)
        except HTTPError as e:
            raise SafeError(f'OpenRouter HTTP {e.code}; response withheld. Reconcile mutations before retrying.') from None
        except Exception:
            raise SafeError('Uncertain API outcome; response withheld. Reconcile before retrying mutations.') from None
    def keys(self):
        result = []
        while True:
            page = self.call('GET', f'/keys?offset={len(result)}&include_disabled=true')['data']
            result.extend(page)
            if len(page) < 100:
                return result

class Admin:
    def __init__(self, api, state_path):
        self.api, self.path = api, private_path(state_path)
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {'users': {}, 'pending': None}
    def save(self):
        write_private(self.path, self.state)
    def current(self, u):
        return self.api.call('GET', '/keys/' + u['hash'])['data']
    def cap(self, u):
        spent = sum(Decimal(str(monthly_usage(self.api.call('GET', '/keys/' + h)['data']))) for h in u.get('retired', []))
        return float(max(Decimal('0'), Decimal(str(u['allowance'])) - spent))
    def patch(self, h, body):
        self.api.call('PATCH', '/keys/' + h, body)
        actual = self.api.call('GET', '/keys/' + h)['data']
        if any(actual.get(k) != v for k, v in body.items()):
            raise SafeError('Update could not be verified; reconcile before continuing.')
    def create(self, name, cap, user, handoff):
        # Durable journal BEFORE POST; never retry creation after any failure.
        self.state['pending'] = {'name': name, 'user': user, 'cap': cap}
        self.save()
        r = self.api.call('POST', '/keys', {'name': name, 'limit': cap, 'limit_reset': 'monthly'})
        write_private(handoff, r['key'] + '\n')
        return r['data']['hash']
    def run(self, command, user=None, allowance=None, apply=False, drained=False):
        if user and not re.fullmatch('[a-z][a-z0-9_-]{0,31}', user):
            raise SafeError('Use a lowercase U-M uniqname.')
        users = self.state['users']
        if command in ('list', 'report'):
            rows = []
            for name, u in users.items():
                key = self.current(u)
                spent = sum(monthly_usage(self.api.call('GET', '/keys/' + h)['data']) for h in u.get('retired', []))
                rows.append({'uniqname': name, 'month_utc': month(), 'allowance': u['allowance'], 'usage_monthly': spent + monthly_usage(key), 'key_limit': key.get('limit'), 'disabled': key['disabled']})
            return rows
        if command == 'reconcile':
            p = self.state.get('pending')
            if not p:
                return {'pending': False}
            matches = [k for k in self.api.keys() if k['name'] == p['name']]
            if not apply:
                return {'pending': True, 'matching_keys': len(matches), 'action': 'disable matches and clear journal; no credential can be recovered'}
            for k in matches:
                self.patch(k['hash'], {'disabled': True})
                u = users.setdefault(p['user'], {'hash': k['hash'], 'retired': [], 'allowance': p['cap']})
                if not u.get('hash'):
                    u['hash'] = k['hash']
                if k['hash'] != u['hash'] and k['hash'] not in u['retired']:
                    u['retired'].append(k['hash'])
            if not users.get(p['user'], {}).get('hash'):
                users.pop(p['user'], None)
            self.state['pending'] = None
            self.save()
            return {'reconciled': True, 'disabled_matches': len(matches)}
        if self.state.get('pending'):
            raise SafeError('Pending creation exists. Run reconcile, inspect, then reconcile --apply first.')
        if command == 'onboard' and user in users:
            return {'existing': True, 'uniqname': user, 'action': 'No new key. Use rotate to replace a lost or disabled key.'}
        if command != 'onboard' and user not in users:
            raise SafeError('Unknown uniqname.')
        u = users.get(user)
        if command == 'onboard':
            # Detect local-state loss before creating any duplicate.
            prefix = 'foreseer:' + user + ':'
            if any(k['name'].startswith(prefix) for k in self.api.keys()):
                raise SafeError('Remote identity already exists. Restore admin state; refusing duplicate onboarding.')
            proposed = money(100 if allowance is None else allowance)
        elif command == 'limit':
            proposed = money(allowance)
        else:
            proposed = u['allowance']
        if not apply:
            preview_cap = proposed
            if u and command in ('limit', 'sync', 'rotate'):
                candidate = dict(u, allowance=proposed)
                preview_cap = self.cap(candidate)
                if command == 'rotate':
                    preview_cap = max(0, preview_cap - monthly_usage(self.current(u)))
            return {'preview': command, 'uniqname': user, 'allowance': proposed, 'new_key_limit': preview_cap if command != 'disable' else None, 'note': 'rotation disables old key first and carries retired-key monthly spend'}
        if command == 'onboard':
            u = {'allowance': proposed, 'retired': []}
            users[user] = u
        if command == 'rotate':
            if not drained:
                raise SafeError('Stop jobs, settle batches and usage, then pass --drained. In-flight billing cannot be atomically transferred.')
            self.patch(u['hash'], {'disabled': True})
            if u['hash'] not in u['retired']:
                u['retired'].append(u['hash'])
            self.save()
        if command in ('onboard', 'rotate'):
            name = 'foreseer:' + user + ':' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
            handoff = self.path.parent / 'handoff' / (name.replace(':', '-') + '.key')
            u['hash'] = self.create(name, self.cap(u), user, handoff)
            self.state['pending'] = None
            self.save()
            return {'created': user, 'handoff_file': str(handoff)}
        if command == 'disable':
            self.patch(u['hash'], {'disabled': True})
        else:
            # Save desired policy first; sync can recover an ambiguous PATCH.
            u['allowance'] = proposed
            self.save()
            self.patch(u['hash'], {'limit': self.cap(u), 'limit_reset': 'monthly'})
        self.save()
        return {'updated': user, 'command': command}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state-dir', default=os.environ.get('FORESEER_ADMIN_DIR'))
    p.add_argument('command', choices=['list', 'report', 'onboard', 'limit', 'rotate', 'disable', 'sync', 'reconcile'])
    p.add_argument('uniqname', nargs='?')
    p.add_argument('--allowance', type=money)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--drained', action='store_true')
    p.add_argument('--output', help='Report CSV outside checkout')
    a = p.parse_args()
    if not a.state_dir:
        p.error('Set FORESEER_ADMIN_DIR to the private directory containing management.key.')
    if a.command in ('onboard','limit','rotate','disable','sync') and not a.uniqname:
        p.error('uniqname required')
    if a.command == 'limit' and a.allowance is None:
        p.error('--allowance required')
    d = private_path(a.state_dir)
    if d.stat().st_mode & 0o077 or (d / 'management.key').stat().st_mode & 0o077:
        raise SafeError('Admin directory must be 700 and management.key 600.')
    with open(d / '.lock', 'a') as lock:
        os.chmod(d / '.lock', 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        obj = Admin(API((d / 'management.key').read_text().strip()), d / 'state.json')
        result = obj.run(a.command, a.uniqname, a.allowance, a.apply, a.drained)
        if a.command == 'report':
            if not a.output:
                p.error('report requires --output outside checkout')
            import io
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=['uniqname','month_utc','allowance','usage_monthly','key_limit','disabled'])
            writer.writeheader()
            writer.writerows(result)
            write_private(a.output, out.getvalue())
            print('Report saved.')
        else:
            print(json.dumps(result, indent=2))

if __name__ == '__main__':
    try:
        main()
    except SafeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print('Operation failed; details withheld to protect credentials. Inspect local state and reconcile before retrying.', file=sys.stderr)
        sys.exit(1)
