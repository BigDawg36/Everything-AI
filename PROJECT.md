# PROJECT.md — Everything-AI

*Knowledge-transfer overview. Written 2026-07-16 after a full audit of the repository. Companion documents: `CLAUDE.md` (operational instructions for AI agents) and `GAPS.md` (honest audit of known weaknesses).*

## What this is

**Everything-AI is not an application. It is a curated mega-collection of 274 Claude Code skills** — prompt/instruction packages in Markdown — aggregated from roughly ten public open-source skill collections into one repo, plus a small build pipeline that repackages the chat-compatible subset (currently 238 skills) for upload to the Claude.ai web/desktop app.

It's for one user (the repo owner) who wants every useful Claude skill available in two places:

1. **Claude Code** — the entire `.claude/skills/` tree is auto-discovered when Claude Code runs anywhere in this repo (or when the tree is copied/symlinked into `~/.claude/`).
2. **Claude.ai chat** — via `chat-skills-bundle/`, which zips the skills that need no local machine (238 currently) so they can be uploaded under *Settings → Capabilities → Skills*.

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
    ├── build-bundle.sh          # THE build script — regenerates dist/ + both manifests
    ├── README.md                # usage instructions for the bundle
    ├── MANIFEST.md              # GENERATED list of the chat skills (238)
    ├── EXCLUDED.md              # GENERATED list of the machine-only skills (36)
    ├── force-include.txt        # classifier overrides (script-bearing but chat-usable)
    ├── force-exclude.txt        # classifier overrides (markdown-only but machine-bound)
    └── dist/everything-ai-chat-skills.zip   # committed build output (~6 MB)
