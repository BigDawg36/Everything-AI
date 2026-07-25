"""Score AcuityMD targets for a medical-device sales motion.

The score is a transparent 0-100 weighted blend of the signals AcuityMD (and
enrichment sources like the NPI registry) give you. Weights live in settings so
a sales manager can retune them without touching code.
"""
from __future__ import annotations

from ..models import Target

DEFAULT_WEIGHTS = {
    "opportunity": 0.35,   # est_annual_value, normalized
    "volume": 0.25,        # procedure_volume, normalized
    "displaceable": 0.20,  # competitor_share (higher share = more to win)
    "growth": 0.15,        # growth_rate
    "freshness": 0.05,     # penalize stale/never-touched when engaged
}

TIERS = [(80, "A"), (60, "B"), (40, "C"), (0, "D")]


def _normalize(values: list[float]) -> dict[int, float]:
    """Min-max normalize a list to 0-1, keyed by index. Flat lists -> 0.5."""
    if not values:
        return {}
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return {i: 0.5 for i in range(len(values))}
    return {i: (v - lo) / (hi - lo) for i, v in enumerate(values)}


def score_targets(targets: list[Target], weights: dict | None = None) -> list[Target]:
    """Score and tier every target in place; returns the same list sorted by
    score descending so the top of the list is where a rep should start."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    if not targets:
        return targets

    n_opp = _normalize([t.est_annual_value for t in targets])
    n_vol = _normalize([t.procedure_volume for t in targets])
    n_grw = _normalize([t.growth_rate for t in targets])

    for i, t in enumerate(targets):
        displaceable = max(0.0, min(1.0, t.competitor_share))
        # Freshness: an engaged/customer target with no recent touch is a risk
        # to attend to; a brand-new prospect is neutral.
        freshness = 0.5
        if t.status in ("engaged", "customer") and not t.last_touch:
            freshness = 1.0  # needs attention -> boosts it up the list

        raw = (
            w["opportunity"] * n_opp.get(i, 0.5)
            + w["volume"] * n_vol.get(i, 0.5)
            + w["displaceable"] * displaceable
            + w["growth"] * n_grw.get(i, 0.5)
            + w["freshness"] * freshness
        )
        t.score = round(raw * 100, 1)
        t.tier = next(tier for threshold, tier in TIERS if t.score >= threshold)

    targets.sort(key=lambda t: t.score, reverse=True)
    return targets


def tier_summary(targets: list[Target]) -> dict[str, int]:
    out = {"A": 0, "B": 0, "C": 0, "D": 0}
    for t in targets:
        out[t.tier] = out.get(t.tier, 0) + 1
    return out
