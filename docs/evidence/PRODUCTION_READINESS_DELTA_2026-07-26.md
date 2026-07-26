# Production readiness delta — 2026-07-26

```yaml
assessment:
  date: "2026-07-26"
  base_assessment: PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md
  prior_matrix_sha: de1fbcf31581de0d62b7584d00a632147b2abd4b
  main_at_write: 9114aae08d368058b2bbe9cfde5c0e6e8e790f60  # #141 merge; re-pin after this ops PR
  classification: late-alpha → beta-staging engineering slice
  authority_decision: NOT_GRANTED
  production_deployed: false
  production_payments_enabled: false
```

## What improved (this campaign)

| Change | Evidence |
|--------|----------|
| FE/seed type-safety on main | PR #141 |
| Registry slug Alembic revision | `20260726_module_registry_slugs` |
| Deploy path uses `alembic upgrade head` | `backend/docker-entrypoint.sh`, Dockerfiles, compose |
| App no longer calls `create_all` on every start | `main.py` lifespan + `ALLOW_CREATE_ALL` default false |
| DB readiness probe | `GET /health/ready` (503 if DB down) |
| CI green on type-safety + migration head | #141 CI |

## Still blocking GA / public domain

| Area | Status |
|------|--------|
| Named public staging host | NOT_PERFORMED |
| Domain / TLS / CORS cutover | Template only (`DOMAIN_CUTOVER_CHECKLIST.md`) |
| Backup/restore on durable env | NOT_COMPUTABLE |
| Observability / on-call / support | FAIL |
| Live payments | Forbidden without separate review |

## Beta staging minimum remaining

1. Operator picks host (Compose VPS / Render paid / Fly / Azure)  
2. Optional domain cutover credentials  
3. Staging acceptance walkthrough receipt on that host  
4. Design Engine flag enablement only on staging with test payments  

**Hard rule:** `ALLOW_PRODUCTION_PAYMENTS=false`, `STRIPE_TEST_MODE=true`.
