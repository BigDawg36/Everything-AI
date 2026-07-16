# CLAUDE.md — Everything-AI

Operational instructions for Claude Code sessions in this repo. Architecture and history: `PROJECT.md`. Known issues and fixes: `GAPS.md`.

## What this repo is

A collection of **274 Claude Code skills** under `.claude/skills/` (Markdown, one directory per skill), 5 sales subagents under `.claude/agents/`, and a packaging pipeline in `chat-skills-bundle/` that zips the chat-compatible skills (currently 238) for upload to Claude.ai chat. **There is no application code.** The skills are the product.

## Commands

There is no build/test/lint toolchain beyond these:

```bash
# Validate every skill (frontmatter present, name==dirname, names unique). CI runs this too.
bash scripts/validate-skills.sh

# Rebuild the Claude.ai chat bundle (regenerates dist/ zip + MANIFEST.md + EXCLUDED.md)
bash chat-skills-bundle/build-bundle.sh
# Prints: "chat-friendly: N | excluded: M (scripts: X, forced: Y)" — verify N+M == skill count

# Count skills / sanity-check the tree
ls .claude/skills | grep -v -E '^(LICENSE|README.md)$' | wc -l   # 274 as of 2026-07
```

Run **both** commands after any change that adds/removes a skill, touches frontmatter, or adds/removes a script file inside a skill — script presence flips a skill's chat/machine classification.

## Conventions

- **One directory per skill** directly under `.claude/skills/` — no nesting, no per-source subfolders. Directory name == skill name, kebab-case.
- **`SKILL.md` is mandatory** and must start with YAML frontmatter:
  ```yaml
  ---
  name: <same-as-directory-name>
  description: >-
    When to trigger, written as user-phrasing matches ("Use when the user says X, Y, Z").
  ---
  ```
  Optional fields seen in the wild: `allowed-tools:` (Trail of Bits skills), `metadata: {version: x.y.z}` (marketing skills), `argument-hint:` (slash-command-style skills). For NEW skills, use the minimal `name` + `description` form; `description` is the routing logic — spend your effort there. `scripts/validate-skills.sh` enforces the invariants.
- **Support files** go in subdirs by role: `references/` (docs the skill reads), `resources/` (report templates/criteria), `templates/` (output templates), `scripts/` (runnables), `evals/evals.json` (test prompts + assertions), `workflows/` (multi-phase procedures).
- **Skills are vendored snapshots** from ~10 upstream collections (map: `ATTRIBUTIONS.md`, table in `PROJECT.md`). Preserve each family's internal style when editing; don't "normalize" vendored skills. When importing a new collection, record its upstream URL + license in `ATTRIBUTIONS.md` at import time.
- Commit messages follow the existing history style: imperative, plain, e.g. `Add 18 claude-mem skills to .claude/skills`, `Refresh chat-skills-bundle: 247 skills`.

## Gotchas

- **`chat-skills-bundle/skills/` and `zips/` don't exist on disk.** The bundle README's tree describes the *inside of the zip*; the build assembles those dirs in a temp dir. Only `dist/` is real.
- **`MANIFEST.md` and `EXCLUDED.md` are GENERATED** by `build-bundle.sh` — never hand-edit them; rebuild instead. Avoid hardcoding skill counts in prose anywhere; they drift.
- **Chat-friendliness = extension heuristic + overrides.** A skill with any `.py/.js/.sh/.cjs/.ps1/.mjs` file is machine-only unless listed in `chat-skills-bundle/force-include.txt`; a script-free skill can still be excluded via `force-exclude.txt` (9 CLI/MCP-bound skills are). Adding even a tiny `.sh` helper silently flips classification on next build — check the printed counts.
- **`obsidian-second-brain/UPSTREAM-CLAUDE.md` is NOT this repo's CLAUDE.md** — it's the vendored upstream repo's instructions (renamed from `CLAUDE.md` to avoid confusion). Never run that skill's `install.sh`/`update.sh` casually: they symlink into the user's `~/.claude/`.
- **The remote has no `main` branch.** Default branch is a `claude/…` working branch. Check `git branch -a` before assuming.
- **Near-duplicate skills exist by design** (`brainstorm`/`brainstorming`, two TDD skills, `commit`/`caveman-commit`). Their descriptions were disambiguated (secondary skill defers to primary); if adding more overlapping skills, follow that pattern — do not delete skills (GAPS.md #6).

## Rules

- **Never edit generated files by hand**: `chat-skills-bundle/dist/everything-ai-chat-skills.zip`, `chat-skills-bundle/MANIFEST.md`, `chat-skills-bundle/EXCLUDED.md`. Rebuild with `build-bundle.sh`.
- **Never delete license/attribution files**: `.claude/skills/LICENSE`, `.claude/skills/obsidian-second-brain/LICENSE`, `ATTRIBUTIONS.md`.
- **Treat `name:`/`description:` frontmatter as load-bearing.** Renaming a skill directory or rewriting a description changes routing behavior across every session using this collection. Do it deliberately, one skill at a time, and run `validate-skills.sh` after.
- **Editing a skill body is safe** — skills are isolated; below-frontmatter changes cannot break other skills.
- **Don't restructure the flat namespace** (no moving skills into subdirectories) — Claude Code discovery expects `.claude/skills/<name>/SKILL.md`.
- **Skill scripts run with user permissions.** Check `SCRIPT-AUDIT.md` (mechanical flag inventory of all 218 vendored scripts) before invoking one you haven't read.

## Pointers

- `PROJECT.md` — architecture, source-family map, data flow, design decisions, and the traps that aren't obvious from the tree.
- `GAPS.md` — the known weaknesses, ordered by severity, each with a scoped fix and a current status line; start there when asked to "improve the repo".
- `ATTRIBUTIONS.md` — upstream source and license per skill family; update it when importing.
- `SCRIPT-AUDIT.md` — per-script risk flags (network / home-writes / exec / curl-pipe-sh).
