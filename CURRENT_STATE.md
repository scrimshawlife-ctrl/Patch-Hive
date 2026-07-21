# CURRENT_STATE

**Authoritative as of:** 2026-07-21  
**Branch:** `main`  
**HEAD:** `7bfbd79` (post-#71); feature branch may advance for revision picker  

### Recent merges (OBSERVED)

| PR | Result |
|----|--------|
| [#66](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/66) | VSI P0: inventory, vision mock, native bridge IDs, multi-image evidence |
| [#67](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/67) | Vision eval harness + consent-gated cloud adapter |
| [#70](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/70) | AI-native engineering foundation (just, indexes, SYSTEM_CONTEXT) |
| [#69](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/69) | Cases/Patches lists + RackBuilder live evidence UX |

**Campaign issue lineage:** [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  

This file supersedes older root notes (`CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md`).  
For inventory classification see [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md).  
For ordered next work see [docs/CONTINUATION.md](docs/CONTINUATION.md).  
For agent bootstrap see [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) + [AI_CONTEXT.md](AI_CONTEXT.md).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** — not audio DSP / hardware control |
| Canonical domain | `backend/canon/` |
| Visual intelligence | P0 on main + eval harness + fail-closed cloud shell |
| FE catalog depth | Cases/Patches/Modules list parity (loading/empty/error/retry) |
| RackBuilder evidence | Live `evidenceApi` when rack selected; demo fallback |
| AI engineering | `justfile`, `.codebase-memory` rebuild, engineering CI |
| Bridge IDs | Native `rig-rev-*` / `gen-run-*` |
| Alembic head | **`20240930_patch_user_overlays`** (revises 20240929) on revision-picker branch; main may still be 20240929 until merge |
| Payments | Test-mode only; production payments disabled |
| Production deploy | **Not performed** |

## Validation snapshot

| Gate | Result | Class |
|------|--------|-------|
| PR #70 CI (backend/frontend/audit/engineering) | success | OBSERVED |
| PR #69 CI (after remerge) | success | OBSERVED |
| Vision production accuracy | no representative dataset | `NOT_COMPUTABLE` |
| Full Compose staging | optional | `NOT_COMPUTABLE` without ops host |

## Immediate continuation priorities

1. `patchhive` package import telemetry + quarantine plan (P2) — see engineering doc  
2. Dual-path residual: keep racks UI; no big-bang delete  
3. Rig revision picker UX / annotation overlays (P4)  
4. Optional: ast-grep domain guard rules in CI  
5. Staging Compose drill when operator provides host  

## Authority boundary

**Do not:** deploy production, enable live Stripe, charge users, or activate hardware without separate operator authorization.
