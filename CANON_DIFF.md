# CANON_DIFF

This audit compares current repository state against the provided Notion canon requirements.

| Canon requirement | Repo status | File(s) affected | Required action |
| --- | --- | --- | --- |
| Monetization Ops tables: EXPORTS | MISSING | `backend/monetization/models.py`, `backend/alembic/versions/20240920_add_monetization_and_referrals.py` | ADD |
| Monetization Ops tables: CREDITS_LEDGER (supports Grant) | MISSING | `backend/monetization/models.py`, `backend/alembic/versions/20240920_add_monetization_and_referrals.py` | ADD |
| Monetization Ops tables: LICENSES | MISSING | `backend/monetization/models.py`, `backend/alembic/versions/20240920_add_monetization_and_referrals.py` | ADD |
| Users table includes `referral_code` + `referred_by` | MISSING | `backend/community/models.py`, `backend/community/routes.py`, `backend/community/schemas.py`, `backend/alembic/versions/20240920_add_monetization_and_referrals.py` | ADD |
| Referral flow: pending + reward after first paid purchase | MISSING | `backend/monetization/referrals.py`, `backend/community/routes.py`, `backend/tests/unit/test_referrals.py` | ADD |
| Transparency: referral code/link + pending referrals + earned credits | MISSING | `backend/monetization/referrals.py`, `backend/monetization/schemas.py`, `backend/community/routes.py` | ADD |
| Payment state does not gate generation/exploration | OK | `backend/export/routes.py`, `backend/patches/routes.py` | NONE |
| ABX-Runes enforcement (registry, manifest, deterministic IDs) | OK | `backend/patchhive/runes/manifest.json`, `backend/patchhive/runes/registry.py` | NONE |
