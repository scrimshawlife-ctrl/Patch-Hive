# AI agent guide (PatchHive)

## First 30 seconds (load order)

1. `SYSTEM_CONTEXT.md` — compressed facts  
2. `CURRENT_STATE.md` — exact SHA / alembic / deploy posture  
3. `docs/CONTINUATION.md` — what to build next  
4. `.codebase-memory/summaries/architecture_summary.json`  
5. Task-specific docs (VSI, CANON, PATCH_ENGINE)

## Hard constraints

- **No audio processing product work** (signal-type `audio` is OK as domain metadata)
- **No hardware control** / MIDI·CV activation
- **No production payments** unless flags + authority
- **Vision cannot self-confirm** inventory
- Prefer `NOT_COMPUTABLE` over invented hardware facts
- Do not merge/deploy without explicit operator intent when risky

## Search tools (use before bulk `read`)

```bash
rg -n "pattern" backend frontend
fd -e py inventory backend
# symbols
grep -n "^Symbol" .codebase-memory/symbols/tags | head   # or editor ctags jump
```

## Safe edit zones

| Safe for product work | Careful / dual-path |
|----------------------|---------------------|
| `backend/canon/` | `backend/racks`, `patches` routers |
| `backend/evidence/` | `backend/patchhive/` + repo-root `patchhive/` (HISTORICAL; see PATCHHIVE_IMPORT_TELEMETRY.md) |
| `frontend/src/pages` MVP | `frontend/src/legacy` |

## Validate before claiming done

```bash
just validate
# or
cd backend && pytest tests --ignore=tests/acceptance -q
cd frontend && npm test -- --run && npm run type-check
```

## Indexes

Regenerate after large refactors:

```bash
just memory
```

Do not commit `.codebase-memory/` binary/index noise (gitignored). Commit docs and scripts that *generate* indexes.
