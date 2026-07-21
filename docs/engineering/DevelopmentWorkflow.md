# Development workflow

## Day-to-day

```text
pull main → branch → implement → just validate → PR → CI → review → merge
```

## Commands (preferred)

| Intent | Command |
|--------|---------|
| Install deps + index | `just setup` |
| Lint | `just lint` |
| Test | `just test` |
| Coverage | `just coverage` |
| Rebuild AI indexes | `just index` / `just memory` |
| Full local validate | `just validate` |
| Build FE | `just build` |
| Docs list | `just docs` |
| Clean caches | `just clean` |

Make targets mirror many of these (`make help`).

## Local stack

```bash
make dev          # docker compose up
make test         # in-compose pytest + FE tests
make db-migrate   # when using compose DB
```

## Token-efficient agent workflow

1. Load `SYSTEM_CONTEXT.md` (~compressed)
2. Load `AI_CONTEXT.md` if more detail needed
3. Search with `rg` / `fd` / ctags before reading whole files
4. Use `.codebase-memory/graph/module_graph.json` for ownership
5. Prefer targeted pytest paths over full suite while iterating

## Dual-path caution

Inventory UI still uses `/api/racks` etc. Canon exports/credits use `/api/canon/*`. Do not delete dual paths without a green vertical slice.
