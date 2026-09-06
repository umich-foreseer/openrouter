# Foreseer research API wiki

## Access and monthly allowances

Jimmy (`jimmyzxj`) administers the **Umich Foreseer** account, **Default** workspace, billing, and management credential. Researchers receive individual inference keys, not dashboard memberships. Request access from Jimmy with your U-M uniqname, GitHub username, project, intended models, and estimated monthly spending. Jimmy privately delivers the key and later grants repository read access. Never share a key between people.

Default allowance: **$100 per calendar month**, resetting at midnight UTC on the first. Jimmy can override it. Ten $100 limits permit roughly $1,000/month in inference; they do not buy credits or establish a separate shared cap. All keys consume one prepaid balance (initial rollout: $25). Requests can fail when that balance is exhausted even if your allowance remains. Funding is manual and auto-top-up stays disabled. Request increases from Jimmy before starting large experiments.

Run Python on your laptop or an existing internet-connected research environment. No proxy, persistent VM, Great Lakes, or Lighthouse configuration is needed.

## Receive a key and make a request

Use Python 3.10+. Save the privately delivered key outside all repositories, for example `~/.config/foreseer/research.key`. Use mode 700 for the directory and 600 for the file. Do not paste credentials into source code, notebooks, issues, chat, shell history, or command arguments.

```bash
export OPENROUTER_API_KEY="$(cat "$HOME/.config/foreseer/research.key")"
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG
# Review preview and current prices; --send makes one paid request:
python3 examples/request.py --model MODEL_ID --provider PROVIDER_SLUG --send
unset OPENROUTER_API_KEY
```

Replace uppercase placeholders. Output is capped at 64 tokens. The synchronous example selects one provider, disables provider fallbacks, and supplies no fallback model. Unsupported parameters or provider unavailability should fail rather than silently change the experiment. It requests providers that do not collect data; account restrictions can further narrow routes.

## Model choice, prices, and reproducibility

