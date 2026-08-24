---
name: ruflo-swarm
description: >-
  Use when coordinating multiple AI agents as a unified team, designing swarm
  topologies, setting up hierarchical queen/worker agent structures, building
  mesh agent networks, or enabling agents to share context and collaborate.
  Triggers on: "ruflo swarm", "agent swarm", "multi-agent team", "swarm
  topology", "hierarchical agents", "mesh agents", "queen agent", "Raft
  consensus agents", "coordinate agents as a team", "adaptive swarm".
---

# Ruflo Swarm — Multi-Agent Coordination

`ruflo-swarm` adds a coordination layer on top of ruflo-core, allowing multiple
AI agents to operate as a single unified team. Agents share context, reach
consensus, and divide work across three topology modes: **hierarchical**,
**mesh**, and **adaptive**.

## Install

```bash
# ruflo-core must be installed first
claude plugin install ruflo-swarm@ruflo
```

## Core Topologies

### Hierarchical (Queen + Workers)

```
          ┌─────────────┐
          │  Queen Agent │  ← strategic planner, holds global state
          └──────┬──────┘
         ┌───────┼───────┐
    ┌────▼────┐ ┌▼────┐ ┌▼────────┐
    │ Worker A│ │Work B│ │Worker C │
    └─────────┘ └──────┘ └─────────┘
    Consensus: Raft (leader election, quorum writes)
```

**When to use:** Tasks with a clear decomposition into parallel subtasks, where
one agent needs to hold final authority and synthesize results.

**Raft consensus** ensures all workers agree on shared state even if some crash
or disconnect. A quorum (majority) must acknowledge each state update before it
is committed.

### Mesh

```
   Agent A ←──→ Agent B
      ↕               ↕
   Agent D ←──→ Agent C
```

No central authority. Any agent can transfer control to any peer based on
predefined handoff protocols.

**When to use:** Exploratory tasks where requirements emerge mid-execution,
breadth-first search over a problem space, or tasks where no single agent
has full context.

### Adaptive

Starts as hierarchical for structure, dynamically re-topologizes to mesh when
the queen detects bottlenecks or high worker divergence.

**When to use:** Long-running complex pipelines where task shape is unknown
upfront.

## Swarm Initialization

### Via tool call (in a Claude Code session)

```
swarm_init({
  "topology": "hierarchical",
  "agents": [
    {"role": "queen", "model": "claude", "context": "You are the strategic planner."},
    {"role": "worker", "model": "claude", "context": "You handle code generation."},
    {"role": "worker", "model": "gemini", "context": "You handle documentation."},
    {"role": "worker", "model": "ollama", "context": "You handle local validation."}
  ],
  "consensus": "raft",
  "quorum": 2
})
```

### Via YAML manifest

Create `.ruflo/swarm.yaml` in your project:

```yaml
topology: hierarchical
consensus: raft
quorum: 2

agents:
  - role: queen
    model: claude
    system_prompt: |
      You are the strategic planner. Decompose tasks, assign to workers,
      aggregate results, and return the synthesized output.

  - role: worker
    label: code-gen
    model: claude
    system_prompt: |
      You write code. Receive a specification, produce working code,
      return it as a fenced code block with the file path in the fence label.

  - role: worker
    label: docs
    model: gemini
    system_prompt: |
      You write documentation. Receive code and context, produce clear
      Markdown documentation.

  - role: worker
    label: validator
    model: ollama
    system_prompt: |
      You validate outputs. Run checks, report pass/fail with reasons.
```

Then in Claude Code: `swarm_init --config .ruflo/swarm.yaml`

## Context Sharing

Workers share context through a **swarm context bus** — a structured JSON
object synchronized across all agents after each turn:

```json
{
  "swarm_id": "swarm_abc123",
  "turn": 7,
  "shared_state": {
    "task": "Build a REST API for user authentication",
    "completed": ["schema design", "route definitions"],
    "in_progress": ["JWT middleware"],
    "blocked": []
  },
  "worker_outputs": {
    "code-gen": "...last output...",
    "docs": "...last output..."
  }
}
```

Agents read `shared_state` before acting and write their output to
`worker_outputs.<label>` after acting.

## Consensus Patterns

### Weighted voting

Weight worker contributions by confidence:

```yaml
consensus:
  mode: weighted_vote
  weights:
    code-gen: 0.5      # most authoritative on code correctness
    docs: 0.3
    validator: 0.2
```

### Debate protocol

Force agents to critique each other before a final decision:

```yaml
consensus:
  mode: debate
  rounds: 2            # two rounds of adversarial critique
  final_arbiter: queen
```

Round 1: each worker proposes. Round 2: each worker critiques all others.
Queen synthesizes from critiqued proposals.

### Raft (default for hierarchical)

The queen is the Raft leader. Workers are followers. State updates require
acknowledgement from `quorum` agents before commit.

## Failure Handling

| Failure | Swarm response |
|---|---|
| Worker crashes | Queen re-assigns that worker's pending tasks to another worker |
| Queen crashes | Raft triggers leader election among workers |
| Quorum lost | Swarm pauses and alerts; resumes when quorum restores |
| Worker diverges | Queen detects via similarity score; sends correction prompt |

## Practical Workflow: Parallel Code Review

```markdown
## Task decomposition (queen does this automatically)
User request: "Review this PR for security, performance, and style issues"

Queen dispatches:
├── Worker: security-review  → grep for known vuln patterns, check deps
├── Worker: perf-review      → profile hot paths, flag O(n²) patterns  
└── Worker: style-review     → lint, naming conventions, docs completeness

Queen aggregates: deduplicate overlapping findings, rank by severity,
format unified review report.
```

## Iteration Limits and Guards

Always set limits to prevent runaway loops:

```yaml
swarm:
  max_turns_per_worker: 20
  max_total_turns: 100
  convergence_check: true        # halt if no new outputs in 3 consecutive turns
  sycophancy_detection: true     # halt if workers are just agreeing without reasoning
```
