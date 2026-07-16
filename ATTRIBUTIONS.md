# ATTRIBUTIONS.md

Every skill in `.claude/skills/` is a vendored snapshot from an upstream collection.
This file records where each family came from and what is known about its license.
Import commits are the authoritative record of which directories belong to which family
(`git log --stat <commit>`).

**Honesty note:** most families were imported without copying their upstream LICENSE
files, and this table was reconstructed after the fact from import-commit messages and
traces inside the vendored files. Entries marked *verify upstream* have no license
recorded in this repo — confirm before redistributing beyond personal use. The
`chat-skills-bundle` redistributes most of these skills; treat unverified entries
accordingly.

| Family | Import commit | Skills | Upstream / author | License |
|---|---|---|---|---|
| Marketing skills | `8debada` | 47 (e.g. `copywriting`, `cro`, `cold-email`, `seo-audit`) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), Corey Haines | MIT — vendored at `.claude/skills/LICENSE` |
| context-engineering-kit | `03c2e2d` | 67 (e.g. `commit`, `create-skill`, `judge`, `kaizen`, `tree-of-thoughts`, FPF skills) | "context-engineering-kit" per import commit; exact upstream URL not recorded | *verify upstream* |
| Trail of Bits security skills | `5356d56` | ~75 (e.g. `semgrep`, `codeql`, `c-review`, `*-vulnerability-scanner`, fuzzing skills; carry `agents/openai.yaml` + Trail of Bits branding) | Trail of Bits (skills reference trailofbits/* repos and ship the ToB mark) | *verify upstream* |
| PicsArt gen-AI | `0756e1e` | 20 (`gen-ai-*`, `agency-*`, `enterprise-*`, `marketer-*`, `prosumer-*`, `picsart-api`, …) | PicsArt per import commit; exact upstream URL not recorded | *verify upstream* |
| Superpowers | `0756e1e` | 14 (e.g. `brainstorming`, `superpowers-test-driven-development`, `writing-skills`, `systematic-debugging`) | "superpowers" per import commit (widely known as obra/superpowers); URL not recorded at import | *verify upstream* |
| AI Sales Team | `22a3e5e` | 13 `sales*` skills + 5 subagents in `.claude/agents/` | Not recorded at import | *verify upstream* |
| claude-mem | `bce2a4b` | 18 (e.g. `mem-search`, `cloud-sync`, `standup`, `weekly-digests`, `smart-explore`, `version-bump`) | claude-mem project (skills reference cmem.ai); URL not recorded at import | *verify upstream* |
| Caveman | `1fdb21b` | 7 (`caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew`) | Not recorded at import | *verify upstream* |
| Arcads ad-generation | `e2a241a` | 5 (`arcads-external-api`, `nano-banana-image-ad`, `chatgpt-image-ad`, `image-ad-clone`, `video`-adjacent) | Arcads (arcads.ai) per skill content | *verify upstream* |
| obsidian-second-brain | `210160d` | 1 | [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | MIT — vendored at `.claude/skills/obsidian-second-brain/LICENSE` |
| ui-ux-pro-max | `25d2694` | 1 | Not recorded at import | *verify upstream* |
| remotion-best-practices | `2054f6d` | 1 | Remotion project docs-derived | *verify upstream* |
| d3-viz | `2e2bf5c` | 1 | Not recorded at import | *verify upstream* |
| playwright-skill | `6ba24db` | 1 | Not recorded at import | *verify upstream* |
| ios-simulator-skill | `51fa065` | 1 | Not recorded at import | *verify upstream* |
| stop-slop | `bf9f2a8` | 1 | Not recorded at import | *verify upstream* |

## House rules

- Do not delete `.claude/skills/LICENSE` (marketing skills MIT) or
  `.claude/skills/obsidian-second-brain/LICENSE`.
- When importing a new collection, copy its LICENSE into the skill directory (or this
  table) at import time — reconstructing attribution later is exactly the problem this
  file exists to stop.
- When an upstream in the *verify upstream* state is identified, update this table with
  the URL and license.
