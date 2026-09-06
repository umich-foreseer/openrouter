"""One explicit, bounded request. Only --send makes a paid request."""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', required=True)
p.add_argument('--provider', required=True, help='Exact provider routing slug from model endpoints')
p.add_argument('--send', action='store_true')
a = p.parse_args()
config = json.loads((Path(__file__).resolve().parents[1] / 'models.json').read_text())
allowed_models = {model for group in config['allowed_models'].values() for model in group}
if a.model not in allowed_models:
    p.error('Model is not in models.json; ask Jimmy to add it before use.')
body = {'model': a.model, 'messages': [{'role': 'user', 'content': 'Say hello in one short sentence.'}], **config['request_defaults'], 'provider': {'order': [a.provider], **config['sync_routing']}}
if not a.send:
    print(json.dumps(body, indent=2))
else:
    try:
        req = Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
        with urlopen(req, timeout=90) as r:
            result = json.load(r)
        print(json.dumps({'date_utc': datetime.now(timezone.utc).isoformat(), 'model_requested': a.model, 'provider_requested': a.provider, 'parameters': config['request_defaults'], 'config_revision': config['revision'], 'id':result.get('id'), 'model':result.get('model'), 'provider':result.get('provider'), 'usage':result.get('usage'), 'choices':result.get('choices')},indent=2))
    except Exception:
        raise SystemExit('Request failed. No automatic retry; inspect account activity before resubmitting.') from None
