# Dashboard State Discovery

## Current Auth/Session Identity
- Backend uses JWT auth in `backend/community/routes.py` with `get_current_user` and `require_auth`.
- Login endpoint: `POST /api/community/auth/login` returns `access_token` and `user`.
- Profile update endpoint: `PATCH /api/community/users/me`.
- No existing `GET /api/community/users/me` identity endpoint (added in this implementation).

## Existing Profile/User Settings UI
- Frontend has a login screen in `frontend/src/pages/Login.tsx`.
- No dedicated profile or account settings UI exists.

## Existing Referrals + Credits Ledger
- No referral models, ledger tables, or routes in the backend.
- No credits balance or export history tracked.

## Gaps to Address
- Add authenticated dashboard routes for credits, exports, referrals, and profile.
- Add referral summary endpoint and referral code storage.
- Add credits ledger + export record storage.
- Add public leaderboards endpoints (aggregate-only) and frontend pages.
