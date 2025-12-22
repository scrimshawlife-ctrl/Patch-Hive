# REFERRAL_IMPLEMENTATION

## Canon rules
- Reward = 3 free credits.
- Granted only after referred user’s **first paid purchase**.
- One reward per referred user.
- No self-referrals.
- Credits do not expire.
- Ledger entry:
  - `change_type = "Grant"`
  - `notes = "Referral reward: <referred_user_id>"`

## Data model
- **users**
  - `referral_code` (unique, immutable once created)
  - `referred_by` (nullable)
- **credits_ledger**
  - `change_type` supports `Grant`
  - `referral_id` links to referral event
- **referrals** (append-only)
  - `referrer_user_id`
  - `referred_user_id`
  - `status` (`Pending` / `Rewarded`)
  - `first_purchase_id`
  - `rewarded_at`

## Event flow
1. **Signup with referral code**
   - Store `referred_by` on the new user.
   - Insert `referrals` row with `status = Pending`.
2. **First successful paid purchase**
   - Create `credits_ledger` entry with `change_type = Purchase` for referred user.
   - Validate it is the first purchase.
   - Validate referral exists and not previously rewarded.
   - Insert `credits_ledger` entry with `change_type = Grant` for referrer.
   - Append new `referrals` row with `status = Rewarded`, `first_purchase_id`, `rewarded_at`.

## Trust & determinism
- Referral logic never affects generation, patch visibility, or exploration.
- Referral credits are not revoked after refunds.
