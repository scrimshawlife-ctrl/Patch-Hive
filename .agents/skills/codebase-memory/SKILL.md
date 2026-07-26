---
name: codebase-memory
description: Index and query PatchHive via DeusData codebase-memory-mcp knowledge graph.
triggers:
  - index this project
  - index with codebase-memory skill
  - show me the architecture
  - find callers of
  - trace the call graph
---

# Codebase Memory (PatchHive)

Use **codebase-memory-mcp** for structural repository intelligence before broad `rg`/`Read` sweeps.

## Index (full + persistent)

```bash
export PATH="$HOME/.local/bin:$PATH"
# Install once: pip install codebase-memory-mcp && codebase-memory-mcp install -y
codebase-memory-mcp cli index_repository \
  --repo-path "$(git rev-parse --show-toplevel)" \
  --mode full \
  --name patch-hive-full \
  --persistence true
```

Writes `.codebase-memory/graph.db.zst` + `artifact.json` (shareable). Also refresh lightweight indexes with `just memory` when needed.

## Query first

| Intent | Tool / CLI |
|--------|------------|
| Status | `index_status --project patch-hive-full` |
| Symbol search | `search_graph --name-pattern '...'` |
| Architecture | `get_architecture --aspects overview` |
| Call path | `trace_path` |
| Routes / Cypher | `query_graph` / `search_graph` |

Project name: **`patch-hive-full`**.

## Fallback

If MCP/binary unavailable: `SYSTEM_CONTEXT.md` → `rg`/`fd` → `just memory` local indexes.
