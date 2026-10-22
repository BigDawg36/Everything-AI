# Scoring reference

Everything here is a starting point. Confirm codes against AcuityMD's own code groupings before they drive rep activity. Mike's overrides always win; record them on the Method tab.

## Product line to data source

### Acumed (extremity fixation)
- Source: AcuityMD Targeting, Strategy = **All Extremity**.
- Volume = sum of the fracture and procedure columns Mike confirms are Acumed-relevant. Default: Distal Radius, Hand Fracture, Clavicle, Ankle Fracture, CMC, and Femur Fracture +28 (the "+28" column rolls up additional procedure groups; AcuityMD shows the detail when the row is expanded).
- If Mike pulls a single body-part strategy (Ankle, Foot, Hand, Wrist, Shoulder, Elbow, Hip, TLB), score that export as a sub-line and note it on the Method tab.

### Orthocell Remplir (peripheral nerve repair)
- Source: AcuityMD search by indication or procedure (peripheral nerve injury / nerve repair) or by CPT.
- Primary signals, nerve repair (suture/coaptation): 64831, 64832 (digital nerve), 64834 to 64837 (hand or foot nerves), 64856, 64857 (major peripheral nerve), 64910, 64911 (repair with conduit or vein allograft).
- Secondary signals, also scored: neuroplasty codes such as 64718 (ulnar nerve at elbow) and 64721 (carpal tunnel).

### Bonesupport CERAMENT G (antibiotic-eluting bone graft substitute)
- Source: AcuityMD search by indication **osteomyelitis**, plus CPT search.
- Signals, bone infection debridement and excision: 11044 (debridement including bone), and partial excision of bone for osteomyelitis such as 23180 (clavicle), 23184 (humerus), 25145 (forearm/wrist sequestrectomy), 27360 (femur), 27640 (tibia), 28122 (foot bone). Hardware removal (20680) is context only.

## Line score (0 to 100)
For each line: `score = percentile rank of the surgeon's volume among all surgeons in this list`, so the top surgeon is 100 and ties share a score. Surgeons with no reported volume score 0 and display "-". A line with no export at all is `No data` for everyone and drops out of the composite.

## Composite and weights
`composite = sum(weight x line score) / sum(weights of lines with data)`

Default weights, stated as defaults until Mike sets his own:
- Acumed 50
- Remplir 25
- CERAMENT G 25

## Tier cutoffs (by composite rank)
- **A**: top 20%.
- **B**: next 30%.
- **C**: remaining 50%.
- A surgeon with a line score of 90+ on any single line is at least B, even with a low composite, and gets a `Single-line spike` flag.

## Flags (never change the score)
- `Cross-line`: top third on two or more lines.
- `Grow` / `Convert`: already using the line per Mike's customer list, or not.
- `Competitive tie`: relationship to a competitor in the same category, from Open Payments or AcuityMD relationships. Internal context only.
- `Facility access unknown`: operates only at facilities not on the rep map.
- `Outside county list`: kept in the list but confirm it belongs in the territory.
