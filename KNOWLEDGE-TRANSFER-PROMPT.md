# Knowledge-Transfer Prompt

This is the reusable prompt that generated `PROJECT.md`, `GAPS.md`, and this repo's
`CLAUDE.md`. Point a capable model at any codebase with the text below to produce the
same three-document knowledge transfer. Run it with the most capable model available —
it is designed so that weaker models can pick up the work afterward from what it writes down.

---

You are running a one-time deep knowledge transfer on this codebase. You are the most capable model this project will have access to for a while, and your job is to write down everything you understand so that less capable models can pick up where you leave off. Be thorough, be specific, and be honest. Write for a competent engineer or AI agent who has never seen this project before.

Explore the entire codebase first. Read the directory structure, the configuration, the dependencies, the core modules, the tests, and any existing documentation. Take your time and build a real understanding before writing anything.

Then produce exactly three files.

## 1. Create PROJECT.md in the repository root.

This is the project overview a senior engineer would give a new hire. Include:

- What this application is and who it's for, in plain language.
- The tech stack and why each major piece appears to have been chosen.
- The architecture: how the major components fit together, where data flows, what talks to what. Use a simple text diagram if it helps.
- The key design decisions you can infer from the code, and the reasoning behind them where it's evident.
- The critical paths: which parts of the codebase matter most, which are load-bearing, and which are safe to change casually.
- Anything surprising or non-obvious that would trip up someone new.

## 2. Create GAPS.md in the repository root.

This is an honest audit of every weakness you find. Do not be polite. Include:

- Tech debt: shortcuts, duplicated logic, outdated patterns, dead code.
- Missing or weak test coverage, and specifically which critical paths are untested.
- Fragile edge cases: places likely to break under unusual input, concurrency, scale, or failure conditions.
- Security concerns: anything from missing input validation to secrets handling to permission gaps. Flag severity.
- Inconsistencies: places where the codebase disagrees with itself on patterns, naming, or structure.
- Half-finished work: migrations, TODOs, feature flags, or abstractions that were started and abandoned.

For every gap, include: what it is, where it lives (file paths), why it matters, and a suggested fix scoped small enough that a less capable model could execute it as a single task. Order the list by severity, most important first.

## 3. Update CLAUDE.md (create it if it doesn't exist).

This file is read at the start of every future Claude Code session, so it must make a smaller model instantly effective in this codebase. Preserve anything useful that's already in it, then expand it with:

- The commands that matter: build, test, lint, run, deploy.
- The conventions this codebase actually follows: naming, file organization, error handling, state management, styling.
- The gotchas: things that look like they should work one way but don't, and the correct way instead.
- The rules: what should never be changed without care, which files are generated, which patterns must be followed for consistency.
- Pointers to PROJECT.md for architecture context and GAPS.md for known issues, with one line explaining what each contains.

Keep CLAUDE.md tight and operational. It is instructions, not an essay. Put the narrative understanding in PROJECT.md instead.

When all three files are complete, finish with a short summary of: the three files you created, the five most important things you learned about this codebase, and the three highest-priority gaps you found.
