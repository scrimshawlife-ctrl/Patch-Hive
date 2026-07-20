# PatchHive continuation plan

**Status date:** 2026-07-20  
**main HEAD:** `a162f85` (merge of PR #47)  
**Tracking:** Issue #46 closed · PR #47 **MERGED**  

## Where we are

Phases 0–8 of `PATCHHIVE_ONESHOT_CANON_ALIGNMENT_001` are **merged to main** (`a162f85`) with green CI at PR head. Pre-merge baseline was `9cae772`.

### Done on campaign branch (OBSERVED)

- [x] Canonical contracts, compiler, runes, immutable hierarchy (ADR 0001)
- [x] Alembic chain through `20240928_fix_schema_gaps` (single head)
- [x] Canonical workspace UI + PatchGraph a11y pair + theme tokens
- [x] Photo evidence resolution path (untrusted evidence only)
- [x] Atomic credits/exports, download tokens, Stripe webhook adapter (test mode)
- [x] Feature flags default-off for legacy social/publish/leaderboards/referrals
- [x] Security workflow (audit, Bandit, Gitleaks, SBOM)
- [x] Docs spine: CANON_ALIGNMENT, FEATURE_FLAGS, SECURITY, OPERATIONS, VALIDATION_EVIDENCE, ACCESSIBILITY
- [x] HTTP `/api/canon/*` for credits, exports, downloads, webhooks

### Explicitly not done

- [x] Merge PR #47 to `main` — **DONE** `a162f85` @ 2026-07-20T23:46:29Z
- [ ] Production or staging deploy
- [ ] Live Stripe / `ALLOW_PRODUCTION_PAYMENTS=true`
- [ ] Full retirement of legacy rack/patch/export dual paths
- [ ] Deletion of historical top-level `patchhive` package and stale page modules
- [ ] Hardware, DSP, MIDI/CV, or ModularGrid live provider implementation

## Recommended work order (post-merge or on branch)

### P0 — Ship gate

1. ~~Human review of PR #47~~ **DONE** — merged `--merge --delete-branch`.
2. Confirm `alembic heads` == `20240928_fix_schema_gaps` on clean `main` checkout.
3. Confirm flags: all `ENABLE_LEGACY_*` false; `STRIPE_TEST_MODE=true`; `ALLOW_PRODUCTION_PAYMENTS=false`.
4. Optional: tag `v0.2.0-canon-mvp` and cut release notes from this file + PR body.

### P1 — Dual-path reduction

1. Inventory every client call still on `/api/racks`, `/api/patches`, `/api/export` vs `/api/canon/*`.
2. Prefer canon routes for export/credits; keep legacy only behind deprecation window.
3. Document residual legacy endpoints in FEATURE_FLAGS or a DEPRECATIONS section.
4. Do **not** delete acceptance coverage until replacement paths are green on Postgres CI.

### P2 — Package hygiene

1. Import telemetry: who still imports top-level `patchhive` vs `backend/*`.
2. Quarantine or remove duplicate package; keep fail-closed vision/ModularGrid adapters.
3. Delete or move unused frontend pages not routed in `App.tsx` (`Feed`, `Publish`, `Publication`, `LeaderboardsModules`, etc.) to `frontend/src/legacy/` or delete with PR.

### P3 — Staging operations

1. Stand up non-prod Postgres + app using OPERATIONS release gates.
2. Run acceptance suite against staging Postgres (clears local `NOT_COMPUTABLE`).
3. Backup/restore drill; ledger `reconcile` job if present.
4. Manual accessibility protocol on staging (see ACCESSIBILITY.md).

### P4 — Product depth (still MVP-scoped)

1. Deeper rig revision UX (explicit revision picker, overlay notes/favorite/tried).
2. Stronger empty/loading/error parity on Modules/Cases/Patches list pages.
3. Expand golden fixtures / property tests for compiler edge cases.
4. Real image scanner implementation behind `ImageScanner` (ops secret + service).

### P5 — Explicitly deferred

- Community feed, profiles, comments, votes, following  
- Public publishing gallery as product surface  
- Leaderboards, contests, marketplace, curriculum  
- Live payments and customer charging  
- Next.js rewrite (forbidden by campaign: keep React/Vite + FastAPI)

## Verification commands (copy/paste)

```bash
# main (post-merge)
git fetch origin && git checkout main && git pull
git rev-parse HEAD   # expect a162f85… or later

cd backend
python -m pip install -e '.[dev]'
alembic heads        # expect 20240928_fix_schema_gaps
python -m pytest tests --ignore=tests/acceptance -q

cd ../frontend
npm ci
npm test -- --run
npm run test:e2e
```

CI authoritative when local Docker/Postgres missing.

## Drift watchlist

| Item | Risk |
|------|------|
| Root `DEPLOY_STATUS.md` (2025-11-26 “ready for Render”) | Stale — do not treat as ship authority |
| Root `CANON_DIFF.md` / `CANON_SYNC.md` | Pre-campaign audits — superseded by CANON_ALIGNMENT |
| `docs/OPERATIONS.md` Alembic head | Must match **20240928_fix_schema_gaps** |
| Social pages still on disk | Dead UI surface if re-linked accidentally |
| Dual export paths | Double-debit risk if both live without shared ledger — prefer canon only |

## Exit criteria for “canon MVP on main”

1. ~~PR #47 merged~~ **DONE**  
2. Main CI green on merge commit — confirm Actions on `a162f85`  
3. Docs on main: README + CURRENT_STATE + CONTINUATION agree on merged HEAD — this pass  
4. No production payment flags enabled  
5. Staging optional but recommended before any public traffic claim  

**Active engineering now starts at P1** (dual-path reduction).
