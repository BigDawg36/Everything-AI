"""Sales Command Center.

An AcuityMD + Power BI sales-operations toolkit for medical-device sales teams.

The package is split so the *analysis / reporting / site* layer runs with only
the Python standard library plus Jinja2 (no browser, no cloud creds), while the
*browser* layer (Playwright) is an optional install used to pull data out of
AcuityMD and Power BI through a browser session the user logs into themselves.

Design principle: **the agent never stores your passwords.** You log in once in
a real browser window; the session is persisted locally and reused.
"""

__version__ = "0.1.0"
