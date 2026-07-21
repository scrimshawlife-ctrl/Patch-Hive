# CURRENT_STATE

**Authoritative as of:** 2026-07-21  
**Branch:** `main`  
**HEAD:** pin after ops 1–3 PR (staging plan, dual-path design, alpha tag notes)

### Recent merges (OBSERVED)

| PR | Result |
|----|--------|
| [#66](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/66)–[#75](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/75) | VSI P0 through multi-photo fusion confirm + Compose receipt |
| [#76](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/76)–[#79](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/79) | Inventory receipt, modules polish, import quarantine, compiler edges |
| [#80](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/80)–[#82](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/82) | Full residual `legacy_pipeline` unit migration onto canon |
| Ops 1–3 PR | Staging host plan + compose.staging; dual-path design F0; alpha release notes |

**Campaign issue lineage:** [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  

For inventory dual-path residual see [docs/evidence/DUAL_PATH_RETIREMENT_DESIGN.md](docs/evidence/DUAL_PATH_RETIREMENT_DESIGN.md).  
For staging host pick see [docs/evidence/STAGING_HOST_PLAN.md](docs/evidence/STAGING_HOST_PLAN.md).  
For agent bootstrap see [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) + [AI_CONTEXT.md](AI_CONTEXT.md).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** |
| Canonical domain | `backend/canon/` (+ export_pack, pipeline, function_registry, query_surface) |
| Default unit tests | No `patchhive` package imports |
| Alembic head | **`20240930_patch_user_overlays`** |
| Local Compose | healthy (prior receipt) |
| Named staging host | plan only — **NOT_PERFORMED** until operator pick |
| Payments | Test-mode only |
| Production deploy | **Not performed** |

## Immediate continuation priorities

1. Operator picks staging host A/B/C/D and provisions secrets  
2. Dual-path **F3** generate dual-write audit (code)  
3. Optional tag `v0.3.0-alpha.1` on green main after this PR  

## Authority boundary

**Do not:** deploy production, enable live Stripe, charge users, or activate hardware without separate operator authorization.
