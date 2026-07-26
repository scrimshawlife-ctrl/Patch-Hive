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
| Compose smoke + backup/restore drill | #145 |
| Acceptance suite on compose Postgres | #146 · 11 PASS |
| Design Engine staging walkthrough | #147 · export `status=succeeded` |
| Unified test runner + CI acceptance gate | #148 · `acceptance-tests.yml` |
| Dual-path F2 thin `GET /api/canon/rigs` | F2_CANON_RIGS_READ_ADAPTER.md |

## Still blocking GA / public domain

| Area | Status |
|------|--------|
| Named public staging host | NOT_PERFORMED |
| Domain / TLS / CORS cutover | Template only (`DOMAIN_CUTOVER_CHECKLIST.md`) |
| Backup/restore on durable env | NOT_COMPUTABLE (local compose drill PASS only) |
| Observability / on-call / support | FAIL |
| Live payments | Forbidden without separate review |

## Beta staging minimum remaining

1. Operator picks host (Compose VPS / Render paid / Fly / Azure)  
2. Optional domain cutover credentials  
3. Staging acceptance walkthrough receipt on that host  
4. ~~Design Engine flag enablement on local staging~~ **DONE** (#147; named host still open)  
5. Dual-path F4/F5 when FE capacity  

**Hard rule:** `ALLOW_PRODUCTION_PAYMENTS=false`, `STRIPE_TEST_MODE=true`.
