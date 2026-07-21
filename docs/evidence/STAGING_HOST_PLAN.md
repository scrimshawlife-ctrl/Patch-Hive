# Named staging host plan

**Date:** 2026-07-21  
**Baseline main:** `7727908` (post PR #82 legacy_pipeline unit migration)  
**Authority:** ops design + local Compose OBSERVED; **no cloud host provisioned in this pass**  
**Payments:** `ALLOW_PRODUCTION_PAYMENTS=false` always on staging  

## Intent

Define how to stand up a **named non-prod** environment (URL + secrets + Postgres) without claiming production readiness. Local Compose drill already PASSed ([STAGING_COMPOSE_RECEIPT.md](STAGING_COMPOSE_RECEIPT.md)).

## Host options (operator pick required)

| Option | Pros | Cons | When to pick |
|--------|------|------|--------------|
| **A. Compose on operator VPS** | Closest to monorepo; cheap; uses `docker-compose.staging.yml` | Operator owns TLS/DNS/backups | Default if you already run Docker hosts |
| **B. Render** | Existing `docs/RENDER_DOCKER.md` path | Free tier sleeps; env drift | Quick public URL |
| **C. Fly.io / Railway** | Snippets present | Less documented here | If team already uses Fly/Railway |
| **D. Azure** | Full template docs | Heaviest; overkill for staging | Enterprise only |

**Default recommendation (SPECULATIVE until operator confirms):** **A — Compose on a private VPS** named `staging.patchhive.<operator-domain>` (or private IP only).

## Required secrets (staging)

| Variable | Staging rule |
|----------|----------------|
| `DATABASE_URL` | Managed Postgres 15 or Compose `db` |
| `SECRET_KEY` | ≥32 random bytes; **not** dev default |
| `CORS_ORIGINS` | Exact frontend origin(s) |
| `STRIPE_TEST_MODE` | `true` |
| `ALLOW_PRODUCTION_PAYMENTS` | `false` |
| All `ENABLE_LEGACY_*` | `false` |
| `ENABLE_LEGACY_PATCHBOOK_DEBIT` | `false` |
| Vision cloud keys | **omit** (mock only) |

## Gate checklist (before sharing staging URL)

Copy of [OPERATIONS.md](../OPERATIONS.md) release gates, plus:

1. [ ] `alembic current` == `20240930_patch_user_overlays (head)`  
2. [ ] `GET /health` → `status: healthy`  
3. [ ] Acceptance suite against staging Postgres: `pytest tests/acceptance -q`  
4. [ ] Ledger reconcile / no double-debit smoke  
5. [ ] Manual a11y protocol ([ACCESSIBILITY.md](../ACCESSIBILITY.md))  
6. [ ] Backup/restore drill of staging DB (record receipt)  
7. [ ] No production payment keys present  

## Local staging-like Compose (this repo)

```bash
# Production-like local stack (no code bind-mounts, no --reload)
docker compose -f docker-compose.staging.yml up -d --build
curl -sf http://localhost:8000/health
docker compose -f docker-compose.staging.yml exec -T backend alembic current
```

Class: **local OBSERVED** when run on a laptop — still **not** a named multi-tenant host.

## Status (this campaign)

| Claim | Status |
|-------|--------|
| Local Compose db+backend healthy | **PASS** (prior receipt) |
| `docker-compose.staging.yml` checked in | **THIS PR** |
| Operator-chosen public/private hostname | **NOT_PERFORMED** — blocked on host pick |
| Production deploy | **NOT_PERFORMED** |

## Operator action required

Reply with **A/B/C/D** (or hostname). Until then agents must not invent cloud credentials or claim staging is live.
