# PROJECT.md — Everything-AI

*Knowledge-transfer overview. Written 2026-07-16 after a full audit of the repository. Companion documents: `CLAUDE.md` (operational instructions for AI agents) and `GAPS.md` (honest audit of known weaknesses).*

## What this is

**Everything-AI is not an application. It is a curated mega-collection of 274 Claude Code skills** — prompt/instruction packages in Markdown — aggregated from roughly ten public open-source skill collections into one repo, plus a small build pipeline that repackages the chat-compatible subset for upload to the Claude.ai web/desktop app.

It's for one user (the repo owner) who wants every useful Claude skill available in two places:

1. **Claude Code** — the entire `.claude/skills/` tree is auto-discovered when Claude Code runs anywhere in this repo (or when the tree is copied/symlinked into `~/.claude/`).
2. **Claude.ai chat** — via `chat-skills-bundle/`, which zips the 247 skills that need no local machine so they can be uploaded under *Settings → Capabilities → Skills*.

There is no server, no database, no package.json, no deployable binary. The "source code" is Markdown; the only build artifact is a zip file.

### Sibling repository

The session/workspace also contains **`-Keeping-Fable-5`**, a placeholder repo whose entire content is a one-line README: *"Prompt to keep Fable 5 when the $$$ goes up."* It holds no code and needs no architecture documentation; treat it as an idea stub, not a project.

## Tech stack (and why)

| Piece | What it is | Why it's here |
|---|---|---|
| Markdown + YAML frontmatter (`SKILL.md`) | The Claude Code skill format: frontmatter `name:`/`description:` + instruction body | It's the format Claude Code auto-discovers and triggers on. The `description` field *is* the routing logic. |
| Bash (`chat-skills-bundle/build-bundle.sh`) | ~35-line build script | Only build step needed: classify skills, copy, zip. No reason for anything heavier. |
| Python / JS / shell helper scripts (inside 27 skills) | e.g. `sales/scripts/*.py`, `obsidian-second-brain/scripts/`, `standup/standup.mjs` | Shipped by the upstream skill authors; mostly stdlib-only so they run without a package install. |
| `agents/openai.yaml` + `assets/trail-of-bits-mark.svg` (74 skills) | Branding/interface metadata | Comes verbatim from the Trail of Bits skill collection, which dual-targets OpenAI's agent format. Harmless to Claude Code; kept for upstream fidelity. |
| Git (vendored copies, **not** submodules) | Each upstream collection was copied in as a snapshot commit | Deliberate: snapshots can't break when upstream changes, and skills stay fully self-contained. The cost is manual re-syncing (see GAPS.md). |

## Repository layout

```
Everything-AI/
├── .claude/
│   ├── skills/                  # 274 skill directories + LICENSE + README.md
│   │   └── <skill-name>/
│   │       ├── SKILL.md         # REQUIRED: frontmatter + instructions (the skill itself)
│   │       ├── references/      # optional: deep-dive docs the skill tells Claude to read
│   │       ├── resources/       # optional: report templates, criteria (Trail of Bits style)
│   │       ├── templates/       # optional: output templates
│   │       ├── scripts/         # optional: runnable helpers (.py/.js/.sh/...)
│   │       ├── evals/evals.json # optional: prompt+assertion test cases (45 skills have these)
│   │       ├── agents/openai.yaml + assets/*.svg   # Trail of Bits branding metadata
│   │       └── workflows/       # optional: multi-phase procedures (semgrep, zeroize-audit…)
│   └── agents/                  # 5 sales research subagent definitions (*.md)
└── chat-skills-bundle/
    ├── build-bundle.sh          # THE build script — regenerates dist/
    ├── README.md                # usage instructions for the bundle
    ├── MANIFEST.md              # hand-maintained list of the 247 chat skills
    ├── EXCLUDED.md              # hand-maintained list of the 27 machine-only skills
    └── dist/everything-ai-chat-skills.zip   # committed build output (~6 MB)
```

Note: the Everything-AI repo root has **no README.md** — the only READMEs live in `.claude/skills/` (which describes only the original 47-skill marketing import and is stale) and `chat-skills-bundle/`.

## Where the skills came from (git history is the map)

Each commit on the main line imported one upstream collection. Knowing the families explains the wildly different styles you'll see:

