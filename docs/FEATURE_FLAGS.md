# Feature flags

All flags are environment variables parsed case-insensitively by backend settings.

| Flag | Default | Purpose |
|---|---:|---|
| `ENABLE_LEGACY_SOCIAL` | `false` | Compatibility feed/comment/vote endpoints only (login/register/profile stay always-on under `/api/community`) |
| `ENABLE_LEGACY_PUBLISHING` | `false` | Compatibility public publication endpoints |
| `ENABLE_LEGACY_LEADERBOARDS` | `false` | Compatibility leaderboard endpoints |
| `ENABLE_LEGACY_REFERRALS` | `false` | Gates `/api/me/referrals`, community referral summary, referral signup capture, and monetization purchase-for-referral recording |
| `STRIPE_TEST_MODE` | `true` | Reject livemode webhook events in the canonical Stripe adapter (`canon.exports.verify_stripe_webhook`) |
| `ALLOW_PRODUCTION_PAYMENTS` | `false` | Reserved kill switch; remains false in this campaign. Live payment HTTP entrypoints are not activated here. |

Auth endpoints (`POST /api/community/auth/login`, registration, profile) are part of the default MVP surface and do **not** require `ENABLE_LEGACY_SOCIAL`.

Historical flags may be enabled only in isolated compatibility tests or explicitly reviewed non-production environments. The frontend does not expose corresponding navigation.
