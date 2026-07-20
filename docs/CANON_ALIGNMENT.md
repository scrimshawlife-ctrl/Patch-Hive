# Canon alignment and product inventory

Authority: ABX-CAN-043, then workspace/naming doctrine, execution specification, product/design specification, repository behavior, and historical claims.

## Classification

| Surface | Classification | Active MVP disposition |
|---|---|---|
| `backend/canon` contracts/compiler/repository | CANON_MVP | Primary canonical domain and persistence adapter |
| Modules, cases, racks, validation | CANON_MVP | Retained and adapted; immutable revisions are canonical truth |
| Runs, patch generation, naming | CANON_MVP | Retained where compatible; canonical compiler emits full artifact set |
| PatchBook/PDF, SVG, JSON, ZIP | CANON_MVP | Export boundary; deterministic PDF metadata and text companion |
| Credits, ledger, Stripe events | CANON_MVP | Canonical atomic ledger and replay-safe test-mode adapter exposed at `/api/canon/*` |
| Admin diagnostics/auditing | CANON_SUPPORTING | RBAC retained; canonical audit events append-only |
| Image/provider detection | CANON_SUPPORTING | Untrusted evidence only; validation, scan adapter, re-encoding, metadata stripping |
| Integration/catalog adapters | CANON_SUPPORTING | Retained behind bounded adapters |
| Community feed, comments, votes, following, notifications | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Public publishing/profiles/sharing | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Leaderboards | FEATURE_FLAGGED_FUTURE | Backend router off by default; absent from navigation |
| Referrals | FEATURE_FLAGGED_FUTURE | Flag defaults off; retained regression coverage only |
| Contests, marketplace, curriculum/workshop tools | DEAD_OR_UNUSED | Outside MVP; no active implementation work |
| Duplicate top-level `patchhive` package | HISTORICAL | Not the canonical backend package; scheduled for removal after compatibility audit |
| `backend/patchhive/tests` duplicate-package corpus | HISTORICAL | Excluded from canonical pytest discovery; imports target superseded v1 symbols and require a separate compatibility/removal decision |
| README social claims and Discord materials | HISTORICAL | Superseded by this document and current README |
| Live deployment state and production data | NOT_COMPUTABLE | No production access or deployment performed |
| PostgreSQL/Docker integration on machines without Docker | NOT_COMPUTABLE | CI service workflow is authoritative when run |

## Resolved drift

- Historical social and publishing routes no longer load by default.
- Public profile fields are not exposed by the retained publishing compatibility surface.
- Canonical revisions, runs, libraries, generated patches, manifests, receipts, ledger entries, and admin audit events reject mutation and deletion at the ORM boundary.
- User notes, favorite, and tried state live in a mutable overlay.
- Duplicate mapped table/class names and the Alembic branch conflict were repaired.
- The rune manifest now declares the eight required operations, schemas, versions, determinism classes, authority, side effects, failure codes, and test vectors.
- Provider output cannot self-promote to confirmed truth.

## Remaining bounded risk

- Legacy persistence models remain for compatibility and are not yet migrated into every canonical route.
- The duplicate historical package requires a later removal PR after import telemetry.
- Its stale duplicate-package test corpus remains preserved but is not evidence for the canonical backend; no tests were deleted.
- Full PostgreSQL transaction and browser E2E execution depend on Docker/browser availability.
- Tagged PDF semantics are limited by ReportLab; every generated PatchBook includes a text-first companion page.
