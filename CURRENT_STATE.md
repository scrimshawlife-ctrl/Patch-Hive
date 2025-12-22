# CURRENT_STATE

## Backend stack
- **Framework**: FastAPI (`backend/main.py`)
- **Database layer**: SQLAlchemy ORM with Alembic migrations (`backend/core/database.py`, `backend/alembic/`)
- **Auth**: JWT-based auth using `core/security.py`, token parsing in `community/routes.py`

## Existing models
- **Users**: `backend/community/models.py`
- **Credits Ledger / Exports / Licenses**: `backend/monetization/models.py`
- **Modules Library**: `backend/modules/models.py`
- **Gallery Revisions**: File-based revisions under `backend/patchhive/gallery/revisions.py` (no DB table)
- **Rigs, Runs, Patches**: Racks + patches exist (`backend/racks/models.py`, `backend/patches/models.py`); runs missing prior to this update

## Payment event handling
- Minimal paid purchase recording via `backend/monetization/routes.py` + `record_purchase()` in `backend/monetization/referrals.py`

## Notes
- Admin console and audit logging were not previously implemented.
- Modules deletion used hard deletes; this update moves to tombstone status.
