# Contributing

## Setup

```bash
# Host tools (macOS example)
brew install ripgrep fd bat jq yq universal-ctags uv just hyperfine gitleaks semgrep ast-grep tree-sitter codespell

# Clone
git clone https://github.com/scrimshawlife-ctrl/Patch-Hive.git
cd Patch-Hive

# Python backend (uv preferred)
cd backend && uv venv && source .venv/bin/activate
uv pip install -e '.[dev]'

# Frontend
cd ../frontend && npm ci

# Local indexes for agents
just index
```

Or: `just setup` / `make setup-dev`.

## Workflow

1. Branch from `main`
2. Keep changes scoped; update docs when authority changes
3. Run `just validate` (or `make validate-local`) before PR
4. Open PR; wait for CI (Backend Tests, Code Quality, Security)
5. Do **not** enable production payments or deploy without operator authority

## Authority docs

| Doc | Use |
|-----|-----|
| `CURRENT_STATE.md` | Exact HEAD, alembic, deploy posture |
| `docs/CONTINUATION.md` | Ordered next work |
| `docs/CANON.md` | Publishing + bridge canon |
| `AI_CONTEXT.md` / `SYSTEM_CONTEXT.md` | LLM retrieval |

## AI agents

Read `docs/engineering/AI_AGENT_GUIDE.md` and load `SYSTEM_CONTEXT.md` first to save tokens.
