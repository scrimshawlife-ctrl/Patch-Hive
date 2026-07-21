# Feature flags

All flags are environment variables parsed case-insensitively by backend settings.

| Flag | Default | Purpose |
|---|---:|---|
| `ENABLE_LEGACY_SOCIAL` | `false` | Compatibility feed/comment/vote endpoints only (login/register/profile stay always-on under `/api/community`) |
| `ENABLE_LEGACY_PUBLISHING` | `false` | Compatibility public publication endpoints |
| `ENABLE_LEGACY_LEADERBOARDS` | `false` | Compatibility leaderboard endpoints |
| `ENABLE_LEGACY_REFERRALS` | `false` | Gates `/api/me/referrals`, community referral summary, referral signup capture, and monetization purchase-for-referral recording |
| `STRIPE_TEST_MODE` | `true` | Reject livemode webhook events in the canonical Stripe adapter and `/api/canon/webhooks/stripe` |
| `ALLOW_PRODUCTION_PAYMENTS` | `false` | Kill switch. When false, production webhook intake returns 403. Startup fails closed if production sets this false while `STRIPE_TEST_MODE=false`, or sets this true without reviewed secrets. |
| `STRIPE_WEBHOOK_SECRET` | empty | Stripe signing secret for `/api/canon/webhooks/stripe` |
| `DOWNLOAD_TOKEN_SECRET` | empty | HMAC secret for scoped export download tokens (falls back to `SECRET_KEY` when long enough) |

Auth endpoints (`POST /api/community/auth/login`, registration, profile) are part of the default MVP surface and do **not** require `ENABLE_LEGACY_SOCIAL`.

### Canonical payment/export HTTP surface

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/canon/credits/balance` | Canonical ledger balance for the authenticated user |
| `GET` | `/api/canon/credits/summary` | Balance + recent ledger rows (account dashboard) |
| `GET` | `/api/canon/exports` | Owner-scoped canonical export history |
| `POST` | `/api/canon/exports` | Atomic debit + export record (`request_export`) with idempotency key |
| `GET` | `/api/canon/exports/{id}` | Owner-scoped export status |
| `POST` | `/api/canon/exports/{id}/download-token` | Issue short-lived principal-scoped token |
| `POST` | `/api/canon/exports/{id}/download` | Verify token scope for a completed/queued export |
| `POST` | `/api/canon/webhooks/stripe` | Replay-safe Stripe-style webhook intake |

### Client preference (P1 — PR #49 done for MVP UI)

| Client surface | Preferred path | Residual legacy |
|---|---|---|
| Rig workspace credits + patch-book debit | `canonApi` → `/api/canon/credits/balance`, `POST /api/canon/exports` | `exportApi.patchbookExport` deprecated; **not used by active UI** |
| Account credits + export list | `accountApi` → `/api/canon/credits/summary`, `GET /api/canon/exports` | `/api/me/credits`, `/api/me/exports` still on server |
| PDF/SVG file bytes | still `/api/export/...` GETs | Artifact delivery only — **no new debits** |
| Acceptance debit tests | **should move to** `POST /api/canon/exports` | still call `POST /api/export/runs/{id}/patchbook` (P1 residual) |
| RigDetail export ids | server `rig_revision_id` + manifest (target) | bridge: `legacy-rack-{id}` + client `legacyRunManifestHash` |

### DEPRECATIONS

| Endpoint / client | Status | Notes |
|---|---|---|
| `exportApi.patchbookExport` | Deprecated | Dual-path debit risk; use `canonApi.createExport` |
| `POST /api/export/runs/{id}/patchbook` | Transitional | Debits legacy ledger path; keep until acceptance ported |
| `POST /api/export/patchbook` | Document-only builder API | No MVP UI caller for debit flow |
| `publishingApi` / `communityApi` / `leaderboardsApi` FE clients | Dead for MVP nav | Only referenced by unrouted pages — P2 cleanup |

Legacy `/api/export` PatchBook **POST** routes remain during transition but must not be used by the active UI. Production payments stay disabled unless a separate reviewed change sets `ALLOW_PRODUCTION_PAYMENTS=true` with real secrets.

Historical flags may be enabled only in isolated compatibility tests or explicitly reviewed non-production environments. The frontend does not expose corresponding navigation.
