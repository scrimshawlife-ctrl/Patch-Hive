# Local Docker staging receipt

**Date:** 2026-07-21  
**Host:** macOS · Docker Desktop  
**Compose file:** `docker-compose.staging.yml`  
**Env file:** `.env.staging.local` (**gitignored**; secrets on disk only)  
**Authority:** OBSERVED local staging — not a public named host  

## Intent

Stand up staging-like stack (Postgres + FastAPI image + Vite FE) on localhost per operator preference “host locally in Docker for now.”

## Commands used

```bash
# Generate secrets into gitignored env (operator machine only)
export STAGING_SECRET_KEY="$(openssl rand -base64 32)"
export STAGING_DB_PASSWORD="$(openssl rand -base64 18 | tr -d '/+=' | head -c 24)"
# write .env.staging.local then:
docker compose -f docker-compose.staging.yml --env-file .env.staging.local up -d --build
```

## Results (OBSERVED)

```yaml
services:
  patchhive-staging-db:
    status: healthy
    ports: "5432:5432"
  patchhive-staging-backend:
    status: healthy
    ports: "8000:8000"
    health_body:
      status: healthy
      app: PatchHive
      version: "0.3.0-alpha.1"
      abx_core_version: "1.2"
  patchhive-staging-frontend:
    status: Up
    ports: "5173:5173"
    vite: ready

alembic:
  current: "20240930_patch_user_overlays (head)"

route_smoke:
  /health: 200
  /openapi.json: 200
  /docs: 200
  frontend http://localhost:5173/: 200

flags:
  ALLOW_PRODUCTION_PAYMENTS: "false"
  STRIPE_TEST_MODE: "true"
  ENABLE_LEGACY_*: "false"

named_public_domain: NOT_PERFORMED
production_deploy: NOT_PERFORMED
live_payments: NOT_PERFORMED
```

## Operator URLs (this machine)

| Surface | URL |
|---------|-----|
| App | http://localhost:5173 |
| API health | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |

## Stop / restart

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging.local stop
docker compose -f docker-compose.staging.yml --env-file .env.staging.local up -d
```

## Domain note

Public domain binding is **not** part of this receipt. See [DOMAIN_CUTOVER_CHECKLIST.md](DOMAIN_CUTOVER_CHECKLIST.md). Agents cannot configure registrar DNS without operator credentials and a public edge (VPS, tunnel, or PaaS).
