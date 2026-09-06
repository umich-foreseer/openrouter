# Admin runbook

This guide is for Jimmy (`jimmyzxj`), the sole OpenRouter administrator for the **Umich Foreseer** account and **Default** workspace. Use it to manage individual researcher keys, preserve spending attribution, and reconcile funding.

The [researcher guide](WIKI.md#your-allowance-and-the-shared-balance) is the authoritative statement of team allowances and permitted usage. This runbook describes how to implement that policy. Account balances and membership observations in the [rollout record](ROLLOUT.md) are historical; inspect live settings before acting.

## Prepare the local admin environment

Run the CLI on Jimmy's Mac with Python 3.10+. It uses only the standard library. Keep the following outside the checkout in a private local directory:

| File or directory | Purpose |
| --- | --- |
| `management.key` | Management credential; never distribute it |
| `state.json` | U-M uniqname mappings, key hashes, allowance overrides, retired-key history, and pending operations |
| `handoff/` | Temporary copies of newly issued research keys |

Use directory mode 700 and management-key mode 600. Back up state in an encrypted, Jimmy-only backup. Its history is necessary for attribution after key rotation. Never upload these files to GitHub, including secrets or Actions artifacts. Store your actual machine path and launcher instructions in a local setup note.

From the repository root, point the CLI to the existing private directory:

```bash
export FORESEER_ADMIN_DIR='/absolute/path/to/private-admin-directory'
python3 admin.py list
```

Replace the path; do not create a second state directory to work around an error. `list` shows configured allowances, current-month usage, active-key limits, and disabled status for locally registered researchers. It is not an inventory of every unregistered account key.

Mutations preview unless you pass `--apply`. Previews and reports can make authenticated read-only requests. Use one Mac and one state directory; the local lock serializes processes using that directory.

## Onboard a researcher

1. Obtain the researcher's U-M uniqname, GitHub username, project, intended models, and expected spending.
2. Preview the new identity and allowance, then apply it.
3. Deliver the key through an approved private channel, confirm receipt, and remove the handoff copy.
4. Grant repository read access and point the researcher to the usage guide.

```bash
python3 admin.py onboard UNIQNAME
python3 admin.py onboard UNIQNAME --apply
```

Replace `UNIQNAME` with the actual uniqname. The command uses the team default allowance. For an approved initial override, add `--allowance AMOUNT` to both preview and apply commands.

The CLI prints only a handoff filename and writes the credential there with mode 600. It does not deliver the key or grant GitHub access. Keep one active research key per person; never share a key between researchers or distribute the management credential.

Onboarding checks existing local identities and remote key-name prefixes. Repeating it for a registered researcher does not create a new key. If the key has been lost or disabled, use the replacement procedure. If remote identity exists but local state is missing, restore the state rather than creating another identity.

## Review usage and change an allowance

```bash
python3 admin.py list
python3 admin.py limit UNIQNAME --allowance AMOUNT
python3 admin.py limit UNIQNAME --allowance AMOUNT --apply
```

An override updates the stored allowance policy. The effective active-key cap accounts for usage on retired keys. Review the preview's proposed cap, then verify the result with `list`. Do not reset usage or create a replacement key to grant a budget increase.

## Replace a key

For planned rotation, have the researcher stop jobs, finish or cancel batches, and wait for usage to settle. If a key is exposed, disable it immediately using the offboarding command below; settle outstanding work before issuing its replacement.

```bash
python3 admin.py rotate UNIQNAME
python3 admin.py rotate UNIQNAME --drained --apply
```

`--drained` confirms that you have handled pending work; it does not check jobs automatically. Rotation disables the previous key first, then creates the replacement. Deliver and remove its handoff copy as for onboarding.

### How the remaining allowance is preserved

The replacement limit equals the configured monthly allowance minus all retired keys' current-month usage, floored at zero. If a researcher with a $100 allowance has spent $37.25, the replacement cap is $62.75. Further rotations continue to include earlier keys. OpenRouter separately enforces the active key's own spending against its cap.

Billing across keys cannot be transferred atomically while requests are in flight. Already submitted work can still incur charges; rerun sync after delayed usage settles. Keep retired keys and their local history so their spending remains available for accounting.

### Maintenance after the UTC month changes

Ordinary keys reset automatically according to the monthly policy. A replacement key retains its reduced cap until you synchronize it after the next UTC month begins:

```bash
python3 admin.py sync UNIQNAME
python3 admin.py sync UNIQNAME --apply
```

Sync reads retired-key monthly counters and recalculates the active cap. Once those counters reset, it restores the configured allowance. Until sync, the replacement's cap remains conservatively lower. There is no scheduled job: include every researcher with a rotated key in the first-of-month checklist. Sync does not re-enable disabled access.

## Disable access and offboard

```bash
python3 admin.py disable UNIQNAME
python3 admin.py disable UNIQNAME --apply
python3 admin.py list
```

Disable prevents new use of the key; it does not guarantee cancellation of already submitted work. Retain the identity and key history for reporting. Remove the person's repository access separately. Do not delete retired keys needed for attribution.

## Recover from an uncertain operation

Creation writes a pending journal before sending the API request. A timeout or crash may leave the outcome uncertain, so the CLI blocks further mutations and never automatically retries creation.

Inspect OpenRouter keys and activity, then preview reconciliation:

```bash
python3 admin.py reconcile
```

Once the provider's state is understood:

```bash
python3 admin.py reconcile --apply
```

Reconciliation searches the attempted unique key name, disables matching keys, and clears the journal. It cannot recover a one-time secret. If an identity remains with a disabled key, rotate it to issue a replacement. If no key was created, onboarding can be retried after resolving uncertainty.

A temporarily absent list result does not prove a timed-out creation will never complete. If uncertainty remains, stop and investigate before clearing the journal. Do not manually erase the journal to bypass recovery.

For an uncertain PATCH, read current settings and compare them with the intended change before rerunning it. Desired allowance policy is saved locally before the update, so sync can help recover an interrupted limit change. Restore missing local state from backup; avoid reconstructing spending history by guesswork.

## Funding and monthly reconciliation

Keep funding manual and auto-top-up disabled. Individual allowances do not reserve or replenish credits. For capacity planning, ten default allowances permit approximately $1,000/month of inference, but do not establish a separate shared cap. Check shared credits before large team runs and add funds manually as approved.

At month end, export usage **before midnight UTC on the first**:

```bash
python3 admin.py report --output "$FORESEER_ADMIN_DIR/usage-YYYY-MM.csv"
```

Replace `YYYY-MM` with the reporting month. The report includes registered researchers and their retired-key usage. It is a current-month snapshot, not a historical billing database. Preserve each export outside the repository.

Reconcile it against account activity, unregistered keys if any, invoices, credit receipts, balance changes, fees, and timing differences. Credit purchases and inference consumption are different accounting events. Keep receipts for the approved reimbursement process.

After the UTC reset, synchronize researchers with rotated keys and verify their effective limits. Check shared funds and resolve any pending operations before the next large experiment.

## Maintain the shared model list

Edit [models.json](models.json) to add or remove exact IDs, then increment `revision` and review the Git diff. Keep coverage broad across model families, affordable options, and useful research baselines. The list is shared configuration, not a ranking. Do not add wildcard routes, automatic model selection, or training-enabled tiers without the relevant review.

Before committing, check new IDs against the public [OpenRouter catalog](https://openrouter.ai/api/v1/models), examine current provider/data-handling options and prices, and confirm the intended endpoint supports the model. The catalog check establishes that an ID is listed; it does not verify Batch or every provider route. Update `catalog_checked_on` only after checking the full list. Never auto-add everything from the catalog.

Run `python3 -m json.tool models.json` to inspect the file and `python3 -m unittest discover -s tests -v` to check the examples. Neither command calls OpenRouter. Publish the reviewed change and tell researchers to update before new runs. Preserve the repository commit used by ongoing experiments; coordinate removals instead of silently switching their models.

`request_defaults` controls the examples' initial output limit. `sync_routing` contains provider fallback and data-collection defaults; these do not apply automatically to Batch. Account-level guardrails have not been configured from this file. The existing key-management CLI remains an admin-only tool and is not required for normal inference.

## Repository permissions

Jimmy's GitHub identity is `xingjian-zhang`. Give researchers repository **read** access only. Keep the repository private and leave organization-wide permissions unchanged. Existing organization owners retain their inherent access; sole OpenRouter administration does not remove that GitHub access.

## References and checks

- [Management API keys](https://openrouter.ai/docs/guides/overview/auth/management-api-keys)
- [Create API key](https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key)
- [Historical rollout verification](ROLLOUT.md)

Run mocked CLI tests from the repository root with `python3 -m unittest discover -s tests -v`. They do not create real keys or run paid inference. Inspect live settings when verifying a real administrative change.
