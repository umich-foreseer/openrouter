# Running the examples

These scripts show the smallest useful request flows to adapt for an experiment. Run them from the repository root with Python 3.10+. They use the standard library; there is no dependency-installation step.

First follow the [researcher guide](../WIKI.md) to obtain a key, set `OPENROUTER_API_KEY`, and choose a model from [models.json](../models.json). Both scripts read this JSON directly and call OpenRouter's official REST endpoints using Python's standard library. You can use the same settings in any compatible client; there is no team client wrapper to install. Replace uppercase placeholders in commands with real values.

## Synchronous example

```bash
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG --send
```

| Argument | Meaning |
| --- | --- |
| `--model` | Required exact OpenRouter model ID |
| `--provider` | Required provider routing slug from the model's endpoints |
| `--send` | Send a paid request; omit to print the request body locally |

The preview is JSON containing the prompt, model, provider settings and shared output limit. A sent request prints JSON with `choices`, requested and returned model/provider, timestamp, request ID, configuration revision, and `usage` when available. Missing response fields can be null.

To adapt it, edit `messages` in `request.py` and explicitly override output length or add supported generation parameters in the request body. `models.json` provides the common starting settings; no temperature is sent by default. Preserve explicit model/provider selection and disabled fallbacks when comparing experimental conditions. The script requests providers that do not collect data; changing that setting requires the review described in the researcher guide.

The shared default bounds output at 64 tokens and makes one request. It is not a dataset runner: it does not provide concurrency control, resumable jobs, automatic retries, or a complete experiment ledger. Add dataset and prompt versions to your own records.

## Batch example

```bash
# Preview locally.
python3 examples/batch.py --model MODEL_ID

# Submit paid work after checking exact-model support and prices.
python3 examples/batch.py --model MODEL_ID --verified-support --send

# Read status/results using the ID returned by submission.
python3 examples/batch.py --model MODEL_ID --get BATCH_ID
```

| Argument | Meaning |
| --- | --- |
| `--model` | Required for all commands; fixes the model during submission |
| `--verified-support` | Your confirmation that you checked current support and pricing; does not perform that check |
| `--send` | Submit the batch; cannot be combined with `--get` |
| `--get` | Retrieve a batch by ID; does not submit another job |

Submission prints the API's batch object. Save its ID. Retrieval prints status and, when available, inline results and usage. The `--model` argument remains required by this script for retrieval but does not select or validate the retrieved batch's model; the batch ID determines what is fetched. Retrieval remains possible if that model has since been removed from the team list; only new requests are checked against the list.

To adapt `batch.py`, edit the inline `requests` list. Give each request a unique `custom_id` and bound its output. The common output default comes from `models.json`. Record the configuration revision and repository commit alongside the returned batch ID. Keep the selected model at batch level and preserve the top-level JSON order: `endpoint`, `model`, then `requests`. This is a text-only example, not a file-upload or multimodal workflow.

The script does not pin a provider, poll automatically, or retry submissions. Review [Batch suitability and shared visibility](../WIKI.md#5-use-batch-for-work-that-can-wait) before using it. If submission times out, reconcile with Jimmy before trying again.

## Errors

Both examples hide exception details to avoid exposing credentials and exit with an error message. They do not retry failed calls. See [getting help](../WIKI.md#6-get-help) for what to report. Preview commands require no key or network access and are safe for checking edits without spending credits.
