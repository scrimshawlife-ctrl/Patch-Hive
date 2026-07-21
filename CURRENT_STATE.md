# CURRENT_STATE

**Authoritative as of:** 2026-07-21  
**Branch:** `grok/patchhive-visual-system-canon-audit` (campaign; draft PR #66)  
**Baseline main HEAD:** `2b72d5b10fef1ab70c74d3c40379eb1593cf8293`  
**Draft PR:** [#66](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/66) — VSI P0 + inventory persist + native bridge IDs + multi-image evidence  
**Operator review:** [docs/evidence/PR66_OPERATOR_REVIEW.md](docs/evidence/PR66_OPERATOR_REVIEW.md) — PASS WITH COMMENTS  
**Acceptance:** 11 passed (testcontainers) — [STAGING_ACCEPTANCE_RECEIPT.md](docs/evidence/STAGING_ACCEPTANCE_RECEIPT.md)  

This file supersedes older root notes (`CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md`, pre-canon `CURRENT_STATE` claims). For inventory classification see [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md). For ordered next work see [docs/CONTINUATION.md](docs/CONTINUATION.md). For VSI evidence see [docs/evidence/](docs/evidence/).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** workspace — not audio synthesis or hardware control |
| Canonical domain | `backend/canon/` — contracts, compiler, runes, exports, downloads, routes, models, repository |
| Visual intelligence | Contracts + mock vision provider + inventory gates in-process; secure image prep; **not** production vision accuracy |
| Hierarchy | User → Rig → RigRevision → GenerationRun → exactly one PatchLibrary → GeneratedPatch (ADR 0001) |
| HTTP canon surface | `/api/canon/*` credits, exports, download tokens, runs alias, Stripe-style webhook (test-mode) |
| Frontend MVP shell | Instrument-bench nav: Rigs, Modules, Cases, Patches, Account, Admin diagnostics; light/dark; skip link |
| MVP credits/export UI | Routed through `/api/canon/*` via `canonApi` + `accountApi` aliases |
| Legacy social/publish/leaderboards/referrals | Feature-flagged **off** by default; pages under `frontend/src/legacy/` |
| Payments | `STRIPE_TEST_MODE=true`, `ALLOW_PRODUCTION_PAYMENTS=false` (`.env.example`) |
| Alembic head | **`20240929_visual_inventory_evidence`** (single head; revises `20240928_fix_schema_gaps`) |
| Bridge IDs | Native `rig-rev-*` / `gen-run-*` (content-bound); legacy helpers deprecated only |
| Production deploy | **Not performed** (`NOT_COMPUTABLE` without ops access) |

## Stack (active)

- **Backend:** FastAPI modular monolith (`backend/main.py`), SQLAlchemy + Alembic, JWT auth
- **Frontend:** React + TypeScript + Vite (`frontend/`)
- **Tests:** pytest (unit/api/acceptance), Vitest, Playwright MVP suite
- **Deploy artifacts retained:** Docker Compose, Render, Azure, Replit package — historical; release gates in [docs/OPERATIONS.md](docs/OPERATIONS.md)

## Models / packages (high signal)

| Surface | Path | Notes |
|---------|------|--------|
| Canon ORM adapters | `backend/canon/models.py` | Append-only hierarchy + ledger/audit |
| Visual contracts | `backend/canon/visual_contracts.py` | ResolutionStatus, candidates, inventory, capability graph |
| Inventory builder | `backend/canon/inventory.py` | Immutable revision + confirmed-hardware patch gate |
| Evidence intake | `backend/evidence/images.py`, `vision_provider.py` | Re-encode + provider-neutral adapter |
| Legacy racks/patches/runs | `backend/racks`, `patches`, `runs` | Still mounted; inventory dual-path residual |
| Duplicate package | top-level / nested `patchhive` | HISTORICAL — many backend tests still import it (P2) |
| Vision / ModularGrid live | adapters fail closed / mock | External implementation required for production accuracy |

## Validation snapshot

| Gate | Result | Class |
|------|--------|-------|
| Local unit/api (no acceptance) @ baseline | 161 passed, 2 xfailed | OBSERVED |
| New VSI unit tests (this campaign) | 20 passed (includes prior image evidence) | OBSERVED |
| Alembic heads (local) | `20240928_fix_schema_gaps` | OBSERVED |
| Full `make test` without Docker Compose | blocked | `NOT_COMPUTABLE` |
| Acceptance without Postgres/Docker | blocked | `NOT_COMPUTABLE` — CI authoritative |
| Vision accuracy metrics | no representative dataset | `NOT_COMPUTABLE` |

## Authority boundary (still in force)

Post-merge engineering may continue on feature branches.  
**Do not:** deploy production, enable live Stripe, charge users, delete production data, or activate hardware without separate operator authorization.

## Immediate continuation priorities

See [docs/CONTINUATION.md](docs/CONTINUATION.md). Short list:

1. Wire `enforce_confirmed_inventory_constraints` into generate API (WP-05)
2. Persist inventory revisions (WP-06) when product path is ready
3. Authenticated multi-image upload + retention/consent
4. Native canon run generation (drop `legacy-*` namespace)
5. P2: remaining `patchhive` import telemetry
6. P3: non-prod Postgres staging + acceptance against real DB
