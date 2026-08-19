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

# Named profiles for common medical-device sales motions. The right weighting
# genuinely differs by what you sell — pick the closest and tune from there.
PROFILES = {
    # Balanced default.
    "balanced": DEFAULT_WEIGHTS,

    # Implants / high-ASP constructs: a few big accounts dominate. Deal size and
    # displacing the incumbent matter far more than raw case count.
    "implant": {
        "opportunity": 0.45, "volume": 0.15, "displaceable": 0.25,
        "growth": 0.10, "freshness": 0.05,
    },

    # Capital equipment: long cycles, few buyers. Budget-sized opportunity and
    # growth (is the service line expanding?) dominate; incumbent share matters
    # less because it's a purchase, not a conversion.
    "capital": {
        "opportunity": 0.50, "volume": 0.10, "displaceable": 0.10,
        "growth": 0.25, "freshness": 0.05,
    },

    # Disposables / consumables: revenue tracks case volume almost linearly, and
    # share-of-wallet conversion is the whole game.
    "disposable": {
        "opportunity": 0.20, "volume": 0.40, "displaceable": 0.30,
        "growth": 0.05, "freshness": 0.05,
    },

    # Service-line / hospital partnership plays: chase growth and engagement
    # recency over pure deal size.
    "service_line": {
        "opportunity": 0.25, "volume": 0.25, "displaceable": 0.10,
        "growth": 0.30, "freshness": 0.10,
    },
}

TIERS = [(80, "A"), (60, "B"), (40, "C"), (0, "D")]


def resolve_weights(settings: dict | None = None, profile: str | None = None) -> dict:
    """Resolve scoring weights.

    Precedence, most-specific wins:

    1. ``--profile X`` on the CLI → exactly ``PROFILES[X]``. An explicit flag is
       an explicit choice, so settings-file ``weights`` do **not** silently
       override it (that made ``--profile`` a no-op whenever the settings file
       happened to define weights).
    2. Otherwise → ``PROFILES[settings.scoring.profile or "balanced"]`` with
       ``settings.scoring.weights`` layered on top as hand-tuned overrides.
    """
    settings = settings or {}
    scoring = settings.get("scoring") or {}

    if profile:
        base = PROFILES.get(profile)
        if base is None:
            raise ValueError(
                f"Unknown scoring profile {profile!r}. Choose one of: {', '.join(sorted(PROFILES))}"
            )
        return dict(base)

    name = scoring.get("profile") or "balanced"
    base = PROFILES.get(name)
    if base is None:
        raise ValueError(
            f"Unknown scoring profile {name!r} in settings. "
            f"Choose one of: {', '.join(sorted(PROFILES))}"
        )
    return {**base, **(scoring.get("weights") or {})}


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
