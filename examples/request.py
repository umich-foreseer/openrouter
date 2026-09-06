"""One explicit, bounded request. Only --send makes a paid request."""
import argparse
import json
import os
from urllib.request import Request, urlopen
from datetime import datetime, timezone

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', required=True)
p.add_argument('--provider', required=True, help='Exact provider routing slug from model endpoints')
p.add_argument('--send', action='store_true')
a = p.parse_args()
body = {'model': a.model, 'messages': [{'role': 'user', 'content': 'Say hello in one short sentence.'}], 'max_tokens': 64, 'temperature': 0, 'provider': {'order': [a.provider], 'allow_fallbacks': False, 'require_parameters': True, 'data_collection': 'deny'}}
if not a.send:
    print(json.dumps(body, indent=2))
else:
    try:
        req = Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
        with urlopen(req, timeout=90) as r:
            result = json.load(r)
        print(json.dumps({'date_utc': datetime.now(timezone.utc).isoformat(), 'model_requested': a.model, 'provider_requested': a.provider, 'parameters': {'max_tokens':64,'temperature':0}, 'id':result.get('id'), 'model':result.get('model'), 'provider':result.get('provider'), 'usage':result.get('usage'), 'choices':result.get('choices')},indent=2))
    except Exception:
        raise SystemExit('Request failed. No automatic retry; inspect account activity before resubmitting.') from None
