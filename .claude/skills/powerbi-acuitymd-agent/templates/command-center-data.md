# Command-center data contract

**Live site:** https://imsc-sales-command-center.netlify.app/ (Netlify).

The command-center website is fed by a single JSON file, `command-center-data.json`,
produced by `/pbi-acuity command-center`.

> **Confirm the real contract before first use.** The shape below is a starting
> scaffold, not the site's confirmed schema. In a session where the site's
> **source repo** is available (add it to scope, or open the Netlify project),
> read how the app loads data — the exact file path it fetches (commonly
> `public/data/*.json` or `src/data/*.json` in a Vite/React build) and the exact
> field names/`id`s each widget reads. Then **rewrite this file to match** so the
> agent and the site never drift. Everything below is provisional until you've
> done that.

## JSON shape

```json
{
  "generated_at": "2026-07-25T14:00:00Z",
  "period": "FY26 · through Jul",
  "kpis": [
    { "id": "revenue_ytd",   "label": "Revenue YTD",   "value": 4820000, "format": "currency", "delta_pct": 12.4, "target": 5000000 },
    { "id": "attainment",    "label": "Plan Attainment","value": 0.964,   "format": "percent",  "delta_pct": 3.1,  "target": 1.0 },
    { "id": "cases_ytd",     "label": "Cases YTD",      "value": 1382,    "format": "number",   "delta_pct": 8.0,  "target": null },
    { "id": "new_accounts",  "label": "New Accounts",   "value": 17,      "format": "number",   "delta_pct": 21.0, "target": 20 }
  ],
  "reps": [
    { "name": "Rep A", "revenue_ytd": 1250000, "attainment": 1.04, "yoy_pct": 9.2, "top_account": "…" }
  ],
  "products": [
    { "category": "Line 1", "revenue_ytd": 2100000, "share_pct": 43.6, "trend": "up" }
  ],
  "watch_list": [
    { "type": "account", "name": "…", "issue": "revenue down 3 months", "owner": "Rep A" }
  ],
  "targets_summary": { "open_targets": 42, "high_priority": 11, "source": "AcuityMD" }
}
```

### Rules
- `generated_at` is UTC ISO-8601. The site shows freshness from it.
- Every `kpis[].value` is a real Power BI value. If a query failed, **omit that
  KPI and add it to a top-level `"errors": []` array** — never ship a fake value.
- `format` is one of `currency | percent | number`. `delta_pct` is vs. prior
  period; `null` if unknown. `target` may be `null`.
- Keep `id`s stable — the site keys off them.

## Building it
1. Run the command-center DAX from `references/powerbi-connection.md`.
2. Map rows into the shape above.
3. Validate: JSON parses, no KPI missing a value, `generated_at` set.
4. Write `command-center-data.json`.

## Publishing (Netlify)

The site is hosted on Netlify. Two ways to update it — both are outward actions,
so **confirm with the user before pushing to production.**

1. **Git-based deploy (preferred if the site auto-deploys from a repo).**
   Commit the refreshed `command-center-data.json` into the site's source repo
   at the exact path the app fetches (confirm it from the source — often
   `public/data/command-center-data.json` in a Vite/React build). Push to the
   branch Netlify builds; the deploy picks it up automatically. This keeps a
   version history of the numbers.
2. **Netlify deploy of the data (no repo access, or data-only update).**
   Use the Netlify tools/CLI to deploy the file to the site. Identify the
   Netlify project for `imsc-sales-command-center`, then deploy the JSON to the
   path the app reads. Verify the live site shows the new `generated_at` after
   the deploy finishes.

After publishing, load the live URL and confirm the KPIs and freshness stamp
updated. If a KPI failed to load, it should be absent + listed in `errors`,
never shown as a fake value.
