"""Build the static command-center dashboard.

A single self-contained ``index.html`` (inline CSS + a tiny bit of vanilla JS
for the SVG sparklines) that renders:

  * top-line KPIs,
  * a rep leaderboard (quota attainment),
  * revenue trend sparklines per rep,
  * the target pipeline by tier,
  * an optional embedded Power BI report (iframe) if you supply an embed URL.

No build step, no server, no external calls — open the file or drop it on any
static host (GitHub Pages, Netlify, SharePoint).
"""
from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..analysis.trends import TrendResult
from ..models import Target

_TEMPLATES = Path(__file__).parent / "templates"


def _sparkline_points(series: list[tuple[str, float]], w: int = 160, h: int = 40) -> str:
    vals = [v for _, v in series]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1.0
    n = len(vals)
    step = w / (n - 1) if n > 1 else 0
    pts = []
    for i, v in enumerate(vals):
        x = i * step
        y = h - ((v - lo) / span) * h
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def build_site(
    kpis: dict,
    attainment: dict,
    trends: list[TrendResult],
    targets: list[Target],
    out_dir: str | Path,
    title: str = "Sales Command Center",
    powerbi_embed_url: str = "",
    generated_at: str = "",
) -> str:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("dashboard.html.j2")

    # Rep leaderboard sorted by attainment.
    leaderboard = sorted(
        (
            {"rep": rep, **vals}
            for rep, vals in attainment.items()
        ),
        key=lambda r: (r.get("attainment_pct") or -1),
        reverse=True,
    )

    # Revenue sparklines per rep.
    rev_trends = [t for t in trends if t.metric == "revenue"]
    sparklines = [
        {
            "rep": t.rep,
            "latest": t.latest,
            "direction": t.direction,
            "mom": t.pop_change_pct,
            "points": _sparkline_points(t.series),
        }
        for t in sorted(rev_trends, key=lambda x: x.latest, reverse=True)
    ]

    # Pipeline by tier.
    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    tier_value = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0}
    for t in targets:
        tier_counts[t.tier] = tier_counts.get(t.tier, 0) + 1
        tier_value[t.tier] = tier_value.get(t.tier, 0.0) + t.est_annual_value

    top_targets = sorted(targets, key=lambda t: t.score, reverse=True)[:15]

    html = template.render(
        title=title,
        generated_at=generated_at,
        kpis=kpis,
        leaderboard=leaderboard,
        sparklines=sparklines,
        tier_counts=tier_counts,
        tier_value=tier_value,
        top_targets=top_targets,
        powerbi_embed_url=powerbi_embed_url,
    )
    index = out / "index.html"
    index.write_text(html)

    # Also drop the raw data as JSON for anyone who wants to build on it.
    (out / "data.json").write_text(json.dumps({
        "kpis": kpis,
        "attainment": attainment,
        "trends": [t.as_dict() for t in trends],
    }, indent=2, default=str))

    return str(index)
