# Foreseer OpenRouter

Shared model access for Foreseer researchers at U-M. Choose any available model from [OpenRouter](https://openrouter.ai/models).

## Get access

Send the administrator your U-M uniqname, OpenRouter email, GitHub username, project, and expected spending. Accept the **Member** invitation to **Umich Foreseer**, then **wait for budget confirmation before using the account**. In **Default Workspace → [API Keys](https://openrouter.ai/workspaces/default/keys)**, create your own key. Members manage their keys; administrators control budgets and billing.

Keep keys out of repositories, notebooks, messages, and logs. Organization Activity shows members each other's models, costs, and request times. Treat shared-workspace Batch metadata and results as team-visible too.

## Run a request

Use your preferred compatible client or these Python 3.10+ examples (standard library only). Clone this repository and run from its root. Save your key privately at `~/.config/foreseer/research.key` with directory mode 700 and file mode 600, then load it:

```bash
export OPENROUTER_API_KEY="$(cat "$HOME/.config/foreseer/research.key")"

# Replace MODEL_ID with an available OpenRouter model ID.
python3 examples/request.py --model MODEL_ID         # local preview
python3 examples/request.py --model MODEL_ID --send  # paid request
```

The example sends a greeting with a 64-token output cap; edit the prompt and cap for your task. OpenRouter selects a provider. Optionally add `--provider PROVIDER_SLUG` to pin a provider and disable fallback. Find its slug on the model's endpoints page. Run a small pilot before scaling; record model, provider, parameters, dataset/prompt versions, code version, request ID, tokens, and cost. Clear the key variable with `unset OPENROUTER_API_KEY` when finished.

### Batch (optional beta)

Check [exact-model Batch support and prices](https://openrouter.ai/docs/batch-quickstart) first. This is a text-only example.

```bash
python3 examples/batch.py --model MODEL_ID         # local preview
python3 examples/batch.py --model MODEL_ID --send  # paid submission; save returned ID
python3 examples/batch.py --get BATCH_ID           # retrieve status/results
```

## Check usage

In [Activity](https://openrouter.ai/activity), select a period and group/filter by **Creator** for a member, **API Key** for a key, or **Model** for model costs. Export Spend, Tokens, and Requests as CSV/PDF. Ask the administrator to confirm your budget or request an increase with the project, amount, and timeframe. New keys do not renew your member allowance; lower key limits can also apply.

For one key, `GET https://openrouter.ai/api/v1/key` with your key as a Bearer token returns `usage_monthly` and `limit_remaining`. These are key-level values, not the combined member budget; a null key limit does not override the member cap.

## Administrator operations

- **Onboard:** invite as Member in [Members](https://openrouter.ai/settings/organization-members), grant repository read access, and after acceptance assign **Foreseer Member — $100/month** in [Guardrails](https://openrouter.ai/workspaces/default/guardrails). Verify the member, amount, monthly reset, and ownership of their self-created key. A rule without assignments enforces nothing; use member assignment, not the workspace default. Coordinate acceptance: spending is technically possible before assignment.
- **Change allowance:** assign a rule for the approved amount. Sharing a rule gives each member an independent budget; editing that rule affects everyone assigned to it. Each member can have one direct rule, so preserve any existing restrictions. Keep model access open. The current budget rule excludes external BYOK spend.
- **Fund and reconcile:** keep auto-top-up off, check [Credits](https://openrouter.ai/settings/credits) before large runs, and retain monthly Activity exports and receipts. Do not add overlapping Creator and Key totals. Individual budgets are not a shared account cap.
- **Old keys:** administrator-issued keys keep their existing limits and are tracked by Key rather than member Creator. Before migration, settle and count their spending against the current month's allowance; do not grant a fresh full budget. Preserve private records. The old CLI is retired; its code and detailed migration notes remain in Git history.
- **Offboard:** disable keys, handle outstanding jobs, export usage, and remove organization and repository access. Disabling keys does not cancel already submitted work.

Tests: `python3 -m unittest discover -s tests -v` (mocked; no network).
