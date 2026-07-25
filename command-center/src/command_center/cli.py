"""Command-center CLI.

Subcommands:

  targets   Score an AcuityMD target export and write targets_scored.csv
  trends    Analyze rep metric time series -> trends.json (+ console summary)
  reps      Generate per-rep report packs (Markdown)
  powerbi   Generate Power BI model.json + measures.dax + report-layout.md
  site      Build the static command-center dashboard (index.html)
  build     Run the whole pipeline (targets -> trends -> reps -> powerbi -> site)
  pull      Browser-pull data from AcuityMD / Power BI (needs Playwright)

Everything except ``pull`` runs with only stdlib + PyYAML + Jinja2.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .analysis.scoring import resolve_weights, score_targets, tier_summary
from .analysis.trends import analyze, quota_attainment
from .enrich.npi import enrich_targets, load_sidecar
from .ingest import load_metrics, load_reps, load_settings, load_targets
from .reports.powerbi_spec import build_powerbi_spec
from .reports.rep_report import build_rep_report
from .site.build import build_site


def _fmt_money(v: float) -> str:
    return f"${v:,.0f}"


def _load_all(args):
    settings = load_settings(args.settings) if args.settings else {}
    reps = load_reps(args.reps) if args.reps else []
    targets = load_targets(args.targets) if args.targets else []
    metrics = load_metrics(args.metrics) if args.metrics else []
    if targets:
        score_targets(targets, resolve_weights(settings, getattr(args, "profile", None)))
    return settings, reps, targets, metrics


def cmd_targets(args):
    _, _, targets, _ = _load_all(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "targets_scored.csv"
    _write_targets_csv(targets, dest)
    summ = tier_summary(targets)
    print(f"Scored {len(targets)} targets -> {dest}")
    print("  Tiers:", ", ".join(f"{k}={v}" for k, v in summ.items()))
    if targets:
        print("  Top 3:")
        for t in targets[:3]:
            print(f"    {t.tier}  {t.score:>5}  {t.name}  ({_fmt_money(t.est_annual_value)})")


def cmd_enrich(args):
    """Validate + enrich targets against the NPPES NPI registry."""
    settings, _, targets, _ = _load_all(args)
    if not targets:
        raise SystemExit("Provide --targets <csv> to enrich.")
    sidecar = load_sidecar(args.npi_data) if args.npi_data else {}
    records, summary = enrich_targets(targets, sidecar=sidecar, online=not args.offline)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    _write_targets_csv(targets, out / "targets_enriched.csv")
    (out / "npi_validation.json").write_text(
        json.dumps({"summary": summary, "records": [r.as_dict() for r in records]},
                   indent=2, default=str)
    )

    total = len(targets)
    print(f"Enriched {total} targets -> {out / 'targets_enriched.csv'}")
    print(f"  verified={summary['verified']}  not_found={summary['not_found']}  "
          f"invalid={summary['invalid']}  unchecked={summary['unchecked']}  "
          f"missing_npi={summary['missing_npi']}")
    bad = [r for r in records if r.status == "invalid"]
    if bad:
        print("  ⚠ Invalid NPIs (fix at the source):")
        for r in bad:
            match = next((t.name for t in targets if t.npi == r.npi), r.npi)
            print(f"      {r.npi}  {match}")
    if summary["unchecked"]:
        print("  note: NPPES was unreachable for some records — format validated only.")
    print(f"  detail -> {out / 'npi_validation.json'}")


def cmd_trends(args):
    _, reps, _, metrics = _load_all(args)
    trends = analyze(metrics)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "trends.json"
    dest.write_text(json.dumps([t.as_dict() for t in trends], indent=2, default=str))
    print(f"Analyzed {len(trends)} (rep, metric) series -> {dest}")
    for t in trends:
        flag = "  ⚠ anomaly" if t.anomaly else ""
        pop = "n/a" if t.pop_change_pct is None else f"{t.pop_change_pct:+.1f}%"
        print(f"  {t.rep:<16} {t.metric:<14} {t.direction:<5} latest={t.latest:>10,.0f}  MoM={pop}{flag}")


def cmd_reps(args):
    settings, reps, targets, metrics = _load_all(args)
    trends = analyze(metrics)
    rev_metric = (settings.get("metrics") or {}).get("revenue_key", "revenue")
    att = quota_attainment(metrics, reps, rev_metric)
    out = Path(args.out) / "rep_reports"
    written = [build_rep_report(rep, trends, targets, att, out) for rep in reps]
    print(f"Wrote {len(written)} rep reports -> {out}/")
    for w in written:
        print(f"  {w}")


def cmd_powerbi(args):
    out = Path(args.out) / "powerbi"
    res = build_powerbi_spec(out)
    print(f"Power BI spec -> {out}/")
    print(f"  model.json, measures.dax ({res['measure_count']} measures), report-layout.md")


def cmd_site(args):
    settings, reps, targets, metrics = _load_all(args)
    trends = analyze(metrics)
    rev_metric = (settings.get("metrics") or {}).get("revenue_key", "revenue")
    att = quota_attainment(metrics, reps, rev_metric)
    kpis = _headline_kpis(targets, metrics, att, rev_metric)
    out = Path(args.out) / "site"
    embed = (settings.get("site") or {}).get("powerbi_embed_url", args.powerbi_embed_url or "")
    title = (settings.get("site") or {}).get("title", "Sales Command Center")
    index = build_site(
        kpis, att, trends, targets, out,
        title=title, powerbi_embed_url=embed, generated_at=args.generated_at or "",
    )
    print(f"Command-center site -> {index}")


def cmd_build(args):
    """Run the full pipeline."""
    cmd_targets(args)
    print()
    cmd_trends(args)
    print()
    cmd_reps(args)
    print()
    cmd_powerbi(args)
    print()
    cmd_site(args)
    print(f"\n✓ Full build complete under {args.out}/")


def cmd_pull(args):
    """Browser-pull from AcuityMD or Power BI (optional Playwright layer)."""
    out = Path(args.out) / "raw"
    out.mkdir(parents=True, exist_ok=True)
    settings = load_settings(args.settings) if args.settings else {}
    if args.source == "acuitymd":
        from .browser.acuitymd import pull_targets_export
        dest = pull_targets_export(
            args.url, out / "acuitymd_targets.csv",
            headless=args.headless, config=(settings.get("acuitymd") or {}),
        )
        print(f"Pulled AcuityMD targets -> {dest}")
    elif args.source == "powerbi":
        from .browser.powerbi import export_visual_data
        cfg = settings.get("powerbi") or {}
        selector = args.visual_selector or cfg.get("visual_more_options_selector")
        if not selector:
            raise SystemExit("Provide --visual-selector or set powerbi.visual_more_options_selector in settings.")
        dest = export_visual_data(
            args.url, out / "powerbi_metrics.csv",
            visual_more_options_selector=selector,
            headless=args.headless, config=cfg,
        )
        print(f"Exported Power BI visual data -> {dest}")


def _headline_kpis(targets, metrics, att, rev_metric):
    revenue_ytd = sum(v["actual"] for v in att.values())
    quota = sum(v["quota"] or 0 for v in att.values())
    attainment = f"{revenue_ytd / quota * 100:.0f}%" if quota else "—"
    pipeline = sum(t.est_annual_value for t in targets if t.status == "prospect")
    a_tier = sum(1 for t in targets if t.tier == "A")
    return {
        "Revenue YTD": _fmt_money(revenue_ytd),
        "Quota attainment": attainment,
        "Open pipeline": _fmt_money(pipeline),
        "A-tier targets": str(a_tier),
    }


def _write_targets_csv(targets, dest):
    import csv
    dest.parent.mkdir(parents=True, exist_ok=True)
    fields = list(targets[0].as_dict().keys()) if targets else []
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for t in targets:
            writer.writerow(t.as_dict())


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="command-center", description="AcuityMD + Power BI sales command center")
    p.add_argument("--version", action="version", version=f"command-center {__version__}")
    p.add_argument("--targets", help="AcuityMD target export CSV")
    p.add_argument("--metrics", help="Power BI metrics CSV (tidy or wide)")
    p.add_argument("--reps", help="Rep roster YAML")
    p.add_argument("--settings", help="Settings YAML")
    p.add_argument("--out", default="data/out", help="Output directory (default: data/out)")
    p.add_argument("--profile", help="Scoring profile: balanced | implant | capital | disposable | service_line")
    p.add_argument("--powerbi-embed-url", default="", help="Power BI publish-to-web iframe URL for the site")
    p.add_argument("--generated-at", default="", help="Timestamp label for the site footer")

    sub = p.add_subparsers(dest="command", required=True)

    enrich = sub.add_parser("enrich", help="Validate/enrich targets via the NPI registry")
    enrich.add_argument("--npi-data", help="JSON sidecar of pre-fetched NPPES records")
    enrich.add_argument("--offline", action="store_true", help="Skip network; validate NPI format only")
    enrich.set_defaults(func=cmd_enrich)

    for name, fn, help_ in [
        ("targets", cmd_targets, "Score AcuityMD targets"),
        ("trends", cmd_trends, "Analyze metric trends"),
        ("reps", cmd_reps, "Generate per-rep reports"),
        ("powerbi", cmd_powerbi, "Generate Power BI spec"),
        ("site", cmd_site, "Build the command-center site"),
        ("build", cmd_build, "Run the whole pipeline"),
    ]:
        sp = sub.add_parser(name, help=help_)
        sp.set_defaults(func=fn)

    pull = sub.add_parser("pull", help="Browser-pull data (needs Playwright)")
    pull.add_argument("source", choices=["acuitymd", "powerbi"])
    pull.add_argument("--url", required=True, help="Saved view / report URL")
    pull.add_argument("--visual-selector", help="Power BI visual 'More options' selector")
    pull.add_argument("--headless", action="store_true", help="Run headless (only after first interactive login)")
    pull.set_defaults(func=cmd_pull)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