| Family | ~Count | Examples | Style |
|---|---|---|---|
| Marketing skills (coreyhaines31/marketingskills, MIT) | 47 | `copywriting`, `cro`, `cold-email`, `seo-audit` | Long trigger-phrase descriptions, `references/`, `evals/`, `metadata.version` |
| context-engineering-kit | 67 | `commit`, `create-skill`, `judge`, `kaizen`, `tree-of-thoughts`, FPF skills (`actualize`, `decay`, `query`, `reflect`) | Short descriptions, slash-command flavored |
| Trail of Bits security skills | ~75 | `semgrep`, `codeql`, `c-review`, `*-vulnerability-scanner`, fuzzers (`aflpp`, `libfuzzer`, `atheris`) | `allowed-tools` frontmatter, `agents/openai.yaml`, `resources/`, `workflows/` |
| PicsArt gen-AI | 20 | `gen-ai-*`, `agency-*`, `enterprise-*`, `marketer-*`, `prosumer-*`, `picsart-api` | Image/brand-asset generation |
| Superpowers (obra) | 14 | `brainstorming`, `superpowers-test-driven-development`, `writing-skills`, `systematic-debugging` | Process-discipline skills |
| AI Sales Team | 13 skills + 5 agents | `sales` (orchestrator), `sales-prospect`, `sales-icp`, `.claude/agents/sales-*.md` | **No YAML frontmatter** (see GAPS.md #1); orchestrator/subagent architecture |
| claude-mem | 18 | `mem-search`, `cloud-sync`, `standup`, `weekly-digests`, `smart-explore` | Assumes the claude-mem memory plugin/DB exists |
| Caveman | 7 | `caveman`, `caveman-commit`, `caveman-stats` | Token-compression modes |
| Arcads ad-generation | 5 | `arcads-external-api`, `nano-banana-image-ad`, `chatgpt-image-ad` | External API driven (ARCADS_API_KEY via `.env`) |
| Singles | ~8 | `ui-ux-pro-max` (1.6 MB of CSV/data), `obsidian-second-brain` (2 MB, a whole vendored source repo), `remotion-best-practices`, `d3-viz`, `playwright-skill`, `ios-simulator-skill`, `stop-slop` | Each its own world |

## Architecture and data flow

There are two consumption paths and one build path:

```
                       ┌────────────────────────────┐
                       │  .claude/skills/<name>/    │
                       │  SKILL.md (frontmatter +   │
                       │  body) + support files     │
                       └──────┬──────────────┬──────┘
        Claude Code session   │              │   chat-skills-bundle/build-bundle.sh
        auto-discovers by     │              │   classifies each skill:
        frontmatter           │              │   contains *.py/*.js/*.sh/*.cjs/*.ps1/*.mjs ?
        `description` match   │              │     yes → EXCLUDED (27, machine-only)
                              ▼              │     no  → chat-friendly (247)
                   ┌───────────────┐         ▼
                   │ Claude Code   │   ┌──────────────────────────────────┐
                   │ (this repo or │   │ dist/everything-ai-chat-skills.zip│
                   │  ~/.claude/)  │   │  ├── skills/<name>/  (browsable) │
                   └───────────────┘   │  ├── zips/<name>.zip (uploadable)│
                                       │  └── README/MANIFEST/EXCLUDED    │
                                       └──────────────┬───────────────────┘
                                                      ▼
                                       user manually uploads individual
                                       zips/<name>.zip to Claude.ai →
                                       Settings → Capabilities → Skills
```

Key mechanics:

- **Skill triggering is entirely driven by the `description:` frontmatter field.** Claude Code (and Claude.ai) match the user's message against these descriptions. A skill with a bad or missing description is effectively invisible or mis-fires.
- **The chat/code split is a single heuristic**: `build-bundle.sh` marks a skill "machine-only" if and only if it contains a file with an executable-script extension. Nothing inspects whether a script-free skill actually *needs* a CLI, MCP server, or git (several do — see GAPS.md).
- **`MANIFEST.md` and `EXCLUDED.md` are not generated.** The build script copies them into the zip as-is; a human must update them when skill counts change. The script only *prints* the counts.
- **The sales suite is its own mini-architecture**: `sales/SKILL.md` is an orchestrator exposing `/sales <subcommand>`; `sales-prospect` fans out to the five subagents in `.claude/agents/` (company, competitive, contacts, opportunity, strategy research), each of which owns a weighted slice of a prospect score, aggregated into `PROSPECT-ANALYSIS.md`.

## Key design decisions (inferred)

1. **Vendor, don't reference.** Every collection is copied in wholesale rather than added as a submodule or fetched at build time. Consequence: total self-containment and snapshot stability, at the cost of duplication (74 identical Trail of Bits SVGs), staleness, and licensing bookkeeping.
2. **One flat namespace.** All 274 skills live directly under `.claude/skills/` with no per-source subdirectories, because Claude Code only discovers one level deep. Consequence: source families are only recoverable from git history, and near-duplicate names coexist (`brainstorm` vs `brainstorming`, `test-driven-development` vs `superpowers-test-driven-development`).
3. **Classification by file extension.** The chat bundle's "can this run in the Claude.ai sandbox?" decision is mechanical (script files present → excluded), chosen for simplicity and reproducibility over accuracy. The commit message "fix flaky classifier" (e1c9491) shows this was already iterated on once.
4. **Committed build artifact.** `dist/everything-ai-chat-skills.zip` is checked into git so the bundle is downloadable without running anything. Consequence: ~6 MB of binary churn per refresh.
5. **Upstream fidelity over consistency.** Skills were not normalized on import — frontmatter styles, directory conventions, and even the presence of frontmatter vary by family. This makes re-syncing from upstream easier but means there is no single "house style" (see Conventions in `CLAUDE.md`).

## Critical paths — what's load-bearing

**Most load-bearing (change with care):**

- `SKILL.md` frontmatter `name:` and `description:` fields, in every skill. These are the entire discovery/routing mechanism. Renaming a directory or editing a description changes when (or whether) the skill fires.
- `chat-skills-bundle/build-bundle.sh` — the classification rule (its `find … -name '*.py' …` list) determines which skills are claimed to work in Claude.ai chat. Adding a new script extension to a skill silently flips its classification on the next build.
- `.claude/skills/LICENSE` and `.claude/skills/README.md` — the only attribution for the MIT-licensed marketing collection. Don't delete.
- The `sales` ↔ `sales-*` ↔ `.claude/agents/sales-*.md` wiring — the orchestrator references subagents and subcommands by exact name.

**Safe to change casually:**

- The instruction *bodies* of individual skills (below the frontmatter) — each skill is isolated; editing one cannot break another.
- `references/`, `resources/`, `templates/` content within a skill.
- `MANIFEST.md` / `EXCLUDED.md` prose (but keep counts truthful).

**Regenerable (never hand-edit):**

- `chat-skills-bundle/dist/everything-ai-chat-skills.zip` — always rebuild with `bash chat-skills-bundle/build-bundle.sh`.

## Surprises and traps for someone new

1. **`.claude/skills/README.md` lies by omission.** It says "47 marketing skills … sourced from coreyhaines31/marketingskills" — true for the first import, but the directory now holds 274 skills from ~10 sources. Don't cite it as an inventory.
2. **The bundle README's directory tree describes the *zip's* contents, not the repo.** `chat-skills-bundle/skills/` and `chat-skills-bundle/zips/` do not exist on disk; they exist only inside `dist/everything-ai-chat-skills.zip` (the build assembles them in a temp dir).
3. **The 14 sales-suite SKILL.md files have no YAML frontmatter at all** — they open with a plain `#` heading. Auto-discovery of them is degraded/unreliable. Every other skill (260) has proper frontmatter.
4. **`obsidian-second-brain` is a complete vendored source repo**, including its own `CLAUDE.md`, `.github/workflows/`, `install.sh` (which symlinks into `~/.claude/`), and a multi-platform adapter build system. Its `CLAUDE.md` targets *that* skill's development, not this repo — don't let an agent confuse the two.
5. **Some "chat-friendly" skills aren't.** The classifier only checks for script files, so markdown-only skills that require CLIs or MCP servers (`gh-cli`, `codeql`, `chrome-mcp-troubleshooting`, `setup-serena-mcp`, `git-worktrees`, …) end up in the chat bundle where they can only offer advice, not function.
6. **Skill trigger collisions are real.** With 274 descriptions in play, overlapping skills (`brainstorm`/`brainstorming`, two TDD skills, two subagent-driven-development skills, `commit`/`caveman-commit`) compete for the same user phrasings; which one fires is effectively nondeterministic.
7. **The remote's default branch is a `claude/…` working branch**, not `main` — there is no `main` branch on the Everything-AI remote at all. Check `git remote show origin` before assuming branch conventions.
8. **Numbers drift.** `chat-skills-bundle/README.md` says 25 excluded skills; `EXCLUDED.md` lists 27 (27 is correct: 274 total − 247 chat = 27). Trust `build-bundle.sh` output and on-disk counts over prose.
