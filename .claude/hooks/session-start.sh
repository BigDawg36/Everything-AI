#!/bin/bash
set -euo pipefail

# Only needed for Claude Code on the web (remote) sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  # Install via PyPI (pip resolves against the package index over HTTPS)
  # rather than piping a downloaded installer script into a shell.
  if ! command -v python3 >/dev/null 2>&1; then
    echo "session-start hook: python3/pip not found, cannot install uv" >&2
    exit 1
  fi
  python3 -m pip install --user --quiet uv
fi

# Pinned to the immutable commit for the v2.11.2 release tag (not the tag
# name itself, which is mutable) for reproducibility and integrity.
# Bump deliberately when upgrading: git ls-remote --tags <repo> <new-tag>
uv tool install --quiet "git+https://github.com/NVIDIA/skillspector.git@69dcdfb74487d361ba4c811d088cfdea2ff3a9dc"

echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
