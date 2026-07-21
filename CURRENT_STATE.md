# CURRENT_STATE

**Authoritative as of:** 2026-07-21  
**Branch:** `main`  
**HEAD:** `6a85beb32cc8aee0344832de7efda64e645badcc`  
**Latest product merge:** [PR #66](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/66) **MERGED** (Visual System Intelligence P0 + inventory + native bridge IDs + multi-image evidence)  
**Prior product path:** PRs #47–#65 (canon MVP + dual-path slices)  
**Campaign issue lineage:** [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed  

This file supersedes older root notes (`CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md`). For inventory classification see [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md). For ordered next work see [docs/CONTINUATION.md](docs/CONTINUATION.md).

## OBSERVED product posture

| Area | State |
|------|--------|
| Product identity | Deterministic Eurorack **rig + patch documentation** workspace — not audio synthesis or hardware control |
| Canonical domain | `backend/canon/` — contracts, compiler, runes, exports, inventory, models |
| Visual intelligence | P0 on main: secure image prep, mock vision, confirmations, inventory gate, multi-image upload |
| Hierarchy | User → Rig → RigRevision → GenerationRun → exactly one PatchLibrary → GeneratedPatch (ADR 0001) |
| HTTP canon surface | `/api/canon/*` credits, exports, downloads, runs alias; evidence under `/api/racks/{id}/evidence/*` |
| Bridge IDs | Native `rig-rev-*` / `gen-run-*` (content-bound) |
| Alembic head | **`20240929_visual_inventory_evidence`** |
| Payments | `STRIPE_TEST_MODE=true`, `ALLOW_PRODUCTION_PAYMENTS=false` |
| Production deploy | **Not performed** |

## Validation snapshot (merge of #66)

| Gate | Result | Class |
|------|--------|-------|
| CI Backend Tests 3.11/3.12 | success | OBSERVED |
| CI Code Quality | success | OBSERVED |
| CI Security | success | OBSERVED |
| Acceptance (testcontainers) | 11 passed (campaign) | OBSERVED |
| Vision production accuracy | no representative dataset | `NOT_COMPUTABLE` |

## Immediate continuation priorities

1. Evaluation harness + synthetic fixtures (in progress on post-merge branch)  
2. Consent-gated cloud vision adapter (fail-closed; no live paid calls in CI)  
3. Wire RackBuilder upload/confirm to real rack IDs end-to-end  
4. Cases/Patches list page depth (P4)  
5. Staging full-stack Compose drill (optional)  

## Authority boundary

**Do not:** deploy production, enable live Stripe, charge users, or activate hardware without separate operator authorization.
