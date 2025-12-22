# CANON_SYNC

| Item | Exists (Yes/No) | Action Taken |
| --- | --- | --- |
| EXPORTS table/model | Yes | Confirmed in `backend/monetization/models.py` + migration. |
| CREDITS_LEDGER table/model | Yes | Confirmed in `backend/monetization/models.py` + migration. |
| User identity model | Yes | `backend/community/models.py` updated with referral fields. |
| Payment event handling (Stripe or mock) | Yes | Added minimal purchase event endpoint in `backend/monetization/routes.py` using `record_purchase()`. |
