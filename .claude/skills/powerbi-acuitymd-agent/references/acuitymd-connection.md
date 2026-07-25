# AcuityMD connection

AcuityMD is a proprietary medtech commercial-intelligence platform. Access to
its data programmatically comes in two ways. **Prefer the API.** Fall back to
browser automation only when API access isn't provisioned.

---

## Path 1 — AcuityMD API (preferred)

AcuityMD offers API / data-integration access to enterprise customers. It is not
a public, self-serve API — you have to have it turned on for your org.

**To get access:** ask your AcuityMD **admin or Customer Success Manager** for
API credentials (a base URL + API token / OAuth client). Confirm:
- the **base URL** for your tenant's API,
- the **auth scheme** (usually a bearer token or OAuth2 client-credentials),
- which **objects** you're entitled to (accounts/facilities, providers,
  procedures, territories, saved lists/targets),
- rate limits.

Set in `.env`:

```
ACUITYMD_BASE_URL=https://api.acuitymd.com   # confirm the real host with your CSM
ACUITYMD_API_TOKEN=...                        # bearer token, OR:
ACUITYMD_CLIENT_ID=...
ACUITYMD_CLIENT_SECRET=...
ACUITYMD_TERRITORY=...                         # default territory filter
```

`scripts/acuitymd_client.py` is written against a conventional REST shape
(bearer auth, `/providers`, `/accounts`, `/procedures` with query filters and
cursor pagination). **Because tenants differ, treat the endpoint paths as
placeholders** — verify them against the API docs your CSM provides and adjust
the `ENDPOINTS` map at the top of the script. The script is structured so that's
a one-line change per endpoint.

What to pull (map to `references/medtech-metrics.md`):
- Providers/facilities in territory with **procedure volumes** and **trend**.
- **Site of care** (HOPD vs. ASC vs. office) and payer mix where available.
- **Competitive / current-vendor** signals.
- Existing **saved lists / targets** so you don't duplicate the rep's work.

---

## Path 2 — Browser automation fallback (no API)

If the org has no API entitlement, log in through the web app and export, using
Playwright. The repo already ships a `playwright-skill` — reuse its runner, or
use `scripts/acuitymd_client.py --browser` which drives a headed/headless login.

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
