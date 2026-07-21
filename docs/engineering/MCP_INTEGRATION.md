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

## Local codebase-memory (not MCP)

Persistent **semantic/structure indexes** for this repo:

```bash
just memory
```

Outputs under `.codebase-memory/` (gitignored). Agents should load
`SYSTEM_CONTEXT.md` + graph JSON before deep exploration.

## sequential-thinking

If your host provides a sequential-thinking MCP, enable it for multi-step
plans. Not bundled as a dependency of PatchHive.

## Security

- Never commit API keys
- Prefer read-only filesystem roots in production agents
- Secret scanning remains in CI (`gitleaks` via security.yml)
