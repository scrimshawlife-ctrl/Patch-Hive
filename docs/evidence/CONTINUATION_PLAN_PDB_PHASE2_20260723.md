# Continuation Plan: Product Database P0 - Phase 2 (Registry Integration)

**Date:** 2026-07-23  
**Source SHA:** 3d86ee1e5c20909f005c3688f70afd0f66256aa3  
**Previous:** Phase 1 complete (models, services, routes, seed ingestion, snapshot, receipts). See PDB_P0_PHASE1_REGISTRY_FOUNDATION_20260723.md and CONTINUATION_PLAN_PDB_P0_20260723.md.

## Goals for Phase 2
- Wire registry into the running application (models registration + API routes).
- Create Alembic migration for the new Device Registry tables.
- Improve ingestion to produce richer, more usable data (better model population, aliases, basic provenance).
- Add minimal test coverage for the registry layer.
- Produce updated snapshot + coverage receipt with higher fidelity.
- Minimal frontend hook (API client + stub page or integration point).
- Update state docs and ensure local verification passes (ruff + pytest).

**Success Criteria:**
- `GET /api/registry/manufacturers` and related endpoints return data from snapshot or DB.
- Alembic head includes registry tables.
- Ingestion produces >300 models with non-trivial coverage.
- New receipt generated.
- No regressions in existing catalog/module tests.
- All changes ruff-clean and import cleanly.

## Phased Work

### Phase 2.1: App Integration (Wire Models + Router)
- Import registry models in `backend/main.py` (for SQLAlchemy registration).
- Mount `registry.routes.router` (prefix `/api/registry`, tags=["registry"]).
- Ensure `/health` or root reflects registry availability if useful.
- Verify with local uvicorn or test client.

**Exit:** Endpoints respond; models registered without errors.

### Phase 2.2: Database Migration
- Generate Alembic migration for all new registry tables (manufacturers, device_families, device_models, device_revisions, ports, controls, capabilities).
- Run `alembic upgrade head` locally (using sqlite for speed if needed).
- Add basic model fixtures or seed in tests/conftest if appropriate.

**Exit:** Migration file created; `alembic heads` shows new revision; tables can be created.

### Phase 2.3: Ingestion Hardening & Richer Data
- Enhance `scripts/ingest_registry_from_seeds.py`:
  - Better parsing of `catalog_modules` (HP, type, brand).
  - Add simple alias handling and provenance.
  - Support multiple seeds.
  - Write richer snapshot (include some revisions/ports stubs if data available).
- Re-run ingestion and update `*_latest.json`.
- Generate new coverage stats.

**Exit:** Snapshot has meaningful models with HP data; coverage >5% if possible from current seeds.

### Phase 2.4: Tests & Verification
- Add `tests/unit/test_registry_models.py` (basic CRUD-like structure tests, snapshot roundtrip).
- Add `tests/api/test_registry_api.py` (using test client against mounted routes).
- Run full relevant pytest suite locally.
- Re-run ruff on changed paths.
- Update inventory receipt or create Phase 2 receipt.

**Exit:** New tests pass; overall relevant test count does not regress.

### Phase 2.5: Minimal Frontend & Docs
- Add basic types and api client calls in `frontend/src/lib/api.ts` and types.
- Create stub `frontend/src/pages/Products.tsx` or extend Modules to link to registry.
- Update `CURRENT_STATE.md`, `ROADMAP.md` (if needed), and create Phase 2 execution receipt.
- Document next steps (live DB population, explorer UI polish, admin tools).

**Exit:** API calls from FE possible (even if mocked); docs reflect reality.

## Execution Notes
- Work locally first (use .venv for backend tests).
- Prefer small, reviewable changes.
- Fail closed on unknowns; preserve compatibility with ModuleCatalog.
- After each phase, run local verification and update the plan with "DONE" markers.
- Docker issues noted — prioritize local path for now.

## Next After Phase 2
- Full DB seed with real snapshot.
- Public Product Explorer UI (manufacturer directory, search, detail pages).
- Vision/inventory integration using registry IDs.
- Admin registry workbench.

**Status:** Drafted. Now executing to completion.


**EXECUTION COMPLETE** as of 2026-07-23T22:31:50.790732Z
All phases 2.1-2.5 executed. Local verification passed. See PDB_P0_PHASE2_INTEGRATION_20260723.md for receipt.