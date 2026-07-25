# Security & credential handling

This agent touches sales data and two authenticated platforms. Treat everything
here as confidential business data.

## Credentials

- **Only** ever read secrets from environment variables or an untracked `.env`
  file. `scripts/*.py` read from the environment; they never take a secret as a
  command-line argument (args show up in shell history and `ps`).
- **Never** write a token, password, client secret, or API key into:
  a report, a template output, a committed file, a commit message, a PR body,
  or a chat message. If you need to show that a value is set, print whether it
  exists and its length — never the value.
- `.env` and all data exports are git-ignored (see the skill's `.gitignore`).
  Verify before committing: `git status` should never list `.env`, `*.csv`,
  `*.xlsx`, `command-center-data.json`, or `REP-*.md` unless the user explicitly
  wants a redacted sample committed.
- Prefer **service principal** (Power BI) and **API token** (AcuityMD) over
  storing a human's password. If a password is unavoidable (browser fallback),
  persist a **session state file** after an interactive login instead of keeping
  the password around.

## Data handling

- AcuityMD provider data is business-contact / commercial data, not patient PHI —
  but physician names, NPIs, and volumes are still sensitive. Don't paste rosters
  into external LLM tools, public artifacts, or third-party services.
- Keep territory integrity: a rep's export contains only their accounts. Don't
  co-mingle territories in a single shared file unless it's an intended roll-up.
- When publishing to the command-center site, push only the aggregated KPI JSON
  the site needs — not the raw account-level pull.

## Outward actions need confirmation

Pushing to the live command-center site, emailing a rep their report, or writing
back to AcuityMD/CRM are outward, hard-to-reverse actions. Confirm with the user
before doing them unless they've pre-authorized that exact action this session.
