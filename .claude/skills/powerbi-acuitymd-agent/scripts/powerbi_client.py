#!/usr/bin/env python3
"""Power BI REST API client for the sales agent.

Authenticates with Microsoft Entra ID (service principal *or* device-code) and
runs DAX queries against a Power BI dataset (semantic model). Also lists
workspaces/datasets/reports for discovery, and can kick off a report export.

Secrets are read from the environment only (never passed as CLI args). See
references/powerbi-connection.md and .env.example.

Examples
--------
  # verify auth + list datasets in the configured workspace
  python powerbi_client.py check
  python powerbi_client.py list-datasets

  # run a DAX query (returns JSON rows); reads DAX from --file or stdin
  python powerbi_client.py query --file query.dax
  echo 'EVALUATE ROW("n", [Revenue])' | python powerbi_client.py query

Requires: msal, requests  (pip install -r requirements.txt)
"""
import argparse
import json
import os
import sys
import time

try:
    import msal
    import requests
except ImportError:
    sys.exit("Missing deps. Run: pip install -r requirements.txt")

AUTHORITY = "https://login.microsoftonline.com/{tenant}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
API = "https://api.powerbi.com/v1.0/myorg"
TOKEN_CACHE = os.path.expanduser("~/.pbi_token_cache.json")


def _env(name, required=True):
    val = os.environ.get(name)
    if required and not val:
        sys.exit(f"Missing required env var: {name} (see .env.example)")
    return val


def get_token():
    """Acquire a bearer token. Service principal if a secret is set, else device code."""
    tenant = _env("PBI_TENANT_ID")
    client_id = _env("PBI_CLIENT_ID")
    secret = os.environ.get("PBI_CLIENT_SECRET")
    authority = AUTHORITY.format(tenant=tenant)

    if secret:  # Mode A: service principal / client credentials
        app = msal.ConfidentialClientApplication(
            client_id, authority=authority, client_credential=secret
        )
        result = app.acquire_token_for_client(scopes=SCOPE)
    else:  # Mode B: device code (interactive, MFA-friendly)
        cache = msal.SerializableTokenCache()
        if os.path.exists(TOKEN_CACHE):
            cache.deserialize(open(TOKEN_CACHE).read())
        app = msal.PublicClientApplication(
            client_id, authority=authority, token_cache=cache
        )
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(SCOPE, account=accounts[0])
        if not result:
            flow = app.initiate_device_flow(scopes=SCOPE)
            if "user_code" not in flow:
                sys.exit("Failed to start device flow: " + json.dumps(flow))
            print(flow["message"], file=sys.stderr)  # URL + code for the user
            result = app.acquire_token_by_device_flow(flow)
        if cache.has_state_changed:
            with open(TOKEN_CACHE, "w") as fh:
                fh.write(cache.serialize())

    if "access_token" not in result:
        sys.exit("Auth failed: " + result.get("error_description", json.dumps(result)))
    return result["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _group_prefix():
    ws = os.environ.get("PBI_WORKSPACE_ID")
    return f"/groups/{ws}" if ws else ""


def list_datasets(token):
    r = requests.get(f"{API}{_group_prefix()}/datasets", headers=_headers(token))
    r.raise_for_status()
    return r.json().get("value", [])


def list_reports(token):
    r = requests.get(f"{API}{_group_prefix()}/reports", headers=_headers(token))
    r.raise_for_status()
    return r.json().get("value", [])


def list_workspaces(token):
    r = requests.get(f"{API}/groups", headers=_headers(token))
    r.raise_for_status()
    return r.json().get("value", [])


def execute_dax(token, dax, dataset_id=None):
    """Run a DAX EVALUATE query and return a list of row dicts."""
    dataset_id = dataset_id or _env("PBI_DATASET_ID")
    body = {
        "queries": [{"query": dax}],
        "serializerSettings": {"includeNulls": True},
    }
    r = requests.post(
        f"{API}/datasets/{dataset_id}/executeQueries",
        headers=_headers(token),
        json=body,
    )
    if r.status_code != 200:
        sys.exit(f"executeQueries {r.status_code}: {r.text}")
    results = r.json()["results"][0]["tables"][0]["rows"]
    return results


def export_report(token, report_id, fmt="PDF", out="report_export"):
    """Start ExportTo, poll to completion, download the file."""
    prefix = f"{API}{_group_prefix()}/reports/{report_id}"
    r = requests.post(f"{prefix}/ExportTo", headers=_headers(token), json={"format": fmt})
    r.raise_for_status()
    export_id = r.json()["id"]
    while True:
        s = requests.get(f"{prefix}/exports/{export_id}", headers=_headers(token))
        s.raise_for_status()
        status = s.json()["status"]
        if status == "Succeeded":
            break
        if status == "Failed":
            sys.exit("Export failed: " + s.text)
        time.sleep(3)
    f = requests.get(f"{prefix}/exports/{export_id}/file", headers=_headers(token))
    f.raise_for_status()
    path = f"{out}.{fmt.lower()}"
    with open(path, "wb") as fh:
        fh.write(f.content)
    return path


def main():
    p = argparse.ArgumentParser(description="Power BI REST client")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("list-workspaces")
    sub.add_parser("list-datasets")
    sub.add_parser("list-reports")
    q = sub.add_parser("query")
    q.add_argument("--file", help="path to a .dax file; omit to read stdin")
    q.add_argument("--dataset", help="override PBI_DATASET_ID")
    e = sub.add_parser("export")
    e.add_argument("--report", required=True)
    e.add_argument("--format", default="PDF")
    e.add_argument("--out", default="report_export")
    args = p.parse_args()

    token = get_token()

    if args.cmd == "check":
        print("Auth OK. Token acquired.", file=sys.stderr)
        ds = list_datasets(token)
        print(f"{len(ds)} dataset(s) visible in the configured scope.")
    elif args.cmd == "list-workspaces":
        print(json.dumps(list_workspaces(token), indent=2))
    elif args.cmd == "list-datasets":
        print(json.dumps(list_datasets(token), indent=2))
    elif args.cmd == "list-reports":
        print(json.dumps(list_reports(token), indent=2))
    elif args.cmd == "query":
        dax = open(args.file).read() if args.file else sys.stdin.read()
        if not dax.strip():
            sys.exit("No DAX provided.")
        rows = execute_dax(token, dax, dataset_id=args.dataset)
        print(json.dumps(rows, indent=2, default=str))
    elif args.cmd == "export":
        path = export_report(token, args.report, args.format, args.out)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
