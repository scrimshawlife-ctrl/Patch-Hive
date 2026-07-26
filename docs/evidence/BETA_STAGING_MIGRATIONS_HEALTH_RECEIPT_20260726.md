# Beta staging — migrations + readiness probe receipt

```yaml
date: "2026-07-26"
source_sha: 102e7c5e50ff871d3149bd6fa3f1b61db445782c  # #142 merge
compose_file: docker-compose.staging.yml
host: local Windows + Docker Desktop 4.81 / Engine 29.6.1
ports:
  api: 18000   # 8000 occupied by unrelated wslrelay
  db: 5433
  fe: 15173
payments:
  ALLOW_PRODUCTION_PAYMENTS: false
  STRIPE_TEST_MODE: true
result: PASS
```

## Commands

```bash
export STAGING_SECRET_KEY=… STAGING_DB_PASSWORD=…
export STAGING_API_PORT=18000 STAGING_DB_PORT=5433 STAGING_FE_PORT=15173
docker compose -f docker-compose.staging.yml up -d --build
curl -sf http://localhost:18000/health
curl -sf http://localhost:18000/health/ready
docker compose -f docker-compose.staging.yml exec -T backend python -m alembic current
```

## OBSERVED results

| Check | Result |
|-------|--------|
| Image build `patch-hive-pr-backend` | PASS |
| Postgres healthy | PASS (`postgres:15-alpine`) |
| Backend container healthy | PASS (Docker healthcheck → `/health/ready`) |
| `GET /health` | **200** `{"status":"healthy",…,"version":"0.3.0-alpha.1"}` |
| `GET /health/ready` | **200** `{"status":"healthy","database":"ok",…}` |
| Entrypoint migrations | PASS — full chain `legacy_foundation` → `20260726_module_registry_slugs` then `Migrations applied.` |
| `alembic current` | **`20260726_module_registry_slugs (head)`** |
| `alembic heads` | single head `20260726_module_registry_slugs` |
| Payments flags in compose | `ALLOW_PRODUCTION_PAYMENTS=false`, `STRIPE_TEST_MODE=true` |

## Notes

1. First bind of host `:8000` failed (`port is already allocated` / WSL `wslrelay` PID); smoke used **`STAGING_API_PORT=18000`**.
2. Docker Desktop on this host intermittently drops the `dockerDesktopLinuxEngine` named pipe mid-session; containers stayed up and HTTP probes remained valid when the engine pipe flaked.
3. On cold start, one migration attempt raced DB recovery (`Consistent recovery state has not been yet reached`); entrypoint retry / restart applied head successfully (idempotent upgrade).

## Code path verified

- `backend/docker-entrypoint.sh` → `python -m alembic upgrade head`
- No `create_all` / `init_db` on staging boot
- Readiness includes DB `SELECT 1` via `/health/ready`
