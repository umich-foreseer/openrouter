# Admin guide

This guide is for administrators of **Umich Foreseer / Default Workspace**. Manage the team through OpenRouter's website. Researchers join as Members and manage their own keys; no local administration CLI is required.

## Invite and assign a budget

1. Obtain the researcher's uniqname, OpenRouter email, GitHub username, project, and expected spending. Check for any previously issued keys.
2. Explain that members can see each other's usage metadata in organization Activity, including models, costs, and request times. Arrange for the researcher to accept the invitation while you are available to assign the budget. Ask them to wait for confirmation before using the account; this request does not technically prevent spending before assignment.
3. Invite them with the **Member** role, not the Admin role, from [Members](https://openrouter.ai/settings/organization-members).
4. After acceptance, assign **Foreseer Member — $100/month** from [Guardrails](https://openrouter.ai/workspaces/default/guardrails) to the correct member account. Reopen the settings to verify the assignment, amount, and monthly reset.
5. Confirm that the budget is active, then have them create a key in the organization's Default Workspace. Verify member ownership without requesting the secret. Grant repository read access and send them the [researcher guide](WIKI.md).

Creating a Guardrail does not apply it to anyone. The prepared rule is for explicit member assignment, not the workspace default. Each member assigned the same rule receives a separate $100/month allowance across their own keys and chatroom usage. Individual key caps also apply. See [Guardrails](https://openrouter.ai/docs/guides/features/guardrails).

There is no team model allowlist. Keep model selection open while retaining spending and data-handling policies. The prepared rule covers OpenRouter credit spend, not external BYOK spend; review accounting separately before introducing BYOK.

For a different allowance, create or reuse a rule for that amount and assign it to that person. Do not edit a shared rule to change only one member. Each member can have at most one directly assigned Guardrail; preserve existing restrictions when replacing it, and verify current-period usage rather than assuming reassignment resets spending.

## Review usage and funding

Use [Activity](https://openrouter.ai/activity) with a defined reporting period:

- **Creator**: member spending across their keys.
- **API Key**: individual keys, including older administrator-issued keys.
- **Model**: model costs for a selected member or key.

Check the assigned Guardrail for the allowance. Export Spend, Tokens, and Requests as CSV/PDF for monthly reconciliation; see [Activity Export](https://openrouter.ai/docs/cookbook/administration/activity-export). Do not add overlapping Creator and Key totals together.

Keep funding manual and auto-top-up disabled. Per-member budgets do not reserve credits or establish a shared account cap. Check [Credits](https://openrouter.ai/settings/credits) before large runs. Reconcile consumption against credit purchases, invoices, fees, and timing differences; retain receipts for reimbursement.

## Existing access and offboarding

The administrator's existing research key retains its current spending limit. The former local CLI is retired. Existing private management credentials, state, and key records remain outside this repository; keep them private and backed up. Old launcher/setup notes refer to the retired tool and should no longer be used. Do not reconstruct or delete private records merely because the code was removed.

If a future member already has an administrator-issued key, stop new requests, finish or cancel outstanding jobs, disable the old key, wait for charges to settle, and export its current-month spending. Neither a key name nor organization membership transfers ownership or old spending. For a member account with no previous usage, assign a temporary allowance equal to the approved budget minus settled legacy spending. Account for any other access before enabling use. If no allowance remains, defer activation until the next period; do not assume that a zero budget blocks access without verifying it. Restore the standard member budget manually at the start of the next UTC calendar month and reconcile delayed charges.

For offboarding, disable the person's keys, coordinate outstanding work, export usage history, and remove organization and repository access. Check the platform's current removal requirements before deleting keys; preserve attribution evidence. Disabling access does not guarantee cancellation of submitted work.

Keep the GitHub repository private and give researchers read access only. Existing organization owners retain their inherent GitHub permissions.

## Verification and preparation record

On 2026-09-06, **Foreseer Member — $100/month** was created and verified in Default Workspace, with no members or keys assigned. The organization retained a single Admin, the existing keys and workspace default rule were unchanged, and auto-top-up was off. No invitations or paid inference were performed. Recheck live state before onboarding.

When onboarding the first researcher, verify their role, budget assignment, key ownership, and usage attribution in Activity. Checking saved settings does not establish that budget enforcement has been tested with real requests. Do not intentionally exhaust a budget to test the cap.

The [initial rollout record](ROLLOUT.md) describes the earlier setup and retired CLI; it is historical evidence, not current operating instructions. Run `python3 -m unittest discover -s tests -v` for mocked example checks. No tests call OpenRouter.
