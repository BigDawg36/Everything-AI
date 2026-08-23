# ATTRIBUTIONS.md

Every skill in `.claude/skills/` is a vendored snapshot from an upstream collection.
This file records where each family came from and its license. Import commits are the
authoritative record of which directories belong to which family (`git log --stat <commit>`).

Upstreams and licenses below were verified against the upstream repositories on
**2026-07-16** (identified via content fingerprints in the vendored files, then confirmed
on each repo's page). Licenses can change upstream; re-verify before large-scale
redistribution.

| Family | Import commit | Skills | Upstream / author | License |
|---|---|---|---|---|
| Marketing skills | `8debada` | 47 (e.g. `copywriting`, `cro`, `cold-email`, `seo-audit`) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), Corey Haines | MIT — vendored at `.claude/skills/LICENSE` |
| context-engineering-kit | `03c2e2d` | 67 (e.g. `commit`, `create-skill`, `judge`, `kaizen`, `tree-of-thoughts`, FPF skills) | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | **GPL-3.0** ⚠ see notes |
| Trail of Bits security skills | `5356d56` | ~75 (e.g. `semgrep`, `codeql`, `c-review`, `*-vulnerability-scanner`, fuzzing skills) | [trailofbits/skills](https://github.com/trailofbits/skills), Trail of Bits | **CC-BY-SA-4.0** ⚠ see notes |
| PicsArt gen-AI | `0756e1e` | 20 (`gen-ai-*`, `agency-*`, `enterprise-*`, `marketer-*`, `prosumer-*`, `picsart-api`, …) | [PicsArt/gen-ai-skills](https://github.com/PicsArt/gen-ai-skills) | MIT |
| Superpowers | `0756e1e` | 14 (e.g. `brainstorming`, `superpowers-test-driven-development`, `writing-skills`, `systematic-debugging`) | [obra/superpowers](https://github.com/obra/superpowers), Jesse Vincent | MIT |
| AI Sales Team | `22a3e5e` | 14 `sales*` skills + 5 subagents in `.claude/agents/` | [zubair-trabzada/ai-sales-team-claude](https://github.com/zubair-trabzada/ai-sales-team-claude), Zubair Trabzada | MIT |
| claude-mem | `bce2a4b` | 18 (e.g. `mem-search`, `cloud-sync`, `standup`, `weekly-digests`, `smart-explore`, `version-bump`) | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) (cmem.ai) | Apache-2.0 |
| Caveman | `1fdb21b` | 7 (`caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew`) | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT |
| Arcads ad-generation | `e2a241a` | 5 (`arcads-external-api`, `nano-banana-image-ad`, `chatgpt-image-ad`, `image-ad-clone`, …) | [krusemediallc/arcads-claude-code](https://github.com/krusemediallc/arcads-claude-code) (Arcads external API) | MIT |
| obsidian-second-brain | `210160d` | 1 | [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | MIT — vendored at `.claude/skills/obsidian-second-brain/LICENSE` |
| ui-ux-pro-max | `25d2694` | 1 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT |
| remotion-best-practices | `2054f6d` | 1 | [remotion-dev/skills](https://github.com/remotion-dev/skills) (official Remotion agent skills, [docs](https://www.remotion.dev/docs/ai/skills)) | **None published** ⚠ see notes |
| d3-viz | `2e2bf5c` | 1 | [chrisvoncsefalvay/claude-d3js-skill](https://github.com/chrisvoncsefalvay/claude-d3js-skill), Chris von Csefalvay | **None listed** ⚠ see notes |
| playwright-skill | `6ba24db` | 1 | [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | MIT |
| ios-simulator-skill | `51fa065` | 1 | [conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill), Conor Luddy | MIT |
| stop-slop | `bf9f2a8` | 1 | [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop), Hardik Pandya | MIT |
| last30days-skill | *(this commit)* | 1 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill), mvanhorn | MIT |

## License notes (read before redistributing)

- **GPL-3.0 — context-engineering-kit (67 skills).** Copyleft: redistributing these skills
  (including inside `chat-skills-bundle`) requires preserving the GPL-3.0 notice and making
  the "source" (the markdown itself, which is what's shipped) available under the same
  license. Shipping this file inside the bundle satisfies attribution; keep it there.
- **CC-BY-SA-4.0 — Trail of Bits skills (~75 skills).** Requires attribution (this file)
  and ShareAlike: derivatives of these skills must carry CC-BY-SA-4.0 as well. The skills
  also ship Trail of Bits branding (`assets/trail-of-bits-mark.svg`) — the mark itself is
  ToB's; don't reuse it outside these skills.
- **No license — remotion-best-practices and d3-viz.** No license is published on either
  upstream repo, which legally defaults to all-rights-reserved. Remotion's skills are
  distributed by Remotion for agent use via their docs; `claude-d3js-skill` is public but
  unlicensed. Personal use is low-risk; **for public redistribution of the chat bundle,
  either obtain permission, or drop these two skills from the bundle**
  (add them to `chat-skills-bundle/force-exclude.txt`).
- MIT and Apache-2.0 families are fine to redistribute with this attribution file included
  (the bundle build copies `ATTRIBUTIONS.md` into the zip).

## House rules

- Do not delete `.claude/skills/LICENSE` (marketing skills MIT) or
  `.claude/skills/obsidian-second-brain/LICENSE`.
- When importing a new collection, record its upstream URL + license here **at import
  time** — reconstructing attribution later is exactly the problem this file exists to stop.
