"""Core data models for the command center.

Kept to stdlib dataclasses so the analysis/report/site layers have zero
third-party dependencies. Every model has a ``from_row`` classmethod that
tolerates the messy, inconsistent column names you get out of a CSV export or a
scraped table.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any, Optional


def _num(value: Any, default: float = 0.0) -> float:
    """Best-effort parse of a number from a spreadsheet cell.

    Strips ``$``, ``,``, ``%`` and whitespace; returns ``default`` on failure.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if s in ("", "-", "n/a", "N/A", "NA", "null", "None"):
        return default
    try:
        return float(s)
    except ValueError:
        return default


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _pick(row: dict, *names: str, default: str = "") -> Any:
    """Return the first present, non-empty value among ``names`` (case/space
    insensitive on the row keys)."""
    lowered = {k.strip().lower(): v for k, v in row.items()}
    for name in names:
        key = name.strip().lower()
        if key in lowered and _clean(lowered[key]) != "":
            return lowered[key]
    return default


@dataclass
class Target:
    """A prospective account/physician surfaced from AcuityMD.

    ``score`` and ``tier`` are filled in later by the scoring module.
    """
    name: str
    npi: str = ""
    specialty: str = ""
    facility: str = ""
    city: str = ""
    state: str = ""
    territory: str = ""
    rep: str = ""
    # Signals used for scoring. Names chosen to be generic across procedures.
    procedure_volume: float = 0.0          # annual volume of the target procedure
    est_annual_value: float = 0.0          # $ opportunity if converted
    competitor_share: float = 0.0          # 0-1, share currently held by competitors
    growth_rate: float = 0.0               # yoy % growth in relevant volume
    status: str = "prospect"               # prospect | engaged | customer | dormant
    last_touch: str = ""                   # ISO date of last rep interaction
    source: str = "acuitymd"
    score: float = 0.0
    tier: str = ""
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict) -> "Target":
        return cls(
            name=_clean(_pick(row, "name", "physician", "account", "target", "hcp")),
            npi=_clean(_pick(row, "npi", "npi_number")),
            specialty=_clean(_pick(row, "specialty", "taxonomy")),
            facility=_clean(_pick(row, "facility", "hospital", "site", "practice")),
            city=_clean(_pick(row, "city")),
            state=_clean(_pick(row, "state", "st")),
            territory=_clean(_pick(row, "territory", "region")),
            rep=_clean(_pick(row, "rep", "owner", "sales_rep", "assigned_rep")),
            procedure_volume=_num(_pick(row, "procedure_volume", "volume", "cases", "annual_volume")),
            est_annual_value=_num(_pick(row, "est_annual_value", "opportunity", "value", "potential")),
            competitor_share=_num(_pick(row, "competitor_share", "comp_share")),
            growth_rate=_num(_pick(row, "growth_rate", "growth", "yoy_growth")),
            status=_clean(_pick(row, "status", "stage", default="prospect")) or "prospect",
            last_touch=_clean(_pick(row, "last_touch", "last_contact", "last_activity")),
            source=_clean(_pick(row, "source", default="acuitymd")) or "acuitymd",
            notes=_clean(_pick(row, "notes", "comment")),
        )

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Metric:
    """A single measured value for a rep on a given date.

    This is the tidy shape everything downstream expects: one row per
    (date, rep, metric). Power BI exports and manual pulls get normalized into
    a list of these.
    """
    period: str            # ISO date (month-end works well): 2026-06-30
    rep: str
    metric: str            # e.g. "revenue", "cases", "new_accounts", "quota"
    value: float
    territory: str = ""

    @classmethod
    def from_row(cls, row: dict) -> "Metric":
        return cls(
            period=_clean(_pick(row, "period", "date", "month")),
            rep=_clean(_pick(row, "rep", "owner", "sales_rep")),
            metric=_clean(_pick(row, "metric", "kpi", "measure")),
            value=_num(_pick(row, "value", "amount", "actual")),
            territory=_clean(_pick(row, "territory", "region")),
        )

    def period_date(self) -> Optional[date]:
        for fmt in ("%Y-%m-%d", "%Y-%m", "%m/%d/%Y", "%m/%Y"):
            try:
                return datetime.strptime(self.period, fmt).date()
            except ValueError:
                continue
        return None


@dataclass
class Rep:
    """A sales rep and their territory/quota configuration."""
    name: str
    territory: str = ""
    email: str = ""
    quota: float = 0.0            # annualized $ quota
    manager: str = ""
    metrics: list = field(default_factory=list)   # populated at report time

    @classmethod
    def from_row(cls, row: dict) -> "Rep":
        return cls(
            name=_clean(_pick(row, "name", "rep")),
            territory=_clean(_pick(row, "territory", "region")),
            email=_clean(_pick(row, "email")),
            quota=_num(_pick(row, "quota", "annual_quota", "target")),
            manager=_clean(_pick(row, "manager")),
        )
