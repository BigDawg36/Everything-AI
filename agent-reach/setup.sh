#!/usr/bin/env bash
#
# setup.sh — install and health-check the agent-reach CLI.
#
# agent-reach gives an AI agent stable internet access (web pages, YouTube,
# RSS, GitHub, Twitter/X, Reddit, Bilibili, Xiaohongshu, ...) by selecting,
# installing, and health-checking a backend for each source ("channel") for
# you. Cookies and tokens stay local under ~/.agent-reach/ — nothing is
# uploaded.
#
# Run interactively on your own machine (macOS/Linux). The OpenCLI step and
# the `agent-reach doctor` checks talk to the network and, for OpenCLI, to a
# local Chrome — so this is not meant to run in a headless CI/sandbox.
#
# Usage:
#   ./setup.sh              # full install: core infra + OpenCLI channel
#   ./setup.sh --core-only  # core infra only, skip the OpenCLI channel
#   ./setup.sh --help
#
set -euo pipefail

VENV_DIR="${AGENT_REACH_VENV:-$HOME/.agent-reach-venv}"
PACKAGE_URL="https://github.com/Panniantong/agent-reach/archive/main.zip"
INSTALL_OPENCLI=1

for arg in "$@"; do
  case "$arg" in
    --core-only) INSTALL_OPENCLI=0 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg (try --help)" >&2
      exit 2
      ;;
  esac
done

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }

# 1. Install the CLI in a dedicated venv.
#    A venv sidesteps macOS PEP 668 ("externally-managed-environment") errors
#    and keeps agent-reach's dependencies isolated from system Python.
step "Installing agent-reach CLI into $VENV_DIR"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 (3.10+) is required but was not found on PATH." >&2
  exit 1
fi
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python3 -m pip install --upgrade pip >/dev/null
pip install "$PACKAGE_URL"

# 2. Core infrastructure — preview (--safe) first, then the real run.
#    --safe shows what would change without touching anything; drop it to apply.
step "Previewing core install (--safe, no changes made)"
agent-reach install --env=auto --safe

step "Applying core install"
agent-reach install --env=auto

# 3. Health check — reports each channel's status and which backend it uses.
step "Running health check"
agent-reach doctor

# 4. Best desktop channel: OpenCLI.
#    OpenCLI drives your existing Chrome session, so authenticated sources
#    (Twitter/X, Reddit, Instagram, Xiaohongshu, ...) work without you handing
#    over any cookies. It prints a Chrome extension to add; install that, then
#    verify with `opencli doctor`.
if [ "$INSTALL_OPENCLI" -eq 1 ]; then
  step "Installing the OpenCLI channel"
  agent-reach install --env=auto --channels=opencli
  cat <<'NOTE'

Next steps for OpenCLI (manual, one-time):
  1. Add the Chrome extension that the command above points you to.
  2. Verify the browser bridge:
       opencli doctor
NOTE
else
  step "Skipping OpenCLI channel (--core-only)"
fi

step "Done"
cat <<NOTE
agent-reach is installed in: $VENV_DIR

To use it in a new shell:
  source "$VENV_DIR/bin/activate"
  agent-reach doctor
NOTE
