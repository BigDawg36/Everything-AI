---
name: ruflo-rag-memory
description: >-
  Use when implementing hybrid retrieval-augmented generation, building agent
  memory systems with graph traversal, setting up vector stores with diversity
  ranking, or managing persistent knowledge bases for AI agents. Triggers on:
  "ruflo rag", "ruflo memory", "hybrid search agents", "graph RAG", "HNSW
  index", "agent memory retrieval", "diversity ranking retrieval", "ruflo
  knowledge base", "vector memory agent", "smart retrieval", "semantic agent
  memory".
---

# Ruflo RAG-Memory — Hybrid Retrieval + Graph Memory

`ruflo-rag-memory` gives agents a persistent, intelligent memory layer.
It combines **vector similarity search**, **graph traversal**, and
**diversity ranking** into a single retrieval pipeline — yielding more
relevant, less redundant results than plain vector RAG.

## Install

```bash
# Requires ruflo-core
claude plugin install ruflo-rag-memory@ruflo
```

## Architecture

```
Query
  │
  ├─► Vector search (HNSW)  ──► top-K semantically similar chunks
  │
  ├─► Graph hop traversal   ──► related entities reachable from top-K
  │
  └─► Diversity ranker       ──► MMR re-ranking to remove redundant results
                                           │
                                           ▼
                               Retrieved context (injected into agent)
```

### Why three stages?

| Stage | Problem it solves |
|---|---|
| HNSW vector search | Fast approximate nearest-neighbour; 3.2–4.7× faster than brute force at N=5 k |
| Graph hop traversal | Captures related facts not directly similar — e.g. "colleague of colleague" relationships |
| MMR diversity ranking | Prevents top-10 results from being 10 near-identical paraphrases |

## Core Tools (exposed by ruflo-core after plugin loads)

| Tool | Signature | Description |
|---|---|---|
| `memory_store` | `(key, value, metadata?)` | Embed and store a fact/document |
| `memory_query` | `(query, top_k?, filter?)` | Hybrid retrieve: vector + graph + MMR |
| `memory_graph_add` | `(entity_a, relation, entity_b, valid_from?, valid_until?)` | Add a typed edge to the knowledge graph |
| `memory_graph_query` | `(entity, hops?, relation_filter?)` | Traverse from entity, return subgraph |
| `memory_consolidate` | `()` | Merge duplicates, expire outdated facts, rebuild indexes |

## Storing Facts

### Simple key-value (auto-embedded)

```
memory_store({
  "key": "project/auth-decision",
  "value": "We chose JWT over sessions because the API is stateless and mobile clients need it.",
  "metadata": {
    "source": "architecture-meeting-2026-08-20",
    "tags": ["auth", "jwt", "decision"]
  }
})
```

### Document chunk (with temporal validity)

```
memory_store({
  "key": "spec/payment-api-v2",
  "value": "Payment endpoints accept Stripe or Braintree. Braintree is deprecated after 2026-12-01.",
  "metadata": {
    "valid_from": "2026-01-01",
    "valid_until": "2026-12-01",
    "tags": ["payments", "deprecation"]
  }
})
```

### Graph edge (relationship)

```
memory_graph_add({
  "entity_a": "mike.mizuha@gmail.com",
  "relation": "owns",
  "entity_b": "everything-ai-repo",
  "valid_from": "2025-01-01"
})
```

## Retrieving

### Semantic query

```
memory_query({
  "query": "What did we decide about authentication?",
  "top_k": 5
})
```

Returns chunks ranked by (relevance × diversity), with graph-enriched context
showing connected entities.

### Filtered query (temporal)

```
memory_query({
  "query": "payment API capabilities",
  "top_k": 8,
  "filter": {
    "valid_on": "2026-08-24",   // only facts valid today
    "tags": ["payments"]
  }
})
```

### Graph traversal

```
memory_graph_query({
  "entity": "everything-ai-repo",
  "hops": 2,                        // follow edges up to 2 hops out
  "relation_filter": ["owns", "contributes_to", "depends_on"]
})
```

Returns a subgraph showing the repository, its owner, its dependencies, and
contributors — useful for scoping an agent's context before a task.

## Multi-Layer Memory Architecture

ruflo-rag-memory implements all five memory layers:

```
Layer 1  Working memory     → agent context window (managed by ruflo-core)
Layer 2  Session memory     → ~/.ruflo/sessions/<id>/ (auto-created per session)
Layer 3  Long-term memory   → ~/.ruflo/memory/vectors/  (HNSW index, persistent)
Layer 4  Entity memory      → ~/.ruflo/memory/graph.db  (SQLite property graph)
Layer 5  Temporal KG        → validity periods on graph edges (time-travel queries)
```

### Performance (from Ruflo benchmarks)

| Retrieval mode | Accuracy (DMR) | Latency |
|---|---|---|
| ruflo-rag-memory (hybrid) | ~94% | 2.6 s |
| Plain vector RAG | ~65% | 0.8 s |
| Full-context baseline | ~92% | 28.9 s |

Hybrid retrieval hits near-full-context accuracy at 1/10th the latency.

## Agent Integration Pattern

Use `memory_query` at the start of each agent turn to ground the agent in
relevant past context:

```markdown
## Agent turn template (with memory)

1. Call memory_query("{{user_request}}", top_k=6)
2. Inject retrieved context at the TOP of the system prompt under "## Relevant memory"
3. Execute the task with grounded context
4. At end of turn: call memory_store to persist any new facts discovered
5. If new relationships found: call memory_graph_add
```

## Consolidation

Run `memory_consolidate` periodically (or when the index exceeds 10 k items):

```bash
# In Claude Code session:
memory_consolidate()

# Or schedule via ruflo background worker:
# workers.memory-consolidator.trigger = "items > 10000"
```

Consolidation:
1. Embeds newly added facts that haven't been indexed yet
2. Merges duplicate entries (cosine similarity > 0.97)
3. Marks expired facts (valid_until < today) as archived
4. Rebuilds the HNSW index for optimal search performance
5. Runs graph garbage collection (orphaned nodes, broken edges)

## Configuration

In `~/.ruflo/config.json`:

```json
{
  "memory": {
    "vector_dims": 1536,
    "hnsw": {
      "m": 16,
      "ef_construction": 200,
      "ef_search": 50
    },
    "mmr_lambda": 0.6,
    "graph_db": "~/.ruflo/memory/graph.db",
    "auto_consolidate_threshold": 10000
  }
}
```

`mmr_lambda`: 1.0 = pure relevance, 0.0 = pure diversity. 0.6 is the default
(slightly relevance-weighted).
