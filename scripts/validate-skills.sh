#!/usr/bin/env bash
# Validate every skill under .claude/skills/:
#   1. each skill directory contains a SKILL.md
#   2. SKILL.md starts with a YAML frontmatter block (--- ... ---)
#   3. frontmatter contains name: and description:
#   4. name: matches the directory name
#   5. no duplicate name: values across the collection
# Exits non-zero and lists every failure. Run from the repo root.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SK="$ROOT/.claude/skills"
fail=0
declare -A seen

for d in "$SK"/*/; do
  name="$(basename "$d")"
  f="$d/SKILL.md"

  if [ ! -f "$f" ]; then
    echo "FAIL [$name] missing SKILL.md"; fail=1; continue
  fi
  if [ "$(head -1 "$f")" != "---" ]; then
    echo "FAIL [$name] SKILL.md does not start with YAML frontmatter"; fail=1; continue
  fi
  # frontmatter = lines between the first two '---' markers
  fm="$(awk 'NR==1 && $0=="---"{infm=1; next} infm && $0=="---"{exit} infm{print}' "$f")"
  if [ -z "$fm" ]; then
    echo "FAIL [$name] frontmatter block is empty or unterminated"; fail=1; continue
  fi
  fmname="$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p' | head -1)"
  if [ -z "$fmname" ]; then
    echo "FAIL [$name] frontmatter has no name: field"; fail=1
  elif [ "$fmname" != "$name" ]; then
    echo "FAIL [$name] frontmatter name '$fmname' != directory name"; fail=1
  fi
  if ! printf '%s\n' "$fm" | grep -q '^description:'; then
    echo "FAIL [$name] frontmatter has no description: field"; fail=1
  fi
  if [ -n "$fmname" ]; then
    if [ -n "${seen[$fmname]:-}" ]; then
      echo "FAIL [$name] duplicate skill name '$fmname' (also in ${seen[$fmname]})"; fail=1
    else
      seen[$fmname]="$name"
    fi
  fi
done

total="$(find "$SK" -mindepth 1 -maxdepth 1 -type d | wc -l)"
if [ "$fail" -eq 0 ]; then
  echo "OK: $total skills validated"
else
  echo "Validation failed (see FAIL lines above; $total skills scanned)"
fi
exit "$fail"
