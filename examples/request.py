"""One small REST request. Preview by default; --send calls OpenRouter."""
import argparse
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', required=True, help='OpenRouter model ID')
p.add_argument('--provider', help='Optional provider slug; pins the request and disables fallback')
p.add_argument('--send', action='store_true')
a = p.parse_args()
provider = {'data_collection': 'deny'}
if a.provider:
    provider.update({'order': [a.provider], 'allow_fallbacks': False})
body = {
    'model': a.model,
    'messages': [{'role': 'user', 'content': 'Say hello in one short sentence.'}],
    'max_tokens': 64,
    'provider': provider,
}
if not a.send:
    print(json.dumps(body, indent=2))
else:
    key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not key:
        p.error('Set OPENROUTER_API_KEY before sending.')
    try:
        req = Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        with urlopen(req, timeout=90) as r:
            result = json.load(r)
        print(json.dumps({'date_utc': datetime.now(timezone.utc).isoformat(), 'model_requested': a.model, 'provider_requested': a.provider, 'id': result.get('id'), 'model': result.get('model'), 'provider': result.get('provider'), 'usage': result.get('usage'), 'choices': result.get('choices')}, indent=2))
    except HTTPError as e:
        e.close()
        reasons = {400: 'Invalid request or unsupported parameters', 401: 'Authentication failed', 402: 'Insufficient credits or allowance', 403: 'Budget, policy, or access restriction', 404: 'Model or endpoint unavailable', 429: 'Rate limit reached'}
        reason = reasons.get(e.code, 'Service error' if e.code >= 500 else 'Request rejected')
        raise SystemExit(f'HTTP {e.code}: {reason}. Check Activity before retrying; raw error details are withheld.') from None
    except (URLError, TimeoutError, OSError):
        raise SystemExit('Connection failed or timed out; outcome may be uncertain. Check Activity before retrying.') from None
    except (ValueError, TypeError, AttributeError):
        raise SystemExit('Unexpected response format. Check Activity before retrying.') from None
