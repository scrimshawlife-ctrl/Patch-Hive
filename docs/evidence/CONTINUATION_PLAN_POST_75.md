# Continuation plan — post PR #75

**Drafted:** 2026-07-21  
**Baseline main HEAD:** `da790b0` (merge of #75 fusion panel confirm + staging Compose receipt)  
**Prior pin:** #74 multi-photo UI (`ba71b7f`); Alembic head `20240930_patch_user_overlays`  
**Authority:** subordinate to ADR-005, VSI contracts, `SYSTEM_CONTEXT.md`, fail-closed  
**Method:** live `main` + CONTINUATION + WORK_PACKAGES + capability matrix + Compose receipt  

## 1. Situation (OBSERVED)

| Fact | Evidence |
|------|----------|
| main includes PR #47–#75 | `gh` merge history; HEAD `da790b0` |
| VSI P0 contracts on main | inventory gate, vision mock, multi-image evidence, native bridge IDs |
| Multi-photo fuse API + UI | reconciliation + RackBuilder multi-file + fusion confirm/reject/defer |
| Local Compose db+backend healthy | `docs/evidence/STAGING_COMPOSE_RECEIPT.md` |
| Acceptance (testcontainers) previously green | `STAGING_ACCEPTANCE_RECEIPT.md` (11 passed) |
| Production deploy | **NOT_PERFORMED** |
| Live Stripe / production payments | **disabled / not claimed** |
| Vision production accuracy | **NOT_COMPUTABLE** (no representative licensed dataset) |
| Dual-path racks/patches HTTP | still primary inventory UI (by design; no big-bang delete) |
| Open campaign PRs | none (clean for next slice) |

### Product posture (one line)

Deterministic Eurorack **rig + patch documentation** with reviewable photo evidence — not audio DSP, not hardware control, not live marketplace.

### Explicit non-goals (hold until operator auth)

- Production / multi-tenant staging host deploy  
- `ALLOW_PRODUCTION_PAYMENTS=true` / live charging  
- Hardware, DSP, MIDI/CV, ModularGrid live provider  
- Big-bang deletion of racks routers  
- Next.js rewrite  
- Community feed / leaderboards / marketplace productization  

---

## 2. What just closed (this campaign arc)

| Slice | PR / artifact | Status |
|-------|---------------|--------|
| VSI P0 + inventory gate + bridge IDs | #66 | MERGED |
| Vision eval + cloud shell (fail-closed) | #67 | MERGED |
| AI engineering foundation | #70 | MERGED |
| Cases/Patches + live evidence UX | #69 | MERGED |
| Reaudit + telemetry + ast-grep | #71 | MERGED |
| Rig revision picker + overlays | #72 | MERGED |
| Multi-photo fuse API | (in #72 lineage / reconcile) | MERGED |
| Multi-photo UI panel | #74 | MERGED |
| Fusion confirm UX + Compose receipt | #75 | MERGED |

Doc drift residual: `CURRENT_STATE.md` still pins older HEAD (`6b7bc2d`) — **docs pin is slice D0 below**.

---

## 3. Residual backlog (classified)

### A — Truth / hygiene (cheap, do first)

| ID | Item | Why | Size |
|----|------|-----|------|
| **D0** | Pin `CURRENT_STATE.md` + `CONTINUATION.md` to `da790b0`; mark fusion confirm **DONE**; refresh capability matrix rows that still say “no multi-photo” | Agents and operators read stale HEAD | S |
| **D1** | Drift watchlist: `OPERATIONS.md` Alembic head claim vs `20240930_…`; root `DEPLOY_STATUS.md` still non-authority | Prevent false “ready to ship” | S |

### B — Product UX (MVP depth, low blast radius)

| ID | Item | Why | Size |
|----|------|-----|------|
| **U1** | Modules list polish (search/filter/sort; link into RackBuilder/placement) — state parity already exists | Catalog is still thin vs Cases/Patches effort | S–M |
| **U2** | RigDetail: surface confirmed inventory revision + “ready for generation” from evidence path | Close photo → inventory → generate loop in UI | M |
| **U3** | Fusion panel: show candidate status after apply; clear rep-id noise in copy; optional “apply to all observations of fuse” if API supports | Confirm UX is shippable but still thin | S |
| **U4** | Empty/loading/error parity audit on Racks + RigDetail vs Cases pattern | Consistency | S |

### C — VSI / evidence (contracts-first)

| ID | Item | Why | Size |
|----|------|-----|------|
| **V1** | Persist sealed `SystemInventoryRevision` rows when user confirms (if not fully end-to-end on live path) | Matrix still notes in-process vs product path gaps | M |
| **V2** | Playwright: multi-photo upload + fusion panel confirm/reject (mocked APIs) | Protect #74/#75 regressions | M |
| **V3** | Cable endpoint inference remains STUB — design-only until model; do not invent accuracy | Capability matrix | hold |
| **V4** | Live vision provider behind existing adapter | Requires **ops secret + eval dataset**; accuracy stays NOT_COMPUTABLE until dataset | L + ops |
| **V5** | Production AV / malware scanner behind `ImageScanner` | Security posture for real uploads | M + ops |

### D — Dual-path / package hygiene

| ID | Item | Why | Size |
|----|------|-----|------|
| **H1** | `patchhive` import telemetry doc + pytest quarantine for pure historical corpus | Large surface; no new features there | M |
| **H2** | Inventory dual-path: keep racks as CANON_SUPPORTING; optional alias docs only | Full retirement is high risk | design hold |
| **H3** | No accidental re-link of `frontend/src/legacy/pages` | Dead social UI | watch |

### E — Staging / ops (beyond local Compose)

| ID | Item | Why | Size |
|----|------|-----|------|
| **O1** | ~~Local Compose db+backend~~ **DONE** (`STAGING_COMPOSE_RECEIPT.md`) | — | done |
| **O2** | Named non-prod host (Render/Fly/etc.) — **blocked on operator host pick** | Real staging URL + secrets | ops |
| **O3** | Acceptance suite against that host Postgres | Clears remaining deploy NOT_COMPUTABLE | M + ops |
| **O4** | Backup/restore + ledger reconcile drill | OPERATIONS gates | ops |
| **O5** | Manual a11y protocol on staging | ACCESSIBILITY.md | ops |

---

## 4. Recommended execution order

Ship small vertical slices; CI green → merge → pin docs. No production deploy in this plan.

```text
Wave 0 — Truth (same day)
  D0  docs pin HEAD #74/#75 + capability matrix refresh
  D1  OPERATIONS Alembic head alignment if drifted

Wave 1 — Harden multi-photo loop (highest ROI product)
  V2  Playwright multi-photo + fusion confirm (mocked)
  U3  Fusion panel polish (status feedback after apply)
  U2  RigDetail inventory-revision / ready-for-generation surface

Wave 2 — Catalog + workspace polish
  U1  Modules search/filter + placement entry points
  U4  Racks/RigDetail state parity audit

Wave 3 — Evidence persistence honesty
  V1  Confirm → sealed inventory revision end-to-end (API + FE receipt)
  (only if gap confirmed by reaudit of confirm path)

Wave 4 — Hygiene (parallelizable)
  H1  patchhive import telemetry + quarantine plan (docs + pytest config)

Wave 5 — Ops-gated (do not start without operator)
  O2–O5  named staging host
  V4/V5  live vision + AV scanner secrets
```

### Suggested first PR stack (if executing immediately)

| Order | Branch theme | Exit criteria |
|-------|--------------|---------------|
| 1 | `docs/pin-main-after-75` | CURRENT_STATE + CONTINUATION + matrix agree on `da790b0`; fusion confirm DONE |
| 2 | `test/e2e-fusion-panel` | Playwright covers multi-file select + confirm fused / reject / conflict blocked |
| 3 | `feat/rigdetail-inventory-receipt` | After confirm, RigDetail shows inventory_revision_id + generation readiness |
| 4 | `feat/modules-catalog-polish` | Search + retry parity retained; links to builder |
| 5 | `chore/patchhive-import-telemetry` | Doc + no new canon→patchhive imports (ast-grep if useful) |

---

## 5. Verification gates (every PR)

```bash
# backend
cd backend && env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance -q
# optional acceptance when Docker available
env -u PYTHONPATH python -m pytest tests/acceptance -q

# frontend
cd frontend && npm run type-check && npm test -- --run && npm run test:e2e

# compose smoke (local)
docker compose up -d db backend
curl -sf http://localhost:8000/health
docker compose exec -T backend alembic current   # expect 20240930_patch_user_overlays
```

CI workflows: backend, frontend, audit, engineering — all required green before merge.

---

## 6. Decision rules

| Rule | Application |
|------|-------------|
| Fail closed | No inventing inventory, credits, or vision accuracy |
| NOT_COMPUTABLE | Prefer explicit over fake metrics (vision, production deploy) |
| Signal-type “audio” | Preserve legitimate patch signal vocabulary; no DSP product work |
| Dual-path | Racks stay until a deliberate retirement campaign |
| Evidence never self-confirms | Fusion panel remains user-initiated |
| No production | Staging host and live payments need separate operator authorization |

---

## 7. Exit criteria for this continuation window

**MVP-hardening complete** when:

1. Docs on main agree on HEAD `da790b0`+ and Alembic `20240930_…`  
2. Playwright protects multi-photo + fusion confirm path  
3. User can see inventory revision / generation readiness after confirm in workspace UI  
4. Modules catalog usable for placement discovery  
5. Still: no production deploy claim, no live payments, vision accuracy NOT_COMPUTABLE  

**Not required** for this window: live vision model, cable CV inference, dual-path deletion, community features.

---

## 8. Open questions (operator)

1. Named staging host preference (Compose-on-server vs Render vs Fly)?  
2. Priority bias: **product UX** (U*) vs **evidence honesty** (V1) vs **hygiene** (H1)?  
3. Any appetite for a **release tag** (e.g. `v0.3.0-vsi-multi-photo`) after Wave 1?

Default if no answer: execute **Wave 0 → Wave 1** in order.
