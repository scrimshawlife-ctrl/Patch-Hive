# Engineering setup report — AI-native foundation

**Branch:** `chore/ai-engineering-foundation`  
**Baseline main:** `8e22fd2`  
**Date:** 2026-07-21  
**Scope:** tooling, docs, indexes, CI — **no application business-logic changes**

## Objectives met

| Objective | Status |
|-----------|--------|
| Local-first search & symbols | Done (rg, fd, bat, jq, yq, ctags, ast-grep) |
| Static analysis shortcuts | Documented + CI extended |
| Persistent local indexes | `.codebase-memory/` + `just memory` |
| Engineering docs | `docs/engineering/*` |
| AI retrieval docs | `AI_CONTEXT.md`, `SYSTEM_CONTEXT.md` |
| Task runners | `justfile` + Makefile targets |
| CI expansion | `engineering-quality.yml` |
| MCP template | `.mcp.json` + docs |
| `.gitignore` for indexes/cache | Updated |

## Host tool versions (this machine, OBSERVED)

| Tool | Version / note |
|------|----------------|
| ripgrep | 15.2.0 |
| fd | 10.4.2 |
| bat | 0.26.1 |
| jq | 1.8.2 |
| yq | v4.53.3 |
| ctags | Exuberant Ctags 5.8 |
| ruff | 0.15.21 (host); project pins 0.15.22 in pyproject) |
| uv | 0.11.29 |
| just | 1.56.0 |
| hyperfine | 1.20.0 |
| gitleaks | 8.30.1 |
| semgrep | 1.170.0 |
| ast-grep | 0.44.1 |
| codespell | 2.4.3 |
| tree-sitter CLI | **not on PATH** (lib may exist via brew); optional |
| Python | 3.14.6 host / CI 3.11–3.12 |
| Node | v22.23.1 |
| npm | 10.9.8 |

Install missing host tools (macOS):

```bash
brew install ripgrep fd bat jq yq universal-ctags uv just hyperfine gitleaks \
  tree-sitter codespell ast-grep
```

Linux: use distro packages or the same tools from official releases.

## Configuration added

| Path | Purpose |
|------|---------|
| `justfile` | setup, lint, test, coverage, index, memory, clean, validate, build, docs, scan |
| `Makefile` | setup-dev, lint, validate-local, index, memory, docs, coverage |
| `scripts/ai/rebuild_indexes.sh` | ctags + graph + hashes |
| `.codebase-memory/` | Local only (gitignored) |
| `docs/engineering/*` | Architecture, standards, testing, release, AI guide, map |
| `AI_CONTEXT.md` | LLM retrieval summary |
| `SYSTEM_CONTEXT.md` | Minimal-token system prompt block |
| `.mcp.json` | MCP server templates |
| `.github/workflows/engineering-quality.yml` | Extra lint/tests/docs/index smoke |
| `.gitignore` | Indexes, cache, artifacts, coverage caches |

## Repository intelligence

- **Symbol index:** ctags → `.codebase-memory/symbols/tags` (~4k lines after rebuild)
- **Module graph:** 20 backend packages, ~95 import edges
- **Content hashes:** key authority files for invalidation
- **Map doc:** `docs/engineering/repository_map.md`

## What was intentionally not done

| Item | Reason |
|------|--------|
| Live embedding model / vector DB | No stable zero-cost default; hash index instead |
| biome/prettier wholesale FE reformat | Would churn product diffs; ESLint+tsc already gated |
| Full-repo mypy strict | Expand gradually; CI already types core canon files |
| trufflehog | gitleaks already in security workflow |
| Application logic changes | Out of scope for foundation |

## Future recommendations

1. Pin **universal-ctags** in contributor docs (better TS support than Exuberant 5.8)
2. Optional **ast-grep** rules under `sgconfig.yml` for dual-path / self-confirm bans
3. Add **semgrep** custom rules for `USER_CONFIRMED` / payment flags
4. Wire **uv** lockfile for backend when ready for lockstep CI
5. Agent bootstrap: always load `SYSTEM_CONTEXT.md` first

## How agents should use this

```text
SYSTEM_CONTEXT.md → CURRENT_STATE.md → CONTINUATION.md → rg/fd → targeted reads
just memory   # after large refactors
just validate # before PR
```

## Authority

- No production deploy
- No payment activation
- Foundation is engineering ergonomics only
