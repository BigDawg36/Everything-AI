# Sales Command Center — AcuityMD + Power BI

A sales-operations toolkit for medical-device teams. It turns an **AcuityMD**
target list and **Power BI** sales metrics into scored targets, per-rep report
packs, a Power BI report spec, and a self-contained **command-center website**.

It ships two ways, deliberately:

- **Now — a Claude skill.** `.claude/skills/command-center/` drives this app
  conversationally ("find me targets," "make rep reports," "update the command
  center"). Start there.
- **Later — a standalone app.** This folder is a normal Python package you can
  run on a schedule, in CI, or from a cron — no Claude required.

## The one thing to understand: it never stores your logins

You told us you have **web logins only** for AcuityMD and Power BI — no API keys,
no service principal. So the tool does **not** ask for, type, or store your
passwords. Instead:

1. The browser layer opens a real Chromium window using a *persistent profile*.
2. **You** log in once — SSO, MFA, all of it.
3. The browser keeps its own session cookies in that profile (under
   `data/profiles/`, gitignored). Later runs reuse it, so pulls can run headless.

If a login screen ever appears mid-run, the tool stops and asks you to sign in
interactively. Credentials are never handled by any code here.

## What it does (and doesn't)

| Capability | How |
|---|---|
| Find & prioritize AcuityMD targets | Browser-pull or CSV export → transparent 0-100 score + A/B/C/D tiers |
| Analyze sales trends | Per-(rep, metric) direction, MoM change, forecast, anomaly flags |
| Per-rep reports | Markdown pack: quota attainment, trends, "what to focus on," top targets |
| Power BI report | **Generates** `model.json` + `measures.dax` + `report-layout.md` to build once in Power BI Desktop; automates the repeatable data export |
| Command-center website | Self-contained `index.html` dashboard, optional embedded Power BI report |

**Not in scope (web-login-only reality):** no AcuityMD API, no Power BI REST
publishing, no clicking-together of Power BI report visuals through a browser.
Report *structure* is authored once by hand from the generated spec; everything
downstream refreshes from re-exported CSVs.

## Architecture

```
command-center/
├── config/                     reps + settings (YAML; *.example.yaml checked in)
├── sample_data/                runnable example CSVs
├── data/                       gitignored: pulls, browser profiles, outputs
└── src/command_center/
    ├── models.py               Target / Metric / Rep (tolerant CSV parsing)
    ├── ingest.py               CSV/YAML → models (tidy + wide-format metrics)
    ├── analysis/
    │   ├── scoring.py          weighted 0-100 target score + tiers
    │   └── trends.py           slope/MoM/forecast/anomaly + quota attainment
    ├── reports/
    │   ├── rep_report.py       per-rep Markdown packs
    │   └── powerbi_spec.py     model.json + measures.dax + layout guide
    ├── site/                   Jinja2 → static command-center dashboard
    ├── browser/                OPTIONAL Playwright layer (session + navigators)
    └── cli.py                  `python -m command_center ...`
```

The **analysis / reports / site** layers depend only on the Python standard
library + PyYAML + Jinja2 — they run anywhere, no browser, no cloud creds. The
**browser** layer (Playwright) is optional and only needed for `pull`.

## Quick start

```bash
cd command-center
pip install -r requirements.txt              # PyYAML + Jinja2

# See it work on the bundled sample data:
PYTHONPATH=src python -m command_center \
  --targets sample_data/acuitymd_targets.csv \
  --metrics sample_data/powerbi_metrics.csv \
  --reps    config/reps.example.yaml \
  --settings config/settings.example.yaml \
  --out data/out \
  build

open data/out/site/index.html                # the command center
ls  data/out/rep_reports/                     # per-rep packs
cat data/out/powerbi/report-layout.md         # how to build the Power BI report
```

Then copy the example configs and point them at your team:

```bash
cp config/reps.example.yaml config/reps.yaml
cp config/settings.example.yaml config/settings.yaml
```

## Pulling live data (optional browser layer)

```bash
pip install playwright
# Chromium is preinstalled in Claude web environments; elsewhere:
# playwright install chromium

# AcuityMD — first run opens a window; log in, then it exports your view:
PYTHONPATH=src python -m command_center --settings config/settings.yaml \
  pull acuitymd --url "https://app.acuitymd.com/<your-saved-view>"

# Power BI — export one visual's underlying data:
PYTHONPATH=src python -m command_center --settings config/settings.yaml \
  pull powerbi --url "https://app.powerbi.com/<report>" \
  --visual-selector "button[aria-label='More options']"
```

Selectors in `config/settings.yaml` are account/version specific — inspect the
page and adjust if a control isn't found.

## Data formats

- **AcuityMD targets CSV** — flexible columns; the parser matches common names
  (`name`/`physician`, `npi`, `est_annual_value`/`opportunity`,
  `procedure_volume`/`cases`, `competitor_share`, `growth_rate`, `rep`,
  `territory`, `status`, `last_touch`). See `sample_data/acuitymd_targets.csv`.
- **Power BI metrics CSV** — either *tidy* (`period, rep, metric, value`) or
  *wide* (`period, rep, revenue, cases, ...`); wide is auto-melted. See
  `sample_data/powerbi_metrics.csv`.
- **reps.yaml** — roster with `territory`, `quota`, `email`, `manager`.

## Roadmap (the "app later" part)
- Scheduled refresh (cron / GitHub Action) once a saved browser session exists.
- Swap the browser export for the Power BI REST API / AcuityMD API if the team
  gains programmatic access — only the `browser/` and `ingest/` seams change.
- Push per-rep packs to email/Slack; write the site to a hosting target.
