---
name: imsc-command-center-release-gate
description: Run a defensible, evidence-based pre-release acceptance review for the IMSC Sales Command Center and CRM, including Power BI report reconciliation, rep activity/follow-up behavior, AcuityMD targeting, permissions, product-line views, and rollback readiness. Use after CRM/dashboard changes or before a Netlify deployment.
---

# IMSC Command Center Release Gate

## Mission and boundaries
Protect the integrity of InterMed SoCal's operational system. Verify that a dashboard release improves reliable rep execution and management visibility rather than only looking better. Scope: territory reporting, surgeon/facility association, owner assignment, activities, overdue reminders, AcuityMD target status, Power BI freshness, and separate Acumed, Orthocell and BONESUPPORT line views. Exclude discontinued Extremity Medical from current navigation, mockups and reporting. Never claim a test ran unless there is test evidence. Prefer read-only checks; never deploy, reset data, modify roles, send notifications or write CRM records unless Mike expressly authorizes that action and the connected tool permits it.

No PHI, patient identifiers, confidential account pricing, passwords, tokens or raw sensitive exports may be stored, embedded in screenshots, placed in issue tickets, or sent to external services. Use sanitized synthetic fixtures where possible.
## Inputs
- Release version/build SHA, deployed or staging URL, date/time and change log.
- Role matrix and expected access levels; current configured schema and workflows.
- Authorized read-only CRM snapshot and independent Power BI extract, each with as-of timestamps and data dictionary. If absent, mark reconciliation untested.
- Previous accepted baseline, if provided, and expected product-line/territory filters.
- Requirements for AcuityMD integration, activity logging, surgeon tagging, overdue alerts to Mike and Tim, and mobile/iPhone use.

## Procedure
1. **Define what changed.** List new features, affected tables, integrations, data feeds, pages, roles and notifications. Separate documented requirements from assumptions.
2. **Build a test matrix** with ID, requirement, severity, method, expected result, actual result, evidence location, tester, timestamp and pass/fail/blocked/not-run. Never silently convert `Not run` into `Pass`.
3. **Data lineage and freshness.** Map Power BI source to extract to Command Center row. Verify report/extract as-of date, territory/rep/facility/surgeon join keys, inactive staff handling, totals and record counts. Compare representative samples and full aggregations where data exists; no made-up tolerances. If no tolerance was approved, require exact matches for integer counts and explain currency rounding policy rather than using arbitrary materiality.
4. **Rep activity and follow-up.** Test create, assign, edit, view and close activities with synthetic records; verify due dates and time zones; reopened tasks; owner visibility; overdue labels; manager summaries; duplicate suppression; and that notifications never go to wrong recipients. Test any alerts on synthetic scheduled items only and only with explicit approval.
5. **Territory and surgeon workflow.** Confirm correct account/facility/surgeon hierarchy, active territory mapping, deduplication rules, empty states, search and tagging, and AcuityMD target status. Distinguish linked data actually synced from a placeholder integration.
6. **Product-line segmentation.** Verify distinct Acumed, Orthocell and BONESUPPORT views, filters, records and permission paths. Flag leakage or mixing between lines; verify absent discontinued-line navigation.
7. **Permissions and privacy.** Use authorized test accounts for admin, VP, territory rep and associate. Verify least-privilege access, row-level territory scoping, safe error messages, no PHI, no confidential pricing in page source or logs. A public URL opening does not prove the underlying role rules are correct.
8. **User experience and reliability.** Run responsive checks for iPhone and desktop, keyboard navigation, loading/error/empty states, session expiry, PWA/offline expectations, link integrity and navigation. Reuse a frontend QA skill for visual details rather than duplicating its checks.
9. **Regression and rollback.** Compare against known-good release, test migration/idempotency and notification side effects where safe, confirm backup/export restore process and rollback owner. Do not execute rollback without approval.
10. **Decision and communication.** Classify defects P0 data exposure/wrong-recipient alerts or major data corruption; P1 broken core workflow/material report mismatch; P2 impaired workflow; P3 polish. Default `NO-GO` for unresolved P0/P1, and `HOLD / INCOMPLETE` if critical tests were not run. Produce three priority actions, owner, deadline and verification step. Never say `GO` without named and dated test evidence.

## Output contract
- Header: `IMSC Sales Command Center | Release Gate | Version | Tested at | Prepared by Mike Mizuha, VP of Sales`.
- Go / No-go / Hold verdict with concise reason and evidence coverage count.
- Requirement and test matrix: `ID | Requirement | Actual | Evidence | Severity | Result`.
- Reconciliation: source dates, control totals, differences, root cause or `Not tested`.
- Blocker register: owner, next action, deadline, retest condition.
- Manager summary: top three actions for Mike/Tim, expected operational benefit.
- Rollback readiness, limitations, and clean post-release verification checklist.

## Tone and layout
Technical enough to be testable, understandable enough for sales leadership. Precise, direct, executive. Light bold, no em dashes, no unverified pass claims. Prefer actionable tables. When preparing a printable report, use IMSC premium black-and-gold styling and the supplied logo only.
