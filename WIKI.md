# Researcher guide

Use Foreseer's shared OpenRouter account to run model experiments. The administrator manages membership, budgets, and billing; you manage your own API keys.

## 1. Get access

Send the administrator your U-M uniqname, OpenRouter account email, GitHub username, project, and estimated monthly spending.

1. Accept the invitation to **Umich Foreseer** as a **Member** using your own OpenRouter account.
2. Wait for the administrator to confirm that your member budget has been assigned before creating keys, using chat, or sending requests. Invitation acceptance does not automatically apply the budget rule.
3. Switch to **Umich Foreseer → Default Workspace**. Create a key in [API Keys](https://openrouter.ai/workspaces/default/keys), using a name such as `uniqname-project`, and save it privately.
4. Once you have repository read access, clone it and follow the examples below from its root directory.

Members can manage their own keys but cannot change administrator-set budgets or payment settings. Organization Activity currently shows usage metadata for all members, including models, costs, and request times. Filtering to your own usage does not hide it from other members. See [organization permissions](https://openrouter.ai/docs/cookbook/administration/organization-management).

Keep keys private and outside repositories, notebooks, messages, and experiment logs. If you already have an administrator-issued key, continue using it under its existing limit until migration is arranged. Joining as a Member does not transfer ownership of that key or attribute its previous spending to your member account.

## 2. Make your first request

You need Python 3.10+; no extra packages are required. Save your key in a private file such as `~/.config/foreseer/research.key`, with directory mode 700 and file mode 600. Load it without pasting the secret into a command:

```bash
export OPENROUTER_API_KEY="$(cat "$HOME/.config/foreseer/research.key")"
```

Choose an available model ID from the [OpenRouter catalog](https://openrouter.ai/models). Replace `MODEL_ID` below:

```bash
# Preview locally without spending credits.
python3 examples/request.py --model MODEL_ID

# Send one small paid request.
python3 examples/request.py --model MODEL_ID --send
```

The example asks for a short greeting and limits output to 64 tokens. OpenRouter chooses a provider eligible under the request's data-handling settings. For an experiment that requires a fixed provider, add `--provider PROVIDER_SLUG`; this disables provider fallback. See the [examples guide](examples/README.md) for details.

Clear the shell variable when finished with `unset OPENROUTER_API_KEY`.

## 3. Choose a model and manage costs

There is no team model allowlist or locally maintained model catalog. Use any model available to your account, within your budget and the data-handling policy below. Check current provider prices, parameters, and endpoint support before running an experiment. A catalog listing is not proof that a particular route or Batch submission will work.

Start with a small pilot and estimate cost from actual usage. Input, output, reasoning, caching, and other charges can differ by model. Bound output length and concurrency in your own experiment code; the example's 64-token cap is only a greeting-sized default.

### Your allowance and the shared balance

The default allowance is **$100 per calendar month**, resetting at midnight UTC on the first. The assigned member Guardrail combines spending across your own keys and chatroom usage. Creating another key does not renew the allowance. A lower individual key cap can restrict spending further. Request an increase from the administrator with the project, estimated cost, and timeframe.

Budgets do not reserve funds: everyone draws from the same prepaid balance. Requests may stop when shared credits run out even if your allowance remains. Legacy keys issued by the administrator retain their separate key limits until migration.

### Check your usage

In [Activity](https://openrouter.ai/activity), select the reporting period and group or filter by **Creator** for member usage, **API Key** for individual keys, and **Model** for model costs. You can export Spend, Tokens, and Requests as CSV/PDF. The administrator can confirm your assigned budget and check how much remains. Administrator-issued keys must be identified by key, not by Creator.

To inspect one key:

```bash
curl -sS https://openrouter.ai/api/v1/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

The [current-key endpoint](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-api-key) returns `usage`, `usage_monthly`, `limit`, `limit_remaining`, and `limit_reset`. These describe that key, not the combined member budget. A null key limit does not mean unlimited member spending.

## 4. Prepare data and record the experiment

Use public research data that you are permitted to send to the chosen provider. Check dataset licenses and restrictions. Publicly downloadable data may still contain personal information; nonpublic institutional and sensitive data are outside this workflow.

Use no-training routes by default. Before using a provider tier that permits training on your data, review the dataset terms with the administrator and obtain approval. The synchronous example sets `data_collection: deny`; this can make some routes unavailable. Check Batch data handling separately.

Record the requested and returned model IDs, actual provider, parameters, prompt/dataset versions, UTC time, request ID, token counts, and actual cost. Preserve your experiment code version. Fix model/provider choices when comparing experiments; provider routing is convenient for ordinary usage but can vary the conditions of a benchmark.

## 5. Use Batch for work that can wait

The repository includes an optional text-only example for OpenRouter's **beta Batch API**. Before submitting, check exact-model support, pricing, and data handling in the [Batch documentation](https://openrouter.ai/docs/batch-quickstart). Synchronous availability does not establish Batch support.

Treat Batch metadata and results in the shared workspace as team-visible. Submit only data that can be shared with the team. Follow the [Batch example](examples/README.md#batch-example); it does not pin providers. After an uncertain submission, check the Batch list before resubmitting to avoid duplicate work and charges.

## 6. Get help

Contact the administrator for membership, budgets, and shared-balance issues. Include the model, UTC time, request/batch ID, and HTTP status when reporting a failure. Never send a key or authorization header.

| Status | Likely issue |
| --- | --- |
| 400 | Invalid request or unsupported parameters |
| 401 | Missing, invalid, or revoked key |
| 402 | Credits or allowance exhausted |
| 403 | Budget, policy, or access restriction |
| 404 | Model, endpoint, or batch unavailable |
| 429 | Rate limit; reduce concurrency |
| 5xx / timeout | Service or connection failure; outcome may be uncertain |

The examples report HTTP status and a general error category without printing raw provider error bodies. Use account Activity or the Batch list to investigate. They do not automatically retry. If a key is exposed, disable it promptly and notify the administrator; already submitted work may still incur charges.
