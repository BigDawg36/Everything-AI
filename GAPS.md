# GAPS.md — Honest audit of Everything-AI

*Written 2026-07-16; statuses updated the same day after a fix pass (see the **Status** line under each heading — 9 fixed, 2 partial, 1 open). Ordered by severity, most important first. Each entry ends with a fix scoped small enough to execute as a single task. See `PROJECT.md` for architecture context.*

---

## 1. Fourteen sales-suite skills have no YAML frontmatter — discovery is broken/degraded

**Status: FIXED (2026-07-16).** All 14 files now carry `name:`/`description:` frontmatter; `scripts/validate-skills.sh` enforces this going forward.

**What:** Every skill except the AI Sales Team suite opens with `---\nname: …\ndescription: …\n---`. The 14 sales files open with a bare `#` heading instead. Claude Code's skill routing matches on the frontmatter `description:`; without it, these skills either don't surface or surface with garbage descriptions (some currently show their `# Title` line or an internal "Metadata" section as their description).

**Where:** `.claude/skills/sales/SKILL.md` and `.claude/skills/sales-{prospect,icp,qualify,contacts,outreach,followup,objections,prep,proposal,competitors,research,report,report-pdf}/SKILL.md` (grep check: `grep -L '^---' .claude/skills/*/SKILL.md`).

**Why it matters:** This is the flagship multi-agent suite in the collection (orchestrator + 5 subagents + 13 subskills), and it's the least reliably triggerable part of the repo.

**Fix (single task):** For each of the 14 files, prepend a YAML frontmatter block with `name:` (matching the directory name) and a one-to-two-sentence `description:` derived from the file's opening paragraph, including trigger phrases like "/sales prospect". Do not change the bodies. Then rebuild the bundle (`bash chat-skills-bundle/build-bundle.sh`) since 13 of these are chat-included.

---

## 2. No validation or CI of any kind — nothing catches gap #1 class errors

**Status: FIXED (2026-07-16).** Added `scripts/validate-skills.sh` and `.github/workflows/validate.yml`. First run immediately caught a real defect: `version-bump` had frontmatter `name: claude-code-plugin-release` (now aligned to the directory name).

**What:** The repo has zero automated checks. No GitHub Actions workflow (the only `ci.yml` is vendored *inside* the obsidian-second-brain skill and does not run for this repo), no lint, no script that verifies each skill directory has a `SKILL.md` with parseable frontmatter and a unique `name:`.

**Where:** Repo root (no `.github/`), everywhere.

