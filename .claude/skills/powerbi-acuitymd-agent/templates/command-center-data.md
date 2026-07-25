# Command-center data contract

The command-center website is fed by a single JSON file, `command-center-data.json`,
produced by `/pbi-acuity command-center`. This documents the shape the site
expects. **Confirm the real contract with whoever owns the site** before wiring
it up — then lock this file to match, so the agent and the site never drift.

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

## Publishing
- **If the site is a repo/static host:** place the JSON at the path the site
  reads (ask the owner; often `public/data/` or an API route), commit, and let
  the site's deploy pick it up. Confirm with the user before pushing to a live
  branch.
- **If the site has an upload endpoint:** POST the JSON there.
- **Otherwise:** leave the file and tell the user the exact deploy step.
- Publishing is an outward action — confirm before pushing to production.
