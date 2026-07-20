# CURRENT_STATE

**Authoritative as of:** 2026-07-20  
**Branch:** `codex/patchhive-oneshot-canon-alignment`  
**HEAD:** `1ab518cbda16f162cceb15e906a503296eeff2bf`  
**Baseline (main):** `9cae772413a4f35a6c116923b2d85250452cd0b7`  
**Campaign:** [Issue #46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) · [PR #47](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/47) (draft, MERGEABLE, CI green)

This file supersedes older root notes (`CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md`, pre-canon `CURRENT_STATE` claims). For inventory classification see [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md). For ordered next work see [docs/CONTINUATION.md](docs/CONTINUATION.md).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** workspace — not audio synthesis or hardware control |
| Canonical domain | `backend/canon/` — contracts, compiler, runes, exports, downloads, routes, models, repository |
| Hierarchy | User → Rig → RigRevision → GenerationRun → exactly one PatchLibrary → GeneratedPatch (ADR 0001) |
| HTTP canon surface | `/api/canon/*` credits, exports, download tokens, Stripe-style webhook (test-mode) |
| Frontend shell | Instrument-bench nav: Rigs, Modules, Cases, Patches, Account, Admin diagnostics; light/dark; skip link |
| Legacy social/publish/leaderboards/referrals | Feature-flagged **off** by default; not in primary nav |
| Payments | `STRIPE_TEST_MODE=true`, `ALLOW_PRODUCTION_PAYMENTS=false` |
| Alembic head | **`20240928_fix_schema_gaps`** (revises `20240927_canon_alignment`) |
| CI | Backend Tests (3.11/3.12 + Postgres), Code Quality, Security/SBOM — green on PR head |
| Production deploy | **Not performed** this campaign (`NOT_COMPUTABLE` without ops access) |

## Stack (active)

- **Backend:** FastAPI modular monolith (`backend/main.py`), SQLAlchemy + Alembic, JWT auth (`core/security.py` + `community/auth_routes.py`)
- **Frontend:** React + TypeScript + Vite (`frontend/`)
- **Tests:** pytest (unit/api/acceptance), Vitest, Playwright MVP suite
- **Deploy artifacts retained:** Docker Compose, Render, Azure, Replit package — historical; release gates in [docs/OPERATIONS.md](docs/OPERATIONS.md)

## Models / packages (high signal)

| Surface | Path | Notes |
|---------|------|--------|
| Canon ORM adapters | `backend/canon/models.py` | Append-only hierarchy + ledger/audit |
| Legacy racks/patches/runs | `backend/racks`, `patches`, `runs` | Still mounted; dual-path until full route migration |
| Monetization (legacy) | `backend/monetization` | Coexists with canon exports/credits |
| Community auth | always on under `/api/community/auth/*` | Social routers require `ENABLE_LEGACY_SOCIAL` |
| Duplicate package | top-level / nested `patchhive` | HISTORICAL — removal after import telemetry |
| Vision / ModularGrid | adapters fail closed | External implementation required |

## Validation snapshot (campaign PR body + CI)

- Local (pre-CI, host without Docker): backend `144 passed, 2 xfailed` (acceptance excluded); frontend `49 passed`; Playwright `4 passed`
- Acceptance on bare hosts without Postgres/Docker: **`NOT_COMPUTABLE`** — CI with Postgres 15 is authoritative
- Deterministic golden compilation hash (campaign): `c2356d416b9784d4487ffadf1fc6aafb974644f0767a5a36cba44d7f397934ee`
- PR checks at head: Backend Tests, Code Quality, Security — **SUCCESS**

## Authority boundary (still in force)

May inspect, modify, test, commit, push campaign branch, open/update draft PR.  
**Do not:** merge without operator intent, deploy production, enable live Stripe, charge users, delete production data, or activate hardware.

## Immediate continuation priorities

See [docs/CONTINUATION.md](docs/CONTINUATION.md). Short list:

1. Operator review + merge PR #47 when ready  
2. Post-merge: dual-path cleanup (legacy racks/patches → full canon routes)  
3. Remove or quarantine duplicate `patchhive` package after import audit  
4. Ops: real Postgres staging deploy (not production payments)  
5. Frontend dead pages (`Feed`, `Publish`, `Publication`, leaderboards) — delete or archive behind flags  
6. Expand Playwright beyond mocked MVP when staging exists  
