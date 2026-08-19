# Everything-AI Skills

A flat collection of **Claude Code skills** vendored from ~10 upstream collections.
Each subdirectory is a self-contained skill with a `SKILL.md` (YAML frontmatter +
instructions), plus optional `references/`, `resources/`, `templates/`, `scripts/`,
and `evals/`. Claude Code auto-discovers these under `.claude/skills/` and invokes
them by matching the `description:` in each skill's frontmatter.

Full source-family map, upstream links, and licenses: see `ATTRIBUTIONS.md` and
`PROJECT.md` at the repo root. Validate the tree with `bash scripts/validate-skills.sh`.

## Source families (import order)

| Family | ~Count | Coverage |
|---|---|---|
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT, Corey Haines — see `LICENSE` in this directory) | 47 | CRO, copywriting, cold email, SEO/AI SEO, ads, pricing, churn, PR, and more |
| context-engineering-kit | 67 | Claude Code workflow skills: commit, create-skill, judge, kaizen, TDD, FPF |
| Trail of Bits security skills | ~75 | Static analysis, fuzzing, crypto review, per-chain vulnerability scanners |
| PicsArt gen-AI | 20 | Image/brand asset generation (`gen-ai-*`, `agency-*`, `enterprise-*`, …) |
| Superpowers (obra) | 14 | Process discipline: brainstorming, TDD, debugging, writing skills |
| AI Sales Team | 13 + 5 agents | `/sales` orchestrator suite (see `.claude/agents/`) |
| claude-mem | 18 | Memory, standup, digests, smart-explore |
| Caveman | 7 | Token-compression modes |
| Arcads ad-generation | 5 | AI video/image ad creative via the Arcads API |
| Singles | ~8 | `ui-ux-pro-max`, `obsidian-second-brain`, `remotion-best-practices`, `d3-viz`, `playwright-skill`, `ios-simulator-skill`, `stop-slop` |
