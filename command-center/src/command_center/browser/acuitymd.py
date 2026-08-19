"""AcuityMD navigator.

AcuityMD has no public API on the plan tier this tool assumes, so we pull
targets through the logged-in web app. Exact selectors change over time and per
account, so they are **config-driven** (see ``config/settings.example.yaml`` ->
``acuitymd``). Two extraction strategies are supported:

  * ``export``  — click AcuityMD's own "Export" control and capture the CSV
                  download (preferred — you get AcuityMD's clean data).
  * ``scrape``  — read the visible results table into rows (fallback when a
                  view has no export button).

This module intentionally does the minimum: authenticate (via the shared
session), navigate to a saved view/URL, and get data out to a CSV the ingest
layer already understands.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .session import browser_session, ensure_logged_in

APP_URL = "https://app.acuitymd.com"


def pull_targets_export(
    view_url: str,
    out_csv: str | Path,
    export_selector: str = "text=Export",
    logged_in_selector: str = "nav",
    headless: bool = False,
    config: dict | None = None,
) -> str:
    """Open a saved AcuityMD view and capture its CSV export to ``out_csv``.

    ``view_url`` is the URL of a saved target list / market view in AcuityMD.
    """
    config = config or {}
    export_selector = config.get("export_selector", export_selector)
    logged_in_selector = config.get("logged_in_selector", logged_in_selector)
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with browser_session("acuitymd", headless=headless) as page:
        if not ensure_logged_in(page, APP_URL, logged_in_selector):
            raise RuntimeError(
                "Not logged into AcuityMD. Re-run with headless=False and sign "
                "in when the window appears; the session will be remembered."
            )
        page.goto(view_url, wait_until="networkidle")
        with page.expect_download() as dl_info:
            page.click(export_selector)
        download = dl_info.value
        download.save_as(str(out_csv))
    return str(out_csv)


def pull_targets_scrape(
    view_url: str,
    out_csv: str | Path,
    table_selector: str = "table",
    logged_in_selector: str = "nav",
    headless: bool = False,
    config: dict | None = None,
) -> str:
    """Fallback: read the visible results table into ``out_csv``.

    Extracts header cells + row cells from the first matching table. Good enough
    to feed the scoring layer when a view has no export.
    """
    config = config or {}
    table_selector = config.get("table_selector", table_selector)
    logged_in_selector = config.get("logged_in_selector", logged_in_selector)
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with browser_session("acuitymd", headless=headless) as page:
        if not ensure_logged_in(page, APP_URL, logged_in_selector):
            raise RuntimeError("Not logged into AcuityMD — see pull_targets_export docstring.")
        page.goto(view_url, wait_until="networkidle")
        page.wait_for_selector(table_selector)
        rows = page.eval_on_selector(
            table_selector,
            """(table) => {
                const headers = [...table.querySelectorAll('thead th')].map(th => th.innerText.trim());
                const body = [...table.querySelectorAll('tbody tr')].map(tr =>
                    [...tr.querySelectorAll('td')].map(td => td.innerText.trim()));
                return {headers, body};
            }""",
        )

    headers = rows.get("headers") or []
    body = rows.get("body") or []
    if not headers and body:
        headers = [f"col{i}" for i in range(len(body[0]))]
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(body)
    return str(out_csv)
