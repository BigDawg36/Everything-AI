#!/usr/bin/env python3
"""AcuityMD client for the sales agent.

Two modes:
  * --api      : call the AcuityMD REST API (bearer token or OAuth2 client creds)
  * --browser  : Playwright fallback that logs into the web app and reads an
                 exported CSV (for orgs without API access)

Both modes normalize output to the record shape documented in
references/acuitymd-connection.md and can write it to CSV.

IMPORTANT: AcuityMD tenants differ. The ENDPOINTS map below is a *placeholder* —
confirm the real base URL and paths with your AcuityMD CSM and edit them here.

Secrets are read from the environment only. See .env.example.

Examples
--------
  python acuitymd_client.py --api targets --territory "SoCal" --out targets.csv
  python acuitymd_client.py --browser export --url "<saved list url>" --out targets.csv

Requires: requests (api mode), playwright (browser mode).
"""
import argparse
import csv
import json
import os
import sys

# --- Normalized output columns (keep in sync with the reference doc) ----------
COLUMNS = [
    "account_id", "account_name", "site_of_care", "city", "state",
    "provider_npi", "provider_name", "specialty",
    "procedure_group", "annual_volume", "volume_trend_pct",
    "current_vendor", "payer_mix", "affiliations", "list_name", "pulled_at",
]

# --- Endpoint map: VERIFY + EDIT against your tenant's API docs ----------------
ENDPOINTS = {
    "providers": "/v1/providers",
    "accounts": "/v1/accounts",
    "procedures": "/v1/procedures",
    "lists": "/v1/lists",
}


def _env(name, required=True):
    val = os.environ.get(name)
    if required and not val:
        sys.exit(f"Missing required env var: {name} (see .env.example)")
    return val


