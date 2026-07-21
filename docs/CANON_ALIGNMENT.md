# Canon alignment and product inventory

Authority: ABX-CAN-043, then workspace/naming doctrine, execution specification, product/design specification, repository behavior, and historical claims.

**Campaign:** Issue #46 closed · PR #47 merged · PR #49 merged (P1 client)  
**Last inventory refresh:** 2026-07-21 · main HEAD `71a4dfa`  
**Continuation plan:** [CONTINUATION.md](CONTINUATION.md)

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
| Legacy `/api/racks`, `/api/patches`, `/api/runs` | CANON_SUPPORTING / transitional | Still mounted; **active inventory UI** — reduce per CONTINUATION P1 residual |
| Legacy `POST /api/export/runs/{id}/patchbook` debit | CANON_SUPPORTING / transitional | Acceptance still depends; MVP UI debits via `/api/canon/exports` only (PR #49) |
| Legacy `/api/export/*` PDF/SVG GET bytes | CANON_SUPPORTING | Artifact delivery; no new MVP debits |
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
| P1 residual | Acceptance debit, run DTO bridge, inventory dual-path | **Open** — see CONTINUATION |

Post-campaign engineering is tracked in [CONTINUATION.md](CONTINUATION.md), not as a re-open of Phase 0–8 unless critical regression appears.
