---
name: setup-tencentdb-agent-memory
description: Guide for setting up TencentDB Agent Memory (layered long-term + symbolic short-term memory system) via Docker and routing Claude Code through its local proxy
argument-hint: Optional - LLM provider/model to use for the memory group and the upstream proxy group
---

User Input:

```text
$ARGUMENTS
```

# Guide for setup TencentDB Agent Memory

TencentDB Agent Memory ("TDAI") gives agents persistent, layered long-term
memory (raw conversation → atoms → scenarios → persona) plus a symbolic
short-term memory that swaps verbose tool logs for compact Mermaid canvases.
The `deploy/global-images` bundle runs three services with Docker Compose —
`memory-core`, `memory-hub` (panel + knowledge), and `proxy` — then prints a
ready-to-use connection block for Claude Code.

## 1. Determine setup context

Ask the user where they want to store the configuration:

**Options:**

1. **Project level (shared via git)** - Configuration tracked in version control, shared with team
   - CLAUDE.md updates go to: `./CLAUDE.md`

2. **Project level (personal preferences)** - Configuration stays local, not tracked in git
   - CLAUDE.md updates go to: `./CLAUDE.local.md`
   - Verify these files are listed in `.gitignore`, add them if not

3. **User level (global)** - Configuration applies to all projects for this user
   - CLAUDE.md updates go to: `~/.claude/CLAUDE.md`

Store the user's choice and use the appropriate paths in subsequent steps.

## 2. Check prerequisites

Verify the host has what `start-all.sh` needs:

- `docker` and `docker compose` (or `docker-compose`) — required to run the three services
- `git` — required to clone the repo

If Docker isn't installed, point the user to <https://docs.docker.com/get-docker/> and stop until it's available.

## 3. Check if TencentDB Agent Memory is already running

Check for existing containers/ports before starting new ones:

```bash
docker ps --filter "name=tdai" --filter "name=memory-core" --filter "name=memory-hub" --filter "name=memory-proxy"
```

If containers are already up and healthy, skip to step 6 (recover the connection block) instead of re-cloning/re-starting.

## 4. Load documentation

Read the following to understand capabilities and deployment models before guiding the user:

- <https://raw.githubusercontent.com/Tencent/TencentDB-Agent-Memory/feat/server_team/README.md> — what the project is and its architecture
- <https://raw.githubusercontent.com/Tencent/TencentDB-Agent-Memory/feat/server_team/README.deployment.md> — Standalone vs Service deployment models
- <https://raw.githubusercontent.com/Tencent/TencentDB-Agent-Memory/feat/server_team/INSTALL.md> — install steps

Note: the repo's default work happens on the `feat/server_team` branch, not `main`; use it for the links above and for the clone in step 5 unless the user asks for a specific ref.

## 5. Clone and configure

```bash
git clone https://github.com/Tencent/TencentDB-Agent-Memory.git
cd TencentDB-Agent-Memory/deploy/global-images
cp .env.example .env
```

Open `.env` and fill in **two independent LLM parameter groups** (defaults reference DeepSeek but any OpenAI-compatible endpoint works):

- **`MEMORY_*` group** — the LLM used internally by `memory-core`/`memory-hub` for embeddings, extraction, and summarization:
  - `MEMORY_LLM_BASE_URL`, `MEMORY_LLM_API_KEY`, `MEMORY_LLM_MODEL`, `MEMORY_LLM_PROTOCOL` (default `openai`)
- **`PROXY_*` group** — the upstream LLM the proxy forwards the user's actual requests to:
  - `PROXY_UPSTREAM_URL`, `PROXY_UPSTREAM_API_KEY`, `PROXY_UPSTREAM_MODEL`

Ask the user for these credentials rather than inventing placeholder values — treat both API keys as secrets: never print them back, never commit `.env`, and don't paste them into chat.

Leave `MEMORY_CORE_PORT` (8420), `PANEL_PORT` (8125), `KNOWLEDGE_PORT` (8424), and `PROXY_PORT` (8096) at their defaults unless something local already binds them.

## 6. Start the services

```bash
./start-all.sh          # use existing local images
# or
PULL=1 ./start-all.sh   # pull the latest images first
```

The script validates every required variable up front, then starts services in order — `memory-core` first, waits for it to report healthy, then `memory-hub`, then `proxy` — so a misconfigured `.env` fails fast instead of leaving a half-started stack.

On success it prints a boxed block with the connection details, roughly:

```text
┌─ 通过 proxy 用 Claude Code ─────────────────────────────────────┐
│  export ANTHROPIC_BASE_URL=http://127.0.0.1:${PROXY_PORT}/claude-code/default
│  export ANTHROPIC_AUTH_TOKEN='${ADMIN_KEY}'
│  claude --model ${UPSTREAM_MODEL}
│
│  admin user_key 保存在: $ADMIN_KEY_FILE
└────────────────────────────────────────────────────────────────┘
```

`ADMIN_KEY` is a locally generated token for the proxy, not an Anthropic API key — it authenticates Claude Code to the local proxy, which then forwards to whatever `PROXY_UPSTREAM_*` points at.

## 7. Apply the connection block

**Confirm with the user before changing their shell environment** — `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` reroute all Claude Code traffic through the local proxy, which is a meaningful change to where their requests go.

If they confirm:

- Export the two variables in the current shell, or add them to their shell profile (`~/.zshrc`/`~/.bashrc`) if they want this persistent
- Note where the admin key file lives (`$ADMIN_KEY_FILE` from the printed block) so they can rotate/revoke it later
- Restart Claude Code (or run `claude --model ${UPSTREAM_MODEL}`) to pick up the new env vars

## 8. Update CLAUDE.md file

Use the path determined in step 1. Once the stack is confirmed healthy, update the appropriate CLAUDE.md file with the following content:

```markdown
### TencentDB Agent Memory is available for persistent agent memory

A local TencentDB Agent Memory stack (memory-core, memory-hub, proxy) runs via Docker Compose from `deploy/global-images`.

**Architecture**: conversations flow through capture → offload (raw logs to external files) → symbolic Mermaid canvas → L1 atom extraction → L2 scenario aggregation → L3 persona synthesis → recall (injected before the next turn).

**Ports**: memory-core `:8420`, panel `:8125`, knowledge `:8424`, proxy `:8096` (see `.env` for overrides).

**Operational commands**:
- View logs: `docker compose -f deploy/global-images/docker-compose.yml logs -f`
- Stop everything: `docker compose -f deploy/global-images/docker-compose.yml down`
- Panel UI: `http://127.0.0.1:8125`

**Usage notes**:
- Memory is only active while Claude Code's `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` point at the local proxy (`http://127.0.0.1:${PROXY_PORT}/claude-code/default`)
- The admin key authenticates to the local proxy only — it is not an Anthropic API key
- Intermediates (atoms, scenarios, persona) are stored as readable Markdown/Mermaid for white-box debugging
```

## 9. Verify

```bash
curl -s http://127.0.0.1:${PANEL_PORT:-8125}/health || true
docker ps --filter "name=memory"
```

Confirm the Panel UI loads at `http://127.0.0.1:8125` and that a short Claude Code exchange after step 7 produces entries visible there.

## 10. Teardown / management reference

```bash
docker compose -f deploy/global-images/docker-compose.yml down        # stop everything
docker compose -f deploy/global-images/docker-compose.yml down -v     # stop and wipe volumes (data loss)
docker compose -f deploy/global-images/docker-compose.yml logs -f     # tail logs
```
