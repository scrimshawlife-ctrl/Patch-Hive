# Staging Compose drill receipt

**Date:** 2026-07-21  
**Host:** macOS (local Docker Desktop)  
**Scope:** `docker compose` db + backend health/migrations smoke (not production)  
**Authority:** OBSERVED local staging only — no production deploy, no live payments  

## Intent

Clear residual `NOT_COMPUTABLE` for full-stack Compose readiness by bringing up
Postgres + FastAPI via project `docker-compose.yml` and recording health,
Alembic head, and route smoke.

## Environment

| Item | Value | Class |
|------|--------|--------|
| Docker daemon | Docker Desktop 29.6.2 (`desktop-linux`) | OBSERVED |
| Compose file | `docker-compose.yml` | OBSERVED |
| Services started | `db`, `backend` (`docker compose up -d db backend`) | OBSERVED |
| Frontend-dev | already present / Up on `:5173` (not required for this receipt) | OBSERVED |
| Production deploy | not performed | NOT_PERFORMED |
| Live Stripe / payments | not exercised | NOT_PERFORMED |

## Results

```yaml
compose_ps:
  patchhive-db:
    image: postgres:15-alpine
    status: healthy
    ports: "5432:5432"
  patchhive-backend:
    image: patch-hive-backend
    status: healthy
    ports: "8000:8000"
  class: OBSERVED

health:
  url: "http://localhost:8000/health"
  http: 200
  body:
    status: healthy
    app: PatchHive
    version: "1.0.0"
    abx_core_version: "1.2"
  class: OBSERVED

alembic:
  command: "docker compose exec -T backend alembic current"
  current: "20240930_patch_user_overlays (head)"
  class: OBSERVED

database:
  command: "docker compose exec -T db psql -U patchhive -d patchhive -c '\\dt'"
  notes:
    - postgres reachable as user patchhive / db patchhive
    - tables include image_assets, classification_evidence_records,
      rig_revisions, runs, patch_user_overlays, racks, patches, etc.
  class: OBSERVED

route_smoke:
  /health: 200
  /openapi.json: 200
  /docs: 200
  /: 200
  class: OBSERVED

production_deploy: NOT_PERFORMED
live_payments: NOT_PERFORMED
full_acceptance_pytest_in_compose: NOT_RUN  # optional follow-on; unit/acceptance already green via CI/testcontainers
```

## Commands (reproducible)

```bash
# Ensure Docker Desktop is running
docker compose up -d db backend
curl -sf http://localhost:8000/health
docker compose exec -T backend alembic current
docker compose exec -T db psql -U patchhive -d patchhive -c '\dt'
```

## Decision

| Claim | Status |
|-------|--------|
| Local Compose stack (db + backend) boots healthy | **PASS** (OBSERVED) |
| Migrations at expected head on compose Postgres | **PASS** (`20240930_patch_user_overlays`) |
| Ready for production / multi-tenant staging | **NOT_CLAIMED** |

## Residual

- Full multi-service acceptance (`pytest tests/acceptance` inside compose network) not re-run here; prior receipt used testcontainers.
- Frontend-dev container not part of the health gate for this drill.
- No production secrets or external providers exercised.
