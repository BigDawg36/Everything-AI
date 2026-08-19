"""Per-rep report packs.

For each rep we produce a self-contained Markdown briefing: quota attainment,
metric trends (with direction + forecast), anomalies to explain, and their top
scored targets to work next. These are the "specific reports for each rep" a
manager hands out in a 1:1.
"""
from __future__ import annotations

from pathlib import Path

from ..analysis.trends import TrendResult
from ..models import Rep, Target

_ARROW = {"up": "↑", "down": "↓", "flat": "→"}


def _fmt_money(v: float) -> str:
    return f"${v:,.0f}"


def _fmt_pct(v) -> str:
    return "n/a" if v is None else f"{v:+.1f}%"


def build_rep_report(
    rep: Rep,
    trends: list[TrendResult],
    targets: list[Target],
    attainment: dict,
    out_dir: str | Path,
) -> str:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rep_trends = [t for t in trends if t.rep == rep.name]
    rep_targets = [t for t in targets if t.rep == rep.name]
    att = attainment.get(rep.name, {})

    lines: list[str] = []
    lines.append(f"# Rep Report — {rep.name}")
    lines.append("")
    lines.append(f"**Territory:** {rep.territory or 'n/a'}  |  **Manager:** {rep.manager or 'n/a'}")
    lines.append("")

    # Quota block
    lines.append("## Quota attainment")
    if att:
        lines.append("")
        lines.append("| Actual (YTD) | Quota | Attainment | Gap |")
        lines.append("|---|---|---|---|")
        lines.append(
            f"| {_fmt_money(att.get('actual', 0))} | {_fmt_money(att.get('quota', 0))} "
            f"| {_fmt_pct(att.get('attainment_pct'))} | {_fmt_money(att.get('gap') or 0)} |"
        )
        pct = att.get("attainment_pct")
        if pct is not None:
            verdict = "ahead of pace" if pct >= 100 else ("on track" if pct >= 75 else "behind pace")
            lines.append("")
            lines.append(f"> **Status: {verdict}.**")
    else:
        lines.append("\n_No quota/revenue data for this rep._")
    lines.append("")

    # Trends
    lines.append("## Metric trends")
    if rep_trends:
        lines.append("")
        lines.append("| Metric | Latest | MoM | Trend | Next (forecast) | Flag |")
        lines.append("|---|---|---|---|---|---|")
        for t in sorted(rep_trends, key=lambda x: x.metric):
            flag = "⚠︎ anomaly" if t.anomaly else ""
            lines.append(
                f"| {t.metric} | {t.latest:,.0f} | {_fmt_pct(t.pop_change_pct)} "
                f"| {_ARROW.get(t.direction,'')} {t.direction} | {t.forecast_next:,.0f} | {flag} |"
            )
    else:
        lines.append("\n_No metric time series for this rep._")
    lines.append("")

    # Narrative call-outs
    callouts = _callouts(rep_trends)
    if callouts:
        lines.append("## What to focus on")
        lines.append("")
        for c in callouts:
            lines.append(f"- {c}")
        lines.append("")

    # Top targets
    lines.append("## Top targets to work next")
    if rep_targets:
        top = sorted(rep_targets, key=lambda x: x.score, reverse=True)[:10]
        lines.append("")
        lines.append("| # | Target | Tier | Score | Est. value | Status | Facility |")
        lines.append("|---|---|---|---|---|---|---|")
        for i, t in enumerate(top, 1):
            lines.append(
                f"| {i} | {t.name} | {t.tier} | {t.score} | {_fmt_money(t.est_annual_value)} "
                f"| {t.status} | {t.facility} |"
            )
    else:
        lines.append("\n_No targets assigned to this rep yet._")
    lines.append("")

    fname = _safe(rep.name) + ".md"
    (out / fname).write_text("\n".join(lines))
    return str(out / fname)


def _callouts(trends: list[TrendResult]) -> list[str]:
    """Surface what a manager should raise in the 1:1.

    Keyed off the most recent month-over-month move (what people actually react
    to), plus statistical anomalies — independent of the longer-run slope, so a
    sharp recent drop still gets flagged even if the 6-month trend is up.
    """
    out = []
    for t in trends:
        mom = t.pop_change_pct
        if t.anomaly:
            out.append(
                f"**{t.metric}** shows an anomaly ({t.latest:,.0f} vs mean {t.mean:,.0f}) — "
                "confirm whether it's a data issue or a real spike/drop worth a conversation."
            )
        elif mom is not None and mom <= -10:
            trend_note = " (still up over the full period, but watch the pullback)" if t.direction == "up" else ""
            out.append(
                f"**{t.metric}** dropped {_fmt_pct(mom)} month-over-month{trend_note} — dig into root cause."
            )
        elif mom is not None and mom >= 15:
            out.append(
                f"**{t.metric}** is accelerating ({_fmt_pct(mom)} MoM) — reinforce what's working."
            )
    return out


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower() or "rep"
