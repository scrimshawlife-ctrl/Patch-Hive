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
| `POST` | `/api/canon/exports` | Atomic debit + export record (`request_export`) with idempotency key |
| `GET` | `/api/canon/exports/{id}` | Owner-scoped export status |
| `POST` | `/api/canon/exports/{id}/download-token` | Issue short-lived principal-scoped token |
| `POST` | `/api/canon/exports/{id}/download` | Verify token scope for a completed/queued export |
| `POST` | `/api/canon/webhooks/stripe` | Replay-safe Stripe-style webhook intake |

Legacy `/api/export` PatchBook routes remain available during transition. Production payments stay disabled unless a separate reviewed change sets `ALLOW_PRODUCTION_PAYMENTS=true` with real secrets.

Historical flags may be enabled only in isolated compatibility tests or explicitly reviewed non-production environments. The frontend does not expose corresponding navigation.
