# MCP integration

## Config file

Repository template: `.mcp.json` (server command hints).

Host agents (Grok Build, Claude Code, Cursor, etc.) load MCP servers from user
config; merge entries carefully.

## Recommended servers

| Server | Role | Status |
|--------|------|--------|
| filesystem | Read/write repo files | Template in `.mcp.json` |
| github | PRs/issues | Needs `GITHUB_TOKEN` |
| memory | Cross-session notes | Template |
| fetch | Public HTTP docs | Template |
| git | Git operations | Optional; CLI `git`/`gh` often enough |

## Codebase memory MCP (DeusData)

Primary structural index. Install `codebase-memory-mcp`, then:

```bash
codebase-memory-mcp install -y
# or copy .cursor/mcp.json.example and set the absolute binary path
codebase-memory-mcp cli index_repository \
  --repo-path "$(git rev-parse --show-toplevel)" \
  --mode full --name patch-hive-full --persistence true
```

Agent trigger: **"Index this project"** / skill `.agents/skills/codebase-memory/`.  
Details: [codebase-memory.md](codebase-memory.md).

## Lightweight local indexes (`just memory`)

```bash
just memory
```

Writes ctags/file-list summaries under `.codebase-memory/` (mostly gitignored;
`graph.db.zst` + `artifact.json` are the shareable MCP artifact).

## sequential-thinking

If your host provides a sequential-thinking MCP, enable it for multi-step
plans. Not bundled as a dependency of PatchHive.

## Security

- Never commit API keys
- Prefer read-only filesystem roots in production agents
- Secret scanning remains in CI (`gitleaks` via security.yml)
