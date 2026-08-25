---
name: ruflo-core
description: >-
  Use when setting up the ruflo agent harness, registering the core MCP server,
  checking server health, discovering available plugins, or bootstrapping any
  ruflo-based multi-agent workflow. Triggers on: "set up ruflo", "ruflo server",
  "ruflo health check", "plugin discovery", "ruflo infrastructure",
  "initialize ruflo", "ruflo harness", "agent harness setup".
---

# Ruflo Core — Agent Harness Foundation

Ruflo is an execution layer that follows the principle **Agent = Model + Harness**.
The model generates reasoning; `ruflo-core` provides the infrastructure — server
lifecycle, health monitoring, and plugin discovery — on top of which all other
ruflo plugins run.

## Core Concept

```
Model (Claude / GPT / Gemini / Ollama …)
    +
Harness (ruflo-core: tools, memory, loops, sandboxes, controls)
    =
Agent capable of coordinated, persistent, multi-provider work
```

## Responsibilities

| Responsibility | What it does |
|---|---|
| **Server lifecycle** | Starts/stops the ruflo MCP server process; exposes tools under `mcp__plugin_ruflo-core_ruflo__*` |
| **Health checks** | Continuous monitoring of registered plugins; reports degraded/down components |
| **Plugin discovery** | Scans installed plugins, loads their manifests, wires their tools into the active session |
| **Multi-provider routing** | Routes model calls to Claude, GPT, Gemini, Cohere, or Ollama based on task and cost policy |
| **Background workers** | Manages up to 12 auto-triggered background QA workers |

## Setup Workflow

### 1. Install (CLI)

```bash
# Add the ruflo marketplace
claude plugin marketplace add ruvnet/ruflo

# Install the foundation first — all other plugins depend on it
claude plugin install ruflo-core@ruflo
```

After installation, `ruflo-core` registers its MCP server. The following bare
tools become available in Claude Code sessions:

- `memory_store` — write a key/value or embedding into ruflo's vector store
- `swarm_init` — bootstrap a swarm topology (delegates to ruflo-swarm)
- `plugin_list` — enumerate installed ruflo plugins and their health status
- `health_check` — poll the server and return component statuses

### 2. Verify

```bash
# Inside a Claude Code session, after installation:
/mcp  # confirm ruflo-core appears in the MCP server list
```

Expected output includes an entry like:
```
ruflo-core   connected   tools: memory_store, swarm_init, plugin_list, health_check
```

### 3. Install dependent plugins

```bash
claude plugin install ruflo-swarm@ruflo
claude plugin install ruflo-rag-memory@ruflo
claude plugin install ruflo-neural-trader@ruflo
```

## Configuration Reference

Ruflo reads `~/.ruflo/config.json` (created on first run). Key fields:

```json
{
  "server": {
    "port": 7890,
    "log_level": "info"
  },
  "providers": {
    "default": "claude",
    "fallback": ["gpt", "gemini"]
  },
  "workers": {
    "max_background": 12,
    "auto_qa": true
  },
  "plugins": {
    "discovery_path": "~/.ruflo/plugins"
  }
}
```

## Multi-Provider LLM Routing

ruflo-core routes tasks across providers based on cost, latency, and capability:

```
Task arrives
    │
    ├── Reasoning / code → Claude (primary)
    ├── Fast summarization → Gemini Flash (secondary)
    ├── Offline / privacy → Ollama (local)
    └── Fallback chain if primary is unavailable
```

Declare per-task routing in your workflow:

```markdown
## Provider hint
preferred_provider: claude
fallback: [gemini, ollama]
max_cost_usd_per_call: 0.05
```

## Background Workers

ruflo-core launches up to 12 background workers for quality assurance:

| Worker | Trigger | Action |
|---|---|---|
| lint-check | on file write | runs linter, posts findings |
| test-runner | on code change | executes changed test files |
| security-scan | on dependency change | audits new packages |
| context-pruner | context > 80% full | summarizes oldest turns |
| memory-consolidator | memory > 10k items | merges and deduplicates |
| health-monitor | every 60 s | polls all registered plugins |

## Troubleshooting

**Server won't start**
```bash
ruflo server status   # check process
ruflo server logs     # tail the server log
ruflo server reset    # wipe state and restart
```

**Plugin not discovered**
1. Confirm it was installed with `claude plugin install <name>@ruflo`
2. Run `plugin_list` — look for status `error` with a reason
3. Check `~/.ruflo/plugins/<name>/manifest.json` exists and is valid JSON

**Tool name conflicts**
If another MCP server also registers `memory_store`, scope calls with the
fully-qualified name: `mcp__plugin_ruflo-core_ruflo__memory_store`.
