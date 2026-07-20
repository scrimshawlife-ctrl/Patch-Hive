# Feature flags

All flags are environment variables parsed case-insensitively by backend settings.

| Flag | Default | Purpose |
|---|---:|---|
| `ENABLE_LEGACY_SOCIAL` | `false` | Compatibility feed/comment/vote endpoints |
| `ENABLE_LEGACY_PUBLISHING` | `false` | Compatibility public publication endpoints |
| `ENABLE_LEGACY_LEADERBOARDS` | `false` | Compatibility leaderboard endpoints |
| `ENABLE_LEGACY_REFERRALS` | `false` | Historical referral behavior; not canonical MVP |
| `STRIPE_TEST_MODE` | `true` | Reject livemode webhook events |
| `ALLOW_PRODUCTION_PAYMENTS` | `false` | Reserved kill switch; remains false in this campaign |

Historical flags may be enabled only in isolated compatibility tests or explicitly reviewed non-production environments. The frontend does not expose corresponding navigation.
