# Dual-path rack/patch retirement — design (no big-bang)

**Date:** 2026-07-21  
**Baseline main:** `7727908`  
**Authority:** design-only; subordinate to [CANON_ALIGNMENT.md](../CANON_ALIGNMENT.md) inventory dual-path matrix  
**Rule:** fail closed; one vertical slice; CI green; no production deploy  

## Situation (OBSERVED)

| Surface | Role today | Class |
|---------|------------|--------|
| `backend/racks` + FE Racks/RackBuilder/RigDetail inventory | Primary inventory HTTP + UI | **CANON_SUPPORTING** |
| `backend/patches` generate + list | Generate + library list | **CANON_SUPPORTING** |
| `backend/runs` patches list | Run-bound patches | **CANON_SUPPORTING** |
| `/api/canon/runs`, `/api/canon/exports`, credits | Monetization + run bridge DTO | **CANON_MVP** |
| Evidence under `/api/racks/{id}/evidence/*` | Multi-photo inventory path | **CANON_MVP** (mounted on rack id) |
| Slices A–E dual-path credits/bridge | Done | — |
| Default unit tests → `patchhive` package | **None** (PR #82) | hygiene done |

FE still uses `rackApi` for list/create/edit and evidence. Renaming HTTP `/racks` → `/rigs` in one PR is **forbidden**.

## Goal state (target, not this PR)

```text
User → Rig (stable id) → RigRevision (immutable) → Run → PatchLibrary → Patch
HTTP: /api/canon/rigs/* (or thin adapter) preferred for new clients
Legacy /api/racks remains until zero FE+acceptance callers
```

Inventory confirmation continues via evidence APIs; rack id may remain the external key while rows dual-write `RigRevisionRecord`.

## Residual dual-path (inventory HTTP)

| ID | Slice | Scope | Exit criteria | Risk |
|----|--------|--------|---------------|------|
| **F0** | Document truth | This design + CONTINUATION pin | Merged design | low |
| **F1** | Alias docs only | README/API: `rack_id ≡ rig_id` for MVP | Docs only | low |
| **F2** | Thin `GET /api/canon/rigs` list | Read adapter over racks table / rig revisions | FE optional switch behind flag | med |
| **F3** | Generate dual-write audit | Confirm every generate path writes bridge + inventory metrics | Tests green; no new legacy-* ids | med |
| **F4** | Evidence path on canon prefix | Optional ` /api/canon/rigs/{id}/evidence/*` alias | Same handlers; dual mount | med |
| **F5** | FE inventory reads prefer canon DTO | RigDetail/Racks consume bridge fields only | Playwright green | med |
| **F6** | Deprecate unused patch list fields | Mark dual response keys | No caller | low |
| **F7** | Quarantine dead rack-only admin paths | If any unused | rg zero callers | low |
| **Z** | Delete `backend/racks` routers | **Only when** F2–F5 live and zero callers | Explicit operator PR | **high** |

## Explicit non-goals

- Big-bang delete of `backend/racks` or `backend/patches`  
- Next.js / GraphQL  
- Production deploy as part of dual-path work  
- Moving vision accuracy to OBSERVED without dataset  

## Recommended execution order

1. **F0** (this document) — ship  
2. **F1** docs alias — optional same PR  
3. **F3** generate dual-write audit (code) — next engineering PR  
4. **F2/F4** read aliases — when FE capacity  
5. **F5** FE cutover — after aliases stable  
6. **Z** delete — separate campaign, never same PR as F2  

## Decision log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep `/api/racks` near-term | Yes | Active inventory UI + evidence path |
| Prefer evidence under rack id | Yes | Avoid breaking multi-photo clients |
| Delete historical `backend/patchhive` package | Later | Unit tests free; package still used by runes/internal |
| Production payments on staging | Never without separate auth | Fail closed |

## Exit criteria for “dual-path residual closed”

1. No MVP FE path invents `legacy-*` ids  
2. Generate always emits native `rig-rev-*` / `gen-run-*` (already intended)  
3. Documented caller map for every `/api/racks` route  
4. Operator-approved delete PR for any router removal  
