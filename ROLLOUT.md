# Jimmy-first rollout

Verified 2026-09-06 with authenticated read-only requests after approved changes.

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

Dashboard verification: Umich Foreseer / Default workspace; Auto Top-Up shows **Enable** (off), with $25 available and one $25 transaction. Organization Members shows one member.

OpenRouter membership: exactly one member, Xingjian Zhang (`jimmyzxj@umich.edu`), role Admin. GitHub: repository is private; `xingjian-zhang` has admin access. Existing organization owner `Jn-Huang` retains inherent admin access. No pending repository invitations; organization default repository permission remains `none`.
