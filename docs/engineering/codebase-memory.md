# Codebase memory layout

Two complementary index layers live under `.codebase-memory/`:

## 1. DeusData codebase-memory-mcp (knowledge graph)

Primary agent skill / MCP graph. Prefer this for structural queries (callers, routes, architecture).

| Path | Purpose |
|------|---------|
| `graph.db.zst` | Compressed knowledge graph (team-shared; commit when refreshed) |
| `artifact.json` | Index metadata (project name, node/edge counts, commit SHA) |
| `.gitattributes` | `merge=ours` for the compressed artifact |

### Install

```bash
pip install codebase-memory-mcp
sudo apt install zstd   # Linux — required for persistence export
codebase-memory-mcp install -y
# or copy .cursor/mcp.json.example → ~/.cursor/mcp.json and set binary path
```

### Index (full + persistent)

```bash
export PATH="$HOME/.local/bin:$PATH"
codebase-memory-mcp cli index_repository \
  --repo-path "$(git rev-parse --show-toplevel)" \
  --mode full \
  --name patch-hive-full \
  --persistence true
```

Via agent (MCP wired): say **"Index this project"** / **"index with codebase-memory skill"**.

### Query examples

```bash
codebase-memory-mcp cli index_status --project patch-hive-full
codebase-memory-mcp cli search_graph --project patch-hive-full --name-pattern 'VisionEvidenceProvider'
codebase-memory-mcp cli get_architecture --project patch-hive-full --aspects overview
```

Or use MCP tools: `search_graph`, `trace_path`, `get_architecture`, `get_callers`, `query_graph`.

Latest committed artifact (this workspace): see `.codebase-memory/artifact.json`.

## 2. Lightweight local indexes (`just memory`)

Regenerable ctags / file lists / coarse import graph (no MCP required):

| Path | Purpose |
|------|---------|
| `symbols/tags` | ctags symbol index |
| `graph/module_graph.json` | package import graph |
| `embeddings/content_hashes.json` | file content hashes for invalidation |
| `summaries/architecture_summary.json` | compact architecture facts |
| `indexes/*` | file lists, routers, TODO hotspots |

```bash
just memory
bash scripts/ai/rebuild_indexes.sh
```

### Host requirement: Universal Ctags

Symbol indexing for layer 2 requires **Universal Ctags** (or Exuberant with `--languages`).  
GNU Emacs `ctags`/`etags` shares the binary name but is **not** supported — the rebuild script detects and skips it instead of failing.

```bash
# Debian/Ubuntu
sudo apt install universal-ctags ripgrep fd-find

# macOS
brew install universal-ctags ripgrep fd
```

No paid embedding API is required for either layer.
