# powerbi-acuitymd-agent

A Claude Code skill that turns Claude into a **medtech sales command-center
agent**. It connects to **AcuityMD** (target/account intelligence) and
**Microsoft Power BI** (sales data of record) and produces:

- ranked **target lists** for reps (AcuityMD, cross-referenced against Power BI),
- **command-center** dashboard data (Power BI KPIs → a JSON contract the site reads),
- **per-rep** sales reports,
- **trend** analysis across the territory.

## Quick start

1. `cd .claude/skills/powerbi-acuitymd-agent/scripts && pip install -r requirements.txt`
2. Copy `.env.example` → `.env` and fill in Power BI + AcuityMD credentials
   (see `references/powerbi-connection.md` and `references/acuitymd-connection.md`).
3. In Claude Code, run `/pbi-acuity connect` to verify both platforms, then any of:
   - `/pbi-acuity targets --territory "SoCal"`
   - `/pbi-acuity command-center`
   - `/pbi-acuity rep-report "Jane Smith"`
   - `/pbi-acuity trends`
   - `/pbi-acuity brief`

## How access works

- **Power BI** → official REST API via Entra ID. Use a **service principal**
  (unattended) or **device-code** sign-in (MFA-friendly). Reads run through the
  `executeQueries` (DAX) endpoint; rendered exports via `ExportTo`.
- **AcuityMD** → **Playwright browser login + export** (this org has no AcuityMD
  API). Log in once interactively to clear SSO/MFA; the session is saved and
  reused, then list exports are downloaded as CSV/XLSX. (An API path exists in
  the code for later, if an entitlement is ever added.)

The command center is the Netlify site
**https://imsc-sales-command-center.netlify.app/**; `/pbi-acuity command-center`
produces the JSON it reads and can publish via Netlify.

## Notes

- **Real data only** — every number traces to a query/pull; nothing is invented.
- Secrets stay in the environment/`.env`; `.env` and all data exports are
  git-ignored. See `references/security.md`.
- AcuityMD endpoint paths in `scripts/acuitymd_client.py` are placeholders —
  confirm and edit them against your tenant's API docs (one line per endpoint).

See `SKILL.md` for the full agent playbook.
