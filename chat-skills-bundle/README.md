# Everything-AI — Chat Skills Bundle

A ready-to-upload bundle of the **chat-friendly skills** from this collection, for the **Claude.ai app** (web/desktop chat).

These are the skills that run as pure guidance/knowledge — no local machine, OS tools, external CLIs, or MCP servers required — so they work inside Claude.ai's sandbox. The machine-only skills are listed in `EXCLUDED.md` and belong in Claude Code. Current counts live in `MANIFEST.md` and `EXCLUDED.md`, which are **generated** by `build-bundle.sh` — don't hand-edit them, and don't trust prose counts anywhere else.

## What's inside the zip

The directory tree below describes the **contents of `dist/everything-ai-chat-skills.zip`** — `skills/` and `zips/` are assembled in a temp dir at build time and do not exist in the repo:

```
everything-ai-chat-skills.zip
├── README.md            # this file
├── MANIFEST.md          # every included skill + description (generated)
├── EXCLUDED.md          # skills left out, and why (generated)
├── ATTRIBUTIONS.md      # upstream sources and licenses
├── skills/              # each skill as a browsable folder (SKILL.md + references/data/assets)
└── zips/                # each skill pre-zipped, one .zip per skill — ready to upload
```

## How the split is decided

1. **Heuristic:** a skill containing any executable script file (`.py/.js/.sh/.cjs/.ps1/.mjs`) is machine-only.
2. **Overrides:** `force-exclude.txt` removes markdown-only skills that still need CLIs/MCP/git (e.g. `gh-cli`, `codeql`); `force-include.txt` can rescue a skill whose scripts are optional. Edit these lists, then rebuild.

## How to use in Claude.ai chat

Skills require a **paid plan** (Pro, Max, Team, or Enterprise).

1. Open **claude.ai** → **Settings → Capabilities**.
2. Turn on **Code execution** (skills run in the sandbox).
3. Under **Skills**, choose **Upload skill** and select a skill's `.zip` from the `zips/` folder.
   - Each `.zip` contains one skill folder with its `SKILL.md`.
4. Repeat for each skill you want. Uploaded skills auto-trigger when your message matches the
   skill's `description`, or you can point Claude at one explicitly.

> Tip: You don't need all of them. Pick the ones matching your work (e.g. `copywriting`, `cro`,
> `cold-email`, `brainstorming`, `marketing-council`, `content-strategy`). Accounts have skill
> limits, and a smaller focused set triggers more reliably.

## Keeping the bundle fresh

`dist/everything-ai-chat-skills.zip` is a committed build artifact. It only reflects the skill tree as of its last build, so **rebuild after any skill change** — especially adding/removing a skill, adding/removing a script file (flips classification), or editing a `description:`:

```bash
bash chat-skills-bundle/build-bundle.sh
```

Verify the printed `chat-friendly: N | excluded: M` counts (N+M must equal the number of skill directories) and commit the regenerated `dist/`, `MANIFEST.md`, and `EXCLUDED.md` together with your skill change.

## Notes

- **Data-backed skills work.** Skills that ship reference `.md`, `.csv`, or `.json` data (e.g.
  `ui-ux-pro-max`, `marketing-plan`) are included — the sandbox can read those files.
- Some included skills describe git/CLI workflows (e.g. `commit`, `create-pr`) — they load fine as
  guidance but give their full value in Claude Code where the shell is available.

Source collection: `Everything-AI/.claude/skills/`.
