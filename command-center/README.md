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
| Validate & enrich targets | Free public **NPPES NPI registry** — catches typo'd NPIs, corrects specialties, fills address/phone |
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
    │   ├── scoring.py          weighted 0-100 target score + tiers + profiles
    │   └── trends.py           slope/MoM/forecast/anomaly + quota attainment
    ├── enrich/
    │   └── npi.py              NPI Luhn validation + NPPES registry enrichment
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

## Validating targets against the NPI registry

Run this *before* scoring — it catches bad data at the source:

```bash
PYTHONPATH=src python -m command_center --targets data/raw/acuitymd_targets.csv \
  --out data/out enrich
```

Every target lands in one of four honest states:

| State | Meaning | What to do |
|---|---|---|
| `verified` | Found in NPPES; specialty/address/phone merged in | Nothing — trust it |
| `not_found` | Well-formed NPI, no registry record | Have the rep confirm |
| `invalid` | Fails the check digit | It's a **typo** — fix at the source |
| `unchecked` | NPPES unreachable (proxy/offline) | Format validated only |

The app calls the **public NPPES API** directly — free, no key, no auth. If your
network blocks it, enrichment degrades to validation-only rather than crashing;
you can also supply pre-fetched records:

```bash
... enrich --npi-data npi_records.json --offline
```

> **NPPES gotcha:** the registry spells the surgical taxonomy **"Orthopaedic
> Surgery"**. Searching `"Orthopedic Surgery"` returns *zero* results —
> "Orthopedic" appears only in physical-therapy/chiropractic taxonomies.
> `normalize_taxonomy()` maps the common colloquial names for you.

The bundled `sample_data/acuitymd_targets.csv` is fictional; its NPIs are
synthetic (they won't resolve in NPPES), and one is *deliberately* given a bad
check digit so `enrich` has a real typo to catch.

## Scoring profiles

The right weighting genuinely differs by what you sell. Pick the closest:

| Profile | For | Weights toward |
|---|---|---|
| `balanced` | general purpose (default) | even blend |
| `implant` | high-ASP constructs | deal size + displacing the incumbent |
| `capital` | long-cycle equipment | opportunity size + growth |
| `disposable` | consumables | case volume + share-of-wallet conversion |
| `service_line` | hospital partnerships | growth + engagement recency |

```bash
... --profile capital targets      # one-off override
```

Or set `scoring.profile` in `config/settings.yaml` as the default, with an
optional `scoring.weights` block to hand-tune individual numbers. An explicit
`--profile` flag wins outright — settings `weights` are ignored for that run, so
the flag can never be a silent no-op.

These are not cosmetic: on the sample data, a low-volume/high-value/fast-growing
target ranks **#6 (D-tier)** under `disposable` but **#3 (B-tier)** under
`capital`.

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
