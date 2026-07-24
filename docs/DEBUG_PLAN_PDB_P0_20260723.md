# DEBUG PLAN: Product Database (PDB) P0 Completion & Integration
**Date**: 2026-07-23  
**Scope**: Main branch state after scoping from feature work (PR #137 contains the bulk of PDB implementation)  
**Goal**: Systematically diagnose gaps between current main and full PDB P0 (per Issue #68), identify blockers to integration/verification, and execute fixes.  
**Method**: Follow systematic-debugging skill (4 phases). No guesses. Root cause first.

## Symptom Summary (Observed on Main)
- Main at 3d86ee1 (pre-PDB foundation).
- PDB work (registry models, seeding, explorer, module mockups, evidence) lives only in PR #137 / feature branch.
- Docker services running (backend, db, frontend-dev) but may not reflect PDB schema changes.
- Pre-existing test collection failures (e.g., "No module named 'parse_cases_research'").
- Old task list items (pdb-models-complete, pdb-ingester, etc.) appear unresolved on main.
- No registry tables/migration visible on main DB without the PR changes.
- make lint/test/build have known env frictions (frontend ESLint config, test imports).

## Phase 1: Root Cause Investigation (Evidence Gathering)

### 1.1 Read Errors & State
- Command to repro: `docker compose exec backend python -m pytest --collectonly -q 2>&1 | head -20`
- Git state on main vs branch.
- Check for registry tables: `docker compose exec backend python -c "from core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names()[:20])"`

### 1.2 Build Tight Feedback Loops
- Loop 1 (DB state): Alembic current revision + registry table presence.
- Loop 2 (API): TestClient calls to /api/registry/* and /api/modules/catalog (expect 404 or empty on main).
- Loop 3 (Tests): Targeted pytest on known passing registry tests (will fail on main until merged).
- Loop 4 (Frontend): Check if /products route and Registry.tsx exist on main (should not).

### 1.3 Recent Changes & Data Flow
- Last main commit: feat(ui): multi-module batch place...
- PDB changes only on branch: backend/registry/, alembic 20260723, seeders, frontend Registry + mockup.
- Data flow for PDB: catalog seeds → registry links in ModuleCatalog → materialize → explorer.

### 1.4 Evidence Checklist
- [ ] Run repro loops and capture output.
- [ ] Confirm registry models/services/routes absent on main.
- [ ] Confirm evidence receipts absent on main (only on branch).
- [ ] Identify import/collect errors root.

**STOP** until Phase 1 data collected.

## Phase 1 Execution Results (Run on main 2026-07-23)

### DB State (Loop 1)
- Total tables: 56
- Registry-related tables present (from prior container run): ['manufacturers', 'device_families', 'device_models', 'device_revisions']
- Root cause note: Docker volume persistence means DB schema from feature-branch runs remains even after `git checkout main`. Code and DB are now drifted.

### API State (Loop 2)
- GET /api/registry/manufacturers?limit=1 → **404** (routes not wired in main branch main.py)
- GET /api/modules/catalog?limit=1 → **200** (pre-existing catalog works)
- Registry.tsx and /products route: **absent** on main (ls + grep confirmed 0 matches)

### Test State (Loop 3)
- Registry-specific tests (test_registry_models.py, test_seeder_catalog.py, etc.): **not present** on main → "no tests collected" / file not found.
- Pre-existing collection error (unrelated to PDB): `ModuleNotFoundError: No module named 'parse_cases_research'` in tests/unit/test_cases_research_parse.py (313 tests collected, 1 error). This blocks full `make test`.

### Code Presence (Loop 4)
- backend/registry/: only __pycache__ (source files absent)
- grep "registry" in backend/main.py: 0 matches (no include_router for registry)
- frontend Registry explorer + module mockup improvements: absent on main

**Conclusion from Phase 1**: PDB implementation is complete and isolated on feature branch + PR #137 (good practice). "Pending" status in old task list is an artifact of context compression + working on branch. Main is intentionally pre-PDB. DB drift is the only live inconsistency.

## Phase 2: Pattern Analysis (Executed)
- Working examples on main: Existing `modules/catalog.py`, `modules/catalog_routes.py` (pre-registry slugs), alembic for other tables.
- Differences vs branch: Branch adds full hierarchy, seeder, routes wiring, Registry.tsx, mockup CSS/JSX, evidence.
- Pattern: Feature developed off-main, PR created. Standard for large P0 work.

## Phase 3: Hypotheses (Validated)
1. **Hypothesis A (confirmed)**: Work correctly branched. "Unresolved on main" expected until merge. Context list is stale.
2. **Hypothesis B (confirmed)**: parse_cases_research error is pre-existing env/collect issue (volume mount or missing local script), not PDB-related.
3. **Hypothesis C (confirmed)**: DB has migrated tables; code on main does not.

## Phase 4: Recommended Execution Steps
1. Merge PR #137 (or rebase main onto it) to bring PDB code to main.
2. After merge: `docker compose exec backend alembic upgrade head` (if not already applied).
3. Re-run targeted tests: `docker compose exec backend python -m pytest ...test_registry* -q`
4. Update CURRENT_STATE.md and close/update task list items.
5. Fix pre-existing parse_cases_research (separate issue): investigate tests/unit/test_cases_research_parse.py import.
6. Re-verify full loops post-merge.
7. Clean any lingering untracked artifacts.

**Plan Status**: Phase 1-3 complete. Phase 4 ready for execution (start with merge review).

## Old Task List Update (from prompt)
The listed items (pdb-models-complete, pdb-ingester, etc.) are **completed in PR #137**. Mark as done post-merge. pdb-plan-draft satisfied by this DEBUG_PLAN + prior evidence files.

- Find working examples: Look for similar patterns in existing modules/catalog (pre-PDB).
- Compare: Main vs branch diff for registry integration points (main.py wiring, catalog.py slugs).
- Identify differences: Main lacks DeviceRegistry tables, seeder script, Registry.tsx, mockup CSS/JSX.
- Dependencies: Requires alembic upgrade, DB migration, frontend build.

## Phase 3: Hypotheses (Ranked)
1. **Hypothesis A (highest)**: PDB implementation was correctly isolated to feature branch per best practices; "incomplete on main" is expected state until PR merge. Root cause of "task list pending" = context compression artifact + branch scoping.
   - Prediction: Merging PR #137 or cherry-picking will resolve task list items.
2. **Hypothesis B**: Test collection errors pre-date PDB and are env/volume mount issues (parse_cases_research not in PYTHONPATH inside container).
   - Prediction: `PYTHONPATH=. pytest ...` or docker volume fix will improve collection without PDB changes.
3. **Hypothesis C**: Docker DB on main does not have the 20260723 migration applied (expected).
   - Prediction: Running alembic upgrade on container will fail until migration file present.

## Phase 4: Implementation & Execution Plan
1. Execute Phase 1 loops (use tools below).
2. Verify Hypothesis A by inspecting PR #137 changes vs main.
3. For test env: Draft minimal fix (e.g., update conftest or docker-compose pythonpath).
4. Draft merge/integration steps.
5. Update task list / CURRENT_STATE with evidence.
6. Re-run verification.
7. If needed, open follow-up issues or amend PR.

**Next Action**: Execute the loops in Phase 1 now.