**Why it matters:** The collection grows by bulk imports. Malformed frontmatter (gap #1), duplicate `name:` fields, or stale manifests land silently and are only discovered when a skill fails to fire.

**Fix (single task):** Add `scripts/validate-skills.sh` (or `.py`) that asserts, for every `.claude/skills/*/`: a `SKILL.md` exists, starts with `---`, contains `name:` and `description:`, and that `name:` values are unique. Print failures and exit non-zero. Optionally wire it into a 10-line GitHub Actions workflow at `.github/workflows/validate.yml`.

---

## 3. Hand-maintained manifests already contradict each other

**Status: FIXED (2026-07-16).** `build-bundle.sh` now regenerates `MANIFEST.md` and `EXCLUDED.md` on every build; hardcoded counts removed from `chat-skills-bundle/README.md`; `.claude/skills/README.md` rewritten as a full source-family inventory.

**What:** `chat-skills-bundle/README.md` claims **25** excluded skills; `EXCLUDED.md` lists **27** (27 is correct today). `build-bundle.sh` computes the real lists at build time but only echoes counts — it copies `MANIFEST.md`/`EXCLUDED.md` into the zip verbatim, so they drift the moment any skill gains or loses a script file. The `.claude/skills/README.md` is worse: it describes the directory as "47 marketing skills" when it contains 274 skills from ~10 sources.

**Where:** `chat-skills-bundle/README.md` (line: "The 25 tool/machine-only skills…"), `chat-skills-bundle/MANIFEST.md`, `chat-skills-bundle/EXCLUDED.md`, `chat-skills-bundle/build-bundle.sh`, `.claude/skills/README.md`.

**Why it matters:** Stale inventories mislead both humans and agents; the bundle ships wrong documentation inside itself.

**Fix (single task):** Extend `build-bundle.sh` to *generate* `MANIFEST.md` (name + first ~160 chars of each `description:`) and `EXCLUDED.md` from its own `chat`/`excluded` arrays, writing them to both `$OUT/` and the build dir; fix the "25" → dynamic count in README (or have the script sed it). Separately update `.claude/skills/README.md` to describe all source families (the table in `PROJECT.md` can be copied).

---

## 4. Licensing/attribution covers only 1 of ~10 vendored collections

**Status: PARTIALLY FIXED (2026-07-16).** `ATTRIBUTIONS.md` added and shipped inside the bundle. Families whose upstream URL/license were never recorded are marked *verify upstream* — confirming those still needs owner/web research.

**What:** `.claude/skills/LICENSE` is Corey Haines's MIT license for the 47 marketing skills. The other ~227 skills (Trail of Bits ~75, context-engineering-kit 67, PicsArt 20, claude-mem 18, superpowers 14, sales 13, caveman 7, Arcads 5, singles) were vendored with no license files or upstream attribution beyond commit messages, and the chat bundle redistributes 247 of them as zips.

**Where:** `.claude/skills/LICENSE`, `.claude/skills/README.md`; absence everywhere else. (A few skills carry marks internally, e.g. Trail of Bits SVG/branding, `property-based-testing/README.md`.)

**Why it matters:** Redistribution (the whole point of `chat-skills-bundle`) without license/attribution is a legal exposure and discourteous to upstream authors. Severity: medium-high legally, trivial to remediate now, painful later.

**Fix (single task):** Create `ATTRIBUTIONS.md` at repo root listing each source family, its upstream repo/author, license, and which skill directories came from it (recoverable from `git log --stat` — commits 8debada, 03c2e2d, 2054f6d, 25d2694, e2a241a, 0756e1e, 22a3e5e, 210160d, 5356d56, 1fdb21b, 6ba24db, 2e2bf5c, 51fa065, bce2a4b, bf9f2a8). Include it in the bundle build.

---

## 5. Chat-bundle classifier misclassifies tool-dependent skills as chat-friendly

**Status: FIXED (2026-07-16).** `force-include.txt`/`force-exclude.txt` overrides added to `build-bundle.sh`; 9 machine-bound markdown-only skills excluded. Bundle is now 238 chat / 36 excluded (27 script-bearing + 9 forced).

**What:** `build-bundle.sh` marks a skill chat-friendly iff it contains no `*.py/*.js/*.sh/*.cjs/*.ps1/*.mjs` file. Markdown-only skills that fundamentally require a machine — `gh-cli`, `codeql`, `git-worktrees`, `chrome-mcp-troubleshooting`, `setup-serena-mcp`, `setup-context7-mcp`, `devcontainer-setup` (has scripts, ok), `ios-simulator` guidance-alikes, `fix-tests`, `babysit` — get included in the Claude.ai bundle where they cannot do their job. Conversely a skill with one optional convenience script is excluded outright.

**Where:** `chat-skills-bundle/build-bundle.sh` (the `find … -name '*.py' …` test); resulting misfiled entries in `MANIFEST.md`.

**Why it matters:** Users upload skills to Claude.ai that silently can't function; trust in the bundle erodes. The commit "fix flaky classifier" shows this boundary is already a known pain point.

**Fix (single task):** Add an explicit override mechanism to `build-bundle.sh`: two plain-text lists at `chat-skills-bundle/force-include.txt` and `force-exclude.txt` consulted after the extension heuristic. Seed `force-exclude.txt` with the obviously machine-bound markdown skills above (review each SKILL.md's requirements first).

---

## 6. Trigger-description collisions between near-duplicate skills

**Status: FIXED (2026-07-16)** for the worst collisions: `caveman-commit` and `caveman-review` no longer claim `/commit`, "write a commit", `/review`, or "review this PR"; both `superpowers-*` duplicates are now explicit-invocation-only; `brainstorm` defers to `brainstorming` for the general pre-implementation gate. No skills deleted.

**What:** Multiple imported families cover the same ground with competing descriptions: `brainstorm` (56 lines) vs `brainstorming` (159 lines); `test-driven-development` (698 lines) vs `superpowers-test-driven-development` (371 lines); `subagent-driven-development` vs `superpowers-subagent-driven-development`; `commit` vs `caveman-commit`; `review-pr` vs `caveman-review` vs `code-review`-adjacent skills; `memorize` (context-kit) alongside the claude-mem memory suite. Which fires for "help me brainstorm" or "write a commit message" is nondeterministic.

**Where:** `.claude/skills/{brainstorm,brainstorming,test-driven-development,superpowers-test-driven-development,subagent-driven-development,superpowers-subagent-driven-development,commit,caveman-commit,review-pr,caveman-review,memorize}/SKILL.md`.

**Why it matters:** Unpredictable skill selection is a correctness bug in a repo whose entire function is skill selection.

**Fix (single task):** For each collision pair, pick a primary (keep description broad) and edit the other's `description:` to be explicitly conditional ("Only when the user explicitly asks for the superpowers TDD process…" / "Only in caveman mode…"). Do not delete any skill; just disambiguate descriptions.

---

## 7. 6 MB binary build artifact committed to git

**Status: ADDRESSED (2026-07-16)** via the keep-and-document option: the zip stays committed (it is the owner's distribution channel), and `chat-skills-bundle/README.md` now documents the rebuild-after-any-skill-change requirement. Revisit `.gitignore`-ing `dist/` if history bloat becomes a problem.

**What:** `chat-skills-bundle/dist/everything-ai-chat-skills.zip` (6,037,145 bytes, 1,619 files inside) is checked in and fully replaced on every rebuild — git stores each version whole.

**Where:** `chat-skills-bundle/dist/`. There is also **no `.gitignore` at repo root** at all.

**Why it matters:** Repo history bloats ~6 MB per refresh, clones get slower forever, and a committed zip inevitably drifts from the skill tree between rebuilds (it is already one commit behind whenever a skill is edited without rebuilding).

**Fix (single task):** Add a root `.gitignore` containing `chat-skills-bundle/dist/`, `git rm --cached` the zip, and note in `chat-skills-bundle/README.md` that the bundle is produced locally via `build-bundle.sh` (or attached to GitHub Releases). If the owner wants the zip downloadable from the repo, keep it but document that every skill edit requires a rebuild commit.

---

## 8. The vendored `obsidian-second-brain` repo-within-a-repo

**Status: FIXED (2026-07-16).** Renamed to `UPSTREAM-CLAUDE.md` with a vendored-snapshot warning prepended; remaining `CLAUDE.md` mentions inside that skill are historical (changelog/fork notes) and were deliberately left untouched.

**What:** This "skill" is a complete upstream source repository: 102 scripts, its own `CLAUDE.md`, `.github/workflows/` (CI + scorecard that never run here), `.gitignore`, `install.sh` that symlinks into `~/.claude/`, a 6-platform adapter build system, and a `dist/` that its own docs say is gitignored (upstream) but whose parent is committed here.

**Where:** `.claude/skills/obsidian-second-brain/` (2.0 MB).

**Why it matters:** (a) Its `CLAUDE.md` can be picked up by agents and mistaken for this repo's instructions. (b) Running its `install.sh`/`update.sh` mutates `~/.claude/` outside the repo. (c) It's the single biggest contributor to tree noise.

**Fix (single task):** Rename its `CLAUDE.md` to `UPSTREAM-CLAUDE.md` (updating the one reference to it in that skill's docs), and add a note at the top of the skill's README that this is a vendored snapshot whose CI/installer are not wired to this repo. Do not restructure the skill otherwise.

---

## 9. Unaudited third-party executable scripts (supply-chain surface)

**Status: FIXED (2026-07-16).** `SCRIPT-AUDIT.md` generated at repo root: 218 scripts inventoried; flags — network: 20, home-writes: 28, exec: 60, curl-pipe-sh: 2. Both `curl|sh` hits were manually reviewed and are benign (a printed hint and a usage comment in obsidian-second-brain installers).

**What:** 218 executable script files across 27 skills were vendored from upstream authors without review. Spot checks found nothing malicious — no hardcoded secrets anywhere (verified by grep for key patterns), `arcads-external-api` handles its API key correctly (env var / `.env`, explicitly told not to log keys), and the `sales` Python scripts use stdlib `urllib` only. But nobody has systematically reviewed, e.g., `obsidian-second-brain`'s 102 scripts or `ios-simulator-skill`'s 43, and several (installers, `standup.mjs`) intentionally touch the filesystem outside the repo or make network calls to user-supplied URLs (`analyze_prospect.py`, `contact_finder.py` will fetch any URL — SSRF-style if ever run server-side).

**Where:** `find .claude/skills -name '*.py' -o -name '*.sh' -o -name '*.js' -o -name '*.mjs' -o -name '*.cjs' -o -name '*.ps1'` — heaviest: `obsidian-second-brain` (102), `ios-simulator-skill` (43), `zeroize-audit` (25).

**Why it matters:** Claude Code executes these with user permissions when a skill instructs it to. Severity: **medium** today (local, single-user, spot-checks clean), high if this collection is ever shared as-is.

**Fix (single task):** Run a scripted review pass: for each of the 27 script-bearing skills, list every file that (a) makes network calls, (b) writes outside the repo/CWD, or (c) invokes `curl|bash`-style patterns, and record the findings in a `SCRIPT-AUDIT.md`. This is enumeration, not judgment — a smaller model can produce the inventory and flag the three categories mechanically.

---

## 10. No repo-root README

**Status: FIXED (2026-07-16).** Root `README.md` added.

**What:** The Everything-AI repo root contains only `.claude/` and `chat-skills-bundle/` — the GitHub landing page renders nothing. The two READMEs that exist are buried and (per gap #3) stale or scoped to one subfolder.

**Where:** `/` (absence).

**Why it matters:** Anyone (or any agent) landing on the repo has to reverse-engineer what it is — which is exactly what this knowledge-transfer exercise had to do.

**Fix (single task):** Write a root `README.md`: one paragraph on what the collection is, the source-family table from `PROJECT.md`, how to use with Claude Code vs Claude.ai, and a pointer to `chat-skills-bundle/`. ~40 lines.

---

## 11. Frontmatter conventions disagree across families

**Status: PARTIALLY FIXED.** Conventions documented in `CLAUDE.md`; the 8 vendored TODOs are deliberately left for upstream fidelity.

**What:** Four coexisting frontmatter dialects: marketing skills use `metadata: {version: x.y.z}`; Trail of Bits uses `allowed-tools:` (space-separated) and multi-line `description: >-`; context-kit uses bare `name`/`description` plus occasional `argument-hint:`; claude-mem adds its own fields. Eight SKILL.md files contain literal TODOs (`brainstorming`, `smart-explore`, `create-hook`, `writing-plans`, `obsidian-second-brain`, `update-docs`, plus two others in the grep). None of this breaks discovery (except gap #1), but there is no documented house standard for *new* skills written in this repo.

**Where:** All `SKILL.md` frontmatter; TODO list via `grep -rn TODO .claude/skills --include=SKILL.md -l`.

**Why it matters:** Without a stated standard, future additions will copy whichever neighbor they saw first, deepening the inconsistency.

**Fix (single task):** Document the canonical minimal frontmatter (`name`, `description`, optional `allowed-tools`, optional `metadata.version`) in `CLAUDE.md` (done — see Conventions there) and leave vendored skills untouched. Optionally, resolve the 8 TODOs one skill at a time as separate tasks.

---

## 12. `-Keeping-Fable-5` sibling repo is an empty placeholder

**Status: OPEN — needs owner input.** The prompt text exists only in the owner's head; nothing in either repo contains it.

**What:** The second repo in this workspace contains a single one-line README ("Prompt to keep Fable 5 when the $$$ goes up") and nothing else — no prompt actually stored.

**Where:** `-Keeping-Fable-5/README.md`.

**Why it matters:** Low severity; but as it stands the repo doesn't do the one thing its name promises (preserve a prompt).

**Fix (single task):** Either add the actual prompt content to that repo's README (owner input required — the prompt text is not derivable from the codebase), or archive the repo.

---

## Explicitly checked and found OK

- **No hardcoded secrets**: grepped all scripts/configs for API-key/token/password literal patterns and known key formats (`sk-…`, `ghp_…`, `AKIA…`) — clean.
- **Bundle math is internally consistent** where it's generated: 274 skills = 247 chat + 27 excluded; the committed zip contains exactly 247 per-skill zips.
- **`arcads-external-api` secret hygiene** is actually good: `.env`-based key, explicit "do not log keys/prompts" rules.
- **Dead code**: essentially none outside vendored infra (gap #8) — skills are data, and unused ones are inert rather than dead.
