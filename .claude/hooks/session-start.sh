#!/bin/bash
set -euo pipefail

# Only needed for Claude Code on the web (remote) sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  # Prefer installing via PyPI (pip resolves against the package index over
  # HTTPS) rather than piping the vendor's installer script into a shell.
  if command -v python3 >/dev/null 2>&1; then
    python3 -m pip install --user --quiet uv
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
fi

# Pinned to the immutable commit for the v2.11.2 release tag (not the tag
# name itself, which is mutable) for reproducibility and integrity.
# Bump deliberately when upgrading: git ls-remote --tags <repo> <new-tag>
uv tool install --quiet "git+https://github.com/NVIDIA/skillspector.git@69dcdfb74487d361ba4c811d088cfdea2ff3a9dc"

echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
