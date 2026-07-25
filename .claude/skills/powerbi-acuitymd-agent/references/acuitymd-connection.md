# AcuityMD connection

AcuityMD is a proprietary medtech commercial-intelligence platform.

> **This org has browser-export access only — no API.** Path 1 below (browser
> automation) is the one to use. Path 2 (the API) is kept for reference in case
> an API entitlement is added later, but don't reach for it now.

---

## Path 1 — Browser automation (the path for this org)

Log in through the web app and export, using Playwright. The repo already ships
a `playwright-skill` — reuse its runner, or use `scripts/acuitymd_client.py
--browser`, which drives a headed/headless login and downloads the export.

**Credentials** (never hard-code — pull from env):

```
ACUITYMD_EMAIL=...
ACUITYMD_PASSWORD=...
# If SSO (Okta/Google/Microsoft) or MFA is enforced, run headed (not headless)
# so the user completes SSO/MFA once; persist the session with a storageState file.
```

Recommended pattern (robust to SSO/MFA):

1. **First run, headed, persist session.** Launch a headed browser, let the user
   complete SSO + MFA manually, then save `context.storage_state()` to
   `~/.acuitymd_state.json`.
2. **Later runs reuse the session** by loading that storage state — no password
   needed until it expires.
3. Navigate to the target list / provider view, apply filters, and **export**
   (AcuityMD exports lists to CSV/XLSX). Read the downloaded file, don't scrape
   the DOM — exports are stabler than page markup.

Browser automation is inherently brittle (selectors and flows change). When it
breaks, prefer re-checking whether API access can be turned on rather than
chasing selectors.

> **Respect the platform's terms.** Automate your *own* authenticated session for
> your own account's data and normal export features. Don't scrape at volumes or
> in ways your AcuityMD agreement prohibits — check with your CSM if unsure.

---

## Path 2 — AcuityMD API (reference only — not available to this org)

Not currently usable here (no API entitlement). If AcuityMD ever turns on API
access for the org, ask the CSM for the base URL + auth (bearer token or OAuth2
client-credentials) and the entitled objects, then set `ACUITYMD_BASE_URL` and
`ACUITYMD_API_TOKEN` (or the client-id/secret pair) in `.env` and run
`acuitymd_client.py --api`. The endpoint paths in that script's `ENDPOINTS` map
are placeholders to verify against the real API docs. Until then, use Path 1.

---

## Normalizing the output

Whichever path you use, land the data in one shape before analysis so the rest
of the skill doesn't care how it was fetched. `acuitymd_client.py` returns (and
can write to CSV) a list of records with these keys:

```
account_id, account_name, site_of_care, city, state,
provider_npi, provider_name, specialty,
procedure_group, annual_volume, volume_trend_pct,
current_vendor, payer_mix, affiliations, list_name, pulled_at
```

Missing fields come back as `null` — never invented. The `provider_npi` lets you
cross-check against the NPI Registry connector if you want to validate a name.
