"""Text-only Batch beta. Default is a preview, never a submission."""
import argparse
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import quote
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--model', required=True)
p.add_argument('--verified-support', action='store_true', help='Confirm current exact-model batch support and pricing have been checked')
p.add_argument('--send', action='store_true')
p.add_argument('--get', metavar='BATCH_ID', help='Read status/results; no submission')
a = p.parse_args()
body = {'endpoint': '/v1/chat/completions', 'model': a.model, 'requests': [{'custom_id': 'hello-1', 'body': {'messages': [{'role':'user','content':'Say hello in one short sentence.'}], 'max_tokens':64}}]}
if a.send and a.get:
    p.error('Choose --send or --get')
if a.send and not a.verified_support:
    p.error('Verify current support for this exact model; then pass --verified-support')
if not a.send and not a.get:
    print(json.dumps(body,indent=2))
else:
    try:
        url = 'https://openrouter.ai/api/beta/batches' + ('/' + quote(a.get,safe='') if a.get else '')
        req = Request(url, data=None if a.get else json.dumps(body).encode(), headers={'Authorization':'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type':'application/json'})
        with urlopen(req,timeout=90) as r:
            result = json.load(r)
        print(json.dumps(result,indent=2))
    except Exception:
        raise SystemExit('Batch request failed. Do not blindly retry submission; reconcile in Batch list first.') from None