```

Repo root also carries `README.md`, `ATTRIBUTIONS.md` (upstream/license per family), `SCRIPT-AUDIT.md` (script risk inventory), and `scripts/validate-skills.sh` (frontmatter validation, wired to CI in `.github/workflows/validate.yml`).

## Where the skills came from (git history is the map)

Each commit on the main line imported one upstream collection. Knowing the families explains the wildly different styles you'll see:

| Family | ~Count | Examples | Style |
|---|---|---|---|
| Marketing skills (coreyhaines31/marketingskills, MIT) | 47 | `copywriting`, `cro`, `cold-email`, `seo-audit` | Long trigger-phrase descriptions, `references/`, `evals/`, `metadata.version` |
| context-engineering-kit | 67 | `commit`, `create-skill`, `judge`, `kaizen`, `tree-of-thoughts`, FPF skills (`actualize`, `decay`, `query`, `reflect`) | Short descriptions, slash-command flavored |
| Trail of Bits security skills | ~75 | `semgrep`, `codeql`, `c-review`, `*-vulnerability-scanner`, fuzzers (`aflpp`, `libfuzzer`, `atheris`) | `allowed-tools` frontmatter, `agents/openai.yaml`, `resources/`, `workflows/` |
| PicsArt gen-AI | 20 | `gen-ai-*`, `agency-*`, `enterprise-*`, `marketer-*`, `prosumer-*`, `picsart-api` | Image/brand-asset generation |
| Superpowers (obra) | 14 | `brainstorming`, `superpowers-test-driven-development`, `writing-skills`, `systematic-debugging` | Process-discipline skills |
| AI Sales Team | 13 skills + 5 agents | `sales` (orchestrator), `sales-prospect`, `sales-icp`, `.claude/agents/sales-*.md` | Orchestrator/subagent architecture (frontmatter added 2026-07-16 — see GAPS.md #1) |
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
        frontmatter           │              │   script file present? → machine-only (27)
        `description` match   │              │   in force-exclude.txt? → machine-only (9)
                              ▼              │   otherwise → chat-friendly (238)
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
- **The chat/code split is a heuristic plus overrides**: `build-bundle.sh` marks a skill "machine-only" if it contains a file with an executable-script extension, then applies `force-exclude.txt` (markdown-only skills that still need CLIs/MCP/git) and `force-include.txt`.
- **`MANIFEST.md` and `EXCLUDED.md` are generated** by `build-bundle.sh` on every build (descriptions parsed from frontmatter). Never hand-edit them.
- **The sales suite is its own mini-architecture**: `sales/SKILL.md` is an orchestrator exposing `/sales <subcommand>`; `sales-prospect` fans out to the five subagents in `.claude/agents/` (company, competitive, contacts, opportunity, strategy research), each of which owns a weighted slice of a prospect score, aggregated into `PROSPECT-ANALYSIS.md`.

## Key design decisions (inferred)

1. **Vendor, don't reference.** Every collection is copied in wholesale rather than added as a submodule or fetched at build time. Consequence: total self-containment and snapshot stability, at the cost of duplication (74 identical Trail of Bits SVGs), staleness, and licensing bookkeeping.
2. **One flat namespace.** All 274 skills live directly under `.claude/skills/` with no per-source subdirectories, because Claude Code only discovers one level deep. Consequence: source families are only recoverable from git history, and near-duplicate names coexist (`brainstorm` vs `brainstorming`, `test-driven-development` vs `superpowers-test-driven-development`).
3. **Classification by file extension, corrected by override lists.** The chat bundle's "can this run in the Claude.ai sandbox?" decision is mechanical (script files present → excluded), chosen for simplicity and reproducibility; `force-exclude.txt`/`force-include.txt` patch the cases the heuristic gets wrong. The commit message "fix flaky classifier" (e1c9491) shows the boundary needed iteration even before the overrides.
4. **Committed build artifact.** `dist/everything-ai-chat-skills.zip` is checked into git so the bundle is downloadable without running anything. Consequence: ~6 MB of binary churn per refresh.
5. **Upstream fidelity over consistency.** Skills were not normalized on import — frontmatter styles, directory conventions, and even the presence of frontmatter vary by family. This makes re-syncing from upstream easier but means there is no single "house style" (see Conventions in `CLAUDE.md`).

## Critical paths — what's load-bearing

**Most load-bearing (change with care):**

- `SKILL.md` frontmatter `name:` and `description:` fields, in every skill. These are the entire discovery/routing mechanism. Renaming a directory or editing a description changes when (or whether) the skill fires.
- `chat-skills-bundle/build-bundle.sh` + `force-*.txt` — the classification rule determines which skills are claimed to work in Claude.ai chat. Adding a script file to a skill silently flips its classification on the next build.
- `.claude/skills/LICENSE` and `.claude/skills/README.md` — the only attribution for the MIT-licensed marketing collection. Don't delete.
- The `sales` ↔ `sales-*` ↔ `.claude/agents/sales-*.md` wiring — the orchestrator references subagents and subcommands by exact name.

**Safe to change casually:**

- The instruction *bodies* of individual skills (below the frontmatter) — each skill is isolated; editing one cannot break another.
- `references/`, `resources/`, `templates/` content within a skill.
- `chat-skills-bundle/README.md` prose (avoid hardcoding counts — they drift).

**Regenerable (never hand-edit):**

- `chat-skills-bundle/dist/everything-ai-chat-skills.zip`, `MANIFEST.md`, `EXCLUDED.md` — always rebuild with `bash chat-skills-bundle/build-bundle.sh`.

## Surprises and traps for someone new

1. **Prose inventories drift.** `.claude/skills/README.md` originally described only the first 47-skill import (rewritten 2026-07-16 as a family map); trust `validate-skills.sh` output and `ATTRIBUTIONS.md` over any prose counts.
2. **The bundle README's directory tree describes the *zip's* contents, not the repo.** `chat-skills-bundle/skills/` and `chat-skills-bundle/zips/` do not exist on disk; they exist only inside `dist/everything-ai-chat-skills.zip` (the build assembles them in a temp dir).
3. **The 14 sales-suite SKILL.md files historically had no YAML frontmatter** (fixed 2026-07-16; `validate-skills.sh` now enforces it). Their bodies still assume `/sales <subcommand>` invocation wired to the orchestrator.
4. **`obsidian-second-brain` is a complete vendored source repo**, including its own `.github/workflows/`, `install.sh` (which symlinks into `~/.claude/`), and a multi-platform adapter build system. Its upstream instructions live in `UPSTREAM-CLAUDE.md` (renamed from `CLAUDE.md` to avoid confusion with this repo's).
5. **Some markdown-only skills still need a machine.** The extension heuristic can't see CLI/MCP requirements, so `force-exclude.txt` keeps `gh-cli`, `codeql`, `chrome-mcp-troubleshooting`, the `setup-*-mcp` skills, and the git-worktree skills out of the chat bundle. Extend that list when importing similar skills.
6. **Skill trigger collisions are real.** With 274 descriptions in play, overlapping skills compete for the same user phrasings. The worst pairs were disambiguated in 2026-07 (secondary skill's description now defers to the primary: `caveman-commit`→`commit`, `caveman-review`→`review-pr`, `superpowers-*`→ unprefixed, `brainstorm`→`brainstorming`); keep new imports out of existing trigger space.
7. **The remote's default branch is a `claude/…` working branch**, not `main` — there is no `main` branch on the Everything-AI remote at all. Check `git remote show origin` before assuming branch conventions.
8. **Numbers drift wherever they're hardcoded.** The manifests are now generated and the bundle README count-free, but any prose that names a skill count (including this file's 274/238/36) goes stale on the next import. Trust `build-bundle.sh` output and `validate-skills.sh` over prose.
