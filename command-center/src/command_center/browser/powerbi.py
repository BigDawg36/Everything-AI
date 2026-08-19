"""Power BI navigator.

With web-login-only access (no REST API / service principal), the reliable way
to get numbers *out* of Power BI is to export a visual's underlying data from
the service UI. This module drives that: open a report, click a visual's
"Export data" (More options -> Export data), and capture the CSV.

For *building* reports we don't automate the service (it's a rich authoring
canvas that doesn't script well through a browser); instead the ``reports``
layer generates the DAX + model + layout you paste once in Power BI Desktop.
That division is deliberate: automate the repeatable data pull, hand-author the
report structure once.
"""
from __future__ import annotations

from pathlib import Path

from .session import browser_session, ensure_logged_in

APP_URL = "https://app.powerbi.com"


def export_visual_data(
    report_url: str,
    out_csv: str | Path,
    visual_more_options_selector: str,
    export_menu_selector: str = "text=Export data",
    logged_in_selector: str = "[aria-label='Power BI']",
    headless: bool = False,
    config: dict | None = None,
) -> str:
    """Export one visual's underlying data from a Power BI report to ``out_csv``.

    You provide the selector for the visual's "More options (...)" button
    (``visual_more_options_selector``) — hover a visual in the service, and its
    ``...`` menu is what opens Export data. Selectors are config-driven because
    Power BI's DOM is dynamic.
    """
    config = config or {}
    export_menu_selector = config.get("export_menu_selector", export_menu_selector)
    logged_in_selector = config.get("logged_in_selector", logged_in_selector)
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with browser_session("powerbi", headless=headless) as page:
        if not ensure_logged_in(page, APP_URL, logged_in_selector):
            raise RuntimeError(
                "Not logged into Power BI. Re-run with headless=False and sign "
                "in when the window appears; the session will be remembered."
            )
        page.goto(report_url, wait_until="networkidle")
        page.click(visual_more_options_selector)
        with page.expect_download() as dl_info:
            page.click(export_menu_selector)
            # Some tenants show a confirm dialog; click through if present.
            try:
                page.click("text=Export", timeout=5000)
            except Exception:
                pass
        download = dl_info.value
        download.save_as(str(out_csv))
    return str(out_csv)


def capture_embed_url(report_url: str, logged_in_selector: str = "[aria-label='Power BI']",
                      headless: bool = False) -> str:
    """Best-effort helper to open a report so you can grab its Publish-to-web /
    embed URL for the command-center site. Returns the current report URL.

    (Generating a true secure-embed token needs the REST API; with web login
    only, use the service's File > Embed report > Publish to web (public) and
    paste that iframe URL into the site config.)
    """
    with browser_session("powerbi", headless=headless) as page:
        ensure_logged_in(page, APP_URL, logged_in_selector)
        page.goto(report_url, wait_until="networkidle")
        return page.url
