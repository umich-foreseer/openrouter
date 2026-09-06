# Researcher guide

Use the team's OpenRouter access to run experiments with different model APIs under one funded account. Each researcher receives an individual key and spending allowance. Jimmy (`jimmyzxj`) handles access, allowance changes, and billing.

## 1. Get access

Send Jimmy your U-M uniqname, GitHub username, project, intended models, and estimated monthly spending. You will receive a research API key privately and read access to this repository. You do not need an OpenRouter dashboard account.

Your key identifies your usage. Keep it to yourself, store it outside repositories, and never include it in notebooks, issues, messages, or experiment logs. Contact Jimmy immediately if it is exposed or lost.

## 2. Make your first request

You need Python 3.10+ and internet access. Clone this repository, then run the commands below from its root. No additional Python packages are required.

Save your delivered key in a private file, such as `~/.config/foreseer/research.key`. On macOS or Linux, give the directory mode 700 and the file mode 600. Load it into your shell without pasting the secret into a command:

```bash
export OPENROUTER_API_KEY="$(cat "$HOME/.config/foreseer/research.key")"
```

Choose an exact model ID and provider routing slug from the [model catalog](https://openrouter.ai/models). Replace `MODEL_ID` and `PROVIDER_SLUG` below with those values.

```bash
# Preview the request; this does not call the API.
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG

# After checking the preview and price, send one paid request.
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG --send
```

The example asks for a short greeting and sets a 64-token output limit. It prints the response and available usage metadata. Once you are finished, clear the shell variable with `unset OPENROUTER_API_KEY`.

See the [examples guide](examples/README.md) to understand the output or adapt the prompt.

## 3. Choose a model and plan the cost

Start with the capability your experiment needs, then check the exact model's provider, supported parameters, and current price. Use explicit model IDs rather than automatic model selection. Availability and prices can change, so check again before a large run.

Estimate the token cost with:

```text
estimated cost = input tokens × input price + output tokens × output price
```

Keep the units consistent. For example, at hypothetical prices of $1 per million input tokens and $4 per million output tokens, 1,000 requests averaging 2,000 input and 500 output tokens would cost about $4. These are illustrative prices, not a quote for a model. Reasoning, caching, tools, and other charges can change the total.

The public model API, `GET https://openrouter.ai/api/v1/models`, reports `pricing.prompt` and `pricing.completion` in dollars **per token**. Model pages may display prices per million tokens.

Run a small pilot, inspect actual token usage and cost, then estimate the full run. Bound output length and concurrency in your own scripts. The sample's 64-token limit is a starting point, not a suitable setting for every experiment.

### Your allowance and the shared balance

The default allowance is **$100 per calendar month**, resetting at midnight UTC on the first. Jimmy can approve a different allowance. For an increase, send the project, model, estimated cost, and timeframe before starting the larger run.

Your allowance limits spending; it does not reserve funds. Everyone draws from the same prepaid account, so requests can stop when the shared balance runs out even if you have allowance left. Contact Jimmy when this happens.

Replacing a key does not renew your allowance. If a replacement still shows a reduced allowance after the next month begins, ask Jimmy to synchronize it.

## 4. Prepare data and record the experiment

This team workflow is for public research data that you are permitted to send to the chosen provider. Check dataset licenses, attribution requirements, and restrictions on processing or redistribution. A dataset being downloadable from Hugging Face does not by itself establish permission or guarantee that it contains no personal information. Nonpublic institutional and sensitive data are outside this workflow.

Use no-training routes by default. Training-enabled provider tiers require deliberate opt-in by you and Jimmy after reviewing the dataset terms and applicable requirements. The synchronous example requests `data_collection: deny`; review the implications before changing it. Check Batch provider data handling separately.

For every experiment, save:

| Record | Why it matters |
| --- | --- |
| Requested and returned model ID; provider | Identifies the service that actually ran the request |
| Parameters, prompt/template version, dataset version | Describes the experimental conditions |
| UTC date and request/generation ID | Helps trace changes and investigate failures |
| Input/output token usage and actual cost | Supports comparison and budgeting |

The synchronous example selects one provider and disables provider fallbacks. It supplies no fallback model. An unavailable route should fail rather than silently change the experiment. Fixed settings still do not guarantee identical results across model updates or repeated calls.

Save missing metadata separately: the example does not know your dataset version, and the provider may omit some response fields. If cost is absent, ask Jimmy to help reconcile the request ID with account activity. Never record authorization headers or API keys.

## 5. Use Batch for work that can wait

Batch is an optional **beta**, text-only path for asynchronous experiments. Before submitting, verify support and current Batch pricing for the **exact model** using the [Batch documentation](https://openrouter.ai/docs/batch-quickstart) and model page. Synchronous availability alone does not establish Batch support. Ask Jimmy if support or data handling is unclear.

**Batch visibility is workspace-wide.** Treat batch metadata and results in the shared workspace as team-visible material. Submit only data that can be shared with the team.

Follow the [Batch example instructions](examples/README.md#batch-example) to preview, submit, and retrieve results. The example fixes the model but does not promise provider pinning. Use synchronous requests when selecting an exact provider is essential. Check actual cost rather than assuming a discount.

After a submission timeout, ask Jimmy to check the Batch list before resubmitting; the original job may already exist.

## 6. Get help

Contact Jimmy for access, allowance, shared-balance, or account issues. For a script problem, include the command with secrets removed, model/provider, UTC time, request or batch ID if available, and the error message or status code. The examples deliberately hide detailed exceptions; report the information you have rather than adding logs that could expose your key.

| Symptom | What to do |
| --- | --- |
| 401 / authentication failure | Check that your key is loaded and has not been revoked; ask Jimmy if it persists. |
| 402 / insufficient funds or allowance | Ask Jimmy to check both your allowance and shared credits. |
| 403 / denied request | Check the provider and requested operation; ask Jimmy about account restrictions. |
| 429 / rate limit | Reduce concurrency. Use bounded backoff for requests known to have been rejected. |
| 400 or 404 | Check the model ID, endpoint, supported parameters, and Batch support. |
| Timeout or server error | The outcome may be uncertain. Check with Jimmy before repeating potentially paid work. |

For planned key replacement, coordinate stopping jobs and settling batches with Jimmy. Already submitted work may still generate charges after access is disabled.
