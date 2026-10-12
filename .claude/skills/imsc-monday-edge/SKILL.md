---
name: imsc-monday-edge
description: Produces the weekly issue of The Monday Edge, the four-page navy-and-gold PDF newsletter Big Mike sends to IMSC reps every Monday at 7:30am Pacific. Use when Mike says "Monday Edge", "this week's newsletter", "Issue 00X", "build the newsletter", or asks for the Friday preview. Handles topic selection against the Covered Log, verified content research, three subject lines, the WeasyPrint PDF build, and the Friday approval package.
---

# The Monday Edge: weekly issue builder

## Purpose
Turn one weekly request into a finished, approval-ready issue of The Monday Edge: a premium four-page PDF that reads like a curated publication, not an email blast. Educational, motivational, brand-consistent, and 100 percent verified.

## Inputs to gather (ask only for what is missing)
1. Issue number and Monday send date.
2. The current Covered Log (topics, products, and conditions used in past issues). If Mike does not paste it, ask for it or for the last issue PDF. Never guess what was covered.
3. Any must-include items this week: product launch, rep win to spotlight, course, quota push, policy note.
4. Current IMSC line card. Use only the manufacturers Mike confirms for this issue. Do not assume a line is still carried.

## Fixed structure (seven numbered sections, four pages)
- Page 1 (navy): masthead with IMSC seal, "Curated by Mike Mizuha" byline, issue number and date. Section 01, Feature (one product or technology deep dive).
- Page 2 (ivory): Section 02, Clinical Minute (one fracture pattern or condition: anatomy, classification, typical fixation options, what the surgeon worries about). Section 03, Portfolio Power (two or three IMSC products with one-line use case and one talk track each).
- Page 3 (navy): Section 04, Course Radar (upcoming verified conferences and courses with dates, city, and why reps should care).
- Page 4 (navy): Section 05, Leadership. Section 06, Sales Psychology (one principle, one field application). Section 07, Field Challenge (one measurable action for the week, with a stat block).

## Workflow
1. Topic selection. Propose a lineup for all seven sections. Check every topic against the Covered Log. No repeats of a product, condition, or principle within the last 8 issues unless Mike asks. Show the lineup in a short table and get a thumbs up before writing.
2. Research. Use primary sources: manufacturer IFUs and surgical technique guides, FDA 510(k) database, peer-reviewed literature (PubMed), and official society sites for conference dates. Record a source for every factual claim. If a fact cannot be verified, drop it or mark it "VERIFY" in the draft.
3. Write. Tone: confident, direct, respectful, motivational. Active voice. Short paragraphs. No em dashes. Light bold only for section labels. No hype words (revolutionary, game-changing, best-in-class). Each section ends with one "Use it this week" line tied to a real account action.
4. Subject lines. Write three options, under 55 characters, no clickbait.
5. Build the PDF. HTML/CSS with inline WeasyPrint-compatible styles, rendered with WeasyPrint (base_url='.'). Palette: deep navy/royal indigo primary, gold accents, ivory contrast page. Playfair Display serif headers, clean sans body. Brushed-silver circular IMSC seal, subtle hexagon texture. Image zones are typographic callout panels. Never use AI-generated clinical or radiograph-style images. Use only real licensed images Mike provides.
6. QA before delivery. Render page images and check: exactly four pages, no overflow or orphaned headers, colors match, every claim has a source, no em dashes, dates are in the future and correct.
7. Deliver the Friday preview package:
   - The PDF.
   - The three subject lines.
   - A source list for every claim.
   - The updated Covered Log (append this issue's topics).
   - A compliance flag list (see below).

## Compliance guardrails
- Product content must stay on-label and match the manufacturer's approved indications and IFU language. No off-label suggestions, no comparative superiority claims, no clinical outcome claims beyond what the cited source states, and no pricing.
- Flag every product or clinical claim in the compliance list with: "Needs compliance review before use with customers or reps."
- No PHI, patient names, case details, or account pricing anywhere in the issue.

## Output standard
Polished enough that Mike only reviews and approves. If anything is uncertain, list it at the top of the preview package under "Verify before Monday."
