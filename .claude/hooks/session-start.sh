#!/bin/bash
set -euo pipefail

# Only needed for Claude Code on the web (remote) sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Pinned to a release tag for reproducibility; bump deliberately when upgrading.
uv tool install --quiet "git+https://github.com/NVIDIA/skillspector.git@v2.11.2"

echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