Get exact IDs from the [model catalog](https://openrouter.ai/models) or public `GET https://openrouter.ai/api/v1/models`. Check the model page for current provider endpoints and prices. Catalog `pricing.prompt` and `pricing.completion` are dollars **per token**. Estimate cost as `input_tokens × prompt_price + output_tokens × completion_price`, accounting separately for caching, reasoning, tools, and other charges. Broad access is not a guarantee that every provider supports every request.

Record requested/returned model ID, provider, parameters, UTC date, dataset version, request/generation ID, token usage, and actual cost. The synchronous example prints these response fields. If cost is missing, retrieve generation details by ID or reconcile with account activity. Never log Authorization headers. Fixed parameters do not guarantee identical outputs across model/provider updates.

## Text-only Batch beta

Batch is **beta**. Before using it, verify **the exact model's** Batch support and current pricing using the [Batch quickstart](https://openrouter.ai/docs/batch-quickstart) and model page. Synchronous availability alone does not prove Batch support. If unclear, ask Jimmy before submitting. The flag below confirms your manual check; it is not automatic capability detection.

```bash
python3 examples/batch.py --model MODEL_ID
# Only after verifying exact-model support and pricing; submits paid work:
python3 examples/batch.py --model MODEL_ID --verified-support --send
# Read status and inline results using the returned ID:
python3 examples/batch.py --model MODEL_ID --get BATCH_ID
```

The example submits one text request, bounded to 64 output tokens, with one fixed batch-level model and no model fallback list. It does not promise provider pinning. Use synchronous requests when exact provider selection is required until the relevant Batch routing contract is verified. Record returned provider information when available. Check actual `usage.cost`; do not assume a discount.

**Batch visibility is workspace-wide.** Keys in Default can list shared batches; treat batch metadata and results as team-shared material, not per-person private storage. Submit only mutually shareable research data. Requests use inline JSON at `/api/beta/batches`, not another provider's file-upload protocol. After a submission timeout, inspect the Batch list before resubmitting to avoid duplicate paid jobs.

## Public data and provider training

This workflow is for public research data, including appropriately licensed Hugging Face datasets. Public availability does not remove license, attribution, redistribution, privacy, or dataset-specific obligations. Verify that sending data to the selected provider is permitted. Public datasets can contain personal information; the hosting platform does not guarantee classification.

Use no-training routes by default. Training-enabled tiers require deliberate opt-in by Jimmy and the researcher after checking licensing and applicable U-M requirements. The synchronous example sets `data_collection: deny`; do not remove it casually. Verify Batch's provider/data handling separately. Approval to use a personal card does not itself approve restricted institutional data. Nonpublic institutional and sensitive data are outside this public-data workflow.

## Common errors

- **401:** missing, invalid, or revoked key. Check your environment variable, then ask Jimmy.
- **402:** insufficient shared credits or allowance. Jimmy checks both.
- **403:** policy/provider denial or forbidden operation. Research keys cannot administer keys.
- **429:** reduce concurrency; use bounded backoff for clearly rejected requests.
- **400/404:** check model ID, endpoint, parameters, and exact Batch support.
- **5xx/timeouts:** outcome may be uncertain. Inspect activity before repeating paid work.

Stop pending work before rotating keys. Already submitted batches and in-flight calls may still generate charges after disabling access.

## Jimmy's administration commands

Keep `management.key`, `state.json`, and handoff files in a private directory on Jimmy's Mac **outside this checkout**. Directory mode must be 700 and management credential mode 600. Back up state using an encrypted Jimmy-only backup: it preserves identity and cross-key spending history. Never put it in GitHub secrets, artifacts, or repository files.

```bash
export FORESEER_ADMIN_DIR='/absolute/path/to/private-admin-directory'
python3 admin.py list
python3 admin.py onboard UNIQNAME
python3 admin.py onboard UNIQNAME --apply
python3 admin.py limit UNIQNAME --allowance 150
python3 admin.py limit UNIQNAME --allowance 150 --apply
python3 admin.py rotate UNIQNAME
# Stop jobs, settle/cancel batches, and wait for billing to settle first:
python3 admin.py rotate UNIQNAME --drained --apply
python3 admin.py disable UNIQNAME
python3 admin.py disable UNIQNAME --apply
python3 admin.py report --output "$FORESEER_ADMIN_DIR/usage.csv"
```

Mutation commands preview until `--apply`. Read-only commands make authenticated API reads. Onboarding checks local state and remote identity prefixes; reruns do not create duplicate keys. The default is $100; `onboard --allowance AMOUNT` supplies an initial override. `limit` changes the stored policy. Offboarding disables access and retains history; also remove that person's GitHub read permission.

New secrets go only to mode-600 handoff files outside the checkout. Output contains only the filename. Jimmy delivers privately, confirms receipt, and removes the handoff copy. Nothing is sent automatically. Researchers never receive the management credential.

### Rotation and UTC rollover

Rotation disables the previous key first, then subtracts all retired keys' current-month usage from the replacement limit. A $100 user who spent $37.25 receives a $62.75 replacement cap. Further rotations keep subtracting prior-key usage. OpenRouter also enforces the active key's own usage. Cross-key billing cannot be transferred atomically while jobs are in flight, so `--drained` is required. Rerun sync after any delayed billing settles.

Normal keys reset automatically at midnight UTC on the first. **After rotation, the reduced cap persists until Jimmy runs sync after the next month begins:**

```bash
python3 admin.py sync UNIQNAME
python3 admin.py sync UNIQNAME --apply
```

Sync reads retired-key monthly counters and restores the configured allowance once they reset. Until then, the cap is conservatively lower. There is no server or scheduled job. Include rotated users in Jimmy's first-of-month checklist. Keep retired keys; deleting them breaks attribution.

### Uncertain API outcomes

The CLI saves a pending journal before creating a key and never retries creation automatically after a timeout/crash. Inspect OpenRouter keys and activity, then:

```bash
python3 admin.py reconcile
python3 admin.py reconcile --apply
```

Reconciliation searches the unique attempted name, disables matching keys, and clears the journal. One-time secrets cannot be recovered. A remaining disabled identity needs rotation; if no key was created, retry onboarding only after resolving uncertainty. A temporarily absent list result does not prove a timed-out creation will never complete. PATCH failures require reading current settings before rerunning the desired update. Use one Mac; a local lock serializes administration using this state directory.

### Billing and repository access

Export at month end **before** UTC counters reset. Reports are current-month snapshots, not historical billing records. They include retired-key usage. Reconcile against account activity, invoices/credit receipts, balance changes, fees, and timing differences. Credit purchases and inference consumption are separate accounting events. Jimmy retains receipts for the approved reimbursement process and adds funds manually. Keep auto-top-up off.

The private repository belongs to `umich-foreseer`. Jimmy's GitHub identity `xingjian-zhang` has admin rights; existing organization owners retain inherent access. Onboard researchers later with repository **read** access only. Do not change organization-wide defaults. No invitations, credit purchases, credential deliveries, or paid test inference are included in this initial rollout.

## References

- [Management API keys](https://openrouter.ai/docs/guides/overview/auth/management-api-keys)
- [Create API key](https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key)
- [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Batch beta](https://openrouter.ai/docs/batch-quickstart)
- [Current models and pricing](https://openrouter.ai/models)

Documentation checked September 2026. Recheck provider contracts before changing workflows.
