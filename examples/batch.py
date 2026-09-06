"""Text-only Batch beta. Preview by default; --send submits, --get reads results."""
import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', help='OpenRouter model ID; required for preview or submission')
actions = p.add_mutually_exclusive_group()
actions.add_argument('--send', action='store_true')
actions.add_argument('--get', metavar='BATCH_ID', help='Read status/results without submitting')
a = p.parse_args()
if not a.get and not a.model:
    p.error('--model is required for preview or submission')
body = None
if not a.get:
    body = {
        'endpoint': '/v1/chat/completions',
        'model': a.model,
        'requests': [{'custom_id': 'hello-1', 'body': {
            'messages': [{'role': 'user', 'content': 'Say hello in one short sentence.'}],
            'max_tokens': 64,
        }}],
    }
if not a.send and not a.get:
    print(json.dumps(body, indent=2))
else:
    key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not key:
        p.error('Set OPENROUTER_API_KEY before submitting or retrieving a batch.')
    try:
        url = 'https://openrouter.ai/api/beta/batches' + ('/' + quote(a.get, safe='') if a.get else '')
        req = Request(url, data=None if a.get else json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        with urlopen(req, timeout=90) as r:
            result = json.load(r)
        print(json.dumps(result, indent=2))
    except HTTPError as e:
        e.close()
        reasons = {400: 'Invalid request or unsupported parameters', 401: 'Authentication failed', 402: 'Insufficient credits or allowance', 403: 'Budget, policy, or access restriction', 404: 'Batch, model, or endpoint unavailable', 429: 'Rate limit reached'}
        reason = reasons.get(e.code, 'Service error' if e.code >= 500 else 'Request rejected')
        raise SystemExit(f'HTTP {e.code}: {reason}. Check the Batch list before resubmitting; raw error details are withheld.') from None
    except (URLError, TimeoutError, OSError):
        raise SystemExit('Connection failed or timed out; outcome may be uncertain. Check the Batch list before resubmitting.') from None
    except (ValueError, TypeError, AttributeError):
        raise SystemExit('Unexpected response format. Check the Batch list before resubmitting.') from None
