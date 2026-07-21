# CURRENT_STATE

**Authoritative as of:** 2026-07-21  
**Branch:** `main`  
**HEAD:** `71a4dfaab7aefe1d4cb920dd9f83abcb7757fea7`  
**Latest product merge:** [PR #49](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/49) MERGED (P1 canon credits/exports client)  
**Prior canon MVP merge:** [PR #47](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/47) at `a162f85`  
**Campaign:** [Issue #46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  
**Open PRs / issues:** none (OBSERVED 2026-07-21)

This file supersedes older root notes (`CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md`, pre-canon `CURRENT_STATE` claims). For inventory classification see [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md). For ordered next work see [docs/CONTINUATION.md](docs/CONTINUATION.md).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** workspace — not audio synthesis or hardware control |
| Canonical domain | `backend/canon/` — contracts, compiler, runes, exports, downloads, routes, models, repository |
| Hierarchy | User → Rig → RigRevision → GenerationRun → exactly one PatchLibrary → GeneratedPatch (ADR 0001) |
| HTTP canon surface | `/api/canon/*` credits (balance + summary), exports (list/create/get), download tokens, Stripe-style webhook (test-mode) |
| Frontend MVP shell | Instrument-bench nav: Rigs, Modules, Cases, Patches, Account, Admin diagnostics; light/dark; skip link |
| MVP credits/export UI | **Routed through `/api/canon/*`** via `canonApi` + `accountApi` aliases (PR #49) |
| Legacy social/publish/leaderboards/referrals | Feature-flagged **off** by default; not in primary nav |
| Payments | `STRIPE_TEST_MODE=true`, `ALLOW_PRODUCTION_PAYMENTS=false` (`.env.example`) |
| Alembic head | **`20240928_fix_schema_gaps`** (single head; revises `20240927_canon_alignment`) |
| CI on main @ `71a4dfa` | Backend Tests, Code Quality, Security/SBOM — **SUCCESS** (push after #49) |
| Production deploy | **Not performed** (`NOT_COMPUTABLE` without ops access) |

## Stack (active)

- **Backend:** FastAPI modular monolith (`backend/main.py`), SQLAlchemy + Alembic, JWT auth (`core/security.py` + `community/auth_routes.py`)
- **Frontend:** React + TypeScript + Vite (`frontend/`)
- **Tests:** pytest (unit/api/acceptance), Vitest, Playwright MVP suite
- **Deploy artifacts retained:** Docker Compose, Render, Azure, Replit package — historical; release gates in [docs/OPERATIONS.md](docs/OPERATIONS.md)

## Models / packages (high signal)

| Surface | Path | Notes |
|---------|------|--------|
| Canon ORM adapters | `backend/canon/models.py` | Append-only hierarchy + ledger/audit |
| Legacy racks/patches/runs | `backend/racks`, `patches`, `runs` | Still mounted; **inventory dual-path remains** (P1 residual) |
| Legacy PatchBook POST | `backend/export/routes.py` `/runs/{id}/patchbook` | Still mounted; **acceptance still depends on it** |
| Monetization (legacy) | `backend/monetization` | Coexists; FE balance aliases canon |
| Community auth | always on under `/api/community/auth/*` | Social routers require `ENABLE_LEGACY_SOCIAL` |
| Duplicate package | top-level / nested `patchhive` | HISTORICAL — many backend tests still import it (P2) |
| Vision / ModularGrid | adapters fail closed | External implementation required |

## Dual-path snapshot (post-#49)

| Client surface | Preferred | Residual legacy |
|----------------|-----------|-----------------|
| Account credits + export list | `accountApi` → `/api/canon/credits/summary`, `/api/canon/exports` | `/api/me/credits`, `/api/me/exports` still exist server-side |
| Rig workspace debit | `canonApi.createExport` | `exportApi.patchbookExport` deprecated; not used by active UI |
| PDF/SVG bytes | `/api/export/...` GETs | Artifact delivery only — no new debits from MVP UI |
| Rig/run inventory | `/api/racks`, `/api/runs`, `/api/patches` | Active UI still uses these (Racks, RigDetail run list, generate) |
| Export bridge IDs | `source_run_id` stringified run id | `source_rig_revision_id: legacy-rack-{id}` + hashed run manifest |

## Validation snapshot

| Gate | Result | Class |
|------|--------|-------|
| CI Backend Tests @ `71a4dfa` | success | OBSERVED |
| CI Code Quality @ `71a4dfa` | success | OBSERVED |
| CI Security @ `71a4dfa` | success | OBSERVED |
| Alembic heads (local) | `20240928_fix_schema_gaps` | OBSERVED |
| Prior local targeted (session): canon export/copy tests | 10 passed | OBSERVED (prior run) |
| Prior local: Vitest / tsc / Playwright MVP | 51 / 0 / 4 | OBSERVED (prior run) |
| Full `make test` without Docker Compose | blocked | `NOT_COMPUTABLE` on hosts without compose plugin |
| Acceptance without Postgres/Docker | blocked | `NOT_COMPUTABLE` — CI authoritative |
| Golden compile hash (campaign) | `c2356d416b9784d4487ffadf1fc6aafb974644f0767a5a36cba44d7f397934ee` | OBSERVED (campaign) |

## Authority boundary (still in force)

Post-merge engineering may continue on feature branches.  
**Do not:** deploy production, enable live Stripe, charge users, delete production data, or activate hardware without separate operator authorization.

## Immediate continuation priorities

See [docs/CONTINUATION.md](docs/CONTINUATION.md). Short list:

1. ~~Operator review + merge PR #47~~ **DONE** (`a162f85`)
2. ~~P1 client: MVP credits/exports → `/api/canon/*`~~ **DONE** (PR #49 @ `71a4dfa`)
3. ~~P1 acceptance + admin grant dual-write + legacy debit gate~~ **IN PR** (`feat/p1-acceptance-canon-exports`)
4. **P1 residual:** real `rig_revision_id` / manifest on run DTOs; inventory dual-path plan
5. **P2:** quarantine unrouted FE pages + duplicate `patchhive` import audit
6. **P3:** non-prod Postgres staging + acceptance against real DB
7. **P4:** Cases/Patches list depth (currently stubs); revision picker UX