def _now():
    # Import here so browser-only users don't need anything extra.
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ============================ API MODE ========================================
def _api_token():
    """Bearer token directly, or fetch one via OAuth2 client-credentials."""
    token = os.environ.get("ACUITYMD_API_TOKEN")
    if token:
        return token
    # OAuth2 client-credentials fallback
    import requests
    cid = _env("ACUITYMD_CLIENT_ID")
    secret = _env("ACUITYMD_CLIENT_SECRET")
    base = _env("ACUITYMD_BASE_URL")
    r = requests.post(
        f"{base}/oauth/token",
        data={"grant_type": "client_credentials",
              "client_id": cid, "client_secret": secret},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def api_pull(resource, params):
    """GET a resource with cursor pagination; return raw records."""
    import requests
    base = _env("ACUITYMD_BASE_URL")
    token = _api_token()
    path = ENDPOINTS.get(resource, f"/v1/{resource}")
    url = f"{base}{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    out, cursor = [], None
    while True:
        q = dict(params)
        if cursor:
            q["cursor"] = cursor
        r = requests.get(url, headers=headers, params=q, timeout=60)
        if r.status_code != 200:
            sys.exit(f"AcuityMD {resource} {r.status_code}: {r.text[:500]}")
        payload = r.json()
        records = payload.get("data", payload if isinstance(payload, list) else [])
        out.extend(records)
        cursor = payload.get("next_cursor") or (payload.get("meta", {}) or {}).get("next_cursor")
        if not cursor:
            break
    return out


def normalize(raw, list_name=""):
    """Best-effort map of a raw AcuityMD record to COLUMNS. Missing -> None.

    Tenant field names vary; adjust the .get() keys to match your API payload.
    """
    def g(*keys):
        for k in keys:
            if isinstance(raw, dict) and raw.get(k) not in (None, ""):
                return raw.get(k)
        return None

    return {
        "account_id":       g("account_id", "facility_id", "id"),
        "account_name":     g("account_name", "facility_name", "name"),
        "site_of_care":     g("site_of_care", "care_setting"),
        "city":             g("city"),
        "state":            g("state", "region"),
        "provider_npi":     g("npi", "provider_npi"),
        "provider_name":    g("provider_name", "physician_name", "name"),
        "specialty":        g("specialty", "taxonomy"),
        "procedure_group":  g("procedure_group", "procedure", "category"),
        "annual_volume":    g("annual_volume", "volume", "case_volume"),
        "volume_trend_pct": g("volume_trend_pct", "trend", "yoy_growth"),
        "current_vendor":   g("current_vendor", "competitor"),
        "payer_mix":        g("payer_mix"),
        "affiliations":     g("affiliations", "facilities"),
        "list_name":        list_name,
        "pulled_at":        _now(),
    }


# ========================== BROWSER MODE ======================================
def browser_export(url, out):
    """Log into AcuityMD (persisting session) and download an export CSV.

    First run: complete SSO/MFA in the headed browser; the session is saved to
    ~/.acuitymd_state.json and reused next time.
    """
    from playwright.sync_api import sync_playwright  # lazy import

    state_file = os.path.expanduser("~/.acuitymd_state.json")
    has_state = os.path.exists(state_file)
    email = os.environ.get("ACUITYMD_EMAIL")
    password = os.environ.get("ACUITYMD_PASSWORD")

    with sync_playwright() as pw:
        # Headed on first login so the user can clear SSO/MFA; headless after.
        browser = pw.chromium.launch(headless=has_state)
        ctx = browser.new_context(
            storage_state=state_file if has_state else None,
            accept_downloads=True,
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # If redirected to a login form (no valid session), attempt/assist login.
        if "login" in page.url or page.query_selector("input[type=password]"):
            if email and page.query_selector("input[type=email], input[name=email]"):
                page.fill("input[type=email], input[name=email]", email)
            if password and page.query_selector("input[type=password]"):
                page.fill("input[type=password]", password)
            print("Complete any SSO/MFA in the browser window, then return here...",
                  file=sys.stderr)
            page.wait_for_url(lambda u: "login" not in u, timeout=180_000)
            ctx.storage_state(path=state_file)  # persist for next time

        # Trigger the list export. Selectors change over time — adjust as needed.
        with page.expect_download(timeout=120_000) as dl_info:
            btn = page.get_by_role("button", name="Export")
            btn.click()
        download = dl_info.value
        download.save_as(out)
        ctx.storage_state(path=state_file)
        browser.close()
    print(f"Downloaded export to {out}", file=sys.stderr)
    return out


# ============================== CSV I/O =======================================
def write_csv(records, out):
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for rec in records:
            w.writerow({k: rec.get(k) for k in COLUMNS})
    print(f"Wrote {len(records)} rows to {out}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description="AcuityMD client")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--api", action="store_true", help="use the AcuityMD API")
    mode.add_argument("--browser", action="store_true", help="Playwright fallback")
    p.add_argument("cmd", choices=["targets", "export", "providers", "accounts"])
    p.add_argument("--territory", default=os.environ.get("ACUITYMD_TERRITORY"))
    p.add_argument("--procedure", help="procedure group filter")
    p.add_argument("--url", help="saved-list URL (browser mode)")
    p.add_argument("--out", default="acuitymd_targets.csv")
    p.add_argument("--raw", action="store_true", help="print raw JSON, skip normalize")
    args = p.parse_args()

    if args.browser:
        if not args.url:
            sys.exit("--browser requires --url (the AcuityMD saved-list page)")
        browser_export(args.url, args.out)
        return

    # API mode
    resource = "providers" if args.cmd in ("targets", "providers") else "accounts"
    params = {}
    if args.territory:
        params["territory"] = args.territory
    if args.procedure:
        params["procedure_group"] = args.procedure
    raw = api_pull(resource, params)
    if args.raw:
        print(json.dumps(raw, indent=2, default=str))
        return
    records = [normalize(r, list_name=args.territory or "") for r in raw]
    write_csv(records, args.out)


if __name__ == "__main__":
    main()
