# CURRENT_STATE

**Authoritative as of:** 2026-07-26  
**Branch pin:** `origin/main`  
**HEAD:** `9114aae08d368058b2bbe9cfde5c0e6e8e790f60` — #141 FE/seed type-safety + registry slug migration; pending ops beta-staging (Alembic entrypoint + `/health/ready`)  
**Recent work:** PDB explorer + catalog place-loop; #141 CI green-path; beta-staging ops slice (migrations-on-deploy, readiness probe, evidence re-pin).  
**Open issues:** #68 P0 Product Database residual; #58 P1 residual + P2 hygiene; #96 UI pages (**open**).  

**Alpha tag lineage:** `v0.3.0-alpha` (late alpha — **not** production)

### Recent merges (OBSERVED)

| PR | Result |
|----|--------|
| [#137](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/137) | Device Registry + catalog seed + `/products` explorer |
| [#138](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/138) | Case rematerialize power-rail preservation |
| [#139](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/139) | codebase-memory index |
| [#141](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/141) | FE/seed type-safety + registry slug Alembic + CI green-path |
| [#96](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/96) | Full product pages visual upgrade (**open**) |

**Campaign issue lineage:** [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** |
| Canonical domain | `backend/canon/` (+ design recipes, export fulfillment) |
| Design Engine flags | **Default off** — see [PATCHBOOK_STAGING_ENABLEMENT.md](docs/design/PATCHBOOK_STAGING_ENABLEMENT.md) |
| Alembic | Single head through `20260726_module_registry_slugs`; deploy via entrypoint `alembic upgrade head` |
| Health | `/health` liveness; `/health/ready` includes DB |
| Local Compose staging | `docker-compose.staging.yml` + receipts under `docs/evidence/STAGING_*` |
| Named staging host | Plan only — **NOT_PERFORMED** |
| Payments | Test-mode only |
| Production deploy | **Not performed** |
| Production readiness | **Not ready** (beta-staging engineering in progress) — [assessment](docs/evidence/PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md) · [matrix](docs/evidence/PRODUCTION_READINESS_MATRIX.md) · [delta](docs/evidence/PRODUCTION_READINESS_DELTA_2026-07-26.md) |

## Immediate continuation priorities

1. Land Alembic-on-deploy + `/health/ready` ops PR; re-pin matrix to merge SHA.
2. Operator: pick named staging host; optional domain cutover ([DOMAIN_CUTOVER_CHECKLIST.md](docs/evidence/DOMAIN_CUTOVER_CHECKLIST.md)).
3. Staging acceptance + Design Engine walkthrough (test payments only).
4. Dual-path thinning (F2+), P1/P2 hygiene per CONTINUATION.
5. #96 UI polish when CI green.

## Authority boundary

**Do not:** deploy production, enable live Stripe, charge users, or activate hardware without separate operator authorization.

## Doc index

| Doc | Use |
|-----|-----|
| [docs/ROADMAP.md](docs/ROADMAP.md) | Capability roadmap |
| [docs/CONTINUATION.md](docs/CONTINUATION.md) | Engineering backlog |
| [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) | Gate framework |
| [docs/evidence/PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md](docs/evidence/PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md) | Latest readiness narrative |
| [docs/FEATURE_FLAGS.md](docs/FEATURE_FLAGS.md) | Flags |
| [brand/README.md](brand/README.md) | Brand kit |

**2026-07-23 continuation:** Registry tables migrated + 704 manufacturers + 39 models populated from snapshot. Services/routes now DB-backed. Live API verified. See docs/evidence/PDB_DB_SEED_20260723.md
**2026-07-23 PDB continuation complete:** DB enriched (376 models + sample revisions/ports). Public Explorer built (directory, search, detail with live models). Registry slugs added to ModuleCatalog/Module for wiring. Basic admin POST /admin/manufacturers. Receipt: docs/evidence/PDB_EXPLORER_WIRING_20260723.md
**2026-07-23 further continuation:** Wired registry slugs into materialize_catalog_entry (and returns). Improved seeder fuzzy matching + re-seeded. Added test_catalog_materialize_registry.py (passed). Enhanced Registry explorer detail to surface links. Catalog now 376 rows all wired; materialization carries links.