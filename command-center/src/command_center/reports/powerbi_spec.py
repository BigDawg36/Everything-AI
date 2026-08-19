"""Generate Power BI-ready artifacts from the tidy data.

Because we only have web logins (no Power BI REST API / service principal), we
do NOT push reports into the service programmatically. Instead we generate
everything a person needs to build the report **once** in Power BI Desktop and
then reuse forever:

  * a clean star-schema CSV/table layout,
  * a ``model.json`` describing tables + relationships,
  * a ``measures.dax`` file with ready-to-paste DAX measures,
  * a ``report-layout.md`` describing the pages/visuals to drop in.

Paste the DAX, wire the CSVs as data sources, and the command-center report is
built. Re-exporting fresh CSVs and hitting Refresh keeps it current.
"""
from __future__ import annotations

import json
from pathlib import Path

MEASURES = [
    ("Total Revenue", "SUM(Metrics[value])", "Filtered to metric = \"revenue\" via the report filter."),
    ("Revenue YTD", "TOTALYTD([Total Revenue], 'Calendar'[Date])", "Year-to-date revenue."),
    ("Quota", "SUM(Reps[quota])", "Annualized quota rollup."),
    ("Quota Attainment %", "DIVIDE([Revenue YTD], [Quota], 0)", "Format as percentage."),
    ("Revenue MoM %", "VAR cur = [Total Revenue] VAR prev = CALCULATE([Total Revenue], DATEADD('Calendar'[Date], -1, MONTH)) RETURN DIVIDE(cur - prev, prev)", "Month-over-month growth."),
    ("Open Pipeline", "SUMX(FILTER(Targets, Targets[status] = \"prospect\"), Targets[est_annual_value])", "Sum of A/B/C prospect opportunity."),
    ("A-Tier Targets", "CALCULATE(COUNTROWS(Targets), Targets[tier] = \"A\")", "Count of top-priority targets."),
    ("Avg Deal Size", "DIVIDE([Total Revenue], DISTINCTCOUNT(Metrics[rep]))", "Rough per-rep average; refine per your CRM."),
]


def build_powerbi_spec(out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Semantic model description (tables + relationships).
    model = {
        "name": "Sales Command Center",
        "tables": [
            {
                "name": "Metrics",
                "source": "metrics.csv",
                "columns": [
                    {"name": "period", "dataType": "dateTime"},
                    {"name": "rep", "dataType": "string"},
                    {"name": "metric", "dataType": "string"},
                    {"name": "value", "dataType": "double"},
                    {"name": "territory", "dataType": "string"},
                ],
            },
            {
                "name": "Targets",
                "source": "targets_scored.csv",
                "columns": [
                    {"name": "name", "dataType": "string"},
                    {"name": "npi", "dataType": "string"},
                    {"name": "rep", "dataType": "string"},
                    {"name": "territory", "dataType": "string"},
                    {"name": "est_annual_value", "dataType": "double"},
                    {"name": "status", "dataType": "string"},
                    {"name": "tier", "dataType": "string"},
                    {"name": "score", "dataType": "double"},
                ],
            },
            {
                "name": "Reps",
                "source": "reps.csv",
                "columns": [
                    {"name": "name", "dataType": "string"},
                    {"name": "territory", "dataType": "string"},
                    {"name": "quota", "dataType": "double"},
                    {"name": "manager", "dataType": "string"},
                ],
            },
            {
                "name": "Calendar",
                "source": "(Power BI generated date table)",
                "columns": [{"name": "Date", "dataType": "dateTime"}],
            },
        ],
        "relationships": [
            {"from": "Metrics[rep]", "to": "Reps[name]", "cardinality": "many-to-one"},
            {"from": "Targets[rep]", "to": "Reps[name]", "cardinality": "many-to-one"},
            {"from": "Metrics[period]", "to": "Calendar[Date]", "cardinality": "many-to-one"},
        ],
    }
    (out / "model.json").write_text(json.dumps(model, indent=2))

    # 2. DAX measures, ready to paste.
    dax_lines = ["// Paste each measure into Power BI (Modeling > New Measure).", ""]
    for name, expr, note in MEASURES:
        dax_lines.append(f"// {note}")
        dax_lines.append(f"{name} = {expr}")
        dax_lines.append("")
    (out / "measures.dax").write_text("\n".join(dax_lines))

    # 3. Report page layout guide.
    layout = _layout_md()
    (out / "report-layout.md").write_text(layout)

    return {
        "model": str(out / "model.json"),
        "measures": str(out / "measures.dax"),
        "layout": str(out / "report-layout.md"),
        "measure_count": len(MEASURES),
    }


def _layout_md() -> str:
    return """# Power BI Report Layout — Sales Command Center

Build this once in Power BI Desktop, publish to your workspace, and refresh by
re-exporting the CSVs the command center writes.

## Data setup
1. Get Data > Text/CSV for `metrics.csv`, `targets_scored.csv`, `reps.csv`.
2. Modeling > New Table > `Calendar = CALENDARAUTO()` (or a marked date table).
3. Create the relationships in `model.json`.
4. Paste every measure from `measures.dax`.

## Page 1 — Command Center (executive)
- KPI cards: **Revenue YTD**, **Quota Attainment %**, **Open Pipeline**, **A-Tier Targets**.
- Line chart: Total Revenue by `Calendar[Date]` (trend).
- Bar chart: Quota Attainment % by `Reps[name]` (sorted descending).
- Map or bar: Open Pipeline by `territory`.
- Slicers: `territory`, `period`.

## Page 2 — Rep Scorecard (one rep at a time)
- Slicer: `Reps[name]` (single select).
- KPI cards: Revenue YTD, Quota Attainment %, Revenue MoM %.
- Line chart: rep revenue vs. a target line.
- Table: top targets (name, tier, score, est_annual_value, status) sorted by score.

## Page 3 — Target Pipeline
- Table/matrix: Targets by tier and status.
- Scatter: `procedure_volume` (x) vs `est_annual_value` (y), size = score, color = tier.
- Card: A-Tier Targets; bar: count by rep.

## Publishing / embedding the command center website
- File > Publish to your Power BI workspace.
- Use **Publish to web** (public) or **Embed** (secure) to surface the report
  inside the command-center site the app generates. Paste the embed iframe into
  `site/config` — see the app README.
"""
