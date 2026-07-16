# Everything-AI

A curated mega-collection of **Claude Code skills** — 274 prompt/instruction packages vendored from ~10 public collections into one flat tree, plus a packaging pipeline that repackages the chat-compatible subset for the Claude.ai app.

There is no application code here. The skills are the product.

## What's inside

```
.claude/skills/        274 skills, one directory each (SKILL.md + support files)
.claude/agents/        5 sales research subagents used by the /sales suite
chat-skills-bundle/    build script + generated manifests + dist zip for Claude.ai chat
scripts/               validate-skills.sh (frontmatter/name validation, also runs in CI)
```

Source families: marketing (Corey Haines, 47), context-engineering-kit (67), Trail of Bits security (~75), PicsArt gen-AI (20), claude-mem (18), superpowers (14), AI Sales Team (13 + 5 agents), caveman (7), Arcads (5), and several singles. Full map with upstream links and licenses: `ATTRIBUTIONS.md`.

## Using the skills

- **Claude Code:** run Claude Code in this repo (or copy `.claude/skills/` into `~/.claude/`) — skills auto-discover and trigger on their frontmatter `description:`.
- **Claude.ai chat:** upload per-skill zips from `chat-skills-bundle/dist/everything-ai-chat-skills.zip` → `zips/`. See `chat-skills-bundle/README.md`; machine-only skills are listed in its generated `EXCLUDED.md`.

## Maintaining

```bash
bash scripts/validate-skills.sh              # frontmatter/name checks (CI runs this too)
bash chat-skills-bundle/build-bundle.sh      # rebuild bundle + regenerate MANIFEST/EXCLUDED
```

Rebuild the bundle after any skill change. Skill `description:` frontmatter is load-bearing routing logic — edit deliberately.

## Documentation

- `PROJECT.md` — architecture, source-family map, design decisions, and the traps that aren't obvious from the tree.
- `GAPS.md` — known weaknesses, ordered by severity, each with a scoped fix.
- `CLAUDE.md` — operational instructions loaded by Claude Code sessions.
- `ATTRIBUTIONS.md` — upstream sources and licenses.
- `SCRIPT-AUDIT.md` — mechanical risk inventory of the 218 vendored scripts.
