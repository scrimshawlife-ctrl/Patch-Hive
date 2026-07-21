# PatchHive continuation plan

**Status date:** 2026-07-21  
**main HEAD:** `7471a2a09cb7435ebf1ea10fe6280ebc94774500`  
**Tracking:** Issue #46 closed · PR #47 MERGED · PR #49 MERGED · PR #51 MERGED  
**Open campaign PRs:** none

## Where we are

Phases 0–8 of `PATCHHIVE_ONESHOT_CANON_ALIGNMENT_001` are on `main` (`a162f85` via PR #47).  
**P1 client dual-path reduction for credits/exports** is on `main` (`71a4dfa` via PR #49).

### Done (OBSERVED)

- [x] Canonical contracts, compiler, runes, immutable hierarchy (ADR 0001)
- [x] Alembic chain through `20240928_fix_schema_gaps` (single head)
- [x] Canonical workspace UI + PatchGraph a11y pair + theme tokens
- [x] Photo evidence resolution path (untrusted evidence only)
- [x] Atomic credits/exports, download tokens, Stripe webhook adapter (test mode)
- [x] Feature flags default-off for legacy social/publish/leaderboards/referrals
- [x] Security workflow (audit, Bandit, Gitleaks, SBOM)
- [x] Docs spine: CANON_ALIGNMENT, FEATURE_FLAGS, SECURITY, OPERATIONS, VALIDATION_EVIDENCE, ACCESSIBILITY
- [x] HTTP `/api/canon/*` for credits, exports, downloads, webhooks
- [x] Merge PR #47 to `main` — `a162f85` @ 2026-07-20T23:46:29Z
- [x] **P1 client wiring (PR #49):** `canonApi` + Account/RigDetail use `/api/canon` for balance, summary, list/create exports, download tokens; `monetizationApi.balance` aliases canon; `exportApi.patchbookExport` deprecated; Playwright mocks canon balance; gitignore allows `frontend/src/lib/`
- [x] Main CI green on merge commit of #49 (`71a4dfa`)

### Explicitly not done

- [ ] Production or staging deploy
- [ ] Live Stripe / `ALLOW_PRODUCTION_PAYMENTS=true`
- [ ] Full retirement of legacy rack/patch/export dual paths
- [ ] Move acceptance credits path off legacy `POST /api/export/runs/{id}/patchbook`
- [ ] Run DTOs with real `rig_revision_id` + server-side manifest hash (still `legacy-rack-{id}` bridge)
- [ ] Deletion of historical top-level/`backend/patchhive` package and unrouted page modules
- [ ] Cases/Patches list pages beyond stubs
- [ ] Hardware, DSP, MIDI/CV, or ModularGrid live provider implementation

## Recommended work order

### P0 — Ship gate (post-#47 / #49)

1. ~~Human review of PR #47~~ **DONE**
2. ~~Human review of PR #49~~ **DONE**
3. [x] Confirm `alembic heads` == `20240928_fix_schema_gaps` on clean `main` checkout
4. [x] Confirm flags in `.env.example`: all `ENABLE_LEGACY_*` false; `STRIPE_TEST_MODE=true`; `ALLOW_PRODUCTION_PAYMENTS=false`
5. [x] Main CI green @ `71a4dfa`
6. Optional: tag `v0.2.1-canon-p1-client` (or `v0.2.0-canon-mvp` if not tagged) and cut release notes

### P1 — Dual-path reduction (ACTIVE residual)

**Completed slices:**
- **PR #49:** FE debit/list/balance → canon only.
- **PR #51:** acceptance debit → `/api/canon/exports`; admin grant dual-writes canonical ledger; legacy debit gateable via `ENABLE_LEGACY_PATCHBOOK_DEBIT`.

**Progress checklist:**
- [x] Acceptance debit tests use `POST /api/canon/exports` + canonical ledger
- [x] Admin credit grant dual-writes `canonical_credit_ledger`
- [x] Legacy PatchBook debit: `deprecated` JSON markers + `ENABLE_LEGACY_PATCHBOOK_DEBIT` (default true; false → 410)
- [ ] Default `ENABLE_LEGACY_PATCHBOOK_DEBIT=false` once remaining non-MVP callers cleared
- [ ] Full retirement of legacy rack/patch list dual path (still needed for inventory UI)
- [ ] Run DTOs carrying real `rig_revision_id` / manifest hash (bridge uses `legacy-rack-{id}` + hashed run)

**Next slices (ordered):**

1. ~~**Acceptance → canon credits path**~~ **DONE** (PR #51)  
2. ~~**Deprecate / feature-gate legacy debit POST**~~ **DONE** (PR #51; default still true for transitional callers)  
3. **Run / revision bridge honesty**  
   - Extend run list DTO with `rig_revision_id` (or explicit null + bridge flag) and canonical `artifact_manifest_hash` when available.  
   - Replace FE `source_rig_revision_id: legacy-rack-{n}` and client-side `legacyRunManifestHash` once backend supplies truth.  
   - **Exit:** RigDetail export payload uses server-authored revision id + manifest; bridge helpers deleted or test-only.

4. **Inventory dual-path plan (design-first, then thin PR)**  
   - Active UI still calls `/api/racks`, `/api/runs`, `/api/patches` for inventory + generate (`Racks.tsx`, `RigDetail.tsx`, `RackBuilder`).  
   - Map each to future `/api/canon/rigs|revisions|runs` (or keep racks as CANON_SUPPORTING with adapters).  
   - Do **not** big-bang delete racks routers.  
   - **Exit:** written inventory matrix in CANON_ALIGNMENT + one vertical slice (e.g. run list via canon) green.
### P2 — Package and dead-UI hygiene

1. **Unrouted frontend pages (OBSERVED not in `App.tsx`):**  
   - `Feed.tsx`, `Publish.tsx`, `Publication.tsx`, `LeaderboardsModules.tsx`, `Gallery.tsx`  
   - Move to `frontend/src/legacy/` or delete in one PR; drop unused `publishingApi`/`communityApi`/`leaderboardsApi` client exports if nothing imports them after move.  
   - **Exit:** `rg` for those page names only under `legacy/` or gone; App routes unchanged for MVP.

2. **Import telemetry for `patchhive` package**  
   - Many `backend/tests/unit/*` and `backend/patchhive/*` still `from patchhive...`.  
   - Classify: CANON_SUPPORTING pipeline vs HISTORICAL duplicate.  
   - Quarantine pytest discovery for pure historical corpus; keep fail-closed vision adapters.  
   - **Exit:** documented import graph + no accidental new top-level `patchhive` imports from `backend/canon`.

3. Worktree hygiene: ignore accidental Finder duplicates (`frontend/src/lib/hash 2.ts` etc.) — do not commit.

### P3 — Staging operations

1. Stand up non-prod Postgres + app using OPERATIONS release gates.
2. Run acceptance suite against staging Postgres (clears local `NOT_COMPUTABLE`).
3. Backup/restore drill; ledger `reconcile` job if present.
4. Manual accessibility protocol on staging (see ACCESSIBILITY.md).
5. Expand Playwright beyond mocked MVP when staging exists.

### P4 — Product depth (still MVP-scoped)

1. **Cases / Patches list pages** — currently placeholders (`Cases.tsx`, `Patches.tsx`); wire to existing `caseApi` / `patchApi` with empty/loading/error parity.
2. Deeper rig revision UX (explicit revision picker, overlay notes/favorite/tried).
3. Stronger empty/loading/error parity on Modules list.
4. Expand golden fixtures / property tests for compiler edge cases.
5. Real image scanner implementation behind `ImageScanner` (ops secret + service).

### P5 — Explicitly deferred

- Community feed, profiles, comments, votes, following  
- Public publishing gallery as product surface  
- Leaderboards, contests, marketplace, curriculum  
- Live payments and customer charging  
- Next.js rewrite (forbidden by campaign: keep React/Vite + FastAPI)  
- Abraxas bridge productization beyond existing `docs/CANON.md` interface notes (RigMetricsPacket etc.) — separate campaign

## Repo continuation analysis (2026-07-21)

**Method:** github continuation recipe + live `main` @ `71a4dfa` evidence packet (no open campaign PR).

### OBSERVED

| Fact | Evidence |
|------|----------|
| HEAD == origin/main | `71a4dfaab7aefe1d4cb920dd9f83abcb7757fea7` |
| No open PRs/issues | `gh pr/issue list` empty open set |
| Alembic single head | `20240928_fix_schema_gaps` |
| Canon routers mounted | `backend/main.py` includes `/api/canon` |
| Legacy routers still mounted | racks, patches, runs, export, monetization, me |
| FE debit path | `RigDetail` → `canonApi.createExport` only |
| FE inventory path | `rackApi` / `runApi` / `patchApi` still primary |
| Acceptance debit path | still `/api/export/runs/{id}/patchbook` |
| Unrouted social/publish pages | on disk, not in `App.tsx` Routes |
| CI green on #49 merge push | Backend / Quality / Security success |
| Docs drift pre-this-pass | README/CURRENT_STATE still claimed HEAD `a162f85` (PR #47 only) |

### INFERRED

- Safest next engineering PR is **acceptance + legacy debit deprecation**, not rack rewrite (smaller blast radius, clears dual-debit residual).
- Cases/Patches stubs are product depth (P4), not blockers for “canon MVP on main.”
- `patchhive` package removal is blocked on test corpus rewrite — quarantine before delete.

### SPECULATIVE (do not promote)

- Staging host choice (Render vs Compose vs Azure) without operator pick.
- Whether racks remain forever as CANON_SUPPORTING vs full rename to “rigs” HTTP.

### Recommended next operator action

1. Merge this docs PR (status truth).  
2. Open `feat/p1-acceptance-canon-exports` implementing CONTINUATION P1 items 1–2.  
3. Hold production deploy and live Stripe.

## Verification commands (copy/paste)

```bash
# main
git fetch origin && git checkout main && git pull --ff-only
git rev-parse HEAD   # expect 7471a2a… or later

cd backend
# prefer project venv; scrub Hermes PYTHONPATH if present
env -u PYTHONPATH python -m pip install -e '.[dev]'
alembic heads        # expect 20240928_fix_schema_gaps
env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance -q
env -u PYTHONPATH python -m pytest tests/api/test_canon_export_api.py -q

cd ../frontend
npm ci
env -u PYTHONPATH npm test -- --run
env -u PYTHONPATH npm run type-check
env -u PYTHONPATH npm run test:e2e
```

CI authoritative when local Docker/Postgres missing. Full `make test` requires Docker Compose plugin.

## Drift watchlist

| Item | Risk |
|------|------|
| Root `DEPLOY_STATUS.md` (2025-11-26 “ready for Render”) | Stale — do not treat as ship authority |
| Root `CANON_DIFF.md` / `CANON_SYNC.md` | Pre-campaign audits — superseded by CANON_ALIGNMENT |
| `docs/OPERATIONS.md` Alembic head | Must match **20240928_fix_schema_gaps** |
| Social pages still on disk | Dead UI surface if re-linked accidentally |
| Dual export debit paths | Double-debit risk if both live without shared ledger — prefer canon only; acceptance still on legacy POST |
| README “checkout campaign branch” | Stale until this docs pass — main is default |
| Finder `* 2.ts` duplicates under `frontend/src/lib/` | Noise; never commit |

## Exit criteria for “canon MVP on main”

1. ~~PR #47 merged~~ **DONE**  
2. ~~Main CI green on merge~~ **DONE** (also #49 @ `71a4dfa`)  
3. Docs on main: README + CURRENT_STATE + CONTINUATION agree on merged HEAD — **this pass**  
4. No production payment flags enabled — **true in `.env.example`**  
5. Staging optional but recommended before any public traffic claim  
6. **Stretch (P1 complete):** acceptance + UI share one debit ledger path (canon)

**Active engineering starts at P1 residual item 1** (acceptance → canon exports).
