# Canon alignment and product inventory

Authority: ABX-CAN-043, then workspace/naming doctrine, execution specification, product/design specification, repository behavior, and historical claims.

**Campaign:** Issue #46 closed · PR #47–#54 product path merged · PR #53 one-page publishing docs  
**Last inventory refresh:** 2026-07-21 · main baseline `72c9dcc` (+ this branch)  
**Continuation plan:** [CONTINUATION.md](CONTINUATION.md)
**Tracking:** open residual issue linked from CONTINUATION (P1 inventory / P2 hygiene)
## Classification

| Surface | Classification | Active MVP disposition |
|---|---|---|
| `backend/canon` contracts/compiler/repository | CANON_MVP | Primary canonical domain and persistence adapter |
| Modules, cases, racks, validation | CANON_MVP | Retained and adapted; immutable revisions are canonical truth |
| Runs, patch generation, naming | CANON_MVP | Retained where compatible; canonical compiler emits full artifact set |
| PatchBook/PDF, SVG, JSON, ZIP | CANON_MVP | Export boundary; deterministic PDF metadata and text companion |
| Credits, ledger, Stripe events | CANON_MVP | Canonical atomic ledger and replay-safe test-mode adapter at `/api/canon/*` |
| Auth login/register/profile | CANON_MVP | Always-on under `/api/community/auth/*` (not behind legacy social flag) |
| Canonical workspace UI (`App.tsx` routes) | CANON_MVP | Rigs, modules, cases, patches, account, admin diagnostics |
| Admin diagnostics/auditing | CANON_SUPPORTING | RBAC retained; canonical audit events append-only |
| Image/provider detection | CANON_SUPPORTING | Untrusted evidence only; validation, scan adapter, re-encoding, metadata stripping |
| Integration/catalog adapters | CANON_SUPPORTING | Retained behind bounded adapters |
| Legacy `/api/racks`, `/api/patches`, `/api/runs` | CANON_SUPPORTING / transitional | Still mounted; **active inventory UI** — see **Inventory dual-path matrix** below |
| Legacy `POST /api/export/runs/{id}/patchbook` debit | CANON_SUPPORTING / transitional | MVP UI + acceptance use `/api/canon/exports` (PR #49/#51); gate via `ENABLE_LEGACY_PATCHBOOK_DEBIT` |
| Legacy `/api/export/*` PDF/SVG GET bytes | CANON_SUPPORTING | Artifact delivery; no new MVP debits |
| Run list DTO bridge fields | CANON_SUPPORTING | Server-authored `legacy-run-*` / `legacy-rack-*` + hash (PR #54); not yet native canon generator IDs |
| Community feed, comments, votes, following, notifications | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Public publishing/profiles/sharing | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Leaderboards | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Referrals | FEATURE_FLAGGED_FUTURE | Flag defaults off; retained regression coverage only |
| Frontend pages not routed (`Feed`, `Publish`, `Publication`, leaderboards, …) | DRIFT / HISTORICAL | On disk but not linked in `App.tsx` — remove or archive (CONTINUATION P2) |
| Contests, marketplace, curriculum/workshop tools | DEAD_OR_UNUSED | Outside MVP; no active implementation work |
| Duplicate top-level `patchhive` package | HISTORICAL | Not the canonical backend package; scheduled for removal after compatibility audit |
| `backend/patchhive/tests` duplicate-package corpus | HISTORICAL | Excluded from canonical pytest discovery; imports target superseded v1 symbols |
| README social claims and Discord materials (pre-PR main) | HISTORICAL | Superseded by current README and this document |
| Root `DEPLOY_STATUS.md` / `CANON_DIFF.md` / `CANON_SYNC.md` | HISTORICAL | Superseded by CURRENT_STATE + CONTINUATION + this file |
| Live deployment state and production data | NOT_COMPUTABLE | No production access or deployment performed |
| PostgreSQL/Docker integration on machines without Docker | NOT_COMPUTABLE | CI service workflow is authoritative when run |

## Resolved drift

- Historical social and publishing routes no longer load by default.
- Public profile fields are not exposed by the retained publishing compatibility surface.
- Canonical revisions, runs, libraries, generated patches, manifests, receipts, ledger entries, and admin audit events reject mutation and deletion at the ORM boundary.
- User notes, favorite, and tried state live in a mutable overlay.
- Duplicate mapped table/class names and the Alembic branch conflict were repaired.
- Alembic single head advanced through `20240927_canon_alignment` → **`20240928_fix_schema_gaps`** (votes/comments/account compatibility tables).
- The rune manifest declares the eight required operations, schemas, versions, determinism classes, authority, side effects, failure codes, and test vectors.
- Provider output cannot self-promote to confirmed truth.
- Canonical export/credit/webhook HTTP is exposed under `/api/canon/*` with production payment startup policy.

## Remaining bounded risk

- Legacy persistence models remain for compatibility and are not yet migrated into every canonical route.
- The duplicate historical package requires a later removal PR after import telemetry.
- Its stale duplicate-package test corpus remains preserved but is not evidence for the canonical backend; no tests were deleted.
- Full PostgreSQL transaction and browser E2E execution depend on Docker/browser availability locally; CI covers Postgres backend suite.
- Tagged PDF semantics are limited by ReportLab; every generated PatchBook includes a text-first companion page.
- Unrouted frontend page modules can reintroduce social surfaces if re-linked without flag review.

## Phase completion (campaign)

| Phase | Focus | Campaign status |
|------:|-------|-----------------|
| 0 | Baseline and drift inventory | Complete (this doc + CURRENT_STATE) |
| 1 | Canonical contracts and persistence | Complete (`backend/canon`, migrations) |
| 2 | Rig truth and immutable revisions | Complete (ADR 0001 + models) |
| 3 | Deterministic compiler and validation | Complete (compiler, runes, golden hash) |
| 4 | Canonical product workspace | Complete (App shell, RigDetail, graph) |
| 5 | Photo evidence workflow | Complete (evidence module + UI resolution) |
| 6 | Exports, credits, Stripe hardening | Complete (test-mode canon routes) |
| 7 | Security, accessibility, operations | Complete (workflows + docs) |
| 8 | Full validation and documentation alignment | Complete — merged main via PR #47 |
| P1 client | Credits/exports FE → `/api/canon/*` | Complete — merged main via PR #49 |
| P1 residual | Acceptance debit, run DTO bridge, inventory dual-path | Acceptance + run DTO **done** (#51/#54); inventory matrix below; dual-path code open |
| P1 docs | One-page publishing + release governance | PR #53 (this lineage) |

Post-campaign engineering is tracked in [CONTINUATION.md](CONTINUATION.md), not as a re-open of Phase 0–8 unless critical regression appears.

## Inventory dual-path matrix (design-first)

**Purpose:** map active MVP client calls to preferred HTTP surfaces without a big-bang delete of racks/patches routers.  
**Rule:** one vertical slice at a time; keep dual mount until replacement green on CI Postgres.  
**Authority:** product inventory only — no production deploy implied.

| Client surface (OBSERVED) | Current HTTP | Preferred long-term | Near-term disposition | Next engineering slice |
|---|---|---|---|---|
| Module gallery list/detail | `GET /api/modules` | Keep as catalog MVP (`CANON_MVP`) | **Retain** | None (stable) |
| Cases list UI | stub page; API `GET /api/cases` exists | Keep catalog | **Retain API**; wire UI (P4) | P4 Cases page |
| Rigs list / create / edit | `GET/POST/PATCH /api/racks` | Adapter over immutable **Rig + RigRevision** | **CANON_SUPPORTING** keep routers | Optional: document rack_id ≡ rig_id |
| Rack builder | `/api/racks` + modules | Same | **Retain** | Photo evidence already separate |
| Run list / detail | `GET /api/runs?rack_id=` | Enriched DTO already; future `/api/canon/runs` | **Retain** + bridge fields | Native canon run write on generate |
| Run patches | `GET /api/runs/{id}/patches` | Canon library membership | **Retain** until generate emits `generated_patches` | Generator dual-write |
| Patch generate | `POST /api/patches/generate/{rack_id}` | Canon compiler + `create_run_with_library` | **Retain** entry; dual-write bridge | **Slice A:** generate ensures bridge + optional GenerationRun |
| Patch list page | stub; `GET /api/patches` | Canon libraries / generated patches | **Retain API**; wire UI (P4) | P4 |
| RigDetail export debit | `POST /api/canon/exports` via run DTO fields | Already preferred | **Done** (#49/#54) | Promote off `legacy-*` IDs |
| Account credits/exports | `/api/canon/*` | Already preferred | **Done** | — |
| PDF/SVG bytes | `GET /api/export/...` | Canon download tokens + artifact store | **Retain GETs** (no debit) | Optional token gate later |
| Legacy patchbook debit POST | `POST /api/export/runs/{id}/patchbook` | Disabled when flag false | **Transitional** | Flip default false after caller audit |
| Auth login/register/me | `/api/community/auth/*`, users | Keep | **Retain** | — |
| Admin diagnostics | `/api/admin/*` | Keep | **Retain** | — |
| Social/publish/leaderboards FE pages | unrouted files + flagged APIs | Off | **P2 archive/delete** | Quarantine PR |
| `publishingApi` / `communityApi` FE | only dead pages | Drop with P2 | **P2** | — |

### Explicit non-goals (this matrix)

- Do **not** rename HTTP `/racks` → `/rigs` in one PR without FE+acceptance+docs.  
- Do **not** delete `backend/racks` or `backend/patches` while Racks/RigDetail depend on them.  
- Do **not** require Next.js or GraphQL.

### Recommended vertical slices (order)

| ID | Slice | Exit criteria |
|----|--------|----------------|
| **A** | On `POST /api/patches/generate/{rack_id}`, after legacy `Run` create, call `ensure_legacy_run_export_bridge` (or stronger dual-write) | New runs immediately `export_bridge_ready` without relying only on list GET side-effect |
| **B** | Optional thin `GET /api/canon/runs?rig_id=` alias returning same bridge DTO | FE can migrate one call site; legacy list remains |
| **C** | Generator writes real `RigRevisionRecord` content hash from rack snapshot (still may keep `legacy-rack-*` id until revision chain exists) | Manifest/hash reflects rack content, not only run id |
| **D** | P2 move unrouted FE pages to `frontend/src/legacy/` | No import from `App.tsx`; dead client APIs unused |
| **E** | `ENABLE_LEGACY_PATCHBOOK_DEBIT=false` default after ripgrep shows no non-test callers | 410 on legacy debit in default env |

**Matrix status:** **DESIGN COMPLETE** (this section). Implementation starts at slice **A** on a feature branch — not in docs-only #53 unless bundled.