# Power BI connection

Power BI is authenticated through **Microsoft Entra ID (Azure AD)**. All data
reads go through the **Power BI REST API** — specifically the `executeQueries`
(DAX) endpoint for numbers and the `ExportTo` endpoint for rendered
reports/pages.

There are two auth modes. Pick based on what the org allows.

---

## Mode A — Service principal (recommended for automation)

Best for an unattended agent. No interactive login, no MFA prompts.

**One-time setup (needs an Entra admin + a Power BI admin):**

1. Entra ID → **App registrations** → *New registration*. Note the
   **Application (client) ID** and **Directory (tenant) ID**.
2. *Certificates & secrets* → new **client secret**. Copy it once.
3. Power BI Admin portal → *Tenant settings* → **"Allow service principals to
   use Power BI APIs"** → enable (usually scoped to a security group; add the app
   to that group).
4. In each Power BI **workspace** the agent needs: *Access* → add the app as
   **Member** or **Contributor**.

**Environment variables** (see `.env.example`):

```
PBI_TENANT_ID=...
PBI_CLIENT_ID=...
PBI_CLIENT_SECRET=...
PBI_WORKSPACE_ID=...        # the "group" GUID; optional if using My workspace
PBI_DATASET_ID=...          # default dataset (semantic model) for DAX queries
```

Token request (client-credentials flow):
- Authority: `https://login.microsoftonline.com/{PBI_TENANT_ID}`
- Scope: `https://analysis.windows.net/powerbi/api/.default`

`scripts/powerbi_client.py` does this with MSAL (`acquire_token_for_client`).

---

## Mode B — Delegated / device-code (when service principals are blocked)

Signs in as the user, no stored password, MFA-friendly. Good when IT won't
provision a service principal.

```
PBI_TENANT_ID=...
PBI_CLIENT_ID=...           # a public client app registration (or the Power BI CLI app id)
# no secret; the script prints a code + URL for the user to complete sign-in
```

The script uses MSAL `acquire_token_by_device_flow` with scope
`https://analysis.windows.net/powerbi/api/.default`. The token is cached to
`~/.pbi_token_cache.json` so the user isn't prompted every run.

> Avoid Resource-Owner-Password (username/password) flow — it breaks under MFA
> and is being deprecated. Prefer A or B.

---

## Reading data: DAX via `executeQueries`

```
POST https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}/executeQueries
Authorization: Bearer <token>
Content-Type: application/json

{ "queries": [ { "query": "EVALUATE <DAX table expression>" } ],
  "serializerSettings": { "includeNulls": true } }
```

- Body must return a **table** — wrap measures in `ROW(...)` or `SUMMARIZECOLUMNS(...)`.
- Max 1,000,000 values or 15MB per response; page large pulls by date.
- If the dataset is in a workspace, the `datasetId` is enough — you don't need
  the workspace in the URL for `executeQueries`.

### Command-center queries

Adapt table/measure names to the actual semantic model (ask the user, or list
tables with `EVALUATE INFO.TABLES()` / `EVALUATE COLUMNSTATISTICS()`). Examples:

```dax
// Territory revenue vs. plan, current + prior year
EVALUATE
SUMMARIZECOLUMNS(
    'Rep'[RepName],
    "Revenue_YTD",  [Revenue YTD],
    "Plan_YTD",     [Plan YTD],
    "Attainment",   DIVIDE([Revenue YTD], [Plan YTD]),
    "Revenue_PY",   [Revenue YTD PY]
)
```

```dax
// Trailing 13-month territory time series for trend analysis
EVALUATE
SUMMARIZECOLUMNS(
    'Date'[YearMonth],
    'Product'[Category],
    "Revenue", [Revenue],
    "Cases",   [Case Count],
    FILTER( ALL('Date'), 'Date'[Date] >= EDATE( TODAY(), -13 ) )
)
ORDER BY 'Date'[YearMonth]
```

```dax
// Top / bottom accounts for a rep (parameterize @rep before sending)
EVALUATE
TOPN( 25,
    SUMMARIZECOLUMNS('Account'[AccountName],
        FILTER('Rep', 'Rep'[RepName] = "REP_NAME_HERE"),
        "Revenue", [Revenue] ),
    [Revenue], DESC )
```

Keep the exact DAX you sent in the report footer so results are reproducible.

## Exporting a rendered report/page

For a pixel-perfect PDF/PPTX/PNG of an existing report:

```
POST /v1.0/myorg/reports/{reportId}/ExportTo   { "format": "PDF" }
GET  /v1.0/myorg/reports/{reportId}/exports/{exportId}   # poll until status = Succeeded
GET  /v1.0/myorg/reports/{reportId}/exports/{exportId}/file
```

Use this when the user wants "the actual dashboard as a PDF" rather than
recomputed numbers.

## Useful discovery endpoints

- `GET /v1.0/myorg/groups` — list workspaces (find `PBI_WORKSPACE_ID`).
- `GET /v1.0/myorg/groups/{groupId}/datasets` — list datasets (find `PBI_DATASET_ID`).
- `GET /v1.0/myorg/groups/{groupId}/reports` — list reports (find `reportId`).

## Troubleshooting

- **401** → token scope wrong or app not added to the workspace.
- **403 on executeQueries** → dataset owner must enable *"Dataset Execute
  Queries REST API"* in tenant settings; XMLA read may need Premium/PPU.
- **404 dataset** → it's in a workspace you weren't granted; add the SP/user.
- **DAX error "not a table"** → wrap scalars in `ROW("name", <measure>)`.
