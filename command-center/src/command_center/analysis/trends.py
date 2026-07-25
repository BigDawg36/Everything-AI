"""Trend detection over rep metric time series.

Pure-Python (statistics module only) so it runs anywhere. For each
(rep, metric) series we compute direction, slope, period-over-period change,
a simple linear forecast for the next period, and flag anomalies.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, asdict
from typing import Optional

from ..models import Metric


@dataclass
class TrendResult:
    rep: str
    metric: str
    n: int
    first: float
    latest: float
    mean: float
    pop_change_pct: Optional[float]   # latest vs previous period, %
    total_change_pct: Optional[float] # latest vs first, %
    slope: float                      # per-period linear slope
    direction: str                    # up | down | flat
    forecast_next: float              # naive linear projection
    anomaly: bool                     # latest point > 2 stdev from mean
    series: list                      # [(period, value), ...] for charts

    def as_dict(self) -> dict:
        return asdict(self)


def _linreg(ys: list[float]) -> tuple[float, float]:
    """Least-squares slope/intercept against x = 0..n-1."""
    n = len(ys)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0, my
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    intercept = my - slope * mx
    return slope, intercept


def _pct(old: float, new: float) -> Optional[float]:
    if old == 0:
        return None
    return round((new - old) / abs(old) * 100, 1)


def analyze_series(rep: str, metric: str, points: list[tuple[str, float]]) -> TrendResult:
    points = sorted(points, key=lambda p: p[0])
    ys = [v for _, v in points]
    n = len(ys)
    slope, intercept = _linreg(ys)
    mean = statistics.fmean(ys) if ys else 0.0
    stdev = statistics.pstdev(ys) if n > 1 else 0.0
    latest = ys[-1] if ys else 0.0
    prev = ys[-2] if n > 1 else None

    if slope > 1e-9 and abs(slope) > 0.01 * (abs(mean) + 1e-9):
        direction = "up"
    elif slope < -1e-9 and abs(slope) > 0.01 * (abs(mean) + 1e-9):
        direction = "down"
    else:
        direction = "flat"

    anomaly = bool(n > 2 and stdev > 0 and abs(latest - mean) > 2 * stdev)

    return TrendResult(
        rep=rep,
        metric=metric,
        n=n,
        first=ys[0] if ys else 0.0,
        latest=latest,
        mean=round(mean, 2),
        pop_change_pct=_pct(prev, latest) if prev is not None else None,
        total_change_pct=_pct(ys[0], latest) if ys else None,
        slope=round(slope, 3),
        direction=direction,
        forecast_next=round(slope * n + intercept, 2),
        anomaly=anomaly,
        series=points,
    )


def analyze(metrics: list[Metric]) -> list[TrendResult]:
    """Group metrics by (rep, metric) and analyze each series."""
    buckets: dict[tuple[str, str], list[tuple[str, float]]] = {}
    for m in metrics:
        buckets.setdefault((m.rep, m.metric), []).append((m.period, m.value))
    results = [analyze_series(rep, metric, pts) for (rep, metric), pts in buckets.items()]
    results.sort(key=lambda r: (r.rep, r.metric))
    return results


def quota_attainment(metrics: list[Metric], reps, revenue_metric: str = "revenue") -> dict[str, dict]:
    """For each rep, sum revenue YTD and compare to quota."""
    rev_by_rep: dict[str, float] = {}
    for m in metrics:
        if m.metric == revenue_metric:
            rev_by_rep[m.rep] = rev_by_rep.get(m.rep, 0.0) + m.value
    out = {}
    for rep in reps:
        actual = rev_by_rep.get(rep.name, 0.0)
        pct = round(actual / rep.quota * 100, 1) if rep.quota else None
        out[rep.name] = {
            "actual": round(actual, 2),
            "quota": rep.quota,
            "attainment_pct": pct,
            "gap": round(rep.quota - actual, 2) if rep.quota else None,
            "territory": rep.territory,
        }
    return out
