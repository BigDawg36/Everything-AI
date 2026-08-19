"""Load raw pulls (CSV) into the tidy models.

Everything upstream — a Power BI export, an AcuityMD target list, a hand-built
spreadsheet, or a table the browser layer scraped — lands here as a CSV and is
normalized into ``Target`` / ``Metric`` / ``Rep`` objects.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import yaml

from .models import Metric, Rep, Target


def _read_csv(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def load_targets(path: str | Path) -> list[Target]:
    return [Target.from_row(r) for r in _read_csv(path)]


def load_metrics(path: str | Path) -> list[Metric]:
    rows = _read_csv(path)
    metrics: list[Metric] = []
    if not rows:
        return metrics
    header = {k.strip().lower() for k in rows[0].keys()}
    # Two supported shapes:
    #   1. Tidy: columns period, rep, metric, value  (one row per measurement)
    #   2. Wide: columns period, rep, revenue, cases, ...  (metrics as columns)
    if "metric" in header and "value" in header:
        return [Metric.from_row(r) for r in rows]
    # Wide -> tidy melt.
    id_cols = {"period", "date", "month", "rep", "owner", "sales_rep", "territory", "region"}
    for r in rows:
        lower = {k.strip().lower(): v for k, v in r.items()}
        period = lower.get("period") or lower.get("date") or lower.get("month") or ""
        rep = lower.get("rep") or lower.get("owner") or lower.get("sales_rep") or ""
        territory = lower.get("territory") or lower.get("region") or ""
        for k, v in lower.items():
            if k in id_cols or v in (None, ""):
                continue
            try:
                value = float(str(v).replace("$", "").replace(",", "").replace("%", ""))
            except ValueError:
                continue
            metrics.append(Metric(period=period, rep=rep, metric=k, value=value, territory=territory))
    return metrics


def load_reps(path: str | Path) -> list[Rep]:
    """Load the rep roster from a YAML config file.

    Expected shape::

        reps:
          - name: Jordan Lee
            territory: OC-North
            email: jordan@example.com
            quota: 1800000
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Rep config not found: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    return [Rep.from_row(r) for r in data.get("reps", [])]


def load_settings(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def group_by(items: Iterable, key: str) -> dict[str, list]:
    out: dict[str, list] = {}
    for it in items:
        out.setdefault(getattr(it, key, "") or "(unassigned)", []).append(it)
    return out
