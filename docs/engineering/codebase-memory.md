# Codebase memory layout

Local directory `.codebase-memory/` (gitignored) stores regenerated indexes:

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

## Host requirement: Universal Ctags

Symbol indexing requires **Universal Ctags** (or Exuberant with `--languages`).  
GNU Emacs `ctags`/`etags` shares the binary name but is **not** supported — the rebuild script detects and skips it instead of failing.

```bash
# Debian/Ubuntu
sudo apt install universal-ctags ripgrep fd-find

# macOS
brew install universal-ctags ripgrep fd
```

No paid embedding API is required. Optional local embedding models may write under `embeddings/` later.
