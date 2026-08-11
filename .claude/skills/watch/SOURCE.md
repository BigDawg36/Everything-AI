# Vendored skill: `watch`

Runtime files copied from [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
(MIT License, by Bradley Bonanno). See `LICENSE`.

| | |
|---|---|
| Upstream repo | `bradautomates/claude-video` |
| Upstream path | `skills/watch/` |
| Skill version | 0.2.0 |
| Vendored at commit | `83da59f` |

## Why this copy exists

`.claude/settings.json` already registers the `claude-video` marketplace and
enables `watch@claude-video`, which is the auto-updating install. Plugins don't
load in Claude Code web sessions, so this copy is what makes `/watch` available
there — the plugin covers local Claude Code, this copy covers the rest.

Both can be active at once in local Claude Code, which registers `watch` twice.
If that's noisy, delete this directory and keep the plugin.

## What was left out

Upstream's own `.skillignore` marks `scripts/build-skill.sh` as dev-only and not
needed at runtime, so it isn't copied. Tests, hooks, and packaging metadata stay
upstream too. `SKILL.md` resolves its scripts relative to its own location, so it
runs unmodified from here.

## Re-syncing

```bash
git clone --depth 1 https://github.com/bradautomates/claude-video.git /tmp/claude-video
cp /tmp/claude-video/skills/watch/SKILL.md .claude/skills/watch/
cp /tmp/claude-video/skills/watch/scripts/*.py .claude/skills/watch/scripts/
```

Then update the version and commit in the table above.

## Runtime dependencies

Needs `yt-dlp`, `ffmpeg`, and `ffprobe` on `PATH`; `scripts/setup.py` installs
them on first run (`brew` on macOS, printed instructions elsewhere). None are
preinstalled in Claude Code cloud containers, so the first `/watch` there pays
the install cost. On Ubuntu containers, `pip install yt-dlp` plus
`apt-get update && apt-get install -y --no-install-recommends ffmpeg` works;
skip the `apt-get update` and the archive fetch 404s on stale indexes. A Whisper
API key (Groq or OpenAI) is only needed for videos with no captions.

## Network policy limits URL sources in cloud sessions

Verified in a Claude Code web session: the agent proxy denies `CONNECT` to
video hosts (`youtube.com`, `vimeo.com` both 403 at the gateway), so `/watch
<url>` cannot fetch anything there regardless of `yt-dlp` being installed.
Local file paths work fully — frame extraction and `Read` of the JPEGs both
verified end to end. Whether URLs work depends on the environment's network
policy, so this is a per-environment limit, not a property of the skill.
