# Initial rollout record — 2026-09-06

This is a historical verification record, not a live account-status page. The balances, limits, permissions, and membership below describe the initial rollout on September 6, 2026. This documentation rewrite did not repeat those account checks.

Implementation recorded in commit `51dfc28c063642b45417205471ae3bc0bf312297`. At that point, 10 mocked CLI tests passed, the deliverable credential scan passed, and the published commit matched the local checkout. No live paid inference test was performed.

For everyday use, see the [researcher guide](WIKI.md). For current operating procedures, see the [admin runbook](ADMIN.md).

## API observations

Verified with authenticated read-only requests after the approved key-setting changes.

```json
{
  "keys": [
    {
      "name": "jimmy-research",
      "limit": 100,
      "limit_reset": "monthly",
      "disabled": false,
      "usage_monthly": 0
    },
    {
      "name": "Default key",
      "limit": null,
      "limit_reset": null,
      "disabled": true,
      "usage_monthly": 0
    }
  ],
  "credits": {
    "total_credits": 25,
    "total_usage": 0
  },
  "research_management_denied_http": "401"
}
```

The research key authenticates successfully to its own `/key` endpoint but is denied on management `/keys`. No paid inference, credit purchases, researcher invitations, or credential deliveries were performed. Private admin state maps `jimmyzxj` to the existing research key.

## Dashboard and GitHub observations

Dashboard verification: Umich Foreseer / Default workspace; Auto Top-Up shows **Enable** (off), with $25 available and one $25 transaction. Organization Members shows one member.

OpenRouter membership: exactly one member, Xingjian Zhang (`jimmyzxj@umich.edu`), role Admin. GitHub: repository is private; `xingjian-zhang` has admin access. Existing organization owner `Jn-Huang` retains inherent admin access. No pending repository invitations; organization default repository permission remains `none`.
