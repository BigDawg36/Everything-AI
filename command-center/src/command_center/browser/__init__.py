"""Browser-automation layer (optional — requires Playwright).

This is how the command center "logs into" AcuityMD and Power BI **without ever
storing your password**:

  1. ``session.py`` opens a real Chromium window using a *persistent* profile
     directory. The first time, YOU log in (SSO, MFA, everything). The session
     cookies are saved into that profile on disk.
  2. On later runs the same profile is reused, so you're already logged in and
     the navigators can drive the pages headlessly.

Install with::

    pip install playwright
    # Chromium is already present in this environment via PLAYWRIGHT_BROWSERS_PATH;
    # elsewhere run:  playwright install chromium

Nothing in this package types or persists credentials. If a login page appears
during an automated run, the tools stop and ask you to log in interactively.
"""
