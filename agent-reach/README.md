# agent-reach CLI setup

[agent-reach](https://github.com/Panniantong/agent-reach) gives an AI agent
(Claude Code, Cursor, OpenClaw, ...) stable **internet access** — reading and
searching content across the web without each agent having to wrestle with
platform APIs, auth, and scraping.

It works as a *capability layer*: for each source ("channel") it selects,
installs, and health-checks a backend for you, and automatically falls back to
the next backend if the primary one fails. As its own tagline puts it — "we
select it, install it, and verify it for you."

## Channels

| Channel | Backend | Config needed |
|---|---|---|
| Web pages | Jina Reader | none (zero-config) |
| YouTube | yt-dlp subtitle extraction | none |
| RSS | feedparser | none |
| GitHub | `gh` CLI | none |
| Twitter/X, Reddit, Bilibili, Xiaohongshu | varies; OpenCLI fallback | login via OpenCLI |

Each channel holds a *prioritized* list of backends. If the first fails, the
next is tried without any manual intervention.

### OpenCLI

**OpenCLI** is a browser-automation backend that reuses your existing Chrome
login session. It's the fallback for sources that require authentication
(Twitter/X, Reddit, Instagram, Xiaohongshu). Because it drives the browser
you're already logged into, you never have to export or hand over cookies.

## Privacy

- Python 3.10+ is the only hard requirement.
- Zero-config channels need **no API keys**.
- Any login credentials/cookies/tokens are stored **locally** under
  `~/.agent-reach/` and are **never uploaded**.

## Quick start

Run on your own machine (macOS/Linux). Either run the helper script:

```bash
./setup.sh            # full install: core infra + OpenCLI
./setup.sh --core-only  # skip the OpenCLI channel
```

...or follow the steps manually:

```bash
# 1. Install the CLI (a venv avoids macOS PEP 668 "externally-managed" errors)
python3 -m venv ~/.agent-reach-venv && source ~/.agent-reach-venv/bin/activate
pip install https://github.com/Panniantong/agent-reach/archive/main.zip

# 2. Core infra — preview with --safe first, then the real run
agent-reach install --env=auto --safe   # shows changes, applies nothing
agent-reach install --env=auto           # applies them

# 3. Health check — status + active backend per channel
agent-reach doctor

# 4. Best desktop channel: OpenCLI (reuses your Chrome logins, no cookies to hand over)
agent-reach install --env=auto --channels=opencli
#    then add the Chrome extension it points you to, and run:
opencli doctor
```

Each new shell needs the venv activated before `agent-reach` is on `PATH`:

```bash
source ~/.agent-reach-venv/bin/activate
```

## Command reference

| Command | Purpose |
|---|---|
| `agent-reach install --env=auto` | One-command setup; auto-detects the environment and configures channels |
| `agent-reach install ... --safe` | Preview mode — report what *would* change without touching anything |
| `agent-reach install ... --channels=opencli` | Install a specific channel (here, the OpenCLI browser bridge) |
| `agent-reach doctor` | Diagnose every channel's status and the backend currently in use |
| `agent-reach uninstall` | Remove all config, tokens, and skill files |
| `opencli doctor` | Verify the OpenCLI browser bridge after adding the Chrome extension |

## Notes on running this in a sandbox / CI

This setup is meant to run interactively on a developer machine:

- The `pip install` pulls the package from a GitHub archive URL. Locked-down
  environments (including some CI runners and this repo's remote execution
  sandbox) restrict outbound network access and will return `403` for that
  download — install from a machine with normal internet access instead.
- The **OpenCLI** step needs a real, logged-in Chrome plus a browser
  extension, so it cannot be completed headlessly.
- `--safe` is your friend: always preview a core install before applying it.
