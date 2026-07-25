#!/usr/bin/env python3
"""Trend analysis over a pulled time series (from Power BI executeQueries).

Input: a CSV or JSON array of rows with at least a period column and a value
column, plus an optional grouping dimension (product, rep, account). Output: a
JSON summary of growth, rolling average, seasonality, concentration, and
anomaly flags — the raw material for TRENDS-{date}.md.

Pure standard library (no pandas needed).

Examples
--------
  # from Power BI JSON rows
  python powerbi_client.py query --file trend.dax > series.json
  python analyze_trends.py series.json --period YearMonth --value Revenue --group Category

  # from a CSV
  python analyze_trends.py series.csv --period month --value revenue
"""
import argparse
import json
import math
import statistics
import sys
from collections import defaultdict


def load_rows(path):
    if path.endswith(".json") or path == "-":
        raw = sys.stdin.read() if path == "-" else open(path).read()
        data = json.loads(raw)
        # Power BI rows use "Table[Column]" keys; strip to bare column names.
        return [{_bare(k): v for k, v in row.items()} for row in data]
    import csv
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _bare(key):
    # "Date[YearMonth]" -> "YearMonth"; "[Revenue]" -> "Revenue"
    if "[" in key and key.endswith("]"):
        return key[key.index("[") + 1:-1]
    return key


def _num(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def series_stats(pairs):
    """pairs: list of (period, value) sorted by period. Returns a stats dict."""
    periods = [p for p, _ in pairs]
    values = [v for _, v in pairs if v is not None]
    if len(values) < 2:
        return {"points": len(values), "note": "insufficient data for trends"}

    first, last = values[0], values[-1]
    total_growth = _pct(last, first)

    # period-over-period growth series
    pop = []
    for i in range(1, len(values)):
        pop.append(_pct(values[i], values[i - 1]))
    pop_clean = [x for x in pop if x is not None]

    # 3-month rolling average (trailing)
    roll = []
    window = 3
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        roll.append(round(statistics.mean(values[lo:i + 1]), 2))

    # YoY if we have >= 13 points
    yoy = _pct(values[-1], values[-13]) if len(values) >= 13 else None

    # seasonality: each period's value vs. mean (index=1.0 is average)
    mean_val = statistics.mean(values)
    seasonality = [round(v / mean_val, 3) if mean_val else None for v in values]

    # anomaly flags: points outside mean +/- 2*stdev of pop growth
    anomalies = []
    if len(pop_clean) >= 3:
        mu, sigma = statistics.mean(pop_clean), statistics.pstdev(pop_clean)
        for i, g in enumerate(pop):
            if g is not None and sigma > 0 and abs(g - mu) > 2 * sigma:
                anomalies.append({"period": periods[i + 1], "pop_growth_pct": g})

    return {
        "points": len(values),
        "first_period": periods[0],
        "last_period": periods[-1],
        "first_value": round(first, 2),
        "last_value": round(last, 2),
        "total_growth_pct": total_growth,
        "yoy_growth_pct": yoy,
        "avg_pop_growth_pct": round(statistics.mean(pop_clean), 2) if pop_clean else None,
        "rolling_3": roll,
        "seasonality_index": seasonality,
        "anomalies": anomalies,
        "direction": _direction(roll),
    }


def _pct(a, b):
    if a is None or b in (None, 0):
        return None
    return round((a - b) / abs(b) * 100, 2)


def _direction(roll):
    if len(roll) < 2:
        return "flat"
    delta = roll[-1] - roll[0]
    band = 0.02 * (abs(roll[0]) or 1)
    if delta > band:
        return "up"
    if delta < -band:
        return "down"
    return "flat"


def concentration(group_totals):
    """Top-N account/group share of total (a risk indicator)."""
    total = sum(v for v in group_totals.values() if v)
    if not total:
        return {}
    ranked = sorted(group_totals.items(), key=lambda kv: kv[1] or 0, reverse=True)
    def top_share(n):
        return round(sum(v for _, v in ranked[:n]) / total * 100, 1)
    return {
        "total": round(total, 2),
        "top1_pct": top_share(1),
        "top5_pct": top_share(5),
        "top10_pct": top_share(10),
        "n_groups": len(ranked),
        "leaders": [{"group": g, "value": round(v, 2)} for g, v in ranked[:10]],
    }


def main():
    p = argparse.ArgumentParser(description="Trend analysis")
    p.add_argument("input", help="CSV or JSON file, or '-' for stdin JSON")
    p.add_argument("--period", required=True, help="period/date column name")
    p.add_argument("--value", required=True, help="numeric value column name")
    p.add_argument("--group", help="optional grouping column (product, rep, ...)")
    p.add_argument("--out", help="write JSON summary to this path")
    args = p.parse_args()

    rows = load_rows(args.input)
    if not rows:
        sys.exit("No rows loaded.")

    result = {"value": args.value, "period": args.period}

    if args.group:
        # per-group time series + concentration of the latest-period totals
        by_group = defaultdict(list)
        latest_totals = defaultdict(float)
        latest_period = max(_get(r, args.period) for r in rows)
        for r in rows:
            g = _get(r, args.group)
            per = _get(r, args.period)
            val = _num(_get(r, args.value))
            by_group[g].append((per, val))
            if per == latest_period and val:
                latest_totals[g] += val
        result["groups"] = {}
        for g, pairs in by_group.items():
            pairs.sort(key=lambda x: str(x[0]))
            result["groups"][g] = series_stats(pairs)
        result["concentration_latest_period"] = concentration(latest_totals)
        result["latest_period"] = latest_period
    else:
        # single aggregate series (sum values per period)
        agg = defaultdict(float)
        seen = defaultdict(bool)
        for r in rows:
            per = _get(r, args.period)
            val = _num(_get(r, args.value))
            if val is not None:
                agg[per] += val
                seen[per] = True
        pairs = sorted(((k, v) for k, v in agg.items()), key=lambda x: str(x[0]))
        result["series"] = series_stats(pairs)

    text = json.dumps(result, indent=2, default=str)
    if args.out:
        open(args.out, "w").write(text)
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(text)


def _get(row, col):
    # tolerate bare or bracketed Power BI column names
    if col in row:
        return row[col]
    for k in row:
        if _bare(k) == col:
            return row[k]
    return None


if __name__ == "__main__":
    main()
