# CLAUDE.md — Everything-AI

Operational instructions for Claude Code sessions in this repo. Architecture and history: `PROJECT.md`. Known issues and fixes: `GAPS.md`.

## What this repo is

A collection of **274 Claude Code skills** under `.claude/skills/` (Markdown, one directory per skill), 5 sales subagents under `.claude/agents/`, and a packaging pipeline in `chat-skills-bundle/` that zips the 247 script-free skills for upload to Claude.ai chat. **There is no application code.** The skills are the product.

## Commands

There is no build/test/lint toolchain. The only commands that matter:

```bash
# Rebuild the Claude.ai chat bundle (regenerates dist/everything-ai-chat-skills.zip)
bash chat-skills-bundle/build-bundle.sh
# Prints: "chat-friendly: N | excluded: M" — verify N+M == number of skill dirs

# Count skills / sanity-check the tree
ls .claude/skills | grep -v -E '^(LICENSE|README.md)$' | wc -l   # 274 as of 2026-07

# Find skills with missing frontmatter (known offenders: the 14 sales-* skills)
grep -L '^---' .claude/skills/*/SKILL.md
```

Run `build-bundle.sh` after **any** change that adds/removes a skill or adds/removes a script file inside a skill — script presence flips a skill's chat/machine classification.

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
  Optional fields seen in the wild: `allowed-tools:` (Trail of Bits skills), `metadata: {version: x.y.z}` (marketing skills), `argument-hint:` (slash-command-style skills). For NEW skills, use the minimal `name` + `description` form; `description` is the routing logic — spend your effort there.
- **Support files** go in subdirs by role: `references/` (docs the skill reads), `resources/` (report templates/criteria), `templates/` (output templates), `scripts/` (runnables), `evals/evals.json` (test prompts + assertions), `workflows/` (multi-phase procedures).
- **Skills are vendored snapshots** from ~10 upstream collections (see the table in `PROJECT.md`). Preserve each family's internal style when editing; don't "normalize" vendored skills.
- Commit messages follow the existing history style: imperative, plain, e.g. `Add 18 claude-mem skills to .claude/skills`, `Refresh chat-skills-bundle: 247 skills`.

## Gotchas

- **`.claude/skills/README.md` is stale** — it describes only the original 47 marketing skills. The directory holds 274 from many sources. Don't treat it as an inventory.
- **`chat-skills-bundle/skills/` and `zips/` don't exist on disk.** The bundle README's tree describes the *inside of the zip*; the build assembles those dirs in a temp dir. Only `dist/` is real.
- **`MANIFEST.md` and `EXCLUDED.md` are hand-maintained**, not generated — `build-bundle.sh` copies them verbatim into the zip. If you change skill counts, update both files AND the counts in `chat-skills-bundle/README.md` (which currently says "25" excluded; correct number is 27 — see GAPS.md #3).
- **The 14 sales skills (`sales`, `sales-*`) have NO frontmatter** — they start with `#` headings. Their auto-discovery is unreliable until GAPS.md #1 is fixed. Don't copy their format for new skills.
- **`obsidian-second-brain/CLAUDE.md` is NOT this repo's CLAUDE.md** — it's vendored upstream source for that one skill. Ignore it unless working inside that skill. Never run its `install.sh`/`update.sh` casually: they symlink into the user's `~/.claude/`.
- **Chat-friendliness is judged only by file extension.** Adding even a tiny `.sh` helper to a skill silently removes it from the 247-skill chat bundle on next build. Check the build output counts.
- **The remote has no `main` branch.** Default branch is a `claude/…` working branch. Check `git branch -a` before assuming.
- **Near-duplicate skills exist by design** (`brainstorm`/`brainstorming`, two TDD skills, `commit`/`caveman-commit`). If asked to "fix duplication", disambiguate their `description:` fields — do not delete skills (GAPS.md #6).

## Rules

- **Never edit `chat-skills-bundle/dist/everything-ai-chat-skills.zip` by hand** — it is generated. Rebuild with `build-bundle.sh`.
- **Never delete `.claude/skills/LICENSE` or `.claude/skills/README.md`** — they are the MIT attribution for the marketing skills.
- **Treat `name:`/`description:` frontmatter as load-bearing.** Renaming a skill directory or rewriting a description changes routing behavior across every session using this collection. Do it deliberately, one skill at a time.
- **Editing a skill body is safe** — skills are isolated; below-frontmatter changes cannot break other skills.
- **Don't restructure the flat namespace** (no moving skills into subdirectories) — Claude Code discovery expects `.claude/skills/<name>/SKILL.md`.
- **Skill scripts run with user permissions.** Before invoking a vendored script you haven't read, skim it — 218 scripts across 27 skills came in unaudited (GAPS.md #9).

## Pointers

- `PROJECT.md` — architecture, source-family map, data flow, design decisions, and the traps that aren't obvious from the tree.
- `GAPS.md` — the 12 known weaknesses, ordered by severity, each with a small scoped fix; start there when asked to "improve the repo".
