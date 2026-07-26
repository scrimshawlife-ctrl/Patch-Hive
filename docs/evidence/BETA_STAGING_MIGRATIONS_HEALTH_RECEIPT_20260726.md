# Beta staging — migrations + readiness probe receipt

```yaml
date: "2026-07-26"
base_sha: 9114aae08d368058b2bbe9cfde5c0e6e8e790f60
branch: ops/beta-staging-migrations-health
payments:
  ALLOW_PRODUCTION_PAYMENTS: false
  STRIPE_TEST_MODE: true
```

## Code changes (OBSERVED)

| Item | Status |
|------|--------|
| `docker-entrypoint.sh` runs `python -m alembic upgrade head` | Implemented |
| `backend/Dockerfile` + `Dockerfile.backend` ENTRYPOINT | Implemented |
| `main.py` lifespan no longer always `init_db()` | Implemented (`ALLOW_CREATE_ALL` default false) |
| `GET /health` liveness | Kept process-only |
| `GET /health/ready` DB `SELECT 1` | Implemented; 503 on failure |
| Compose/Render/Fly health → `/health/ready` | Updated |
| API test for ready | `test_health_ready` |

## Staging compose smoke

| Step | Result |
|------|--------|
| `docker compose -f docker-compose.staging.yml up -d --build` | **NOT_PERFORMED** in agent session (Docker availability not assumed) |
| `curl /health/ready` | **NOT_PERFORMED** (compose not run) |
| `alembic current` → `20260726_module_registry_slugs` | **NOT_PERFORMED** (compose not run); CI backend-tests apply Alembic against Postgres |

Operators: run compose smoke from [OPERATIONS.md](../OPERATIONS.md) and append a dated note here when complete.

## CI

Re-validate on the merge PR: backend-tests, code-quality, engineering, security.
