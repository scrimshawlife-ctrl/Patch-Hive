# Staging backup/restore drill receipt

```yaml
date: "2026-07-26"
method: scripts/staging/smoke.ps1 (or smoke.sh)
compose: docker-compose.staging.yml
source_sha_base: 07340d9  # re-pin after this PR merges
payments: fail-closed
```

## Procedure (automated)

1. Start staging stack (Alembic head via entrypoint).  
2. `GET /health` + `GET /health/ready` → healthy / `database: ok`.  
3. `alembic current` → `20260726_module_registry_slugs`.  
4. `pg_dump -Fc` of `patchhive` → host `tmp/staging-smoke/patchhive-staging.dump`.  
5. `pg_restore -l` includes TABLE entries.  
6. Create `patchhive_restore_smoke`, `pg_restore` into it, assert `alembic_version` matches head.  
7. Drop restore database (live staging DB untouched).

## Status

| Step | Class |
|------|--------|
| Script checked in | OBSERVED (this PR) |
| Full drill executed on Windows Docker Desktop | **PASS** (2026-07-26) |

### OBSERVED results

| Check | Result |
|-------|--------|
| `/health` + `/health/ready` | 200 / `database: ok` |
| `alembic current` | `20260726_module_registry_slugs (head)` |
| `pg_dump -Fc` size | ~194 KB |
| `pg_restore` side DB `alembic_version` | `20260726_module_registry_slugs` |

Re-run:

```powershell
powershell -File scripts/staging/smoke.ps1
```

**Authority:** local staging only — not production backup policy.
