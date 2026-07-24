# CURRENT_STATE

**Authoritative as of:** 2026-07-23  
**Branch pin:** `origin/main`  
**HEAD:** `3d86ee1e5c20909f005c3688f70afd0f66256aa3` — feat(ui): multi-module batch place with contiguous HP pack (#136)  
**Recent work:** PDB-01 catalog inventory receipt (see docs/evidence/CATALOG_INVENTORY_RECEIPT_20260723.md); active ModuleCatalog + /catalog/* + materialize (HP fail-closed) + Modules UI + batch place integration; GalleryRevision append-only.  
**Open issues:** #68 P0 Product Database/Device Registry/Explorer (inventory step complete); #58 P1 residual + P2 hygiene.  

**PDB Progress (this session):** Phase 1 complete — full registry models, seed ingestion (704 brands / 376 models), services, route stubs, snapshot artifacts, and new evidence receipt (PDB_P0_PHASE1_REGISTRY_FOUNDATION_20260723.md).


**PDB Phase 2 (this session):** Registry wired into main.py, Alembic migration created, tests added, ingestion re-run, local verification green (ruff + pytest). See PDB_P0_PHASE2_INTEGRATION_20260723.md

**Alpha tag lineage:** `v0.3.0-alpha` (late alpha — **not** production)

### Recent merges (OBSERVED)

| PR | Result |
|----|--------|
| [#86](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/86)–[#88](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/88) | F3 dual-write audit; local staging receipt; Cyber Hive brand kit |
| [#89](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/89)–[#94](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/94) | Design system + Design Engine foundation → pack download |
| [#95](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/95) | Login Cyber Hive auth gate |
| [#96](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/96) | Full product pages visual upgrade (**open**) |

**Campaign issue lineage:** [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** |
| Canonical domain | `backend/canon/` (+ design recipes, export fulfillment) |
| Design Engine flags | **Default off** — see [PATCHBOOK_STAGING_ENABLEMENT.md](docs/design/PATCHBOOK_STAGING_ENABLEMENT.md) |
| Alembic | Chain includes `20260721_design_engine_export_columns` + `20260721_user_style_recipes` |
| Local Compose staging | Receipts under `docs/evidence/STAGING_*` |
| Named staging host | Plan only — **NOT_PERFORMED** |
| Payments | Test-mode only |
| Production deploy | **Not performed** |
| Production readiness | **Not ready** — [assessment](docs/evidence/PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md) · [matrix](docs/evidence/PRODUCTION_READINESS_MATRIX.md) |

## Immediate continuation priorities

1. PDB-01/02: follow catalog inventory (712 brands scanned) — implement Device Registry hierarchy models (Manufacturer etc.), adapters from gallery/catalog, coverage/snapshot endpoints + receipts (Issue #68).
2. Align any demo creds; land pending UI polish.
3. Staging host + Design Engine full walkthrough receipt (test payments).
4. Dual-path thinning (F2+), P1/P2 hygiene per CONTINUATION.
5. Validate + re-pin readiness docs/matrix to current SHA.
6. Public Product Explorer navigation + pages per spec.  

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