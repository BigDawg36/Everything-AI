# Koa

Mike's voice-first personal assistant. The spec is in [AGENT.md](AGENT.md). Behavior settings are in [config.toml](config.toml).

Current stage: **Tier 1, the brain.** Text conversation only: no tools, no voice, and no memory between runs yet.

## Run it on your laptop (first time)

You need Python 3.11 or newer. Check with `python3 --version` (Mac) or `py --version` (Windows).

1. **Open a terminal in this folder.** It's the `koa` folder inside the Everything-AI repo.

2. **Make a private Python environment.** This keeps Koa's libraries separate from everything else on your machine.
   - Mac: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -m venv .venv` then `.venv\Scripts\activate`

3. **Install the one library Koa needs.**
   `pip install -r requirements.txt`

4. **Add your API key.** Copy `.env.example` to a new file named `.env`, then paste your Anthropic key after `ANTHROPIC_API_KEY=`. Get a key at console.anthropic.com under API Keys. The `.env` file is git-ignored, so it never gets committed.

5. **Start Koa.**
   `python -m koa.cli`

Type to talk. Type `exit` to leave. Press Ctrl+C while Koa is answering to stop a reply.

Next time you only need step 2's `activate` command, then step 5.

## Verify Tier 1

1. Tell Koa something specific: "My top rep this quarter is Jason."
2. Ask two unrelated questions.
3. Ask: "Who's my top rep?" Koa should answer Jason.
4. Type `exit`, restart, and ask again. Koa should **not** know. That's expected; long-term memory arrives in Tier 4.
5. Turn off Wi-Fi and send a message. You should see a plain "can't reach the model" note, not a crash. Turn Wi-Fi back on, and the next message should work.

## Tests

`python -m unittest discover tests`

These run without an API key or network. They check that history is sent every turn, that failed turns roll back cleanly, that errors become plain-language messages, and that the persona keeps its rails.

## Layout

```
koa/
  AGENT.md            spec and decisions
  config.toml         model, effort, schedule (tune here, not in code)
  koa/
    brain.py          the one conversation loop every interface shares
    persona.py        Koa's system prompt
    providers/        the model seam: swap Claude for another provider here only
    cli.py            text interface
  tests/
```
