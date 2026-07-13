#!/usr/bin/env bash
# Rebuild the Claude.ai chat-skills bundle from .claude/skills/.
# Chat-friendly = no executable scripts (.py/.js/.sh/.cjs/.ps1/.mjs) => runs as pure
# guidance in the Claude.ai sandbox. Everything else is Claude Code / machine-only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SK="$ROOT/.claude/skills"
OUT="$ROOT/chat-skills-bundle"
BUILD="$(mktemp -d)"
mkdir -p "$BUILD/skills" "$BUILD/zips"

chat=(); excluded=()
for d in "$SK"/*/; do
  name="$(basename "$d")"
  if [ -n "$(find "$d" -type f \( -name '*.py' -o -name '*.js' -o -name '*.sh' \
        -o -name '*.cjs' -o -name '*.ps1' -o -name '*.mjs' \) -print -quit)" ]; then
    excluded+=("$name")
  else
    chat+=("$name")
    cp -R "$d" "$BUILD/skills/$name"
    (cd "$BUILD/skills" && zip -qr "$BUILD/zips/$name.zip" "$name")
  fi
done

cp "$OUT/README.md" "$OUT/MANIFEST.md" "$OUT/EXCLUDED.md" "$BUILD/" 2>/dev/null || true
mkdir -p "$OUT/dist"
rm -f "$OUT/dist/everything-ai-chat-skills.zip"
(cd "$BUILD" && zip -qr "$OUT/dist/everything-ai-chat-skills.zip" .)
echo "chat-friendly: ${#chat[@]} | excluded: ${#excluded[@]}"
echo "bundle -> $OUT/dist/everything-ai-chat-skills.zip"
rm -rf "$BUILD"
