# Metric dictionary (medtech sales)

The shared vocabulary that AcuityMD (market/opportunity) and Power BI (booked
business) map onto. When a real model uses different names, map to these and note
the mapping in the report footer.

## Account / facility

| Metric | Source | Meaning |
|---|---|---|
| Account name / ID | Both | The facility, IDN, or practice |
| Site of care | AcuityMD | HOPD / ASC / office — drives pricing & access |
| Procedure (case) volume | AcuityMD | Addressable case count in-scope, annualized |
| Volume trend % | AcuityMD | YoY growth in relevant procedures (momentum) |
| Current vendor / share | AcuityMD | Competitive presence → displaceability |
| Payer mix | AcuityMD | Commercial vs. government skew |
| Current revenue | Power BI | What *we* book at this account today |
| Penetration | Derived | Our revenue ÷ addressable opportunity |
| Whitespace | Derived | Addressable opportunity with ~no current revenue |

## Provider / physician

| Metric | Source | Meaning |
|---|---|---|
| Provider name / NPI | AcuityMD | The implanter/proceduralist; NPI validates identity |
| Specialty | AcuityMD | Ortho, spine, cardiology, etc. |
| Procedure volume & trend | AcuityMD | Case flow for targeting |
| Affiliations | AcuityMD | Facilities/IDNs they practice at → access path |
| Referral pattern | AcuityMD | Upstream referrers (where available) |

## Rep / territory (Power BI)

| Metric | Meaning |
|---|---|
| Revenue (YTD / MTD / TTM) | Booked revenue for the period |
| Plan / quota & attainment | Revenue ÷ plan |
| YoY growth | vs. same period prior year |
| Product mix | Revenue by product line/category |
| Top / bottom accounts | Concentration and risk |
| Pipeline / open opps | Forward-looking (if the model has it) |
| Case count | Volume complement to revenue $ |

## Derived / trend measures (computed in `analyze_trends.py`)

- **Growth rate** — period-over-period and YoY %.
- **Rolling average** — 3-month smoothing to separate signal from noise.
- **Seasonality index** — month's share vs. its typical share.
- **Concentration** — top-N account share of revenue (risk indicator).
- **Anomaly flag** — a month outside a rolling band (e.g. ±2σ), for the watch list.

## Targeting inputs → score (used by `/pbi-acuity targets`)

Opportunity size (volume) · Momentum (trend) · Whitespace vs. penetration ·
Competitive displaceability · Access/affiliation. Weights are set in `SKILL.md`
and should be tuned to the user's current priorities (e.g. defend vs. expand).
