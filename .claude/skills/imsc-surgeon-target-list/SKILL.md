---
name: imsc-surgeon-target-list
description: Build, score, and tier an InterMed SoCal surgeon target list from AcuityMD exports (the All Extremity strategy plus indication, procedure, or CPT searches), ranked on Acumed, Orthocell Remplir, and Bonesupport CERAMENT G opportunity, with cross-line flags and rep assignment. Use when Mike asks to build or refresh a surgeon target list, rank surgeons in the territory, find who to call on for Acumed, Remplir, or CERAMENT G, tier surgeons A/B/C, or decide which surgeons get a target brief. For a deep dive on one named surgeon, use imsc-surgeon-target-brief instead.
---

# IMSC Surgeon Target List

## Mission and boundaries
Turn AcuityMD exports into a ranked, defensible list of who each rep should work next, and why. One list, three product lines, one score per surgeon that a rep can explain in a sentence. This skill builds and ranks the list; `imsc-surgeon-target-brief` does the per-surgeon deep dive on the names it hands off.

Territory: Orange County plus surrounding areas. Never include San Diego County. Never include discontinued Extremity Medical.

Data rules: AcuityMD exports are licensed IMSC data. Keep them internal, never paste them to third-party services, never request or store PHI. Procedure counts are aggregate claims volumes, not patients. Never invent volumes, relationships, or adoption status. Every number in the output traces to a named export and date.

## Inputs
1. **All Extremity strategy export** from AcuityMD Targeting (surgeon, facility, city, and the strategy columns: Femur Fracture +28, Distal Radius, Hand Fracture, Clavicle, Ankle Fracture, CMC, and any others present). Required.
2. **Indication / procedure / CPT search exports** for Remplir and CERAMENT G (nerve repair and osteomyelitis searches; code list in `references/scoring.md`). Optional per line; a line with no export is scored `No data`, never zero.
3. **Rep map**: facility or city to rep. Optional; unmatched surgeons show `Unassigned`.
4. **Current customer list** by line, if Mike supplies it, to split Grow (already using) from Convert (not yet).
5. Overrides from Mike: weights, tier cutoffs, territory counties, list length.

State the export name and pull date for every input at the top of the output. If an export's columns differ from what is described here, map them explicitly and show the mapping before scoring.

## Procedure
1. **Normalize.** One row per surgeon. Merge exports on NPI when present, otherwise on name + facility, and list every merge you were not certain of. A surgeon at several facilities stays one row with all facilities listed.
2. **Filter.** Remove San Diego County, surgeons with zero volume on every scored line, and anyone flagged inactive. Move removed rows to an Exclusions tab with the reason. Flag, do not remove, surgeons outside the confirmed county list.
3. **Score each line 0 to 100** by percentile rank of that line's volume among surgeons in this list (method in `references/scoring.md`). Blanks and "-" in AcuityMD mean no reported volume; treat as 0 for ranking but show "-" in the output.
4. **Composite score.** Weighted sum of the three line scores using Mike's weights, or the defaults in `references/scoring.md`, stated on the Method tab. Re-normalize weights across lines that have data so a missing export does not sink everyone.
5. **Tier.** A, B, C by composite rank using the cutoffs in `references/scoring.md`. Add flags, not score changes, for: Cross-line (top third on two or more lines), Grow vs Convert, Competitive tie (Open Payments or AcuityMD relationships to a competitor, if supplied), and Facility access unknown.
6. **Assign reps** from the rep map. Then check balance: A-tier count per rep, and any rep with no A-tier targets.
7. **Hand off.** Name the top targets (default 10, or Mike's number) to run through `imsc-surgeon-target-brief`, each with a one-line reason.
8. **QA.** Recount rows in and out, re-add one composite by hand, confirm no San Diego County rows, and confirm every number has a source.

## Output contract
- **Header:** `IMSC Surgeon Target List | Territory | Exports used + pull dates | Prepared for Mike Mizuha`.
- **Summary (top of reply, fits one screen):** total surgeons scored, A/B/C counts, top 10 with composite and the line driving each, A-tier count per rep, the three biggest cross-line opportunities, and data gaps.
- **Spreadsheet** (xlsx, or CSV if xlsx is unavailable) with tabs:
  - `Ranked List`: Rank | Tier | Surgeon | NPI | Facility | City | County | Rep | Acumed vol | Acumed score | Remplir vol | Remplir score | CERAMENT G vol | CERAMENT G score | Composite | Flags | Why (one line).
  - `By Rep`: the same rows grouped by rep, A-tier first.
  - `Cross-Line`: surgeons flagged Cross-line.
  - `Exclusions`: removed rows and reason.
  - `Method`: weights, cutoffs, export names and dates, column mapping, merge notes.
- **Brief queue:** the hand-off list for `imsc-surgeon-target-brief`.
- For a PDF or slide, use IMSC black-and-gold styling with the supplied logo only.

## Tone
Direct and plain. Short sentences, light bold, no em dashes. The "Why" column reads like something a rep would say to their manager: "Top 5% ankle fracture volume, operates at an IMSC account, no Remplir use yet."
