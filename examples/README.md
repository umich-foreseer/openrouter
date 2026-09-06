# Running the examples

Use Python 3.10+ and the standard library. Follow the [researcher guide](../WIKI.md) to create a key and set `OPENROUTER_API_KEY`. Run the commands below from the repository root. Choose an available model directly from [OpenRouter](https://openrouter.ai/models); there is no local model catalog or configuration file.

Both scripts preview locally by default. Edit the prompt and output limit directly in the example for your experiment, or use your preferred compatible client.

## Synchronous example

```bash
# Preview, then send one small paid request.
python3 examples/request.py --model MODEL_ID
python3 examples/request.py --model MODEL_ID --send

# Optional: fix the provider for an experiment.
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG --send
```

Replace `MODEL_ID` and `PROVIDER_SLUG` with actual catalog values. By default OpenRouter chooses an eligible provider. Supplying `--provider` pins that provider and disables fallback; obtain its routing slug from the model's endpoints.

The example sends one greeting request with `max_tokens: 64` and `data_collection: deny`. It sends no temperature. Adapt the output limit for your task; some model routes may be unavailable under the data-handling requirement. Keep any changes consistent with the [data policy](../WIKI.md#4-prepare-data-and-record-the-experiment).

Output includes the requested and returned model/provider, UTC time, request ID, available usage, and choices. Missing response fields may be null. Record dataset, prompt, parameters, and experiment code version separately. Fix model/provider choices for controlled comparisons.

## Batch example

Check current exact-model Batch support, pricing, and data handling before submission. See the [Batch documentation](https://openrouter.ai/docs/batch-quickstart).

```bash
# Preview locally.
python3 examples/batch.py --model MODEL_ID

# Submit one paid batch.
python3 examples/batch.py --model MODEL_ID --send

# Retrieve status/results; no model argument is needed.
python3 examples/batch.py --get BATCH_ID
```

`--send` and `--get` are mutually exclusive. Retrieval requires your API key and makes a read request, not another submission. Submission prints the batch object; save its ID for retrieval. A model ID is required only for preview/submission.

The example contains one text request with `max_tokens: 64`. Edit its inline `requests` list for your experiment, using a unique `custom_id` per request. It does not pin providers, apply the synchronous example's data-collection setting, poll automatically, or retry. Check [shared visibility and Batch suitability](../WIKI.md#5-use-batch-for-work-that-can-wait) before using it.

## Errors and checks

HTTP failures report the status and a general error category, such as authentication, credits, policy, unavailable model, or rate limits. Raw error bodies and authorization headers are not printed. For timeouts or unexpected responses, inspect Activity or the Batch list before resubmitting; the previous attempt may have incurred charges.

Preview commands require neither credentials nor network access. Run `python3 -m unittest discover -s tests -v` from the repository root to check previews, mocked requests, routing options, Batch retrieval, and error handling without spending credits.
