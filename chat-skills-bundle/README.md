# Everything-AI — Chat Skills Bundle

A ready-to-upload bundle of **230 chat-friendly skills** for the **Claude.ai app** (web/desktop chat).

These are the skills from the `Everything-AI` collection that run as pure guidance/knowledge — no
local machine, OS tools, external CLIs, or MCP servers required — so they work inside Claude.ai's
sandbox. (The 25 tool/machine-only skills are listed in `EXCLUDED.md` and belong in Claude Code.)

## What's inside

```
chat-skills-bundle/
├── README.md            # this file
├── MANIFEST.md          # all 230 skills + descriptions
├── EXCLUDED.md          # the 25 skills left out (and why)
├── skills/              # each skill as a browsable folder (SKILL.md + references/data/assets)
└── zips/                # each skill pre-zipped, one .zip per skill — ready to upload
```

## How to use in Claude.ai chat

Skills require a **paid plan** (Pro, Max, Team, or Enterprise).

1. Open **claude.ai** → **Settings → Capabilities**.
2. Turn on **Code execution** (skills run in the sandbox).
3. Under **Skills**, choose **Upload skill** and select a skill's `.zip` from the `zips/` folder.
   - Each `.zip` contains one skill folder with its `SKILL.md`.
4. Repeat for each skill you want. Uploaded skills auto-trigger when your message matches the
   skill's `description`, or you can point Claude at one explicitly.

> Tip: You don't need all 230. Pick the ones matching your work (e.g. `copywriting`, `cro`,
> `cold-email`, `brainstorming`, `marketing-council`, `content-strategy`). Accounts have skill
> limits, and a smaller focused set triggers more reliably.

## Notes

- **Prose vs. workflow.** Most of these are knowledge/advice skills and are fully usable in chat.
  A subset describe CLI/git workflows (e.g. `commit`, `create-pr`, `git-worktrees`, `gh-cli`) — they
  load fine as guidance but give their full value in Claude Code where the shell is available.
- **Data-backed skills work.** Skills that ship reference `.md`, `.csv`, or `.json` data (e.g.
  `ui-ux-pro-max`, `marketing-plan`) are included — the sandbox can read those files.
- Regenerate this bundle anytime with `build-bundle.sh` in the repo.

Source collection: `Everything-AI/.claude/skills/`.
