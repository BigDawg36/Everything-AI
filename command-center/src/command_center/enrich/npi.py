"""NPI validation + NPPES registry enrichment.

Three-state result for every target, which is the honest shape of this problem:

  * ``invalid``    — fails format/Luhn check. A typo. Fix it at the source.
  * ``not_found``  — well-formed but not assigned in NPPES. Verify the record.
  * ``verified``   — found; we merge specialty, address, phone, credential.

Two ways to run it, because network access differs by environment:

  1. **Direct** (default) — calls the public NPPES API over HTTPS. Works on a
     normal laptop; no key, no auth. If the network blocks it (corporate proxy,
     sandbox), enrichment degrades to validation-only rather than crashing.
  2. **Sidecar** — pass ``--npi-data <file.json>`` with records already fetched
     (e.g. by Claude via the NPI Registry MCP tools). Keyed by NPI string.

NPPES gotcha encoded here: the registry spells the surgical taxonomy
**"Orthopaedic Surgery"**. Searching "Orthopedic Surgery" returns zero results;
"Orthopedic" only appears in physical-therapy/chiropractic taxonomies.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

NPPES_URL = "https://npiregistry.cms.hhs.gov/api/"
NPPES_VERSION = "2.1"

# NPPES taxonomy spellings that differ from how sales teams say them.
TAXONOMY_ALIASES = {
    "orthopedic surgery": "Orthopaedic Surgery",
    "orthopedics": "Orthopaedic Surgery",
    "ortho": "Orthopaedic Surgery",
    "spine surgery": "Orthopaedic Surgery, Orthopaedic Surgery of the Spine",
    "hand surgery": "Orthopaedic Surgery, Hand Surgery",
    "sports medicine": "Orthopaedic Surgery, Sports Medicine",
}


def normalize_taxonomy(term: str) -> str:
    """Map a colloquial specialty to the spelling NPPES actually indexes."""
    return TAXONOMY_ALIASES.get((term or "").strip().lower(), term)


def luhn_valid(npi: str) -> bool:
    """Validate an NPI's format and check digit.

    NPI uses Luhn over the number prefixed with the healthcare ID ``80840``.
    """
    npi = (npi or "").strip()
    if len(npi) != 10 or not npi.isdigit():
        return False
    payload = "80840" + npi[:9]
    total = 0
    # Double every second digit from the right of the full payload.
    for i, ch in enumerate(reversed(payload)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - (total % 10)) % 10
    return check == int(npi[9])


def luhn_check_digit(first9: str) -> int:
    """Compute the correct check digit for a 9-digit NPI stem (test helper)."""
    payload = "80840" + first9
    total = 0
    for i, ch in enumerate(reversed(payload)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - (total % 10)) % 10


@dataclass
class NpiRecord:
    """Normalized subset of an NPPES provider record."""
    npi: str
    status: str                    # verified | not_found | invalid | unchecked
    name: str = ""
    credential: str = ""
    taxonomy: str = ""
    enumeration_type: str = ""     # Individual | Organization
    address: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    phone: str = ""
    note: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _parse_nppes(npi: str, payload: dict) -> NpiRecord:
    results = payload.get("results") or []
    if not results:
        return NpiRecord(npi=npi, status="not_found",
                         note="Well-formed NPI, but no NPPES record.")
    r = results[0]
    basic = r.get("basic") or {}
    etype = "Organization" if r.get("enumeration_type") == "NPI-2" else "Individual"
    if etype == "Organization":
        name = basic.get("organization_name", "")
    else:
        name = " ".join(x for x in [basic.get("first_name", ""), basic.get("last_name", "")] if x)

    taxonomy = ""
    for t in (r.get("taxonomies") or []):
        if t.get("primary"):
            taxonomy = t.get("desc", "")
            break
    if not taxonomy and r.get("taxonomies"):
        taxonomy = r["taxonomies"][0].get("desc", "")

    addr = {}
    for a in (r.get("addresses") or []):
        if a.get("address_purpose") == "LOCATION":
            addr = a
            break
    if not addr and r.get("addresses"):
        addr = r["addresses"][0]

    return NpiRecord(
        npi=npi,
        status="verified",
        name=name.strip().title(),
        credential=basic.get("credential", "") or "",
        taxonomy=taxonomy,
        enumeration_type=etype,
        address=addr.get("address_1", "") or "",
        city=addr.get("city", "") or "",
        state=addr.get("state", "") or "",
        postal_code=addr.get("postal_code", "") or "",
        phone=addr.get("telephone_number", "") or "",
    )


def lookup(npi: str, timeout: int = 20) -> NpiRecord:
    """Look up one NPI against the live NPPES API.

    Never raises on network failure — returns an ``unchecked`` record with the
    reason, so a blocked network degrades to validation-only.
    """
    npi = (npi or "").strip()
    if not luhn_valid(npi):
        return NpiRecord(npi=npi, status="invalid",
                         note="Fails NPI format/check-digit validation — likely a typo.")
    url = NPPES_URL + "?" + urllib.parse.urlencode({"version": NPPES_VERSION, "number": npi})
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return NpiRecord(npi=npi, status="unchecked",
                         note=f"NPPES unreachable ({type(exc).__name__}); validated format only.")
    except json.JSONDecodeError:
        return NpiRecord(npi=npi, status="unchecked", note="NPPES returned unparseable JSON.")
    return _parse_nppes(npi, payload)


def load_sidecar(path: str | Path) -> dict[str, NpiRecord]:
    """Load pre-fetched NPPES records from a JSON sidecar.

    Accepts either ``{"<npi>": {...raw NPPES payload or normalized fields...}}``
    or a list of normalized records with an ``npi`` key.
    """
    data = json.loads(Path(path).read_text())
    out: dict[str, NpiRecord] = {}
    items = data.items() if isinstance(data, dict) else ((d.get("npi", ""), d) for d in data)
    for npi, val in items:
        npi = str(npi).strip()
        if not npi:
            continue
        if isinstance(val, dict) and "results" in val:
            out[npi] = _parse_nppes(npi, val)
        elif isinstance(val, dict):
            known = {f for f in NpiRecord.__dataclass_fields__}
            fields = {k: v for k, v in val.items() if k in known}
            fields.setdefault("npi", npi)
            fields.setdefault("status", "verified")
            out[npi] = NpiRecord(**fields)
    return out


def enrich_targets(targets, sidecar: dict[str, NpiRecord] | None = None,
                   online: bool = True) -> tuple[list, dict]:
    """Validate/enrich every target in place. Returns (records, summary).

    Merge policy: registry data *fills gaps and corrects specialty*, but never
    overwrites the rep's own commercial fields (value, volume, status, notes).
    """
    sidecar = sidecar or {}
    records: list[NpiRecord] = []
    summary = {"verified": 0, "not_found": 0, "invalid": 0, "unchecked": 0, "missing_npi": 0}

    for t in targets:
        npi = (t.npi or "").strip()
        if not npi:
            summary["missing_npi"] += 1
            t.notes = _append_note(t.notes, "No NPI on record — cannot verify.")
            continue

        if npi in sidecar:
            rec = sidecar[npi]
        elif online:
            rec = lookup(npi)
        else:
            rec = NpiRecord(npi=npi,
                            status="invalid" if not luhn_valid(npi) else "unchecked",
                            note="Offline mode — format check only.")
        records.append(rec)
        summary[rec.status] = summary.get(rec.status, 0) + 1

        if rec.status == "verified":
            # Correct/fill specialty and location; leave commercial fields alone.
            if rec.taxonomy:
                if t.specialty and rec.taxonomy.lower() != t.specialty.lower():
                    t.notes = _append_note(
                        t.notes, f"Specialty per NPPES: {rec.taxonomy} (was '{t.specialty}')")
                t.specialty = rec.taxonomy
            t.city = t.city or rec.city
            t.state = t.state or rec.state
            if rec.phone:
                t.notes = _append_note(t.notes, f"Phone: {rec.phone}")
            t.notes = _append_note(t.notes, "NPI verified in NPPES.")
        elif rec.status == "invalid":
            t.notes = _append_note(t.notes, f"⚠ Invalid NPI ({npi}) — {rec.note}")
        elif rec.status == "not_found":
            t.notes = _append_note(t.notes, f"⚠ NPI {npi} not found in NPPES.")

    return records, summary


def _append_note(existing: str, addition: str) -> str:
    existing = (existing or "").strip()
    return f"{existing} | {addition}" if existing else addition
