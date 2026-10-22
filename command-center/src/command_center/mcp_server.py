"""AcuityMD MCP server.

Exposes an AcuityMD target export (plus optional Power BI metrics and the rep
roster) to Claude as read-only MCP tools: find and rank targets, look one up,
roll up a territory, surface whitespace, verify an NPI, and check rep trends.

AcuityMD has no public API on the plan tier this tool assumes, so the server
reads the CSV you export from AcuityMD (or pull with ``command-center pull
acuitymd``). Point it at a single file or a folder; with a folder it always
reads the newest ``*.csv``, so dropping a fresh export in is all a refresh takes.

It runs locally over stdio. Your AcuityMD data never leaves the machine except
as tool results sent to the Claude client you connect it to, and NPI lookups
(public NPPES registry) when ``verify_npi`` is called.

Configuration (environment variables):

  ACUITYMD_TARGETS      CSV file, or a folder of exports (newest wins). Required.
  COMMAND_CENTER_SETTINGS  settings.yaml (scoring profile/weights, column_map).
  COMMAND_CENTER_REPS   reps.yaml roster (quota attainment).
  POWERBI_METRICS       Power BI metrics CSV (rep trends).
  NPI_OFFLINE           "1" to skip live NPPES calls (format check only).

Run:  python -m command_center.mcp_server
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .analysis.scoring import PROFILES, resolve_weights, score_targets, tier_summary
from .analysis.trends import analyze, quota_attainment
from .enrich.npi import NpiRecord, lookup, luhn_valid
from .ingest import load_metrics, load_reps, load_settings
from .models import Target

# Column names Target.from_row understands. Anything else in the export is
# reported by dataset_info so the user knows to add a column_map entry.
KNOWN_COLUMNS = {
    "name", "physician", "account", "target", "hcp", "npi", "npi_number",
    "specialty", "taxonomy", "facility", "hospital", "site", "practice", "city",
    "state", "st", "territory", "region", "rep", "owner", "sales_rep",
    "assigned_rep", "procedure_volume", "volume", "cases", "annual_volume",
    "est_annual_value", "opportunity", "value", "potential", "competitor_share",
    "comp_share", "growth_rate", "growth", "yoy_growth", "status", "stage",
    "last_touch", "last_contact", "last_activity", "source", "notes", "comment",
}

READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


# --------------------------------------------------------------------------
# Data loading (cached; reloads automatically when the export changes)
# --------------------------------------------------------------------------

def _env_path(name: str) -> Optional[Path]:
    val = os.environ.get(name, "").strip()
    return Path(val).expanduser() if val else None


def _resolve_export(path: Path) -> Path:
    """A file is used as-is; a folder resolves to its newest CSV."""
    if path.is_dir():
        csvs = sorted(path.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not csvs:
            raise FileNotFoundError(f"No .csv files in {path}")
        return csvs[0]
    if not path.exists():
        raise FileNotFoundError(f"AcuityMD export not found: {path}")
    return path


def _read_rows(path: Path, column_map: dict) -> tuple[list[dict], list[str]]:
    """Read the export, renaming columns per settings ``acuitymd.column_map``."""
    rename = {str(k).strip().lower(): str(v).strip() for k, v in (column_map or {}).items()}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header = list(reader.fieldnames or [])
        rows = []
        for raw in reader:
            row = {}
            for k, v in raw.items():
                if k is None:
                    continue
                row[rename.get(k.strip().lower(), k)] = v
            rows.append(row)
    return rows, header


@dataclass
class _State:
    export: Optional[Path] = None
    mtime: float = 0.0
    header: list = field(default_factory=list)
    targets: list = field(default_factory=list)
    settings: dict = field(default_factory=dict)
    loaded_at: str = ""


_state = _State()


def _settings() -> dict:
    p = _env_path("COMMAND_CENTER_SETTINGS")
    return load_settings(p) if p else {}


def _load(force: bool = False) -> _State:
    src = _env_path("ACUITYMD_TARGETS")
    if src is None:
        raise RuntimeError(
            "ACUITYMD_TARGETS is not set. Point it at an AcuityMD CSV export or a "
            "folder of exports in your MCP client config."
        )
    export = _resolve_export(src)
    mtime = export.stat().st_mtime
    if not force and export == _state.export and mtime == _state.mtime:
        return _state

    settings = _settings()
    column_map = (settings.get("acuitymd") or {}).get("column_map") or {}
    rows, header = _read_rows(export, column_map)
    targets = [Target.from_row(r) for r in rows]
    targets = [t for t in targets if t.name or t.npi]
    score_targets(targets, resolve_weights(settings))

    _state.export, _state.mtime, _state.header = export, mtime, header
    _state.targets, _state.settings = targets, settings
    _state.loaded_at = datetime.now().isoformat(timespec="seconds")
    return _state


def _scored(profile: Optional[str]) -> list[Target]:
    """Targets scored with the configured weights, or rescored with ``profile``.

    Scores are relative to the whole export (min-max normalized), so filters
    are applied after scoring, never before.
    """
    st = _load()
    if not profile:
        return st.targets
    fresh = [Target(**{**t.as_dict(), "score": 0.0, "tier": ""}) for t in st.targets]
    return score_targets(fresh, resolve_weights(st.settings, profile))


def _days_since(iso: str) -> Optional[int]:
    if not iso:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return (date.today() - datetime.strptime(iso.strip(), fmt).date()).days
        except ValueError:
            continue
    return None


def _match(value: str, wanted: Optional[str]) -> bool:
    return not wanted or wanted.strip().lower() in (value or "").lower()


def _row(t: Target, brief: bool = True) -> dict:
    d = t.as_dict()
    d["days_since_touch"] = _days_since(t.last_touch)
    if brief:
        keep = ("tier", "score", "name", "npi", "specialty", "facility", "city",
                "territory", "rep", "status", "procedure_volume",
                "est_annual_value", "competitor_share", "growth_rate",
                "last_touch", "days_since_touch")
        d = {k: d[k] for k in keep}
    return d


# --------------------------------------------------------------------------
# MCP server + tools
# --------------------------------------------------------------------------

mcp = FastMCP(
    "acuitymd",
    instructions=(
        "Read-only access to the user's AcuityMD target export (medical-device "
        "physician and facility targets), scored 0-100 with A-D tiers. Start "
        "with dataset_info if results look empty or columns look wrong. Scores "
        "are relative to the current export, not absolute. Numbers come from "
        "the export as-is: cite them, do not extrapolate, and tell the user to "
        "confirm anything customer-facing in AcuityMD itself."
    ),
)


@mcp.tool(annotations=READ_ONLY)
def dataset_info() -> dict:
    """Describe the loaded AcuityMD export: file, freshness, row count, tier
    mix, and which columns were recognized vs ignored. Call this first when
    results look wrong; ignored columns need a column_map entry in settings."""
    st = _load()
    mapped = {str(k).strip().lower() for k in
              ((st.settings.get("acuitymd") or {}).get("column_map") or {})}
    ignored = [h for h in st.header
               if h.strip().lower() not in KNOWN_COLUMNS and h.strip().lower() not in mapped]
    return {
        "export_file": str(st.export),
        "export_modified": datetime.fromtimestamp(st.mtime).isoformat(timespec="seconds"),
        "loaded_at": st.loaded_at,
        "targets": len(st.targets),
        "tiers": tier_summary(st.targets),
        "scoring_profile": (st.settings.get("scoring") or {}).get("profile") or "balanced",
        "available_profiles": sorted(PROFILES),
        "columns_in_export": st.header,
        "columns_ignored": ignored,
        "reps": sorted({t.rep for t in st.targets if t.rep}),
        "territories": sorted({t.territory for t in st.targets if t.territory}),
    }


@mcp.tool(annotations=READ_ONLY)
def find_targets(
    rep: Optional[str] = None,
    territory: Optional[str] = None,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    facility: Optional[str] = None,
    status: Optional[str] = None,
    tier: Optional[str] = None,
    min_score: float = 0.0,
    profile: Optional[str] = None,
    sort_by: str = "score",
    limit: int = 25,
) -> dict:
    """Rank AcuityMD targets. All text filters are case-insensitive substring
    matches. tier is one or more letters, e.g. "A" or "AB". profile rescores
    with a named weighting (balanced, implant, capital, disposable,
    service_line). sort_by: score | est_annual_value | procedure_volume |
    competitor_share | growth_rate."""
    if sort_by not in ("score", "est_annual_value", "procedure_volume",
                       "competitor_share", "growth_rate"):
        raise ValueError(f"Unsupported sort_by {sort_by!r}")
    tiers = set((tier or "").upper().replace(",", "").replace(" ", ""))
    hits = [
        t for t in _scored(profile)
        if _match(t.rep, rep) and _match(t.territory, territory)
        and _match(t.specialty, specialty) and _match(t.city, city)
        and _match(t.facility, facility) and _match(t.status, status)
        and (not tiers or t.tier in tiers) and t.score >= min_score
    ]
    hits.sort(key=lambda t: getattr(t, sort_by), reverse=True)
    limit = max(1, min(limit, 200))
    return {
        "matched": len(hits),
        "returned": min(len(hits), limit),
        "total_opportunity": round(sum(t.est_annual_value for t in hits), 2),
        "targets": [_row(t) for t in hits[:limit]],
    }


@mcp.tool(annotations=READ_ONLY)
def get_target(query: str) -> dict:
    """Full record for one target, by exact NPI or a name/facility substring.
    Returns every match (up to 10) when the query is ambiguous."""
    q = query.strip().lower()
    targets = _load().targets
    hits = [t for t in targets if t.npi == query.strip()] or [
        t for t in targets if q in t.name.lower() or q in t.facility.lower()
    ]
    rank = {id(t): i + 1 for i, t in enumerate(targets)}
    return {
        "matched": len(hits),
        "targets": [{**_row(t, brief=False), "rank_in_export": rank[id(t)]} for t in hits[:10]],
    }


@mcp.tool(annotations=READ_ONLY)
def territory_summary(group_by: str = "rep", rep: Optional[str] = None,
                      territory: Optional[str] = None) -> dict:
    """Roll up targets by rep, territory, specialty, facility, city, or status:
    count, A-D tier mix, total opportunity, total procedure volume, and the
    top target in each group."""
    if group_by not in ("rep", "territory", "specialty", "facility", "city", "status"):
        raise ValueError(f"Unsupported group_by {group_by!r}")
    groups: dict[str, list[Target]] = {}
    for t in _load().targets:
        if _match(t.rep, rep) and _match(t.territory, territory):
            groups.setdefault(getattr(t, group_by) or "(unassigned)", []).append(t)
    out = []
    for key, items in groups.items():
        top = max(items, key=lambda t: t.score)
        out.append({
            group_by: key,
            "targets": len(items),
            "tiers": tier_summary(items),
            "total_opportunity": round(sum(t.est_annual_value for t in items), 2),
            "total_procedure_volume": round(sum(t.procedure_volume for t in items), 1),
            "top_target": {"name": top.name, "tier": top.tier, "score": top.score},
        })
    out.sort(key=lambda g: g["total_opportunity"], reverse=True)
    return {"group_by": group_by, "groups": out}


@mcp.tool(annotations=READ_ONLY)
def whitespace(rep: Optional[str] = None, territory: Optional[str] = None,
               min_competitor_share: float = 0.5, stale_days: int = 60,
               limit: int = 25) -> dict:
    """Find untapped and neglected opportunity:
    - conquest: prospects where competitors hold at least min_competitor_share
      of the volume and nobody has touched them (or not in stale_days);
    - at_risk: engaged accounts and customers with no touch in stale_days.
    Each list is sorted by score."""
    pool = [t for t in _load().targets
            if _match(t.rep, rep) and _match(t.territory, territory)]

    def stale(t: Target) -> bool:
        d = _days_since(t.last_touch)
        return d is None or d > stale_days

    conquest = [t for t in pool if t.status == "prospect"
                and t.competitor_share >= min_competitor_share and stale(t)]
    at_risk = [t for t in pool if t.status in ("engaged", "customer") and stale(t)]
    limit = max(1, min(limit, 100))
    return {
        "conquest": {
            "count": len(conquest),
            "total_opportunity": round(sum(t.est_annual_value for t in conquest), 2),
            "targets": [_row(t) for t in conquest[:limit]],
        },
        "at_risk": {
            "count": len(at_risk),
            "total_opportunity": round(sum(t.est_annual_value for t in at_risk), 2),
            "targets": [_row(t) for t in at_risk[:limit]],
        },
    }


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
def verify_npi(npi: str) -> dict:
    """Validate an NPI (check digit) and look it up in the public CMS NPPES
    registry: name, credential, primary specialty, practice address, phone.
    Also says whether the NPI appears in the AcuityMD export."""
    npi = npi.strip()
    if os.environ.get("NPI_OFFLINE", "").strip() in ("1", "true", "yes"):
        rec = NpiRecord(npi=npi, status="invalid" if not luhn_valid(npi) else "unchecked",
                        note="Offline mode: format check only.")
    else:
        rec = lookup(npi)
    in_export = [t.name for t in _load().targets if t.npi == npi]
    return {**rec.as_dict(), "in_acuitymd_export": bool(in_export), "export_names": in_export}


@mcp.tool(annotations=READ_ONLY)
def rep_performance(rep: Optional[str] = None) -> dict:
    """Sales trends per rep and metric from the Power BI metrics export
    (direction, period-over-period change, naive next-period forecast, anomaly
    flag), plus quota attainment when a rep roster is configured. Needs
    POWERBI_METRICS; COMMAND_CENTER_REPS is optional."""
    mpath = _env_path("POWERBI_METRICS")
    if mpath is None:
        return {"error": "POWERBI_METRICS is not set; rep trends need a Power BI metrics CSV."}
    metrics = [m for m in load_metrics(mpath) if _match(m.rep, rep)]
    out: dict = {"trends": [r.as_dict() for r in analyze(metrics)]}
    rpath = _env_path("COMMAND_CENTER_REPS")
    if rpath:
        reps = [r for r in load_reps(rpath) if _match(r.name, rep)]
        key = (_settings().get("metrics") or {}).get("revenue_key", "revenue")
        out["quota_attainment"] = quota_attainment(metrics, reps, revenue_metric=key)
    return out


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def reload_export() -> dict:
    """Force a re-read of the export and settings. Normally unnecessary: the
    server reloads on its own when the export file changes."""
    st = _load(force=True)
    return {"export_file": str(st.export), "targets": len(st.targets), "loaded_at": st.loaded_at}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
