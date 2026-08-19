"""Persistent, user-authenticated browser sessions.

The whole security model of the command center lives here: we use a Playwright
*persistent context* keyed to a profile directory on disk. Credentials are
never handled by this code — the human logs in once in a visible window and the
browser stores its own session cookies in the profile.
"""
from __future__ import annotations

import os
from pathlib import Path
from contextlib import contextmanager

# Where browser profiles live. Each service gets its own profile so sessions
# never bleed together. This directory is gitignored.
PROFILE_ROOT = Path(os.environ.get("CC_PROFILE_ROOT", Path(__file__).resolve().parents[3] / "data" / "profiles"))


def _require_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return sync_playwright
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Playwright is not installed. Run `pip install playwright` (Chromium "
            "is already available in this environment). The browser layer is "
            "optional; the analysis/report/site layers work without it."
        ) from exc


@contextmanager
def browser_session(service: str, headless: bool = False, chromium_path: str | None = None):
    """Yield a logged-in Playwright page for ``service`` (e.g. 'acuitymd').

    First run: pass ``headless=False`` and log in when the window appears.
    Later runs can use ``headless=True`` because the profile keeps you signed in.

    Usage::

        with browser_session("acuitymd") as page:
            page.goto("https://app.acuitymd.com/...")
            ...
    """
    sync_playwright = _require_playwright()
    profile_dir = PROFILE_ROOT / service
    profile_dir.mkdir(parents=True, exist_ok=True)

    launch_kwargs = {
        "user_data_dir": str(profile_dir),
        "headless": headless,
        "viewport": {"width": 1440, "height": 900},
        "accept_downloads": True,
    }
    # Reuse the environment's pre-installed Chromium when a path is given/known.
    exe = chromium_path or os.environ.get("CC_CHROMIUM_PATH")
    if exe:
        launch_kwargs["executable_path"] = exe

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(**launch_kwargs)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            yield page
        finally:
            ctx.close()


def ensure_logged_in(page, login_url: str, logged_in_selector: str, timeout_ms: int = 180_000) -> bool:
    """Navigate to ``login_url`` and wait until ``logged_in_selector`` appears.

    If the user needs to authenticate, the visible window gives them up to
    ``timeout_ms`` (default 3 min) to complete SSO/MFA. Returns True once the
    logged-in marker is present. This function never enters credentials.
    """
    page.goto(login_url, wait_until="domcontentloaded")
    try:
        page.wait_for_selector(logged_in_selector, timeout=timeout_ms)
        return True
    except Exception:
        return False
