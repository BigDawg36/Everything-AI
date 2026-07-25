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
- **AcuityMD** → the **API** if your org has it provisioned (ask your CSM), with
  a **Playwright browser-login fallback** that reuses a saved session for orgs
  without API access.

## Notes

- **Real data only** — every number traces to a query/pull; nothing is invented.
- Secrets stay in the environment/`.env`; `.env` and all data exports are
  git-ignored. See `references/security.md`.
- AcuityMD endpoint paths in `scripts/acuitymd_client.py` are placeholders —
  confirm and edit them against your tenant's API docs (one line per endpoint).

See `SKILL.md` for the full agent playbook.
