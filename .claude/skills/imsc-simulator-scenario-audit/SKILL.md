---
name: imsc-simulator-scenario-audit
description: Design and audit clinically accurate, realistic synthetic surgeon and podiatrist conversations for the InterMed SoCal Surgeon Call Simulator and ElevenLabs voice agent. Use for simulator scenario prompts, tough objections, rep coaching scorecards, call transitions, and synthetic QA of sales-call roleplays. This is a scenario and training-content skill, not UI testing.
---

# IMSC Surgeon Simulator Scenario Audit

## Purpose
Build difficult but winnable, realistic voice roleplays that coach InterMed SoCal reps to discover relevant clinical needs, discuss only approved products and evidence, handle skepticism without pressure, and earn a specific next step when appropriate. The experience should resemble a busy orthopedic surgeon or podiatrist, not a quiz bot. This skill owns **scenario content, clinician behavior, scorecards, and synthetic conversation tests**. Use frontend-visual-qa or webapp-testing for pixels, navigation, browser compatibility, or Netlify release verification instead.

## When to use
- Mike requests an IMSC Surgeon Call Simulator scenario, persona, rubric, voice-agent prompt, or surgical sales call roleplay.
- The same objection, product selection, interruption, sales discovery, or debrief needs repeated revision.
- Mike wants a balanced quality audit of a transcript or a realistic training set for traumatologists, hand/extremity surgeons, sports medicine, plastics, or podiatrists.
- He asks to improve ElevenLabs agent realism without adding features he did not ask for.

## Inputs and source-of-truth
1. Specialty, setting, desired difficulty, training skill, and specific surgical indication or workflow.
2. Only current approved materials for product facts: product IFU/labeling, authorized training decks, approved claims matrices and properly sourced peer-reviewed evidence when appropriate.
3. Relevant IMSC product line from Mike's currently authorized catalog. Include Acumed, BONESUPPORT, Orthocell, ABYRX, OsteoMed, Turner Imaging, restor3d, Orthomed, ExsoMed, ITS, Voom, Xperience, Artoss, Bacterin, BioAccess and Next Science only when genuinely relevant. Never add discontinued/disallowed vendors.
4. Platform constraints when known: mobile and desktop, ElevenLabs conversational agent, Netlify-hosted app, interruptions and hospital Wi-Fi sensitivity.
5. Approved objectives and rubric from the user, when supplied. Do not silently redefine the assessment standard.

Where clinical claims or indications are not supplied, use explicit **[PRODUCT FACT REQUIRED]** placeholders. Do not invent device specifications, FDA indications, study results, or pricing.

## Scenario design procedure
1. Pick a **specific** specialty and real-world call context (e.g., a busy surgeon between cases, a podiatrist planning a complex reconstruction). State time pressure and why this visit may matter.
2. Construct a fictional persona card: specialty, years in practice (fictional), practice setting, dominant workflow, familiarity with the product category, two authentic objections, preferred communication style, and one hidden but discoverable need. Never reuse a real clinician's private behavior or patient details.
3. Define exactly one primary sales learning goal and no more than two secondary goals. Default learning goals: relevant discovery, clinical workflow understanding, evidence discipline, objection handling, concise value framing, OR support expectations, and an appropriate next step.
4. Build a five-beat conversation path, **not** a fixed script: opening resistance; discovery opportunity; material objection; deeper follow-up or surprise constraint; evidence-based commitment or justified no-decision. The surgeon should adapt to rep replies, respond to questions asked, and avoid prematurely rewarding generic pitches.
5. Design 3 levels of objection depth. Examples: existing vendor preference, staff/setup burden, inventory availability, value vs cost, prior clinical concern, insufficient evidence, time pressure. All objections must remain fictional and non-patient-specific.
6. Write the **voice-agent system prompt** with explicit persona, behavior constraints, what to reveal only if the rep asks, interruption behavior, realism calibration, allowed and prohibited claims, success/failure rules, safety exits, and wrap-up trigger. Require concise spoken turns; never hallucinate device specifications.
7. Create a scoring rubric totaling 100 points: preparation/relevance 10, discovery 25, clinical/product accuracy and claims discipline 25, objection handling 20, next step and mutual action 15, professionalism and empathy 5. If the user already supplied a rubric, use theirs instead and note differences.
8. Include absolute disqualifiers: invented claims, patient identifiers, fabricated study results, coercive sales tactics, or knowingly misleading statements. A scenario may show a learning mistake but may never reward it.
9. Provide a brief two-pass synthetic transcript fixture: one weak rep exchange and one stronger rep exchange. Score both against the same rubric and explain why the stronger one did better. Use fictional identities and no real patient/case details.
10. Specify deployment-safe handoff notes separately from QA results. Do **not** change a live ElevenLabs agent, publish to Netlify, or modify the simulator unless Mike explicitly approved that change.

## Quality gates
- **Realism:** surgeon challenges unsupported claims; rep has to earn attention; prompts avoid canned agreement. Dialogue is natural and short enough for voice.
- **Factual accuracy:** every specific claim matches current approved materials or is marked as a placeholder. Never include invented study data, device specs, operative details, or payer claims.
- **Training value:** the exercise has a measurable skill objective and a useful debrief with specific behaviors the rep can change next call.
- **Accessibility and pacing:** tolerate speech pauses, interruptions, misunderstood names, and dropped/restarted audio; no assumptions about an uninterrupted 10-minute session.
- **Safety:** no PHI, real patient examples, confidential account prices or exact contract terms, stored voice credentials, real surgeon personality assertions, or prompts for unauthorized access.
- **Scope:** content-only audit does not assert that the app or integration functions, nor that the scenarios have been deployed.

## Output contract
Return in this order:
1. **Scenario card**: specialty, context, primary skill goal, difficulty, opening line, hidden need and objections.
2. **Agent prompt**: copy/paste-ready self-contained voice-roleplay system instruction that includes response limits, branching and guardrails.
3. **Scorecard**: six criteria with weights and 1-2 observable high-scoring behaviors each.
4. **Synthetic tests**: weak/strong examples, scores and coaching notes, all invented and de-identified.
5. **Claim sources**: table of each product-specific claim with its evidence or [PRODUCT FACT REQUIRED].
6. **Handoff**: proposed changes to ElevenLabs instructions and acceptance tests; status **Draft, Not deployed** unless deployment was explicitly requested and verified.

## Style and execution
Premium InterMed SoCal black-and-gold theme if visuals requested, otherwise structured readable plain text. Direct, professional, concise, no em dashes, light bold. Preserve Mike's established rep objectives and never assume that the hardest call requires a sale. Credible no-decision or trial hesitation is a valid end state. Prefer the smallest change that fixes the requested training issue. Never invent clinical or product claims or upload sensitive company data to unknown plugins.

## Safe trigger example
"Use IMSC Simulator Scenario Audit to build a difficult but fair 6-minute voice roleplay with a skeptical hand surgeon considering an Acumed product. Use placeholders where the indication is not provided, then score one weak and one strong synthetic call."
